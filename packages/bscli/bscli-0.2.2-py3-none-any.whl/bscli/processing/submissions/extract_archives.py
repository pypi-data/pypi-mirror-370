import logging
import tarfile
from pathlib import Path

import patoolib

from bscli.processing import SubmissionsProcessing
from bscli.processing.utils import get_all_files, filter_files

logger = logging.getLogger(__name__)


class ExtractArchives(SubmissionsProcessing):
    @staticmethod
    def _extract_patoolib(path: Path, submission_name: str) -> bool:
        try:
            # Attempt to extract archive to parent folder.
            # The verbosity and interactive parameters should ensure nothing hangs, or shows output.
            # It may not be bulletproof however, as it only sets the stdin of the extraction process to an empty string.
            # Anything shown to standard error is also not hidden, and impossible to hide.
            patoolib.extract_archive(
                path, outdir=path.parent, verbosity=-1, interactive=False
            )
            return True
        except patoolib.util.PatoolError:
            logger.error(
                'Failed to extract archive "%s" in %s', path.name, submission_name
            )
            return False

    @staticmethod
    def _extract_tarfile(path: Path, submission_name: str) -> bool:
        # TODO: should we extract a subset by manually filtering members as shown in the examples?
        # See https://docs.python.org/3/library/tarfile.html#examples.
        # Besides stripping out non-regular files like named pipes/links, we should also really check whether the file
        # extracts to the target folder, i.e. isn't absolute (/ prefix) or contains "..", permission bits etc.
        # We probably want to specify a custom filter callable if this is supported (enforce this?) and return `None`
        # on 'bad' entries to skip extracting them, rather than raising `FilterError`` to produce a fatal error.
        # We could take most of what the 'data' filter does, but tweak it a bit?
        # This would avoid rejecting (further) extraction of archives that do not pass the filter, which is done on a
        # member by member basis, so extraction of an archive may fail at any point and will not attempt to clean up.
        # This would leave a confusing mess of a potentially half extracted archive alongside the archive itself.
        try:
            with tarfile.open(path, errorlevel=2) as tf:
                # Filters were introduces as a Python 3.12 feature, but may be backported as a security feature.
                # See https://docs.python.org/3/library/tarfile.html#supporting-older-python-versions.
                if hasattr(tarfile, "data_filter"):
                    # Specify a data filter to prevent most of the problematic stuff from occurring.
                    # See https://docs.python.org/3/library/tarfile.html#tarfile.data_filter.
                    # Note that any member not passing the filter will halt extraction entirely.
                    # This is because it is raised as a 'fatal' error.
                    tf.extractall(path.parent, filter="data")
                else:
                    logger.warning("Data filter not supported, update Python version")
                    tf.extractall(path.parent)
            return True
        except (tarfile.TarError, OSError):
            logger.error(
                'Failed to extract archive "%s" in %s', path.name, submission_name
            )
            return False

    @staticmethod
    def _extract_archive(path: Path, submission_name: str) -> bool:
        name = path.name.lower()

        # Extract tar files using the Python tarfile library rather than passing it to patoolib.
        # While patoolib supports extracting these archives itself, it tends to use the installed GNU tar binary.
        # This is problematic as it does not handle tar files made on OSX by BSD tar well, which students often submit.
        # Such tars include extra extended header keywords it does not understand, which generate error messages that
        # are printed to the standard error stream, unless '--warning=no-unknown-keyword' is specified.
        # However, we have no way to hide the standard error stream, or to specify this warning option via patoolib.
        # This causes spamming of the standard error stream with messages like the following:
        # tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.quarantine'
        # tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.metadata:kMDItemWhereFroms'
        # tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.metadata:kMDItemDownloadedDate'
        # tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.macl'
        # tar: Ignoring unknown extended header keyword 'SCHILY.fflags'
        # tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.FinderInfo'
        # By extracting via tarfile we also have more control over what is extracted, which has security implications.
        if (
            name.endswith(".tar")
            or name.endswith(".tar.xz")
            or name.endswith(".tar.gz")
            or name.endswith(".tar.bz2")
        ):
            return ExtractArchives._extract_tarfile(path, submission_name)
        else:
            return ExtractArchives._extract_patoolib(path, submission_name)

    def process_submission(self, submission_path: Path):
        excluded_archives = []

        # Try to recursively extract archives as students sometimes submit nested archives.
        # We do limit to 3 iterations to help mitigate (un)intentional zip-bomb like situations.
        for _ in range(1, 3):
            # Walk the path to get a list of all files under path, either directly or in subdirectories, then filter on supported archive extensions.
            files = get_all_files(submission_path)
            arc_files = filter_files(
                files, ["zip", "rar", "7z", "tar", "xz", "gz", "bz2"]
            )

            # Break out early if no archives are found.
            if not arc_files:
                break

            for file in arc_files:
                # Do not try to extract archives that already failed to extract.
                if file in excluded_archives:
                    continue

                if self._extract_archive(file, submission_path.name):
                    # Remove the archive once extracted so that we do not try extracting it again.
                    file.unlink()
                else:
                    # Failed to extract, so mark it to prevent re-extracting next iteration.
                    # We also keep the file so that the grader can try to sort it out themselves.
                    excluded_archives.append(file)

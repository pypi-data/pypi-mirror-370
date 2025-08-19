import fnmatch
import logging
import re
import shutil
from pathlib import Path

from bscli.config import AssignmentConfig
from bscli.processing import SubmissionsProcessing
from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


# removeFiles: list of glob: '.*' to remove all dotfiles, '*.exe' to remove all exe, etc
# removeFolders: list of glob: '.*' to remove all dotfolders, '__MACOSX' etc
# removeMimes: list of glob: 'application/x-sharedlib', 'application/x-executable', 'application/x-dosexec'
# ^ use python-libmagic? just subprocess.run 'file'?
class RemoveFiles(SubmissionsProcessing):
    def __init__(
        self, config: AssignmentConfig, progress_reporter: ProgressReporter = None
    ):
        super().__init__(progress_reporter)
        self.config = config
        self.regex_files = [
            re.compile(fnmatch.translate(pattern), re.IGNORECASE)
            for pattern in config.remove_files
        ]
        self.regex_folders = [
            re.compile(fnmatch.translate(pattern), re.IGNORECASE)
            for pattern in config.remove_folders
        ]

    def _should_remove_file(self, name: str) -> bool:
        for regex in self.regex_files:
            if regex.match(name):
                return True
        return False

    def _should_remove_folder(self, name: str) -> bool:
        for regex in self.regex_folders:
            if regex.match(name):
                return True
        return False

    def process_submission(self, submission_path: Path):
        entries = list(submission_path.iterdir())

        for entry in entries:
            if entry.is_fifo():
                # Python libraries like shutil do not handle fifo/named pipes well, so remove any encountered.
                # This is mostly an issue during Hacking in C where students use named pipes as part of their exploit and end up submitting them.
                entry.unlink()
            elif entry.is_symlink():
                # Remove any symbolic links encountered that may be produced due to extracting tarballs.
                # Following such links may have undesired consequences, or pull in files that should not be included.
                entry.unlink()
            elif entry.is_dir():
                if self._should_remove_folder(entry.name):
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    # Recursively process child directory.
                    self.process_submission(entry)
            elif entry.is_file():
                if self._should_remove_file(entry.name):
                    entry.unlink()
                # TODO: Check Mime type?

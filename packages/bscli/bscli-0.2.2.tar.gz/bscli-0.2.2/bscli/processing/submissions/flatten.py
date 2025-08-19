import logging
import random
import shutil
import string
from pathlib import Path

from bscli.processing import SubmissionsProcessing
from bscli.processing.utils import get_all_files

logger = logging.getLogger(__name__)


class Flatten(SubmissionsProcessing):
    def process_submission(self, submission_path: Path):
        for file in get_all_files(submission_path):
            # No need to move files already at the top-level folder.
            if file.parent == submission_path:
                continue

            # Attempt to move file to top-level folder; add random component in name to handle duplicates.
            target_path = submission_path / file.name
            while target_path.exists():
                rand_str = "".join(
                    random.choice(string.ascii_lowercase) for _ in range(10)
                )
                target_path = submission_path / f"dup-{rand_str}-{file.name}"

            file.rename(target_path)
        # Remove any leftover empty folders.
        for dir_ in [dir_ for dir_ in submission_path.iterdir() if dir_.is_dir()]:
            shutil.rmtree(dir_, ignore_errors=True)


class SmartFlatten(SubmissionsProcessing):
    @staticmethod
    def _is_empty(path: Path) -> bool:
        # Check if the path contains any files, directly or indirectly.
        for item in path.iterdir():
            if item.is_dir():
                if not SmartFlatten._is_empty(item):
                    return False
            else:
                return False

        return True

    @staticmethod
    def _prune(path: Path):
        # Prune folders without any files, directly or indirectly.
        dirs = [dir_ for dir_ in path.iterdir() if dir_.is_dir()]

        for dir_ in dirs:
            if SmartFlatten._is_empty(dir_):
                shutil.rmtree(dir_, ignore_errors=True)
            else:
                SmartFlatten._prune(dir_)

    @staticmethod
    def _merge(src: Path, dst: Path):
        for entry in list(src.iterdir()):
            if entry.is_file():
                # Ensure parent folder structure exists, then move the file there.
                dst.mkdir(parents=True, exist_ok=True)
                # We cannot move a file to a folder with the same name, so guard against that.
                target_path = dst / entry.name
                while target_path.exists():
                    rand_str = "".join(
                        random.choice(string.ascii_lowercase) for _ in range(10)
                    )
                    target_path = dst / f"dup-{rand_str}-{entry.name}"
                else:
                    entry.rename(target_path)
            elif entry.is_dir():
                SmartFlatten._merge(entry, dst / entry.name)

    def process_submission(self, submission_path: Path):
        files = get_all_files(submission_path)
        if files:
            # Find the longest common prefix path of all files.
            common_path = files[0].parent
            while not all([common_path in file.parents for file in files]):
                common_path = common_path.parent

            # If this common prefix path is not the submission path itself, we have redundant empty top-level folders.
            # We merge all files and folders under this common prefix path into the submission path.
            # This gets rid of the redundant top-level folders, but will leave empty folders.
            # Those are cleaned up with the later prune call however, so this is not an issue.
            if common_path != submission_path:
                self._merge(common_path, submission_path)

        # Remove empty folder trees, i.e. trees only containing other folders and not any actual files.
        self._prune(submission_path)

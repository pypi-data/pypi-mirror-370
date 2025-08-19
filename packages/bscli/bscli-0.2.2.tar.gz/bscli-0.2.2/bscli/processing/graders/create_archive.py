import logging
import shutil
import subprocess
from pathlib import Path

from bscli.config import AssignmentConfig
from bscli.division import Division
from bscli.processing import SubmissionsProcessing, GraderProcessing
from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


class MoveToGraderFolder(SubmissionsProcessing):
    def __init__(
        self,
        division: Division,
        graders_path: Path,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.submission_to_grader: dict[str, str] = dict()
        self.graders_path = graders_path

        for grader_id, submissions in division:
            for submission in submissions:
                self.submission_to_grader[submission.folder_name] = grader_id

            grader_path = graders_path / grader_id / "submissions"
            grader_path.mkdir(parents=True, exist_ok=True)

    def process_submission(self, submission_path: Path):
        grader_id = self.submission_to_grader[submission_path.name]
        grader_path = self.graders_path / grader_id / "submissions"
        shutil.move(submission_path, grader_path)


class CreateGraderArchives(GraderProcessing):
    """
    Creates compressed archives for each grader.

    Note: No longer uses 7z password encryption - FileSender handles encryption.
    Archives are created for compression/convenience only.
    """

    def __init__(
        self,
        dist_path: Path,
        assignment_config: AssignmentConfig,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.dist_path = dist_path
        self.assignment_config = assignment_config

    def process_grader(self, grader_path: Path):
        grader_id = grader_path.name
        assignment_id = self.assignment_config.identifier

        # Create target file path, and ensure parent folders exists.
        parent_path = self.dist_path.resolve() / assignment_id
        archive_path = parent_path / f"{assignment_id}-{grader_id}.7z"
        parent_path.mkdir(parents=True, exist_ok=True)

        # Create unencrypted compressed archive
        # FileSender will handle encryption with assignment-specific password
        # 'a'      => Add files to archive command.
        # '-ms=on' => Turn on solid mode (groups files together for better compression).
        # '-mx=9'  => Use Ultra compression level.
        # No '-mhe' or '-p' => No encryption (FileSender handles this)
        args = [
            "7za",
            "a",
            "-ms=on",
            "-mx=9",
            archive_path,
            "./",
        ]
        try:
            cp = subprocess.run(
                args, shell=False, check=False, capture_output=True, cwd=grader_path
            )
            if cp.returncode != 0:
                logger.fatal(
                    'Creating archive failed with exit code %d and stderr output "%s"',
                    cp.returncode,
                    cp.stderr,
                )
        except FileNotFoundError:
            logger.fatal("Creating archive failed as 7-Zip was not found")

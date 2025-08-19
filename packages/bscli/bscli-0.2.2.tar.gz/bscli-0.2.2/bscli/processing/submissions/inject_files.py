import shutil
from pathlib import Path

from bscli.config import AssignmentConfig
from bscli.processing import SubmissionsProcessing
from bscli.progress import ProgressReporter


class InjectFiles(SubmissionsProcessing):
    def __init__(
        self,
        config: AssignmentConfig,
        inject_path: Path,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.inject_path = inject_path / config.identifier / "submission"

    def process_submission(self, submission_path: Path):
        # TODO: some check to prevent overwriting student files? Perhaps rename them in such cases?
        shutil.copytree(self.inject_path, submission_path, dirs_exist_ok=True)

    def execute(self, path: Path):
        if self.inject_path.exists():
            super().execute(path)

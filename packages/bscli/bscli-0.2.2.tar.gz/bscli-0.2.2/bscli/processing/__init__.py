import logging
from abc import ABC, abstractmethod
from pathlib import Path

from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


class SubmissionsProcessing(ABC):
    def __init__(self, progress_reporter: ProgressReporter = None):
        self.progress_reporter = progress_reporter

    @abstractmethod
    def process_submission(self, submission_path: Path):
        pass

    def execute(self, path: Path):
        dirs = [dir_ for dir_ in path.iterdir() if dir_.is_dir()]

        for idx, dir_ in enumerate(dirs):
            if self.progress_reporter:
                self.progress_reporter.start(idx + 1, len(dirs), dir_.name)
            self.process_submission(dir_)
        if self.progress_reporter:
            self.progress_reporter.finish(len(dirs))


class GraderProcessing(ABC):
    def __init__(self, progress_reporter: ProgressReporter = None):
        self.progress_reporter = progress_reporter

    @abstractmethod
    def process_grader(self, grader_path: Path):
        pass

    def execute(self, path: Path):
        dirs = [dir_ for dir_ in path.iterdir() if dir_.is_dir()]

        for idx, dir_ in enumerate(dirs):
            if self.progress_reporter:
                self.progress_reporter.start(idx + 1, len(dirs), dir_.name)
            self.process_grader(dir_)
        if self.progress_reporter:
            self.progress_reporter.finish(len(dirs))


class NOPProcessing(SubmissionsProcessing):
    def process_submission(self, submission_path: Path):
        pass

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional

from bscli.downloader import SubmissionInfo, AssignmentInfo
from bscli.logs import LogEntry, load_log


class Division:
    division: dict[str, list[SubmissionInfo]]

    def __init__(self, graders: Iterable[str]):
        self.division = {grader: [] for grader in graders}

    def __iter__(self):
        return self.division.items().__iter__()

    def __getitem__(self, grader_id: str) -> list[SubmissionInfo]:
        return self.division.get(grader_id, [])

    def graders(self) -> list[str]:
        return list(self.division.keys())

    def assign_to(self, grader_id: str, submission: SubmissionInfo):
        self.division[grader_id].append(submission)

    def assign_many_to(self, grader_id: str, submissions: list[SubmissionInfo]):
        self.division[grader_id].extend(submissions)

    def assign_randomly(self, submission: SubmissionInfo):
        grader_id = random.choice(list(self.division.keys()))
        self.assign_to(grader_id, submission)

    def write_logs(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

        for grader_id, submissions in self.division.items():
            log_path = path / f"{grader_id}.log"

            with open(log_path, "w", encoding="utf-8") as f:
                for submission in submissions:
                    f.write(f"{LogEntry.from_info(submission).serialize()}\n")


class Divider(ABC):
    @abstractmethod
    def initialize(self, assignment: AssignmentInfo) -> bool:
        pass

    def divide(self, assignment: AssignmentInfo) -> Division:
        pass


class DivisionLog:
    def __init__(self):
        self.division: dict[str, list[LogEntry]] = dict()
        self.grader: dict[int, str] = dict()

    def __iter__(self):
        return self.division.items().__iter__()

    def get_entries(self, grader_id: str) -> list[LogEntry]:
        return self.division[grader_id]

    def has_entity_id(self, entity_id: int) -> bool:
        return self.get_grader(entity_id) is not None

    def get_grader(self, entity_id: int) -> Optional[str]:
        return self.grader.get(entity_id, None)

    @staticmethod
    def read(path: Path) -> DivisionLog:
        log = DivisionLog()
        for log_path in path.iterdir():
            if not log_path.is_file() or log_path.suffix != ".log":
                continue

            grader_id = log_path.stem
            log_entries = load_log(log_path)
            log.division[grader_id] = log_entries
            for entry in log_entries:
                log.grader[entry.entity_id] = grader_id

        return log

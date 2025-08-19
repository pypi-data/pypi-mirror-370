from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from bscli.downloader import SubmissionInfo

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    @dataclass
    class Student:
        name: str
        username: str

    entity_id: int
    submission_id: int
    folder_name: str
    students: list[Student]

    def serialize(self) -> str:
        return f'{self.entity_id};{self.submission_id};{self.folder_name};{",".join(f"{s.name} ({s.username})" for s in self.students)}'

    @staticmethod
    def deserialize(line: str):
        parts = line.split(";")
        entity_id = int(parts[0])
        submission_id = int(parts[1])
        folder_name = parts[2]
        students: list[LogEntry.Student] = []
        for student_str in parts[3].split(","):
            name, _, username = student_str.rpartition(" (")
            students.append(LogEntry.Student(name, username[:-1]))

        return LogEntry(entity_id, submission_id, folder_name, students)

    @staticmethod
    def from_info(info: SubmissionInfo):
        return LogEntry(
            info.entity_id,
            info.submission_id,
            info.folder_name,
            [
                LogEntry.Student(s.display_name, s.user_name.lower())
                for s in info.students
            ],
        )


def load_log(path: Path) -> list[LogEntry]:
    return [
        LogEntry.deserialize(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]

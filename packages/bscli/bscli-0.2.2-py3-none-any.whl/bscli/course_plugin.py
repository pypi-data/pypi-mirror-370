from __future__ import annotations

from abc import ABC

from bscli.division import Divider
from bscli.processing import GraderProcessing, SubmissionsProcessing


# NOTE: placeholder and subject to complete overhaul if need be.
class CoursePlugin(ABC):
    def __init__(self, name: str):
        self.name = name

    def initialize(self) -> bool:
        return True

    def get_divider(self, assignment_id: str) -> Divider:
        raise NotImplementedError

    def modify_submission_passes(
        self, passes: list[SubmissionsProcessing]
    ) -> list[SubmissionsProcessing]:
        return passes

    def modify_grader_passes(
        self, passes: list[GraderProcessing]
    ) -> list[GraderProcessing]:
        return passes


class DefaultCoursePlugin(CoursePlugin):
    def __init__(self):
        super().__init__("default")

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bscli.config import AssignmentConfig, Config
from bscli.division import Division
from bscli.downloader import AssignmentInfo
from bscli.processing import GraderProcessing
from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


@dataclass
class GraderSubmissionsConfig:
    """Configuration loaded from grader directory."""

    @dataclass
    class Grader:
        name: str
        email: str

    @dataclass
    class Grade:
        name: str
        type: str
        aliases: dict[str, str]
        max_points: float
        object_max_points: float
        symbols: list[str]

    @dataclass
    class Submission:
        @dataclass
        class Student:
            name: str
            username: str

        entity_id: int
        entity_type: str
        submission_id: int
        submitted_by: int
        students: dict[int, Student]

    org_unit_id: int
    folder_id: int
    group_category_id: Optional[int]
    assignment_id: str
    default_code_block_language: str
    grader: Grader
    grade: Grade
    submissions: dict[str, Submission]

    @staticmethod
    def from_json(obj: dict):
        return GraderSubmissionsConfig(
            org_unit_id=obj["orgUnitId"],
            folder_id=obj["folderId"],
            group_category_id=obj["groupCategoryId"],
            assignment_id=obj["assignmentId"],
            default_code_block_language=obj["defaultCodeBlockLanguage"],
            grader=GraderSubmissionsConfig.Grader(
                name=obj["grader"]["name"], email=obj["grader"]["email"]
            ),
            grade=GraderSubmissionsConfig.Grade(
                name=obj["grade"]["name"],
                type=obj["grade"]["type"],
                aliases=obj["grade"]["aliases"],
                max_points=obj["grade"]["maxPoints"],
                object_max_points=obj["grade"]["objectMaxPoints"],
                symbols=obj["grade"]["symbols"],
            ),
            submissions={
                folder_name: GraderSubmissionsConfig.Submission(
                    entity_id=submission["entityId"],
                    entity_type=submission["entityType"],
                    submission_id=submission["submissionId"],
                    submitted_by=submission["submittedBy"],
                    students={
                        int(user_id): GraderSubmissionsConfig.Submission.Student(
                            name=student["name"], username=student["username"]
                        )
                        for user_id, student in submission["students"].items()
                    },
                )
                for folder_name, submission in obj["submissions"].items()
            },
        )


class CreateGraderConfig(GraderProcessing):
    def __init__(
        self,
        division: Division,
        assignment_info: AssignmentInfo,
        config: Config,
        assignment_config: AssignmentConfig,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.division = division
        self.assignment_info = assignment_info
        self.config = config
        self.assignment_config = assignment_config

    def process_grader(self, grader_path: Path):
        submissions_info = self.division[grader_path.name]
        config_path = grader_path / "grader.json"
        grader_info = self.config.graders[grader_path.name]

        grade_object = self.assignment_info.grade_object
        grade_scheme = self.assignment_info.grade_scheme

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "orgUnitId": self.assignment_info.course.org_unit.id,
                        "folderId": self.assignment_info.assignment.id,
                        "groupCategoryId": self.assignment_info.assignment.group_type_id,
                        "assignmentId": self.assignment_config.identifier,
                        "defaultCodeBlockLanguage": self.assignment_config.default_code_block_language,
                        "draftFeedback": self.assignment_config.draft_feedback,
                        "gradedByFooter": self.assignment_config.graded_by_footer,
                        "grader": {
                            "name": grader_info.name,
                            "email": grader_info.contact_email,
                        },
                        "grade": (
                            {
                                "name": grade_object.name,
                                "type": grade_object.grade_type,
                                "aliases": self.assignment_config.grade_aliases,
                                "maxPoints": self.assignment_info.assignment.assessment.score_denominator,
                                "objectMaxPoints": grade_object.max_points,
                                "symbols": (
                                    [r.symbol for r in grade_scheme.ranges]
                                    if grade_scheme
                                    else [
                                        x
                                        for x in range(
                                            0, int(grade_object.max_points) + 1
                                        )
                                    ]
                                ),
                            }
                            if grade_object
                            else None
                        ),
                        "submissions": {
                            info.folder_name: {
                                "entityId": info.entity_id,
                                "entityType": info.entity_type,
                                "submissionId": info.submission_id,
                                "submittedBy": int(info.submitted_by.identifier),
                                "students": {
                                    int(student.identifier): {
                                        "name": student.display_name,
                                        "username": student.user_name,
                                    }
                                    for student in info.students
                                },
                            }
                            for info in submissions_info
                        },
                    },
                    indent=4,
                    ensure_ascii=False,
                )
            )

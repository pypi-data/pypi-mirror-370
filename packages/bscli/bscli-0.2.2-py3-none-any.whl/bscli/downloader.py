from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from typing import Optional

import bsapi
import bsapi.types

from bscli.progress import ProgressReporter
from bscli.utils import format_filesize

logger = logging.getLogger(__name__)


@dataclass
class SubmissionInfo:
    entity_id: int
    entity_type: str
    submitted_by: bsapi.types.User
    submitted_at: datetime.datetime
    submission_id: int
    folder_name: str
    comment: str
    group_name: Optional[str]
    students: list[bsapi.types.User]


@dataclass
class AssignmentInfo:
    identifier: str
    course: bsapi.types.MyOrgUnitInfo
    assignment: bsapi.types.DropboxFolder
    users: dict[int, bsapi.types.User]
    groups: Optional[dict[int, bsapi.types.GroupData]]
    submissions: list[SubmissionInfo]
    grade_object: Optional[bsapi.types.GradeObject]
    grade_scheme: Optional[bsapi.types.GradeScheme]


class Downloader:
    def __init__(
        self,
        api: bsapi.BSAPI,
        root_path: Path,
        progress_reporter: ProgressReporter = None,
    ):
        self.api = api
        self.root_path = root_path
        self.submissions_path = root_path / "stage" / "submissions"
        self.progress_reporter = progress_reporter

    def download_submission(
        self,
        org_unit_id: int,
        folder_id: int,
        submission: bsapi.types.EntityDropBox,
        users: dict[int, bsapi.types.User],
        groups: dict[int, bsapi.types.GroupData],
    ) -> Optional[SubmissionInfo]:
        entity_id = submission.entity.entity_id
        entity_type = submission.entity.entity_type
        name = submission.entity.get_name()

        if entity_type == "Group":
            folder_name = name.replace(" ", "-").lower()
            students = [users[user_id] for user_id in groups[entity_id].enrollments]
        else:
            folder_name = users[entity_id].user_name.lower()
            students = [users[entity_id]]

        # Find the latest submission if multiple exist, and default to None if no submission was made.
        latest_submission = max(
            submission.submissions, key=attrgetter("submission_date"), default=None
        )
        total_size = (
            sum(map(lambda f_: f_.size, latest_submission.files))
            if latest_submission
            else 0
        )
        logger.info(
            "Downloading submission from %s (%s)", name, format_filesize(total_size)
        )

        if not latest_submission:
            logger.info("Skipping as no submission was made")
            return None

        submission_path = self.submissions_path.joinpath(folder_name)
        submission_path.mkdir(parents=True, exist_ok=True)

        for file in latest_submission.files:
            dest_path = submission_path.joinpath(file.file_name)
            contents = self.api.get_dropbox_folder_submission_file(
                org_unit_id, folder_id, latest_submission.id, file.file_id
            )

            with open(dest_path, "wb") as f:
                f.write(contents)

        return SubmissionInfo(
            entity_id=entity_id,
            entity_type=entity_type,
            submitted_by=users[int(latest_submission.submitted_by.identifier)],
            submitted_at=latest_submission.submission_date,
            submission_id=latest_submission.id,
            folder_name=folder_name,
            comment=latest_submission.comment.text,
            group_name=submission.entity.name,
            students=students,
        )

    def download_submissions(
        self,
        org_unit_id: int,
        folder_id: int,
        ignored_submissions: list[str],
        users: dict[int, bsapi.types.User],
        groups: dict[int, bsapi.types.GroupData],
    ) -> list[SubmissionInfo]:
        logger.info("Obtaining Brightspace dropbox folder submission metadata")
        submissions = self.api.get_dropbox_folder_submissions(org_unit_id, folder_id)
        submissions_info = []

        for idx, submission in enumerate(submissions):
            if self.progress_reporter:
                self.progress_reporter.start(
                    idx + 1, len(submissions), submission.entity.get_name()
                )

            if submission.entity.get_name() in ignored_submissions:
                logger.info("Ignoring submission from %s", submission.entity.get_name())
                continue

            info = self.download_submission(
                org_unit_id, folder_id, submission, users, groups
            )
            if info is not None:
                submissions_info.append(info)

        if self.progress_reporter:
            self.progress_reporter.finish(len(submissions))
        return submissions_info

    def download_assignment(
        self,
        identifier: str,
        course: bsapi.types.MyOrgUnitInfo,
        assignment: bsapi.types.DropboxFolder,
        ignored_submissions: list[str] = None,
    ) -> Optional[AssignmentInfo]:
        """Download assignment submissions with concrete objects (no config needed)."""

        if ignored_submissions is None:
            ignored_submissions = []

        users = {
            int(user.user.identifier): user.user
            for user in self.api.get_users(course.org_unit.id)
        }
        groups = (
            {
                group.group_id: group
                for group in self.api.get_groups(
                    course.org_unit.id, assignment.group_type_id
                )
                if group.enrollments
            }
            if assignment.group_type_id is not None
            else None
        )

        if assignment.due_date and assignment.due_date > datetime.datetime.now(
            datetime.timezone.utc
        ):
            logger.warning(
                'Due date of assignment "%s" has not yet passed', assignment.name
            )

        # Handle grading setup - assignments may not have grade objects
        grade_object = None
        grade_scheme = None

        if assignment.grade_item_id is None:
            logger.warning(
                '⚠️Assignment "%s" is not associated with a grade object - continuing without grading support',
                assignment.name,
            )
        else:
            grade_object = self.api.get_grade_object(
                course.org_unit.id, assignment.grade_item_id
            )

            if grade_object.grade_scheme_id is not None:
                grade_scheme = self.api.get_grade_scheme(
                    course.org_unit.id, grade_object.grade_scheme_id
                )

            if grade_object.grade_type not in ["SelectBox", "Numeric"]:
                logger.fatal(
                    'Assignment "%s" has an unsupported grade type "%s"',
                    assignment.name,
                    grade_object.grade_type,
                )
                return None
            if (
                grade_object.grade_type == "Numeric"
                and assignment.assessment.score_denominator is None
            ):
                logger.fatal(
                    'Assignment "%s" has Numeric grade type but no Score Out Of field set',
                    assignment.name,
                )
                return None

        submissions = self.download_submissions(
            course.org_unit.id,
            assignment.id,
            ignored_submissions,
            users,
            groups,
        )

        return AssignmentInfo(
            identifier,
            course,
            assignment,
            users,
            groups,
            submissions,
            grade_object,
            grade_scheme,
        )

    def download_from_config(
        self, config, assignment_id: str
    ) -> Optional[AssignmentInfo]:
        """Download assignment using config-based lookup (backward compatibility)."""
        if assignment_id not in config.assignments:
            logger.fatal('No assignment with id "%s" exists', assignment_id)
            return None

        import bsapi.helper

        api_helper = bsapi.helper.APIHelper(self.api)
        assignment_config = config.assignments[assignment_id]

        course = api_helper.find_course_by_name(config.course_name)
        assignment = api_helper.find_assignment(
            course.org_unit.id, assignment_config.name
        )

        return self.download_assignment(
            assignment_id, course, assignment, assignment_config.ignored_submissions
        )

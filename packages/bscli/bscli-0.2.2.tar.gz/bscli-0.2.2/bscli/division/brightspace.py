from __future__ import annotations

import logging
import random

import bsapi
import bsapi.helper
import bsapi.types

from bscli.config import Config
from bscli.division import Divider, Division
from bscli.downloader import AssignmentInfo

logger = logging.getLogger(__name__)


class BrightspaceDivider(Divider):
    def __init__(self, api: bsapi.BSAPI, config: Config):
        self.api = api
        self.config = config
        self.user_to_grader: dict[int, tuple[str, str]] = dict()

    def initialize(self, assignment: AssignmentInfo) -> bool:
        assignment_config = self.config.assignments[assignment.identifier]
        helper = bsapi.helper.APIHelper(self.api)

        group_category = helper.find_group_category(
            assignment.course.org_unit.id,
            assignment_config.division.group_category_name,
        )
        groups = self.api.get_groups(
            assignment.course.org_unit.id, group_category.group_category_id
        )

        # TODO: Check if Brightspace data is sane etc

        # Build mapping of student to grader based on grading groups.
        for group in groups:
            grader_id = assignment_config.division.group_mapping[group.name]
            for user_id in group.enrollments:
                if user_id in self.user_to_grader:
                    # Student is already in a grading group, so it is in multiple groups.
                    student = assignment.users[user_id]
                    prior_grader, prior_group = self.user_to_grader[user_id]
                    logger.warning(
                        "Student %s is in multiple grading groups (%s graded by %s, and %s graded by %s)",
                        student.display_name,
                        prior_group,
                        prior_grader,
                        group.name,
                        grader_id,
                    )
                else:
                    self.user_to_grader[user_id] = (grader_id, group.name)

        # Check if all students are in a grading group.
        missing_students = [
            student
            for user_id, student in assignment.users.items()
            if user_id not in self.user_to_grader
        ]

        for student in missing_students:
            logger.warning(
                "Student %s is not in any grading group", student.display_name
            )

        return True

    def divide(self, assignment: AssignmentInfo) -> Division:
        assignment_config = self.config.assignments[assignment.identifier]
        graders = set(assignment_config.division.group_mapping.values())
        division = Division(graders)

        for submission in assignment.submissions:
            submitter_id = int(submission.submitted_by.identifier)

            # Ensure a grader exists for this submission.
            if submitter_id not in self.user_to_grader:
                available_graders: set[str] = set()

                # No grader for the submitter of this submission, so look at partners if any exist.
                for student in submission.students:
                    # Skip submitter itself.
                    if student.identifier == submission.submitted_by.identifier:
                        continue

                    # Check if the partner has a grader, and if so add it to the set of possible graders.
                    partner_grader, _ = self.user_to_grader.get(
                        int(student.identifier), (None, None)
                    )
                    if partner_grader:
                        available_graders.add(partner_grader)

                # If no partner graders are available, then consider every grader as a possible grader.
                had_partner_grader = len(available_graders) > 0
                if not available_graders:
                    available_graders = graders

                # Select a grader randomly from the set of possible graders.
                selected_grader = random.choice(list(available_graders))
                self.user_to_grader[submitter_id] = (selected_grader, "")
                if had_partner_grader:
                    if len(available_graders) == 1:
                        logger.warning(
                            "Student %s is not in any grading group, selected %s due to partner",
                            submission.submitted_by.display_name,
                            selected_grader,
                        )
                    else:
                        logger.warning(
                            "Student %s is not in any grading group, selected %s at random due to partner",
                            submission.submitted_by.display_name,
                            selected_grader,
                        )
                else:
                    logger.warning(
                        "Student %s is not in any grading group, selected %s at random",
                        submission.submitted_by.display_name,
                        selected_grader,
                    )

            # Find grader and assign submission to that grader.
            grader_id, _ = self.user_to_grader[submitter_id]
            division.assign_to(grader_id, submission)

        return division

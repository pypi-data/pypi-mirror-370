from __future__ import annotations

import logging
from operator import itemgetter
from pathlib import Path

from bscli.config import Config
from bscli.division import Divider, Division
from bscli.division.random_divider import RandomDivider
from bscli.downloader import AssignmentInfo, SubmissionInfo

logger = logging.getLogger(__name__)


class PersistentDivider(Divider):
    def __init__(self, config: Config, data_path: Path):
        self.config = config
        self.data_path = data_path

    def initialize(self, assignment: AssignmentInfo) -> bool:
        return True

    @staticmethod
    def _save_persist_list(path: Path, submissions: list[SubmissionInfo]):
        path.write_text("\n".join(s.folder_name for s in submissions), encoding="utf-8")

    @staticmethod
    def _load_persist_list(path: Path) -> list[str]:
        if path.is_file():
            return path.read_text(encoding="utf-8").splitlines()
        else:
            return []

    def divide(self, assignment: AssignmentInfo) -> Division:
        assignment_config = self.config.assignments[assignment.identifier]
        grader_weights = assignment_config.division.grader_weights
        category = assignment_config.division.group_category_name
        category_path = self.data_path / "divisions" / category

        # Normalize weights so that they sum to 1.
        weight_sum = sum(grader_weights.values())
        for grader_id, weight in grader_weights.items():
            grader_weights[grader_id] = weight / weight_sum

        if not category_path.is_dir():
            # No prior division exists, so create a random one now, based on same graders and weights.
            random_divider = RandomDivider(self.config)
            division = random_divider.divide(assignment)
        else:
            # Load previously created persist lists, transform it into a mapping of `folder_name` to `grader_id`.
            graders = grader_weights.keys()
            persist = {
                grader_id: self._load_persist_list(category_path / grader_id)
                for grader_id in graders
            }
            to_grader: dict[str, str] = dict()
            for grader_id, submissions in persist.items():
                for folder_name in submissions:
                    to_grader[folder_name] = grader_id
            division = Division(graders)

            # Partition submissions into those already assigned to a grader, and those not yet assigned to one.
            assigned: list[SubmissionInfo] = []
            unassigned: list[SubmissionInfo] = []
            for submission in assignment.submissions:
                (
                    assigned if submission.folder_name in to_grader else unassigned
                ).append(submission)

            # Assigned the already assigned submissions to their prior grader.
            for submission in assigned:
                division.assign_to(to_grader[submission.folder_name], submission)

            # Assign unassigned submissions to graders, taking weights and assigned submission count in division into account.
            for submission in unassigned:
                # Get grader based on grader the furthest away from target workload.
                grader_id, _ = max(
                    [
                        (
                            grader_id,
                            weight * len(assignment.submissions)
                            - len(division[grader_id]),
                        )
                        for grader_id, weight in grader_weights.items()
                    ],
                    key=itemgetter(1),
                )
                division.assign_to(grader_id, submission)

        # Save division to persist lists.
        category_path.mkdir(parents=True, exist_ok=True)
        for grader_id, submissions in division:
            self._save_persist_list(category_path / grader_id, submissions)

        return division

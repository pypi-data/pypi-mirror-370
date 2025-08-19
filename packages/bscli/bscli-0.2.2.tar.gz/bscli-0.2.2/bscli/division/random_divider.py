from __future__ import annotations

import logging
import random

from bscli.config import Config
from bscli.division import Divider, Division
from bscli.downloader import AssignmentInfo

logger = logging.getLogger(__name__)


class RandomDivider(Divider):
    def __init__(self, config: Config):
        self.config = config

    def initialize(self, assignment: AssignmentInfo) -> bool:
        return True

    def divide(self, assignment: AssignmentInfo) -> Division:
        assignment_config = self.config.assignments[assignment.identifier]
        grader_weights = assignment_config.division.grader_weights
        division = Division(grader_weights.keys())

        # Normalize weights so that they sum to 1.
        weight_sum = sum(grader_weights.values())
        for grader_id, weight in grader_weights.items():
            grader_weights[grader_id] = weight / weight_sum

        # Make copy of the list of submissions, and randomly shuffle it.
        total_submissions = len(assignment.submissions)
        to_divide = list(assignment.submissions)
        random.shuffle(to_divide)

        # Assign submissions from the shuffled list based on normalized weights.
        for grader_id, weight in grader_weights.items():
            # Add a random number between 0.0 and 1.0, then floor to do probabilistic rounding.
            # If the 'target' is 10.4, this means 40% of the time we get 11, and 60% of the time 10.
            # This should produce more accurate weight based divisions on average, compared to regular rounding/floor/ceiling.
            target = int(weight * total_submissions + random.random())
            num = min(target, len(to_divide))
            division.assign_many_to(grader_id, to_divide[:num])
            to_divide = to_divide[num:]

        # Mop up by dividing any remaining submissions randomly in case we did not get an exact division.
        for submission in to_divide:
            division.assign_randomly(submission)

        return division

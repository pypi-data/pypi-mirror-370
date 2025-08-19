import logging
from pathlib import Path

from bscli.downloader import AssignmentInfo
from bscli.processing import SubmissionsProcessing
from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


class CreateFeedbackTemplate(SubmissionsProcessing):
    def __init__(
        self, info: AssignmentInfo, progress_reporter: ProgressReporter = None
    ):
        super().__init__(progress_reporter)
        self.info = info
        self.submissions_info = {si.folder_name: si for si in info.submissions}

    def process_submission(self, submission_path: Path):
        assert (
            submission_path.name in self.submissions_info
        ), f"No submission info for folder {submission_path.name}"
        submission_info = self.submissions_info[submission_path.name]

        # Format as local time zone, rather than UTC.
        # This assumes the machine running this has the same timezone as the graders.
        submitted_at = submission_info.submitted_at.astimezone().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Mark late submissions and show how late they are to give graders more context.
        if (
            self.info.assignment.due_date
            and submission_info.submitted_at > self.info.assignment.due_date
        ):
            # No way to pick our own formatting, so manually break it down into the desired components.
            late_by = submission_info.submitted_at - self.info.assignment.due_date
            days = late_by.days
            hours = late_by.seconds // 3600
            minutes = (late_by.seconds // 60) % 60
            seconds = late_by.seconds % 60
            submitted_at += f' (!!!LATE!!! {days} day{"s" if days != 1 else ""}, {hours}h:{minutes}m:{seconds}s)'

        with open(submission_path / "feedback.txt", "w", encoding="utf-8") as f:
            f.write(f"Assignment: {self.info.assignment.name}\n")
            f.write(
                f"Submitted by: {submission_info.submitted_by.display_name} ({submission_info.submitted_by.user_name.lower()})\n"
            )
            f.write(f"Submitted at: {submitted_at}\n")
            if self.info.groups:
                f.write(f"Group: {submission_info.group_name}\n")
                for student in submission_info.students:
                    f.write(
                        f"Group member: {student.display_name} ({student.user_name.lower()})\n"
                    )
            f.write("====================[Brightspace comment]====================\n")
            f.write(f"{submission_info.comment}\n")

            if self.info.grade_object:
                f.write(
                    "====================[Enter grade below]======================\n"
                )
                f.write("TODO\n")
                f.write(
                    "====================[Enter feedback below]===================\n"
                )
                f.write("\n")

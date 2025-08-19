import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bsapi
import bsapi.feedback
import bsapi.types

from bscli.processing.graders.grader_config import GraderSubmissionsConfig

logger = logging.getLogger(__name__)


def handle(ctx, args):
    """Handle upload command."""
    submissions_path = args.submissions_path
    if not submissions_path.is_absolute():
        submissions_path = ctx.root_path / submissions_path

    if not submissions_path.exists():
        print(f"❌ Submissions directory not found: {submissions_path}")
        return

    upload_feedback(ctx, submissions_path, args.draft, args.force)


@dataclass
class ProcessedGrade:
    symbol: Optional[str]
    score: Optional[float]
    placeholder: bool

    @staticmethod
    def from_symbol(symbol: str):
        return ProcessedGrade(symbol, None, False)

    @staticmethod
    def from_score(score: float):
        return ProcessedGrade(None, score, False)

    @staticmethod
    def from_placeholder():
        return ProcessedGrade(None, None, True)

    def __str__(self) -> str:
        if self.placeholder:
            return "<None>"
        elif self.symbol is not None:
            return self.symbol
        elif self.score is not None:
            return str(self.score)
        else:
            return "<None>"


@dataclass
class ProcessedFeedback:
    grade: str
    feedback: str


@dataclass
class SubmissionInfo:
    folder_name: str
    path: Path
    submission: GraderSubmissionsConfig.Submission
    grade: ProcessedGrade
    feedback: str
    feedback_html: str


def load_grader_config(grader_path: Path) -> Optional[GraderSubmissionsConfig]:
    """Load grader configuration from directory."""
    config_path = grader_path / "grader.json"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        return GraderSubmissionsConfig.from_json(config_data)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None


def process_grade(
    grade: str, name: str, config: GraderSubmissionsConfig
) -> Optional[ProcessedGrade]:
    """Process and validate a grade string."""
    if grade == "TODO":
        return ProcessedGrade.from_placeholder()

    # Apply grade aliases
    for alias, to in config.grade.aliases.items():
        if grade.lower() == alias.lower():
            grade = to

    if config.grade.type == "Numeric":
        try:
            grade = grade.replace(",", ".")
            score = float(grade)

            if score < 0:
                logger.error(
                    'Invalid grade "%s" for "%s" (cannot be negative)', grade, name
                )
            elif score > config.grade.max_points:
                logger.error(
                    'Invalid grade "%s" for "%s" (cannot exceed %s)',
                    grade,
                    name,
                    config.grade.max_points,
                )
            else:
                return ProcessedGrade.from_score(score)
        except ValueError:
            logger.error(
                'Invalid grade "%s" for "%s" (could not parse as float)', grade, name
            )

        return None
    elif config.grade.type == "SelectBox":
        for symbol in config.grade.symbols:
            if grade.lower() == symbol.lower():
                return ProcessedGrade.from_symbol(symbol)

        logger.error(
            'Invalid grade symbol "%s" for "%s" (valid options are %s)',
            grade,
            name,
            ", ".join(f'"{s}"' for s in config.grade.symbols),
        )
        if config.grade.aliases:
            logger.error("Available grade aliases:")
            for k, v in config.grade.aliases.items():
                logger.error("- %s => %s", k, v)
        return None
    else:
        logger.error('Grade type "%s" is not supported', config.grade.type)
        return None


def process_feedback_file(path: Path, name: str) -> Optional[ProcessedFeedback]:
    """Parse feedback file for grade and feedback content."""
    grade_header = "====================[Enter grade below]======================"
    feedback_header = "====================[Enter feedback below]==================="

    try:
        feedback_text = path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f'Could not read feedback file for "%s": %s', name, e)
        return None

    grade_header_idx = feedback_text.find(grade_header)
    feedback_header_idx = feedback_text.find(feedback_header)

    if grade_header_idx < 0:
        logger.error(f'Feedback file of "%s" is missing grade field header', name)
        return None
    if feedback_header_idx < 0:
        logger.error(f'Feedback file of "%s" is missing feedback field header', name)
        return None
    if feedback_header_idx < grade_header_idx:
        logger.error(
            f'Feedback file of "%s" has feedback field header before grade field header',
            name,
        )
        return None

    grade_field = feedback_text[
        grade_header_idx + len(grade_header) : feedback_header_idx
    ].strip()
    feedback_field = feedback_text[feedback_header_idx + len(feedback_header) :].strip()

    if not grade_field:
        logger.error(f'Feedback file of "%s" has an empty grade field', name)
        return None

    return ProcessedFeedback(grade_field, feedback_field)


def process_submission(
    path: Path,
    submission: GraderSubmissionsConfig.Submission,
    config: GraderSubmissionsConfig,
) -> Optional[SubmissionInfo]:
    """Process a single submission directory."""
    name = path.name
    feedback_path = path / "feedback.txt"
    submission_from = submission.students[submission.submitted_by]
    submitted_by = f"{submission_from.name} ({submission_from.username.lower()})"

    print(f"  Processing {name} (submitted by {submitted_by})")

    if not feedback_path.is_file():
        logger.error('Skipping "%s" due to missing feedback file', name)
        return None

    processed_feedback = process_feedback_file(feedback_path, name)
    if processed_feedback is None:
        logger.error('Skipping "%s" due to errors while processing feedback file', name)
        return None

    grade = process_grade(processed_feedback.grade, name, config)
    if grade is None:
        logger.error('Skipping "%s" due to errors while processing grade', name)
        return None
    elif grade.placeholder:
        logger.warning('Skipping "%s" as it has not yet been graded', name)
        return None

    # Finalize feedback with grader footer
    feedback = processed_feedback.feedback
    feedback += f"\n\nYour submission was graded by {config.grader.name} (you can contact me using {config.grader.email})"

    # Convert to HTML
    feedback_encoder = bsapi.feedback.BasicCodeEncoder(
        config.default_code_block_language, line_numbers=True
    )
    feedback_html = feedback_encoder.encode(feedback)

    return SubmissionInfo(name, path, submission, grade, feedback, feedback_html)


def get_conflict_resolution(force: bool) -> str:
    """Get user input for conflict resolution."""
    if force:
        return "overwrite"

    while True:
        print("\nConflict resolution options:")
        print("  overwrite - Replace existing feedback with yours")
        print("  skip      - Keep existing feedback, skip yours")
        print("  cancel    - Abort upload")

        choice = input("Choose [overwrite/skip/cancel]: ").lower().strip()
        if choice in ["overwrite", "skip", "cancel"]:
            return choice
        print("Invalid choice, please try again")


def ask_for_assignment_deletion(successfully_uploaded: list[SubmissionInfo]) -> bool:
    """Ask user if they want to delete assignment folders for privacy."""
    if not successfully_uploaded:
        return False
    
    print("\n🔒 Privacy Options")
    print(f"You have successfully uploaded feedback for {len(successfully_uploaded)} assignment(s).")
    print("For privacy reasons, you may want to delete the local assignment folders.")
    print("This will only delete folders where feedback was successfully uploaded.")
    
    while True:
        choice = input("\nDo you want to delete the successfully uploaded assignment folders? [y/N]: ").lower().strip()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no', '']:
            return False
        print("Please answer 'y' for yes or 'n' for no.")


def delete_assignment_folders(successfully_uploaded: list[SubmissionInfo]):
    """Delete assignment folders for successfully uploaded submissions."""
    print("\n🗑️  Deleting assignment folders...")
    deleted_count = 0
    
    for info in successfully_uploaded:
        try:
            shutil.rmtree(info.path)
            print(f"  ✅ Deleted {info.folder_name}")
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete folder {info.folder_name}: {e}")
            print(f"  ❌ Failed to delete {info.folder_name}: {e}")
    
    print(f"\n📊 Deletion complete: {deleted_count}/{len(successfully_uploaded)} folders deleted")
    if deleted_count == len(successfully_uploaded):
        print("🎉 All assignment folders successfully deleted for privacy")


def upload_feedback(ctx, submissions_path: Path, draft: bool, force: bool):
    """Upload feedback from grader directory to Brightspace."""
    print(f"📤 Uploading feedback from: {submissions_path}")

    # Load grader configuration
    config = load_grader_config(submissions_path)
    if config is None:
        return

    # Find submissions directory
    submissions_path = submissions_path / "submissions"
    if not submissions_path.exists():
        print(f"❌ Submissions directory not found: {submissions_path}")
        return

    # Process all submissions
    print("🔍 Processing submissions...")
    submissions_info: list[SubmissionInfo] = []

    for folder_name, submission in config.submissions.items():
        submission_path = submissions_path / folder_name

        if not submission_path.is_dir():
            print(f"  Skipping {folder_name} (directory not found)")
            continue

        info = process_submission(submission_path, submission, config)
        if info is not None:
            submissions_info.append(info)

    if not submissions_info:
        print("❌ No valid submissions found to upload")
        return

    print(f"✅ Found {len(submissions_info)} submissions ready for upload")

    # Check for existing feedback
    api = ctx.api()
    print("🔍 Checking for existing feedback...")

    conflicts = []
    for info in submissions_info:
        try:
            existing = api.get_dropbox_folder_submission_feedback(
                config.org_unit_id,
                config.folder_id,
                info.submission.entity_type,
                info.submission.entity_id,
            )
            if existing:
                conflicts.append((info, existing))
        except bsapi.APIError as e:
            logger.warning(
                f"Could not check existing feedback for {info.folder_name}: {e}"
            )

    # Handle conflicts
    if conflicts:
        print(f"⚠️  Found {len(conflicts)} submissions with existing feedback")
        resolution = get_conflict_resolution(force)

        if resolution == "cancel":
            print("❌ Upload cancelled")
            return
        elif resolution == "skip":
            # Remove conflicted submissions
            for info, _ in conflicts:
                submissions_info.remove(info)
                print(f"  Skipping {info.folder_name} (existing feedback kept)")

    if not submissions_info:
        print("❌ No submissions left to upload after conflict resolution")
        return

    # Upload feedback
    print("📤 Uploading feedback to Brightspace...")
    successfully_uploaded: list[SubmissionInfo] = []

    for info in submissions_info:
        try:
            if config.grade.type == "SelectBox":
                api.set_dropbox_folder_submission_feedback(
                    config.org_unit_id,
                    config.folder_id,
                    info.submission.entity_type,
                    info.submission.entity_id,
                    symbol=info.grade.symbol,
                    html_feedback=info.feedback_html,
                    draft=draft,
                )
            elif config.grade.type == "Numeric":
                # Scale score if needed
                scaled_score = (
                    info.grade.score / config.grade.max_points
                ) * config.grade.object_max_points
                api.set_dropbox_folder_submission_feedback(
                    config.org_unit_id,
                    config.folder_id,
                    info.submission.entity_type,
                    info.submission.entity_id,
                    score=scaled_score,
                    html_feedback=info.feedback_html,
                    draft=draft,
                )

            # Handle file attachments
            attach_path = info.path / "__attach_feedback"
            if attach_path.exists() and attach_path.is_dir():
                for file_path in attach_path.iterdir():
                    if file_path.is_file():
                        print(f"    Attaching {file_path.name}")
                        api.add_dropbox_folder_submission_feedback_file(
                            config.org_unit_id,
                            config.folder_id,
                            info.submission.entity_type,
                            info.submission.entity_id,
                            file_path,
                        )

            successfully_uploaded.append(info)
            status = "draft" if draft else "published"
            print(f"  ✅ {info.folder_name} (grade: {info.grade}, {status})")

        except bsapi.APIError as e:
            logger.error(f"Failed to upload feedback for {info.folder_name}: {e}")
            print(f"  ❌ {info.folder_name} (upload failed)")

    # Summary
    success_count = len(successfully_uploaded)
    print(f"\n📊 Upload complete: {success_count}/{len(submissions_info)} successful")
    if success_count < len(submissions_info):
        print("⚠️  Some uploads failed - check logs for details")
    else:
        status = "draft" if draft else "published"
        print(f"🎉 All feedback uploaded successfully as {status}")
    
    # Ask about deleting assignment folders for privacy
    if successfully_uploaded and ask_for_assignment_deletion(successfully_uploaded):
        delete_assignment_folders(successfully_uploaded)

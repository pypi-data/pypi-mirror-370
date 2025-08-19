import logging
import shutil

from bscli.division.brightspace import BrightspaceDivider
from bscli.division.persistent import PersistentDivider
from bscli.division.random_divider import RandomDivider
from bscli.downloader import Downloader
from bscli.filesender import FileSenderUploader
from bscli.processing import NOPProcessing, SubmissionsProcessing, GraderProcessing
from bscli.processing.graders.create_archive import (
    MoveToGraderFolder,
    CreateGraderArchives,
)
from bscli.processing.graders.feedback_template import CreateFeedbackTemplate
from bscli.processing.graders.grader_config import CreateGraderConfig
from bscli.processing.graders.grading_instructions import (
    InjectGraderFiles,
    AddGraderFiles,
    CreateGradingInstructions,
)
from bscli.processing.submissions.docx_to_pdf import DocxToPdf
from bscli.processing.submissions.extract_archives import ExtractArchives
from bscli.processing.submissions.fix_permissions import FixFilePermissions
from bscli.processing.submissions.flatten import Flatten, SmartFlatten
from bscli.processing.submissions.inject_files import InjectFiles
from bscli.processing.submissions.remove_files import RemoveFiles
from bscli.progress import Report

logger = logging.getLogger(__name__)


def handle(ctx, args):
    """Handle distribute command."""
    if not hasattr(args, "assignment_id") or args.assignment_id is None:
        print("❌ Distribute command requires an assignment ID")
        print("\nUsage: bscli distribute <assignment-id> [--no-upload]")
        return

    if not ctx.is_valid_assignment_id(args.assignment_id):
        print(f"❌ Unknown assignment: {args.assignment_id}")
        print("\nUse 'bscli list assignments' to see available assignments")
        return

    distribute(ctx, args.assignment_id, getattr(args, "no_upload", False))


def distribute(ctx, assignment_id: str, no_upload: bool = False):
    """Distribute an assignment."""
    config = ctx.course_config()
    api = ctx.api()

    assignment_config = config.assignments[assignment_id]
    root_path = ctx.root_path
    stage_path = root_path / "stage"
    submissions_path = stage_path / "submissions"
    graders_path = stage_path / "graders"
    data_path = root_path / "data"
    inject_path = data_path / "inject"
    grader_data_path = ctx.package_data_path() / "grader"
    course_path = data_path / "course" / config.course
    distributions_path = root_path / "distributions"
    logs_path = root_path / "logs"

    # Download submissions
    downloader = Downloader(api, root_path, Report("Download submissions"))
    assignment_info = downloader.download_from_config(config, assignment_id)
    if assignment_info is None:
        logger.fatal("Failed to download submissions, abandoning distribution")
        return

    # Initialize divider
    division_method = assignment_config.division.method
    assert division_method in [
        "random",
        "persistent",
        "brightspace",
        "custom",
    ], f'unknown division method "{division_method}"'

    match division_method:
        case "random":
            divider = RandomDivider(config)
        case "persistent":
            divider = PersistentDivider(config, data_path)
        case "brightspace":
            divider = BrightspaceDivider(api, config)
        case "custom":
            divider = ctx.course_plugin().get_divider(assignment_id)
        case _:
            assert False, "Unreachable"

    if not divider.initialize(assignment_info):
        logger.fatal("Failed to initialize divider, abandoning distribution")
        return

    division = divider.divide(assignment_info)
    division.write_logs(logs_path / assignment_id)

    # Configure file hierarchy processing
    file_hierarchy = assignment_config.file_hierarchy
    assert file_hierarchy in [
        "flatten",
        "smart",
        "original",
    ], f'unknown file hierarchy "{file_hierarchy}"'

    match file_hierarchy:
        case "flatten":
            file_hierarchy_pass = Flatten(Report("Flatten files"))
        case "smart":
            file_hierarchy_pass = SmartFlatten(Report("Smart flatten files"))
        case "original":
            file_hierarchy_pass = NOPProcessing()
        case _:
            assert False, "Unreachable"

    # Configure processing passes
    submission_passes: list[SubmissionsProcessing] = [
        ExtractArchives(Report("Extract archives")),
        FixFilePermissions(Report("Fix file permissions")),
        RemoveFiles(assignment_config, Report("Remove files")),
        DocxToPdf(Report("Convert DOCX to PDF")),
        file_hierarchy_pass,
        InjectFiles(assignment_config, inject_path, Report("Inject files")),
        CreateFeedbackTemplate(assignment_info, Report("Create feedback templates")),
        MoveToGraderFolder(division, graders_path, Report("Move to graders")),
    ]

    grader_passes: list[GraderProcessing] = [
        InjectGraderFiles(
            assignment_config, inject_path, Report("Inject grader files")
        ),
        AddGraderFiles(grader_data_path, course_path, Report("Add grader files")),
        CreateGraderConfig(
            division,
            assignment_info,
            config,
            assignment_config,
            Report("Create grader configs"),
        ),
        CreateGradingInstructions(
            assignment_info,
            assignment_config,
            Report("Create grading instructions"),
        ),
        CreateGraderArchives(
            distributions_path, assignment_config, Report("Create grader archives")
        ),
    ]

    # Allow course plugin to modify passes
    course_plugin = ctx.course_plugin()
    submission_passes = course_plugin.modify_submission_passes(submission_passes)
    grader_passes = course_plugin.modify_grader_passes(grader_passes)

    # Execute processing passes
    for pass_ in submission_passes:
        pass_.execute(submissions_path)
    for pass_ in grader_passes:
        pass_.execute(graders_path)

    if no_upload:
        print("Skipping upload to FileSender (--no-upload flag)")
        return

    # Upload to FileSender
    print("Uploading files via FileSender...")
    filesender_config = ctx.filesender_config()
    uploader = FileSenderUploader(distributions_path, config, filesender_config)

    if uploader.upload(
        assignment_id,
        assignment_config,
        assignment_info.course.org_unit.name,
        assignment_info.assignment.name,
    ):
        print(
            "📧 FileSender upload completed successfully. Graders have received emails with their archives."
        )

        # Log upload status
        failed_uploads = []
        for grader_id in config.graders:
            status = uploader.get_upload_status(grader_id)
            if status:
                if status["status"] == "failed":
                    failed_uploads.append(
                        f"  ❌ {grader_id}: {status.get('error', 'Upload failed')}"
                    )

        if failed_uploads:
            print("\n⚠️  Some uploads failed:")
            for failure in failed_uploads:
                print(failure)

        # Clean up stage directory
        shutil.rmtree(stage_path, ignore_errors=True)
        print("\n✅ Distribution complete!")
    else:
        logger.fatal("Failed to upload via FileSender")
        print("❌ Stage directory preserved for debugging")

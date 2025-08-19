import logging
import shutil
from pathlib import Path
from bscli.downloader import Downloader
from bscli.progress import Report

logger = logging.getLogger(__name__)


def handle(ctx, args):
    """Handle download command."""
    if args.course_id and args.brightspace_assignment_id:
        download_direct(ctx, args.course_id, args.brightspace_assignment_id, args.path)
    elif args.assignment_id:
        if not ctx.is_valid_assignment_id(args.assignment_id):
            return
        download_configured(ctx, args.assignment_id, args.path)
    else:
        print("❌ Download command requires either:")
        print("   • assignment_id (with course.json)")
        print("   • --course-id and --assignment-id (without course.json)")
        print()
        print("Examples:")
        print("   bscli download homework-1")
        print("   bscli download --course-id 12345 --assignment-id 54321")
        print()
        print("💡 Use 'bscli list assignments' to see available assignments")


def _execute_download(ctx, downloader_func, assignment_name: str, download_path: Path):
    """Execute download with common file handling logic."""
    temp_root = ctx.root_path / ".bscli_temp"
    temp_root.mkdir(exist_ok=True)

    try:
        print("📥 Starting download...")
        downloader = Downloader(ctx.api(), temp_root, Report("Download submissions"))
        assignment_info = downloader_func(downloader)

        if assignment_info is None:
            print("❌ Failed to download submissions")
            print("💡 Check your network connection and permissions")
            return False

        # Move downloaded files to target location
        source_path = temp_root / "stage" / "submissions"
        if source_path.exists():
            download_path.mkdir(parents=True, exist_ok=True)

            print("📁 Organizing downloaded files...")
            file_count = 0
            for item in source_path.iterdir():
                target = download_path / item.name
                if target.exists():
                    shutil.rmtree(target) if target.is_dir() else target.unlink()
                shutil.move(str(item), str(target))
                file_count += 1

            print(
                f"✅ Successfully downloaded {file_count} submissions for '{assignment_name}'"
            )
            print(f"📁 Files saved to: {download_path}")
            return True
        else:
            print("❌ No submissions found to download")
            print("💡 Check if assignment has any submitted work")
            return False

    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("💡 Try again or check your API configuration")
        return False
    finally:
        if temp_root.exists():
            shutil.rmtree(temp_root, ignore_errors=True)


def download_configured(ctx, assignment_id: str, download_path: Path = None):
    """Download submissions using course.json configuration."""
    config = ctx.course_config()
    assignment_config = config.assignments[assignment_id]

    if download_path is None:
        download_path = ctx.root_path / assignment_config.name
    elif not download_path.is_absolute():
        download_path = ctx.root_path / download_path

    print(f"📚 Course: {config.course_name}")
    print(f"📝 Assignment: {assignment_id} ({assignment_config.name})")
    print(f"📁 Target path: {download_path}")

    def do_download(downloader):
        return downloader.download_from_config(config, assignment_id)

    success = _execute_download(ctx, do_download, assignment_config.name, download_path)
    if not success:
        logger.error("Failed to download submissions for assignment: %s", assignment_id)


def download_direct(
    ctx, course_id: int, assignment_id: int, download_path: Path = None
):
    """Download submissions using direct Brightspace IDs."""
    print("🔍 Looking up course and assignment details...")
    api = ctx.api()

    # Get course and assignment details
    try:
        enrollments = api.get_course_enrollments()
        course_enrollment = next(
            (e for e in enrollments if e.org_unit.id == course_id), None
        )

        if not course_enrollment:
            print(f"❌ Course {course_id} not found in your enrollments")
            print("💡 Use 'bscli list courses' to see available courses")
            return

        dropbox_folders = api.get_dropbox_folders(course_id)
        assignment = next((f for f in dropbox_folders if f.id == assignment_id), None)

        if not assignment:
            print(f"❌ Assignment {assignment_id} not found in course {course_id}")
            print(
                f"💡 Use 'bscli list assignments --course-id {course_id}' to see available assignments"
            )
            return

    except Exception as e:
        print(f"❌ Failed to lookup course/assignment: {e}")
        print("💡 Check your network connection and permissions")
        return

    if download_path is None:
        safe_name = "".join(
            c for c in assignment.name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        download_path = ctx.root_path / safe_name
    elif not download_path.is_absolute():
        download_path = ctx.root_path / download_path

    print(f"📚 Course: {course_enrollment.org_unit.name}")
    print(f"📝 Assignment: {assignment.name}")
    print(f"📁 Target path: {download_path}")

    def do_download(downloader):
        return downloader.download_assignment(
            f"{assignment.name}", course_enrollment, assignment, []
        )

    success = _execute_download(ctx, do_download, assignment.name, download_path)
    if not success:
        logger.error(
            "Failed to download submissions for course %s, assignment %s",
            course_id,
            assignment_id,
        )

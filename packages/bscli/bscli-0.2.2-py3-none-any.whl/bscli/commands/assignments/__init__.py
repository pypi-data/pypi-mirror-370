import argparse
from pathlib import Path
from bscli.commands.assignments import distribute, download
from bscli.commands.assignments.list import ListAssignmentsCommand
from bscli.commands.assignments.find_grader import find_grader
from bscli.commands.assignments.list_graders import list_graders
from bscli.commands.assignments.list_deadlines import list_deadlines
from bscli.commands.base import BaseCommand, BaseGroupCommand, DualModeCommand, validate_assignment_id


class DistributeCommand(BaseCommand):
    """Distribute assignments to graders."""

    name = "distribute"
    help = "Distribute assignments to graders"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("assignment_id", nargs="?", help="Assignment identifier (required - direct mode not supported)")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )
        parser.add_argument("--force", action="store_true", help="Force redistribution")
        parser.add_argument(
            "--no-upload", action="store_true", help="Skip FileSender upload"
        )

    def validate_args(self, ctx, args: argparse.Namespace) -> bool:
        """Validate arguments based on the flags provided."""
        if not args.assignment_id:
            # assignment_id is required for distribution
            parser = argparse.ArgumentParser()
            parser.error("assignment_id is required for distribution (direct mode not supported)")
            return False
        return True

    def execute(self, ctx, args: argparse.Namespace) -> None:
        distribute.handle(ctx, args)


class DownloadCommand(DualModeCommand):
    """Download assignment submissions."""

    name = "download"
    help = "Download assignment submissions"

    def setup_command_parser(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--path", type=Path, help="Download path")

    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute download in direct mode."""
        from bscli.commands.assignments.download import download_direct
        download_direct(ctx, course_id, assignment_id, args.path)

    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute download in config mode."""
        from bscli.commands.assignments.download import download_configured
        download_configured(ctx, assignment_id, args.path)


class FindGraderCommand(BaseCommand):
    """Find grader for assignment submissions."""

    name = "find-grader"
    help = "Find grader for assignment submissions"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "search", help="Search term (student name, username, or folder name)"
        )

    def execute(self, ctx, args: argparse.Namespace) -> None:
        find_grader(ctx, args.search)


class GradingProgressCommand(DualModeCommand):
    """Check grading progress for assignments."""

    name = "grading-progress"
    help = "Check grading progress for assignments"

    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute grading progress check in direct mode."""
        from bscli.commands.assignments.grading_progress import check_grading_progress_direct
        check_grading_progress_direct(ctx, course_id, assignment_id)

    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute grading progress check in config mode."""
        from bscli.commands.assignments.grading_progress import check_grading_progress_config
        check_grading_progress_config(ctx, assignment_id)


class CheckGradingGroupsCommand(DualModeCommand):
    """Check Brightspace grading groups configuration for assignments."""

    name = "check-grading-groups"
    help = "Check Brightspace grading groups configuration for assignments"

    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute grading groups check in direct mode."""
        print("❌ Grading groups check is not supported in direct mode")
        print("💡 Use assignment_id with course.json for grading groups validation")
        print("💡 This feature requires grading group configuration from course.json")

    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute grading groups check in config mode."""
        from bscli.commands.assignments.check_grading_groups import check_grading_groups_config
        check_grading_groups_config(ctx, assignment_id)


class ListSubmissionsCommand(DualModeCommand):
    """List submissions with various filters."""

    name = "list-submissions"
    help = "List submissions with various filters"

    def setup_command_parser(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        # Create a custom argument group for better help organization
        filter_group = parser.add_mutually_exclusive_group()
        filter_group.add_argument("--ungraded", action="store_true", help="List ungraded submissions")
        filter_group.add_argument("--undistributed", action="store_true", help="List undistributed submissions")

    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute list submissions in direct mode."""
        from bscli.commands.assignments.list_submissions import list_all_submissions_direct, list_ungraded_direct
        
        if args.ungraded:
            list_ungraded_direct(ctx, course_id, assignment_id)
        elif args.undistributed:
            print("❌ --undistributed is not supported in direct mode")
            print("💡 Use assignment_id with course.json for undistributed submissions")
        else:
            list_all_submissions_direct(ctx, course_id, assignment_id)

    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute list submissions in config mode."""
        from bscli.commands.assignments.list_submissions import list_all_submissions, list_ungraded, list_undistributed
        
        if args.ungraded:
            list_ungraded(ctx, assignment_id)
        elif args.undistributed:
            list_undistributed(ctx, assignment_id)
        else:
            list_all_submissions(ctx, assignment_id)


class ListGradersCommand(BaseCommand):
    """List all graders."""

    name = "list-graders"
    help = "List all graders"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def execute(self, ctx, args: argparse.Namespace) -> None:
        list_graders(ctx)


class ListDeadlinesCommand(BaseCommand):
    """List assignment deadlines."""

    name = "list-deadlines"
    help = "List assignment deadlines"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--course-id",
            type=int,
            help="Brightspace course ID (use when no course.json)",
        )

    def execute(self, ctx, args: argparse.Namespace) -> None:
        list_deadlines(ctx, getattr(args, "course_id", None))


class ListDivisionCommand(DualModeCommand):
    """List grading division for an assignment."""

    name = "list-division"
    help = "List grading division for an assignment"

    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute list division in direct mode."""
        print("❌ Grading division is not supported in direct mode")
        print("💡 Use assignment_id with course.json for grading division")
        print("💡 This feature requires grading distribution logs from course.json")

    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute list division in config mode."""
        from bscli.commands.assignments.list_division import list_division_config
        list_division_config(ctx, assignment_id)


class AssignmentsCommand(BaseGroupCommand):
    """Assignment management commands."""

    name = "assignments"
    help = "📝 Assignment management"

    def __init__(self):
        self.subcommands = {
            ListAssignmentsCommand.name: ListAssignmentsCommand,
            DistributeCommand.name: DistributeCommand,
            DownloadCommand.name: DownloadCommand,
            FindGraderCommand.name: FindGraderCommand,
            GradingProgressCommand.name: GradingProgressCommand,
            CheckGradingGroupsCommand.name: CheckGradingGroupsCommand,
            ListSubmissionsCommand.name: ListSubmissionsCommand,
            ListGradersCommand.name: ListGradersCommand,
            ListDeadlinesCommand.name: ListDeadlinesCommand,
            ListDivisionCommand.name: ListDivisionCommand,
        }

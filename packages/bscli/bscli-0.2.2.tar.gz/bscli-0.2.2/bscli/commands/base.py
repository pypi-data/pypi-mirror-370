"""Base command classes for consistent CLI structure."""

import argparse
from typing import Dict, Type, Any, Optional


class BaseCommand:
    """Base class for all CLI commands."""

    name: str = ""
    help: str = ""

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup argument parser for this command."""
        pass

    def execute(self, ctx, args: argparse.Namespace) -> None:
        """Execute the command."""
        raise NotImplementedError

    def validate_args(self, ctx, args: argparse.Namespace) -> bool:
        """Validate arguments. Return True if valid, False otherwise."""
        return True


class BaseGroupCommand(BaseCommand):
    """Base class for commands that group multiple subcommands."""

    def __init__(self):
        self.subcommands: Dict[str, Type[BaseCommand]] = {}

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup parser with subcommands."""
        subparsers = parser.add_subparsers(
            dest=f"{self.name}_action", help=f"{self.name.title()} actions"
        )

        for command_class in self.subcommands.values():
            cmd_parser = subparsers.add_parser(
                command_class.name, help=command_class.help
            )
            command_class().setup_parser(cmd_parser)

    def execute(self, ctx, args: argparse.Namespace) -> None:
        """Execute the appropriate subcommand."""
        action = getattr(args, f"{self.name}_action", None)

        if not action:
            self._show_help_message()
            return

        if action not in self.subcommands:
            self._show_unknown_action_error(action)
            return

        command_class = self.subcommands[action]
        command = command_class()

        if not command.validate_args(ctx, args):
            return

        command.execute(ctx, args)

    def _show_help_message(self):
        """Show help message when no action is provided."""
        print(f"❌ {self.name} command requires an action")
        print(f"Available actions: {', '.join(self.subcommands.keys())}")

    def _show_unknown_action_error(self, action: str):
        """Show error message for unknown actions."""
        print(f"❌ Unknown {self.name} action: {action}")
        print(f"Available actions: {', '.join(self.subcommands.keys())}")


def validate_assignment_id(ctx, assignment_id: str) -> bool:
    """Validate assignment ID exists in course config."""
    return ctx.is_valid_assignment_id(assignment_id)


def require_course_config(ctx):
    """Require course config with standardized error handling."""
    try:
        return ctx.course_config()
    except:
        print("❌ Course configuration not found")
        print("💡 Create a course.json file or use --course-config parameter")
        return None


def require_config_or_course_id(ctx, course_id=None):
    """Load course config or validate course_id parameter with standardized errors."""
    if course_id:
        try:
            api = ctx.api()
            enrollments = api.get_course_enrollments()
            course = next(
                (e.org_unit for e in enrollments if e.org_unit.id == course_id), None
            )
            if not course:
                print(f"❌ Course {course_id} not found in your enrollments")
                print("💡 Use 'bscli courses list' to see available courses")
                return None, None
            return None, course_id
        except Exception as e:
            print(f"❌ Failed to validate course ID: {e}")
            return None, None
    else:
        try:
            config = ctx.course_config()
            api_helper = ctx.api_helper()
            org_unit_id = api_helper.find_course_by_name(config.course_name).org_unit.id
            return config, org_unit_id
        except:
            print("❌ Course configuration not found")
            print("💡 Create a course.json file or use --course-id parameter")
            return None, None


class ErrorHandler:
    """Standardized error handling and messaging."""
    
    @staticmethod
    def dual_mode_error(command_name: str) -> str:
        """Standard error message for dual-mode commands."""
        return f"Either assignment_id (with course.json) or both --course-id and --assignment-id are required"
    
    @staticmethod
    def course_not_found_error(course_id: int) -> str:
        """Standard error message for course not found."""
        return f"❌ Course {course_id} not found in your enrollments"
    
    @staticmethod
    def assignment_not_found_error(assignment_id: int, course_id: int) -> str:
        """Standard error message for assignment not found."""
        return f"❌ Assignment {assignment_id} not found in course {course_id}"
    
    @staticmethod
    def config_not_found_error() -> str:
        """Standard error message for missing course config."""
        return "❌ Course configuration not found"
    
    @staticmethod
    def config_not_found_hint() -> str:
        """Standard hint for missing course config."""
        return "💡 Create a course.json file or use --course-id parameter"


def validate_dual_mode_args(args: argparse.Namespace) -> bool:
    """Validate dual-mode arguments (assignment_id OR course_id + assignment_id)."""
    has_course_and_assignment = args.course_id and args.brightspace_assignment_id
    has_assignment_id = getattr(args, 'assignment_id', None)
    
    return has_course_and_assignment or has_assignment_id


def get_dual_mode_error_message(command_name: str) -> str:
    """Get standardized error message for dual-mode validation failure."""
    return ErrorHandler.dual_mode_error(command_name)


def add_dual_mode_arguments(parser: argparse.ArgumentParser, assignment_required: bool = True) -> None:
    """Add standard dual-mode arguments to parser."""
    if assignment_required:
        parser.add_argument(
            "assignment_id", 
            nargs="?", 
            help="Assignment identifier (required unless using --course-id and --assignment-id)"
        )
    
    parser.add_argument("--course-id", type=int, help="Brightspace course ID")
    parser.add_argument(
        "--assignment-id",
        type=int,
        dest="brightspace_assignment_id",
        help="Brightspace assignment ID",
    )


class DualModeCommand(BaseCommand):
    """Base class for commands that support both config and direct mode."""
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Setup parser with dual-mode arguments."""
        add_dual_mode_arguments(parser, assignment_required=True)
        self.setup_command_parser(parser)
    
    def setup_command_parser(self, parser: argparse.ArgumentParser) -> None:
        """Override this method to add command-specific arguments."""
        pass
    
    def validate_args(self, ctx, args: argparse.Namespace) -> bool:
        """Validate dual-mode arguments."""
        if not validate_dual_mode_args(args):
            # Check if course.json exists to provide better error message
            try:
                ctx.course_config()
                # course.json exists, but assignment_id is missing
                parser = argparse.ArgumentParser()
                parser.error("assignment_id is required")
                return False
            except:
                # No course.json, show dual-mode error
                parser = argparse.ArgumentParser()
                parser.error(get_dual_mode_error_message(self.name))
                return False
        return True
    
    def execute(self, ctx, args: argparse.Namespace) -> None:
        """Execute command in appropriate mode."""
        if args.course_id and args.brightspace_assignment_id:
            # Direct mode
            self.execute_direct_mode(ctx, args.course_id, args.brightspace_assignment_id, args)
        elif args.assignment_id:
            # Config mode
            self.execute_config_mode(ctx, args.assignment_id, args)
        else:
            # This shouldn't happen due to validation, but handle gracefully
            print(f"❌ {self.name} command requires either:")
            print("   • assignment_id (with course.json)")
            print("   • --course-id and --assignment-id (without course.json)")
    
    def execute_direct_mode(self, ctx, course_id: int, assignment_id: int, args: argparse.Namespace) -> None:
        """Execute command in direct mode. Override this method."""
        raise NotImplementedError("Direct mode not implemented for this command")
    
    def execute_config_mode(self, ctx, assignment_id: str, args: argparse.Namespace) -> None:
        """Execute command in config mode. Override this method."""
        raise NotImplementedError("Config mode not implemented for this command")


def validate_course_and_assignment_direct(ctx, course_id: int, assignment_id: int) -> tuple[Optional[Any], Optional[Any]]:
    """Validate course and assignment IDs in direct mode."""
    try:
        api = ctx.api()
        
        # Validate course
        enrollments = api.get_course_enrollments()
        course_enrollment = next(
            (e for e in enrollments if e.org_unit.id == course_id), None
        )
        if not course_enrollment:
            print(ErrorHandler.course_not_found_error(course_id))
            return None, None
        
        # Validate assignment
        dropbox_folders = api.get_dropbox_folders(course_id)
        assignment = next((f for f in dropbox_folders if f.id == assignment_id), None)
        if not assignment:
            print(ErrorHandler.assignment_not_found_error(assignment_id, course_id))
            return None, None
        
        return course_enrollment, assignment
    
    except Exception as e:
        print(f"❌ Failed to validate course/assignment: {e}")
        return None, None

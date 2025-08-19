import argparse
from bscli.utils import (
    TablePrinter,
)
from bscli.commands.base import BaseCommand


class ListCoursesCommand(BaseCommand):
    """List all courses you have access to."""

    name = "list"
    help = "List all courses you have access to"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def execute(self, ctx, args: argparse.Namespace) -> None:
        list_courses(ctx)


def _get_course_data(ctx, config):
    """Get common course data from config."""
    api_helper = ctx.api_helper()
    org_unit_id = api_helper.find_course_by_name(config.course_name).org_unit.id
    return ctx.api(), api_helper, org_unit_id


def list_courses(ctx):
    """List all courses the user has access to."""
    print("📚 Fetching your courses...")
    api = ctx.api()
    table = TablePrinter()
    table.add_column("brightspace id")
    table.add_column("code")
    table.add_column("name")
    table.add_column("role")

    try:
        enrollments = api.get_course_enrollments()
        if not enrollments:
            print("❌ No courses found")
            print("💡 Make sure you have instructor access to at least one course")
            return

        for enrollment in enrollments:
            org_unit = enrollment.org_unit
            role = enrollment.access.classlist_role_name or "Unknown"
            table.add_row([str(org_unit.id), org_unit.code or "", org_unit.name, role])

        print(f"✅ Found {len(enrollments)} courses:")
        table.print()
        print()
        print("💡 Copy the Brightspace ID to use with --course-id parameter")

    except Exception as e:
        print(f"❌ Failed to retrieve courses: {e}")
        print("💡 Check your network connection and API configuration")

import argparse
import datetime
import bsapi.types

from bscli.commands.courses.list import _get_course_data
from bscli.utils import (
    TablePrinter,
    format_datetime,
    format_timedelta,
    to_local_time,
)
from bscli.commands.base import BaseCommand, require_config_or_course_id


class ListAssignmentsCommand(BaseCommand):
    """List assignments with submission status."""

    name = "list"
    help = "List assignments with submission status"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--course-id",
            type=int,
            help="Brightspace course ID (use when no course.json)",
        )

    def execute(self, ctx, args: argparse.Namespace) -> None:
        list_assignments(ctx, getattr(args, "course_id", None))


def _require_config_or_course_id(ctx, course_id=None):
    """Load course config or validate course_id parameter."""
    if course_id:
        # Validate course ID exists
        try:
            api = ctx.api()
            enrollments = api.get_course_enrollments()
            course = next(
                (e.org_unit for e in enrollments if e.org_unit.id == course_id), None
            )
            if not course:
                print(f"❌ Course {course_id} not found in your enrollments")
                print("💡 Use 'bscli list courses' to see available courses")
                return None, None
            return None, course_id  # No config, but valid course_id
        except Exception as e:
            print(f"❌ Failed to validate course ID: {e}")
            return None, None
    else:
        # Require course config
        try:
            config = ctx.course_config()
            api_helper = ctx.api_helper()
            org_unit_id = api_helper.find_course_by_name(config.course_name).org_unit.id
            return config, org_unit_id
        except:
            print("❌ No course configuration found")
            print("💡 Create course.json or use --course-id parameter")
            return None, None


def _require_config(ctx):
    """Load course config with error handling."""
    try:
        return ctx.course_config()
    except:
        print("❌ No course configuration found")
        print("💡 Create a course.json file to use this command")
        return None


def list_graders(ctx):
    """List all graders."""
    config = _require_config(ctx)
    if not config:
        return

    table = TablePrinter()
    table.add_column("identifier")
    table.add_column("name")
    table.add_column("email")
    table.add_column("contact email")

    if not config.graders:
        print("❌ No graders configured")
        print("💡 Add graders to your course.json file")
        return

    for grader_id, grader in config.graders.items():
        table.add_row([grader_id, grader.name, grader.email, grader.contact_email])

    print(f"✅ Found {len(config.graders)} graders:")
    table.print()


def list_assignments(ctx, course_id=None):
    """List all assignments."""
    print("📝 Fetching assignments...")

    config, org_unit_id = _require_config_or_course_id(ctx, course_id)
    if org_unit_id is None:
        return

    api = ctx.api()
    use_config = config is not None

    if use_config:
        name_to_identifier = {
            assignment.name: identifier
            for identifier, assignment in config.assignments.items()
        }
        print(f"📚 Course: {config.course_name}")
    else:
        name_to_identifier = {}
        # Get course name for display
        enrollments = api.get_course_enrollments()
        course = next(
            (e.org_unit for e in enrollments if e.org_unit.id == org_unit_id), None
        )
        print(f"📚 Course: {course.name if course else f'ID {org_unit_id}'}")

    table = TablePrinter()
    if use_config:
        table.add_column("identifier")
    table.add_column("brightspace id")
    table.add_column("name")
    table.add_column("group")
    table.add_column("grade")
    table.add_column("due")
    table.add_column("submitted")
    table.add_column("graded")

    try:
        dropbox_folders = api.get_dropbox_folders(org_unit_id)
        if not dropbox_folders:
            print("❌ No assignments found")
            print("💡 Make sure the course has dropbox assignments")
            return

        group_categories = {
            c.group_category_id: c for c in api.get_group_categories(org_unit_id)
        }

        for dropbox in dropbox_folders:
            due_date = (
                format_datetime(to_local_time(dropbox.due_date))
                if dropbox.due_date
                else "<None>"
            )

            group_category_name = (
                group_categories[dropbox.group_type_id].name
                if dropbox.group_type_id is not None
                else "<Individual>"
            )

            grade_name = "<None>"
            if dropbox.grade_item_id:
                try:
                    grade_object = api.get_grade_object(
                        org_unit_id, dropbox.grade_item_id
                    )
                    grade_name = grade_object.name
                except:
                    grade_name = "<error>"

            submitted = f"{dropbox.total_users_with_submissions}/{dropbox.total_users}"
            graded = (
                f"{dropbox.total_users_with_feedback}/{dropbox.total_users_with_submissions}"
                if dropbox.total_users_with_submissions > 0
                else "0/0"
            )

            row_data = [
                str(dropbox.id),
                dropbox.name,
                group_category_name,
                grade_name,
                due_date,
                submitted,
                graded,
            ]

            if use_config:
                identifier = name_to_identifier.get(dropbox.name, "<Not configured>")
                row_data.insert(0, identifier)

            table.add_row(row_data)

        print(f"✅ Found {len(dropbox_folders)} assignments:")
        table.print()

        if not use_config:
            print()
            print(
                "💡 To download submissions: bscli download --course-id <course> --assignment-id <id>"
            )
        else:
            print()
            print("💡 To download submissions: bscli download <identifier>")

    except Exception as e:
        print(f"❌ Failed to retrieve assignments: {e}")
        print("💡 Check your network connection and course permissions")


def list_deadlines(ctx, course_id=None):
    """List all deadlines."""
    print("⏰ Checking assignment deadlines...")

    config, org_unit_id = _require_config_or_course_id(ctx, course_id)
    if org_unit_id is None:
        return

    api = ctx.api()
    use_config = config is not None

    table = TablePrinter()
    if use_config:
        table.add_column("identifier")
    table.add_column("name")
    table.add_column("deadline")
    if use_config:
        table.add_column("distributed")

    try:
        dropbox_folders = api.get_dropbox_folders(org_unit_id)
        if not dropbox_folders:
            print("❌ No assignments found")
            return

        utc_now = datetime.datetime.now(datetime.timezone.utc)

        if use_config:
            # Config mode: show assignment identifiers and distribution status
            dropbox_by_name = {f.name: f for f in dropbox_folders}

            for identifier, assignment in config.assignments.items():
                if assignment.name not in dropbox_by_name:
                    print(f"⚠️  Assignment '{assignment.name}' not found in Brightspace")
                    continue

                dropbox = dropbox_by_name[assignment.name]

                if dropbox.due_date is None:
                    deadline = "<None>"
                elif dropbox.due_date < utc_now:
                    deadline = format_timedelta(utc_now - dropbox.due_date) + " ago"
                else:
                    deadline = "in " + format_timedelta(dropbox.due_date - utc_now)

                distributed = ctx.has_distributed(identifier)
                table.add_row(
                    [
                        identifier,
                        assignment.name,
                        deadline,
                        "yes" if distributed else "no",
                    ]
                )
        else:
            # Direct mode: show all assignments with deadlines
            for dropbox in dropbox_folders:
                if dropbox.due_date is None:
                    deadline = "<None>"
                elif dropbox.due_date < utc_now:
                    deadline = format_timedelta(utc_now - dropbox.due_date) + " ago"
                else:
                    deadline = "in " + format_timedelta(dropbox.due_date - utc_now)

                table.add_row([dropbox.name, deadline])

        if use_config:
            print(f"✅ Found {len(config.assignments)} configured assignments:")
        else:
            assignments_with_deadlines = sum(
                1 for f in dropbox_folders if f.due_date is not None
            )
            print(
                f"✅ Found {assignments_with_deadlines}/{len(dropbox_folders)} assignments with deadlines:"
            )

        table.print()

        if not use_config:
            print()
            print(
                "💡 Create course.json to see distribution status and use assignment identifiers"
            )

    except Exception as e:
        print(f"❌ Failed to retrieve deadlines: {e}")


def list_ungraded(ctx, assignment_id: str):
    """List ungraded submissions for an assignment."""
    config = _require_config(ctx)
    if not config:
        return

    if not ctx.is_valid_assignment_id(assignment_id):
        return

    print(f"📊 Checking ungraded submissions for {assignment_id}...")
    api, api_helper, org_unit_id = _get_course_data(ctx, config)
    assignment_config = config.assignments[assignment_id]

    try:
        assignment = api_helper.find_assignment(org_unit_id, assignment_config.name)
        submissions = api.get_dropbox_folder_submissions(org_unit_id, assignment.id)
        division_log = ctx.load_division_log(assignment_id)

        table = TablePrinter()
        table.add_column("name")
        table.add_column("grader")

        ungraded_count = 0
        for submission in submissions:
            if submission.status != bsapi.types.ENTITY_DROPBOX_STATUS_SUBMITTED:
                continue

            graded_by = division_log.get_grader(submission.entity.entity_id)
            table.add_row([submission.entity.get_name(), graded_by or "<None>"])
            ungraded_count += 1

        if ungraded_count == 0:
            print("✅ All submissions have been graded!")
        else:
            print(f"📊 Found {ungraded_count} ungraded submissions:")
            table.sort_rows(columns=[1])
            table.print()

    except Exception as e:
        print(f"❌ Failed to check ungraded submissions: {e}")


def list_undistributed(ctx):
    """List all undistributed submissions."""
    config = _require_config(ctx)
    if not config:
        return

    print("📋 Checking undistributed submissions...")
    api, api_helper, org_unit_id = _get_course_data(ctx, config)

    try:
        assignments = {f.name: f for f in api.get_dropbox_folders(org_unit_id)}

        table = TablePrinter()
        table.add_column("name")
        table.add_column("assignment")

        undistributed_count = 0
        for assignment_id, assignment_config in config.assignments.items():
            if not ctx.has_distributed(assignment_id):
                continue

            if assignment_config.name not in assignments:
                continue

            assignment = assignments[assignment_config.name]
            submissions = api.get_dropbox_folder_submissions(org_unit_id, assignment.id)
            division_log = ctx.load_division_log(assignment_id)

            for submission in submissions:
                if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
                    continue

                if not division_log.has_entity_id(submission.entity.entity_id):
                    table.add_row([submission.entity.get_name(), assignment.name])
                    undistributed_count += 1

        if undistributed_count == 0:
            print("✅ All submissions have been distributed!")
        else:
            print(f"📋 Found {undistributed_count} undistributed submissions:")
            table.sort_rows(columns=[1])
            table.print()
            print()
            print("💡 Run 'bscli distribute <assignment>' to assign these to graders")

    except Exception as e:
        print(f"❌ Failed to check undistributed submissions: {e}")


def list_division(ctx, assignment_id: str):
    """List the grading division for an assignment."""
    config = _require_config(ctx)
    if not config:
        return

    if not ctx.is_valid_assignment_id(assignment_id):
        return

    print(f"👥 Checking grading division for {assignment_id}...")

    table = TablePrinter()
    table.add_column("entity id")
    table.add_column("name")
    table.add_column("students")
    table.add_column("grader")

    division_log = ctx.load_division_log(assignment_id)

    if not division_log:
        print("❌ No grading division found")
        print(
            f"💡 Run 'bscli distribute {assignment_id}' to create grading assignments"
        )
        return

    total_entries = 0
    for grader_id, entries in division_log:
        grader_name = config.graders[grader_id].name
        for entry in entries:
            students_str = ",".join(f"{s.name} ({s.username})" for s in entry.students)
            table.add_row(
                [entry.entity_id, entry.folder_name, students_str, grader_name]
            )
            total_entries += 1

    print(f"✅ Found {total_entries} grading assignments:")
    table.sort_rows(columns=[3])
    table.print()

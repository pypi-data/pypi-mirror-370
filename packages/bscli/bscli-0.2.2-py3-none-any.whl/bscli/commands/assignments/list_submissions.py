import argparse
import bsapi.types
from bscli.commands.courses.list import _get_course_data
from bscli.utils import TablePrinter
from bscli.commands.base import require_course_config, validate_assignment_id



def list_all_submissions(ctx, assignment_id: str):
    """List all submissions for an assignment."""
    config = require_course_config(ctx)
    if not config:
        return

    print(f"📋 Listing all submissions for {assignment_id}...")
    api, api_helper, org_unit_id = _get_course_data(ctx, config)
    assignment_config = config.assignments[assignment_id]

    try:
        assignment = api_helper.find_assignment(org_unit_id, assignment_config.name)
        submissions = api.get_dropbox_folder_submissions(org_unit_id, assignment.id)
        division_log = ctx.load_division_log(assignment_id)

        table = TablePrinter()
        table.add_column("name")
        table.add_column("status")
        table.add_column("grader")

        total_count = 0
        for submission in submissions:
            # Skip unsubmitted entries
            if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
                continue

            status_map = {
                bsapi.types.ENTITY_DROPBOX_STATUS_SUBMITTED: "Submitted",
                bsapi.types.ENTITY_DROPBOX_STATUS_DRAFT: "Draft",
                bsapi.types.ENTITY_DROPBOX_STATUS_PUBLISHED: "Published",
            }
            status = status_map.get(submission.status, "Unknown")

            graded_by = division_log.get_grader(submission.entity.entity_id)
            grader_name = (
                config.graders[graded_by].name
                if graded_by and graded_by in config.graders
                else graded_by or "<None>"
            )

            table.add_row([submission.entity.get_name(), status, grader_name])
            total_count += 1

        if total_count == 0:
            print("❌ No submissions found for this assignment")
        else:
            print(f"📋 Found {total_count} submissions:")
            table.sort_rows(columns=[0])  # Sort by name
            table.print()

    except Exception as e:
        print(f"❌ Failed to list submissions: {e}")


def list_ungraded(ctx, assignment_id: str):
    """List ungraded submissions for an assignment."""
    config = require_course_config(ctx)
    if not config:
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


def list_undistributed(ctx, assignment_id: str):
    """List undistributed submissions for an assignment."""
    config = require_course_config(ctx)
    if not config:
        return

    print(f"📋 Checking undistributed submissions for {assignment_id}...")
    api, api_helper, org_unit_id = _get_course_data(ctx, config)
    assignment_config = config.assignments[assignment_id]

    try:
        if not ctx.has_distributed(assignment_id):
            print(f"❌ Assignment {assignment_id} has not been distributed yet")
            return

        assignment = api_helper.find_assignment(org_unit_id, assignment_config.name)
        submissions = api.get_dropbox_folder_submissions(org_unit_id, assignment.id)
        division_log = ctx.load_division_log(assignment_id)

        table = TablePrinter()
        table.add_column("name")

        undistributed_count = 0
        for submission in submissions:
            if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
                continue

            if not division_log.has_entity_id(submission.entity.entity_id):
                table.add_row([submission.entity.get_name()])
                undistributed_count += 1

        if undistributed_count == 0:
            print("✅ All submissions have been distributed!")
        else:
            print(f"📋 Found {undistributed_count} undistributed submissions:")
            table.sort_rows(columns=[0])  # Sort by name
            table.print()
            print()
            print(
                f"💡 Run 'bscli assignments distribute {assignment_id}' to assign these to graders"
            )

    except Exception as e:
        print(f"❌ Failed to check undistributed submissions: {e}")


def list_all_submissions_direct(ctx, course_id: int, assignment_id: int):
    """List all submissions for an assignment using direct Brightspace IDs."""
    print(f"📋 Listing all submissions for assignment {assignment_id} in course {course_id}...")
    api = ctx.api()

    try:
        # Validate course and assignment
        enrollments = api.get_course_enrollments()
        course_enrollment = next(
            (e for e in enrollments if e.org_unit.id == course_id), None
        )
        if not course_enrollment:
            print(f"❌ Course {course_id} not found in your enrollments")
            return

        dropbox_folders = api.get_dropbox_folders(course_id)
        assignment = next((f for f in dropbox_folders if f.id == assignment_id), None)
        if not assignment:
            print(f"❌ Assignment {assignment_id} not found in course {course_id}")
            return

        # Get submissions
        submissions = api.get_dropbox_folder_submissions(course_id, assignment_id)

        table = TablePrinter()
        table.add_column("name")
        table.add_column("status")

        total_count = 0
        for submission in submissions:
            # Skip unsubmitted entries
            if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
                continue

            status_map = {
                bsapi.types.ENTITY_DROPBOX_STATUS_SUBMITTED: "Submitted",
                bsapi.types.ENTITY_DROPBOX_STATUS_DRAFT: "Draft",
                bsapi.types.ENTITY_DROPBOX_STATUS_PUBLISHED: "Published",
            }
            status = status_map.get(submission.status, "Unknown")

            table.add_row([submission.entity.get_name(), status])
            total_count += 1

        if total_count == 0:
            print("❌ No submissions found for this assignment")
        else:
            print(f"📋 Found {total_count} submissions:")
            table.sort_rows(columns=[0])  # Sort by name
            table.print()

    except Exception as e:
        print(f"❌ Failed to list submissions: {e}")


def list_ungraded_direct(ctx, course_id: int, assignment_id: int):
    """List ungraded submissions for an assignment using direct Brightspace IDs."""
    print(f"📊 Checking ungraded submissions for assignment {assignment_id} in course {course_id}...")
    api = ctx.api()

    try:
        # Validate course and assignment
        enrollments = api.get_course_enrollments()
        course_enrollment = next(
            (e for e in enrollments if e.org_unit.id == course_id), None
        )
        if not course_enrollment:
            print(f"❌ Course {course_id} not found in your enrollments")
            return

        dropbox_folders = api.get_dropbox_folders(course_id)
        assignment = next((f for f in dropbox_folders if f.id == assignment_id), None)
        if not assignment:
            print(f"❌ Assignment {assignment_id} not found in course {course_id}")
            return

        # Get submissions
        submissions = api.get_dropbox_folder_submissions(course_id, assignment_id)

        table = TablePrinter()
        table.add_column("name")

        ungraded_count = 0
        for submission in submissions:
            if submission.status != bsapi.types.ENTITY_DROPBOX_STATUS_SUBMITTED:
                continue

            table.add_row([submission.entity.get_name()])
            ungraded_count += 1

        if ungraded_count == 0:
            print("✅ All submissions have been graded!")
        else:
            print(f"📊 Found {ungraded_count} ungraded submissions:")
            table.sort_rows(columns=[0])  # Sort by name
            table.print()

    except Exception as e:
        print(f"❌ Failed to check ungraded submissions: {e}")

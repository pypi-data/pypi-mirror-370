from dataclasses import dataclass
import bsapi.types
from bscli.utils import TablePrinter


@dataclass
class Progress:
    draft: int
    published: int
    assigned: int




def check_grading_progress_config(ctx, assignment_id: str):
    """Check the grading progress of an assignment using course.json."""
    if not ctx.is_valid_assignment_id(assignment_id):
        print(f"❌ Unknown assignment: {assignment_id}")
        return

    config = ctx.course_config()
    api = ctx.api()
    api_helper = ctx.api_helper()

    assignment_config = config.assignments[assignment_id]
    org_unit_id = api_helper.find_course_by_name(config.course_name).org_unit.id
    assignment = api_helper.find_assignment(org_unit_id, assignment_config.name)
    submissions = api.get_dropbox_folder_submissions(org_unit_id, assignment.id)
    division_log = ctx.load_division_log(assignment_id)

    table = TablePrinter()
    table.add_column("grader")
    table.add_column("draft")
    table.add_column("published")
    table.add_column("assigned")
    table.add_column("completed")

    progress = {grader: Progress(0, 0, 0) for grader in config.graders}

    for submission in submissions:
        if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
            continue
        if not division_log.has_entity_id(submission.entity.entity_id):
            continue

        graded_by = division_log.get_grader(submission.entity.entity_id)
        progress[graded_by].assigned += 1

        if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_PUBLISHED:
            progress[graded_by].published += 1
        elif submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_DRAFT:
            progress[graded_by].draft += 1

    for grader_id, prog in progress.items():
        if prog.assigned == 0:
            continue

        if prog.published == prog.assigned:
            completed = "yes"
        elif prog.draft + prog.published == prog.assigned:
            completed = "draft"
        else:
            completed = "no"

        table.add_row(
            [
                config.graders[grader_id].name,
                prog.draft,
                prog.published,
                prog.assigned,
                completed,
            ]
        )

    table.sort_rows()
    table.print()


def check_grading_progress_direct(ctx, course_id: int, assignment_id: int):
    """Check the grading progress of an assignment using direct Brightspace IDs."""
    print(f"📊 Checking grading progress for assignment {assignment_id} in course {course_id}...")
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

        # Count submissions by status
        total_submissions = 0
        draft_count = 0
        published_count = 0
        submitted_count = 0

        for submission in submissions:
            if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_UNSUBMITTED:
                continue
            
            total_submissions += 1
            if submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_PUBLISHED:
                published_count += 1
            elif submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_DRAFT:
                draft_count += 1
            elif submission.status == bsapi.types.ENTITY_DROPBOX_STATUS_SUBMITTED:
                submitted_count += 1

        # Display results
        print(f"📚 Course: {course_enrollment.org_unit.name}")
        print(f"📝 Assignment: {assignment.name}")
        print()
        print(f"📊 Grading Progress:")
        print(f"   Total submissions: {total_submissions}")
        print(f"   Published (graded): {published_count}")
        print(f"   Draft (being graded): {draft_count}")
        print(f"   Submitted (not graded): {submitted_count}")
        
        if total_submissions > 0:
            completion_percent = (published_count / total_submissions) * 100
            print(f"   Completion: {completion_percent:.1f}%")
        
        if published_count == total_submissions and total_submissions > 0:
            print("✅ All submissions have been graded!")
        elif submitted_count == 0 and total_submissions > 0:
            print("✅ All submissions are being processed!")
        
        print()
        print("💡 Note: Individual grader progress requires course.json configuration")

    except Exception as e:
        print(f"❌ Failed to check grading progress: {e}")

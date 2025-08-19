from bscli.utils import TablePrinter


def _require_config(ctx):
    """Load course config with error handling."""
    try:
        return ctx.course_config()
    except:
        print("❌ No course configuration found")
        print("💡 Create a course.json file to use this command")
        return None




def list_division_config(ctx, assignment_id: str):
    """List the grading division for an assignment using course.json."""
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
            f"💡 Run 'bscli assignments distribute {assignment_id}' to create grading assignments"
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

from bscli.utils import TablePrinter, is_match


def find_grader(ctx, search: str):
    """Find the grader for a search term."""
    config = ctx.course_config()

    table = TablePrinter()
    table.add_column("entity id")
    table.add_column("name")
    table.add_column("students")
    table.add_column("grader")
    table.add_column("assignment")

    for assignment_id, assignment in config.assignments.items():
        if not ctx.has_distributed(assignment_id):
            continue

        division_log = ctx.load_division_log(assignment_id)
        for grader_id, entries in division_log:
            grader_name = config.graders[grader_id].name
            for entry in entries:
                students_str = ",".join(
                    f"{s.name} ({s.username})" for s in entry.students
                )

                if is_match(search, entry.folder_name) or is_match(
                    search, students_str
                ):
                    table.add_row(
                        [
                            entry.entity_id,
                            entry.folder_name,
                            students_str,
                            grader_name,
                            assignment.name,
                        ]
                    )

    table.sort_rows(columns=[4])
    table.print()

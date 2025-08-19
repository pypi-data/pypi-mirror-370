from bscli.utils import TablePrinter


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

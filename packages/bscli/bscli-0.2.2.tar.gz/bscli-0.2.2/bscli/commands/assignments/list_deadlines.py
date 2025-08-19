import datetime
from bscli.utils import TablePrinter, format_timedelta


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
                print("💡 Use 'bscli courses list' to see available courses")
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

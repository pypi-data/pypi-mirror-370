

def check_grading_groups_config(ctx, assignment_id: str):
    """Check the grading groups of an assignment using course.json."""
    if not ctx.is_valid_assignment_id(assignment_id):
        print(f"❌ Unknown assignment: {assignment_id}")
        return

    config = ctx.course_config()
    api = ctx.api()
    api_helper = ctx.api_helper()

    assignment_config = config.assignments[assignment_id]

    if assignment_config.division.method != "brightspace":
        print(f"ℹ️  Assignment {assignment_id} does not use Brightspace grading groups")
        return

    print(f"🔍 Checking grading groups for {assignment_id}...")
    issues_found = False

    # Grab all required Brightspace metadata
    org_unit_id = api_helper.find_course_by_name(config.course_name).org_unit.id
    grading_group_category = api_helper.find_group_category(
        org_unit_id, assignment_config.division.group_category_name
    )
    assignment = api_helper.find_assignment(org_unit_id, assignment_config.name)
    users = {
        int(user.user.identifier): user.user for user in api.get_users(org_unit_id)
    }
    groups = (
        {
            group.group_id: group
            for group in api.get_groups(org_unit_id, assignment.group_type_id)
        }
        if assignment.group_type_id is not None
        else None
    )
    grading_groups = {
        group.group_id: group
        for group in api.get_groups(
            org_unit_id, grading_group_category.group_category_id
        )
    }

    # Build map of user to grading groups
    user_to_grading_groups: dict[int, list[int]] = {user_id: [] for user_id in users}
    for grading_group in grading_groups.values():
        for user_id in grading_group.enrollments:
            user_to_grading_groups[user_id].append(grading_group.group_id)

    # Build map of user to assignment group
    user_to_group: dict[int, int] = dict()
    if groups is not None:
        for group in groups.values():
            for user_id in group.enrollments:
                user_to_group[user_id] = group.group_id

    # Check users not in exactly one grading group
    for user_id, in_grading_groups in user_to_grading_groups.items():
        if len(in_grading_groups) == 1:
            continue

        user = users[user_id]
        issues_found = True

        if len(in_grading_groups) == 0:
            print(
                f"{user.display_name} ({user.user_name.lower()}) is not in any grading group"
            )
        elif len(in_grading_groups) > 1:
            groups_str = ", ".join(
                grading_groups[group_id].name for group_id in in_grading_groups
            )
            print(
                f"{user.display_name} ({user.user_name.lower()}) is in multiple grading groups: {groups_str}"
            )

        # Show assignment group info
        if user_id not in user_to_group:
            continue

        group = groups[user_to_group[user_id]]
        print(f"- In assignment group {group.name}")

        # Show group partners info
        for partner_id in group.enrollments:
            if partner_id == user_id:
                continue

            partner = users[partner_id]
            partner_grading_groups = user_to_grading_groups[partner_id]
            print(
                f"- Group partner {partner.display_name} ({partner.user_name.lower()}) ",
                end="",
            )
            if partner_grading_groups:
                groups_str = ", ".join(
                    grading_groups[group_id].name for group_id in partner_grading_groups
                )
                print(f"is in grading group(s): {groups_str}")
            else:
                print("is not in any grading group")

    # Check for split groups
    if groups:
        for group in groups.values():
            if len(group.enrollments) <= 1:
                continue
            if all(
                user_to_grading_groups[group.enrollments[0]]
                == user_to_grading_groups[user_id]
                for user_id in group.enrollments
            ):
                continue

            issues_found = True
            print(f"Group {group.name} is split over multiple grading groups")
            for user_id in group.enrollments:
                user = users[user_id]
                print(
                    f"- Group member {user.display_name} ({user.user_name.lower()}) ",
                    end="",
                )

                in_grading_groups = user_to_grading_groups[user_id]
                if in_grading_groups:
                    groups_str = ", ".join(
                        grading_groups[group_id].name for group_id in in_grading_groups
                    )
                    print(f"is in grading group(s): {groups_str}")
                else:
                    print("is not in any grading group")

    # Show success message if no issues found
    if not issues_found:
        print("✅ All grading groups are configured correctly!")

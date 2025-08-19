"""Course configuration creation functionality."""

import json
from pathlib import Path

from bscli.filesender import generate_encryption_password, is_valid_password


def _get_valid_input(prompt, validator=None, default=None):
    """Get valid user input with optional validation."""
    while True:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        if not value:
            continue
        if validator is None or validator(value):
            return value
        # If we get here, validation failed - loop continues


def _get_course_selection(api):
    """Get course selection from user."""
    enrollments = api.get_course_enrollments()
    if not enrollments:
        print("❌ No courses found")
        return None

    print("Available courses:")
    for i, enrollment in enumerate(enrollments, 1):
        role = enrollment.access.classlist_role_name or "Unknown"
        print(f"  {i}. {enrollment.org_unit.name} ({role})")

    while True:
        choice = input(f"\nSelect course (1-{len(enrollments)}): ").strip()
        if not choice:
            print("❌ Selection cancelled")
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(enrollments):
                return enrollments[idx]
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Please enter a number")


def _get_assignment_defaults():
    """Get assignment default settings."""
    defaults = {}

    # Draft feedback
    draft = input("\nUpload feedback as draft by default? [y/N]: ").lower().strip()
    defaults["draftFeedback"] = draft in ["y", "yes"]

    # Default code language
    code_lang = input("Default code block language [clike]: ").strip()
    defaults["defaultCodeBlockLanguage"] = code_lang or "clike"

    # File hierarchy
    print("\nFile hierarchy processing:")
    print("  smart    - Flatten if only one file, keep structure if multiple")
    print("  flatten  - Put all files in submission root")
    print("  original - Keep original folder structure")

    hierarchy_validator = lambda x: x in ["smart", "flatten", "original"]
    defaults["fileHierarchy"] = _get_valid_input(
        "File hierarchy [smart]: ", hierarchy_validator, "smart"
    )

    # Division method
    print("\nGrading division method:")
    print("  random      - Randomly assign submissions to graders every time")
    print("  persistent  - Use persistent groups across assignments, stored locally")
    print("  brightspace - Use Brightspace grading groups")

    division_validator = lambda x: x in ["random", "persistent", "brightspace"]
    division_method = _get_valid_input(
        "Division method [random]: ", division_validator, "random"
    )

    division = {"method": division_method}
    if division_method in ["persistent", "brightspace"]:
        group_category = input("Group category name: ").strip()
        if group_category:
            division["groupCategoryName"] = group_category

    defaults["division"] = division
    defaults["ignoredSubmissions"] = []
    defaults["gradeAliases"] = {}
    defaults["removeFiles"] = ["*.exe", ".DS_Store"]
    defaults["removeFolders"] = [".git", "__pycache__", "__MACOSX"]

    return defaults


def _get_encryption_password():
    """Get encryption password from user (optional)."""
    print("FileSender encryption password (optional):")
    print("  Requirements: min 8 chars, uppercase, lowercase, digit, special char")
    print("  Leave empty to send files without encryption")

    generate_pwd = input("Generate password automatically? [y/N]: ").lower().strip()
    if generate_pwd in ["y", "yes"]:
        password = generate_encryption_password()
        print(f"Generated password: {password}")
        return password

    while True:
        password = input("Enter password (or press Enter to skip): ").strip()
        if not password:
            print("No encryption password set - files will be sent unencrypted")
            return None
        if is_valid_password(password):
            return password
        print(
            "❌ Password must be at least 8 chars with uppercase, lowercase, digit, and special character"
        )


def _process_assignments(api, org_unit_id):
    """Process assignment configuration."""
    print("Fetching assignments from Brightspace...")
    dropbox_folders = api.get_dropbox_folders(org_unit_id)

    if not dropbox_folders:
        print("No assignments found in course")
        return {}

    print(f"Found {len(dropbox_folders)} assignments:")
    for i, folder in enumerate(dropbox_folders, 1):
        print(f"  {i}. {folder.name}")

    # Get selection strategy
    include_all = input(f"\nInclude all assignments? [Y/n]: ").lower().strip()

    if include_all in ["n", "no"]:
        selection = input(
            "Select assignments (comma-separated numbers or 'all'): "
        ).strip()
        if selection.lower() == "all":
            selected_folders = list(enumerate(dropbox_folders, 1))
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                selected_folders = [
                    (i, dropbox_folders[i - 1])
                    for i in indices
                    if 1 <= i <= len(dropbox_folders)
                ]
            except (ValueError, IndexError):
                print("❌ Invalid selection, including all assignments")
                selected_folders = list(enumerate(dropbox_folders, 1))
    else:
        selected_folders = list(enumerate(dropbox_folders, 1))

    # Process each selected assignment
    assignments = {}
    used_identifiers = set()

    for i, folder in selected_folders:
        print(f"\n--- Assignment {i}/{len(dropbox_folders)} ---")
        print(f"Brightspace name: {folder.name}")

        # Get identifier
        suggested_id = f"A{i:02d}"
        while True:
            identifier = input(f"Short identifier [{suggested_id}]: ").strip()
            if not identifier:
                identifier = suggested_id
            if identifier not in used_identifiers:
                used_identifiers.add(identifier)
                break
            print(f"❌ Identifier '{identifier}' already used")

        # Get encryption password
        password = _get_encryption_password()

        # Build assignment data
        assignment_data = {"name": folder.name}
        if password:
            assignment_data["encryptionPassword"] = password

        assignments[identifier] = assignment_data
        print(f"✅ Added assignment: {identifier} -> {folder.name}")

    return assignments


def _process_graders(api, org_unit_id):
    """Process grader configuration."""
    graders = {}

    try:
        print("Fetching users with grading roles from Brightspace...")
        users = api.get_users(org_unit_id)

        # Find potential graders
        grader_users = [
            user_enrollment
            for user_enrollment in users
            if any(
                keyword in user_enrollment.role.name.lower()
                for keyword in ["grader", "instructor", "ta"]
            )
        ]

        if grader_users:
            print(f"Found {len(grader_users)} potential graders:")
            for i, user_enrollment in enumerate(grader_users, 1):
                user = user_enrollment.user
                role = user_enrollment.role.name
                print(f"  {i}. {user.display_name} ({user.email_address}) - {role}")

            include_all = input(f"\nInclude all as graders? [Y/n]: ").lower().strip()

            if include_all in ["n", "no"]:
                selection = input(
                    "Select graders (comma-separated numbers or 'all'): "
                ).strip()
                if selection.lower() == "all":
                    selected_users = grader_users
                else:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(",")]
                        selected_users = [
                            grader_users[i]
                            for i in indices
                            if 0 <= i < len(grader_users)
                        ]
                    except (ValueError, IndexError):
                        print("❌ Invalid selection, including all graders")
                        selected_users = grader_users
            else:
                selected_users = grader_users

            # Process selected graders
            used_identifiers = set()
            for user_enrollment in selected_users:
                user = user_enrollment.user
                base_identifier = (
                    user.user_name.lower()
                    if user.user_name
                    else user.display_name.lower().replace(" ", "_")
                )
                identifier = "".join(
                    c for c in base_identifier if c.isalnum() or c == "_"
                )

                # Ensure unique identifier
                counter = 1
                while identifier in used_identifiers:
                    identifier = f"{base_identifier}_{counter}"
                    counter += 1
                used_identifiers.add(identifier)

                graders[identifier] = {
                    "name": user.display_name,
                    "email": user.email_address or f"{user.user_name}@unknown.edu",
                }

    except Exception as e:
        if "403" in str(e) or "Not Authorized" in str(e):
            print("⚠️  Permission denied - cannot fetch course users automatically")
            print("Your role doesn't have permission to view all course users.")
        else:
            print(f"❌ Failed to fetch graders: {e}")

    # Manual grader addition
    if not graders:
        print("\nAdding graders manually:")
        add_manual = True
    else:
        add_manual = input(
            "\nAdd additional manual graders? [y/N]: "
        ).lower().strip() in ["y", "yes"]

    if add_manual:
        print("\nEnter grader information (press Enter on identifier to finish):")
        while True:
            print("\n--- New Grader ---")
            grader_id = input("Grader identifier (e.g., 'john_doe'): ").strip()
            if not grader_id:
                break

            if grader_id in graders:
                print(f"❌ Identifier '{grader_id}' already exists")
                continue

            name = input("Full name: ").strip()
            email = input("Email: ").strip()

            if name and email:
                graders[grader_id] = {"name": name, "email": email}
                print(f"✅ Added grader: {name}")
            else:
                print("❌ Name and email are required")

    return graders


def _save_config(config, course_identifier):
    """Save configuration to file."""
    print("\n" + "=" * 50)
    print("SAVE CONFIGURATION")
    print("=" * 50)

    default_path = Path(f"./{course_identifier}/course.json")
    print(f"\nDefault save location: {default_path}")

    custom_path = input("Custom path (press Enter for default): ").strip()
    save_path = Path(custom_path) if custom_path else default_path

    # Create directory and save
    save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(save_path, "w") as f:
            json.dump(config, f, indent=4)

        print(f"\n✅ Course configuration saved to: {save_path}")
        print(f"📊 Configuration summary:")
        print(f"   Course: {config['courseName']}")
        print(f"   Assignments: {len(config['assignments'])}")
        print(f"   Graders: {len(config['graders'])}")
        print(f"\nYou can now use this configuration with:")
        print(f"   bscli --course-config {save_path} assignments list")
        print(f"\nor in the folder where course.json is stored:")
        print(f"   bscli assignments list")

    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


def create_course_config(ctx):
    """Create course configuration interactively."""
    print("🏗️  Course Configuration Creator")
    print("=" * 50)
    print()

    api = ctx.api()

    # Step 1: Get course selection
    try:
        course_enrollment = _get_course_selection(api)
        if not course_enrollment:
            return

        course_name = course_enrollment.org_unit.name
        org_unit_id = course_enrollment.org_unit.id
        print(f"\n📚 Selected course: {course_name}")
    except Exception as e:
        print(f"❌ Failed to get courses: {e}")
        return

    # Step 2: Basic course info
    print("\n" + "=" * 50)
    print("BASIC COURSE INFORMATION")
    print("=" * 50)

    print("\nEnter a short internal identifier for this course:")
    print("This will be used for file organization and plugins.")
    print("Examples: 'se2024', 'algorithms', 'proc'")

    def validate_identifier(value):
        return value.replace("-", "").replace("_", "").isalnum()

    course_identifier = _get_valid_input(
        "Course identifier: ", validate_identifier
    ).lower()

    # Step 3: Assignment defaults
    print("\n" + "=" * 50)
    print("ASSIGNMENT DEFAULTS")
    print("=" * 50)
    defaults = _get_assignment_defaults()

    # Step 4: Process assignments
    print("\n" + "=" * 50)
    print("ASSIGNMENTS")
    print("=" * 50)
    try:
        assignments = _process_assignments(api, org_unit_id)
    except Exception as e:
        print(f"❌ Failed to fetch assignments: {e}")
        assignments = {}

    # Step 5: Process graders
    print("\n" + "=" * 50)
    print("GRADERS")
    print("=" * 50)
    graders = _process_graders(api, org_unit_id)

    if not graders:
        print(
            "⚠️  No graders configured - you'll need to add them manually to the config file later"
        )

    # Step 6: Create and save configuration
    config = {
        "courseName": course_name,
        "course": course_identifier,
        "assignmentDefaults": defaults,
        "assignments": assignments,
        "graders": graders,
    }

    _save_config(config, course_identifier)

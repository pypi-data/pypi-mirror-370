"""
FileSender integration for Brightspace CLI.

Uses vendored filesender.py from:
https://github.com/filesender/filesender/blob/master/scripts/client/filesender.py

License: BSD (see vendored code)
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from bscli.config import Config

logger = logging.getLogger(__name__)


def generate_encryption_password():
    """Generate a secure encryption password that meets FileSender requirements."""
    import random
    import string

    # Ensure we have at least one of each required character type
    lowercase = random.choice(string.ascii_lowercase)
    uppercase = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*")

    # Generate additional random characters
    remaining_length = random.randint(8, 12)  # Total length between 12-16
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    additional = "".join(random.choice(all_chars) for _ in range(remaining_length))

    # Combine and shuffle
    password_chars = list(lowercase + uppercase + digit + special + additional)
    random.shuffle(password_chars)

    return "".join(password_chars)


def is_valid_password(password):
    """Check if password meets FileSender requirements."""
    if len(password) < 8:
        return False

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    return has_lower and has_upper and has_digit and has_special


@dataclass
class FileSenderConfig:
    base_url: str
    username: str
    email: str
    apikey: str
    default_transfer_days_valid: int = 10

    @staticmethod
    def from_json(obj: dict):
        return FileSenderConfig(
            base_url=obj["baseUrl"],
            username=obj["username"],
            email=obj["email"],
            apikey=obj["apikey"],
            default_transfer_days_valid=obj.get("defaultTransferDaysValid", 10),
        )


class FileSenderUploader:
    def __init__(
        self, dist_path: Path, config: Config, filesender_config: FileSenderConfig
    ):
        self.dist_path = dist_path
        self.config = config
        self.filesender_config = filesender_config
        self.upload_results: Dict[str, dict] = {}

    def _get_filesender_script_path(self) -> Path:
        """Get path to the vendored filesender.py script."""
        return Path(__file__).parent / "filesender_client" / "filesender.py"

    def _upload_file(
        self,
        file_path: Path,
        grader_email: str,
        subject: str,
        message: str,
        encryption_password: Optional[str] = None,
    ) -> bool:
        """Upload a single file using the vendored FileSender CLI script."""

        script_path = self._get_filesender_script_path()

        if not script_path.exists():
            logger.error(f"FileSender script not found at: {script_path}")
            return False

        # Prepare command arguments
        cmd = [
            "python3",
            str(script_path),
            "-b",
            self.filesender_config.base_url + "/rest.php",
            "-u",
            self.filesender_config.username,
            "-a",
            self.filesender_config.apikey,
            "-f",
            self.filesender_config.email,
            "-r",
            grader_email,
            "-s",
            subject,
            "-m",
            message,
            "--days",
            str(self.filesender_config.default_transfer_days_valid),
        ]

        # Add encryption if configured
        if encryption_password:
            cmd.extend(["-e", encryption_password])

        cmd.append(str(file_path))

        try:
            # Run the FileSender script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300,  # 5 minute timeout
            )

            logger.info(f"FileSender upload successful for {file_path.name}")
            logger.debug(f"FileSender output: {result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"FileSender upload failed for {file_path.name}")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Exit code: {e.returncode}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")

            # Try to run FileSender script directly to see its help/error output
            try:
                help_result = subprocess.run(
                    ["python3", str(script_path), "--help"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                logger.debug(f"FileSender help output: {help_result.stdout}")
            except Exception:
                logger.debug("Could not run FileSender help command")

            return False
        except subprocess.TimeoutExpired:
            logger.error(f"FileSender upload timed out for {file_path.name}")
            return False

    def upload(
        self,
        assignment_id: str,
        assignment_config,
        course_name: str,
        assignment_name: str,
    ) -> bool:
        """Upload all grader archives for an assignment to FileSender."""
        assignment_path = self.dist_path / assignment_id

        if not assignment_path.exists():
            logger.error(f"Assignment path does not exist: {assignment_path}")
            return False

        success_count = 0
        total_count = 0

        subject = f"{course_name}: {assignment_name}"
        encryption_password = getattr(assignment_config, "encryption_password", None)

        # Handle optional encryption
        if encryption_password:
            print(f"\n🔐 Assignment Encryption Password: {encryption_password}")
        else:
            print(f"\n📂 Files will be sent without encryption")
            print("⚠️  Consider adding an encryption password for sensitive content")
        print()

        for grader_id, grader_info in self.config.graders.items():
            archive_path = assignment_path / f"{assignment_id}-{grader_id}.7z"

            if not archive_path.exists():
                logger.warning(
                    f"Archive not found for grader {grader_id}: {archive_path}"
                )
                continue

            total_count += 1

            # Create message content
            message = self._create_message(
                grader_id, course_name, assignment_name, bool(encryption_password)
            )

            print(f"📤 Uploading archive for {grader_id}...")

            if self._upload_file(
                archive_path, grader_info.email, subject, message, encryption_password
            ):
                success_count += 1
                self.upload_results[grader_id] = {
                    "status": "success",
                    "file": archive_path.name,
                    "encrypted": bool(encryption_password),
                }
                print(f"✅ {grader_id}: Upload successful")
            else:
                self.upload_results[grader_id] = {
                    "status": "failed",
                    "file": archive_path.name,
                    "error": "Upload failed",
                    "encrypted": bool(encryption_password),
                }
                print(f"❌ {grader_id}: Upload failed")

        if total_count == 0:
            logger.warning("No archives found to upload")
            return False

        print(f"\n📊 Upload Summary: {success_count}/{total_count} successful")

        if success_count > 0 and encryption_password:
            print(
                f"\n🔐 REMINDER: Distribute the password '{encryption_password}' securely to graders"
            )
            print(
                "   The graders will need this password to decrypt their archives from FileSender"
            )
        elif success_count > 0:
            print(f"\n📂 Files sent successfully without encryption")

        logger.info(
            f"FileSender upload completed: {success_count}/{total_count} successful"
        )
        return success_count == total_count

    def _create_message(
        self, grader_id: str, course_name: str, assignment_name: str, is_encrypted: bool
    ) -> str:
        """Create email message content for grader."""
        if is_encrypted:
            message_lines = [
                f"Grading assignment for {course_name} - {assignment_name}",
                "",
                "Your submissions archive can be downloaded via the link below.",
                "",
                "IMPORTANT: This archive is encrypted.",
                "You will need a decryption password to access the files.",
                "You will receive the password through a separate secure channel.",
                "Please contact the instructor if you have not received the password.",
                "",
                "Download the archive from the FileSender link, using the provided password.",
                "Then extract and review the submissions for grading.",
                "",
                f"Grader: {grader_id}",
            ]
        else:
            message_lines = [
                f"Grading assignment for {course_name} - {assignment_name}",
                "",
                "Your submissions archive can be downloaded via the link below.",
                "",
                "Download the archive from the FileSender link.",
                "Then extract and review the submissions for grading.",
                "",
                f"Grader: {grader_id}",
            ]

        return "\n".join(message_lines)

    def get_upload_status(self, grader_id: str) -> Optional[dict]:
        """Get the upload status for a specific grader."""
        return self.upload_results.get(grader_id)

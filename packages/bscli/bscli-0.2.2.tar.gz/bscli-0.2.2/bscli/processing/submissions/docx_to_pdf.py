import logging
import subprocess
from pathlib import Path

from bscli.processing import SubmissionsProcessing
from bscli.processing.utils import get_all_files

logger = logging.getLogger(__name__)


class DocxToPdf(SubmissionsProcessing):
    def process_submission(self, submission_path: Path):
        for file in get_all_files(submission_path):
            if file.suffix.lower() == ".docx":
                args = [
                    "libreoffice",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    file.parent,
                    file,
                ]
                cp = subprocess.run(args, shell=False, check=False, capture_output=True)
                if cp.returncode != 0:
                    logger.warning(
                        'Converting "%s" to PDF failed: %s (exit code %d)',
                        file.name,
                        cp.stderr.decode("utf-8"),
                        cp.returncode,
                    )

    def execute(self, path: Path):
        # Check whether libreoffice is installed.
        args = ["libreoffice", "--version"]
        try:
            cp = subprocess.run(args, shell=False, check=False, capture_output=True)
            if cp.returncode == 0:
                logger.debug("Found LibreOffice version %s", cp.stdout.decode("utf-8"))
                super().execute(path)
            else:
                logger.warning("Skipping DOCX to PDF pass as LibreOffice was not found")
        except FileNotFoundError:
            logger.warning("Skipping DOCX to PDF pass as LibreOffice was not found")

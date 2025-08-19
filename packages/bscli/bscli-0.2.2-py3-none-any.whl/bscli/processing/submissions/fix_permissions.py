import logging
import os
import stat
import time
from pathlib import Path

from bscli.processing import SubmissionsProcessing
from bscli.processing.utils import get_all_files

logger = logging.getLogger(__name__)


class FixFilePermissions(SubmissionsProcessing):
    READABLE = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH

    def process_submission(self, submission_path: Path):
        for file in get_all_files(submission_path):
            stat_ = file.stat()
            permissions = stat.S_IMODE(stat_.st_mode)

            # Make sure we have read permissions to the files.
            # It can happen students submit files that are not readable by default.
            # One common cause is Wireshark packet captures as it runs as root.
            # The produced capture is stored as having root as the owner, which often leads to students mangling permissions when submitting them in tars.
            if permissions & self.READABLE != self.READABLE:
                os.chmod(file, permissions | self.READABLE)

            # Zip files do not support last modified timestamps before 1980.
            # This means trying to zip such files will fail, which has happened with some student submissions.
            # As such, update the last modified timestamp to the current time for all such files.
            # https://stackoverflow.com/questions/3725662/what-is-the-earliest-timestamp-value-that-is-supported-in-zip-file-format
            if time.localtime(stat_.st_mtime).tm_year < 1980:
                os.utime(file)

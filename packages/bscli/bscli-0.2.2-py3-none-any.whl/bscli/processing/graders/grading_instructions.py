import importlib.resources
import logging
import shutil
from importlib.abc import Traversable
from pathlib import Path

from bscli.config import AssignmentConfig
from bscli.downloader import AssignmentInfo
from bscli.processing import GraderProcessing
from bscli.progress import ProgressReporter

logger = logging.getLogger(__name__)


class CreateGradingInstructions(GraderProcessing):
    def __init__(
        self,
        assignment_info: AssignmentInfo,
        assignment_config: AssignmentConfig,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.assigment_info = assignment_info
        self.assignment_config = assignment_config

    def process_grader(self, grader_path: Path):
        if self.assigment_info.grade_object or self.assigment_info.grade_scheme is None:
            logger.warning(
                "No assignment info provided, skipping grading instructions creation."
            )
            return

        grade_name = self.assigment_info.grade_object.name
        grade_type = self.assigment_info.grade_object.grade_type
        scheme_name = self.assigment_info.grade_scheme.name
        symbols = [f'"{r.symbol}"' for r in self.assigment_info.grade_scheme.ranges]
        aliases = self.assignment_config.grade_aliases

        assert grade_type in [
            "SelectBox",
            "Numeric",
        ], "Update grading instructions for new grade type"

        with open(grader_path / "grading_instructions.txt", "w", encoding="utf-8") as f:
            f.write(
                f'This document outlines the grading instructions for "{self.assigment_info.assignment.name}" of "{self.assigment_info.course.org_unit.name}" if using the Brightspace upload script.\n'
            )
            f.write("\n")
            f.write(
                "There is a folder for each submission you have to grade in the submissions/ folder.\n"
            )
            f.write(
                'In there you find a "feedback.txt" template file with some information about that submission.\n'
            )
            f.write(
                "It also contains two parts you have to fill out: the grade and the feedback.\n"
            )
            f.write("Instructions for filling out these parts can be found below.\n")
            f.write(
                "After all feedback and grades have been filled out, run `bscli upload` to upload the grades and feedback to Brightspace using the API.\n"
            )
            if self.assignment_config.draft_feedback:
                f.write("Your feedback and grades will be uploaded in a draft state.\n")
                f.write(
                    "Before they are visible to students, they have to be published in Brightspace.\n"
                )
            else:
                f.write(
                    "Your feedback and grades will be uploaded in a published state.\n"
                )
                f.write(
                    "This means the feedback and grades will be immediately visible to students.\n"
                )
            f.write("\n")
            f.write("[Feedback]\n")
            f.write(
                "Feedback is written in a mostly plaintext style, with some Markdown influence.\n"
            )
            f.write(
                "Paragraphs are formed similar to Markdown, and there is support for inline code and code blocks.\n"
            )
            f.write(
                "Inline code is specified by putting text between single backtick '`' characters.\n"
            )
            f.write(
                "Code blocks are specified by putting text between triple backtick '```' characters, which may span multiple lines.\n"
            )
            f.write(
                f'Code blocks can specify the code language on a per-block basis, but defaults to "{self.assignment_config.default_code_block_language}".\n'
            )
            f.write(
                'See "readme.txt" for a more elaborate explanation of the feedback syntax.\n'
            )
            f.write("\n")
            f.write("[Grade]\n")
            f.write('By default the grade has the placeholder "TODO" value.\n')
            f.write(
                "Any submission still having this placeholder value will be skipped when uploading the grades and feedback.\n"
            )
            f.write("\n")
            f.write(
                f'The assignment is linked to grade "{grade_name}", which is a "{grade_type}" grade using scheme "{scheme_name}".\n'
            )
            if grade_type == "Numeric":
                f.write(
                    f"This means you have to replace the placeholder value with a numeric value between {0.0} and {self.assigment_info.assignment.assessment.score_denominator}.\n"
                )
                f.write(
                    'It does not matter whether you use a dot or a period as the decimal separator, "9.5" and "9,5" will both be parsed into a 9.5.\n'
                )
            elif grade_type == "SelectBox":
                f.write(
                    f'This means you have to replace the placeholder value with one of the following values: {", ".join(symbols)}.\n'
                )
                f.write(
                    'The case of the symbol does not matter, "good", "gOOD", "GOOD", and "Good" are all equivalent for example.\n'
                )
            if aliases:
                f.write("\n")
                f.write("[Aliases]\n")
                f.write("You can also enter one of the grade aliases listed below.\n")
                f.write(
                    'If your grade matches any of the values to the left of the "=>" arrow (case insensitive), it is replaced with the value to the right.\n'
                )
                f.write(
                    "These aliases are usually provided as a shorthand notation for long grade symbols which are otherwise tedious and error prone to type out.\n"
                )
                f.write(
                    'Another use case may be to mimic "SelectBox" style grades for a "Numeric" grades, mapping a symbol to a numeric grade value.\n'
                )
                f.write("\n")
                for alias, value in aliases.items():
                    f.write(f'"{alias}" => "{value}"\n')


class AddGraderFiles(GraderProcessing):
    def __init__(
        self,
        grader_data_path: Traversable,
        course_path: Path,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.grader_data_path = grader_data_path
        self.course_path = course_path

    def process_grader(self, grader_path: Path):
        # TODO: some check to prevent overwriting student files? Perhaps rename them in such cases?
        with importlib.resources.as_file(self.grader_data_path) as grader_data_path:
            shutil.copytree(grader_data_path, grader_path, dirs_exist_ok=True)

        course_readme_path = self.course_path / "course_readme.txt"
        course_grading_function_path = self.course_path / "course_grading_function.sh"

        if course_readme_path.exists():
            shutil.copyfile(course_readme_path, grader_path / course_readme_path.name)
        if course_grading_function_path.exists():
            shutil.copyfile(
                course_grading_function_path,
                grader_path / course_grading_function_path.name,
            )


class InjectGraderFiles(GraderProcessing):
    def __init__(
        self,
        config: AssignmentConfig,
        inject_path: Path,
        progress_reporter: ProgressReporter = None,
    ):
        super().__init__(progress_reporter)
        self.inject_path = inject_path / config.identifier / "grader"

    def process_grader(self, grader_path: Path):
        # TODO: some check to prevent overwriting student files? Perhaps rename them in such cases?
        shutil.copytree(self.inject_path, grader_path, dirs_exist_ok=True)

    def execute(self, path: Path):
        if self.inject_path.exists():
            super().execute(path)

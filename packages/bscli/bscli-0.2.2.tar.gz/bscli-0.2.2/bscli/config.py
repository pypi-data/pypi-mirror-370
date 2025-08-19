from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import jsonschema

import bscli.utils


@dataclass
class DivisionConfig:
    method: str
    grader_weights: dict[str, float]
    group_category_name: str
    group_mapping: dict[str, str]

    @staticmethod
    def from_json(obj: dict):
        return DivisionConfig(
            method=obj["method"],
            grader_weights=obj.get("graderWeights", dict()),
            group_category_name=obj.get("groupCategoryName", ""),
            group_mapping=obj.get("groupMapping", dict()),
        )


@dataclass
class AssignmentBase:
    ignored_submissions: list[str]
    draft_feedback: bool
    default_code_block_language: str
    division: DivisionConfig
    grade_aliases: dict[str, str]
    file_hierarchy: str
    remove_files: list[str]
    remove_folders: list[str]
    remove_mime_types: list[str]
    graded_by_footer: bool

    @staticmethod
    def from_partial_json(obj: dict):
        return AssignmentBase(
            ignored_submissions=obj.get("ignoredSubmissions", []),
            draft_feedback=obj.get("draftFeedback", False),
            default_code_block_language=obj.get("defaultCodeBlockLanguage", "clike"),
            division=(
                DivisionConfig.from_json(obj["division"]) if "division" in obj else None
            ),
            grade_aliases=obj.get("gradeAliases", dict()),
            file_hierarchy=obj.get("fileHierarchy", "original"),
            remove_files=obj.get("removeFiles", []),
            remove_folders=obj.get("removeFolders", []),
            remove_mime_types=obj.get("removeMimeTypes", []),
            graded_by_footer=obj.get("gradedByFooter", True),
        )

    @staticmethod
    def from_json_or_default(default, obj: dict):
        return AssignmentBase(
            ignored_submissions=obj.get(
                "ignoredSubmissions", default.ignored_submissions
            ),
            draft_feedback=obj.get("draftFeedback", default.draft_feedback),
            default_code_block_language=obj.get(
                "defaultCodeBlockLanguage", default.default_code_block_language
            ),
            division=(
                DivisionConfig.from_json(obj["division"])
                if "division" in obj
                else default.division
            ),
            grade_aliases=obj.get("gradeAliases", default.grade_aliases),
            file_hierarchy=obj.get("fileHierarchy", default.file_hierarchy),
            remove_files=obj.get("removeFiles", default.remove_files),
            remove_folders=obj.get("removeFolders", default.remove_folders),
            remove_mime_types=obj.get("removeMimeTypes", default.remove_mime_types),
            graded_by_footer=obj.get("gradedByFooter", default.graded_by_footer),
        )


@dataclass
class AssignmentConfig(AssignmentBase):
    name: str
    identifier: str
    encryption_password: Optional[str]

    @staticmethod
    def from_json(identifier: str, default: AssignmentBase, obj: dict):
        base = AssignmentBase.from_json_or_default(default, obj)

        return AssignmentConfig(
            ignored_submissions=base.ignored_submissions,
            draft_feedback=base.draft_feedback,
            default_code_block_language=base.default_code_block_language,
            division=base.division,
            grade_aliases=base.grade_aliases,
            file_hierarchy=base.file_hierarchy,
            remove_files=base.remove_files,
            remove_folders=base.remove_folders,
            remove_mime_types=base.remove_mime_types,
            graded_by_footer=base.graded_by_footer,
            encryption_password=obj.get("encryptionPassword", None),
            name=obj["name"],
            identifier=identifier,
        )


@dataclass
class GraderConfig:
    name: str
    identifier: str
    email: str
    contact_email: str

    @staticmethod
    def from_json(identifier: str, obj: dict):
        return GraderConfig(
            name=obj["name"],
            identifier=identifier,
            email=obj["email"],
            contact_email=obj.get("contactEmail", obj["email"]),
        )


@dataclass
class Config:
    course: str  # used to find course specific hooks/scripts
    course_name: str  # Brightspace course name
    assignment_defaults: AssignmentBase
    assignments: dict[str, AssignmentConfig]
    graders: dict[str, GraderConfig]

    @staticmethod
    def from_json(obj: dict):
        assignment_defaults = AssignmentBase.from_partial_json(
            obj["assignmentDefaults"]
        )

        return Config(
            course=obj["course"],
            course_name=obj["courseName"],
            assignment_defaults=assignment_defaults,
            assignments={
                id_: AssignmentConfig.from_json(
                    id_, assignment_defaults, obj["assignments"][id_]
                )
                for id_ in obj["assignments"]
            },
            graders={
                id_: GraderConfig.from_json(id_, obj["graders"][id_])
                for id_ in obj["graders"]
            },
        )


def load_validated(path: Path, schema, type_):
    json_obj = bscli.utils.read_json(path)
    jsonschema.validate(instance=json_obj, schema=schema)
    return type_.from_json(json_obj)

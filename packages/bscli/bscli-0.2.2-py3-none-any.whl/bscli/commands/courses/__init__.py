import argparse
from bscli.commands.courses.list import ListCoursesCommand
from bscli.commands.courses.create_config import create_course_config
from bscli.commands.base import BaseCommand, BaseGroupCommand


class ConfigCreateCommand(BaseCommand):
    """Create course configuration interactively."""

    name = "create-config"
    help = "Create course configuration interactively"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def execute(self, ctx, args: argparse.Namespace) -> None:
        create_course_config(ctx)


class CoursesCommand(BaseGroupCommand):
    """Course management commands."""

    name = "courses"
    help = "📚 Course management"

    def __init__(self):
        self.subcommands = {
            ListCoursesCommand.name: ListCoursesCommand,
            ConfigCreateCommand.name: ConfigCreateCommand,
        }

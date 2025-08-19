#!/usr/bin/env python3
from bscli.cli import CLI
from bscli.commands.courses import CoursesCommand
from bscli.commands.assignments import AssignmentsCommand
from bscli.commands.feedback import FeedbackCommand
from bscli.commands.config import ConfigCommand


def main():
    """Main entry point for the Brightspace CLI."""
    cli = CLI()

    cli.register_command(CoursesCommand)
    cli.register_command(AssignmentsCommand)
    cli.register_command(FeedbackCommand)
    cli.register_command(ConfigCommand)

    cli.run()


if __name__ == "__main__":
    main()

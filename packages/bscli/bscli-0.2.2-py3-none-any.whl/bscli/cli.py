#!/usr/bin/env python3
"""Modern CLI framework for Brightspace CLI."""

import argparse
import importlib.resources
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Type, Optional, Callable, Any
from importlib.abc import Traversable

import bsapi
import bsapi.helper

from bscli.config import Config, load_validated
from bscli.filesender import FileSenderConfig
from bscli.oauth import perform_oauth_interactive, TokenManager
from bscli.utils import read_json
from bscli.division import DivisionLog
from bscli.course_plugin import CoursePlugin, DefaultCoursePlugin


DEFAULT_CONFIG_PATH = Path.home() / ".config/bscli"


class Context:
    """CLI context providing lazy-loaded resources."""

    def __init__(self, config_dir: Path, course_config_path: Path, root_path: Path):
        self.config_dir = config_dir
        self.course_config_path = course_config_path
        self.root_path = root_path

        self._course_config: Optional[Config] = None
        self._api_config: Optional[bsapi.APIConfig] = None
        self._filesender_config: Optional[FileSenderConfig] = None
        self._api: Optional[bsapi.BSAPI] = None
        self._api_helper: Optional[bsapi.helper.APIHelper] = None
        self._token_manager: Optional[TokenManager] = None
        self._package_data_path: Optional[Traversable] = None
        self._course_plugin: Optional[CoursePlugin] = None

    def course_config(self) -> Config:
        if self._course_config is None:
            if not self.course_config_path.exists():
                print(f"❌ Course config not found: {self.course_config_path}")
                print("💡 Create a course.json file or specify --course-config path")
                sys.exit(1)

            schema = read_json(
                self.package_data_path() / "schema" / "course.schema.json"
            )
            self._course_config = load_validated(
                self.course_config_path, schema, Config
            )
        return self._course_config

    def api_config(self) -> bsapi.APIConfig:
        if self._api_config is None:
            path = self.config_dir / "bsapi.json"
            if not path.exists():
                print(f"❌ API config not found: {path}")
                print("💡 Run: bscli config init bsapi")
                sys.exit(1)

            schema = read_json(
                self.package_data_path() / "schema" / "bsapi.schema.json"
            )
            self._api_config = load_validated(path, schema, bsapi.APIConfig)

            # Environment overrides
            if client_id := os.environ.get("BSCLI_CLIENT_ID"):
                self._api_config.client_id = client_id
            if client_secret := os.environ.get("BSCLI_CLIENT_SECRET"):
                self._api_config.client_secret = client_secret
        return self._api_config

    def filesender_config(self) -> FileSenderConfig:
        if self._filesender_config is None:
            path = self.config_dir / "filesender.json"
            if not path.exists():
                print(f"❌ FileSender config not found: {path}")
                print("💡 Run: bscli config init filesender")
                sys.exit(1)

            schema = read_json(
                self.package_data_path() / "schema" / "filesender.schema.json"
            )
            self._filesender_config = load_validated(path, schema, FileSenderConfig)
        return self._filesender_config

    def api(self) -> bsapi.BSAPI:
        if self._api is None:
            self._api = self._connect_api()
        return self._api

    def api_helper(self) -> bsapi.helper.APIHelper:
        if self._api_helper is None:
            self._api_helper = bsapi.helper.APIHelper(self.api())
        return self._api_helper

    def token_manager(self) -> TokenManager:
        if self._token_manager is None:
            self._token_manager = TokenManager(self.config_dir / "token.json")
        return self._token_manager

    def package_data_path(self) -> Traversable:
        if self._package_data_path is None:
            import bscli

            self._package_data_path = importlib.resources.files(bscli).joinpath("data")
        return self._package_data_path

    def course_plugin(self) -> CoursePlugin:
        if self._course_plugin is None:
            self._course_plugin = DefaultCoursePlugin()
            plugin_path = (
                self.root_path
                / "data"
                / "course"
                / self.course_config().course
                / "plugin.py"
            )
            if plugin_path.is_file():
                self._course_plugin = self._load_plugin(plugin_path)
                if not self._course_plugin.initialize():
                    print("⚠️  Warning: Course plugin failed to initialize")
        return self._course_plugin

    def _connect_api(self) -> bsapi.BSAPI:
        config = self.api_config()
        token = self.token_manager().get_token()

        if not token:
            print("🔐 No access token found. Starting authentication...")
            try:
                token = perform_oauth_interactive(config)
                self.token_manager().save_token(token)
                print("✅ Authentication successful")
            except KeyboardInterrupt:
                print("\n❌ Authentication cancelled")
                sys.exit(1)

        api = bsapi.BSAPI.from_config(config, token)

        # Test connection and handle token expiration
        try:
            _ = api.whoami()
            return api
        except bsapi.APIError as e:
            if "invalid" in str(e).lower() or "expired" in str(e).lower():
                print("🔄 Token expired, re-authenticating...")
                token = perform_oauth_interactive(config)
                self.token_manager().save_token(token)
                api = bsapi.BSAPI.from_config(config, token)
                _ = api.whoami()
                return api
            else:
                print(f"❌ API error: {e}")
                print("💡 Check your network connection and API configuration")
                sys.exit(1)

    def _load_plugin(self, path: Path) -> CoursePlugin:
        spec = importlib.util.spec_from_file_location("bscli.plugin", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module.create_course_plugin(self)

    # Utility methods
    def has_distributed(self, assignment_id: str) -> bool:
        return (self.root_path / "distributions" / assignment_id).is_dir()

    def is_valid_assignment_id(self, assignment_id: str) -> bool:
        assignments = self.course_config().assignments
        if assignment_id not in assignments:
            print(f"❌ Unknown assignment: {assignment_id}")
            print(f"💡 Available assignments: {', '.join(assignments.keys())}")
            return False
        return True

    def load_division_log(self, assignment_id: str) -> DivisionLog:
        if not self.has_distributed(assignment_id):
            return DivisionLog()
        return DivisionLog.read(self.root_path / "logs" / assignment_id)


class CLI:
    """Main CLI application."""

    def __init__(self):
        self.commands: Dict[str, Type] = {}
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            encoding="utf-8",
            filemode="a",
        )
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        logging.getLogger().addHandler(console)

    def register_command(self, command_class: Type) -> None:
        """Register a command class."""
        self.commands[command_class.name] = command_class

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Brightspace CLI",
            epilog=self._get_help_epilog(),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Global arguments
        parser.add_argument(
            "--config-dir",
            type=Path,
            default=DEFAULT_CONFIG_PATH,
            help="Global configuration directory (default: ~/.config/bscli)",
        )
        parser.add_argument(
            "--course-config",
            type=Path,
            default=Path("course.json"),
            help="Course configuration file (default: ./course.json)",
        )
        parser.add_argument(
            "--root",
            type=Path,
            default=Path("."),
            help="Working directory (default: .)",
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        for command_class in self.commands.values():
            cmd_parser = subparsers.add_parser(
                command_class.name, help=command_class.help
            )
            command_class().setup_parser(cmd_parser)

        return parser

    def _get_help_epilog(self) -> str:
        """Get help epilog text."""
        return """
Common workflows:
  Setup:                bscli config init bsapi && bscli config init filesender
  Course setup:         bscli courses config-create
  Assignment handling:  bscli assignments download → bscli feedback upload
  Distribution:         bscli assignments distribute homework-1

Examples:
  bscli courses list                                   # Show all courses
  bscli courses config-create                          # Create course configuration
  bscli assignments list                               # Show all assignments
  bscli assignments download homework-1                # Download submissions for homework-1
  bscli assignments distribute homework-1              # Distribute homework-1 to graders
  bscli assignments find-grader "john doe"             # Find which grader is assigned to a student
  bscli assignments grading-progress hw1               # Check grading progress for assignment
  bscli assignments check-grading-groups hw1           # Check Brightspace grading groups setup
  bscli assignments list-submissions hw1               # List all submissions for assignment
  bscli assignments list-submissions --ungraded hw1    # List ungraded submissions
  bscli assignments list-submissions --undistributed   # List undistributed submissions
  bscli feedback upload                                # Upload graded submissions back
"""

    def run(self, args: Optional[list] = None) -> None:
        """Run the CLI application."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.command:
            parser.print_help()
            return

        # Setup logging with root path
        logging.basicConfig(
            filename=parsed_args.root / "app.log",
            level=logging.INFO,
            encoding="utf-8",
            filemode="a",
        )

        # Create context
        ctx = Context(
            parsed_args.config_dir, parsed_args.course_config, parsed_args.root
        )

        # Execute command
        command_class = self.commands[parsed_args.command]
        command = command_class()
        command.execute(ctx, parsed_args)

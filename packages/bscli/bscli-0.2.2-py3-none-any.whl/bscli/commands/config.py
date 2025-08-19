import argparse
import json
from bscli.commands.base import BaseCommand, BaseGroupCommand


class ShowCommand(BaseCommand):
    """Show current configuration status."""

    name = "show"
    help = "Show config status"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        pass

    def execute(self, ctx, args: argparse.Namespace) -> None:
        show_config(ctx)


class InitCommand(BaseCommand):
    """Initialize configurations."""

    name = "init"
    help = "Initialize config"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        init_sub = parser.add_subparsers(dest="init_type")
        init_sub.add_parser("bsapi", help="Initialize API config")
        init_sub.add_parser("filesender", help="Initialize FileSender config")
        init_sub.add_parser("all", help="Initialize all configs")

    def execute(self, ctx, args: argparse.Namespace) -> None:
        handle_init(ctx, args)


class AuthorizeCommand(BaseCommand):
    """Request new OAuth token."""

    name = "authorize"
    help = "Request new OAuth token"

    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--manual",
            action="store_true",
            help="Use manual authorization (just show URL and ask for code)",
        )

    def execute(self, ctx, args: argparse.Namespace) -> None:
        handle_authorize(ctx, args)


class ConfigCommand(BaseGroupCommand):
    """Configuration management commands."""

    name = "config"
    help = "⚙️ Configuration management"

    def __init__(self):
        self.subcommands = {
            ShowCommand.name: ShowCommand,
            InitCommand.name: InitCommand,
            AuthorizeCommand.name: AuthorizeCommand,
        }


def handle_init(ctx, args):
    """Handle init subcommands."""
    if not hasattr(args, "init_type") or args.init_type is None:
        print("❌ Init command requires a subcommand")
        print("\nAvailable commands:")
        print("  bsapi             Initialize Brightspace API configuration")
        print("  filesender        Initialize FileSender configuration")
        print("  all               Initialize all configurations")
        return

    init_handlers = {
        "bsapi": lambda: init_bsapi_config(ctx),
        "filesender": lambda: init_filesender_config(ctx),
        "all": lambda: init_all_config(ctx),
    }

    handler = init_handlers.get(args.init_type)
    if handler:
        handler()
    else:
        print(f"❌ Unknown init command: {args.init_type}")


def handle_authorize(ctx, args):
    """Handle authorization command."""
    from bscli.oauth import perform_oauth_interactive, perform_oauth_manual

    print("🔐 OAuth Token Authorization")
    print("=" * 50)

    # Delete existing token
    token_file = ctx.config_dir / "token.json"
    if token_file.exists():
        try:
            token_file.unlink()
            print("✅ Existing token deleted")
        except Exception as e:
            print(f"⚠️  Could not delete existing token: {e}")
    else:
        print("ℹ️  No existing token found")

    print()

    # Get API config
    try:
        api_config = ctx.api_config()
    except SystemExit:
        return

    # Choose flow based on flag
    if args.manual:
        print("Using manual authorization mode...")
        try:
            token = perform_oauth_manual(api_config)
            ctx.token_manager().save_token(token)
            print("✅ Token saved successfully")
            print("You can now use the API.")
        except KeyboardInterrupt:
            print("\n❌ Authorization cancelled")
        except Exception as e:
            print(f"❌ Authorization failed: {e}")
    else:
        print("Using interactive authorization mode...")
        try:
            token = perform_oauth_interactive(api_config)
            if token:
                ctx.token_manager().save_token(token)
                print("✅ Token saved successfully")
                print("You can now use the API.")
            else:
                print("❌ Interactive authorization failed")
                print("Try using --manual flag for manual authorization")
        except KeyboardInterrupt:
            print("\n❌ Authorization cancelled")
        except Exception as e:
            print(f"❌ Authorization failed: {e}")


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


def show_config(ctx):
    """Show current configuration status."""
    print("📋 Configuration Status")
    print("=" * 40)
    print()

    configs = [
        (
            "Brightspace API",
            ctx.config_dir / "bsapi.json",
            ["lmsUrl", "clientId", "leVersion", "lpVersion"],
        ),
        (
            "FileSender",
            ctx.config_dir / "filesender.json",
            ["baseUrl", "email", "defaultTransferDaysValid"],
        ),
    ]

    for name, config_file, keys in configs:
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config_data = json.load(f)
                print(f"✅ {name} Configuration:")
                print(f"   File: {config_file}")
                for key in keys:
                    value = config_data.get(key, "Not set")
                    if key == "clientId" and value != "Not set":
                        value = f"{value[:8]}..."
                    if key == "defaultTransferDaysValid":
                        value = f"{value} days"
                    print(f"   {key}: {value}")
            except Exception as e:
                print(f"❌ {name} config file exists but is invalid: {e}")
        else:
            print(f"❌ {name} Configuration: Not found")
            print(f"   Expected: {config_file}")
        print()

    # Check token
    token_file = ctx.config_dir / "token.json"
    status = (
        "Cached"
        if token_file.exists()
        else "Not cached (will authenticate on first API call)"
    )
    print(f"✅ OAuth Token: {status}")


def init_bsapi_config(ctx):
    """Initialize Brightspace API configuration."""
    print("🔧 Brightspace API Configuration Setup")
    print("=" * 50)
    print()

    config = {}

    # Required fields
    print("Enter your Brightspace OAuth API credentials:")
    config["clientId"] = _get_valid_input("Client ID: ")
    config["clientSecret"] = _get_valid_input("Client Secret: ")

    print("\nEnter your Brightspace LMS URL (without https://):")
    print("Example: brightspace.university.edu")
    config["lmsUrl"] = _get_valid_input("LMS URL: ")

    print("\nEnter your OAuth redirect URI (with https://):")
    print("Example: https://yourdomain.com/callback")
    config["redirectUri"] = _get_valid_input("Redirect URI: ")

    # API Versions with defaults
    print("\nAPI Versions (press Enter for defaults):")
    config["leVersion"] = _get_valid_input("LE Version [1.79]: ", default="1.79")
    config["lpVersion"] = _get_valid_input("LP Version [1.47]: ", default="1.47")

    _save_json_config(ctx, config, "bsapi.json", "Brightspace API")


def init_filesender_config(ctx):
    """Initialize FileSender configuration."""
    print("📤 FileSender Configuration Setup")
    print("=" * 50)
    print()

    config = {}

    print("Enter your FileSender configuration:")
    print("You can find these details in your FileSender account settings.")
    print()

    print("Enter your FileSender base URL:")
    print("Example: https://filesender.surf.nl")
    config["baseUrl"] = _get_valid_input("Base URL: ")

    print("\nEnter your FileSender API username/identifier:")
    print("You can find this on the FileSender profile page.")
    print("Warning: this may not be your login name - it can be a random string!")
    config["username"] = _get_valid_input("Username: ")

    print("\nEnter your email address (as shown on FileSender profile):")
    config["email"] = _get_valid_input("Email: ")

    print("\nEnter your FileSender API key:")
    print("(This should be a long hexadecimal string)")
    config["apikey"] = _get_valid_input("API Key: ")

    print("\nEnter default transfer validity (in days):")

    def validate_days(value):
        try:
            return int(value) > 0
        except ValueError:
            return False

    days_str = _get_valid_input("Transfer validity [14]: ", validate_days, "14")
    config["defaultTransferDaysValid"] = int(days_str)

    _save_json_config(ctx, config, "filesender.json", "FileSender")


def _save_json_config(ctx, config, filename, config_name):
    """Save JSON configuration file."""
    ctx.config_dir.mkdir(exist_ok=True)
    config_file = ctx.config_dir / filename

    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        print(f"\n✅ {config_name} configuration saved to: {config_file}")
        print(f"You can now use {config_name}.")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


def init_all_config(ctx):
    """Initialize all configurations."""
    print("🚀 Configuration Setup")
    print("=" * 50)
    print()
    print("This will set up both Brightspace API and FileSender configurations.")
    print()

    init_bsapi_config(ctx)
    print("\n" + "-" * 50 + "\n")
    init_filesender_config(ctx)
    print("\n🎉 Setup complete!")

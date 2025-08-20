import os
import subprocess
import sys
from pathlib import Path

import click
import inquirer
from click.core import ParameterSource

from arm_cli.config import (
    get_active_project_config,
    get_config_dir,
    load_project_config,
    save_config,
)
from arm_cli.settings import get_setting, load_settings, save_settings, set_setting


@click.group()
def self():
    """Manage the CLI itself"""
    pass


@self.command()
@click.option(
    "--source",
    default=None,
    type=click.Path(exists=True),
    help="Install from a local source path (defaults to current directory if specified without value)",
)
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompts")
@click.pass_context
def update(ctx, source, force):
    config = ctx.obj["config"]  # noqa: F841 - config available for future use
    """Update arm-cli from PyPI or source"""
    if source is None and ctx.get_parameter_source("source") == ParameterSource.COMMANDLINE:
        source = "."

    if source:
        print(f"Installing arm-cli from source at {source}...")

        if not force:
            if not click.confirm(
                "Do you want to install arm-cli from source? This will clear pip " "cache."
            ):
                print("Update cancelled.")
                return

        # Clear Python import cache
        print("Clearing Python caches...")
        subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/pip")])
        subprocess.run(["python", "-c", "import importlib; importlib.invalidate_caches()"])

        # Install from the provided source path
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", source], check=True)
        print(f"arm-cli installed from source at {source} successfully!")
    else:
        print("Updating arm-cli from PyPI...")

        if not force:
            if not click.confirm("Do you want to update arm-cli from PyPI?"):
                print("Update cancelled.")
                return

        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "arm-cli"], check=True)
        print("arm-cli updated successfully!")


@self.group()
def settings():
    """Manage CLI settings"""
    pass


@settings.command("show")
@click.pass_context
def show_settings(ctx):
    """Show the settings file path and contents"""
    from arm_cli.settings import get_settings_file

    settings_file = get_settings_file()
    print(f"Settings file: {settings_file}")
    print()

    if settings_file.exists():
        with open(settings_file, "r") as f:
            print(f.read())
    else:
        print("Settings file does not exist yet.")


@settings.command("get")
@click.argument("key")
@click.pass_context
def get_settings_cmd(ctx, key):
    """Get a specific setting value"""
    from arm_cli.settings import get_setting

    value = get_setting(key)
    if value is not None:
        print(value)
    else:
        print(f"Error: Unknown setting '{key}'")
        # Get available settings to show user
        from arm_cli.settings import load_settings

        settings = load_settings()
        print(f"Available settings: {', '.join(settings.model_fields.keys())}")
        sys.exit(1)


@settings.command("set")
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.pass_context
def set_settings(ctx, key, value):
    """Set a configuration value"""
    from arm_cli.settings import get_setting, load_settings, save_settings, set_setting

    settings = load_settings()

    # If no arguments provided, launch interactive mode
    if key is None and value is None:
        # Get all available settings
        available_settings = list(settings.model_fields.keys())

        # Create choices for inquirer
        choices = []
        for setting_key in available_settings:
            current_val = getattr(settings, setting_key)
            choices.append(f"{setting_key} (current: {current_val})")

        # Ask user to select a setting
        questions = [
            inquirer.List(
                "setting",
                message="Select a setting to modify",
                choices=choices,
                carousel=True,
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                print("Configuration cancelled.")
                return

            # Extract the key from the selected choice
            selected_choice = answers["setting"]
            key = selected_choice.split(" (current:")[0]

        except KeyboardInterrupt:
            print("\nConfiguration cancelled.")
            return

    # If only key is provided, ask for value
    if key is not None and value is None:
        current_value = getattr(settings, key)

        # Create appropriate input question based on type
        if isinstance(current_value, bool):
            questions = [
                inquirer.List(
                    "value",
                    message=f"Set {key} (current: {current_value})",
                    choices=["true", "false"],
                    default="true" if current_value else "false",
                    carousel=True,
                )
            ]
        else:
            questions = [
                inquirer.Text(
                    "value",
                    message=f"Set {key} (current: {current_value})",
                    default=str(current_value),
                )
            ]

        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                print("Configuration cancelled.")
                return

            value = answers["value"]

        except KeyboardInterrupt:
            print("\nConfiguration cancelled.")
            return

    # Now we have both key and value, proceed with validation and setting
    if key is None or value is None:
        print("Error: Both key and value are required.")
        return

    # Check if the key exists in settings
    if not hasattr(settings, key):
        print(f"Error: Unknown setting '{key}'")
        print(f"Available settings: {', '.join(settings.model_fields.keys())}")
        return

    # Get the current value
    current_value = getattr(settings, key)

    # Convert value to the appropriate type based on the current value
    try:
        if isinstance(current_value, int):
            new_value = int(value)
        elif isinstance(current_value, bool):
            if value.lower() in ("true", "1", "yes", "on"):
                new_value = True
            elif value.lower() in ("false", "0", "no", "off"):
                new_value = False
            else:
                print(
                    f"Error: Invalid boolean value '{value}'. Use true/false, 1/0, yes/no, or on/off"
                )
                return
        else:
            new_value = value
    except ValueError as e:
        print(f"Error: Invalid value '{value}' for setting '{key}': {e}")
        return

    # Set the new value
    setattr(settings, key, new_value)
    save_settings(settings)

    print(f"Updated {key}: {current_value} → {new_value}")

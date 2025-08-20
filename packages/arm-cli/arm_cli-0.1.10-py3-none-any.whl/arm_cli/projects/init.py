import json
import sys
from pathlib import Path
from typing import Optional

import click
import inquirer

from arm_cli.config import (
    add_project_to_list,
    copy_default_project_config,
    load_project_config,
    save_config,
)
from arm_cli.settings import get_setting


def _init(ctx, project_path: str, name: Optional[str] = None):
    """Initialize a new project from an existing directory or JSON file"""
    config = ctx.obj["config"]

    project_path_obj = Path(project_path).resolve()

    # Determine if the path is a JSON file or directory
    if project_path_obj.is_file() and project_path_obj.suffix.lower() == ".json":
        # Path is a JSON file - use it directly as the config
        config_file = project_path_obj
        project_dir = project_path_obj.parent

        if name is None:
            name = project_dir.name

        print(f"Using existing JSON config file: {config_file}")
        project_config = load_project_config(str(config_file))

    elif project_path_obj.is_dir():
        # Path is a directory - show interactive menu for JSON files
        project_dir = project_path_obj

        if name is None:
            name = project_dir.name

        # Find all JSON files in the directory
        json_files = list(project_dir.glob("*.json"))

        if not json_files:
            print(f"No JSON files found in {project_dir}")
            print("Creating new project with default configuration...")

            # Create new project config using default template
            try:
                default_config_path = copy_default_project_config()
                with open(default_config_path, "r") as f:
                    default_data = json.load(f)

                # Update with project-specific information
                default_data["name"] = name
                default_data["project_directory"] = str(project_dir)

                # Save the new project config
                project_config_file = project_dir / "arm_cli_project_config.json"
                with open(project_config_file, "w") as f:
                    json.dump(default_data, f, indent=2)

                project_config = load_project_config(str(project_config_file))
                config_file = project_config_file
                print(f"Created new project configuration at {project_config_file}")

            except Exception as e:
                print(f"Error creating project configuration: {e}")
                sys.exit(1)
        else:
            # Create choices for inquirer
            choices = []
            for json_file in json_files:
                choices.append(str(json_file.name))

            # Add default option
            choices.append("Use default configuration")

            # Create the question
            questions = [
                inquirer.List(
                    "config_file",
                    message=f"Select a configuration file from {project_dir.name} or use default",
                    choices=choices,
                    carousel=True,
                )
            ]

            try:
                answers = inquirer.prompt(questions)
                if answers is None:
                    print("Cancelled.")
                    return

                selected_choice = answers["config_file"]

                if selected_choice == "Use default configuration":
                    # Create new project config using default template
                    try:
                        default_config_path = copy_default_project_config()
                        with open(default_config_path, "r") as f:
                            default_data = json.load(f)

                        # Update with project-specific information
                        default_data["name"] = name
                        default_data["project_directory"] = str(project_dir)

                        # Save the new project config
                        project_config_file = project_dir / "project_config.json"
                        with open(project_config_file, "w") as f:
                            json.dump(default_data, f, indent=2)

                        project_config = load_project_config(str(project_config_file))
                        config_file = project_config_file
                        print(f"Created new project configuration at {project_config_file}")

                    except Exception as e:
                        print(f"Error creating project configuration: {e}")
                        sys.exit(1)
                else:
                    # Use the selected JSON file
                    config_file = project_dir / selected_choice
                    print(f"Using configuration file: {config_file}")
                    project_config = load_project_config(str(config_file))

            except KeyboardInterrupt:
                print("\nCancelled.")
                return
    else:
        print(f"Error: {project_path} is not a valid directory or JSON file")
        sys.exit(1)

    # Add to available projects and set as active
    add_project_to_list(config, str(config_file), project_config.name)
    save_config(config)

    print(f"Project '{project_config.name}' initialized and set as active")
    resolved_dir = project_config.get_resolved_project_directory(
        getattr(project_config, "_config_file_path", None)
    )
    print(f"Project directory: {resolved_dir}")


# Create the command object
init = click.command(name="init")(
    click.argument("project_path", type=click.Path(exists=True))(
        click.option("--name", help="Name for the project (defaults to directory name)")(
            click.pass_context(_init)
        )
    )
)

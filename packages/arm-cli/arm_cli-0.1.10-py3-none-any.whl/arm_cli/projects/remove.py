from typing import Optional

import click
import inquirer

from arm_cli.config import (
    get_available_projects,
    print_available_projects,
    print_no_projects_message,
    remove_project_from_list,
    save_config,
)
from arm_cli.settings import get_setting


def _remove(ctx, project: Optional[str] = None):
    """Remove a project from available projects"""
    config = ctx.obj["config"]

    # If no project specified, show interactive list
    if project is None:
        available_projects = get_available_projects(config)

        if not available_projects:
            print("No projects available to remove.")
            return

        # Create choices for inquirer
        choices = []
        for proj in available_projects:
            active_indicator = " *" if proj.path == config.active_project else ""
            choices.append(f"{proj.name}{active_indicator}")

        # Create the question
        questions = [
            inquirer.List(
                "project",
                message="Select a project to remove",
                choices=choices,
                carousel=True,
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if answers is None:
                print("Cancelled.")
                return

            # Extract project name (remove the active indicator if present)
            selected_choice = answers["project"]
            project = selected_choice.replace(" *", "")

        except KeyboardInterrupt:
            print("\nCancelled.")
            return

    # Try to remove the project
    # At this point, project is guaranteed to be a string
    assert project is not None  # type guard

    # Check if this is the active project
    available_projects = get_available_projects(config)
    is_active = False
    for proj in available_projects:
        if proj.name.lower() == project.lower():
            is_active = proj.path == config.active_project
            break

    # Confirm removal, especially for active project
    if is_active:
        confirm_questions = [
            inquirer.Confirm(
                "confirm",
                message=f"Are you sure you want to remove the active project '{project}'? This will clear the active project.",
                default=False,
            )
        ]

        try:
            confirm_answers = inquirer.prompt(confirm_questions)
            if confirm_answers is None or not confirm_answers["confirm"]:
                print("Removal cancelled.")
                return
        except KeyboardInterrupt:
            print("\nCancelled.")
            return
    else:
        confirm_questions = [
            inquirer.Confirm(
                "confirm",
                message=f"Are you sure you want to remove project '{project}'?",
                default=False,
            )
        ]

        try:
            confirm_answers = inquirer.prompt(confirm_questions)
            if confirm_answers is None or not confirm_answers["confirm"]:
                print("Removal cancelled.")
                return
        except KeyboardInterrupt:
            print("\nCancelled.")
            return

    # Remove the project
    if remove_project_from_list(config, project):
        save_config(config)
        print(f"Removed project: {project}")
        if is_active:
            print("Active project has been cleared.")
    else:
        print(f"Project '{project}' not found in available projects")
        print_available_projects(config)


# Create the command object
remove = click.command(name="remove")(
    click.argument("project", required=False)(click.pass_context(_remove))
)

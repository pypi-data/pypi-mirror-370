import click

from arm_cli.config import get_active_project_config
from arm_cli.system.setup_utils import (
    setup_data_directories,
    setup_docker_group,
    setup_shell,
    setup_xhost,
)


@click.group()
def system():
    """Manage the system this CLI is running on"""
    pass


@system.command()
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompts")
@click.pass_context
def setup(ctx, force):
    config = ctx.obj["config"]
    """Generic setup (will be refined later)"""

    # Load project configuration
    project_config = get_active_project_config(config)
    if project_config:
        print(f"Setting up system for project: {project_config.name}")
        if project_config.description:
            print(f"Description: {project_config.description}")
    else:
        print("No active project configuration found. Using default settings.")

    setup_xhost(force=force)

    setup_shell(force=force)

    # Setup docker group (may require sudo)
    if not setup_docker_group(force=force):
        print("Docker group setup was not completed.")
        print("You can run this setup again later with: arm-cli system setup")

    # Setup data directories (may require sudo)
    data_directory = "/DATA"  # Default fallback
    if project_config and project_config.data_directory:
        data_directory = project_config.data_directory

    if not setup_data_directories(force=force, data_directory=data_directory):
        print("Data directory setup was not completed.")
        print("You can run this setup again later with: arm-cli system setup")

    # Additional setup code can go here (e.g., starting containers,
    # attaching, etc.)
    pass

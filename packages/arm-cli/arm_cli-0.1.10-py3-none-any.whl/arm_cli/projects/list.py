import click

from arm_cli.config import get_available_projects, print_no_projects_message


def _list(ctx):
    """List all available projects"""
    config = ctx.obj["config"]
    available_projects = get_available_projects(config)

    if not available_projects:
        print_no_projects_message()
        return

    print("Available Projects:")
    for i, project in enumerate(available_projects, 1):
        active_indicator = " *" if project.path == config.active_project else ""
        print(f"  {i}. {project.name}{active_indicator}")
        print(f"     Path: {project.path}")
        print()


# Create the command object
list = click.command(name="ls")(click.pass_context(_list))

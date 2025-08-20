import click

# Import the modules and access the command objects
import arm_cli.projects.activate
import arm_cli.projects.info
import arm_cli.projects.init
import arm_cli.projects.list
import arm_cli.projects.remove

# Get the command objects
activate = arm_cli.projects.activate.activate
info = arm_cli.projects.info.info
init = arm_cli.projects.init.init
ls_cmd = arm_cli.projects.list.list
remove = arm_cli.projects.remove.remove


@click.group()
def projects():
    """Manage ARM projects"""
    pass


# Register all project commands
projects.add_command(init)
projects.add_command(activate)
projects.add_command(ls_cmd)
projects.add_command(info)
projects.add_command(remove)

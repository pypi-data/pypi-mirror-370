from beartype.claw import beartype_this_package

# Enable beartype on the package without polluting package __init__
beartype_this_package()

import click

from arm_cli import __version__
from arm_cli.config import load_config
from arm_cli.container.container import container
from arm_cli.projects.projects import projects
from arm_cli.self.self import self
from arm_cli.system.system import system


@click.version_option(version=__version__)
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
def cli(ctx):
    """Experimental CLI for deploying robotic applications"""
    # Load config and store in context
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config()


# Add command groups
cli.add_command(container)
cli.add_command(projects)
cli.add_command(self)
cli.add_command(system)

if __name__ == "__main__":
    cli()

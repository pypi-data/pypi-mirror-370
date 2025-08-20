import click
import pytest
from click.testing import CliRunner

from arm_cli.cli import cli


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner instance."""
    return CliRunner()


def get_all_commands(command):
    """Recursively retrieve all commands and subcommands."""
    commands = []
    if isinstance(command, click.Command):
        commands.append(command)
    if isinstance(command, click.Group):
        for subcommand in command.commands.values():
            commands.extend(get_all_commands(subcommand))
    return commands


@pytest.mark.parametrize("command", get_all_commands(cli))
def test_command_help(runner, command):
    """Test that each command and subcommand displays help."""
    result = runner.invoke(command, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from arm_cli.config import GlobalContext, ProjectConfig
from arm_cli.projects.projects import projects


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner instance."""
    return CliRunner()


@pytest.fixture
def temp_project_config():
    """Create a temporary project configuration."""
    config_data = {
        "name": "test-project",
        "description": "Test project for unit tests",
        "project_directory": "/tmp/test-project",
        "docker_compose_file": "docker-compose.yml",
        "data_directory": "/DATA",
    }
    return config_data


@pytest.fixture
def mock_config(temp_project_config):
    """Create a mock config with an active project."""
    config = GlobalContext(active_project="/tmp/test-project-config.json")
    return config


def test_projects_info_no_active_project(runner):
    """Test that info command handles no active project gracefully."""
    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = None

        result = runner.invoke(projects, ["info"], obj={"config": GlobalContext()})

        assert result.exit_code == 0
        assert "No active project configured" in result.output


def test_projects_info_with_project(runner, mock_config, temp_project_config):
    """Test that info command displays project information correctly."""
    project_config = ProjectConfig(**temp_project_config)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        result = runner.invoke(projects, ["info"], obj={"config": mock_config})

        assert result.exit_code == 0
        assert "Active Project: test-project" in result.output
        assert "Description: Test project for unit tests" in result.output
        assert "Project Directory: /tmp/test-project" in result.output
        assert "Docker Compose File: docker-compose.yml" in result.output
        assert "Data Directory: /DATA" in result.output


def test_projects_info_minimal_project(runner, mock_config):
    """Test that info command works with minimal project configuration."""
    project_config = ProjectConfig(name="minimal-project")

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        result = runner.invoke(projects, ["info"], obj={"config": mock_config})

        assert result.exit_code == 0
        assert "Active Project: minimal-project" in result.output


def test_projects_info_field_option(runner, mock_config, temp_project_config):
    """Test that info command with --field extracts specific field values."""
    project_config = ProjectConfig(**temp_project_config)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        # Test each field
        result = runner.invoke(projects, ["info", "--field", "name"], obj={"config": mock_config})
        assert result.exit_code == 0
        assert result.output.strip() == "test-project"

        result = runner.invoke(
            projects, ["info", "--field", "description"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "Test project for unit tests"

        result = runner.invoke(
            projects, ["info", "--field", "project_directory"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/tmp/test-project"

        result = runner.invoke(
            projects, ["info", "--field", "docker_compose_file"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "docker-compose.yml"

        result = runner.invoke(
            projects, ["info", "--field", "data_directory"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/DATA"


def test_projects_info_field_with_spaces(runner, mock_config, temp_project_config):
    """Test that info command handles field names with spaces correctly."""
    project_config = ProjectConfig(**temp_project_config)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        # Test field names with spaces (should be converted to underscores)
        result = runner.invoke(
            projects, ["info", "--field", "Project Directory"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/tmp/test-project"

        result = runner.invoke(
            projects, ["info", "--field", "Docker Compose File"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "docker-compose.yml"


def test_projects_info_field_case_insensitive(runner, mock_config, temp_project_config):
    """Test that info command handles case-insensitive field names."""
    project_config = ProjectConfig(**temp_project_config)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        # Test different case variations
        result = runner.invoke(
            projects, ["info", "--field", "PROJECT_DIRECTORY"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/tmp/test-project"

        result = runner.invoke(
            projects, ["info", "--field", "Project_Directory"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == "/tmp/test-project"


def test_projects_info_field_empty_value(runner, mock_config):
    """Test that info command handles empty field values correctly."""
    project_config = ProjectConfig(name="test", description=None, project_directory=None)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        result = runner.invoke(
            projects, ["info", "--field", "description"], obj={"config": mock_config}
        )
        assert result.exit_code == 0
        assert result.output.strip() == ""  # Empty string for None values


def test_projects_info_field_unknown_field(runner, mock_config, temp_project_config):
    """Test that info command handles unknown field names gracefully."""
    project_config = ProjectConfig(**temp_project_config)

    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = project_config

        result = runner.invoke(
            projects, ["info", "--field", "nonexistent_field"], obj={"config": mock_config}
        )
        assert result.exit_code == 0  # Click doesn't exit with error code for stderr output
        assert "Unknown field: nonexistent_field" in result.output
        assert "Available fields:" in result.output


def test_projects_info_field_no_active_project(runner):
    """Test that info command with --field handles no active project gracefully."""
    with patch("arm_cli.projects.info.get_active_project_config") as mock_get_config:
        mock_get_config.return_value = None

        result = runner.invoke(
            projects, ["info", "--field", "name"], obj={"config": GlobalContext()}
        )

        assert result.exit_code == 0
        assert "No active project configured" in result.output


def test_projects_help(runner):
    """Test that projects command shows help."""
    result = runner.invoke(projects, ["--help"])

    assert result.exit_code == 0
    assert "Manage ARM projects" in result.output
    assert "activate" in result.output
    assert "info" in result.output
    assert "init" in result.output
    assert "ls" in result.output
    assert "remove" in result.output

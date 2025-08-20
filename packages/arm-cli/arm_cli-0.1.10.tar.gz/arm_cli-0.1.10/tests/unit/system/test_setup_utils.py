from unittest import mock

import pytest

from arm_cli.system.setup_utils import is_line_in_file, setup_xhost


@pytest.fixture
def temp_file(tmp_path):
    """Creates a temporary file for testing file operations."""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("existing line\n")
    return test_file


def test_setup_xhost():
    """Test that setup_xhost runs the xhost command correctly."""
    with mock.patch("subprocess.run") as mock_run:
        # Mock the check to return False (not configured)
        mock_run.return_value.stdout = "some other output"
        setup_xhost(force=True)
        # Should be called twice: once to check, once to configure
        assert mock_run.call_count == 2
        # Check that the configuration call was made
        mock_run.assert_any_call(["xhost", "+local:docker"], check=True)


def test_is_line_in_file_exists(temp_file):
    """Test if the function correctly detects an existing line."""
    assert is_line_in_file("existing line", temp_file)


def test_is_line_in_file_not_exists(temp_file):
    """Test if the function correctly returns False for a missing line."""
    assert not is_line_in_file("missing line", temp_file)

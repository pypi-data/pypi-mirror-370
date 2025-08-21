# tests/test_fixtures.py
"""
Test the enhanced testing infrastructure and fixtures
"""

import pytest
from pathlib import Path

from fnb.config import RsyncTaskConfig, FnbConfig
from conftest import (
    assert_exit_code,
    assert_error_message_contains,
    assert_stdout_contains,
    SAMPLE_VALID_CONFIG,
)


def test_temp_dir_fixture(temp_dir):
    """Test temp_dir fixture creates a valid temporary directory"""
    assert isinstance(temp_dir, Path)
    assert temp_dir.exists()
    assert temp_dir.is_dir()

    # Test writing to the directory
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.read_text() == "test content"


def test_temp_config_files_fixture(temp_config_files):
    """Test temp_config_files fixture creates various config files"""
    assert "valid" in temp_config_files
    assert "invalid_toml" in temp_config_files
    assert "missing_fields" in temp_config_files
    assert "empty" in temp_config_files

    # Verify files exist
    for config_type, path in temp_config_files.items():
        assert path.exists(), f"{config_type} config file should exist"

    # Verify valid config contains expected content
    valid_content = temp_config_files["valid"].read_text()
    assert "[fetch.logs]" in valid_content
    assert "[backup.logs]" in valid_content


def test_sample_tasks_fixture(sample_tasks):
    """Test sample_tasks fixture provides various task configurations"""
    assert "local" in sample_tasks
    assert "remote" in sample_tasks
    assert "disabled" in sample_tasks

    # Verify task properties
    local_task = sample_tasks["local"]
    assert isinstance(local_task, RsyncTaskConfig)
    assert local_task.host == "none"
    assert local_task.enabled is True

    remote_task = sample_tasks["remote"]
    assert "remote.host" in remote_task.host
    assert remote_task.enabled is True

    disabled_task = sample_tasks["disabled"]
    assert disabled_task.enabled is False


def test_sample_config_fixture(sample_config):
    """Test sample_config fixture provides valid FnbConfig"""
    assert isinstance(sample_config, FnbConfig)
    assert "task1" in sample_config.fetch
    assert "task1" in sample_config.backup
    assert "disabled_task" in sample_config.fetch
    assert "disabled_task" in sample_config.backup


def test_mock_pexpect_fixture(mock_pexpect):
    """Test mock_pexpect fixture provides proper mock"""
    # Test that we can call the mock and get expected behavior
    child = mock_pexpect.spawn("test_command")
    assert child.expect.return_value == 0
    assert child.exitstatus == 0
    assert child.signalstatus is None


def test_mock_subprocess_fixture(mock_subprocess):
    """Test mock_subprocess fixture provides proper mock"""
    # Test that subprocess.run is mocked
    assert mock_subprocess.return_value.returncode == 0


def test_test_env_vars_fixture(test_env_vars):
    """Test test_env_vars fixture sets up environment variables"""
    import os

    assert "TEST_SOURCE" in test_env_vars
    assert "TEST_TARGET" in test_env_vars
    assert "FNB_PASSWORD_DEFAULT" in test_env_vars
    assert "FNB_PASSWORD_testhost" in test_env_vars

    # Verify environment variables are actually set
    assert os.environ.get("TEST_SOURCE") == "/test/source"
    assert os.environ.get("FNB_PASSWORD_DEFAULT") == "default_password"


def test_cli_runner_fixture(cli_runner):
    """Test cli_runner fixture provides CliRunner"""
    from typer.testing import CliRunner

    assert isinstance(cli_runner, CliRunner)


def test_utility_functions():
    """Test utility functions work correctly"""

    # Create mock result object
    class MockResult:
        def __init__(self, exit_code=0, output="", stdout=""):
            self.exit_code = exit_code
            self.output = output
            self.stdout = stdout
            self.exception = None

    # Test assert_exit_code
    result = MockResult(exit_code=0)
    assert_exit_code(result, 0)  # Should pass

    with pytest.raises(AssertionError):
        assert_exit_code(result, 1)  # Should fail

    # Test assert_error_message_contains
    result = MockResult(output="Error: File not found")
    assert_error_message_contains(result, "File not found")  # Should pass

    with pytest.raises(AssertionError):
        assert_error_message_contains(result, "Other error")  # Should fail

    # Test assert_stdout_contains
    result = MockResult(stdout="Command completed successfully")
    assert_stdout_contains(result, "completed")  # Should pass

    with pytest.raises(AssertionError):
        assert_stdout_contains(result, "failed")  # Should fail


def test_clean_env_fixture(clean_env):
    """Test clean_env fixture cleans environment variables properly"""
    import os

    # This test verifies that environment is restored after fixture
    # The fixture itself handles cleanup, so we just verify it doesn't break
    original_path = os.environ.get("PATH")
    assert original_path is not None

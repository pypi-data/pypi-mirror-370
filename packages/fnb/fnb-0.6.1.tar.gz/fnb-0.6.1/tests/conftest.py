# tests/conftest.py
import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from fnb.config import RsyncTaskConfig, FnbConfig


# === Test Data Constants ===
SAMPLE_VALID_CONFIG = """
[fetch.logs]
label = "logs"
summary = "Fetch logs from remote server"
host = "user@testhost"
source = "~/source/"
target = "./target/"
options = ["-av", "--delete"]
enabled = true

[backup.logs]
label = "logs"
summary = "Backup logs to external storage"
host = "none"
source = "./target/"
target = "./backup/"
options = ["-av"]
enabled = true

[fetch.data]
label = "data"
summary = "Fetch data from remote server"
host = "user@testhost"
source = "~/data/"
target = "./data/"
options = ["-av", "--delete"]
enabled = false
"""

SAMPLE_INVALID_TOML = """
[fetch.logs
label = "logs"
[[[invalid toml syntax
"""

SAMPLE_MISSING_FIELDS = """
[fetch.incomplete]
label = "incomplete"
# missing required fields: summary, host, source, target, options
"""


# === Temporary File Management ===
@pytest.fixture
def temp_dir():
    """Temporary directory for test files"""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_files(temp_dir):
    """Generate temporary config files for testing"""
    configs = {
        "valid": temp_dir / "valid.toml",
        "invalid_toml": temp_dir / "invalid.toml",
        "missing_fields": temp_dir / "incomplete.toml",
        "empty": temp_dir / "empty.toml",
    }

    # Create sample files
    configs["valid"].write_text(SAMPLE_VALID_CONFIG)
    configs["invalid_toml"].write_text(SAMPLE_INVALID_TOML)
    configs["missing_fields"].write_text(SAMPLE_MISSING_FIELDS)
    configs["empty"].write_text("")

    yield configs


@pytest.fixture
def config_file_path(tmp_path):
    """Create a temporary config file for testing"""
    config = """
[fetch.logs]
label = "logs"
summary = "Fetch logs from remote server"
host = "user@remote-host"
source = "~/path/to/source/"
target = "./local/backup/path/"
options = ["-auvz", "--delete", '--rsync-path="~/.local/bin/rsync"']
enabled = true

[backup.logs]
label = "logs"
summary = "Backup logs to external storage"
host = "none"
source = "./local/backup/path/"
target = "./external/backup/path/"
options = ["-auvz", "--delete"]
enabled = true

[fetch.data]
label = "data"
summary = "Fetch data from remote server"
host = "user@remote-host"
source = "~/path/to/source/"
target = "./local/backup/path/"
options = ["-auvz", "--delete", '--rsync-path="~/.local/bin/rsync"']
enabled = false
"""
    config_file = tmp_path / "test_config.toml"
    config_file.write_text(config)
    return config_file


# === Mock Fixtures ===
@pytest.fixture
def mock_pexpect():
    """Mock pexpect for SSH testing"""
    with patch("fnb.gear.pexpect") as mock:
        mock_child = Mock()
        mock_child.expect.return_value = 0
        mock_child.exitstatus = 0
        mock_child.signalstatus = None
        mock.spawn.return_value = mock_child
        yield mock


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for rsync testing"""
    with patch("fnb.gear.subprocess.run") as mock:
        mock.return_value.returncode = 0
        yield mock


@pytest.fixture
def mock_platformdirs():
    """Mock platformdirs for config path testing"""
    with patch("fnb.reader.platformdirs.user_config_path") as mock:
        yield mock


# === Environment Management ===
@pytest.fixture
def clean_env():
    """Clean environment variables for testing"""
    backup = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(backup)


@pytest.fixture
def test_env_vars():
    """Set up test environment variables"""
    test_vars = {
        "TEST_SOURCE": "/test/source",
        "TEST_TARGET": "/test/target",
        "FNB_PASSWORD_DEFAULT": "default_password",
        "FNB_PASSWORD_testhost": "host_specific_password",
    }
    os.environ.update(test_vars)
    yield test_vars
    for key in test_vars:
        os.environ.pop(key, None)


# === CLI Testing ===
@pytest.fixture
def cli_runner():
    """Typer CLI test runner"""
    return CliRunner()


# === Sample Objects ===
@pytest.fixture
def sample_tasks():
    """Sample RsyncTaskConfig objects"""
    return {
        "local": RsyncTaskConfig(
            label="test_local",
            summary="Test local task",
            host="none",
            source="/src/local",
            target="/dst/local",
            options=["-av", "--delete"],
            enabled=True,
        ),
        "remote": RsyncTaskConfig(
            label="test_remote",
            summary="Test remote task",
            host="user@remote.host",
            source="/src/remote",
            target="/dst/remote",
            options=["-av", "--delete", "--compress"],
            enabled=True,
        ),
        "disabled": RsyncTaskConfig(
            label="test_disabled",
            summary="Test disabled task",
            host="none",
            source="/src/disabled",
            target="/dst/disabled",
            options=["-av"],
            enabled=False,
        ),
    }


@pytest.fixture
def sample_config(sample_tasks):
    """Sample FnbConfig object"""
    return FnbConfig(
        fetch={
            "task1": sample_tasks["remote"],
            "disabled_task": sample_tasks["disabled"],
        },
        backup={
            "task1": sample_tasks["local"],
            "disabled_task": sample_tasks["disabled"],
        },
    )


# === Utility Functions ===
def assert_exit_code(result, expected_code=0):
    """Assert CLI command exit code"""
    assert result.exit_code == expected_code, (
        f"Expected exit code {expected_code}, got {result.exit_code}. Output: {result.output}"
    )


def assert_error_message_contains(result, message):
    """Assert error message contains specific text"""
    error_text = (
        result.output
        if result.output
        else str(result.exception)
        if result.exception
        else ""
    )
    assert message in error_text, (
        f"Expected '{message}' in error output, got: {error_text}"
    )


def assert_stdout_contains(result, message):
    """Assert stdout contains specific text"""
    assert message in result.stdout, (
        f"Expected '{message}' in stdout, got: {result.stdout}"
    )

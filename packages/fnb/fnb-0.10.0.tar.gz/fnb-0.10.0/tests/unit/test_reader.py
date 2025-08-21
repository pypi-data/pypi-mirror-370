# tests/test_reader.py
import os
import tomllib
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO
import platformdirs

import pytest

from fnb.config import FnbConfig
from fnb.reader import ConfigReader


def test_config_reader_with_explicit_path(config_file_path):
    """Test ConfigReader with an explicitly provided config path"""
    reader = ConfigReader(config_file_path)

    assert reader.config_path == config_file_path
    assert isinstance(reader.config, FnbConfig)
    assert len(reader.config.fetch) == 2
    assert reader.config.fetch["logs"].label == "logs"


def test_config_reader_env_expansion(tmp_path, monkeypatch):
    """Test that environment variables are expanded in config paths"""
    # Create a config with environment variables
    config_content = """
[fetch.test]
label = "test"
summary = "Test with env vars"
host = "user@host"
source = "$TEST_SOURCE_DIR/source/"
target = "$TEST_TARGET_DIR/target/"
options = ["-auvz"]
enabled = true
"""
    config_file = tmp_path / "env_config.toml"
    config_file.write_text(config_content)

    # Set environment variables
    monkeypatch.setenv("TEST_SOURCE_DIR", "/env/source")
    monkeypatch.setenv("TEST_TARGET_DIR", "/env/target")

    # Create reader and test expansion
    reader = ConfigReader(config_file)
    fetch_task = reader.config.fetch["test"]

    assert fetch_task.source == "/env/source/source/"
    assert fetch_task.target == "/env/target/target/"


# tests/test_reader.py (続き)
def test_config_reader_file_not_found():
    """Test ConfigReader behavior with non-existent config file"""
    with pytest.raises(FileNotFoundError) as excinfo:
        reader = ConfigReader(Path("non_existent_file.toml"))

    assert "Config file not found:" in str(excinfo.value)


def test_config_reader_default_path_search(tmp_path, monkeypatch):
    """Test ConfigReader default path search logic"""
    # Create fake config file at expected path
    fake_config_dir = tmp_path / ".config" / "fnb"
    fake_config_dir.mkdir(parents=True)
    config_file = fake_config_dir / "config.toml"

    config_content = """
[fetch.test]
label = "test"
summary = "Test task"
host = "user@host"
source = "~/source/"
target = "./target/"
options = ["-auvz"]
enabled = true
"""
    config_file.write_text(config_content)

    # Mock home directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: fake_config_dir
    )

    # Reader should find the config in the mocked home directory
    reader = ConfigReader()
    assert reader.config_path == config_file
    assert reader.config.fetch["test"].label == "test"


def test_config_reader_multiple_config_files_priority(tmp_path, monkeypatch):
    """Test ConfigReader priority when multiple config files exist"""
    # Create multiple config files in different locations
    # 1. Current directory - highest priority
    local_config = tmp_path / "fnb.toml"
    local_config.write_text("""
[fetch.local]
label = "local"
summary = "Local config"
host = "local@host"
source = "~/local/"
target = "./local/"
options = ["-auvz"]
enabled = true
""")

    # 2. Config directory - lower priority
    config_dir = tmp_path / ".config" / "fnb"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.toml"
    config_file.write_text("""
[fetch.config_dir]
label = "config_dir"
summary = "Config dir"
host = "config@host"
source = "~/config/"
target = "./config/"
options = ["-auvz"]
enabled = true
""")

    # Mock working directory and config path
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(platformdirs, "user_config_path", lambda app_name: config_dir)

    # Should pick local config (highest priority)
    reader = ConfigReader()
    assert reader.config_path.resolve() == local_config.resolve()
    assert "local" in reader.config.fetch
    assert "config_dir" not in reader.config.fetch


def test_config_reader_config_directory_multiple_toml_files(tmp_path, monkeypatch):
    """Test ConfigReader handling multiple TOML files in config/ directory"""
    # Create config/ directory with multiple TOML files
    config_subdir = tmp_path / "config"
    config_subdir.mkdir()

    # Create multiple TOML files (should be sorted)
    config1 = config_subdir / "a_first.toml"
    config1.write_text("""
[fetch.first]
label = "first"
summary = "First config"
host = "first@host"
source = "~/first/"
target = "./first/"
options = ["-auvz"]
enabled = true
""")

    config2 = config_subdir / "z_last.toml"
    config2.write_text("""
[fetch.last]
label = "last"
summary = "Last config"
host = "last@host"
source = "~/last/"
target = "./last/"
options = ["-auvz"]
enabled = true
""")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: tmp_path / ".config" / "fnb"
    )

    # Should pick first file alphabetically
    reader = ConfigReader()
    assert reader.config_path.resolve() == config1.resolve()
    assert reader.config.fetch["first"].label == "first"


def test_config_reader_no_config_file_found(tmp_path, monkeypatch):
    """Test ConfigReader behavior when no config file is found anywhere"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: tmp_path / ".config" / "fnb"
    )

    with pytest.raises(FileNotFoundError) as excinfo:
        ConfigReader()

    error_msg = str(excinfo.value)
    assert "No config file found in expected locations:" in error_msg
    assert "fnb.toml" in error_msg
    assert "config.toml" in error_msg
    assert "Run 'fnb init' to create one" in error_msg


def test_config_reader_invalid_toml_syntax(tmp_path, monkeypatch):
    """Test ConfigReader behavior with invalid TOML syntax"""
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("""
[fetch.test
label = "test"  # Missing closing bracket
invalid syntax here
""")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: tmp_path / ".config" / "fnb"
    )

    with pytest.raises(ValueError) as excinfo:
        ConfigReader(invalid_toml)

    error_msg = str(excinfo.value)
    assert "Invalid TOML in config file" in error_msg
    assert str(invalid_toml) in error_msg


def test_config_reader_invalid_pydantic_validation(tmp_path, monkeypatch):
    """Test ConfigReader behavior with invalid Pydantic validation"""
    invalid_config = tmp_path / "invalid_schema.toml"
    invalid_config.write_text("""
[fetch.test]
label = "test"
summary = "Test task"
host = "user@host"
# Missing required 'source' and 'target' fields
options = ["-auvz"]
enabled = true
""")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: tmp_path / ".config" / "fnb"
    )

    with pytest.raises(ValueError) as excinfo:
        ConfigReader(invalid_config)

    error_msg = str(excinfo.value)
    assert "Invalid config schema" in error_msg
    assert str(invalid_config) in error_msg


def test_config_reader_empty_file(tmp_path, monkeypatch):
    """Test ConfigReader behavior with empty TOML file"""
    empty_file = tmp_path / "empty.toml"
    empty_file.write_text("")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        platformdirs, "user_config_path", lambda app_name: tmp_path / ".config" / "fnb"
    )

    # Empty TOML should be valid but result in empty config
    reader = ConfigReader(empty_file)
    assert len(reader.config.fetch) == 0
    assert len(reader.config.backup) == 0


@pytest.mark.skipif(
    os.getuid() == 0, reason="Root user can read files regardless of permissions"
)
def test_config_reader_file_permission_error(tmp_path, monkeypatch):
    """Test ConfigReader behavior with file permission errors"""
    config_file = tmp_path / "protected.toml"
    config_file.write_text("""
[fetch.test]
label = "test"
summary = "Test task"
host = "user@host"
source = "~/source/"
target = "./target/"
options = ["-auvz"]
enabled = true
""")

    # Make file unreadable (simulate permission error)
    config_file.chmod(0o000)

    try:
        with pytest.raises(ValueError) as excinfo:
            ConfigReader(config_file)

        error_msg = str(excinfo.value)
        assert "Error reading config file" in error_msg
        assert str(config_file) in error_msg
    finally:
        # Restore permissions for cleanup
        config_file.chmod(0o644)


def test_config_reader_env_expansion_nested_vars(tmp_path, monkeypatch):
    """Test environment variable expansion with nested variables"""
    config_content = """
[fetch.nested]
label = "nested"
summary = "Nested env vars test"
host = "user@host"
source = "$BASE_DIR/$SUB_DIR/source/"
target = "$HOME/$PROJECT/target/"
options = ["-auvz"]
enabled = true

[backup.nested_backup]
label = "nested_backup"
summary = "Nested backup vars"
host = "backup@host"
source = "$HOME/$PROJECT/data/"
target = "$BACKUP_ROOT/$DATE/backup/"
options = ["-auvz", "--exclude=$TEMP_DIR/*"]
enabled = true
"""
    config_file = tmp_path / "nested_env.toml"
    config_file.write_text(config_content)

    # Set nested environment variables
    monkeypatch.setenv("BASE_DIR", "/base")
    monkeypatch.setenv("SUB_DIR", "sub")
    monkeypatch.setenv("HOME", "/home/user")
    monkeypatch.setenv("PROJECT", "myproject")
    monkeypatch.setenv("BACKUP_ROOT", "/backup")
    monkeypatch.setenv("DATE", "2024-01-01")
    monkeypatch.setenv("TEMP_DIR", "/tmp")

    reader = ConfigReader(config_file)

    # Test fetch task
    fetch_task = reader.config.fetch["nested"]
    assert fetch_task.source == "/base/sub/source/"
    assert fetch_task.target == "/home/user/myproject/target/"

    # Test backup task
    backup_task = reader.config.backup["nested_backup"]
    assert backup_task.source == "/home/user/myproject/data/"
    assert backup_task.target == "/backup/2024-01-01/backup/"
    assert "--exclude=/tmp/*" in backup_task.options


def test_config_reader_env_expansion_missing_vars(tmp_path, monkeypatch):
    """Test environment variable expansion with missing variables"""
    config_content = """
[fetch.missing_vars]
label = "missing_vars"
summary = "Missing env vars test"
host = "user@host"
source = "$EXISTING_VAR/source/"
target = "$MISSING_VAR/target/"
options = ["-auvz", "--backup-dir=$ANOTHER_MISSING"]
enabled = true
"""
    config_file = tmp_path / "missing_env.toml"
    config_file.write_text(config_content)

    # Set only one variable
    monkeypatch.setenv("EXISTING_VAR", "/existing")
    # MISSING_VAR and ANOTHER_MISSING are intentionally not set

    reader = ConfigReader(config_file)
    fetch_task = reader.config.fetch["missing_vars"]

    # Should expand existing var and leave missing ones as-is
    assert fetch_task.source == "/existing/source/"
    assert fetch_task.target == "$MISSING_VAR/target/"
    assert "--backup-dir=$ANOTHER_MISSING" in fetch_task.options


def test_config_reader_env_expansion_special_characters(tmp_path, monkeypatch):
    """Test environment variable expansion with special characters"""
    config_content = """
[fetch.special_chars]
label = "special_chars"
summary = "Special characters test"
host = "user@host"
source = "$SPECIAL_PATH/source/"
target = "$UNICODE_PATH/target/"
options = ["-auvz", "--log-file=$LOG_PATH"]
enabled = true
"""
    config_file = tmp_path / "special_chars.toml"
    config_file.write_text(config_content)

    # Set variables with special characters
    monkeypatch.setenv("SPECIAL_PATH", "/path with spaces/and-dashes")
    monkeypatch.setenv("UNICODE_PATH", "/パス/with/日本語")
    monkeypatch.setenv("LOG_PATH", "/var/log/app-name_v1.0.log")

    reader = ConfigReader(config_file)
    fetch_task = reader.config.fetch["special_chars"]

    assert fetch_task.source == "/path with spaces/and-dashes/source/"
    assert fetch_task.target == "/パス/with/日本語/target/"
    assert "--log-file=/var/log/app-name_v1.0.log" in fetch_task.options


def test_config_reader_env_expansion_list_and_dict_structures(tmp_path, monkeypatch):
    """Test environment variable expansion in nested list and dict structures"""
    config_content = """
[fetch.complex_structure]
label = "complex_structure"
summary = "Complex structure with env vars"
host = "user@host"
source = "$SRC_BASE/data/"
target = "$TGT_BASE/backup/"
options = [
    "-auvz",
    "--exclude=$EXCLUDE_DIR/*",
    "--backup-dir=$BACKUP_DIR",
    "--log-file=$LOG_BASE/sync.log"
]
enabled = true
"""
    config_file = tmp_path / "complex_env.toml"
    config_file.write_text(config_content)

    # Set environment variables
    monkeypatch.setenv("SRC_BASE", "/source/root")
    monkeypatch.setenv("TGT_BASE", "/target/root")
    monkeypatch.setenv("EXCLUDE_DIR", "/temp")
    monkeypatch.setenv("BACKUP_DIR", "/backups")
    monkeypatch.setenv("LOG_BASE", "/var/log")

    reader = ConfigReader(config_file)
    fetch_task = reader.config.fetch["complex_structure"]

    assert fetch_task.source == "/source/root/data/"
    assert fetch_task.target == "/target/root/backup/"
    assert "--exclude=/temp/*" in fetch_task.options
    assert "--backup-dir=/backups" in fetch_task.options
    assert "--log-file=/var/log/sync.log" in fetch_task.options


def test_config_reader_print_status_basic_output(tmp_path, monkeypatch, capsys):
    """Test ConfigReader print_status basic output functionality"""
    config_content = """
[fetch.test_fetch]
label = "test_fetch"
summary = "Test fetch task"
host = "user@host"
source = "~/source/"
target = "/local/target/"
options = ["-auvz"]
enabled = true

[backup.test_backup]
label = "test_backup"
summary = "Test backup task"
host = "backup@host"
source = "/local/data/"
target = "/backup/target/"
options = ["-auvz"]
enabled = true
"""
    config_file = tmp_path / "status_test.toml"
    config_file.write_text(config_content)

    reader = ConfigReader(config_file)

    # Test print_status without directory checking
    reader.print_status(check_dirs=False)
    captured = capsys.readouterr()

    # Check that config file path is displayed
    assert str(config_file) in captured.out
    assert "📄 Config file:" in captured.out

    # Check that fetch tasks are displayed
    assert "📦 Fetch Tasks (remote → local):" in captured.out
    assert "✅ test_fetch:" in captured.out
    assert "user@host:~/source/ → /local/target/" in captured.out

    # Check that backup tasks are displayed
    assert "💾 Backup Tasks (local → external):" in captured.out
    assert "✅ test_backup:" in captured.out
    assert "backup@host:/local/data/ → /backup/target/" in captured.out


def test_config_reader_print_status_no_enabled_tasks(tmp_path, monkeypatch, capsys):
    """Test ConfigReader print_status with no enabled tasks"""
    config_content = """
[fetch.disabled_fetch]
label = "disabled_fetch"
summary = "Disabled fetch task"
host = "user@host"
source = "~/source/"
target = "/local/target/"
options = ["-auvz"]
enabled = false

[backup.disabled_backup]
label = "disabled_backup"
summary = "Disabled backup task"
host = "backup@host"
source = "/local/data/"
target = "/backup/target/"
options = ["-auvz"]
enabled = false
"""
    config_file = tmp_path / "no_enabled.toml"
    config_file.write_text(config_content)

    reader = ConfigReader(config_file)
    reader.print_status(check_dirs=False)
    captured = capsys.readouterr()

    # Should show "No enabled tasks" messages
    assert "❌ No enabled fetch tasks" in captured.out
    assert "❌ No enabled backup tasks" in captured.out


@patch("fnb.reader.verify_directory")
def test_config_reader_print_status_with_directory_checking(
    mock_verify_dir, tmp_path, capsys
):
    """Test ConfigReader print_status with directory existence checking"""
    config_content = """
[fetch.local_target]
label = "local_target"
summary = "Local target task"
host = "user@host"
source = "~/source/"
target = "/local/existing/"
options = ["-auvz"]
enabled = true

[fetch.remote_target]
label = "remote_target"
summary = "Remote target task"
host = "user@host"
source = "~/source/"
target = "remote@host:/remote/target/"
options = ["-auvz"]
enabled = true

[backup.local_target_backup]
label = "local_target_backup"
summary = "Local backup task"
host = "backup@host"
source = "/local/data/"
target = "/backup/missing/"
options = ["-auvz"]
enabled = true
"""
    config_file = tmp_path / "dir_check.toml"
    config_file.write_text(config_content)

    # Mock verify_directory to simulate different scenarios
    def mock_verify_side_effect(path):
        if path == "/local/existing/":
            return Path("/local/existing/")
        elif path == "/backup/missing/":
            raise FileNotFoundError(f"Directory not found: {path}")
        else:
            return Path(path)

    mock_verify_dir.side_effect = mock_verify_side_effect

    reader = ConfigReader(config_file)
    reader.print_status(check_dirs=True)
    captured = capsys.readouterr()

    # Should check local paths but skip remote paths
    assert "📁 Target for local_target exists: /local/existing" in captured.out
    assert "⚠️  Target for local_target_backup does not exist:" in captured.out
    # Remote target should be displayed but not checked (no directory check icons for remote paths)
    assert "remote@host:/remote/target/" in captured.out
    assert "Target for remote_target" not in captured.out


@patch("fnb.reader.verify_directory")
def test_config_reader_check_directory_scenarios(mock_verify_dir, tmp_path, capsys):
    """Test ConfigReader _check_directory method with various scenarios"""
    config_content = """
[fetch.test]
label = "test"
summary = "Test task"
host = "user@host"
source = "~/source/"
target = "/test/target/"
options = ["-auvz"]
enabled = true
"""
    config_file = tmp_path / "check_dir.toml"
    config_file.write_text(config_content)

    reader = ConfigReader(config_file)

    # Test 1: Directory exists
    mock_verify_dir.return_value = Path("/test/target/")
    reader._check_directory("/test/target/", "Test Directory")
    captured = capsys.readouterr()
    assert "📁 Test Directory exists: /test/target" in captured.out

    # Test 2: Directory not found
    mock_verify_dir.side_effect = FileNotFoundError("Directory not found")
    reader._check_directory("/missing/dir/", "Missing Directory")
    captured = capsys.readouterr()
    assert "⚠️  Missing Directory does not exist:" in captured.out

    # Test 3: Other ValueError (e.g., permission issue)
    mock_verify_dir.side_effect = ValueError("Permission denied")
    reader._check_directory("/protected/dir/", "Protected Directory")
    captured = capsys.readouterr()
    assert "⚠️  Protected Directory issue: Permission denied" in captured.out


def test_config_reader_print_status_empty_config(tmp_path, capsys):
    """Test ConfigReader print_status with empty config (no tasks)"""
    empty_config = tmp_path / "empty_status.toml"
    empty_config.write_text("")  # Completely empty config

    reader = ConfigReader(empty_config)
    reader.print_status(check_dirs=False)
    captured = capsys.readouterr()

    # Should show config file and empty task lists
    assert str(empty_config) in captured.out
    assert "📄 Config file:" in captured.out
    assert "❌ No enabled fetch tasks" in captured.out
    assert "❌ No enabled backup tasks" in captured.out

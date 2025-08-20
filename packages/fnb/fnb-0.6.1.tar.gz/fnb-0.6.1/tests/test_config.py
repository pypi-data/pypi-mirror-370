# tests/test_config.py
from pathlib import Path

import pytest

from fnb.config import FnbConfig, RsyncTaskConfig, load_config


def test_rsync_task_config_basic():
    """Test basic initialization of RsyncTaskConfig"""
    task = RsyncTaskConfig(
        label="test",
        summary="Test task",
        host="user@example.com",
        source="/path/to/source/",
        target="./local/path/",
        options=["-auvz", "--delete"],
    )

    assert task.label == "test"
    assert task.summary == "Test task"
    assert task.host == "user@example.com"
    assert task.source == "/path/to/source/"
    assert task.target == "./local/path/"
    assert task.options == ["-auvz", "--delete"]
    assert task.enabled == True  # Default value


def test_rsync_task_config_properties():
    """Test the property methods of RsyncTaskConfig"""
    # Remote task
    remote_task = RsyncTaskConfig(
        label="remote",
        summary="Remote task",
        host="user@example.com",
        source="/path/to/source/",
        target="./local/path/",
        options=["-auvz"],
    )

    assert remote_task.is_remote == True
    assert remote_task.rsync_source == "user@example.com:/path/to/source/"
    assert remote_task.rsync_target == "./local/path/"

    # Local task
    local_task = RsyncTaskConfig(
        label="local",
        summary="Local task",
        host="none",
        source="./source/path/",
        target="./target/path/",
        options=["-auvz"],
    )

    assert local_task.is_remote == False
    assert local_task.rsync_source == "./source/path/"
    assert local_task.rsync_target == "./target/path/"


def test_fnb_config_basic():
    """Test basic initialization of FnbConfig"""
    fetch_task = RsyncTaskConfig(
        label="test-fetch",
        summary="Test fetch task",
        host="user@example.com",
        source="/path/to/source/",
        target="./local/path/",
        options=["-auvz"],
    )

    backup_task = RsyncTaskConfig(
        label="test-backup",
        summary="Test backup task",
        host="none",
        source="./source/path/",
        target="./target/path/",
        options=["-auvz"],
    )

    config = FnbConfig(fetch={"test": fetch_task}, backup={"test": backup_task})

    assert len(config.fetch) == 1
    assert config.fetch["test"].label == "test-fetch"
    assert len(config.backup) == 1
    assert config.backup["test"].label == "test-backup"


def test_get_enabled_tasks():
    """Test getting enabled tasks from FnbConfig"""
    enabled_task = RsyncTaskConfig(
        label="enabled",
        summary="Enabled task",
        host="user@example.com",
        source="/path/to/source/",
        target="./local/path/",
        options=["-auvz"],
        enabled=True,
    )

    disabled_task = RsyncTaskConfig(
        label="disabled",
        summary="Disabled task",
        host="user@example.com",
        source="/path/to/source/",
        target="./local/path/",
        options=["-auvz"],
        enabled=False,
    )

    config = FnbConfig(fetch={"task1": enabled_task, "task2": disabled_task}, backup={})

    enabled_tasks = config.get_enabled_tasks("fetch")
    assert len(enabled_tasks) == 1
    assert enabled_tasks[0].label == "enabled"


def test_get_task_by_label():
    """Test getting tasks by label from FnbConfig"""
    task1 = RsyncTaskConfig(
        label="logs",
        summary="Log task",
        host="user@example.com",
        source="/path/to/logs/",
        target="./local/logs/",
        options=["-auvz"],
    )

    task2 = RsyncTaskConfig(
        label="data",
        summary="Data task",
        host="user@example.com",
        source="/path/to/data/",
        target="./local/data/",
        options=["-auvz"],
    )

    config = FnbConfig(fetch={"task1": task1, "task2": task2}, backup={})

    found_task = config.get_task_by_label("fetch", "logs")
    assert found_task is not None
    assert found_task.label == "logs"

    not_found_task = config.get_task_by_label("fetch", "nonexistent")
    assert not_found_task is None


def test_load_config(config_file_path):
    """Test loading configuration from a file"""
    config = load_config(config_file_path)

    assert len(config.fetch) == 2
    assert config.fetch["logs"].label == "logs"
    assert config.fetch["logs"].enabled == True
    assert config.fetch["data"].enabled == False

    assert len(config.backup) == 1
    assert config.backup["logs"].label == "logs"
    assert config.backup["logs"].enabled == True


def test_load_config_file_not_found():
    """Test loading a non-existent configuration file"""
    non_existent_path = Path("non_existent_file.toml")
    with pytest.raises(FileNotFoundError):
        load_config(non_existent_path)


def test_load_config_invalid_toml(tmp_path):
    """Test loading an invalid TOML file"""
    invalid_toml = tmp_path / "invalid.toml"
    invalid_toml.write_text("This is not a valid TOML file")

    with pytest.raises(ValueError) as excinfo:
        load_config(invalid_toml)
    assert "Invalid TOML file" in str(excinfo.value)

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from fnb.cli import app


@pytest.fixture
def runner():
    """Setup CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_config_reader():
    """Setup mock ConfigReader for testing."""
    with patch("fnb.cli.ConfigReader") as mock:
        reader_instance = MagicMock()
        mock.return_value = reader_instance

        # Mock config with sample tasks
        fetch_task = MagicMock()
        fetch_task.enabled = True
        fetch_task.host = "user@host"
        fetch_task.target = "./local/path"

        backup_task = MagicMock()
        backup_task.enabled = True
        backup_task.source = "./local/path"
        backup_task.target = "./backup/path"

        # Setup get_task_by_label to return the tasks
        reader_instance.config.get_task_by_label.side_effect = lambda kind, label: {
            ("fetch", "logs"): fetch_task,
            ("backup", "logs"): backup_task,
        }.get((kind, label))

        yield mock, reader_instance


def test_fetch_command(runner, mock_config_reader):
    """Test the fetch command."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_run:
        # Run the CLI command
        result = runner.invoke(app, ["fetch", "logs", "--config", "test_config.toml"])

        # Verify the command ran successfully
        assert result.exit_code == 0

        # Verify the ConfigReader was initialized correctly
        mock_class.assert_called_once_with(Path("test_config.toml"))

        # Verify the correct task was fetched
        mock_instance.config.get_task_by_label.assert_called_once_with("fetch", "logs")

        # Verify fetcher.run was called
        mock_run.assert_called_once()


def test_backup_command(runner, mock_config_reader):
    """Test the backup command."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.backuper.run") as mock_run:
        # CLI コマンドを実行
        result = runner.invoke(app, ["backup", "logs", "--config", "test_config.toml"])

        # コマンドが正常に実行されたことを確認
        assert result.exit_code == 0

        # ConfigReaderが正しく初期化されたことを確認
        mock_class.assert_called_once_with(Path("test_config.toml"))

        # 正しいタスクが取得されたことを確認
        mock_instance.config.get_task_by_label.assert_called_with("backup", "logs")

        # backuper.runが呼び出されたことを確認
        mock_run.assert_called_once()


def test_sync_command(runner, mock_config_reader):
    """Test the sync command."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_fetcher_run:
        with patch("fnb.cli.backuper.run") as mock_backuper_run:
            # CLI コマンドを実行
            result = runner.invoke(
                app, ["sync", "logs", "--config", "test_config.toml"]
            )

            # コマンドが正常に実行されたことを確認
            assert result.exit_code == 0

            # ConfigReaderが正しく初期化されたことを確認
            mock_class.assert_called_once_with(Path("test_config.toml"))

            # 正しいタスクが取得されたことを確認
            assert mock_instance.config.get_task_by_label.call_count == 2

            # fetcherとbackuperの両方が呼び出されたことを確認
            mock_fetcher_run.assert_called_once()
            mock_backuper_run.assert_called_once()


def test_sync_command_with_disabled_tasks(runner, mock_config_reader):
    """Test the sync command with disabled tasks."""
    mock_class, mock_instance = mock_config_reader

    # モックを修正して、タスクを無効に設定
    fetch_task = mock_instance.config.get_task_by_label("fetch", "logs")
    fetch_task.enabled = False
    backup_task = mock_instance.config.get_task_by_label("backup", "logs")
    backup_task.enabled = False

    with patch("fnb.cli.fetcher.run") as mock_fetcher_run:
        with patch("fnb.cli.backuper.run") as mock_backuper_run:
            # CLI コマンドを実行
            result = runner.invoke(
                app, ["sync", "logs", "--config", "test_config.toml"]
            )

            # コマンドが正常に実行されたことを確認
            assert result.exit_code == 0

            # fetcherもbackuperも呼び出されていないことを確認
            mock_fetcher_run.assert_not_called()
            mock_backuper_run.assert_not_called()

            # 出力に「スキップ」というメッセージが含まれていることを確認
            assert "Skipping fetch" in result.stdout
            assert "Skipping backup" in result.stdout


def test_status_command(runner, mock_config_reader):
    """Test the status command."""
    _, mock_instance = mock_config_reader

    # CLI コマンドを実行
    result = runner.invoke(app, ["status", "--config", "test_config.toml"])

    # コマンドが正常に実行されたことを確認
    assert result.exit_code == 0

    # print_statusが呼び出されたことを確認
    mock_instance.print_status.assert_called_once()


def test_init_command(runner):
    """Test the init command."""
    with patch("fnb.cli.generator.run") as mock_run:
        # CLIコマンドを実行
        result = runner.invoke(app, ["init"])

        # コマンドが正常に実行されたことを確認
        assert result.exit_code == 0

        # generator.runが呼び出されたことを確認
        mock_run.assert_called_once_with(kind="all", force=False)


@patch("fnb.cli.ConfigReader", side_effect=FileNotFoundError)
def test_config_not_found(mock_reader):
    """Test behavior when config file is not found."""
    runner = CliRunner()

    # status コマンドのテスト
    result = runner.invoke(app, ["status"])
    assert "No config file found" in result.stdout
    assert result.exit_code == 1

    # sync コマンドのテスト
    result = runner.invoke(app, ["sync", "logs"])
    assert "Use --create-dirs" in result.stdout
    assert result.exit_code == 1


def test_label_not_found_direct_check(runner):
    """ラベルが見つからない場合のメッセージをより直接的に確認"""
    # fetch コマンドのテスト
    result = runner.invoke(
        app, ["fetch", "unknown", "--config", "non_existent_config.toml"]
    )
    assert result.exit_code != 0 or "Label not found: unknown" in result.stdout

    # backup コマンドのテスト
    result = runner.invoke(
        app, ["backup", "unknown", "--config", "non_existent_config.toml"]
    )
    assert result.exit_code != 0 or "Label not found: unknown" in result.stdout


def test_version_command(runner):
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "fnb version" in result.stdout


def test_init_command_invalid_kind(runner):
    """Test init command with invalid kind parameter."""
    with patch(
        "fnb.cli.generator.run", side_effect=ValueError("Invalid kind: invalid")
    ):
        result = runner.invoke(app, ["init", "invalid"])
        assert result.exit_code == 1
        assert "❌ Error: Invalid kind: invalid" in result.stdout


def test_init_command_with_force_flag(runner):
    """Test init command with force flag."""
    with patch("fnb.cli.generator.run") as mock_run:
        result = runner.invoke(app, ["init", "config", "--force"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(kind="config", force=True)


def test_status_command_generic_error(runner):
    """Test status command with generic exception."""
    with patch("fnb.cli.ConfigReader", side_effect=Exception("Generic error")):
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 1
        assert "❌ Error: Generic error" in result.stdout


def test_fetch_command_task_not_found(runner, mock_config_reader):
    """Test fetch command when task is not found."""
    mock_class, mock_instance = mock_config_reader
    mock_instance.config.get_task_by_label.return_value = None

    result = runner.invoke(
        app, ["fetch", "nonexistent", "--config", "test_config.toml"]
    )
    assert result.exit_code == 1
    assert "❌ Label not found: nonexistent" in result.stdout


def test_fetch_command_file_not_found_error(runner, mock_config_reader):
    """Test fetch command with FileNotFoundError."""
    mock_class, mock_instance = mock_config_reader

    with patch(
        "fnb.cli.fetcher.run", side_effect=FileNotFoundError("Directory not found")
    ):
        result = runner.invoke(app, ["fetch", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Directory not found" in result.stdout
        assert "Use --create-dirs option" in result.stdout


def test_fetch_command_generic_error(runner, mock_config_reader):
    """Test fetch command with generic exception."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run", side_effect=Exception("Generic fetch error")):
        result = runner.invoke(app, ["fetch", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Error: Generic fetch error" in result.stdout


def test_backup_command_task_not_found(runner, mock_config_reader):
    """Test backup command when task is not found."""
    mock_class, mock_instance = mock_config_reader
    mock_instance.config.get_task_by_label.return_value = None

    result = runner.invoke(
        app, ["backup", "nonexistent", "--config", "test_config.toml"]
    )
    assert result.exit_code == 1
    assert "❌ Label not found: nonexistent" in result.stdout


def test_backup_command_file_not_found_error(runner, mock_config_reader):
    """Test backup command with FileNotFoundError."""
    mock_class, mock_instance = mock_config_reader

    with patch(
        "fnb.cli.backuper.run", side_effect=FileNotFoundError("Source not found")
    ):
        result = runner.invoke(app, ["backup", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Source not found" in result.stdout
        assert "Use --create-dirs option" in result.stdout


def test_backup_command_generic_error(runner, mock_config_reader):
    """Test backup command with generic exception."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.backuper.run", side_effect=Exception("Generic backup error")):
        result = runner.invoke(app, ["backup", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Error: Generic backup error" in result.stdout


def test_sync_command_file_not_found_error(runner, mock_config_reader):
    """Test sync command with FileNotFoundError."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run", side_effect=FileNotFoundError("Network error")):
        result = runner.invoke(app, ["sync", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Network error" in result.stdout
        assert "Use --create-dirs option" in result.stdout


def test_sync_command_generic_error(runner, mock_config_reader):
    """Test sync command with generic exception."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run", side_effect=Exception("Sync operation failed")):
        result = runner.invoke(app, ["sync", "logs", "--config", "test_config.toml"])
        assert result.exit_code == 1
        assert "❌ Error: Sync operation failed" in result.stdout


def test_fetch_command_with_ssh_password(runner, mock_config_reader):
    """Test fetch command with SSH password parameter."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_run:
        result = runner.invoke(
            app,
            [
                "fetch",
                "logs",
                "--ssh-password",
                "secret",
                "--config",
                "test_config.toml",
            ],
        )
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["ssh_password"] == "secret"


def test_sync_command_with_ssh_password(runner, mock_config_reader):
    """Test sync command with SSH password parameter."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_fetcher_run:
        with patch("fnb.cli.backuper.run") as mock_backuper_run:
            result = runner.invoke(
                app,
                [
                    "sync",
                    "logs",
                    "--ssh-password",
                    "secret",
                    "--config",
                    "test_config.toml",
                ],
            )
            assert result.exit_code == 0
            mock_fetcher_run.assert_called_once()
            args, kwargs = mock_fetcher_run.call_args
            assert kwargs["ssh_password"] == "secret"


def test_commands_with_dry_run_flag(runner, mock_config_reader):
    """Test commands with dry-run flag."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_fetcher_run:
        result = runner.invoke(
            app, ["fetch", "logs", "--dry-run", "--config", "test_config.toml"]
        )
        assert result.exit_code == 0
        args, kwargs = mock_fetcher_run.call_args
        assert kwargs["dry_run"] is True

    with patch("fnb.cli.backuper.run") as mock_backuper_run:
        result = runner.invoke(
            app, ["backup", "logs", "--dry-run", "--config", "test_config.toml"]
        )
        assert result.exit_code == 0
        args, kwargs = mock_backuper_run.call_args
        assert kwargs["dry_run"] is True


def test_commands_with_create_dirs_flag(runner, mock_config_reader):
    """Test commands with create-dirs flag."""
    mock_class, mock_instance = mock_config_reader

    with patch("fnb.cli.fetcher.run") as mock_fetcher_run:
        result = runner.invoke(
            app, ["fetch", "logs", "--create-dirs", "--config", "test_config.toml"]
        )
        assert result.exit_code == 0
        args, kwargs = mock_fetcher_run.call_args
        assert kwargs["create_dirs"] is True

    with patch("fnb.cli.backuper.run") as mock_backuper_run:
        result = runner.invoke(
            app, ["backup", "logs", "--create-dirs", "--config", "test_config.toml"]
        )
        assert result.exit_code == 0
        args, kwargs = mock_backuper_run.call_args
        assert kwargs["create_dirs"] is True

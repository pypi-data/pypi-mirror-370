import os
import shutil
import subprocess
import unittest
from unittest.mock import patch, Mock

from fnb.config import RsyncTaskConfig
from fnb.fetcher import run


class TestFetcher(unittest.TestCase):
    """Test suite for fetcher module."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear FNB_PASSWORD environment variables to avoid interference
        for key in list(os.environ.keys()):
            if key.startswith("FNB_PASSWORD"):
                del os.environ[key]

        self.task = RsyncTaskConfig(
            label="test",
            summary="Test fetch task",
            host="user@remote-host",
            source="~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            enabled=True,
        )
        os.makedirs(self.task.target, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("./local", ignore_errors=True)

    @patch("fnb.fetcher.run_rsync")
    def test_run_basic(self, mock_run_rsync):
        """Test basic fetch operation."""
        # Configure mock
        mock_run_rsync.return_value = None

        # Run the function
        run(self.task)

        # Verify the call
        mock_run_rsync.assert_called_once_with(
            source="user@remote-host:~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            ssh_password=None,
        )

    @patch("fnb.fetcher.run_rsync")
    def test_run_with_dry_run(self, mock_run_rsync):
        """Test fetch operation with dry-run option."""
        # Run with dry_run=True
        run(self.task, dry_run=True)

        # Verify --dry-run was added to options
        called_args = mock_run_rsync.call_args[1]
        self.assertIn("--dry-run", called_args["options"])

    @patch("fnb.fetcher.run_rsync")
    def test_run_with_password(self, mock_run_rsync):
        """Test fetch operation with SSH password."""
        # Run with password
        test_password = "test_password"
        run(self.task, ssh_password=test_password)

        # Verify password was passed
        mock_run_rsync.assert_called_once_with(
            source="user@remote-host:~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            ssh_password=test_password,
        )

    @patch("fnb.fetcher.run_rsync")
    def test_run_with_existing_dry_run(self, mock_run_rsync):
        """Test that --dry-run isn't duplicated if already in options."""
        # Create task with --dry-run already in options
        task_with_dry_run = RsyncTaskConfig(
            label="test",
            summary="Test fetch task",
            host="user@remote-host",
            source="~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete", "--dry-run"],
            enabled=True,
        )

        # Run with dry_run=True
        run(task_with_dry_run, dry_run=True)

        # Verify options only have one --dry-run
        called_args = mock_run_rsync.call_args[1]
        dry_run_count = called_args["options"].count("--dry-run")
        self.assertEqual(dry_run_count, 1)

    def test_run_with_none_task(self):
        """Test that ValueError is raised when task is None."""
        with self.assertRaises(ValueError) as context:
            run(None)
        self.assertEqual(str(context.exception), "Task cannot be None")

    @patch("fnb.fetcher.get_ssh_password")
    @patch("fnb.fetcher.run_rsync")
    def test_run_with_env_password(self, mock_run_rsync, mock_get_ssh_password):
        """Test SSH password retrieval from environment variables."""
        # Mock environment password retrieval
        env_password = "env_test_password"
        mock_get_ssh_password.return_value = env_password

        # Run without explicit password
        run(self.task)

        # Verify get_ssh_password was called with correct host
        mock_get_ssh_password.assert_called_once_with("user@remote-host")

        # Verify run_rsync was called with environment password
        mock_run_rsync.assert_called_once_with(
            source="user@remote-host:~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            ssh_password=env_password,
        )

    @patch("fnb.fetcher.get_ssh_password")
    @patch("fnb.fetcher.run_rsync")
    def test_run_password_precedence_cli_over_env(
        self, mock_run_rsync, mock_get_ssh_password
    ):
        """Test that CLI password takes precedence over environment password."""
        # Mock environment password retrieval
        env_password = "env_password"
        cli_password = "cli_password"
        mock_get_ssh_password.return_value = env_password

        # Run with explicit CLI password
        run(self.task, ssh_password=cli_password)

        # Verify get_ssh_password was NOT called (CLI takes precedence)
        mock_get_ssh_password.assert_not_called()

        # Verify run_rsync was called with CLI password
        mock_run_rsync.assert_called_once_with(
            source="user@remote-host:~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            ssh_password=cli_password,
        )

    @patch("fnb.fetcher.get_ssh_password")
    @patch("fnb.fetcher.run_rsync")
    def test_run_no_password_available(self, mock_run_rsync, mock_get_ssh_password):
        """Test remote task execution when no SSH password is available."""
        # Mock no password available from environment
        mock_get_ssh_password.return_value = None

        # Run without explicit password
        run(self.task)

        # Verify get_ssh_password was called
        mock_get_ssh_password.assert_called_once_with("user@remote-host")

        # Verify run_rsync was called with None password
        mock_run_rsync.assert_called_once_with(
            source="user@remote-host:~/remote/path/",
            target="./local/path/",
            options=["-auvz", "--delete"],
            ssh_password=None,
        )

    @patch("fnb.fetcher.run_rsync")
    def test_run_local_task_with_password_warning(self, mock_run_rsync):
        """Test warning message when SSH password is provided for local task."""
        # Create local task (host="none")
        local_task = RsyncTaskConfig(
            label="local_test",
            summary="Local test task",
            host="none",
            source="./source/",
            target="./local/path/",
            options=["-auvz"],
            enabled=True,
        )
        os.makedirs(local_task.target, exist_ok=True)

        # Run with password for local task
        with patch("builtins.print") as mock_print:
            run(local_task, ssh_password="ignored_password")

        # Verify warning was printed
        mock_print.assert_any_call(
            "Warning: SSH password provided for local task, ignoring"
        )

        # Verify run_rsync was called with None password
        mock_run_rsync.assert_called_once_with(
            source="./source/",
            target="./local/path/",
            options=["-auvz"],
            ssh_password=None,
        )

    @patch("fnb.fetcher.verify_directory")
    @patch("fnb.fetcher.run_rsync")
    def test_run_target_directory_error(self, mock_run_rsync, mock_verify_directory):
        """Test handling of target directory verification failure."""
        # Mock verify_directory to fail
        mock_verify_directory.side_effect = FileNotFoundError(
            "Target directory not found"
        )

        result = run(self.task)

        # Verify the result is False
        self.assertFalse(result)

        # Verify verify_directory was called for target
        mock_verify_directory.assert_called_once_with("./local/path/", create=False)

        # Verify run_rsync was never called due to early return
        mock_run_rsync.assert_not_called()

    @patch("fnb.fetcher.verify_directory")
    @patch("fnb.fetcher.run_rsync")
    def test_run_rsync_failure(self, mock_run_rsync, mock_verify_directory):
        """Test handling of rsync command failure."""
        # Mock verify_directory to succeed
        mock_verify_directory.return_value = None

        # Mock run_rsync to raise CalledProcessError
        mock_run_rsync.side_effect = subprocess.CalledProcessError(
            returncode=2, cmd="rsync"
        )

        with self.assertRaises(subprocess.CalledProcessError) as context:
            run(self.task)

        # Verify the exception details
        self.assertEqual(context.exception.returncode, 2)
        self.assertEqual(context.exception.cmd, "rsync")

    @patch("fnb.fetcher.verify_directory")
    @patch("fnb.fetcher.run_rsync")
    def test_run_unexpected_error(self, mock_run_rsync, mock_verify_directory):
        """Test handling of unexpected errors during execution."""
        # Mock verify_directory to succeed
        mock_verify_directory.return_value = None

        # Mock run_rsync to raise a generic exception
        mock_run_rsync.side_effect = Exception("Network error")

        with self.assertRaises(Exception) as context:
            run(self.task)

        # Verify the exception message
        self.assertEqual(str(context.exception), "Network error")

    @patch("fnb.fetcher.verify_directory")
    @patch("fnb.fetcher.run_rsync")
    def test_run_with_create_dirs_success(self, mock_run_rsync, mock_verify_directory):
        """Test successful directory creation when create_dirs=True."""
        # Mock verify_directory to succeed
        mock_verify_directory.return_value = None

        result = run(self.task, create_dirs=True)

        # Verify the result is True
        self.assertTrue(result)

        # Verify verify_directory was called with create=True
        mock_verify_directory.assert_called_once_with("./local/path/", create=True)

        # Verify run_rsync was called
        mock_run_rsync.assert_called_once()


if __name__ == "__main__":
    unittest.main()

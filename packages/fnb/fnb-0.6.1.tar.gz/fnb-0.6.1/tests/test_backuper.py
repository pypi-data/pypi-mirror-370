import os
import shutil
import subprocess
import unittest
from unittest.mock import patch, Mock

from fnb.backuper import run
from fnb.config import RsyncTaskConfig


class TestBackuper(unittest.TestCase):
    """Test suite for backuper module."""

    def setUp(self):
        """Set up test fixtures."""
        self.task = RsyncTaskConfig(
            label="test",
            summary="Test backup task",
            host="none",  # Local source
            source="./local/path/",
            target="./external/backup/path/",
            options=["-auvz", "--delete"],
            enabled=True,
        )

        os.makedirs(self.task.source, exist_ok=True)
        os.makedirs(self.task.target, exist_ok=True)

    def tearDown(self):
        shutil.rmtree("./local", ignore_errors=True)
        shutil.rmtree("./external", ignore_errors=True)

    @patch("fnb.backuper.run_rsync")
    def test_run_basic(self, mock_run_rsync):
        """Test basic backup operation."""
        # Configure mock
        mock_run_rsync.return_value = None

        # Run the function
        run(self.task)

        # Verify the call
        mock_run_rsync.assert_called_once_with(
            source="./local/path/",
            target="./external/backup/path/",
            options=["-auvz", "--delete"],
            ssh_password=None,
        )

    @patch("fnb.backuper.run_rsync")
    def test_run_with_dry_run(self, mock_run_rsync):
        """Test backup operation with dry-run option."""
        # Run with dry_run=True
        run(self.task, dry_run=True)

        # Verify --dry-run was added to options
        called_args = mock_run_rsync.call_args[1]
        self.assertIn("--dry-run", called_args["options"])

    @patch("fnb.backuper.run_rsync")
    def test_run_with_existing_dry_run(self, mock_run_rsync):
        """Test that --dry-run isn't duplicated if already in options."""
        # Create task with --dry-run already in options
        task_with_dry_run = RsyncTaskConfig(
            label="test",
            summary="Test backup task",
            host="none",
            source="./local/path/",
            target="./external/backup/path/",
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

    @patch("fnb.backuper.verify_directory")
    @patch("fnb.backuper.run_rsync")
    def test_run_source_directory_error(self, mock_run_rsync, mock_verify_directory):
        """Test handling of source directory verification failure."""
        # Mock verify_directory to raise FileNotFoundError for source
        mock_verify_directory.side_effect = [
            FileNotFoundError("Source directory not found"),  # First call (source)
            None,  # Would be second call (target) but won't reach it
        ]

        result = run(self.task)

        # Verify the result is False
        self.assertFalse(result)

        # Verify verify_directory was called for source
        mock_verify_directory.assert_called_once_with("./local/path/", create=False)

        # Verify run_rsync was never called due to early return
        mock_run_rsync.assert_not_called()

    @patch("fnb.backuper.verify_directory")
    @patch("fnb.backuper.run_rsync")
    def test_run_target_directory_error(self, mock_run_rsync, mock_verify_directory):
        """Test handling of target directory verification failure."""
        # Mock verify_directory to succeed for source, fail for target
        mock_verify_directory.side_effect = [
            None,  # First call (source) - success
            ValueError("Invalid target directory"),  # Second call (target) - fail
        ]

        result = run(self.task)

        # Verify the result is False
        self.assertFalse(result)

        # Verify verify_directory was called twice
        self.assertEqual(mock_verify_directory.call_count, 2)

        # Verify run_rsync was never called due to early return
        mock_run_rsync.assert_not_called()

    @patch("fnb.backuper.verify_directory")
    @patch("fnb.backuper.run_rsync")
    def test_run_rsync_failure(self, mock_run_rsync, mock_verify_directory):
        """Test handling of rsync command failure."""
        # Mock verify_directory to succeed
        mock_verify_directory.return_value = None

        # Mock run_rsync to raise CalledProcessError
        mock_run_rsync.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="rsync"
        )

        with self.assertRaises(subprocess.CalledProcessError) as context:
            run(self.task)

        # Verify the exception details
        self.assertEqual(context.exception.returncode, 1)
        self.assertEqual(context.exception.cmd, "rsync")

    @patch("fnb.backuper.verify_directory")
    @patch("fnb.backuper.run_rsync")
    def test_run_unexpected_error(self, mock_run_rsync, mock_verify_directory):
        """Test handling of unexpected errors during execution."""
        # Mock verify_directory to succeed
        mock_verify_directory.return_value = None

        # Mock run_rsync to raise a generic exception
        mock_run_rsync.side_effect = Exception("Unexpected error")

        with self.assertRaises(Exception) as context:
            run(self.task)

        # Verify the exception message
        self.assertEqual(str(context.exception), "Unexpected error")


if __name__ == "__main__":
    unittest.main()

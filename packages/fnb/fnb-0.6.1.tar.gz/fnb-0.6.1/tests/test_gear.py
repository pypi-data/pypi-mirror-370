# tests/test_gear.py
import subprocess
import signal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pexpect

from fnb.gear import run_rsync, verify_directory


def test_run_rsync_basic():
    """Test running rsync without password (normal execution)"""
    with patch("subprocess.run") as mock_run:
        # Set up the mock
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        # Call the function
        run_rsync("source", "target", ["-auvz"])

        # Check the mock was called correctly
        mock_run.assert_called_once_with(
            ["rsync", "-auvz", "source", "target"], check=True
        )


@patch("pexpect.spawn")
def test_run_rsync_with_password(mock_spawn):
    """Test running rsync with SSH password using pexpect"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.exitstatus = 0
    mock_child.signalstatus = None

    # Call the function
    run_rsync("user@host:source", "target", ["-auvz"], ssh_password="password123")

    # Check the mocks were called correctly
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")


@patch("pexpect.spawn")
def test_run_rsync_ssh_timeout_caught(mock_spawn):
    """Test SSH timeout when caught by exception handler"""
    # Set up the mock to simulate timeout exception being caught
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.side_effect = pexpect.TIMEOUT("Password prompt timeout")
    mock_child.closed = False

    # Call the function - timeout should be caught and return False
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123", timeout=5
    )

    # Should return False when timeout is caught
    assert result is False
    mock_spawn.assert_called_once()
    mock_child.close.assert_called_once()


@patch("pexpect.spawn")
def test_run_rsync_ssh_eof(mock_spawn):
    """Test SSH connection closed unexpectedly (EOF)"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 1  # EOF matched
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return False for EOF
    assert result is False
    mock_spawn.assert_called_once()
    mock_child.close.assert_called_once()


@patch("pexpect.spawn")
def test_run_rsync_ssh_eof_exception(mock_spawn):
    """Test SSH EOF exception handling"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.side_effect = pexpect.EOF("Connection closed")
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return False for EOF exception
    assert result is False
    mock_spawn.assert_called_once()
    mock_child.close.assert_called_once()


@patch("pexpect.spawn")
def test_run_rsync_ssh_with_signal_termination(mock_spawn):
    """Test SSH session terminated by signal (e.g., SIGHUP)"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.exitstatus = None
    mock_child.signalstatus = signal.SIGHUP
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return True (signal termination is often normal)
    assert result is True
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")
    # In test environment (non-interactive), expect() is called instead of interact()
    assert mock_child.expect.call_count >= 2  # Password prompt + EOF expect


@patch("pexpect.spawn")
def test_run_rsync_ssh_with_exit_code(mock_spawn):
    """Test SSH session with non-zero exit code"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.exitstatus = 2  # Non-zero exit code
    mock_child.signalstatus = None
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should still return True (warnings are not failures)
    assert result is True
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")


@patch("pexpect.spawn")
def test_run_rsync_custom_pexpect_exception(mock_spawn):
    """Test handling of custom pexpect exceptions that aren't EOF or TIMEOUT"""

    # Create a custom pexpect exception that's not EOF or TIMEOUT
    class CustomPexpectError(pexpect.ExceptionPexpect):
        pass

    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.side_effect = CustomPexpectError("Custom pexpect error")
    mock_child.closed = False

    # Call the function and expect the custom exception to be re-raised
    with pytest.raises(CustomPexpectError):
        run_rsync("user@host:source", "target", ["-auvz"], ssh_password="password123")

    # Child should still be closed in finally block
    mock_child.close.assert_called_once()


@patch("pexpect.spawn")
def test_run_rsync_general_exception(mock_spawn):
    """Test handling of general exceptions during SSH execution"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.side_effect = RuntimeError("General runtime error")
    mock_child.closed = False

    # Call the function and expect exception to be re-raised
    with pytest.raises(RuntimeError):
        run_rsync("user@host:source", "target", ["-auvz"], ssh_password="password123")

    # Child should still be closed in finally block
    mock_child.close.assert_called_once()


@patch("pexpect.spawn")
def test_run_rsync_cleanup_exception(mock_spawn):
    """Test finally clause cleanup when close() raises exception"""
    # Set up the mock
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 1  # EOF
    mock_child.closed = False
    mock_child.close.side_effect = Exception("Close failed")  # Simulate close() error

    # Call the function - should handle close() exception gracefully
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return False for EOF and not raise close() exception
    assert result is False
    mock_spawn.assert_called_once()
    mock_child.close.assert_called_once()


def test_run_rsync_error_handling():
    """Test error handling when rsync fails"""
    with patch("subprocess.run") as mock_run:
        # Set up the mock to raise an exception
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["rsync", "-auvz", "source", "target"]
        )

        # Call the function and expect an exception
        with pytest.raises(subprocess.CalledProcessError):
            run_rsync("source", "target", ["-auvz"])


class TestVerifyDirectory:
    """Test cases for verify_directory function"""

    def setup_method(self):
        """Set up test environment before each test method"""
        # テスト用の一時ディレクトリパス
        self.test_dir = Path("./test_dir_for_verify")
        self.nested_dir = self.test_dir / "nested" / "path"

        # テスト前にクリーンアップ
        self._cleanup()

    def teardown_method(self):
        """Clean up after each test method"""
        self._cleanup()

    def _cleanup(self):
        """Remove test directories if they exist"""
        import shutil

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_existing_directory(self):
        """Should return Path object for existing directory"""
        # テスト用ディレクトリを作成
        self.test_dir.mkdir(exist_ok=True)

        # 検証
        result = verify_directory(str(self.test_dir))
        assert result == self.test_dir
        assert result.exists()
        assert result.is_dir()

    def test_missing_directory_without_create(self):
        """Should raise FileNotFoundError for non-existing directory when create=False"""
        # 存在しないディレクトリを検証
        with pytest.raises(FileNotFoundError) as excinfo:
            verify_directory(str(self.test_dir))

        assert str(self.test_dir) in str(excinfo.value)
        assert not self.test_dir.exists()

    def test_missing_directory_with_create(self):
        """Should create and return Path for non-existing directory when create=True"""
        # 存在しないディレクトリを作成オプションで検証
        result = verify_directory(str(self.test_dir), create=True)

        assert result == self.test_dir
        assert result.exists()
        assert result.is_dir()

    def test_nested_directory_with_create(self):
        """Should create nested directories when create=True"""
        # 存在しない多階層ディレクトリを作成オプションで検証
        result = verify_directory(str(self.nested_dir), create=True)

        assert result == self.nested_dir
        assert result.exists()
        assert result.is_dir()

    def test_file_path(self, tmp_path):
        """Should raise ValueError when path exists but is not a directory"""
        # 一時ファイルを作成
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")

        # ファイルパスを検証
        with pytest.raises(ValueError) as excinfo:
            verify_directory(str(test_file))

        assert "not a directory" in str(excinfo.value)

    def test_remote_path(self):
        """Should raise ValueError for remote paths"""
        remote_path = "user@host:/path/to/dir"

        with pytest.raises(ValueError) as excinfo:
            verify_directory(remote_path)

        assert "Remote paths are not supported" in str(excinfo.value)

    def test_create_directory_failure(self, tmp_path):
        """Should raise OSError when directory creation fails"""
        # Create a path under a file (impossible to create directory)
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        impossible_dir = test_file / "impossible_subdir"

        with pytest.raises(OSError) as excinfo:
            verify_directory(str(impossible_dir), create=True)

        assert "Failed to create directory" in str(excinfo.value)


@patch("os.isatty")
@patch("pexpect.spawn")
def test_run_rsync_interactive_environment(mock_spawn, mock_isatty):
    """Test SSH password automation in interactive environment"""
    # Set up the mocks
    mock_isatty.return_value = True  # Simulate interactive environment
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.exitstatus = 0
    mock_child.signalstatus = None
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return True and use interact() in interactive environment
    assert result is True
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")
    mock_child.interact.assert_called_once()


@patch("os.isatty")
@patch("pexpect.spawn")
def test_run_rsync_non_interactive_environment(mock_spawn, mock_isatty):
    """Test SSH password automation in non-interactive environment"""
    # Set up the mocks
    mock_isatty.return_value = (
        False  # Simulate non-interactive environment (CI/scripts)
    )
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.exitstatus = 0
    mock_child.signalstatus = None
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return True and use expect() instead of interact()
    assert result is True
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")
    mock_child.interact.assert_not_called()
    # expect() called twice: once for password prompt, once for EOF
    assert mock_child.expect.call_count == 2


@patch("os.isatty")
@patch("pexpect.spawn")
def test_run_rsync_interact_fallback_to_expect(mock_spawn, mock_isatty):
    """Test fallback from interact() to expect() when interact() fails"""
    # Set up the mocks
    mock_isatty.return_value = True  # Interactive environment
    mock_child = MagicMock()
    mock_spawn.return_value = mock_child
    mock_child.expect.return_value = 0  # Password prompt matched
    mock_child.interact.side_effect = Exception("interact() failed")  # Simulate failure
    mock_child.exitstatus = 0
    mock_child.signalstatus = None
    mock_child.closed = False

    # Call the function
    result = run_rsync(
        "user@host:source", "target", ["-auvz"], ssh_password="password123"
    )

    # Should return True and fallback to expect() after interact() fails
    assert result is True
    mock_spawn.assert_called_once()
    mock_child.sendline.assert_called_once_with("password123")
    mock_child.interact.assert_called_once()  # Attempted but failed
    assert mock_child.expect.call_count == 2  # Password prompt + fallback EOF

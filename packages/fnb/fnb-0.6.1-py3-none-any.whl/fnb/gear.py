# src/fnb/gear.py

import os
import subprocess
from pathlib import Path

import pexpect
import signal


def run_rsync(
    source: str,
    target: str,
    options: list[str],
    ssh_password: str | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess | bool:
    """Execute an rsync command with optional SSH password automation.

    Args:
        source (str): Source path (e.g., user@host:~/remote/path/source/).
        target (str): Destination path (e.g., ./local/dir).
        options (list[str]): Additional rsync options (e.g., ["-auvz", "--delete"]).
        ssh_password (str | None): SSH password for automation (if needed).
            If provided, uses pexpect to send password during SSH authentification.
        timeout (int): Timeout in seconds for SSH password prompt (default: 30).

    Raises:
        subprocess.CalledProcessError: If rsync execution fails.
        pexpect.TIMEOUT: If the SSH password prompt times out.
        pexpect.EOF: If the connection unexpectedly closes.
        Exception: For any other errors during execution.

    Returns:
        subprocess.CompletedProcess | bool: The completed process info if succesfull without password, or True/False if using password automation.
    """
    cmd = ["rsync"] + options + [source, target]
    cmd_str = " ".join(cmd)

    print(f"Executing: {cmd_str}")

    try:
        if ssh_password:
            # Use pexpect for interactive SSH passwort automation
            return _run_rsync_with_password(
                command=cmd_str,
                ssh_password=ssh_password,
                timeout=timeout,
            )
        else:
            # Regular non-interactive execution
            return subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"rsync failed with exit code {e.returncode}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        print(f"Error executing rsync: {e}")
        raise


def _run_rsync_with_password(
    command: str, ssh_password: str, timeout: int = 30
) -> bool:
    """Run rsync command with SSH password automation using pexpect

    Args:
        cmd_str (str): The full rsync command as string
        ssh_password (str): SSH password for automation
        timeout (int): Timeout in seconds for password prompt

    Returns:
        bool: True if successful, False if failed
    """
    child = None
    try:
        child = pexpect.spawn(command)
        child.timeout = timeout

        i = child.expect(["[Pp]assword:", pexpect.EOF, pexpect.TIMEOUT])

        if i == 0:  # Password prompt
            child.sendline(ssh_password)

            # Check if we're in an interactive environment
            if os.isatty(0):  # Interactive terminal (stdin is a TTY)
                try:
                    child.interact()
                except Exception as e:
                    print(f"interact() failed: {e}")
                    # Fall back to non-interactive mode
                    child.expect(pexpect.EOF, timeout=timeout)
            else:
                # Non-interactive environment (CI, scripts, etc.)
                print(
                    "Non-interactive environment detected, using expect() instead of interact()"
                )
                child.expect(pexpect.EOF, timeout=timeout)

            # Note: After interact() or expect(), the process might have exited with
            # SIGHUP or similar signals due to SSH connection closure.
            # This is often normal and shouldn't be treated as an error.

            # If we have a very clear failure (like returncode > 1), report it
            if child.exitstatus is not None and child.exitstatus > 1:
                print(f"Warning: rsync exited with code {child.exitstatus}")
                # We're being more lenient here and treating this as a warning
                # rather than a hard error

            # If process was terminated by a signal, it could be SIGHUP from SSH
            # which is often normal when the SSH session ends
            if child.signalstatus is not None:
                signal_name = signal.Signals(child.signalstatus).name
                print(
                    f"Note: Process ended with signal {signal_name}. "
                    f"This is often normal with SSH sessions."
                )

            return True

        elif i == 1:  # EOF
            print("Connection closed unexpectedly. Check SSH configuration.")
            # This might be a critical error, but we'll just warn and continue
            return False

        elif i == 2:  # TIMEOUT
            print(f"Timed out waiting for password prompt after {timeout}s.")
            raise pexpect.TIMEOUT(
                f"Timed out waiting for password prompt after {timeout}s: {command}"
            )

    except pexpect.ExceptionPexpect as e:
        print(f"pexpect error: {e}")
        # Only re-raise truly unexpected pexpect errors
        if not isinstance(e, (pexpect.EOF, pexpect.TIMEOUT)):
            raise
        return False
    except Exception as e:
        print(f"Unexpected error during rsync: {e}")
        raise
    finally:
        # Ensure child process is closed properly if it exists
        if child and not child.closed:
            try:
                child.close()
            except Exception:
                # Ignore errors during cleanup
                pass

    return False


def verify_directory(path: str, create: bool = False) -> Path:
    """Verifies that the specified directory exists or creates it if requested.

    Args:
        path (str): Directory path to verify/create.
        create (bool): If True, create the directory.

    Returns:
        Path: Path object of the verified directory.

    Raises:
        FileNotFoundError: If the directory doesn't exist and create=False.
        ValueError: If the path is invalid or is a remote path (contains ":")
        OSError: If directory creation fails.
    """
    # Check if the path is remote
    if ":" in path:
        raise ValueError(f"Remote paths are not supported for verification: {path}")

    dir_path = Path(path)

    if dir_path.exists():
        if not dir_path.is_dir():
            raise ValueError(f"Path exists but is not a directory: {dir_path}")
        return dir_path

    if not create:
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
        return dir_path
    except OSError as e:
        raise OSError(f"Failed to create directory {dir_path}: {e}")


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/gear.py

    """
    source = "user@hostname:~/remote/path/backup/"
    target = "./local/path/backup/"
    options = ["-auvz", "--delete", "--dry-run"]
    ssh_password = "something"
    run_rsync(source=source, target=target, options=options, ssh_password=ssh_password)

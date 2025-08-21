"""fetcher.py

This module handles the 'fetch' operation in the fnb (Fetch'n'Backup) tool.

- Fetch: Remote server -> Local directory
- Uses rsync via gear.run_rsync
- SSH-based transfer with optional automation
- Reads from [fetch.LABEL] section in config.toml

Separated from backuper.py for clarity and future extensibility.
For example:
    - Adding delay or throttling between fetches
    - Supporting different types of remote automation
    - Custom handling for partial/incremental fetch
"""

import subprocess

from fnb.config import RsyncTaskConfig
from fnb.env import get_ssh_password
from fnb.gear import run_rsync, verify_directory


def run(
    task: RsyncTaskConfig,
    dry_run: bool = False,
    ssh_password: str | None = None,
    create_dirs: bool = False,
) -> bool:
    """Execute the fetch operation for a given task

    Args:
        task (RsyncTaskConfig): The task configuration.
        dry_run (bool): Preview rsync without file transfer.
        ssh_password (str | None): SSH password for automation.
        create_dirs (bool): If True, create target directory if it doesn't exist.

    Returns:
        bool: True if successful, False if failed.

    Raises:
        ValueError: If task is None or invalid.
        FileNotFoundError: If target directory doesn't exist and create_dirs is False.
        subprocess.CalledProcessError: If rsync command fails.
        Exception: For any other errors during execution.
    """
    if task is None:
        raise ValueError("Task cannot be None")

    if not task.is_remote:
        if ssh_password:
            print("Warning: SSH password provided for local task, ignoring")
        ssh_password = None
    elif ssh_password is None and task.is_remote:
        # Try to get the password from environment variables
        ssh_password = get_ssh_password(task.host)
        if ssh_password:
            print(f"Using SSH password from environment for host: {task.host}")

    source = task.rsync_source
    target = task.rsync_target
    options = task.options.copy()

    if dry_run and "--dry-run" not in options:
        options.append("--dry-run")

    try:
        print(f"Fetching {task.label} from {source} to {target}")
        if dry_run:
            print("(DRY RUN - no files will be modified)")

        # For fetch, we only need to verify the target directory exists
        # Target is always local in fetch operations
        try:
            verify_directory(target, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            print(f"Target directory error: {e}")
            return False

        run_rsync(
            source=source,
            target=target,
            options=options,
            ssh_password=ssh_password,
        )

        print(f"Fetch completed successfully: {task.label}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Fetch failed with error code {e.returncode}: {task.label}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        print(f"Fetch failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/fetcher.py

    """
    from pathlib import Path

    from fnb.reader import ConfigReader

    config_path = Path("examples/config.toml")
    reader = ConfigReader(config_path)
    task = reader.config.get_task_by_label("fetch", "logs")
    run(task=task, dry_run=True, ssh_password=None, create_dirs=False)

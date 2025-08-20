"""backuper.py

This module handles the 'backup' operations in the fnb (Fetch'n'Backup) tool.

- Backup: Local directory -> Cloud or external storage
- Uses rsync via gear.run_rsync
- Typically used for syncing to OneDrive or NAS
- Reads from [backup.LABEL] section in config.toml

Separated from fetcher.py to allow for future specialization:
    - Adding snapshot-style folder naming (e.g., YYYY-MM-DD/)
    - Cloud API integration or notifications
    - Verification or checksum logic post-backup
"""

import subprocess

from fnb.config import RsyncTaskConfig
from fnb.gear import run_rsync, verify_directory


def run(
    task: RsyncTaskConfig, dry_run: bool = False, create_dirs: bool = False
) -> bool:
    """Execute the backup operation for a given label defined in config.toml.

    Args:
        task (RsyncTaskConfig): The rsync task configuration.
        dry_run (bool): Preview rsync without file transfer.
        create_dirs (bool): If True, create directories if they don't exist.

    Returns:
        bool: True if successful, False if failed.

    Raises:
        ValueError: If task is None or invalid.
        FileNotFoundError: If directories doesn't exist and create_dirs is false.
        subprocess.CalledProcessError: If rsync command fails.
        Exception: For any other errors during execution.
    """
    if task is None:
        raise ValueError("Task cannot be None")

    source = task.rsync_source
    target = task.rsync_target
    options = task.options.copy()

    if dry_run and "--dry-run" not in options:
        options.append("--dry-run")

    try:
        print(f"Backing up {task.label} from {source} to {target}")
        if dry_run:
            print("(DRY RUN - no files will be modified)")

        # Ensure source directory exists (for backup, source is always local)
        try:
            verify_directory(source, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            print(f"Source directory error: {e}")
            return False

        # Ensure target directory exists (for backup, source is always local)
        try:
            verify_directory(target, create=create_dirs)
        except (FileNotFoundError, ValueError) as e:
            print(f"Target directory error: {e}")
            return False

        run_rsync(source=source, target=target, options=options, ssh_password=None)

        print(f"Backup completed successfully: {task.label}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Backup failed with error code {e.returncode}: {task.label}")
        # Re-raise to allow caller to handle
        raise
    except Exception as e:
        print(f"Backup failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/backuper.py

    """
    from pathlib import Path

    from fnb.reader import ConfigReader

    config_path = Path("examples/config.toml")
    reader = ConfigReader(config_path)
    task = reader.config.get_task_by_label("backup", "logs")
    run(task=task, dry_run=True, create_dirs=False)

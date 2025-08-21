# config.py
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class RsyncTaskConfig(BaseModel):
    """A single rsync task configuration

    Attributes:
        label (str): Unique identifier for the task.
        summary (str): Short description of the task.
        host (str): Remote host (e.g., "user@host") or "none" for local.
        source (str): Source path of rsync.
        target (str): Target path of rsync.
        options (list[str]): List of rsync options.
        enabled (bool): Whether the task is enabled.
        mode (Literal["fetch", "backup"]): Mode of the task.
    """

    label: str
    summary: str
    host: str
    source: str
    target: str
    options: list[str]
    enabled: bool = True

    @property
    def is_remote(self) -> bool:
        """Check if the task involves a remote host.

        Returns:
            bool: True if the host is remote, False otherwise.
        """
        return self.host.lower() != "none"

    @property
    def rsync_source(self) -> str:
        """Get the formatted source path for rsync.

        Returns:
            str: The source path, prefixed with host if remote.
        """
        return f"{self.host}:{self.source}" if self.is_remote else self.source

    @property
    def rsync_target(self) -> str:
        """Get the target path for rsync.

        Returns:
            str: The target path.
        """
        return self.target


class FnbConfig(BaseModel):
    """Configuration loader for fnb (Fetch'n'Backup)

    This class loads and parsed configuration files for fetch/backup tasks,
    expands environment variables, and provides access to task configurations.

    Attributes:
        fetch (dict[str, RsyncTaskConfig]): Fetch task configurations.
        backup (dict[str, RsyncTaskConfig]): Backup task configurations.
    """

    fetch: dict[str, RsyncTaskConfig] = {}
    backup: dict[str, RsyncTaskConfig] = {}

    def get_enabled_tasks(
        self, kind: Literal["fetch", "backup"]
    ) -> list[RsyncTaskConfig]:
        """Get all enabled tasks of the specified kind.

        Args:
            kind (Literal["fetch", "backup"]): The kind of tasks to retrieve.

        Returns:
            list[RsyncTaskConfig]: List of enabled tasks.
        """
        tasks = getattr(self, kind)
        return [task for task in tasks.values() if task.enabled]

    def get_task_by_label(
        self, kind: Literal["fetch", "backup"], label: str
    ) -> RsyncTaskConfig | None:
        """Get a task by its label.

        Args:
            kind (Literal["fetch", "backup"]): The kind of task to retrieve.
            label (str): The label of the task.

        Returns:
            Optional[RsyncTaskConfig]: The task if found, None otherwise.
        """
        tasks = getattr(self, kind)
        for task in tasks.values():
            if task.label == label:
                return task
        return None


def load_config(path: Path) -> FnbConfig:
    """Load configuration from a TOML file

    Args:
        path (Path): Path to the TOML configuration file.

    Returns:
        FnbConfig: Parsed configuration object.

    Raises:
        FileNotFoundError: If the configuration file doew not exist.
        ValueError: If the configuration file is not a valid TOML file.
        Exception: Other exceptions rased during parsing
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {path}")

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML file at {path}: {e}")
    except Exception as e:
        raise Exception(f"Error reading configuration file at {path}: {e}")

    try:
        return FnbConfig.model_validate(data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


if __name__ == "__main__":
    """Self test

    $ uv run python src/fnb/config.py

    """
    config = load_config(Path("examples/config.toml"))

    print("\nEnabled Fetch Tasks:")
    for task in config.get_enabled_tasks("fetch"):
        print(f" - {task.label}: {task.source} -> {task.target}")

    print("\nEnabled Backup Tasks:")
    for task in config.get_enabled_tasks("backup"):
        print(f" - {task.label}: {task.source} -> {task.target}")

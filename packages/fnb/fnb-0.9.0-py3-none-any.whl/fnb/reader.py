import os
import tomllib
from pathlib import Path
from typing import Any

import platformdirs

from fnb.config import FnbConfig
from fnb.gear import verify_directory


class ConfigReader:
    def __init__(self, config_path: Path | None = None):
        """Initialize a ConfigReader

        Args:
            config_path (Path | None): Path to config file, or None to auto-detect.

        Raises:
            FileNotFoundError: If no config file could be found.
            ValueError: If the config file is invalid.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_file(self.config_path)
        self._expand_env_vars()

    def _load_file(self, path: Path) -> FnbConfig:
        """Load a TOML config file and convert to FnbConfig.

        Args:
            path (Path): Path to the config file.

        Returns:
            FnbConfig: The parsed config.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file is invalid TOML or doesn't match the expected schema.

        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            with path.open("rb") as f:
                raw_data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML in config file {path}: {e}")
        except Exception as e:
            raise ValueError(f"Error reading config file {path}: {e}")

        try:
            return FnbConfig.model_validate(raw_data)
        except Exception as e:
            raise ValueError(f"Invalid config schema in {path}: {e}")

    def _get_default_config_path(self) -> Path:
        """Find the default config file in the standard locations.

        Returns:
            Path: Path to the config file.

        Raises:
            FileNotFoundError: If no config file could be found.
        """
        app_name = "fnb"
        config_dir = platformdirs.user_config_path(app_name)
        candidates = [
            Path("./fnb.toml"),
            Path("./config.toml"),
            *sorted(Path("./config/").glob("*.toml")),
            config_dir / "config.toml",
            *sorted(config_dir.glob("*.toml")),
        ]

        for path in candidates:
            if path.exists():
                return path

        # Build a more helpful error message
        searched_paths = "\n - ".join([str(p) for p in candidates])
        raise FileNotFoundError(
            f"No config file found in expected locations:\n - {searched_paths}\n"
            "Run 'fnb init' to create one in the current directory."
        )

    def _expand_env_vars(self) -> None:
        """Expand environment variables in path strings within the config."""

        def expand(obj: Any) -> Any:
            """Recursively expand env vars in strings or collections"""
            if isinstance(obj, str):
                # Expand environment variables
                return os.path.expandvars(obj)
            elif isinstance(obj, list):
                return [expand(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: expand(v) for k, v in obj.items()}
            else:
                return obj

        for section in ("fetch", "backup"):
            section_data = getattr(self.config, section)
            for key, task in section_data.items():
                updated = task.model_dump()
                expanded = expand(updated)
                section_data[key] = task.model_validate(expanded)

    def print_status(self, check_dirs: bool = True) -> None:
        """Print status of fetch tasks.

        Args:
            check_dirs (bool): If True, check if directories exist.
        """
        print(f"\n📄 Config file: {self.config_path}")

        self._print_fetch_tasks(check_dirs)
        self._print_backup_tasks(check_dirs)

        print("")  # 最後に空行を追加

    def _print_fetch_tasks(self, check_dirs: bool) -> None:
        """Print status of fetch tasks.

        Args:
            check_dirs (bool): If True, check if directories exist.
        """
        print("\n📦 Fetch Tasks (remote → local):")
        fetch_tasks = self.config.get_enabled_tasks("fetch")
        if not fetch_tasks:
            print(" ❌ No enabled fetch tasks")
            return

        for task in fetch_tasks:
            print(f" ✅ {task.label}: {task.rsync_source} → {task.rsync_target}")

            # rsync_targetのディレクトリの存在確認
            if check_dirs and ":" not in task.rsync_target:  # ローカルパスのみチェック
                self._check_directory(task.rsync_target, f"Target for {task.label}")

    def _print_backup_tasks(self, check_dirs: bool) -> None:
        """Print status of backup tasks.

        Args:
            check_dirs (bool): If True, check if directories exist.
        """
        print("\n💾 Backup Tasks (local → external):")
        backup_tasks = self.config.get_enabled_tasks("backup")
        if not backup_tasks:
            print(" ❌ No enabled backup tasks")
            return

        for task in backup_tasks:
            print(f" ✅ {task.label}: {task.rsync_source} → {task.rsync_target}")

            # rsync_targetのディレクトリの存在確認
            if check_dirs and ":" not in task.rsync_target:  # ローカルパスのみチェック
                self._check_directory(task.rsync_target, f"Target for {task.label}")

    def _check_directory(self, path: str, label: str) -> None:
        """Check if a directory exists and print status.

        Args:
            path (str): Path to check
            label (str): Label to display in output
        """
        try:
            dir_path = verify_directory(path)
            print(f"    📁 {label} exists: {dir_path}")
        except FileNotFoundError:
            print(f"    ⚠️  {label} does not exist: {path}")
        except ValueError as e:
            print(f"    ⚠️  {label} issue: {e}")


if __name__ == "__main__":
    """Self test.

    $ uv run python src/fnb/reader.py

    """
    reader = ConfigReader()
    config = reader.config

    print("📦 Enabled Fetch Tasks:")
    for task in config.get_enabled_tasks("fetch"):
        print(f" - {task.label}: {task.source} → {task.target}")

    print("\n💾 Enabled Backup Tasks:")
    for task in config.get_enabled_tasks("backup"):
        print(f" - {task.label}: {task.source} → {task.target}")

    reader.print_status()

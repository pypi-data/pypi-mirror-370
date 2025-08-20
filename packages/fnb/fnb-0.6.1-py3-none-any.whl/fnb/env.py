"""env.py

This module handles loading environment variables from .env files
and retrieving SSH passwords for specific hosts.

Uses python-dotenv to handle the .env file loading and provides
a clean interface for retrieving host-specific SSH passwords.
"""

import os
from pathlib import Path

import platformdirs
from dotenv import load_dotenv


def load_env_files() -> bool:
    """Load environment variables from .env files in various locations.

    Loads from the following locations in order (later overrides earlier):
    1. ~/.config/fnb/.env - Global user configuration
    2. ./.env - Local project configuration

    Returns:
        bool: True if any .env file was loaded, False otherwise.
    """
    # Track if we loaded any env files
    loaded = False

    # Global config location
    app_name = "fnb"
    config_dir = platformdirs.user_config_path(app_name)

    global_env = config_dir / ".env"
    if global_env.exists():
        load_dotenv(global_env)
        loaded = True

    # Local config (higher priority)
    local_env = Path("./.env")
    if local_env.exists():
        load_dotenv(local_env)
        loaded = True

    return loaded


def get_ssh_password(host: str) -> str | None:
    """Get the SSH password for a specific host from environment variables.

    Checks environment variables in the following order:
    1. FNB_PASSWORD_{normalized_host} - Host-specific password
    2. FNB_PASSWORD_DEFAULT - Default password for all hosts

    Args:
        host (str): The hostname, either "user@host" or just "host"

    Returns:
        str | None: The password if found, None otherwise
    """
    # Load .env files if not already loaded
    load_env_files()

    # First try to find a password for the specific host
    # Replace any characters that can't be in an
    # environment variable with underscore
    normalized_host = host.replace("@", "_").replace(".", "_").replace("-", "_")
    password = os.environ.get(f"FNB_PASSWORD_{normalized_host}")

    # If not found, try the default password
    if password is None:
        password = os.environ.get("FNB_PASSWORD_DEFAULT")

    return password


if __name__ == "__main__":
    """Self Test.

    $ uv run src/fnb/env.py

    """
    loaded = load_env_files()
    print(f"Loaded .env files: {loaded}")

    test_host = "user@example.com"
    password = get_ssh_password(test_host)
    if password:
        print(f"Found password for {test_host}: {'*' * len(password)}")
    else:
        print(f"No password found for {test_host}")

    # Test default password
    default_password = os.environ.get("FNB_PASSWORD_DEFAULT")
    if default_password:
        print(f"Default password is set: {'*' * len(default_password)}")
    else:
        print("No default password found")

# tests/test_env.py
import os
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from fnb.env import get_ssh_password, load_env_files


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables for testing"""
    env_backup = {k: v for k, v in os.environ.items() if k.startswith("FNB_PASSWORD")}
    # Clear FNB_PASSWORD variables
    for key in list(os.environ.keys()):
        if key.startswith("FNB_PASSWORD"):
            del os.environ[key]
    yield
    # Restore
    os.environ.update(env_backup)


@pytest.fixture
def temp_env_files():
    """Create temporary .env files for testing"""
    with TemporaryDirectory() as temp_dir:
        global_env = Path(temp_dir) / "global" / ".env"
        local_env = Path(temp_dir) / "local" / ".env"

        global_env.parent.mkdir(parents=True)
        local_env.parent.mkdir(parents=True)

        yield {
            "global": global_env,
            "local": local_env,
            "global_dir": global_env.parent,
            "local_dir": local_env.parent,
        }


@pytest.fixture
def mock_platformdirs():
    """Mock platformdirs for cross-platform testing"""
    with patch("fnb.env.platformdirs.user_config_path") as mock:
        yield mock


class TestLoadEnvFiles:
    """Test cases for load_env_files function"""

    def test_load_env_files_no_files(self, mock_platformdirs, tmp_path, clean_env):
        """Test load_env_files when no .env files exist"""
        mock_platformdirs.return_value = tmp_path / "config"

        with patch("fnb.env.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = load_env_files()

        assert result is False

    def test_load_env_files_global_only(
        self, mock_platformdirs, temp_env_files, clean_env
    ):
        """Test loading global .env file only"""
        mock_platformdirs.return_value = temp_env_files["global_dir"]

        # Create global .env file
        temp_env_files["global"].write_text("FNB_PASSWORD_DEFAULT=global_password\n")

        with patch("fnb.env.Path") as mock_local_path:
            mock_local_path.return_value.exists.return_value = False
            result = load_env_files()

        assert result is True
        assert os.environ.get("FNB_PASSWORD_DEFAULT") == "global_password"

    def test_load_env_files_local_only(
        self, mock_platformdirs, temp_env_files, clean_env
    ):
        """Test loading local .env file only"""
        mock_platformdirs.return_value = temp_env_files["global_dir"]

        # Create local .env file
        temp_env_files["local"].write_text("FNB_PASSWORD_DEFAULT=local_password\n")

        with patch("fnb.env.Path") as mock_local_path:
            mock_local_path.return_value.exists.return_value = True
            mock_local_path.return_value = temp_env_files["local"]
            result = load_env_files()

        assert result is True
        assert os.environ.get("FNB_PASSWORD_DEFAULT") == "local_password"

    @pytest.mark.skip(
        reason="Priority test requires more complex mocking - to be fixed"
    )
    def test_load_env_files_priority_local_overrides_global(
        self, mock_platformdirs, temp_env_files, clean_env
    ):
        """Test that local .env overrides global .env"""
        # TODO: Fix priority test with proper mocking
        pass


class TestGetSshPassword:
    """Test cases for get_ssh_password function"""

    def test_get_ssh_password_not_found(self, clean_env):
        """Test when no password is found"""
        password = get_ssh_password("unknown@host.com")

        assert password is None

    def test_get_ssh_password_default_fallback(self, clean_env):
        """Test falling back to default password when host-specific not found"""
        os.environ["FNB_PASSWORD_DEFAULT"] = "default_password"

        password = get_ssh_password("test@example.com")

        assert password == "default_password"

    def test_get_ssh_password_host_specific(self, clean_env):
        """Test retrieving host-specific password"""
        os.environ["FNB_PASSWORD_test_example_com"] = "host_specific_password"
        os.environ["FNB_PASSWORD_DEFAULT"] = "default_password"

        password = get_ssh_password("test@example.com")

        # Should get host-specific password, not default
        assert password == "host_specific_password"

    def test_get_ssh_password_host_normalization_user_at_host(self, clean_env):
        """Test host normalization for user@host format"""
        os.environ["FNB_PASSWORD_user_server_example_com"] = "normalized_password"

        password = get_ssh_password("user@server.example.com")

        assert password == "normalized_password"

    def test_get_ssh_password_host_normalization_host_with_dashes(self, clean_env):
        """Test host normalization for hosts with dashes"""
        os.environ["FNB_PASSWORD_web_server_01"] = "dash_password"

        password = get_ssh_password("web-server-01")

        assert password == "dash_password"

    def test_get_ssh_password_host_normalization_mixed_special_chars(self, clean_env):
        """Test host normalization with multiple special characters"""
        os.environ["FNB_PASSWORD_dev_user_test_db_example_org"] = "mixed_password"

        password = get_ssh_password("dev-user@test.db.example.org")

        assert password == "mixed_password"


class TestPlatformIntegration:
    """Test platform-specific functionality"""

    def test_platformdirs_integration(self, clean_env):
        """Test platformdirs integration for cross-platform config paths"""
        with patch("fnb.env.platformdirs.user_config_path") as mock_config_path:
            mock_config_path.return_value = Path("/mock/config/fnb")

            with patch("fnb.env.Path") as mock_path:
                mock_path.return_value.exists.return_value = False
                result = load_env_files()

            # Should call platformdirs with correct app name
            mock_config_path.assert_called_once_with("fnb")
            assert result is False

    def test_load_env_files_both_exist_integration(
        self, mock_platformdirs, temp_env_files, clean_env
    ):
        """Test integration when both global and local .env files exist"""
        mock_platformdirs.return_value = temp_env_files["global_dir"]

        # Create both files
        temp_env_files["global"].write_text("FNB_PASSWORD_GLOBAL=global_value\n")
        temp_env_files["local"].write_text("FNB_PASSWORD_LOCAL=local_value\n")

        with patch("fnb.env.Path") as mock_local_path:
            mock_local_path.return_value.exists.return_value = True
            mock_local_path.return_value = temp_env_files["local"]
            result = load_env_files()

        assert result is True
        assert os.environ.get("FNB_PASSWORD_GLOBAL") == "global_value"
        assert os.environ.get("FNB_PASSWORD_LOCAL") == "local_value"


class TestSelfTestExecution:
    """Test __main__ self-test execution"""

    def test_main_execution_with_password(self, clean_env):
        """Test self-test execution when password is found"""
        os.environ["FNB_PASSWORD_user_example_com"] = "test_password"

        # Execute the main block directly by running the module as script
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "src/fnb/env.py"],
            capture_output=True,
            text=True,
            cwd=".",
            env=os.environ.copy(),
        )

        assert result.returncode == 0
        assert "Found password for user@example.com:" in result.stdout
        assert "*" * len("test_password") in result.stdout

    def test_main_execution_no_password(self, clean_env):
        """Test self-test execution when no password is found"""
        # Ensure no passwords are set for user@example.com
        # clean_env fixture already clears FNB_PASSWORD_* variables

        # Execute the main block
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "src/fnb/env.py"],
            capture_output=True,
            text=True,
            cwd=".",
            env=os.environ.copy(),
        )

        assert result.returncode == 0
        assert "No password found for user@example.com" in result.stdout
        assert "No default password found" in result.stdout

    def test_main_execution_with_default_password(self, clean_env):
        """Test self-test execution with only default password set"""
        os.environ["FNB_PASSWORD_DEFAULT"] = "default_password"
        # No specific password for user@example.com

        # Execute the main block
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "src/fnb/env.py"],
            capture_output=True,
            text=True,
            cwd=".",
            env=os.environ.copy(),
        )

        assert result.returncode == 0
        assert "Found password for user@example.com:" in result.stdout
        assert "Default password is set:" in result.stdout
        assert "*" * len("default_password") in result.stdout

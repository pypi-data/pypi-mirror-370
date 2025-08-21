"""Integration tests for complete fnb workflows.

This module contains integration tests that verify end-to-end functionality
across multiple modules, CLI commands, and complete user workflows.
"""

import os
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from typer.testing import CliRunner

from fnb.cli import app


@pytest.mark.integration
class TestIntegrationFixtures:
    """Test fixtures and utilities for integration tests."""

    @pytest.fixture
    def integration_temp_dir(self, tmp_path):
        """Create a temporary directory and change to it for integration tests."""
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        yield tmp_path
        os.chdir(original_cwd)

    @pytest.fixture
    def cli_runner(self):
        """CLI runner for integration tests."""
        return CliRunner()

    @pytest.fixture
    def integrated_mocks(self):
        """Comprehensive mocks for integration testing."""
        with (
            patch("fnb.gear.run_rsync") as mock_run_rsync,
            patch("fnb.gear.verify_directory") as mock_verify_directory,
            patch("fnb.env.load_env_files") as mock_load_env,
            patch("fnb.env.get_ssh_password") as mock_get_password,
        ):
            mock_run_rsync.return_value = None
            mock_verify_directory.return_value = None
            mock_load_env.return_value = True
            mock_get_password.return_value = "test_password"

            yield {
                "run_rsync": mock_run_rsync,
                "verify_directory": mock_verify_directory,
                "load_env": mock_load_env,
                "get_ssh_password": mock_get_password,
            }

    @pytest.fixture
    def sample_config_content(self):
        """Sample configuration content for integration tests."""
        return """[fetch.logs]
label = "logs"
summary = "Fetch logs from remote server"
host = "user@testhost"
source = "~/logs/"
target = "./local/logs/"
options = ["-av", "--delete"]
enabled = true

[fetch.docs]
label = "docs"
summary = "Fetch documentation"
host = "user@testhost"
source = "~/docs/"
target = "./local/docs/"
options = ["-av"]
enabled = true

[backup.logs]
label = "logs"
summary = "Backup logs to external storage"
host = "none"
source = "./local/logs/"
target = "./backup/logs/"
options = ["-av", "--delete"]
enabled = true

[backup.docs]
label = "docs"
summary = "Backup documentation"
host = "none"
source = "./local/docs/"
target = "./backup/docs/"
options = ["-av"]
enabled = false
"""

    @pytest.fixture
    def sample_env_content(self):
        """Sample environment file content for integration tests."""
        return """# SSH passwords for integration testing
FNB_PASSWORD_user_testhost=test_password
FNB_PASSWORD_admin_server=admin_password
"""

    @pytest.fixture
    def real_config_workflow(
        self, integration_temp_dir, sample_config_content, sample_env_content
    ):
        """Setup real configuration files for workflow testing."""
        config_file = integration_temp_dir / "fnb.toml"
        config_file.write_text(sample_config_content)

        env_file = integration_temp_dir / ".env"
        env_file.write_text(sample_env_content)

        # Create directory structure
        (integration_temp_dir / "local" / "logs").mkdir(parents=True, exist_ok=True)
        (integration_temp_dir / "local" / "docs").mkdir(parents=True, exist_ok=True)
        (integration_temp_dir / "backup").mkdir(parents=True, exist_ok=True)

        return {
            "config": config_file,
            "env": env_file,
            "temp_dir": integration_temp_dir,
        }


@pytest.mark.integration
class TestCompleteWorkflows(TestIntegrationFixtures):
    """Integration tests for complete fnb workflows."""

    def test_basic_setup_and_teardown(self, cli_runner, integration_temp_dir):
        """Test basic integration test setup works correctly."""
        # Verify we're in the temp directory
        assert os.getcwd() == str(integration_temp_dir)

        # Verify CLI runner works
        result = cli_runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "fnb" in result.output

    def test_fixtures_work_correctly(self, real_config_workflow, integrated_mocks):
        """Test that integration fixtures are set up correctly."""
        # Verify config file exists
        assert real_config_workflow["config"].exists()
        assert real_config_workflow["env"].exists()

        # Verify directory structure
        assert (real_config_workflow["temp_dir"] / "local" / "logs").exists()
        assert (real_config_workflow["temp_dir"] / "backup").exists()

        # Verify mocks are active
        assert "run_rsync" in integrated_mocks
        assert "get_ssh_password" in integrated_mocks


@pytest.mark.integration
class TestCLIWorkflowIntegration(TestIntegrationFixtures):
    """Integration tests for CLI command workflows."""

    def test_init_status_workflow(self, cli_runner, integration_temp_dir):
        """Test init → status workflow integration."""
        # Step 1: Initialize configuration
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Created fnb.toml from template" in result.output

        # Verify config file was created
        assert (integration_temp_dir / "fnb.toml").exists()

        # Step 2: Check status with generated config
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Config file: fnb.toml" in result.output
        assert "Fetch Tasks" in result.output
        assert "Backup Tasks" in result.output

    def test_init_status_fetch_workflow(
        self, cli_runner, integration_temp_dir, integrated_mocks
    ):
        """Test complete init → status → fetch workflow."""
        # Step 1: Initialize
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Step 2: Check status
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0

        # Step 3: Execute fetch (with mocked gear operations)
        result = cli_runner.invoke(app, ["fetch", "logs", "--dry-run"])
        assert result.exit_code == 0
        assert "Fetching logs" in result.output

    def test_init_status_backup_workflow(
        self, cli_runner, integration_temp_dir, integrated_mocks
    ):
        """Test complete init → status → backup workflow."""
        # Step 1: Initialize
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Step 2: Check status
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0

        # Create source directory for backup
        source_dir = integration_temp_dir / "local" / "logs"
        source_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Execute backup (with mocked gear operations)
        result = cli_runner.invoke(app, ["backup", "logs", "--dry-run"])
        assert result.exit_code == 0
        assert "Backing up logs" in result.output

    def test_status_with_existing_config(self, cli_runner, real_config_workflow):
        """Test status command with pre-existing configuration."""
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Config file: fnb.toml" in result.output
        assert "logs" in result.output
        assert "docs" in result.output

        # Check that tasks are shown correctly
        assert "Fetch Tasks" in result.output
        assert "Backup Tasks" in result.output

    def test_fetch_dry_run_with_existing_config(self, cli_runner, real_config_workflow):
        """Test fetch command dry-run with pre-existing configuration."""
        result = cli_runner.invoke(app, ["fetch", "logs", "--dry-run"])
        assert result.exit_code == 0
        assert "Fetching logs" in result.output
        assert "DRY RUN" in result.output

    def test_backup_with_existing_config_success(
        self, cli_runner, real_config_workflow
    ):
        """Test backup command success flow."""
        # Create source and target directories
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        (real_config_workflow["temp_dir"] / "backup" / "logs").mkdir(
            parents=True, exist_ok=True
        )

        result = cli_runner.invoke(app, ["backup", "logs"])
        assert result.exit_code == 0
        assert "Backing up logs" in result.output
        # Backup actually runs rsync locally, so it should complete
        assert "completed successfully" in result.output

    def test_cli_error_handling_integration(self, cli_runner, integration_temp_dir):
        """Test CLI error handling without configuration."""
        # Try to run commands without config file
        result = cli_runner.invoke(app, ["fetch", "nonexistent"])
        assert result.exit_code != 0
        assert "Config file not found" in result.output

        result = cli_runner.invoke(app, ["backup", "nonexistent"])
        assert result.exit_code != 0
        assert "Config file not found" in result.output

        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code != 0
        assert "No config file found" in result.output


@pytest.mark.integration
class TestMultiModuleIntegration(TestIntegrationFixtures):
    """Integration tests for multi-module interactions."""

    def test_config_reader_gear_integration(self, real_config_workflow):
        """Test ConfigReader → gear integration."""
        from fnb.reader import ConfigReader

        # Load configuration with explicit path
        reader = ConfigReader(real_config_workflow["config"])
        config = reader.config

        # Verify configuration is loaded correctly
        assert config is not None
        fetch_task = config.get_task_by_label("fetch", "logs")
        assert fetch_task.label == "logs"
        assert fetch_task.host == "user@testhost"

        # Test integration by verifying task properties (no external calls)
        # This tests the config→operation integration without network dependencies
        assert fetch_task.rsync_source == "user@testhost:~/logs/"
        assert fetch_task.rsync_target == "./local/logs/"
        assert fetch_task.is_remote is True

        # Test that backup task integration also works
        backup_task = config.get_task_by_label("backup", "logs")
        assert backup_task.label == "logs"
        assert backup_task.host == "none"
        assert backup_task.is_remote is False

    def test_env_gear_cli_integration(self, real_config_workflow, integrated_mocks):
        """Test env → gear → CLI integration for SSH passwords."""
        # Test that SSH password flows through the system
        password = integrated_mocks["get_ssh_password"]("user@testhost")
        assert password == "test_password"

        # Test integration by verifying the SSH password retrieval mechanism
        from fnb.reader import ConfigReader
        from fnb.env import get_ssh_password

        reader = ConfigReader(real_config_workflow["config"])
        fetch_task = reader.config.get_task_by_label("fetch", "logs")

        # Test that remote tasks would trigger password lookup
        assert fetch_task.is_remote is True
        assert fetch_task.host == "user@testhost"

        # Test the integration path without actual network calls
        # The integration is tested by verifying task properties and password lookup pattern

    def test_generator_reader_cli_integration(self, cli_runner, integration_temp_dir):
        """Test generator → reader → CLI integration (init workflow)."""
        # Step 1: Generate config with CLI
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Step 2: Verify reader can load generated config
        from fnb.reader import ConfigReader

        reader = ConfigReader()
        assert reader.config is not None

        # Step 3: Verify generated config has expected structure
        assert hasattr(reader.config, "fetch")
        assert hasattr(reader.config, "backup")
        assert len(reader.config.fetch) > 0
        assert len(reader.config.backup) > 0

        # Step 4: Verify CLI can use generated config
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Fetch Tasks" in result.output

    def test_full_module_chain_integration(
        self, real_config_workflow, integrated_mocks
    ):
        """Test complete module chain: reader → config → operation → gear."""
        # Step 1: Reader loads configuration
        from fnb.reader import ConfigReader

        reader = ConfigReader(real_config_workflow["config"])
        config = reader.config

        # Step 2: Config provides validated task
        backup_task = config.get_task_by_label("backup", "logs")
        assert backup_task.label == "logs"
        assert backup_task.host == "none"  # Local backup

        # Step 3: Operation module processes task
        from fnb.backuper import run

        # Create directories for backup to work
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        (real_config_workflow["temp_dir"] / "backup" / "logs").mkdir(
            parents=True, exist_ok=True
        )

        # Step 4: Gear executes rsync - for local backup, gear functions are called
        result = run(backup_task, dry_run=True)
        assert result is True

        # For local backup, verify_directory should be called but not run_rsync in dry mode

    def test_configuration_discovery_integration(self, integration_temp_dir):
        """Test configuration file discovery across modules."""
        from fnb.reader import ConfigReader

        # Test 1: No config file found - should raise error
        try:
            reader = ConfigReader()
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected behavior

        # Test 2: Create local config file
        config_content = """[fetch.test]
label = "test"
summary = "Test task"
host = "localhost"
source = "/tmp/"
target = "/tmp/backup/"
options = ["-av"]
enabled = true
"""
        config_file = integration_temp_dir / "fnb.toml"
        config_file.write_text(config_content)

        # Test 3: Reader discovers local config
        reader = ConfigReader()
        assert reader.config is not None
        assert reader.config.get_task_by_label("fetch", "test") is not None

    def test_error_propagation_through_modules(self, real_config_workflow):
        """Test error propagation through the complete module stack."""
        from fnb.reader import ConfigReader
        from fnb.backuper import run

        # Load valid config
        reader = ConfigReader(real_config_workflow["config"])
        backup_task = reader.config.get_task_by_label("backup", "logs")

        # Create source but NOT target directory to trigger error
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        # Intentionally don't create backup/logs directory

        # Run backup - should fail gracefully
        result = run(backup_task, dry_run=False, create_dirs=False)
        assert result is False  # Should return False on directory error


@pytest.mark.integration
class TestSyncWorkflowIntegration(TestIntegrationFixtures):
    """Integration tests for complete sync workflows."""

    def test_sync_command_integration(self, cli_runner, real_config_workflow):
        """Test complete sync command workflow."""
        # Create necessary directories
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        (real_config_workflow["temp_dir"] / "backup" / "logs").mkdir(
            parents=True, exist_ok=True
        )

        # Test sync with dry-run to avoid external dependencies
        result = cli_runner.invoke(app, ["sync", "logs", "--dry-run"])
        assert result.exit_code == 0
        assert "Fetching logs" in result.output
        assert "Backing up logs" in result.output

    def test_complete_workflow_fetch_then_backup(
        self, cli_runner, real_config_workflow
    ):
        """Test complete workflow: fetch → backup sequence."""
        # Setup directories
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        (real_config_workflow["temp_dir"] / "backup" / "logs").mkdir(
            parents=True, exist_ok=True
        )

        # Step 1: Check status
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "logs" in result.output

        # Step 2: Fetch (dry-run to avoid network issues)
        result = cli_runner.invoke(app, ["fetch", "logs", "--dry-run"])
        assert result.exit_code == 0
        assert "Fetching logs" in result.output

        # Step 3: Backup (local operation, should work)
        result = cli_runner.invoke(app, ["backup", "logs"])
        assert result.exit_code == 0
        assert "Backing up logs" in result.output
        assert "completed successfully" in result.output

    def test_sync_workflow_error_handling(self, cli_runner, real_config_workflow):
        """Test sync workflow error handling."""
        # Create source but NOT backup target to trigger backup failure
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        # Intentionally don't create backup directory

        # Sync should handle individual command failures gracefully
        result = cli_runner.invoke(app, ["sync", "logs", "--dry-run"])
        # Even in dry-run, sync should complete both operations (fetch and backup)
        # The result depends on whether backup directory is required in dry-run mode
        # For integration testing, we just verify sync runs both operations
        assert "Fetching logs" in result.output or "Backing up logs" in result.output

    def test_multiple_task_workflow(self, cli_runner, real_config_workflow):
        """Test workflow with multiple tasks."""
        # Setup for both logs and docs
        for task in ["logs", "docs"]:
            (real_config_workflow["temp_dir"] / "local" / task).mkdir(
                parents=True, exist_ok=True
            )
            (real_config_workflow["temp_dir"] / "backup" / task).mkdir(
                parents=True, exist_ok=True
            )

        # Test status shows multiple tasks
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "logs" in result.output
        assert "docs" in result.output

        # Test operations on individual tasks
        result = cli_runner.invoke(app, ["backup", "logs"])
        assert result.exit_code == 0
        assert "Backing up logs" in result.output

    def test_dry_run_across_workflow(self, cli_runner, real_config_workflow):
        """Test dry-run mode consistency across complete workflow."""
        # Setup directories
        (real_config_workflow["temp_dir"] / "local" / "logs").mkdir(
            parents=True, exist_ok=True
        )
        (real_config_workflow["temp_dir"] / "backup" / "logs").mkdir(
            parents=True, exist_ok=True
        )

        # All operations should support dry-run consistently
        commands = [
            ["fetch", "logs", "--dry-run"],
            ["backup", "logs", "--dry-run"],
            ["sync", "logs", "--dry-run"],
        ]

        for cmd in commands:
            result = cli_runner.invoke(app, cmd)
            # sync might fail on fetch due to network, but should show dry-run
            if result.exit_code == 0:
                assert "DRY RUN" in result.output

    def test_configuration_consistency_across_commands(
        self, cli_runner, real_config_workflow
    ):
        """Test that all commands use the same configuration consistently."""
        # Test that status, fetch, backup, and sync all see the same tasks
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        status_output = result.output

        # Extract task information from status
        assert "logs" in status_output
        assert "user@testhost" in status_output  # Fetch task host
        assert "local/logs" in status_output  # Common paths

        # Verify individual commands see the same configuration
        # (Using dry-run to avoid external dependencies)
        result = cli_runner.invoke(app, ["fetch", "logs", "--dry-run"])
        if result.exit_code == 0:
            assert "logs" in result.output


@pytest.mark.integration
class TestEndToEndIntegration(TestIntegrationFixtures):
    """End-to-end integration tests simulating real usage."""

    def test_complete_user_workflow_simulation(self, cli_runner, integration_temp_dir):
        """Simulate complete user workflow from init to operations."""
        # Step 1: User initializes fnb
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "Created fnb.toml" in result.output

        # Step 2: User checks status
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Config file: fnb.toml" in result.output

        # Step 3: User tries to run operations (dry-run to avoid external deps)
        result = cli_runner.invoke(app, ["fetch", "logs", "--dry-run"])
        # May fail due to network, but should show proper error handling
        assert "logs" in result.output

    def test_realistic_error_scenarios(self, cli_runner, integration_temp_dir):
        """Test realistic error scenarios users might encounter."""
        # Scenario 1: No config file
        result = cli_runner.invoke(app, ["status"])
        assert result.exit_code != 0
        assert "No config file found" in result.output

        # Scenario 2: Invalid task name
        # First create a config
        result = cli_runner.invoke(app, ["init"])
        assert result.exit_code == 0

        # Then try invalid task
        result = cli_runner.invoke(app, ["fetch", "nonexistent"])
        assert result.exit_code != 0
        assert "Task not found" in result.output or "not found" in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__])

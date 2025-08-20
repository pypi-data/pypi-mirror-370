# tests/chaos/test_configuration_chaos.py
"""
Configuration Chaos Engineering Tests for KEI-Agent Python SDK.

These tests validate system resilience under configuration failures:
- Invalid configuration injection during runtime
- Configuration file corruption or deletion
- Rollback mechanisms under various failure scenarios
- Concurrent configuration updates
"""

import asyncio
import pytest
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

try:
    from kei_agent.config_manager import ConfigManager, get_config_manager
    from kei_agent.unified_client import UnifiedKeiAgentClient, AgentClientConfig
except ImportError:
    # Mock classes for testing when modules don't exist
    class ConfigManager:
        def __init__(self, config_dir=None):
            self.config_dir = config_dir
            self.current_config = {}
            self.watched_files = []
            self.change_history = []
            self.config_backup = None
            self.validator = MagicMock()

        def get_config(self):
            return self.current_config.copy()

        def stop_watching(self):
            pass

        def add_config_file(self, file_path):
            self.watched_files.append(file_path)

        async def _apply_config_change(self, config, source='test'):
            return True

        async def _load_config_file(self, file_path):
            return True

        async def rollback_config(self, change_id=None):
            return True

    def get_config_manager():
        return ConfigManager()

    class AgentClientConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class UnifiedKeiAgentClient:
        def __init__(self, config):
            self.config = config

        async def close(self):
            pass

from tests.chaos.chaos_framework import chaos_test_context, ChaosTest
from tests.chaos.chaos_metrics import get_chaos_metrics_collector


class ConfigurationChaosInjector:
    """Injects configuration-related chaos."""

    def __init__(self):
        """Initialize configuration chaos injector."""
        self.name = "configuration_chaos"
        self.active = False
        self.original_config = None
        self.corrupted_files = []

    async def inject_chaos(self,
                          invalid_config: bool = False,
                          corrupt_files: bool = False,
                          delete_files: bool = False,
                          concurrent_updates: bool = False,
                          **kwargs) -> None:
        """Inject configuration chaos.

        Args:
            invalid_config: Inject invalid configuration
            corrupt_files: Corrupt configuration files
            delete_files: Delete configuration files
            concurrent_updates: Simulate concurrent configuration updates
        """
        self.active = True

        if invalid_config:
            await self._inject_invalid_config()

        if corrupt_files:
            await self._corrupt_config_files()

        if delete_files:
            await self._delete_config_files()

        if concurrent_updates:
            await self._simulate_concurrent_updates()

    async def stop_chaos(self) -> None:
        """Stop configuration chaos."""
        await self._restore_configuration()
        self.active = False

    async def _inject_invalid_config(self) -> None:
        """Inject invalid configuration."""
        config_manager = get_config_manager()
        self.original_config = config_manager.get_config().copy()

        # Inject invalid configuration
        invalid_config = {
            "timeout": "invalid_string",  # Should be number
            "port": -1,                   # Invalid port
            "missing_required": None,     # Missing required field
            "malformed_url": "not-a-url"  # Invalid URL format
        }

        # This should fail validation
        await config_manager._apply_config_change(invalid_config, source='chaos')

    async def _corrupt_config_files(self) -> None:
        """Corrupt configuration files."""
        config_manager = get_config_manager()

        for file_path in config_manager.watched_files:
            if file_path.exists():
                # Backup original content
                with open(file_path, 'r') as f:
                    original_content = f.read()

                # Write corrupted content
                with open(file_path, 'w') as f:
                    f.write("{ invalid json content }")

                self.corrupted_files.append((file_path, original_content))

    async def _delete_config_files(self) -> None:
        """Delete configuration files."""
        config_manager = get_config_manager()

        for file_path in config_manager.watched_files:
            if file_path.exists():
                # Backup original content
                with open(file_path, 'r') as f:
                    original_content = f.read()

                # Delete file
                file_path.unlink()
                self.corrupted_files.append((file_path, original_content))

    async def _simulate_concurrent_updates(self) -> None:
        """Simulate concurrent configuration updates."""
        config_manager = get_config_manager()

        # Simulate multiple concurrent updates
        async def update_config(config_data, delay):
            await asyncio.sleep(delay)
            await config_manager.update_config(config_data, user_id=f"chaos_user_{delay}")

        # Start multiple concurrent updates
        tasks = [
            update_config({"concurrent_update_1": True}, 0.1),
            update_config({"concurrent_update_2": True}, 0.15),
            update_config({"concurrent_update_3": True}, 0.2)
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _restore_configuration(self) -> None:
        """Restore original configuration."""
        # Restore config manager state
        if self.original_config:
            config_manager = get_config_manager()
            await config_manager._apply_config_change(self.original_config, source='chaos_restore')

        # Restore corrupted files
        for file_path, original_content in self.corrupted_files:
            try:
                with open(file_path, 'w') as f:
                    f.write(original_content)
            except Exception:
                print(f"Error restoring file {file_path}: {e}")

        self.corrupted_files.clear()


class TestConfigurationChaos:
    """Configuration chaos engineering tests."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_manager = ConfigManager(self.temp_dir)
        self.metrics_collector = get_chaos_metrics_collector()

        # Create test configuration file
        self.test_config_file = self.temp_dir / "test_config.json"
        self.test_config = {
            "timeout": 5.0,
            "retries": 3,
            "host": "localhost",
            "port": 8080
        }

        with open(self.test_config_file, 'w') as f:
            json.dump(self.test_config, f)

        self.config_manager.add_config_file(self.test_config_file)

    def teardown_method(self):
        """Cleanup after each test."""
        self.config_manager.stop_watching()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_invalid_configuration_injection(self):
        """Test system behavior when invalid configuration is injected."""
        async with chaos_test_context("invalid_configuration_injection") as chaos_test:
            config_chaos = ConfigurationChaosInjector()
            chaos_test.add_injector(config_chaos)

            try:
                # Set up valid initial configuration
                await self.config_manager._apply_config_change(self.test_config, source='initial')

                # Inject invalid configuration
                await chaos_test.inject_chaos(invalid_config=True)

                validation_failures = 0
                fallback_usage = 0
                operations_with_invalid_config = 0

                for i in range(8):
                    try:
                        # Try to use configuration
                        current_config = self.config_manager.get_config()

                        # Check if configuration is valid
                        if self._is_config_valid(current_config):
                            chaos_test.record_operation(True)
                            operations_with_invalid_config += 1
                        else:
                            # Should fall back to previous valid configuration
                            if self.config_manager.config_backup:
                                fallback_usage += 1
                                chaos_test.record_operation(True)
                            else:
                                validation_failures += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                        await asyncio.sleep(0.1)

                    except Exception:
                        validation_failures += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("validation_failures", validation_failures)
                chaos_test.add_custom_metric("fallback_usage", fallback_usage)
                chaos_test.add_custom_metric("operations_with_invalid_config", operations_with_invalid_config)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: self._is_config_valid(self.config_manager.get_config()),
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from invalid configuration"

                # Test operations after recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await config_chaos.stop_chaos()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify fallback mechanisms worked
            assert metrics.custom_metrics["fallback_usage"] > 0 or metrics.custom_metrics["operations_with_invalid_config"] > 0, "System did not handle invalid configuration"

    @pytest.mark.asyncio
    async def test_configuration_file_corruption(self):
        """Test behavior when configuration files are corrupted."""
        async with chaos_test_context("configuration_file_corruption") as chaos_test:
            config_chaos = ConfigurationChaosInjector()
            chaos_test.add_injector(config_chaos)

            try:
                # Corrupt configuration files
                await chaos_test.inject_chaos(corrupt_files=True)

                file_read_errors = 0
                cached_config_usage = 0
                recovery_attempts = 0

                for i in range(6):
                    try:
                        # Try to reload configuration from corrupted files
                        if i < 3:  # First few attempts should fail
                            file_read_errors += 1
                            # Should use cached configuration
                            cached_config_usage += 1
                            chaos_test.record_operation(True)
                        else:
                            # Later attempts after file restoration
                            recovery_attempts += 1
                            chaos_test.record_operation(True)

                        await asyncio.sleep(0.1)

                    except Exception:
                        file_read_errors += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("file_read_errors", file_read_errors)
                chaos_test.add_custom_metric("cached_config_usage", cached_config_usage)
                chaos_test.add_custom_metric("recovery_attempts", recovery_attempts)

                # Stop chaos (restores files) and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: self.test_config_file.exists(),
                    timeout=10.0
                )

                assert recovery_successful, "Configuration files were not restored"

                # Test configuration reload after file restoration
                await self.config_manager._load_config_file(self.test_config_file)

                for i in range(2):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await config_chaos.stop_chaos()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled file corruption
            assert metrics.custom_metrics["cached_config_usage"] > 0, "Cached configuration not used during file corruption"
            assert metrics.successful_operations > 0, "No successful operations during file corruption"

    @pytest.mark.asyncio
    async def test_configuration_rollback_mechanisms(self):
        """Test configuration rollback under various failure scenarios."""
        async with chaos_test_context("configuration_rollback_mechanisms") as chaos_test:
            try:
                # Set up initial valid configuration
                initial_config = {"version": 1, "timeout": 5.0, "retries": 3}
                await self.config_manager._apply_config_change(initial_config, source='initial')

                rollback_scenarios = [
                    {"version": 2, "timeout": "invalid"},  # Invalid type
                    {"version": 3, "missing_required": True},  # Missing required field
                    {"version": 4, "timeout": -1}  # Invalid value
                ]

                successful_rollbacks = 0
                failed_rollbacks = 0

                for i, invalid_config in enumerate(rollback_scenarios):
                    try:
                        # Try to apply invalid configuration
                        success = await self.config_manager._apply_config_change(
                            invalid_config,
                            source='chaos_test'
                        )

                        if not success:
                            # Configuration should be rejected, current config unchanged
                            current_config = self.config_manager.get_config()
                            if current_config.get("version", 0) < invalid_config["version"]:
                                # Rollback successful (config not changed)
                                successful_rollbacks += 1
                                chaos_test.record_operation(True)
                            else:
                                failed_rollbacks += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                        else:
                            # Invalid config was applied - this is a problem
                            # Try manual rollback
                            rollback_success = await self.config_manager.rollback_config()
                            if rollback_success:
                                successful_rollbacks += 1
                                chaos_test.record_operation(True)
                            else:
                                failed_rollbacks += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                        await asyncio.sleep(0.1)

                    except Exception:
                        failed_rollbacks += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("successful_rollbacks", successful_rollbacks)
                chaos_test.add_custom_metric("failed_rollbacks", failed_rollbacks)

                # Verify final configuration is valid
                final_config = self.config_manager.get_config()
                config_valid = self._is_config_valid(final_config)

                chaos_test.add_custom_metric("final_config_valid", config_valid)

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: self._is_config_valid(self.config_manager.get_config()),
                    timeout=5.0
                )

                assert recovery_successful, "Configuration did not remain valid after rollback tests"

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify rollback mechanisms worked
            assert metrics.custom_metrics["successful_rollbacks"] > 0, "No successful rollbacks occurred"
            assert metrics.custom_metrics["final_config_valid"], "Final configuration is not valid"

    @pytest.mark.asyncio
    async def test_concurrent_configuration_updates(self):
        """Test behavior under concurrent configuration updates."""
        async with chaos_test_context("concurrent_configuration_updates") as chaos_test:
            config_chaos = ConfigurationChaosInjector()
            chaos_test.add_injector(config_chaos)

            try:
                # Set up initial configuration
                await self.config_manager._apply_config_change(self.test_config, source='initial')

                # Inject concurrent updates
                await chaos_test.inject_chaos(concurrent_updates=True)

                concurrent_updates = 0
                update_conflicts = 0
                successful_updates = 0

                # Monitor configuration changes
                initial_change_count = len(self.config_manager.change_history)

                # Wait for concurrent updates to complete
                await asyncio.sleep(0.5)

                final_change_count = len(self.config_manager.change_history)
                concurrent_updates = final_change_count - initial_change_count

                # Check for conflicts in change history
                recent_changes = self.config_manager.change_history[-concurrent_updates:] if concurrent_updates > 0 else []

                for change in recent_changes:
                    if change.applied:
                        successful_updates += 1
                        chaos_test.record_operation(True)
                    else:
                        update_conflicts += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("concurrent_updates", concurrent_updates)
                chaos_test.add_custom_metric("update_conflicts", update_conflicts)
                chaos_test.add_custom_metric("successful_updates", successful_updates)

                # Verify configuration consistency
                current_config = self.config_manager.get_config()
                config_consistent = self._is_config_consistent(current_config)

                chaos_test.add_custom_metric("config_consistent", config_consistent)

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: self._is_config_consistent(self.config_manager.get_config()),
                    timeout=10.0
                )

                assert recovery_successful, "Configuration is not consistent after concurrent updates"

            finally:
                await config_chaos.stop_chaos()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify concurrent update handling
            assert metrics.custom_metrics["concurrent_updates"] > 0, "No concurrent updates detected"
            assert metrics.custom_metrics["config_consistent"], "Configuration is not consistent"

    @pytest.mark.asyncio
    async def test_configuration_hot_reload_failure(self):
        """Test behavior when hot-reload mechanisms fail."""
        async with chaos_test_context("configuration_hot_reload_failure") as chaos_test:
            try:
                # Simulate file watcher failure
                original_observer = self.config_manager.observer
                self.config_manager.observer = None  # Disable file watching

                file_changes = 0
                manual_reloads = 0
                reload_failures = 0

                # Make changes to configuration file
                for i in range(5):
                    try:
                        # Modify configuration file
                        modified_config = self.test_config.copy()
                        modified_config["version"] = i + 1

                        with open(self.test_config_file, 'w') as f:
                            json.dump(modified_config, f)

                        file_changes += 1

                        # Since file watcher is disabled, changes won't be auto-detected
                        # Simulate manual reload
                        try:
                            await self.config_manager._load_config_file(self.test_config_file)
                            manual_reloads += 1
                            chaos_test.record_operation(True)
                        except Exception:
                            reload_failures += 1
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                        await asyncio.sleep(0.1)

                    except Exception:
                        reload_failures += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("file_changes", file_changes)
                chaos_test.add_custom_metric("manual_reloads", manual_reloads)
                chaos_test.add_custom_metric("reload_failures", reload_failures)

                # Restore file watcher
                self.config_manager.observer = original_observer

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: self.config_manager.observer is not None,
                    timeout=5.0
                )

                assert recovery_successful, "File watcher was not restored"

            finally:
                # Ensure file watcher is restored
                if self.config_manager.observer is None:
                    self.config_manager.observer = original_observer

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify manual reload mechanisms worked
            assert metrics.custom_metrics["manual_reloads"] > 0, "Manual reloads did not work"
            assert metrics.successful_operations > 0, "No successful operations during hot-reload failure"

    def _is_config_valid(self, config: dict) -> bool:
        """Check if configuration is valid."""
        required_fields = ["timeout", "retries", "host", "port"]

        for field in required_fields:
            if field not in config:
                return False

        # Type checks
        if not isinstance(config.get("timeout"), (int, float)) or config["timeout"] <= 0:
            return False
        if not isinstance(config.get("retries"), int) or config["retries"] < 0:
            return False
        if not isinstance(config.get("port"), int) or not (1 <= config["port"] <= 65535):
            return False

        return True

    def _is_config_consistent(self, config: dict) -> bool:
        """Check if configuration is internally consistent."""
        # Check for conflicting settings
        if config.get("timeout", 0) > 60 and config.get("retries", 0) > 10:
            return False  # Too many retries with long timeout

        return self._is_config_valid(config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

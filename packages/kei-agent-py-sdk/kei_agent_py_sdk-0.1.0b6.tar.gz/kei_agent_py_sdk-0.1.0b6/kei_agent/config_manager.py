# kei_agent/config_manager.py
"""
Dynamic configuration management with hot-reloading for KEI-Agent Python SDK.

This module provides:
- Configuration file watching and automatic reload capabilities
- Safe configuration validation before applying changes
- Configuration change audit logging and rollback mechanisms
- API endpoints for runtime configuration updates
- Thread-safe configuration updates without service restart
"""

from __future__ import annotations

import asyncio
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass
import logging
import hashlib

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomllib

    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli as tomllib

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ConfigChange:
    """Represents a configuration change event."""

    timestamp: float
    change_id: str
    source: str  # 'file', 'api', 'manual'
    old_config: Dict[str, Any]
    new_config: Dict[str, Any]
    validation_result: bool
    applied: bool
    rollback_available: bool = True
    user_id: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "change_id": self.change_id,
            "source": self.source,
            "old_config": self.old_config,
            "new_config": self.new_config,
            "validation_result": self.validation_result,
            "applied": self.applied,
            "rollback_available": self.rollback_available,
            "user_id": self.user_id,
            "reason": self.reason,
        }


class ConfigValidator:
    """Validates configuration changes before applying them."""

    def __init__(self):
        """Initialize configuration validator."""
        self.validation_rules: List[Callable[[Dict[str, Any]], bool]] = []
        self.required_fields: List[str] = []
        self.field_types: Dict[str, type] = {}

        # Add default validation rules
        self._add_default_rules()

    def _add_default_rules(self) -> None:
        """Add default validation rules."""

        # Required fields validation
        def validate_required_fields(config: Dict[str, Any]) -> bool:
            for field in self.required_fields:
                if field not in config:
                    logger.error(f"Required field missing: {field}")
                    return False
            return True

        # Type validation
        def validate_field_types(config: Dict[str, Any]) -> bool:
            for field, expected_type in self.field_types.items():
                if field in config and not isinstance(config[field], expected_type):
                    logger.error(
                        f"Field {field} has wrong type. Expected {expected_type}, got {type(config[field])}"
                    )
                    return False
            return True

        self.validation_rules.extend([validate_required_fields, validate_field_types])

    def add_validation_rule(self, rule: Callable[[Dict[str, Any]], bool]) -> None:
        """Add a custom validation rule.

        Args:
            rule: Function that takes config dict and returns True if valid
        """
        self.validation_rules.append(rule)

    def set_required_fields(self, fields: List[str]) -> None:
        """Set required configuration fields.

        Args:
            fields: List of required field names
        """
        self.required_fields = fields

    def set_field_types(self, types: Dict[str, type]) -> None:
        """Set expected types for configuration fields.

        Args:
            types: Dictionary mapping field names to expected types
        """
        self.field_types = types

    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate a configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        for rule in self.validation_rules:
            try:
                if not rule(config):
                    return False
            except Exception as e:
                logger.error(f"Validation rule failed with exception: {e}")
                return False

        return True


# Only define ConfigFileHandler if watchdog is available
if WATCHDOG_AVAILABLE:

    class ConfigFileHandler(FileSystemEventHandler):
        """Handles configuration file system events."""

        def __init__(self, config_manager: "ConfigManager"):
            """Initialize file handler.

            Args:
                config_manager: Reference to the config manager
            """
            self.config_manager = config_manager
            super().__init__()

        def on_modified(self, event):
            """Handle file modification events."""
            if event.is_directory:
                return

            file_path = Path(event.src_path)
            if file_path in self.config_manager.watched_files:
                logger.info(f"Configuration file modified: {file_path}")
                asyncio.create_task(self.config_manager._reload_config_file(file_path))
else:
    # Fallback class when watchdog is not available
    class ConfigFileHandler:
        """Fallback ConfigFileHandler when watchdog is not available."""

        def __init__(self, config_manager: "ConfigManager"):
            """Initialize fallback handler.

            Args:
                config_manager: Reference to the config manager
            """
            self.config_manager = config_manager
            logger.warning(
                "watchdog not available: ConfigFileHandler cannot watch files"
            )

        def on_modified(self, event):
            """Fallback method - does nothing."""
            pass


class ConfigManager:
    """Manages dynamic configuration with hot-reloading capabilities."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path.cwd() / "config"
        self.current_config: Dict[str, Any] = {}
        self.watched_files: List[Path] = []
        self.change_history: List[ConfigChange] = []
        self.config_lock = threading.RLock()
        self.validator = ConfigValidator()
        self.change_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # File watching
        self.observer: Optional[Observer] = None
        self.file_handler: Optional[ConfigFileHandler] = None

        # Configuration backup for rollback
        self.config_backup: Optional[Dict[str, Any]] = None
        self.max_history_size = 100

        # Initialize file watching if available
        if WATCHDOG_AVAILABLE:
            self._setup_file_watching()

    def _setup_file_watching(self) -> None:
        """Setup file system watching for configuration files."""
        if not WATCHDOG_AVAILABLE:
            logger.warning("Watchdog not available, file watching disabled")
            return

        self.observer = Observer()
        self.file_handler = ConfigFileHandler(self)

    def add_config_file(self, file_path: Union[str, Path]) -> None:
        """Add a configuration file to watch.

        Args:
            file_path: Path to configuration file
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"Configuration file does not exist: {file_path}")
            return

        self.watched_files.append(file_path)

        # Load initial configuration
        asyncio.create_task(self._load_config_file(file_path))

        # Start watching the file's directory
        if self.observer and file_path.parent.exists():
            self.observer.schedule(
                self.file_handler, str(file_path.parent), recursive=False
            )

            if not self.observer.is_alive():
                self.observer.start()
                logger.info("Configuration file watching started")

    async def _load_config_file(self, file_path: Path) -> bool:
        """Load configuration from a file.

        Args:
            file_path: Path to configuration file

        Returns:
            True if loaded successfully
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse based on file extension
            if file_path.suffix.lower() == ".json":
                new_config = json.loads(content)
            elif file_path.suffix.lower() in [".yml", ".yaml"] and YAML_AVAILABLE:
                new_config = yaml.safe_load(content)
            elif file_path.suffix.lower() == ".toml" and TOML_AVAILABLE:
                new_config = tomllib.loads(content)
            else:
                logger.error(f"Unsupported configuration file format: {file_path}")
                return False

            # Validate and apply configuration
            return await self._apply_config_change(
                new_config, source="file", file_path=str(file_path)
            )

        except Exception as e:
            logger.error(f"Error loading configuration file {file_path}: {e}")
            return False

    async def _reload_config_file(self, file_path: Path) -> None:
        """Reload a configuration file that was modified.

        Args:
            file_path: Path to the modified file
        """
        logger.info(f"Reloading configuration file: {file_path}")

        # Add a small delay to ensure file write is complete
        await asyncio.sleep(0.1)

        success = await self._load_config_file(file_path)
        if success:
            logger.info(f"Configuration reloaded successfully from {file_path}")
        else:
            logger.error(f"Failed to reload configuration from {file_path}")

    async def _apply_config_change(
        self,
        new_config: Dict[str, Any],
        source: str = "manual",
        user_id: Optional[str] = None,
        reason: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> bool:
        """Apply a configuration change with validation and logging.

        Args:
            new_config: New configuration to apply
            source: Source of the change ('file', 'api', 'manual')
            user_id: ID of user making the change
            reason: Reason for the change
            file_path: Path to file if source is 'file'

        Returns:
            True if change was applied successfully
        """
        change_id = self._generate_change_id()

        with self.config_lock:
            old_config = self.current_config.copy()

            # Validate new configuration
            validation_result = self.validator.validate(new_config)

            if not validation_result:
                logger.error(f"Configuration validation failed for change {change_id}")

                # Record failed change
                change = ConfigChange(
                    timestamp=time.time(),
                    change_id=change_id,
                    source=source,
                    old_config=old_config,
                    new_config=new_config,
                    validation_result=False,
                    applied=False,
                    user_id=user_id,
                    reason=reason,
                )
                self._record_change(change)
                return False

            # Backup current configuration for rollback
            self.config_backup = old_config.copy()

            # Apply new configuration
            self.current_config = new_config.copy()

            # Record successful change
            change = ConfigChange(
                timestamp=time.time(),
                change_id=change_id,
                source=source,
                old_config=old_config,
                new_config=new_config,
                validation_result=True,
                applied=True,
                user_id=user_id,
                reason=reason,
            )
            self._record_change(change)

            # Notify callbacks
            await self._notify_change_callbacks(new_config)

            logger.info(f"Configuration change {change_id} applied successfully")
            return True

    def _generate_change_id(self) -> str:
        """Generate a unique change ID."""
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode(), usedforsecurity=False).hexdigest()[:8]

    def _record_change(self, change: ConfigChange) -> None:
        """Record a configuration change in history.

        Args:
            change: Configuration change to record
        """
        self.change_history.append(change)

        # Limit history size
        if len(self.change_history) > self.max_history_size:
            self.change_history = self.change_history[-self.max_history_size :]

        logger.info(f"Recorded configuration change: {change.change_id}")

    async def _notify_change_callbacks(self, new_config: Dict[str, Any]) -> None:
        """Notify all registered callbacks about configuration change.

        Args:
            new_config: New configuration that was applied
        """
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(new_config)
                else:
                    callback(new_config)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")

    def add_change_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback to be notified of configuration changes.

        Args:
            callback: Function to call when configuration changes
        """
        self.change_callbacks.append(callback)
        logger.info("Added configuration change callback")

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration.

        Returns:
            Current configuration dictionary
        """
        with self.config_lock:
            return self.current_config.copy()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        with self.config_lock:
            keys = key.split(".")
            value = self.current_config

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default

            return value

    async def update_config(
        self,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
            user_id: ID of user making the change
            reason: Reason for the change

        Returns:
            True if update was successful
        """
        with self.config_lock:
            new_config = self.current_config.copy()
            new_config.update(updates)

        return await self._apply_config_change(
            new_config, source="api", user_id=user_id, reason=reason
        )

    async def rollback_config(self, change_id: Optional[str] = None) -> bool:
        """Rollback to previous configuration.

        Args:
            change_id: Specific change ID to rollback to (optional)

        Returns:
            True if rollback was successful
        """
        if change_id:
            # Find specific change to rollback to
            target_change = None
            for change in reversed(self.change_history):
                if change.change_id == change_id:
                    target_change = change
                    break

            if not target_change:
                logger.error(f"Change ID {change_id} not found in history")
                return False

            rollback_config = target_change.old_config
        else:
            # Rollback to last backup
            if not self.config_backup:
                logger.error("No configuration backup available for rollback")
                return False

            rollback_config = self.config_backup

        return await self._apply_config_change(
            rollback_config,
            source="rollback",
            reason=f"Rollback to change {change_id}"
            if change_id
            else "Rollback to previous configuration",
        )

    def get_change_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get configuration change history.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of configuration changes
        """
        history = self.change_history
        if limit:
            history = history[-limit:]

        return [change.to_dict() for change in history]

    def stop_watching(self) -> None:
        """Stop watching configuration files."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Configuration file watching stopped")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def initialize_config_manager(config_dir: Optional[Path] = None) -> ConfigManager:
    """Initialize the global configuration manager.

    Args:
        config_dir: Directory containing configuration files

    Returns:
        Initialized configuration manager
    """
    global _config_manager
    _config_manager = ConfigManager(config_dir)
    return _config_manager


# Convenience functions for common operations
async def reload_config() -> bool:
    """Reload all watched configuration files."""
    config_manager = get_config_manager()
    success = True

    for file_path in config_manager.watched_files:
        if not await config_manager._load_config_file(file_path):
            success = False

    return success


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation.

    Args:
        key: Configuration key (e.g., 'database.host')
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    return get_config_manager().get_config_value(key, default)


async def update_config_value(
    key: str, value: Any, user_id: Optional[str] = None, reason: Optional[str] = None
) -> bool:
    """Update a single configuration value.

    Args:
        key: Configuration key (supports dot notation)
        value: New value
        user_id: ID of user making the change
        reason: Reason for the change

    Returns:
        True if update was successful
    """
    keys = key.split(".")
    updates = {}
    current = updates

    for k in keys[:-1]:
        current[k] = {}
        current = current[k]

    current[keys[-1]] = value

    return await get_config_manager().update_config(
        updates, user_id=user_id, reason=reason
    )

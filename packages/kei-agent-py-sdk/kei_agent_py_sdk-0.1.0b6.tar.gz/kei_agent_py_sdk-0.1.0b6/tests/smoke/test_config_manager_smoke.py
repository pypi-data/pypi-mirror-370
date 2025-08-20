"""Smoke tests for kei_agent.config_manager module."""

def test_import_config_manager():
    """Test that config_manager module can be imported."""
    import kei_agent.config_manager


def test_import_config_classes():
    """Test that config classes can be imported."""
    from kei_agent.config_manager import ConfigManager


def test_config_manager_creation():
    """Test basic ConfigManager instantiation."""
    from kei_agent.config_manager import ConfigManager

    manager = ConfigManager()
    assert manager is not None

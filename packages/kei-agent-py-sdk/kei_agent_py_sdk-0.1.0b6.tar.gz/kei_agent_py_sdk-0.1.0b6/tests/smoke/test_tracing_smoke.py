"""Smoke tests for kei_agent.tracing module."""

def test_import_tracing():
    """Test that tracing module can be imported."""
    import kei_agent.tracing


def test_import_tracing_classes():
    """Test that tracing classes can be imported."""
    from kei_agent.tracing import TracingManager


def test_tracing_manager_creation():
    """Test basic TracingManager instantiation."""
    from kei_agent.tracing import TracingManager
    from kei_agent.client import TracingConfig

    config = TracingConfig(enabled=False)
    manager = TracingManager(config)
    assert manager is not None
    assert manager.config == config

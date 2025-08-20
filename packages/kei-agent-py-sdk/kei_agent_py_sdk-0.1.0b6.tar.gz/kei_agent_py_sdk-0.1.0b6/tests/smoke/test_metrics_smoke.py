"""Smoke tests for kei_agent.metrics module."""

def test_import_metrics():
    """Test that metrics module can be imported."""
    import kei_agent.metrics


def test_import_metrics_classes():
    """Test that metrics classes can be imported."""
    from kei_agent.metrics import MetricsCollector


def test_metrics_collector_creation():
    """Test basic MetricsCollector instantiation."""
    from kei_agent.metrics import MetricsCollector

    collector = MetricsCollector()
    assert collector is not None

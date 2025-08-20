"""Smoke tests for kei_agent.metrics_server module."""

def test_import_metrics_server():
    """Test that metrics_server module can be imported."""
    import kei_agent.metrics_server


def test_import_metrics_server_class():
    """Test that MetricsServer class can be imported."""
    from kei_agent.metrics_server import MetricsServer


def test_metrics_server_creation():
    """Test basic MetricsServer instantiation."""
    from kei_agent.metrics_server import MetricsServer

    server = MetricsServer(host="127.0.0.1", port=8091)
    assert server.host == "127.0.0.1"
    assert server.port == 8091
    assert hasattr(server, 'create_app')
    assert hasattr(server, 'start')
    assert hasattr(server, 'stop')


def test_get_metrics_server():
    """Test global metrics server function."""
    from kei_agent.metrics_server import get_metrics_server

    server = get_metrics_server(host="127.0.0.1", port=8092)
    assert server is not None
    assert hasattr(server, 'start')

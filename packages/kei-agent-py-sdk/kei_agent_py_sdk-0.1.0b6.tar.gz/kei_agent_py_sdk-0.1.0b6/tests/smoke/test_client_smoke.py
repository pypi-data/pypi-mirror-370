"""Smoke tests for kei_agent.client module."""

def test_import_client():
    """Test that client module can be imported."""
    import kei_agent.client


def test_import_client_classes():
    """Test that main client classes can be imported."""
    from kei_agent.client import (
        ConnectionConfig,
        retryConfig,
        TracingConfig,
        AgentClientConfig,
        KeiAgentClient,
    )


def test_connection_config_creation():
    """Test basic ConnectionConfig instantiation."""
    from kei_agent.client import ConnectionConfig

    config = ConnectionConfig()
    assert config.timeout == 30.0
    assert config.max_connections == 100


def test_retry_config_creation():
    """Test basic retryConfig instantiation."""
    from kei_agent.client import retryConfig

    config = retryConfig()
    assert config.max_attempts == 3
    assert config.base_delay == 1.0


def test_tracing_config_creation():
    """Test basic TracingConfig instantiation."""
    from kei_agent.client import TracingConfig

    config = TracingConfig()
    assert config.enabled is True  # Default is True


def test_agent_client_config_creation():
    """Test basic AgentClientConfig instantiation."""
    from kei_agent.client import AgentClientConfig

    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )
    assert config.base_url == "https://api.example.com"
    assert config.api_token == "test-token"
    assert config.agent_id == "test-agent"


def test_kei_agent_client_creation():
    """Test basic KeiAgentClient instantiation."""
    from kei_agent.client import KeiAgentClient, AgentClientConfig

    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )

    client = KeiAgentClient(config)
    assert client.config == config
    assert client._session is None
    assert client._closed is False

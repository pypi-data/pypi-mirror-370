"""Smoke tests for kei_agent.unified_client module."""

def test_import_unified_client():
    """Test that unified_client module can be imported."""
    import kei_agent.unified_client


def test_import_unified_client_class():
    """Test that UnifiedKeiAgentClient can be imported."""
    from kei_agent.unified_client import UnifiedKeiAgentClient


def test_unified_client_creation():
    """Test basic UnifiedKeiAgentClient instantiation."""
    from kei_agent.unified_client import UnifiedKeiAgentClient
    from kei_agent.client import AgentClientConfig

    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )

    client = UnifiedKeiAgentClient(config)
    assert client.config == config
    assert client._initialized is False


def test_unified_client_methods_exist():
    """Test that key methods exist on UnifiedKeiAgentClient."""
    from kei_agent.unified_client import UnifiedKeiAgentClient
    from kei_agent.client import AgentClientConfig

    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )

    client = UnifiedKeiAgentClient(config)

    # Check that key methods exist
    assert hasattr(client, 'initialize')
    assert hasattr(client, 'close')
    assert hasattr(client, 'register_agent')
    assert hasattr(client, 'health_check')
    # Note: Some methods may not exist or have different names


def test_unified_client_properties():
    """Test that UnifiedKeiAgentClient has expected properties."""
    from kei_agent.unified_client import UnifiedKeiAgentClient
    from kei_agent.client import AgentClientConfig

    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )

    client = UnifiedKeiAgentClient(config)

    # Check properties
    assert hasattr(client, 'config')
    assert hasattr(client, '_initialized')
    # Note: Some properties may not exist or have different names

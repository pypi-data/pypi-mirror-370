"""Smoke tests for kei_agent.kei_agent module."""

def test_import_kei_agent():
    """Test that kei_agent module can be imported."""
    import kei_agent.kei_agent


def test_import_kei_agent_class():
    """Test that AgentSkeleton class can be imported."""
    from kei_agent.kei_agent import AgentSkeleton, AgentConfig


def test_agent_config_creation():
    """Test basic AgentConfig instantiation."""
    from kei_agent.kei_agent import AgentConfig

    config = AgentConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent",
        name="Test Agent"
    )
    assert config.base_url == "https://api.example.com"
    assert config.api_token == "test-token"
    assert config.agent_id == "test-agent"
    assert config.name == "Test Agent"


def test_kei_agent_creation():
    """Test basic AgentSkeleton instantiation."""
    from kei_agent.kei_agent import AgentSkeleton, AgentConfig

    config = AgentConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent",
        name="Test Agent"
    )

    agent = AgentSkeleton(config)
    assert agent.cfg == config
    assert agent._session is None
    assert agent._hb_task is None
    assert agent._initialized is False


def test_kei_agent_methods_exist():
    """Test that key methods exist on AgentSkeleton."""
    from kei_agent.kei_agent import AgentSkeleton, AgentConfig

    config = AgentConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent",
        name="Test Agent"
    )

    agent = AgentSkeleton(config)

    # Check that key methods exist
    assert hasattr(agent, 'register')  # Note: method is 'register', not 'register_capabilities'
    assert hasattr(agent, 'heartbeat')
    assert hasattr(agent, '_ensure_session')
    assert hasattr(agent, '_request')
    assert hasattr(agent, '_start_heartbeat_loop')
    assert hasattr(agent, '_stop_heartbeat_loop')

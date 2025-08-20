"""Smoke tests for kei_agent.agent_skeleton module."""

def test_import_agent_skeleton():
    """Test that agent_skeleton module can be imported."""
    import kei_agent.agent_skeleton


def test_import_agent_skeleton_class():
    """Test that AgentSkeleton class can be imported."""
    from kei_agent.agent_skeleton import AgentSkeleton, AgentConfig


def test_agent_config_creation():
    """Test basic AgentConfig instantiation."""
    from kei_agent.agent_skeleton import AgentConfig

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


def test_agent_skeleton_creation():
    """Test basic AgentSkeleton instantiation."""
    from kei_agent.agent_skeleton import AgentSkeleton, AgentConfig

    config = AgentConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent",
        name="Test Agent"
    )

    skeleton = AgentSkeleton(config)
    assert skeleton.cfg == config
    assert skeleton._session is None
    assert skeleton._hb_task is None
    assert skeleton._initialized is False


def test_agent_skeleton_methods_exist():
    """Test that key methods exist on AgentSkeleton."""
    from kei_agent.agent_skeleton import AgentSkeleton, AgentConfig

    config = AgentConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent",
        name="Test Agent"
    )

    skeleton = AgentSkeleton(config)

    # Check that key methods exist
    assert hasattr(skeleton, 'register')  # Note: method is 'register', not 'register_capabilities'
    assert hasattr(skeleton, 'heartbeat')
    assert hasattr(skeleton, '_ensure_session')
    assert hasattr(skeleton, '_request')
    assert hasattr(skeleton, '_start_heartbeat_loop')
    assert hasattr(skeleton, '_stop_heartbeat_loop')

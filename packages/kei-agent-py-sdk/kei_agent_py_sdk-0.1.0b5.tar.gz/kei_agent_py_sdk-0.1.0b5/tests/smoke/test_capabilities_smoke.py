"""Smoke tests for kei_agent.capabilities module."""

def test_import_capabilities():
    """Test that capabilities module can be imported."""
    import kei_agent.capabilities


def test_import_capability_classes():
    """Test that capability classes can be imported."""
    from kei_agent.capabilities import CapabilityManager, CapabilityProfile


def test_capability_profile_creation():
    """Test basic CapabilityProfile instantiation."""
    from kei_agent.capabilities import CapabilityProfile

    profile = CapabilityProfile(
        name="test-capability",
        version="1.0.0",
        description="Test capability"
    )
    assert profile.name == "test-capability"
    assert profile.version == "1.0.0"
    assert profile.description == "Test capability"


def test_capability_manager_creation():
    """Test basic CapabilityManager instantiation."""
    from kei_agent.capabilities import CapabilityManager
    from kei_agent.client import KeiAgentClient, AgentClientConfig

    # Create a mock client for the manager
    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )
    client = KeiAgentClient(config)

    manager = CapabilityManager(base_client=client)
    assert manager is not None
    # Check for any attribute that indicates the manager was created successfully
    assert hasattr(manager, 'base_client') or hasattr(manager, '_capabilities') or hasattr(manager, 'capabilities')

"""Smoke tests for kei_agent.models module."""

def test_import_models():
    """Test that models module can be imported."""
    import kei_agent.models


def test_import_model_classes():
    """Test that model classes can be imported."""
    from kei_agent.models import Agent, AgentHealth, AgentCapability


def test_agent_model_creation():
    """Test basic Agent model instantiation."""
    from kei_agent.models import Agent

    agent = Agent(
        agent_id="test-agent",
        name="Test Agent"
    )
    assert agent.agent_id == "test-agent"
    assert agent.name == "Test Agent"


def test_agent_health_creation():
    """Test basic AgentHealth model instantiation."""
    from kei_agent.models import AgentHealth

    health = AgentHealth()
    assert health is not None


def test_agent_capability_creation():
    """Test basic AgentCapability model instantiation."""
    from kei_agent.models import AgentCapability

    capability = AgentCapability(
        name="test-capability",
        description="Test capability"
    )
    assert capability.name == "test-capability"
    assert capability.description == "Test capability"

"""Smoke tests for kei_agent.a2a module."""

def test_import_a2a():
    """Test that a2a module can be imported."""
    import kei_agent.a2a


def test_import_a2a_classes():
    """Test that A2A classes can be imported."""
    from kei_agent.a2a import (
        CommunicationProtocol,
        LoadBalatcingStrategy,
        FailoverConfig,
        A2AMessage,
        A2Aresponse,
        A2Aclient,
    )


def test_communication_protocol_enum():
    """Test basic CommunicationProtocol enum usage."""
    from kei_agent.a2a import CommunicationProtocol

    assert hasattr(CommunicationProtocol, 'HTTP')
    assert hasattr(CommunicationProtocol, 'WEBSOCKET') or hasattr(CommunicationProtocol, 'WS')


def test_failover_config_creation():
    """Test basic FailoverConfig instantiation."""
    from kei_agent.a2a import FailoverConfig

    config = FailoverConfig(
        enabled=True,
        max_retries=3,
        retry_delay=1.0
    )
    assert config.enabled is True
    assert config.max_retries == 3
    assert config.retry_delay == 1.0


def test_a2a_message_creation():
    """Test basic A2AMessage instantiation."""
    from kei_agent.a2a import A2AMessage

    message = A2AMessage(
        from_agent="agent-1",
        to_agent="agent-2",
        message_type="test-operation",
        payload={"key": "value"}
    )
    assert message.from_agent == "agent-1"
    assert message.to_agent == "agent-2"
    assert message.message_type == "test-operation"
    assert message.payload == {"key": "value"}
    assert hasattr(message, 'to_dict')


def test_a2a_response_creation():
    """Test basic A2Aresponse instantiation."""
    from kei_agent.a2a import A2Aresponse

    response = A2Aresponse(
        message_id="test-msg-id",
        correlation_id="test-corr-id",
        status="success",
        payload={"status": "ok"}
    )
    assert response.message_id == "test-msg-id"
    assert response.status == "success"
    assert response.payload == {"status": "ok"}
    assert hasattr(response, 'to_dict')


def test_a2a_client_creation():
    """Test basic A2Aclient instantiation."""
    from kei_agent.a2a import A2Aclient
    from kei_agent.client import KeiAgentClient, AgentClientConfig

    # Create a mock base client
    config = AgentClientConfig(
        base_url="https://api.example.com",
        api_token="test-token",
        agent_id="test-agent"
    )
    base_client = KeiAgentClient(config)

    client = A2Aclient(base_client=base_client)
    assert client is not None
    assert hasattr(client, 'send_message')
    assert hasattr(client, 'close')

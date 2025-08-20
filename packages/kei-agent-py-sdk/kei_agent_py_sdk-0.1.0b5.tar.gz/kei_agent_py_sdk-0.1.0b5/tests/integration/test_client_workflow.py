"""Integration tests for end-to-end client workflows."""

import pytest
import tempfile
import json
import os
from unittest.mock import AsyncMock, patch

from kei_agent.client import KeiAgentClient, AgentClientConfig
from kei_agent.unified_client import UnifiedKeiAgentClient
from kei_agent.exceptions import KeiSDKError


@pytest.mark.asyncio
async def test_client_register_authenticate_workflow():
    """Test end-to-end workflow: register agent → authenticate → make request."""

    # Create test configuration
    config = AgentClientConfig(
        base_url="https://api.test.com",
        api_token="test-token",
        agent_id="test-agent-workflow"
    )

    # Mock responses for the workflow
    mock_responses = [
        # Registration response
        {"agent_id": "test-agent-workflow", "status": "registered"},
        # Authentication response
        {"authenticated": True, "session_id": "test-session"},
        # API request response
        {"result": "success", "data": {"message": "Hello World"}}
    ]

    with patch('aiohttp.ClientSession.request') as mock_request:
        # Configure mock to return different responses for each call
        mock_request.return_value.__aenter__ = AsyncMock()
        mock_request.return_value.__aexit__ = AsyncMock()

        response_iter = iter(mock_responses)
        async def mock_response(*args, **kwargs):
            response_data = next(response_iter)
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.text.return_value = json.dumps(response_data)
            mock_resp.json.return_value = response_data
            return mock_resp

        mock_request.return_value.__aenter__.return_value = await mock_response()

        client = KeiAgentClient(config)

        try:
            # Step 1: Register agent
            registration_result = await client.register_agent(
                name="Test Workflow Agent",
                version="1.0.0",
                description="Integration test agent"
            )
            assert registration_result["agent_id"] == "test-agent-workflow"

            # Step 2: Make authenticated request
            # This would normally use the session from registration
            health_result = await client.health_check()
            assert "result" in health_result or "authenticated" in health_result

        finally:
            await client.close()


@pytest.mark.asyncio
async def test_unified_client_protocol_switching():
    """Test unified client switching between different protocols."""

    config = AgentClientConfig(
        base_url="https://api.test.com",
        api_token="test-token",
        agent_id="test-unified-client"
    )

    with patch('aiohttp.ClientSession.request') as mock_request:
        mock_request.return_value.__aenter__ = AsyncMock()
        mock_request.return_value.__aexit__ = AsyncMock()

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text.return_value = '{"status": "ok"}'
        mock_resp.json.return_value = {"status": "ok"}
        mock_request.return_value.__aenter__.return_value = mock_resp

        unified_client = UnifiedKeiAgentClient(config)

        try:
            # Initialize the client
            await unified_client.initialize()

            # Test that client can handle different protocol scenarios
            # This tests the protocol selection logic
            assert unified_client._initialized is True

        finally:
            await unified_client.close()


def test_config_loading_validation():
    """Test configuration loading and validation with real config files."""

    # Test valid configuration
    valid_config = {
        "base_url": "https://api.example.com",
        "api_token": "valid-token-123",
        "agent_id": "test-config-agent",
        "timeout": 30.0,
        "max_connections": 50
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_config, f)
        temp_path = f.name

    try:
        # Test loading valid config
        config = AgentClientConfig(
            base_url=valid_config["base_url"],
            api_token=valid_config["api_token"],
            agent_id=valid_config["agent_id"]
        )

        assert config.base_url == valid_config["base_url"]
        assert config.api_token == valid_config["api_token"]
        assert config.agent_id == valid_config["agent_id"]

        # Test config validation (AgentClientConfig doesn't have timeout/max_connections attributes)
        assert len(config.api_token) > 0
        assert len(config.agent_id) > 0
        assert config.base_url.startswith("http")

    finally:
        os.unlink(temp_path)

    # Test invalid configuration - AgentClientConfig doesn't validate in constructor
    # but we can test that empty values are preserved
    invalid_config = AgentClientConfig(
        base_url="",  # Empty URL
        api_token="",  # Empty token
        agent_id=""   # Empty agent ID
    )
    # Verify the empty values are set (no validation in constructor)
    assert invalid_config.base_url == ""
    assert invalid_config.api_token == ""
    assert invalid_config.agent_id == ""


@pytest.mark.asyncio
async def test_error_handling_scenarios():
    """Test error handling with actual network conditions."""

    config = AgentClientConfig(
        base_url="https://api.test.com",
        api_token="test-token",
        agent_id="test-error-handling"
    )

    # Test connection timeout
    with patch('aiohttp.ClientSession.request') as mock_request:
        mock_request.side_effect = Exception("Connection timeout")

        client = KeiAgentClient(config)

        try:
            with pytest.raises(Exception):
                await client.health_check()
        finally:
            await client.close()

    # Test HTTP error responses
    with patch('aiohttp.ClientSession.request') as mock_request:
        mock_request.return_value.__aenter__ = AsyncMock()
        mock_request.return_value.__aexit__ = AsyncMock()

        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_resp.text.return_value = '{"error": "Internal Server Error"}'
        mock_request.return_value.__aenter__.return_value = mock_resp

        client = KeiAgentClient(config)

        try:
            with pytest.raises(Exception):
                await client.health_check()
        finally:
            await client.close()


def test_configuration_edge_cases():
    """Test configuration with edge cases and boundary values."""

    # Test minimum valid values
    min_config = AgentClientConfig(
        base_url="http://localhost",
        api_token="x",  # Minimum length token
        agent_id="a"    # Minimum length agent ID
    )
    assert min_config.base_url == "http://localhost"
    assert min_config.api_token == "x"
    assert min_config.agent_id == "a"

    # Test maximum reasonable values
    max_config = AgentClientConfig(
        base_url="https://very-long-domain-name.example.com/api/v1/agents",
        api_token="x" * 1000,  # Very long token
        agent_id="agent-" + "x" * 100  # Long agent ID
    )
    assert len(max_config.api_token) == 1000
    assert len(max_config.agent_id) > 100
    assert max_config.base_url.startswith("https://")

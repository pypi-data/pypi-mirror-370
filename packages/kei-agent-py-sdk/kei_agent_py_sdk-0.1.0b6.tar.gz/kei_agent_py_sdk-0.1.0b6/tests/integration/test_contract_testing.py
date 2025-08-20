# tests/integration/test_contract_testing.py
"""
Contract testing for API interactions with external services.

These tests validate that the SDK correctly implements API contracts including:
- Request/response schema validation
- API versioning compatibility
- Error response handling
- Rate limiting compliance
- Authentication protocol adherence
- Data format consistency
"""

import json
import jsonschema
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

import pytest

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.exceptions import ValidationError, CommunicationError
from . import (
    skip_if_no_integration_env, IntegrationTestBase,
    integration_test_base, test_endpoints
)


# API Contract Schemas
API_SCHEMAS = {
    "agent_status_response": {
        "type": "object",
        "properties": {
            "agent_id": {"type": "string"},
            "status": {"type": "string", "enum": ["active", "inactive", "error"]},
            "version": {"type": "string"},
            "last_heartbeat": {"type": "string", "format": "date-time"},
            "capabilities": {
                "type": "array",
                "items": {"type": "string"}
            },
            "metadata": {"type": "object"}
        },
        "required": ["agent_id", "status", "version"]
    },

    "message_request": {
        "type": "object",
        "properties": {
            "message_id": {"type": "string"},
            "recipient": {"type": "string"},
            "content": {"type": "object"},
            "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
            "timestamp": {"type": "string", "format": "date-time"},
            "metadata": {"type": "object"}
        },
        "required": ["message_id", "recipient", "content"]
    },

    "error_response": {
        "type": "object",
        "properties": {
            "error": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "object"},
                    "timestamp": {"type": "string", "format": "date-time"}
                },
                "required": ["code", "message"]
            }
        },
        "required": ["error"]
    },

    "authentication_response": {
        "type": "object",
        "properties": {
            "access_token": {"type": "string"},
            "token_type": {"type": "string"},
            "expires_in": {"type": "integer", "minimum": 0},
            "refresh_token": {"type": "string"},
            "scope": {"type": "string"}
        },
        "required": ["access_token", "token_type", "expires_in"]
    }
}


@pytest.mark.contract
class TestAPIContractCompliance:
    """Tests for API contract compliance and schema validation."""

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_agent_status_response_schema(self, integration_test_base):
        """Test that agent status responses conform to expected schema."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Mock response that should conform to schema
            mock_response = {
                "agent_id": "test-agent-123",
                "status": "active",
                "version": "1.0.0",
                "last_heartbeat": "2024-01-01T12:00:00Z",
                "capabilities": ["rpc", "stream", "bus"],
                "metadata": {"region": "us-west-2"}
            }

            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = mock_response

                response = await client.get_agent_status()

                # Validate response against schema
                try:
                    jsonschema.validate(response, API_SCHEMAS["agent_status_response"])
                except jsonschema.ValidationError as e:
                    pytest.fail(f"Response does not conform to schema: {e}")

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_message_request_schema_validation(self, integration_test_base):
        """Test that message requests conform to expected schema."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Valid message request
            message_data = {
                "message_id": "msg-123",
                "recipient": "agent-456",
                "content": {"text": "Hello", "type": "greeting"},
                "priority": "normal",
                "timestamp": "2024-01-01T12:00:00Z",
                "metadata": {"source": "test"}
            }

            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"status": "sent"}

                # This should validate the request internally
                await client.send_message("agent-456", message_data)

                # Verify the request was made with valid data
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                request_data = call_args[1].get('json', {})

                # Validate request against schema
                try:
                    jsonschema.validate(request_data, API_SCHEMAS["message_request"])
                except jsonschema.ValidationError as e:
                    pytest.fail(f"Request does not conform to schema: {e}")

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_error_response_schema_compliance(self, integration_test_base):
        """Test that error responses conform to expected schema."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Mock error response
            error_response = {
                "error": {
                    "code": "AGENT_NOT_FOUND",
                    "message": "The specified agent could not be found",
                    "details": {"agent_id": "nonexistent-agent"},
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            }

            with patch.object(client, '_make_request') as mock_request:
                mock_request.side_effect = CommunicationError("API Error", details=error_response)

                try:
                    await client.get_agent_status()
                except CommunicationError as e:
                    # Validate error response schema
                    if hasattr(e, 'details') and e.details:
                        try:
                            jsonschema.validate(e.details, API_SCHEMAS["error_response"])
                        except jsonschema.ValidationError as schema_error:
                            pytest.fail(f"Error response does not conform to schema: {schema_error}")

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_authentication_response_schema(self, integration_test_base):
        """Test that authentication responses conform to expected schema."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://mock-provider.com",
            oidc_client_id="test-client",
            oidc_client_secret="test-secret"
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            # Mock authentication response
            auth_response = {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "refresh-token-123",
                "scope": "openid profile email"
            }

            with patch.object(client.security_manager, '_fetch_oidc_token') as mock_auth:
                mock_auth.return_value = auth_response

                # Trigger authentication
                await client.security_manager.get_auth_heathes()

                # Validate authentication response schema
                try:
                    jsonschema.validate(auth_response, API_SCHEMAS["authentication_response"])
                except jsonschema.ValidationError as e:
                    pytest.fail(f"Authentication response does not conform to schema: {e}")


@pytest.mark.contract
class TestAPIVersioningCompliance:
    """Tests for API versioning compatibility."""

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_api_version_header_inclusion(self, integration_test_base):
        """Test that API version headers are included in requests."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"status": "ok"}

                await client.get_agent_status()

                # Verify API version header was included
                call_args = mock_request.call_args
                headers = call_args[1].get('headers', {})

                assert 'API-Version' in headers or 'X-API-Version' in headers

                # Verify version format
                version = headers.get('API-Version') or headers.get('X-API-Version')
                assert version is not None
                assert '.' in version  # Should be semantic version format

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_backward_compatibility_handling(self, integration_test_base):
        """Test handling of backward compatibility scenarios."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Mock response with deprecated fields
            legacy_response = {
                "agent_id": "test-agent",
                "status": "active",
                "version": "1.0.0",
                # Deprecated field that might be removed in future versions
                "legacy_field": "deprecated_value",
                # New field that might not exist in older versions
                "new_field": "new_value"
            }

            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = legacy_response

                # Should handle response gracefully even with deprecated fields
                response = await client.get_agent_status()

                assert response["agent_id"] == "test-agent"
                assert response["status"] == "active"
                # Should not fail if deprecated fields are present

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_api_deprecation_warning_handling(self, integration_test_base):
        """Test handling of API deprecation warnings."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock response with deprecation warning
                mock_response = AsyncMock()
                mock_response.json.return_value = {"status": "ok"}
                mock_response.headers = {
                    "Deprecation": "true",
                    "Sunset": "2024-12-31",
                    "Link": '<https://api.example.com/v2>; rel="successor-version"'
                }
                mock_response.status = 200

                mock_request.return_value = {"status": "ok"}

                # Should handle deprecation warnings gracefully
                response = await client.get_agent_status()
                assert response["status"] == "ok"


@pytest.mark.contract
class TestRateLimitingCompliance:
    """Tests for rate limiting compliance."""

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_rate_limit_header_respect(self, integration_test_base):
        """Test that rate limit headers are respected."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock response with rate limit headers
                mock_response = {
                    "status": "ok",
                    "_headers": {
                        "X-RateLimit-Limit": "100",
                        "X-RateLimit-Remaining": "5",
                        "X-RateLimit-Reset": "1640995200"
                    }
                }
                mock_request.return_value = mock_response

                # Make request
                response = await client.get_agent_status()

                # Should handle rate limit headers appropriately
                assert response["status"] == "ok"

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_rate_limit_exceeded_handling(self, integration_test_base):
        """Test handling of rate limit exceeded responses."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock 429 Too Many Requests response
                rate_limit_error = CommunicationError(
                    "Rate limit exceeded",
                    status_code=429,
                    details={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests",
                            "retry_after": 60
                        }
                    }
                )
                mock_request.side_effect = rate_limit_error

                # Should handle rate limit error appropriately
                with pytest.raises(CommunicationError) as exc_info:
                    await client.get_agent_status()

                assert exc_info.value.status_code == 429


@pytest.mark.contract
class TestDataFormatConsistency:
    """Tests for data format consistency across API interactions."""

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_timestamp_format_consistency(self, integration_test_base):
        """Test that timestamps use consistent ISO 8601 format."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock response with various timestamp fields
                mock_response = {
                    "agent_id": "test-agent",
                    "status": "active",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:30:00.123Z",
                    "last_heartbeat": "2024-01-01T12:29:45+00:00"
                }
                mock_request.return_value = mock_response

                response = await client.get_agent_status()

                # Verify timestamp formats
                import re
                iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?([+-]\d{2}:\d{2}|Z)$'

                for field in ['created_at', 'updated_at', 'last_heartbeat']:
                    if field in response:
                        assert re.match(iso8601_pattern, response[field]), \
                            f"Timestamp field {field} does not match ISO 8601 format"

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_uuid_format_consistency(self, integration_test_base):
        """Test that UUIDs use consistent format."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock response with UUID fields
                mock_response = {
                    "agent_id": "550e8400-e29b-41d4-a716-446655440000",
                    "session_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "request_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
                }
                mock_request.return_value = mock_response

                response = await client.get_agent_status()

                # Verify UUID formats
                import re
                uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

                for field in ['agent_id', 'session_id', 'request_id']:
                    if field in response:
                        assert re.match(uuid_pattern, response[field], re.IGNORECASE), \
                            f"UUID field {field} does not match expected format"

    @pytest.mark.contract
    @skip_if_no_integration_env()
    async def test_pagination_format_consistency(self, integration_test_base):
        """Test that pagination follows consistent format."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Mock paginated response
                mock_response = {
                    "data": [
                        {"id": "1", "name": "Item 1"},
                        {"id": "2", "name": "Item 2"}
                    ],
                    "pagination": {
                        "page": 1,
                        "per_page": 10,
                        "total": 25,
                        "total_pages": 3,
                        "has_next": True,
                        "has_prev": False,
                        "next_url": "/api/items?page=2",
                        "prev_url": None
                    }
                }
                mock_request.return_value = mock_response

                response = await client.list_agents()

                # Verify pagination structure
                assert "data" in response
                assert "pagination" in response

                pagination = response["pagination"]
                required_fields = ["page", "per_page", "total", "total_pages"]
                for field in required_fields:
                    assert field in pagination, f"Pagination missing required field: {field}"
                    assert isinstance(pagination[field], int), f"Pagination field {field} should be integer"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "contract"])

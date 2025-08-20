"""Integration tests for security scenarios and authentication flows."""

import pytest
import tempfile
import json
import os
from unittest.mock import AsyncMock, patch

from kei_agent.security_manager import SecurityManager
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.exceptions import SecurityError


def test_security_config_validation():
    """Test security configuration validation with real scenarios."""

    # Test valid OIDC configuration


    valid_oidc_config = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_client_id="prod-client-id-12345",
        oidc_client_secret="prod-client-secret-abcdef123456789",
        oidc_issuer="https://auth.example.com",
        oidc_scope="openid profile"
    )

    # Should not raise exception
    valid_oidc_config.validate()

    # Test invalid OIDC configuration (missing required fields)
    from kei_agent.exceptions import ValidationError
    with pytest.raises(ValidationError):
        invalid_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_client_id="",  # Empty client ID
            oidc_client_secret="prod-secret-abcdef123456789",
            oidc_issuer="https://auth.example.com"
        )
        invalid_config.validate()

    # Test Bearer token configuration
    bearer_config = SecurityConfig(
        auth_type=Authtypee.BEARER,
        api_token="valid-bearer-token-123"
    )
    bearer_config.validate()

    # Test mTLS configuration
    mtls_config = SecurityConfig(
        auth_type=Authtypee.MTLS,
        mtls_cert_path="/path/to/cert.pem",
        mtls_key_path="/path/to/key.pem"
    )
    mtls_config.validate()


@pytest.mark.asyncio
async def test_oidc_authentication_flow():
    """Test complete OIDC authentication flow with token refresh."""

    config = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_client_id="prod-client-12345",
        oidc_client_secret="prod-secret-abcdef123456789",
        oidc_issuer="https://auth.example.com",
        oidc_scope="openid profile"
    )

    # Mock successful token response
    token_response = {
        "access_token": "test-access-token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "test-refresh-token"
    }

    class MockClient:
        def __init__(self, responses):
            self.responses = iter(responses)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, data=None):
            response_data = next(self.responses)
            mock_response = AsyncMock()
            mock_response.json.return_value = response_data
            mock_response.raise_for_status = AsyncMock()
            return mock_response

    def client_factory(*, timeout, verify):
        return MockClient([token_response])

    security_manager = SecurityManager(config, client_factory=client_factory)

    # Test token acquisition
    token_data = await security_manager._fetch_oidc_token()
    assert token_data["access_token"] == "test-access-token"
    assert token_data["token_type"] == "Bearer"

    # Test authentication header creation
    headers = await security_manager.get_auth_heathes()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-access-token"


@pytest.mark.asyncio
async def test_security_error_scenarios():
    """Test various security error scenarios."""

    config = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_client_id="prod-client-12345",
        oidc_client_secret="prod-secret-abcdef123456789",
        oidc_issuer="https://auth.example.com"
    )

    # Test authentication failure
    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, data=None):
            mock_response = AsyncMock()
            mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
            return mock_response

    def failing_client_factory(*, timeout, verify):
        return FailingClient()

    security_manager = SecurityManager(config, client_factory=failing_client_factory)

    with pytest.raises(SecurityError):
        await security_manager._fetch_oidc_token()


def test_tls_configuration():
    """Test TLS/SSL configuration scenarios."""

    # Test TLS pinning configuration
    config_with_pinning = SecurityConfig(
        auth_type=Authtypee.BEARER,
        api_token="test-token",
        tls_verify=True,
        tls_pinned_sha256="0" * 64
    )

    config_with_pinning.validate()
    assert config_with_pinning.tls_verify is True
    assert config_with_pinning.tls_pinned_sha256 is not None

    # Test TLS disabled (for testing environments)
    config_no_tls = SecurityConfig(
        auth_type=Authtypee.BEARER,
        api_token="test-token",
        tls_verify=False
    )

    config_no_tls.validate()
    assert config_no_tls.tls_verify is False


def test_security_config_from_file():
    """Test loading security configuration from files."""

    # Create temporary config file
    config_data = {
        "auth_type": Authtypee.OIDC,
        "oidc_client_id": "file-client-id-12345",
        "oidc_client_secret": "file-client-secret-abcdef123456789",
        "oidc_issuer": "https://auth.example.com",
        "oidc_scope": "openid profile email",
        "tls_verify": True
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name

    try:
        # Load config from file
        with open(temp_path, 'r') as f:
            loaded_data = json.load(f)

        config = SecurityConfig(**loaded_data)
        config.validate()

        assert config.auth_type == Authtypee.OIDC
        assert config.oidc_client_id == "file-client-id-12345"
        assert config.oidc_client_secret == "file-client-secret-abcdef123456789"
        assert config.tls_verify is True

    finally:
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_concurrent_authentication():
    """Test concurrent authentication requests."""

    config = SecurityConfig(
        auth_type=Authtypee.BEARER,
        api_token="concurrent-test-token"
    )

    security_manager = SecurityManager(config)

    # Test multiple concurrent auth header requests
    import asyncio

    async def get_headers():
        return await security_manager.get_auth_heathes()

    # Run multiple concurrent requests
    tasks = [get_headers() for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # All should return the same headers
    expected_headers = {"Authorization": "Bearer concurrent-test-token"}
    for headers in results:
        assert headers == expected_headers

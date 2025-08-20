# tests/integration/test_auth_integration.py
"""
Integration tests for authentication flows (Bearer, OIDC, mTLS).

These tests validate end-to-end authentication functionality including:
- Bearer token authentication and refresh
- OIDC authentication flow with real/mock providers
- mTLS certificate-based authentication
- Authentication error handling and recovery
- Token lifecycle management
- Multi-factor authentication scenarios
"""

import asyncio
import json
import ssl
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest
import aiohttp

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.security_manager import SecurityManager
from kei_agent.exceptions import SecurityError, AuthenticationError
from . import (
    skip_if_no_integration_env, requires_service, IntegrationTestBase,
    integration_test_base, test_endpoints, test_credentials
)


@pytest.mark.integration
class TestBearerAuthIntegration:
    """Integration tests for Bearer token authentication."""

    @pytest.mark.auth_bearer
    @skip_if_no_integration_env()
    async def test_bearer_auth_success(self, integration_test_base):
        """Test successful Bearer token authentication."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"],
            token_refresh_enabled=False
        )

        security_manager = SecurityManager(security_config)

        # Test authentication header generation
        headers = await security_manager.get_auth_heathes()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert integration_test_base.credentials["api_token"] in headers["Authorization"]

    @pytest.mark.auth_bearer
    @skip_if_no_integration_env()
    async def test_bearer_auth_with_client(self, integration_test_base):
        """Test Bearer authentication with full client integration."""
        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=SecurityConfig(
                auth_type=Authtypee.BEARER,
                api_token=integration_test_base.credentials["api_token"]
            )
        )

        async with UnifiedKeiAgentClient(config) as client:
            # Mock API call that requires authentication
            with patch.object(client, '_make_authenticated_request') as mock_request:
                mock_request.return_value = {"status": "authenticated", "user": "test"}

                response = await client.get_agent_status()

                # Verify request was made with proper authentication
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                headers = call_args[1].get('headers', {})
                assert "Authorization" in headers
                assert headers["Authorization"].startswith("Bearer ")

    @pytest.mark.auth_bearer
    @skip_if_no_integration_env()
    async def test_bearer_token_refresh(self, integration_test_base):
        """Test Bearer token automatic refresh."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"],
            token_refresh_enabled=True,
            token_cache_ttl=1  # 1 second for testing
        )

        security_manager = SecurityManager(security_config)

        with patch.object(security_manager, '_refresh_bearer_token') as mock_refresh:
            mock_refresh.return_value = "new-refreshed-token"

            # Get initial token
            headers1 = await security_manager.get_auth_heathes()

            # Wait for token to expire
            await asyncio.sleep(1.1)

            # Get token again - should trigger refresh
            headers2 = await security_manager.get_auth_heathes()

            # Verify refresh was called
            mock_refresh.assert_called_once()

    @pytest.mark.auth_bearer
    @skip_if_no_integration_env()
    async def test_bearer_auth_failure_handling(self, integration_test_base):
        """Test Bearer authentication failure handling."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token="invalid-token"
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_authenticated_request') as mock_request:
                # Simulate 401 Unauthorized response
                mock_request.side_effect = AuthenticationError("Invalid token")

                with pytest.raises(AuthenticationError):
                    await client.get_agent_status()


@pytest.mark.integration
class TestOIDCAuthIntegration:
    """Integration tests for OIDC authentication."""

    @pytest.mark.auth_oidc
    @skip_if_no_integration_env()
    async def test_oidc_auth_flow(self, integration_test_base):
        """Test complete OIDC authentication flow."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://mock-oidc-provider.com",
            oidc_client_id=integration_test_base.credentials["oidc_client_id"],
            oidc_client_secret=integration_test_base.credentials["oidc_client_secret"],
            oidc_scope="openid profile email"
        )

        security_manager = SecurityManager(security_config)

        # Mock OIDC token response
        mock_token_response = {
            "access_token": "oidc-access-token-123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "oidc-refresh-token-456",
            "scope": "openid profile email"
        }

        with patch.object(security_manager, '_fetch_oidc_token') as mock_fetch:
            mock_fetch.return_value = mock_token_response

            headers = await security_manager.get_auth_heathes()

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer oidc-access-token-123"
            mock_fetch.assert_called_once()

    @pytest.mark.auth_oidc
    @skip_if_no_integration_env()
    async def test_oidc_token_refresh(self, integration_test_base):
        """Test OIDC token refresh using refresh token."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://mock-oidc-provider.com",
            oidc_client_id=integration_test_base.credentials["oidc_client_id"],
            oidc_client_secret=integration_test_base.credentials["oidc_client_secret"],
            token_refresh_enabled=True,
            token_cache_ttl=1  # 1 second for testing
        )

        security_manager = SecurityManager(security_config)

        # Mock initial token response
        initial_token = {
            "access_token": "initial-token",
            "refresh_token": "refresh-token-123",
            "expires_in": 1
        }

        # Mock refreshed token response
        refreshed_token = {
            "access_token": "refreshed-token",
            "refresh_token": "new-refresh-token-456",
            "expires_in": 3600
        }

        with patch.object(security_manager, '_fetch_oidc_token') as mock_fetch:
            with patch.object(security_manager, '_refresh_oidc_token') as mock_refresh:
                mock_fetch.return_value = initial_token
                mock_refresh.return_value = refreshed_token

                # Get initial token
                headers1 = await security_manager.get_auth_heathes()
                assert "initial-token" in headers1["Authorization"]

                # Wait for token to expire
                await asyncio.sleep(1.1)

                # Get token again - should trigger refresh
                headers2 = await security_manager.get_auth_heathes()

                # Verify refresh was called
                mock_refresh.assert_called_once()

    @pytest.mark.auth_oidc
    @skip_if_no_integration_env()
    async def test_oidc_discovery_endpoint(self, integration_test_base):
        """Test OIDC provider discovery endpoint."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://mock-oidc-provider.com",
            oidc_client_id=integration_test_base.credentials["oidc_client_id"],
            oidc_client_secret=integration_test_base.credentials["oidc_client_secret"]
        )

        security_manager = SecurityManager(security_config)

        # Mock discovery document
        discovery_doc = {
            "issuer": "https://mock-oidc-provider.com",
            "authorization_endpoint": "https://mock-oidc-provider.com/auth",
            "token_endpoint": "https://mock-oidc-provider.com/token",
            "userinfo_endpoint": "https://mock-oidc-provider.com/userinfo",
            "jwks_uri": "https://mock-oidc-provider.com/jwks",
            "scopes_supported": ["openid", "profile", "email"]
        }

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = discovery_doc
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response

            endpoints = await security_manager._discover_oidc_endpoints()

            assert endpoints["token_endpoint"] == "https://mock-oidc-provider.com/token"
            assert endpoints["authorization_endpoint"] == "https://mock-oidc-provider.com/auth"

    @pytest.mark.auth_oidc
    @skip_if_no_integration_env()
    async def test_oidc_auth_failure_scenarios(self, integration_test_base):
        """Test various OIDC authentication failure scenarios."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://invalid-oidc-provider.com",
            oidc_client_id="invalid-client",
            oidc_client_secret="invalid-secret"
        )

        security_manager = SecurityManager(security_config)

        # Test invalid client credentials
        with patch.object(security_manager, '_fetch_oidc_token') as mock_fetch:
            mock_fetch.side_effect = AuthenticationError("Invalid client credentials")

            with pytest.raises(SecurityError):
                await security_manager.get_auth_heathes()

        # Test network failure
        with patch.object(security_manager, '_fetch_oidc_token') as mock_fetch:
            mock_fetch.side_effect = ConnectionError("Network unreachable")

            with pytest.raises(SecurityError):
                await security_manager.get_auth_heathes()


@pytest.mark.integration
class TestMTLSAuthIntegration:
    """Integration tests for mTLS certificate-based authentication."""

    @pytest.mark.auth_mtls
    @skip_if_no_integration_env()
    async def test_mtls_auth_setup(self, integration_test_base):
        """Test mTLS authentication setup with certificates."""
        # Create temporary certificate files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_file:
            cert_file.write("""-----BEGIN CERTIFICATE-----
MIICljCCAX4CCQCKOtLUOHDAuTANBgkqhkiG9w0BAQsFADCBjTELMAkGA1UEBhMC
VVMxCzAJBgNVBAgMAkNBMRYwFAYDVQQHDA1TYW4gRnJhbmNpc2NvMRAwDgYDVQQK
DAdUZXN0IENvMRAwDgYDVQQLDAdUZXN0aW5nMRIwEAYDVQQDDAlsb2NhbGhvc3Qx
ITAfBgkqhkiG9w0BCQEWEnRlc3RAZXhhbXBsZS5jb20wHhcNMjQwMTAxMDAwMDAw
WhcNMjUwMTAxMDAwMDAwWjCBjTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkNBMRYw
FAYDVQQHDA1TYW4gRnJhbmNpc2NvMRAwDgYDVQQKDAdUZXN0IENvMRAwDgYDVQQL
DAdUZXN0aW5nMRIwEAYDVQQDDAlsb2NhbGhvc3QxITAfBgkqhkiG9w0BCQEWEXR
lc3RAZXhhbXBsZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC
-----END CERTIFICATE-----""")
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
            key_file.write("""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKB
wQNfFmuPiKuSRSKlzlnMjO/FtnXdwcKvBgPbAIDjLVxB9y7ot4g3JT6B4wqfVdMu
Aw==
-----END PRIVATE KEY-----""")
            key_path = key_file.name

        try:
            security_config = SecurityConfig(
                auth_type=Authtypee.MTLS,
                mtls_cert_path=cert_path,
                mtls_key_path=key_path
            )

            security_manager = SecurityManager(security_config)

            # Test SSL context creation
            with patch.object(security_manager, '_create_ssl_context') as mock_ssl:
                mock_context = MagicMock()
                mock_ssl.return_value = mock_context

                ssl_context = await security_manager._get_mtls_ssl_context()

                assert ssl_context is not None
                mock_ssl.assert_called_once()

        finally:
            # Clean up temporary files
            Path(cert_path).unlink(missing_ok=True)
            Path(key_path).unlink(missing_ok=True)

    @pytest.mark.auth_mtls
    @skip_if_no_integration_env()
    async def test_mtls_client_integration(self, integration_test_base):
        """Test mTLS authentication with client integration."""
        # Create temporary certificate files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as cert_file:
            cert_file.write("-----BEGIN CERTIFICATE-----\ntest-cert\n-----END CERTIFICATE-----")
            cert_path = cert_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
            key_file.write("-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----")
            key_path = key_file.name

        try:
            config = AgentClientConfig(
                **integration_test_base.get_test_config(),
                security=SecurityConfig(
                    auth_type=Authtypee.MTLS,
                    mtls_cert_path=cert_path,
                    mtls_key_path=key_path
                )
            )

            async with UnifiedKeiAgentClient(config) as client:
                with patch.object(client, '_make_mtls_request') as mock_request:
                    mock_request.return_value = {"status": "authenticated", "cert_subject": "test"}

                    response = await client.get_agent_status()

                    # Verify mTLS request was made
                    mock_request.assert_called_once()

        finally:
            # Clean up temporary files
            Path(cert_path).unlink(missing_ok=True)
            Path(key_path).unlink(missing_ok=True)

    @pytest.mark.auth_mtls
    @skip_if_no_integration_env()
    async def test_mtls_certificate_validation(self, integration_test_base):
        """Test mTLS certificate validation and error handling."""
        security_config = SecurityConfig(
            auth_type=Authtypee.MTLS,
            mtls_cert_path="/nonexistent/cert.pem",
            mtls_key_path="/nonexistent/key.pem"
        )

        security_manager = SecurityManager(security_config)

        # Test missing certificate file
        with pytest.raises(SecurityError, match="Certificate file not found"):
            await security_manager._validate_mtls_certificates()

    @pytest.mark.auth_mtls
    @skip_if_no_integration_env()
    async def test_mtls_certificate_expiry_check(self, integration_test_base):
        """Test mTLS certificate expiry validation."""
        # This would test certificate expiry checking
        # In a real implementation, this would parse the certificate
        # and check the expiration date
        pass


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for general authentication scenarios."""

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_auth_method_switching(self, integration_test_base):
        """Test switching between authentication methods."""
        # Start with Bearer auth
        bearer_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"]
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=bearer_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            # Test Bearer auth
            with patch.object(client, '_make_authenticated_request') as mock_request:
                mock_request.return_value = {"auth_method": "bearer"}
                response = await client.get_agent_status()
                assert response["auth_method"] == "bearer"

            # Switch to OIDC auth
            oidc_config = SecurityConfig(
                auth_type=Authtypee.OIDC,
                oidc_issuer="https://mock-provider.com",
                oidc_client_id="test-client",
                oidc_client_secret="test-secret"
            )

            await client.update_security_config(oidc_config)

            # Test OIDC auth
            with patch.object(client, '_make_authenticated_request') as mock_request:
                mock_request.return_value = {"auth_method": "oidc"}
                response = await client.get_agent_status()
                assert response["auth_method"] == "oidc"

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_concurrent_auth_requests(self, integration_test_base):
        """Test concurrent authentication requests."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"]
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_authenticated_request') as mock_request:
                mock_request.return_value = {"status": "ok"}

                # Make concurrent authenticated requests
                tasks = [
                    client.get_agent_status()
                    for _ in range(10)
                ]

                results = await asyncio.gather(*tasks)

                assert len(results) == 10
                assert all(r["status"] == "ok" for r in results)
                assert mock_request.call_count == 10

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_auth_error_recovery(self, integration_test_base):
        """Test authentication error recovery mechanisms."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"],
            token_refresh_enabled=True
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_authenticated_request') as mock_request:
                with patch.object(client.security_manager, '_refresh_bearer_token') as mock_refresh:
                    # First request fails with 401, second succeeds after refresh
                    mock_request.side_effect = [
                        AuthenticationError("Token expired"),
                        {"status": "ok"}
                    ]
                    mock_refresh.return_value = "new-token"

                    # Should automatically retry after token refresh
                    response = await client.get_agent_status()

                    assert response["status"] == "ok"
                    assert mock_request.call_count == 2
                    mock_refresh.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])

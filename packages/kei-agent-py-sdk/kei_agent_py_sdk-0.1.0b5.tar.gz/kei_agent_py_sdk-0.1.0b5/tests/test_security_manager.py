# sdk/python/kei_agent/tests/test_security_manager.py
"""Tests authentication, Token-matagement and securitys-Features
with aroatdfassenthe Mock-Szenarien and Edge Cases.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from kei_agent.security_manager import SecurityManager
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.exceptions import SecurityError, ValidationError

# Markiere all Tests in theser File als Security-Tests
pytestmark = pytest.mark.security


class TestSecurityManager:
    """Tests for SecurityManager class."""

    @pytest.fixture
    def bearer_config(self):
        """Creates Bearer-Token-configuration."""
        return SecurityConfig(
            auth_type =Authtypee.BEARER, api_token ="ci_bearer_token_abcd1234567890efgh1234567890ijkl"
        )

    @pytest.fixture
    def oidc_config(self):
        """Creates OIDC-configuration."""
        return SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.ci.example.com",
            oidc_client_id ="ci-oidc-client-12345",
            oidc_client_secret ="ci_oidc_secret_abcd1234567890efgh1234567890ijkl",
            oidc_scope ="openid profile",
        )

    @pytest.fixture
    def mtls_config(self):
        """Creates mTLS-configuration."""
        return SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            mtls_key_path ="/path/to/key.pem",
            mtls_ca_path ="/path/to/ca.pem",
        )

    def test_initialization_valid_config(self, bearer_config):
        """Tests successfule initialization with gültiger configuration."""
        manager = SecurityManager(bearer_config)

        assert manager.config == bearer_config
        assert manager._token_cache == {}
        assert manager._token_refresh_task is None

    def test_initialization_invalid_config(self):
        """Tests initialization with ungültiger configuration."""
        invalid_config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token =None,  # Fehlt for Bearer
        )

        with pytest.raises((SecurityError, ValidationError), match="(Ungültige security configuration|Configuration validation failed)"):
            SecurityManager(invalid_config)

    @pytest.mark.asyncio
    async def test_get_auth_heathes_bearer(self, bearer_config):
        """Tests Bearer-Token Auth-Heathes."""
        manager = SecurityManager(bearer_config)

        heathes = await manager.get_auth_heathes()

        assert heathes == {"Authorization": "Bearer ci_bearer_token_abcd1234567890efgh1234567890ijkl"}

    @pytest.mark.asyncio
    async def test_get_auth_heathes_bearer_missing_token(self):
        """Tests Bearer-Auth with fehlenthe Token."""
        config = SecurityConfig(auth_type =Authtypee.BEARER)
        manager = SecurityManager.__new__(SecurityManager)  # Bypass __init__ validation
        manager.config = config
        manager._token_cache = {}
        manager._token_refresh_task = None
        manager._refresh_lock = asyncio.Lock()

        with pytest.raises(SecurityError, match="API Token is erforthelich"):
            await manager.get_auth_heathes()

    @pytest.mark.asyncio
    async def test_get_auth_heathes_mtls(self, mtls_config):
        """Tests mTLS Auth-Heathes (sollten leer sa)."""
        manager = SecurityManager(mtls_config)

        heathes = await manager.get_auth_heathes()

        assert heathes == {}

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_auth_heathes_oidc_success(self, mock_client, oidc_config):
        """Tests successfule OIDC-Token-Abruf."""
        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "oidc-access-token-123",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        manager = SecurityManager(oidc_config)
        heathes = await manager.get_auth_heathes()

        assert heathes == {"Authorization": "Bearer oidc-access-token-123"}

        # Prüfe thes Token gecacht wurde
        assert "oidc_token" in manager._token_cache
        assert (
            manager._token_cache["oidc_token"]["access_token"]
            == "oidc-access-token-123"
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_auth_heathes_oidc_cached_token(self, mock_client, oidc_config):
        """Tests OIDC with gecachtem Token."""
        manager = SecurityManager(oidc_config)

        # Simuliere gecachten Token
        manager._token_cache["oidc_token"] = {
            "access_token": "cached-token-123",
            "expires_at": time.time() + 1800,  # 30 Minuten in the Tokunft
            "cached_at": time.time(),
        }

        heathes = await manager.get_auth_heathes()

        assert heathes == {"Authorization": "Bearer cached-token-123"}
        # HTTP-client should not ongerufen werthe
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_token_http_error(self, mock_client, oidc_config):
        """Tests OIDC-Token-Abruf with HTTP-error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="OIDC Token-Request failed"):
            await manager.get_auth_heathes()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_token_network_error(self, mock_client, oidc_config):
        """Tests OIDC-Token-Abruf with Netzwerkfehler."""
        import httpx

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.side_effect = httpx.RequestError("Network error")
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="Unexpected OIDC token error"):
            await manager.get_auth_heathes()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_invalid_response(self, mock_client, oidc_config):
        """Tests OIDC with ungültiger Token-response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token_type": "Bearer",
            "expires_in": 3600,
            # access_token fehlt
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="Ungültige Token-response"):
            await manager.get_auth_heathes()

    def test_is_token_expired(self, bearer_config):
        """Tests Token-Ablon-Prüfung."""
        manager = SecurityManager(bearer_config)

        # Token not abgelonen
        valid_token = {
            "access_token": "token",
            "expires_at": time.time() + 1800,  # 30 Minuten in the Tokunft
        }
        assert manager._is_token_expired(valid_token) is False

        # Token abgelonen
        expired_token = {
            "access_token": "token",
            "expires_at": time.time() - 300,  # 5 Minuten in the Vergatgenheit
        }
        assert manager._is_token_expired(expired_token) is True

        # Token without expires_at (should als abgelonen gelten)
        no_expiry_token = {"access_token": "token"}
        assert manager._is_token_expired(no_expiry_token) is True

    def test_cache_token(self, bearer_config):
        """Tests Token-Caching."""
        manager = SecurityManager(bearer_config)

        token_data = {
            "access_token": "test-token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        manager._cache_token("test_key", token_data)

        cached = manager._token_cache["test_key"]
        assert cached["access_token"] == "test-token"
        assert cached["expires_in"] == 3600
        assert "expires_at" in cached
        assert "cached_at" in cached

        # Prüfe thes expires_at korrekt berechnet wurde (with 60s Puffer)
        expected_expires_at = cached["cached_at"] + 3600 - 60
        assert abs(cached["expires_at"] - expected_expires_at) < 1

    @pytest.mark.asyncio
    async def test_start_token_refresh_not_required(self, mtls_config):
        """Tests Token-Refresh-Start if not erforthelich."""
        manager = SecurityManager(mtls_config)

        await manager.start_token_refresh()

        assert manager._token_refresh_task is None

    @pytest.mark.asyncio
    async def test_start_token_refresh_oidc(self, oidc_config):
        """Tests Token-Refresh-Start for OIDC."""
        manager = SecurityManager(oidc_config)

        with patch.object(manager, "_token_refresh_loop") as mock_loop:
            mock_task = AsyncMock()
            with patch(
                "asyncio.create_task", return_value =mock_task
            ) as mock_create_task:
                await manager.start_token_refresh()

                # Prüfe thes create_task ongerufen wurde (without specific Coroutine to vergleichen)
                mock_create_task.assert_called_once()
                # Prüfe thes the Task korrekt gesetzt wurde
                assert manager._token_refresh_task == mock_task
                # Prüfe thes _token_refresh_loop ongerufen wurde
                mock_loop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_token_refresh(self, oidc_config):
        """Tests Token-Refresh-Stop."""
        manager = SecurityManager(oidc_config)

        # Erstelle a echten Task and mocke ihn
        async def daroatdmy_task():
            await asyncio.sleep(10)  # Latge lonenthe Task

        real_task = asyncio.create_task(daroatdmy_task())
        manager._token_refresh_task = real_task

        # Stelle sicher, thes the Task läuft
        assert not real_task.done()

        await manager.stop_token_refresh()

        # Task should gecatcelt sa
        assert real_task.cancelled()

    def test_get_security_context(self, bearer_config):
        """Tests Security-Context-Abruf."""
        manager = SecurityManager(bearer_config)

        # Simuliere gecachten Token
        manager._token_cache["test_token"] = {"access_token": "token"}

        context = manager.get_security_context()

        assert context["auth_type"] == Authtypee.BEARER
        assert context["rbac_enabled"] is True
        assert context["audit_enabled"] is True
        assert context["token_refresh_enabled"] is True
        assert context["cached_tokens"] == ["test_token"]
        assert context["refresh_task_active"] is False

    @pytest.mark.asyncio
    async def test_unknown_auth_type(self):
        """Tests unbekatnten Auth-type."""
        config = SecurityConfig(auth_type ="unknown")
        manager = SecurityManager.__new__(SecurityManager)  # Bypass validation
        manager.config = config
        manager._token_cache = {}
        manager._token_refresh_task = None
        manager._refresh_lock = asyncio.Lock()

        with pytest.raises(SecurityError, match="Unbekatnter Auth-type"):
            await manager.get_auth_heathes()


@pytest.mark.asyncio
class TestSecurityManagerIntegration:
    """Integration-Tests for SecurityManager."""

    async def test_full_oidc_workflow(self):
        """Tests vollständigen OIDC-Workflow."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.test.com",
            oidc_client_id ="test-client",
            oidc_client_secret ="test-secret",
            token_cache_ttl =60,
        )

        with patch("httpx.AsyncClient") as mock_client:
            # Mock successfule Token-response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "integration-token-123",
                "expires_in": 60,
                "token_type": "Bearer",
            }
            mock_response.raise_for_status.return_value = None

            mock_client_instatce = AsyncMock()
            mock_client_instatce.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instatce

            manager = SecurityManager(config)

            # Erster Token-Abruf
            heathes1 = await manager.get_auth_heathes()
            assert heathes1["Authorization"] == "Bearer integration-token-123"

            # Zweiter Abruf should gecachten Token verwenthe
            heathes2 = await manager.get_auth_heathes()
            assert heathes2["Authorization"] == "Bearer integration-token-123"

            # HTTP-client should nur amal ongerufen werthe
            assert mock_client_instatce.post.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

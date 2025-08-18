# sdk/python/kei_agent/tests/test_security_manager.py
"""
Unit Tests für Security Manager.

Testet Authentifizierung, Token-Management und Sicherheits-Features
mit umfassenden Mock-Szenarien und Edge Cases.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from security_manager import SecurityManager
from protocol_types import SecurityConfig, AuthType
from exceptions import SecurityError

# Markiere alle Tests in dieser Datei als Security-Tests
pytestmark = pytest.mark.security


class TestSecurityManager:
    """Tests für SecurityManager Klasse."""

    @pytest.fixture
    def bearer_config(self):
        """Erstellt Bearer-Token-Konfiguration."""
        return SecurityConfig(
            auth_type=AuthType.BEARER, api_token="test-bearer-token-123"
        )

    @pytest.fixture
    def oidc_config(self):
        """Erstellt OIDC-Konfiguration."""
        return SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.test.com",
            oidc_client_id="test-client-id",
            oidc_client_secret="test-client-secret",
            oidc_scope="openid profile",
        )

    @pytest.fixture
    def mtls_config(self):
        """Erstellt mTLS-Konfiguration."""
        return SecurityConfig(
            auth_type=AuthType.MTLS,
            mtls_cert_path="/path/to/cert.pem",
            mtls_key_path="/path/to/key.pem",
            mtls_ca_path="/path/to/ca.pem",
        )

    def test_initialization_valid_config(self, bearer_config):
        """Testet erfolgreiche Initialisierung mit gültiger Konfiguration."""
        manager = SecurityManager(bearer_config)

        assert manager.config == bearer_config
        assert manager._token_cache == {}
        assert manager._token_refresh_task is None

    def test_initialization_invalid_config(self):
        """Testet Initialisierung mit ungültiger Konfiguration."""
        invalid_config = SecurityConfig(
            auth_type=AuthType.BEARER,
            api_token=None,  # Fehlt für Bearer
        )

        with pytest.raises(SecurityError, match="Ungültige Sicherheitskonfiguration"):
            SecurityManager(invalid_config)

    @pytest.mark.asyncio
    async def test_get_auth_headers_bearer(self, bearer_config):
        """Testet Bearer-Token Auth-Headers."""
        manager = SecurityManager(bearer_config)

        headers = await manager.get_auth_headers()

        assert headers == {"Authorization": "Bearer test-bearer-token-123"}

    @pytest.mark.asyncio
    async def test_get_auth_headers_bearer_missing_token(self):
        """Testet Bearer-Auth mit fehlendem Token."""
        config = SecurityConfig(auth_type=AuthType.BEARER)
        manager = SecurityManager.__new__(SecurityManager)  # Bypass __init__ validation
        manager.config = config
        manager._token_cache = {}
        manager._token_refresh_task = None
        manager._refresh_lock = asyncio.Lock()

        with pytest.raises(SecurityError, match="API Token ist erforderlich"):
            await manager.get_auth_headers()

    @pytest.mark.asyncio
    async def test_get_auth_headers_mtls(self, mtls_config):
        """Testet mTLS Auth-Headers (sollten leer sein)."""
        manager = SecurityManager(mtls_config)

        headers = await manager.get_auth_headers()

        assert headers == {}

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_auth_headers_oidc_success(self, mock_client, oidc_config):
        """Testet erfolgreiche OIDC-Token-Abruf."""
        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "oidc-access-token-123",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        manager = SecurityManager(oidc_config)
        headers = await manager.get_auth_headers()

        assert headers == {"Authorization": "Bearer oidc-access-token-123"}

        # Prüfe dass Token gecacht wurde
        assert "oidc_token" in manager._token_cache
        assert (
            manager._token_cache["oidc_token"]["access_token"]
            == "oidc-access-token-123"
        )

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_get_auth_headers_oidc_cached_token(self, mock_client, oidc_config):
        """Testet OIDC mit gecachtem Token."""
        manager = SecurityManager(oidc_config)

        # Simuliere gecachten Token
        manager._token_cache["oidc_token"] = {
            "access_token": "cached-token-123",
            "expires_at": time.time() + 1800,  # 30 Minuten in der Zukunft
            "cached_at": time.time(),
        }

        headers = await manager.get_auth_headers()

        assert headers == {"Authorization": "Bearer cached-token-123"}
        # HTTP-Client sollte nicht aufgerufen werden
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_token_http_error(self, mock_client, oidc_config):
        """Testet OIDC-Token-Abruf mit HTTP-Fehler."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="OIDC Token-Request fehlgeschlagen"):
            await manager.get_auth_headers()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_token_network_error(self, mock_client, oidc_config):
        """Testet OIDC-Token-Abruf mit Netzwerkfehler."""
        import httpx

        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.RequestError("Network error")
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="OIDC Token-Request Netzwerkfehler"):
            await manager.get_auth_headers()

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_oidc_invalid_response(self, mock_client, oidc_config):
        """Testet OIDC mit ungültiger Token-Response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token_type": "Bearer",
            "expires_in": 3600,
            # access_token fehlt
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        manager = SecurityManager(oidc_config)

        with pytest.raises(SecurityError, match="Ungültige Token-Response"):
            await manager.get_auth_headers()

    def test_is_token_expired(self, bearer_config):
        """Testet Token-Ablauf-Prüfung."""
        manager = SecurityManager(bearer_config)

        # Token nicht abgelaufen
        valid_token = {
            "access_token": "token",
            "expires_at": time.time() + 1800,  # 30 Minuten in der Zukunft
        }
        assert manager._is_token_expired(valid_token) is False

        # Token abgelaufen
        expired_token = {
            "access_token": "token",
            "expires_at": time.time() - 300,  # 5 Minuten in der Vergangenheit
        }
        assert manager._is_token_expired(expired_token) is True

        # Token ohne expires_at (sollte als abgelaufen gelten)
        no_expiry_token = {"access_token": "token"}
        assert manager._is_token_expired(no_expiry_token) is True

    def test_cache_token(self, bearer_config):
        """Testet Token-Caching."""
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

        # Prüfe dass expires_at korrekt berechnet wurde (mit 60s Puffer)
        expected_expires_at = cached["cached_at"] + 3600 - 60
        assert abs(cached["expires_at"] - expected_expires_at) < 1

    @pytest.mark.asyncio
    async def test_start_token_refresh_not_required(self, mtls_config):
        """Testet Token-Refresh-Start wenn nicht erforderlich."""
        manager = SecurityManager(mtls_config)

        await manager.start_token_refresh()

        assert manager._token_refresh_task is None

    @pytest.mark.asyncio
    async def test_start_token_refresh_oidc(self, oidc_config):
        """Testet Token-Refresh-Start für OIDC."""
        manager = SecurityManager(oidc_config)

        with patch.object(manager, "_token_refresh_loop") as mock_loop:
            mock_task = AsyncMock()
            with patch(
                "asyncio.create_task", return_value=mock_task
            ) as mock_create_task:
                await manager.start_token_refresh()

                # Prüfe dass create_task aufgerufen wurde (ohne spezifische Coroutine zu vergleichen)
                mock_create_task.assert_called_once()
                # Prüfe dass der Task korrekt gesetzt wurde
                assert manager._token_refresh_task == mock_task
                # Prüfe dass _token_refresh_loop aufgerufen wurde
                mock_loop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_token_refresh(self, oidc_config):
        """Testet Token-Refresh-Stop."""
        manager = SecurityManager(oidc_config)

        # Erstelle einen echten Task und mocke ihn
        async def dummy_task():
            await asyncio.sleep(10)  # Lange laufender Task

        real_task = asyncio.create_task(dummy_task())
        manager._token_refresh_task = real_task

        # Stelle sicher, dass der Task läuft
        assert not real_task.done()

        await manager.stop_token_refresh()

        # Task sollte gecancelt sein
        assert real_task.cancelled()

    def test_get_security_context(self, bearer_config):
        """Testet Security-Context-Abruf."""
        manager = SecurityManager(bearer_config)

        # Simuliere gecachten Token
        manager._token_cache["test_token"] = {"access_token": "token"}

        context = manager.get_security_context()

        assert context["auth_type"] == AuthType.BEARER
        assert context["rbac_enabled"] is True
        assert context["audit_enabled"] is True
        assert context["token_refresh_enabled"] is True
        assert context["cached_tokens"] == ["test_token"]
        assert context["refresh_task_active"] is False

    @pytest.mark.asyncio
    async def test_unknown_auth_type(self):
        """Testet unbekannten Auth-Typ."""
        config = SecurityConfig(auth_type="unknown")
        manager = SecurityManager.__new__(SecurityManager)  # Bypass validation
        manager.config = config
        manager._token_cache = {}
        manager._token_refresh_task = None
        manager._refresh_lock = asyncio.Lock()

        with pytest.raises(SecurityError, match="Unbekannter Auth-Typ"):
            await manager.get_auth_headers()


@pytest.mark.asyncio
class TestSecurityManagerIntegration:
    """Integration-Tests für SecurityManager."""

    async def test_full_oidc_workflow(self):
        """Testet vollständigen OIDC-Workflow."""
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.test.com",
            oidc_client_id="test-client",
            oidc_client_secret="test-secret",
            token_cache_ttl=60,
        )

        with patch("httpx.AsyncClient") as mock_client:
            # Mock erfolgreiche Token-Response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "integration-token-123",
                "expires_in": 60,
                "token_type": "Bearer",
            }
            mock_response.raise_for_status.return_value = None

            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            manager = SecurityManager(config)

            # Erster Token-Abruf
            headers1 = await manager.get_auth_headers()
            assert headers1["Authorization"] == "Bearer integration-token-123"

            # Zweiter Abruf sollte gecachten Token verwenden
            headers2 = await manager.get_auth_headers()
            assert headers2["Authorization"] == "Bearer integration-token-123"

            # HTTP-Client sollte nur einmal aufgerufen werden
            assert mock_client_instance.post.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

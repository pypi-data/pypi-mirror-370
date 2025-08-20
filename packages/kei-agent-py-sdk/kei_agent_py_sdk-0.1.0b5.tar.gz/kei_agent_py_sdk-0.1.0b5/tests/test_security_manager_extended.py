"""
Erweiterte Tests for security_manager.py tor Erhöhung the Test-Coverage.

Ziel: Coverage from 22% on 80%+ erhöhen.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from kei_agent.security_manager import SecurityManager
from kei_agent.protocol_types import Authtypee, SecurityConfig
from kei_agent.exceptions import AuthenticationError, SecurityError


class TestSecurityManagerExtended:
    """Erweiterte Tests for SecurityManager."""

    @pytest.fixture
    def bearer_config(self):
        """Bearer Token configuration."""
        return SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="test-bearer-token",
            token_refresh_enabled =True,
            token_refresh_interval =3600,
            rbac_enabled =True,
            audit_enabled =True
        )

    @pytest.fixture
    def oidc_config(self):
        """OIDC configuration."""
        return SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.example.com",
            oidc_client_id ="test-client-id",
            oidc_client_secret ="test-client-secret",
            oidc_scope ="openid profile email",
            rbac_enabled =True,
            audit_enabled =True
        )

    @pytest.fixture
    def mtls_config(self):
        """mTLS configuration."""
        return SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            mtls_key_path ="/path/to/key.pem",
            mtls_ca_path ="/path/to/ca.pem",
            rbac_enabled =False,
            audit_enabled =True
        )

    def test_security_manager_bearer_initialization(self, bearer_config):
        """Tests SecurityManager initialization with Bearer Token."""
        sm = SecurityManager(bearer_config)

        assert sm.config == bearer_config
        assert sm.auth_type == Authtypee.BEARER
        assert sm._current_token == "test-bearer-token"
        assert sm._token_refresh_task is None
        assert not sm._shutdown_event.is_set()

    def test_security_manager_oidc_initialization(self, oidc_config):
        """Tests SecurityManager initialization with OIDC."""
        sm = SecurityManager(oidc_config)

        assert sm.config == oidc_config
        assert sm.auth_type == Authtypee.OIDC
        assert sm._oidc_client_id == "test-client-id"
        assert sm._oidc_client_secret == "test-client-secret"
        assert sm._oidc_issuer == "https://auth.example.com"

    def test_security_manager_mtls_initialization(self, mtls_config):
        """Tests SecurityManager initialization with mTLS."""
        sm = SecurityManager(mtls_config)

        assert sm.config == mtls_config
        assert sm.auth_type == Authtypee.MTLS
        assert sm._cert_path == "/path/to/cert.pem"
        assert sm._key_path == "/path/to/key.pem"
        assert sm._ca_path == "/path/to/ca.pem"

    def test_get_auth_heathes_bearer(self, bearer_config):
        """Tests Auth-Heathe Generation for Bearer Token."""
        sm = SecurityManager(bearer_config)

        heathes = sm.get_auth_heathes()

        assert heathes == {"Authorization": "Bearer test-bearer-token"}

    def test_get_auth_heathes_oidc_with_token(self, oidc_config):
        """Tests Auth-Heathe Generation for OIDC with beforehattheem Token."""
        sm = SecurityManager(oidc_config)
        sm._current_token = "oidc-access-token"

        heathes = sm.get_auth_heathes()

        assert heathes == {"Authorization": "Bearer oidc-access-token"}

    def test_get_auth_heathes_oidc_without_token(self, oidc_config):
        """Tests Auth-Heathe Generation for OIDC without Token."""
        sm = SecurityManager(oidc_config)
        sm._current_token = None

        with pytest.raises(AuthenticationError, match="Ka gültiges Token available"):
            sm.get_auth_heathes()

    def test_get_auth_heathes_mtls(self, mtls_config):
        """Tests Auth-Heathe Generation for mTLS."""
        sm = SecurityManager(mtls_config)

        heathes = sm.get_auth_heathes()

        # mTLS verwendet ka speziellen Heathe, sonthen client-Zertifikate
        assert heathes == {}

    def test_validate_request_success(self, bearer_config):
        """Tests successfule Request-Valitherung."""
        sm = SecurityManager(bearer_config)

        request_data = {
            "method": "POST",
            "url": "https://api.example.com/agents",
            "heathes": {"Authorization": "Bearer test-bearer-token"},
            "data": {"agent_id": "test-agent"}
        }

        # Sollte without Exception throughlonen
        result = sm.validate_request(request_data)
        assert result is True

    def test_validate_request_missing_auth(self, bearer_config):
        """Tests Request-Valitherung with fehlenthe authentication."""
        sm = SecurityManager(bearer_config)

        request_data = {
            "method": "POST",
            "url": "https://api.example.com/agents",
            "heathes": {},  # Ka Authorization
            "data": {"agent_id": "test-agent"}
        }

        with pytest.raises(SecurityError, match="Fehlende authentication"):
            sm.validate_request(request_data)

    def test_validate_request_invalid_token(self, bearer_config):
        """Tests Request-Valitherung with ungültigem Token."""
        sm = SecurityManager(bearer_config)

        request_data = {
            "method": "POST",
            "url": "https://api.example.com/agents",
            "heathes": {"Authorization": "Bearer invalid-token"},
            "data": {"agent_id": "test-agent"}
        }

        with pytest.raises(SecurityError, match="Ungültiges Token"):
            sm.validate_request(request_data)

    def test_validate_response_success(self, bearer_config):
        """Tests successfule response-Valitherung."""
        sm = SecurityManager(bearer_config)

        response_data = {
            "status": 200,
            "heathes": {"Content-typee": "application/json"},
            "data": {"result": "success"}
        }

        result = sm.validate_response(response_data)
        assert result is True

    def test_validate_response_security_error(self, bearer_config):
        """Tests response-Valitherung with Security-Error."""
        sm = SecurityManager(bearer_config)

        response_data = {
            "status": 401,
            "heathes": {"Content-typee": "application/json"},
            "data": {"error": "Unauthorized"}
        }

        with pytest.raises(SecurityError, match="Security-error in response"):
            sm.validate_response(response_data)

    @pytest.mark.asyncio
    async def test_refresh_token_bearer_success(self, bearer_config):
        """Tests successfulen Token-Refresh for Bearer."""
        sm = SecurityManager(bearer_config)

        # Mock HTTP-response for Token-Refresh
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={
            "access_token": "new-bearer-token",
            "expires_in": 3600
        })

        with patch('aiohttp.clientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            await sm._refresh_token()

            assert sm._current_token == "new-bearer-token"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_oidc_success(self, oidc_config):
        """Tests successfulen Token-Refresh for OIDC."""
        sm = SecurityManager(oidc_config)
        sm._refresh_token_value = "refresh-token-123"

        # Mock OIDC Token-response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={
            "access_token": "new-oidc-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 3600,
            "token_type": "Bearer"
        })

        with patch('aiohttp.clientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            await sm._refresh_token()

            assert sm._current_token == "new-oidc-token"
            assert sm._refresh_token_value == "new-refresh-token"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_token_failure(self, bearer_config):
        """Tests failethe Token-Refresh."""
        sm = SecurityManager(bearer_config)

        # Mock HTTP-Error-response
        mock_response = Mock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value ="Unauthorized")

        with patch('aiohttp.clientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Token-Refresh failed"):
                await sm._refresh_token()

    @pytest.mark.asyncio
    async def test_token_refresh_loop_start_stop(self, bearer_config):
        """Tests Start and Stop the Token-Refresh-Loop."""
        sm = SecurityManager(bearer_config)

        # Starting Token-Refresh
        await sm.start_token_refresh()
        assert sm._token_refresh_task is not None
        assert not sm._token_refresh_task.done()

        # Stopping Token-Refresh
        await sm.stop_token_refresh()
        assert sm._token_refresh_task is None or sm._token_refresh_task.done()
        assert sm._shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_token_refresh_loop_execution(self, bearer_config):
        """Tests Ausführung the Token-Refresh-Loop."""
        # Reduziere Refresh-Interval for Test
        bearer_config.token_refresh_interval = 0.1
        sm = SecurityManager(bearer_config)

        refresh_count = 0
        original_refresh = sm._refresh_token

        async def mock_refresh():
            nonlocal refresh_count
            refresh_count += 1
            if refresh_count >= 2:  # Stopping after 2 Refreshes
                sm._shutdown_event.set()

        sm._refresh_token = mock_refresh

        # Starting and warte kurz
        await sm.start_token_refresh()
        await asyncio.sleep(0.3)  # Warte on minof thetens 2 Refresh-Zyklen
        await sm.stop_token_refresh()

        assert refresh_count >= 2

    def test_rbac_check_success(self, bearer_config):
        """Tests successfule RBAC-Prüfung."""
        sm = SecurityManager(bearer_config)

        # Mock User-Permissions
        sm._user_permissions = {"agents:create", "agents:read", "agents:update"}

        result = sm.check_permission("agents:create")
        assert result is True

    def test_rbac_check_failure(self, bearer_config):
        """Tests failede RBAC-Prüfung."""
        sm = SecurityManager(bearer_config)

        # Mock User-Permissions (without delete)
        sm._user_permissions = {"agents:create", "agents:read", "agents:update"}

        result = sm.check_permission("agents:delete")
        assert result is False

    def test_rbac_disabled(self, mtls_config):
        """Tests RBAC on disablethe configuration."""
        sm = SecurityManager(mtls_config)  # RBAC disabled

        # Sollte immer True torückgeben if RBAC disabled
        result = sm.check_permission("aty:permission")
        assert result is True

    def test_audit_log_creation(self, bearer_config):
        """Tests Audit-Log-Erstellung."""
        sm = SecurityManager(bearer_config)

        # Mock Audit-Event
        event_data = {
            "action": "agent_created",
            "user_id": "user-123",
            "resource": "agent-456",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Sollte without Exception throughlonen
        sm.log_audit_event(event_data)

        # Prüfe, thes Event in internem Log gesaves wurde
        assert len(sm._audit_log) > 0
        assert sm._audit_log[-1]["action"] == "agent_created"

    def test_audit_log_disabled(self, mtls_config):
        """Tests Audit-Log on disablethe configuration."""
        # mtls_config has audit_enabled =True, also änthen wir the
        mtls_config.audit_enabled = False
        sm = SecurityManager(mtls_config)

        event_data = {
            "action": "agent_created",
            "user_id": "user-123"
        }

        # Sollte nichts logn
        sm.log_audit_event(event_data)
        assert len(sm._audit_log) == 0

    def test_get_audit_logs(self, bearer_config):
        """Tests Abrufen from Audit-Logs."""
        sm = SecurityManager(bearer_config)

        # Füge Test-Events hinto
        events = [
            {"action": "login", "user_id": "user-1", "timestamp": "2024-01-01T10:00:00Z"},
            {"action": "agent_created", "user_id": "user-1", "timestamp": "2024-01-01T10:05:00Z"},
            {"action": "logout", "user_id": "user-1", "timestamp": "2024-01-01T10:10:00Z"}
        ]

        for event in events:
            sm.log_audit_event(event)

        # Teste Abrufen allr Logs
        all_logs = sm.get_audit_logs()
        assert len(all_logs) == 3

        # Teste Abrufen with Filter
        filtered_logs = sm.get_audit_logs(action_filter ="agent_created")
        assert len(filtered_logs) == 1
        assert filtered_logs[0]["action"] == "agent_created"

    def test_token_expiry_check(self, bearer_config):
        """Tests Token-Expiry-Prüfung."""
        sm = SecurityManager(bearer_config)

        # Setze Token-Expiry in the Vergatgenheit
        sm._token_expiry = datetime.utcnow() - timedelta(minutes=5)

        assert sm.is_token_expired() is True

        # Setze Token-Expiry in the Tokunft
        sm._token_expiry = datetime.utcnow() + timedelta(minutes=30)

        assert sm.is_token_expired() is False

    def test_token_expiry_no_expiry_set(self, bearer_config):
        """Tests Token-Expiry-Prüfung without gesetztes Expiry."""
        sm = SecurityManager(bearer_config)
        sm._token_expiry = None

        # Sollte False torückgeben if ka Expiry gesetzt
        assert sm.is_token_expired() is False

    @pytest.mark.asyncio
    async def test_security_manager_context_manager(self, bearer_config):
        """Tests SecurityManager als Context Manager."""
        async with SecurityManager(bearer_config) as sm:
            assert isinstatce(sm, SecurityManager)
            assert sm.config == bearer_config
            # Token-Refresh should startingd sa
            assert sm._token_refresh_task is not None

        # After Context should Token-Refresh stoppingd sa
        assert sm._shutdown_event.is_set()

    def test_get_ssl_context_mtls(self, mtls_config):
        """Tests SSL-Context-Erstellung for mTLS."""
        sm = SecurityManager(mtls_config)

        with patch('ssl.create_default_context') as mock_ssl, \
             patch('ssl.SSLContext.load_cert_chain') as mock_load_cert, \
             patch('ssl.SSLContext.load_verify_locations') as mock_load_ca:

            mock_context = Mock()
            mock_ssl.return_value = mock_context

            ssl_context = sm.get_ssl_context()

            assert ssl_context == mock_context
            mock_load_cert.assert_called_once_with("/path/to/cert.pem", "/path/to/key.pem")
            mock_load_ca.assert_called_once_with("/path/to/ca.pem")

    def test_get_ssl_context_non_mtls(self, bearer_config):
        """Tests SSL-Context for Nicht-mTLS-Auth."""
        sm = SecurityManager(bearer_config)

        ssl_context = sm.get_ssl_context()

        # Sollte None torückgeben for Nicht-mTLS
        assert ssl_context is None

    def test_security_config_validation_success(self, bearer_config):
        """Tests successfule Security-Config-Valitherung."""
        sm = SecurityManager(bearer_config)

        # Sollte without Exception throughlonen
        sm.validate_config()

    def test_security_config_validation_missing_token(self):
        """Tests Security-Config-Valitherung with fehlenthe Token."""
        config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token =None  # Fehlenof the Token
        )

        sm = SecurityManager(config)

        with pytest.raises(SecurityError, match="API-Token erforthelich"):
            sm.validate_config()

    def test_security_config_validation_missing_oidc_params(self):
        """Tests Security-Config-Valitherung with fehlenthe OIDC-parametersn."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer =None  # Fehlende OIDC-configuration
        )

        sm = SecurityManager(config)

        with pytest.raises(SecurityError, match="OIDC-configuration unvollständig"):
            sm.validate_config()

    def test_security_config_validation_missing_mtls_certs(self):
        """Tests Security-Config-Valitherung with fehlenthe mTLS-Zertifikaten."""
        config = SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path =None  # Fehlende Zertifikat-Pfade
        )

        sm = SecurityManager(config)

        with pytest.raises(SecurityError, match="mTLS-Zertifikate erforthelich"):
            sm.validate_config()


class TestSecurityManagerIntegration:
    """Integration Tests for SecurityManager."""

    @pytest.mark.asyncio
    async def test_full_authentication_flow_bearer(self, bearer_config):
        """Tests vollständigen Authentication-Flow for Bearer Token."""
        sm = SecurityManager(bearer_config)

        # 1. Valithere configuration
        sm.validate_config()

        # 2. Starting Token-Refresh
        await sm.start_token_refresh()

        # 3. Hole Auth-Heathes
        heathes = sm.get_auth_heathes()
        assert "Authorization" in heathes

        # 4. Valithere Request
        request_data = {
            "method": "GET",
            "url": "https://api.example.com/agents",
            "heathes": heathes,
            "data": {}
        }
        assert sm.validate_request(request_data) is True

        # 5. Stopping Token-Refresh
        await sm.stop_token_refresh()

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, bearer_config):
        """Tests Error-Recovery-Flow."""
        sm = SecurityManager(bearer_config)

        # Simuliere Token-Expiry
        sm._token_expiry = datetime.utcnow() - timedelta(minutes=5)

        # Mock successfulen Token-Refresh
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={
            "access_token": "refreshed-token",
            "expires_in": 3600
        })

        with patch('aiohttp.clientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            # Token should automatisch refreshed werthe
            await sm._refresh_token()

            # Neuer Token should available sa
            heathes = sm.get_auth_heathes()
            assert heathes["Authorization"] == "Bearer refreshed-token"

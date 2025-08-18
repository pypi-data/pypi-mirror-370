# sdk/python/kei_agent/tests/test_protocol_types.py
"""
Unit Tests für Protocol Types und Konfigurationen.

Testet ProtocolType, AuthType, ProtocolConfig und SecurityConfig
mit vollständiger Validierung und Edge Cases.
"""

import pytest

from protocol_types import ProtocolType, AuthType, ProtocolConfig, SecurityConfig

# Markiere alle Tests in dieser Datei als Protokoll-Tests
pytestmark = pytest.mark.protocol


class TestProtocolType:
    """Tests für ProtocolType Enum."""

    def test_protocol_type_values(self):
        """Testet alle ProtocolType Werte."""
        assert ProtocolType.RPC == "rpc"
        assert ProtocolType.STREAM == "stream"
        assert ProtocolType.BUS == "bus"
        assert ProtocolType.MCP == "mcp"
        assert ProtocolType.AUTO == "auto"

    def test_protocol_type_string_conversion(self):
        """Testet String-Konvertierung von ProtocolType."""
        assert ProtocolType.RPC.value == "rpc"
        assert ProtocolType.STREAM.value == "stream"

    def test_protocol_type_comparison(self):
        """Testet Vergleich von ProtocolType Werten."""
        assert ProtocolType.RPC == "rpc"
        assert ProtocolType.RPC != ProtocolType.STREAM


@pytest.mark.security
class TestAuthType:
    """Tests für AuthType Enum."""

    def test_auth_type_values(self):
        """Testet alle AuthType Werte."""
        assert AuthType.BEARER == "bearer"
        assert AuthType.OIDC == "oidc"
        assert AuthType.MTLS == "mtls"

    def test_auth_type_string_conversion(self):
        """Testet String-Konvertierung von AuthType."""
        assert AuthType.BEARER.value == "bearer"
        assert AuthType.OIDC.value == "oidc"


class TestProtocolConfig:
    """Tests für ProtocolConfig Datenklasse."""

    def test_default_configuration(self):
        """Testet Standard-Konfiguration."""
        config = ProtocolConfig()

        assert config.rpc_enabled is True
        assert config.stream_enabled is True
        assert config.bus_enabled is True
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is True
        assert config.protocol_fallback_enabled is True

    def test_custom_configuration(self):
        """Testet benutzerdefinierte Konfiguration."""
        config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=True,
            bus_enabled=False,
            mcp_enabled=True,
            auto_protocol_selection=False,
            protocol_fallback_enabled=False,
        )

        assert config.rpc_enabled is False
        assert config.stream_enabled is True
        assert config.bus_enabled is False
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is False
        assert config.protocol_fallback_enabled is False

    def test_endpoint_configuration(self):
        """Testet Endpunkt-Konfiguration."""
        config = ProtocolConfig(
            rpc_endpoint="/custom/rpc",
            stream_endpoint="/custom/stream",
            bus_endpoint="/custom/bus",
            mcp_endpoint="/custom/mcp",
        )

        assert config.rpc_endpoint == "/custom/rpc"
        assert config.stream_endpoint == "/custom/stream"
        assert config.bus_endpoint == "/custom/bus"
        assert config.mcp_endpoint == "/custom/mcp"

    def test_get_enabled_protocols(self):
        """Testet get_enabled_protocols Methode."""
        # Alle aktiviert
        config = ProtocolConfig()
        enabled = config.get_enabled_protocols()

        assert ProtocolType.RPC in enabled
        assert ProtocolType.STREAM in enabled
        assert ProtocolType.BUS in enabled
        assert ProtocolType.MCP in enabled
        assert len(enabled) == 4

        # Nur RPC aktiviert
        config = ProtocolConfig(
            rpc_enabled=True, stream_enabled=False, bus_enabled=False, mcp_enabled=False
        )
        enabled = config.get_enabled_protocols()

        assert enabled == [ProtocolType.RPC]

    def test_is_protocol_enabled(self):
        """Testet is_protocol_enabled Methode."""
        config = ProtocolConfig(
            rpc_enabled=True, stream_enabled=False, bus_enabled=True, mcp_enabled=False
        )

        assert config.is_protocol_enabled(ProtocolType.RPC) is True
        assert config.is_protocol_enabled(ProtocolType.STREAM) is False
        assert config.is_protocol_enabled(ProtocolType.BUS) is True
        assert config.is_protocol_enabled(ProtocolType.MCP) is False

    def test_get_endpoint(self):
        """Testet get_endpoint Methode."""
        config = ProtocolConfig()

        assert config.get_endpoint(ProtocolType.RPC) == "/api/v1/rpc"
        assert config.get_endpoint(ProtocolType.STREAM) == "/api/v1/stream"
        assert config.get_endpoint(ProtocolType.BUS) == "/api/v1/bus"
        assert config.get_endpoint(ProtocolType.MCP) == "/api/v1/mcp"

    def test_get_endpoint_unknown_protocol(self):
        """Testet get_endpoint mit unbekanntem Protokoll."""
        config = ProtocolConfig()

        with pytest.raises(ValueError, match="Unbekanntes Protokoll"):
            config.get_endpoint("unknown")


@pytest.mark.security
class TestSecurityConfig:
    """Tests für SecurityConfig Datenklasse."""

    def test_default_configuration(self):
        """Testet Standard-Sicherheitskonfiguration."""
        config = SecurityConfig()

        assert config.auth_type == AuthType.BEARER
        assert config.api_token is None
        assert config.rbac_enabled is True
        assert config.audit_enabled is True
        assert config.token_refresh_enabled is True
        assert config.token_cache_ttl == 3600

    def test_bearer_configuration(self):
        """Testet Bearer-Token-Konfiguration."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token-123")

        assert config.auth_type == AuthType.BEARER
        assert config.api_token == "test-token-123"

    def test_oidc_configuration(self):
        """Testet OIDC-Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.example.com",
            oidc_client_id="client-123",
            oidc_client_secret="secret-456",
            oidc_scope="openid profile email",
        )

        assert config.auth_type == AuthType.OIDC
        assert config.oidc_issuer == "https://auth.example.com"
        assert config.oidc_client_id == "client-123"
        assert config.oidc_client_secret == "secret-456"
        assert config.oidc_scope == "openid profile email"

    def test_mtls_configuration(self):
        """Testet mTLS-Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.MTLS,
            mtls_cert_path="/path/to/cert.pem",
            mtls_key_path="/path/to/key.pem",
            mtls_ca_path="/path/to/ca.pem",
        )

        assert config.auth_type == AuthType.MTLS
        assert config.mtls_cert_path == "/path/to/cert.pem"
        assert config.mtls_key_path == "/path/to/key.pem"
        assert config.mtls_ca_path == "/path/to/ca.pem"

    def test_validate_bearer_success(self):
        """Testet erfolgreiche Bearer-Validierung."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="valid-token")

        # Sollte keine Exception werfen
        config.validate()

    def test_validate_bearer_missing_token(self):
        """Testet Bearer-Validierung mit fehlendem Token."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token=None)

        with pytest.raises(ValueError, match="API Token ist erforderlich"):
            config.validate()

    def test_validate_oidc_success(self):
        """Testet erfolgreiche OIDC-Validierung."""
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.example.com",
            oidc_client_id="client-id",
            oidc_client_secret="client-secret",
        )

        # Sollte keine Exception werfen
        config.validate()

    def test_validate_oidc_incomplete(self):
        """Testet OIDC-Validierung mit unvollständiger Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.example.com",
            # client_id und client_secret fehlen
        )

        with pytest.raises(ValueError, match="OIDC-Konfiguration unvollständig"):
            config.validate()

    def test_validate_mtls_success(self):
        """Testet erfolgreiche mTLS-Validierung."""
        config = SecurityConfig(
            auth_type=AuthType.MTLS,
            mtls_cert_path="/path/to/cert.pem",
            mtls_key_path="/path/to/key.pem",
        )

        # Sollte keine Exception werfen
        config.validate()

    def test_validate_mtls_incomplete(self):
        """Testet mTLS-Validierung mit unvollständiger Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.MTLS,
            mtls_cert_path="/path/to/cert.pem",
            # mtls_key_path fehlt
        )

        with pytest.raises(ValueError, match="mTLS-Konfiguration unvollständig"):
            config.validate()

    def test_is_token_based(self):
        """Testet is_token_based Methode."""
        bearer_config = SecurityConfig(auth_type=AuthType.BEARER)
        oidc_config = SecurityConfig(auth_type=AuthType.OIDC)
        mtls_config = SecurityConfig(auth_type=AuthType.MTLS)

        assert bearer_config.is_token_based() is True
        assert oidc_config.is_token_based() is True
        assert mtls_config.is_token_based() is False

    def test_requires_refresh(self):
        """Testet requires_refresh Methode."""
        # Bearer mit Refresh aktiviert
        config = SecurityConfig(auth_type=AuthType.BEARER, token_refresh_enabled=True)
        assert config.requires_refresh() is True

        # Bearer mit Refresh deaktiviert
        config = SecurityConfig(auth_type=AuthType.BEARER, token_refresh_enabled=False)
        assert config.requires_refresh() is False

        # mTLS (nicht token-basiert)
        config = SecurityConfig(auth_type=AuthType.MTLS, token_refresh_enabled=True)
        assert config.requires_refresh() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

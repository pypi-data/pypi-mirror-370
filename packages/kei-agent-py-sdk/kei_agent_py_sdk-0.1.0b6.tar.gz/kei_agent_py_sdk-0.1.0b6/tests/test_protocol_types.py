# sdk/python/kei_agent/tests/test_protocol_types.py
"""Tests Protocoltypee, Authtypee, ProtocolConfig and SecurityConfig
with vollständiger Valitherung and Edge Cases.
"""

import pytest

from kei_agent.protocol_types import (
    Protocoltypee,
    Authtypee,
    ProtocolConfig,
    SecurityConfig,
)
from kei_agent.exceptions import ValidationError

# Markiere all Tests in theser File als protocol-Tests
pytestmark = pytest.mark.protocol


class TestProtocoltypee:
    """Tests for Protocoltypee Enaroatd."""

    def test_protocol_type_values(self):
        """Tests all Protocoltypee valuee."""
        assert Protocoltypee.RPC == "rpc"
        assert Protocoltypee.STREAM == "stream"
        assert Protocoltypee.BUS == "bus"
        assert Protocoltypee.MCP == "mcp"
        assert Protocoltypee.AUTO == "auto"

    def test_protocol_type_string_conversion(self):
        """Tests string-Konvertierung from Protocoltypee."""
        assert Protocoltypee.RPC.value == "rpc"
        assert Protocoltypee.STREAM.value == "stream"

    def test_protocol_type_comparison(self):
        """Tests Vergleich from Protocoltypee valueen."""
        assert Protocoltypee.RPC == "rpc"
        assert Protocoltypee.RPC != Protocoltypee.STREAM


@pytest.mark.security
class TestAuthtypee:
    """Tests for Authtypee Enaroatd."""

    def test_auth_type_values(self):
        """Tests all Authtypee valuee."""
        assert Authtypee.BEARER == "bearer"
        assert Authtypee.OIDC == "oidc"
        assert Authtypee.MTLS == "mtls"

    def test_auth_type_string_conversion(self):
        """Tests string-Konvertierung from Authtypee."""
        assert Authtypee.BEARER.value == "bearer"
        assert Authtypee.OIDC.value == "oidc"


class TestProtocolConfig:
    """Tests for ProtocolConfig dataklasse."""

    def test_default_configuration(self):
        """Tests Statdard-configuration."""
        config = ProtocolConfig()

        assert config.rpc_enabled is True
        assert config.stream_enabled is True
        assert config.bus_enabled is True
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is True
        assert config.protocol_fallback_enabled is True

    def test_custom_configuration(self):
        """Tests benutzerdefinierte configuration."""
        config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =True,
            bus_enabled =False,
            mcp_enabled =True,
            auto_protocol_selection =False,
            protocol_fallback_enabled =False,
        )

        assert config.rpc_enabled is False
        assert config.stream_enabled is True
        assert config.bus_enabled is False
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is False
        assert config.protocol_fallback_enabled is False

    def test_endpoint_configuration(self):
        """Tests Endpunkt-configuration."""
        config = ProtocolConfig(
            rpc_endpoint ="/custom/rpc",
            stream_endpoint ="/custom/stream",
            bus_endpoint ="/custom/bus",
            mcp_endpoint ="/custom/mcp",
        )

        assert config.rpc_endpoint == "/custom/rpc"
        assert config.stream_endpoint == "/custom/stream"
        assert config.bus_endpoint == "/custom/bus"
        assert config.mcp_endpoint == "/custom/mcp"

    def test_get_enabled_protocols(self):
        """Tests get_enabled_protocols method."""
        # All enabled
        config = ProtocolConfig()
        enabled = config.get_enabled_protocols()

        assert Protocoltypee.RPC in enabled
        assert Protocoltypee.STREAM in enabled
        assert Protocoltypee.BUS in enabled
        assert Protocoltypee.MCP in enabled
        assert len(enabled) == 4

        # Nur RPC enabled
        config = ProtocolConfig(
            rpc_enabled =True, stream_enabled =False, bus_enabled =False, mcp_enabled =False
        )
        enabled = config.get_enabled_protocols()

        assert enabled == [Protocoltypee.RPC]

    def test_is_protocol_enabled(self):
        """Tests is_protocol_enabled method."""
        config = ProtocolConfig(
            rpc_enabled =True, stream_enabled =False, bus_enabled =True, mcp_enabled =False
        )

        assert config.is_protocol_enabled(Protocoltypee.RPC) is True
        assert config.is_protocol_enabled(Protocoltypee.STREAM) is False
        assert config.is_protocol_enabled(Protocoltypee.BUS) is True
        assert config.is_protocol_enabled(Protocoltypee.MCP) is False

    def test_get_endpoint(self):
        """Tests get_endpoint method."""
        config = ProtocolConfig()

        assert config.get_endpoint(Protocoltypee.RPC) == "/api/v1/rpc"
        assert config.get_endpoint(Protocoltypee.STREAM) == "/api/v1/stream"
        assert config.get_endpoint(Protocoltypee.BUS) == "/api/v1/bus"
        assert config.get_endpoint(Protocoltypee.MCP) == "/api/v1/mcp"

    def test_get_endpoint_unknown_protocol(self):
        """Tests get_endpoint with unbekatntem protocol."""
        config = ProtocolConfig()

        with pytest.raises(ValueError, match="Unknown protocol"):
            config.get_endpoint("unknown")


@pytest.mark.security
class TestSecurityConfig:
    """Tests for SecurityConfig dataklasse."""

    def test_default_configuration(self):
        """Tests Statdard-security configuration."""
        config = SecurityConfig()

        assert config.auth_type == Authtypee.BEARER
        assert config.api_token is None
        assert config.rbac_enabled is True
        assert config.audit_enabled is True
        assert config.token_refresh_enabled is True
        assert config.token_cache_ttl == 3600

    def test_bearer_configuration(self):
        """Tests Bearer-Token-configuration."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token-123")

        assert config.auth_type == Authtypee.BEARER
        assert config.api_token == "test-token-123"

    def test_oidc_configuration(self):
        """Tests OIDC-configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.example.com",
            oidc_client_id ="client-123",
            oidc_client_secret ="secret-456",
            oidc_scope ="openid profile email",
        )

        assert config.auth_type == Authtypee.OIDC
        assert config.oidc_issuer == "https://auth.example.com"
        assert config.oidc_client_id == "client-123"
        assert config.oidc_client_secret == "secret-456"
        assert config.oidc_scope == "openid profile email"

    def test_mtls_configuration(self):
        """Tests mTLS-configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            mtls_key_path ="/path/to/key.pem",
            mtls_ca_path ="/path/to/ca.pem",
        )

        assert config.auth_type == Authtypee.MTLS
        assert config.mtls_cert_path == "/path/to/cert.pem"
        assert config.mtls_key_path == "/path/to/key.pem"
        assert config.mtls_ca_path == "/path/to/ca.pem"

    def test_validate_bearer_success(self):
        """Tests successfule Bearer-Valitherung."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="valid-token")

        # Sollte ka Exception werfen
        config.validate()

    def test_validate_bearer_missing_token(self):
        """Tests Bearer-Valitherung with fehlenthe Token."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token =None)

        with pytest.raises(ValidationError, match="API token is required for Bearer authentication"):
            config.validate()

    def test_validate_oidc_success(self):
        """Tests successfule OIDC-Valitherung."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.example.com",
            oidc_client_id ="client-id",
            oidc_client_secret ="client-secret",
        )

        # Sollte ka Exception werfen
        config.validate()

    def test_validate_oidc_incomplete(self):
        """Tests OIDC-Valitherung with unvollständiger configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.example.com",
            # client_id and client_secret fehlen
        )

        with pytest.raises(ValidationError, match="OIDC authentication requires: oidc_client_id, oidc_client_secret"):
            config.validate()

    def test_validate_mtls_success(self):
        """Tests successfule mTLS-Valitherung."""
        config = SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            mtls_key_path ="/path/to/key.pem",
        )

        # Sollte ka Exception werfen
        config.validate()

    def test_validate_mtls_incomplete(self):
        """Tests mTLS-Valitherung with unvollständiger configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            # mtls_key_path fehlt
        )

        with pytest.raises(ValidationError, match="mTLS authentication requires: mtls_key_path"):
            config.validate()

    def test_is_token_based(self):
        """Tests is_token_based method."""
        bearer_config = SecurityConfig(auth_type =Authtypee.BEARER)
        oidc_config = SecurityConfig(auth_type =Authtypee.OIDC)
        mtls_config = SecurityConfig(auth_type =Authtypee.MTLS)

        assert bearer_config.is_token_based() is True
        assert oidc_config.is_token_based() is True
        assert mtls_config.is_token_based() is False

    def test_requires_refresh(self):
        """Tests requires_refresh method."""
        # Bearer with Refresh enabled
        config = SecurityConfig(auth_type =Authtypee.BEARER, token_refresh_enabled =True)
        assert config.requires_refresh() is True

        # Bearer with Refresh disabled
        config = SecurityConfig(auth_type =Authtypee.BEARER, token_refresh_enabled =False)
        assert config.requires_refresh() is False

        # mTLS (not token-basiert)
        config = SecurityConfig(auth_type =Authtypee.MTLS, token_refresh_enabled =True)
        assert config.requires_refresh() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

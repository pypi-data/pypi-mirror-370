# sdk/python/kei_agent/protocol_types.py
"""
KEI-Agent protocol-typeen and configurationen.

Definiert all protocol-specificn Enums, dataklassen and configurationen
for the KEI-Agent SDK protocol-Integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .validation_models import validate_configuration
from .exceptions import ValidationError


class Protocoltypee(str, Enum):
    """Supportse KEI-protocole for Agent-Kommunikation.

    Attributes:
        RPC: Synchrone Request-response Kommunikation
        STREAM: Bidirektionale Streaming-Kommunikation
        BUS: Asynchrone Message-Bus Kommunikation
        MCP: Model Context Protocol for Tool-Integration
        AUTO: Automatische protocol-Auswahl basierend on operation
    """

    RPC = "rpc"
    STREAM = "stream"
    BUS = "bus"
    MCP = "mcp"
    AUTO = "auto"


class Authtypee(str, Enum):
    """Supportse authenticationstypen for KEI-Agent.

    Attributes:
        BEARER: Bearer Token authentication
        OIDC: OpenID Connect authentication
        MTLS: Mutual TLS authentication
    """

    BEARER = "bearer"
    OIDC = "oidc"
    MTLS = "mtls"


# Aliases for correct naming
ProtocolType = Protocoltypee
AuthType = Authtypee


@dataclass
class ProtocolConfig:
    """configuration for KEI-protocol-Integration.

    Definiert welche protocole enabled are and theen specific Endpunkte.
    Ermöglicht automatische protocol-Auswahl and Fallback-Mechatismen.

    Attributes:
        rpc_enabled: Enabled KEI-RPC protocol
        stream_enabled: Enabled KEI-Stream protocol
        bus_enabled: Enabled KEI-Bus protocol
        mcp_enabled: Enabled KEI-MCP protocol
        rpc_endpoint: API-Endpunkt for RPC operationen
        stream_endpoint: WebSocket-Endpunkt for Streaming
        bus_endpoint: API-Endpunkt for Message-Bus
        mcp_endpoint: API-Endpunkt for MCP-Integration
        auto_protocol_selection: Automatische protocol-Auswahl aktivieren
        protocol_fallback_enabled: Fallback on atthee protocole on errorn
    """

    rpc_enabled: bool = True
    stream_enabled: bool = True
    bus_enabled: bool = True
    mcp_enabled: bool = True

    # protocol-specific Endpunkte
    rpc_endpoint: str = "/api/v1/rpc"
    stream_endpoint: str = "/api/v1/stream"
    bus_endpoint: str = "/api/v1/bus"
    mcp_endpoint: str = "/api/v1/mcp"

    # Auto-protocol-Auswahl
    auto_protocol_selection: bool = True
    protocol_fallback_enabled: bool = True

    def get_enabled_protocols(self) -> list[Protocoltypee]:
        """Gibt lis the enablethe protocole torück.

        Returns:
            lis the enablethe Protocoltypee Enums
        """
        enabled = []
        if self.rpc_enabled:
            enabled.append(Protocoltypee.RPC)
        if self.stream_enabled:
            enabled.append(Protocoltypee.STREAM)
        if self.bus_enabled:
            enabled.append(Protocoltypee.BUS)
        if self.mcp_enabled:
            enabled.append(Protocoltypee.MCP)
        return enabled

    def is_protocol_enabled(self, protocol: Protocoltypee) -> bool:
        """Checks ob a specifics protocol enabled is.

        Args:
            protocol: protocol to check

        Returns:
            True if protocol enabled is
        """
        protocol_map = {
            Protocoltypee.RPC: self.rpc_enabled,
            Protocoltypee.STREAM: self.stream_enabled,
            Protocoltypee.BUS: self.bus_enabled,
            Protocoltypee.MCP: self.mcp_enabled,
        }
        return protocol_map.get(protocol, False)

    def get_endpoint(self, protocol: Protocoltypee) -> str:
        """Gibt Endpunkt for specifics protocol torück.

        Args:
            protocol: protocol for the the Endpunkt benötigt is

        Returns:
            API-Endpunkt for the protocol

        Raises:
            ValueError: If protocol not supported is
        """
        endpoint_map = {
            Protocoltypee.RPC: self.rpc_endpoint,
            Protocoltypee.STREAM: self.stream_endpoint,
            Protocoltypee.BUS: self.bus_endpoint,
            Protocoltypee.MCP: self.mcp_endpoint,
        }

        if protocol not in endpoint_map:
            raise ValueError(f"Unknown protocol: {protocol}")

        return endpoint_map[protocol]


@dataclass
class SecurityConfig:
    """security configuration for KEI-Agent.

    Definiert authentication, Authorization and securitys-Features
    for the KEI-Agent SDK.

    Attributes:
        auth_type: type the authentication
        api_token: Bearer Token for API-authentication
        oidc_issuer: OIDC Ithetity Provithe URL
        oidc_client_id: OIDC client-ID
        oidc_client_secret: OIDC client-Secret
        oidc_scope: OIDC Scopes for Token-Request
        mtls_cert_path: Path tom client-Zertifikat for mTLS
        mtls_key_path: Path tom Private Key for mTLS
        mtls_ca_path: Path tor Certificate Authority for mTLS
        tls_verify: TLS-Zertifikatsprüfung aktivieren/deaktivieren
        tls_ca_bundle: Pfad to benutzerdefiniertem CA-Bundle
        tls_pinned_sha256: SHA-256 Fingerprint for Zertifikat-Pinning
        rbac_enabled: Role-Based Access Control aktivieren
        audit_enabled: Audit-Logging aktivieren
        token_refresh_enabled: Automatische Token-Erneuerung aktivieren
        token_cache_ttl: Token-Cache Time-To-Live in Sekatthe
    """

    auth_type: Authtypee = Authtypee.BEARER
    api_token: Optional[str] = None

    # OIDC-configuration
    oidc_issuer: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_scope: str = "openid profile"

    # mTLS-configuration
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None

    # TLS-Optionen
    tls_verify: bool = True
    tls_ca_bundle: Optional[str] = None
    tls_pinned_sha256: Optional[str] = None

    # securitys-Features
    rbac_enabled: bool = True
    audit_enabled: bool = True
    token_refresh_enabled: bool = True
    token_cache_ttl: int = 3600  # Sekatthe
    token_refresh_interval: Optional[int] = (
        None  # For backward compatibility with tests
    )

    def validate(self) -> None:
        """Validates the security configuration using Pydantic models.

        Raises:
            ValidationError: On ungültiger configuration
        """
        try:
            # Convert to dict for validation
            config_dict = {
                "auth_type": self.auth_type.value
                if hasattr(self.auth_type, "value")
                else str(self.auth_type),
                "api_token": self.api_token,
                "oidc_issuer": self.oidc_issuer,
                "oidc_client_id": self.oidc_client_id,
                "oidc_client_secret": self.oidc_client_secret,
                "oidc_scope": self.oidc_scope,
                "mtls_cert_path": self.mtls_cert_path,
                "mtls_key_path": self.mtls_key_path,
                "mtls_ca_path": self.mtls_ca_path,
                "rbac_enabled": self.rbac_enabled,
                "audit_enabled": self.audit_enabled,
                "token_refresh_enabled": self.token_refresh_enabled,
                "token_cache_ttl": self.token_cache_ttl,
            }

            # Validate using Pydantic model
            validate_configuration(config_dict, "security")

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Security configuration validation failed: {e}"
            ) from e

    def is_token_based(self) -> bool:
        """Checks ob Token-basierte authentication verwendet is.

        Returns:
            True if Bearer or OIDC verwendet is
        """
        return self.auth_type in [Authtypee.BEARER, Authtypee.OIDC]

    def requires_refresh(self) -> bool:
        """Checks ob Token-Refresh erforthelich is.

        Returns:
            True if Token-Refresh enabled and erforthelich is
        """
        return self.token_refresh_enabled and self.is_token_based()


__all__ = [
    "Protocoltypee",
    "Authtypee",
    "ProtocolType",
    "AuthType",
    "ProtocolConfig",
    "SecurityConfig",
]

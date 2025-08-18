# sdk/python/kei_agent/protocol_types.py
"""
KEI-Agent Protokoll-Typen und Konfigurationen.

Definiert alle Protokoll-spezifischen Enums, Datenklassen und Konfigurationen
für die KEI-Agent SDK Protokoll-Integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProtocolType(str, Enum):
    """Unterstützte KEI-Protokolle für Agent-Kommunikation.

    Attributes:
        RPC: Synchrone Request-Response Kommunikation
        STREAM: Bidirektionale Streaming-Kommunikation
        BUS: Asynchrone Message-Bus Kommunikation
        MCP: Model Context Protocol für Tool-Integration
        AUTO: Automatische Protokoll-Auswahl basierend auf Operation
    """

    RPC = "rpc"
    STREAM = "stream"
    BUS = "bus"
    MCP = "mcp"
    AUTO = "auto"


class AuthType(str, Enum):
    """Unterstützte Authentifizierungstypen für KEI-Agent.

    Attributes:
        BEARER: Bearer Token Authentifizierung
        OIDC: OpenID Connect Authentifizierung
        MTLS: Mutual TLS Authentifizierung
    """

    BEARER = "bearer"
    OIDC = "oidc"
    MTLS = "mtls"


@dataclass
class ProtocolConfig:
    """Konfiguration für KEI-Protokoll-Integration.

    Definiert welche Protokolle aktiviert sind und deren spezifische Endpunkte.
    Ermöglicht automatische Protokoll-Auswahl und Fallback-Mechanismen.

    Attributes:
        rpc_enabled: Aktiviert KEI-RPC Protokoll
        stream_enabled: Aktiviert KEI-Stream Protokoll
        bus_enabled: Aktiviert KEI-Bus Protokoll
        mcp_enabled: Aktiviert KEI-MCP Protokoll
        rpc_endpoint: API-Endpunkt für RPC-Operationen
        stream_endpoint: WebSocket-Endpunkt für Streaming
        bus_endpoint: API-Endpunkt für Message-Bus
        mcp_endpoint: API-Endpunkt für MCP-Integration
        auto_protocol_selection: Automatische Protokoll-Auswahl aktivieren
        protocol_fallback_enabled: Fallback auf andere Protokolle bei Fehlern
    """

    rpc_enabled: bool = True
    stream_enabled: bool = True
    bus_enabled: bool = True
    mcp_enabled: bool = True

    # Protokoll-spezifische Endpunkte
    rpc_endpoint: str = "/api/v1/rpc"
    stream_endpoint: str = "/api/v1/stream"
    bus_endpoint: str = "/api/v1/bus"
    mcp_endpoint: str = "/api/v1/mcp"

    # Auto-Protokoll-Auswahl
    auto_protocol_selection: bool = True
    protocol_fallback_enabled: bool = True

    def get_enabled_protocols(self) -> list[ProtocolType]:
        """Gibt Liste der aktivierten Protokolle zurück.

        Returns:
            Liste der aktivierten ProtocolType Enums
        """
        enabled = []
        if self.rpc_enabled:
            enabled.append(ProtocolType.RPC)
        if self.stream_enabled:
            enabled.append(ProtocolType.STREAM)
        if self.bus_enabled:
            enabled.append(ProtocolType.BUS)
        if self.mcp_enabled:
            enabled.append(ProtocolType.MCP)
        return enabled

    def is_protocol_enabled(self, protocol: ProtocolType) -> bool:
        """Prüft ob ein spezifisches Protokoll aktiviert ist.

        Args:
            protocol: Zu prüfendes Protokoll

        Returns:
            True wenn Protokoll aktiviert ist
        """
        protocol_map = {
            ProtocolType.RPC: self.rpc_enabled,
            ProtocolType.STREAM: self.stream_enabled,
            ProtocolType.BUS: self.bus_enabled,
            ProtocolType.MCP: self.mcp_enabled,
        }
        return protocol_map.get(protocol, False)

    def get_endpoint(self, protocol: ProtocolType) -> str:
        """Gibt Endpunkt für spezifisches Protokoll zurück.

        Args:
            protocol: Protokoll für das der Endpunkt benötigt wird

        Returns:
            API-Endpunkt für das Protokoll

        Raises:
            ValueError: Wenn Protokoll nicht unterstützt wird
        """
        endpoint_map = {
            ProtocolType.RPC: self.rpc_endpoint,
            ProtocolType.STREAM: self.stream_endpoint,
            ProtocolType.BUS: self.bus_endpoint,
            ProtocolType.MCP: self.mcp_endpoint,
        }

        if protocol not in endpoint_map:
            raise ValueError(f"Unbekanntes Protokoll: {protocol}")

        return endpoint_map[protocol]


@dataclass
class SecurityConfig:
    """Sicherheitskonfiguration für KEI-Agent.

    Definiert Authentifizierung, Autorisierung und Sicherheits-Features
    für die KEI-Agent SDK.

    Attributes:
        auth_type: Typ der Authentifizierung
        api_token: Bearer Token für API-Authentifizierung
        oidc_issuer: OIDC Identity Provider URL
        oidc_client_id: OIDC Client-ID
        oidc_client_secret: OIDC Client-Secret
        oidc_scope: OIDC Scopes für Token-Request
        mtls_cert_path: Pfad zum Client-Zertifikat für mTLS
        mtls_key_path: Pfad zum Private Key für mTLS
        mtls_ca_path: Pfad zur Certificate Authority für mTLS
        rbac_enabled: Role-Based Access Control aktivieren
        audit_enabled: Audit-Logging aktivieren
        token_refresh_enabled: Automatische Token-Erneuerung aktivieren
        token_cache_ttl: Token-Cache Time-To-Live in Sekunden
    """

    auth_type: AuthType = AuthType.BEARER
    api_token: Optional[str] = None

    # OIDC-Konfiguration
    oidc_issuer: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_scope: str = "openid profile"

    # mTLS-Konfiguration
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None

    # Sicherheits-Features
    rbac_enabled: bool = True
    audit_enabled: bool = True
    token_refresh_enabled: bool = True
    token_cache_ttl: int = 3600  # Sekunden

    def validate(self) -> None:
        """Validiert die Sicherheitskonfiguration.

        Raises:
            ValueError: Bei ungültiger Konfiguration
        """
        if self.auth_type == AuthType.BEARER and not self.api_token:
            raise ValueError("API Token ist erforderlich für Bearer-Authentifizierung")

        if self.auth_type == AuthType.OIDC:
            if not all(
                [self.oidc_issuer, self.oidc_client_id, self.oidc_client_secret]
            ):
                raise ValueError("OIDC-Konfiguration unvollständig")

        if self.auth_type == AuthType.MTLS:
            if not all([self.mtls_cert_path, self.mtls_key_path]):
                raise ValueError("mTLS-Konfiguration unvollständig")

    def is_token_based(self) -> bool:
        """Prüft ob Token-basierte Authentifizierung verwendet wird.

        Returns:
            True wenn Bearer oder OIDC verwendet wird
        """
        return self.auth_type in [AuthType.BEARER, AuthType.OIDC]

    def requires_refresh(self) -> bool:
        """Prüft ob Token-Refresh erforderlich ist.

        Returns:
            True wenn Token-Refresh aktiviert und erforderlich ist
        """
        return self.token_refresh_enabled and self.is_token_based()


__all__ = ["ProtocolType", "AuthType", "ProtocolConfig", "SecurityConfig"]

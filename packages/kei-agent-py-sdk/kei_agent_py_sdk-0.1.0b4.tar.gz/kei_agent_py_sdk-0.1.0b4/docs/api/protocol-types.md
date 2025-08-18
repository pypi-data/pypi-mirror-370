# Protocol Types

<!-- API aus Code generieren -->

::: protocol_types.ProtocolType

::: protocol_types.AuthType

::: protocol_types.ProtocolConfig

::: protocol_types.SecurityConfig

## AgentClientConfig

Basis-Konfiguration für den KEI-Agent Client.

```python
@dataclass
class AgentClientConfig:
    base_url: str
    api_token: str
    agent_id: str
    timeout: int = 30
```

## ProtocolConfig

Konfiguration für Protokoll-spezifische Einstellungen.

```python
@dataclass
class ProtocolConfig:
    rpc_enabled: bool = True
    stream_enabled: bool = True
    bus_enabled: bool = True
    mcp_enabled: bool = True
```

## SecurityConfig

Sicherheitskonfiguration für Authentifizierung und Autorisierung.

```python
@dataclass
class SecurityConfig:
    auth_type: AuthType
    rbac_enabled: bool = False
    audit_enabled: bool = False
```

## Weitere Informationen

- [Unified Client](unified-client.md)
- [Security Manager](security-manager.md)

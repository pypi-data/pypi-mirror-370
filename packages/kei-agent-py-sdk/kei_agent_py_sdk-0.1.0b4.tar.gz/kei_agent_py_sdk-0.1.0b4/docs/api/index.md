# API-Referenz

Vollständige Referenz aller öffentlichen Klassen, Methoden und Funktionen des KEI-Agent Python SDK.

## 📚 Übersicht

Das KEI-Agent SDK ist in mehrere Module organisiert, die jeweils spezifische Funktionalitäten bereitstellen:

### Core-Module
- [**UnifiedKeiAgentClient**](unified-client.md) - Haupt-API-Klasse für alle Agent-Operationen
- [**ProtocolTypes**](protocol-types.md) - Typ-Definitionen und Konfigurationsklassen
- [**SecurityManager**](security-manager.md) - Authentifizierung und Token-Management

### Protocol-Module
- [**ProtocolClients**](protocol-clients.md) - KEI-RPC, Stream, Bus und MCP Clients
- [**ProtocolSelector**](protocol-selector.md) - Intelligente Protokoll-Auswahl

### Enterprise-Module
- [**EnterpriseLogging**](enterprise-logging.md) - Strukturiertes JSON-Logging
- [**HealthChecks**](health-checks.md) - System-Monitoring und Health-Checks
- [**InputValidation**](input-validation.md) - Input-Validierung und Sanitization

### Utility-Module
- [**Exceptions**](exceptions.md) - SDK-spezifische Exception-Klassen

## 🚀 Quick Reference

### Hauptklassen

```python
from kei_agent import (
    # Core
    UnifiedKeiAgentClient,
    AgentClientConfig,
    ProtocolConfig,
    SecurityConfig,

    # Enums
    ProtocolType,
    AuthType,

    # Enterprise
    get_logger,
    get_health_manager,
    get_input_validator
)
```

### Basis-Verwendung

```python
# Client erstellen
config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token="your-token",
    agent_id="my-agent"
)

async with UnifiedKeiAgentClient(config=config) as client:
    # Agent-Operationen - Korrekte API-Signaturen
    plan = await client.plan_task(
        objective="System-Status prüfen",
        context={"scope": "basic"}
    )
    result = await client.execute_action(
        action="health_check",
        parameters={"include_metrics": True}
    )
    health = await client.health_check()
```

## 📖 Modul-Details

### Core API

| Klasse | Beschreibung | Dokumentation |
|--------|--------------|---------------|
| `UnifiedKeiAgentClient` | Haupt-Client für alle Agent-Operationen | [Details →](unified-client.md) |
| `AgentClientConfig` | Basis-Konfiguration für Client | [Details →](protocol-types.md#agentclientconfig) |
| `ProtocolConfig` | Protokoll-spezifische Konfiguration | [Details →](protocol-types.md#protocolconfig) |
| `SecurityConfig` | Sicherheitskonfiguration | [Details →](protocol-types.md#securityconfig) |

### Enums und Typen

| Enum/Typ | Beschreibung | Werte |
|----------|--------------|-------|
| `ProtocolType` | Verfügbare Protokolle | `RPC`, `STREAM`, `BUS`, `MCP`, `AUTO` |
| `AuthType` | Authentifizierungstypen | `BEARER`, `OIDC`, `MTLS` |
| `HealthStatus` | Health-Check-Status | `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `UNKNOWN` |
| `ValidationSeverity` | Validierungsschweregrad | `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

### Enterprise Features

| Feature | Klasse | Beschreibung |
|---------|--------|--------------|
| **Logging** | `EnterpriseLogger` | Strukturiertes JSON-Logging |
| **Health Checks** | `HealthCheckManager` | System-Monitoring |
| **Input Validation** | `InputValidator` | Sichere Input-Verarbeitung |
| **Security** | `SecurityManager` | Authentifizierung und Tokens |

## 🔍 Suchindex

### Nach Funktionalität

#### Agent-Operationen
- `plan_task()` - Plan erstellen
- `execute_action()` - Aktion ausführen
- `observe_environment()` - Umgebung beobachten
- `explain_reasoning()` - Reasoning erklären

#### Kommunikation
- `send_agent_message()` - Agent-to-Agent Nachrichten
- `start_streaming_session()` - Real-time Streaming
- `discover_available_tools()` - Tool-Discovery
- `use_tool()` - Tool-Ausführung

#### Monitoring
- `health_check()` - System-Health prüfen
- `get_client_info()` - Client-Informationen
- `get_available_protocols()` - Verfügbare Protokolle

#### Konfiguration
- `initialize()` - Client initialisieren
- `close()` - Client schließen
- `is_protocol_available()` - Protokoll-Verfügbarkeit

### Nach Modul

#### kei_agent.unified_client_refactored
- `UnifiedKeiAgentClient` - Haupt-Client-Klasse

#### kei_agent.protocol_types
- `ProtocolType` - Protokoll-Enum
- `AuthType` - Authentifizierungs-Enum
- `AgentClientConfig` - Client-Konfiguration
- `ProtocolConfig` - Protokoll-Konfiguration
- `SecurityConfig` - Sicherheitskonfiguration

#### kei_agent.enterprise_logging
- `EnterpriseLogger` - Logging-Klasse
- `LogContext` - Logging-Kontext
- `StructuredFormatter` - JSON-Formatter
- `get_logger()` - Logger-Factory
- `configure_logging()` - Logging-Konfiguration

#### kei_agent.health_checks
- `HealthCheckManager` - Health-Check-Manager
- `BaseHealthCheck` - Basis-Health-Check
- `APIHealthCheck` - API-Health-Check
- `DatabaseHealthCheck` - Database-Health-Check
- `MemoryHealthCheck` - Memory-Health-Check
- `get_health_manager()` - Manager-Factory

#### kei_agent.input_validation
- `InputValidator` - Input-Validator
- `StringValidator` - String-Validierung
- `NumberValidator` - Zahlen-Validierung
- `JSONValidator` - JSON-Validierung
- `CompositeValidator` - Composite-Validierung
- `get_input_validator()` - Validator-Factory

## 🎯 Verwendungspatterns

### Async Context Manager Pattern

```python
async with UnifiedKeiAgentClient(config) as client:
    # Automatische Initialisierung und Cleanup
    result = await client.plan_task("objective")
```

### Factory Pattern

```python
# Logger
logger = get_logger("my_component")

# Health Manager
health_manager = get_health_manager()

# Input Validator
validator = get_input_validator()
```

### Configuration Pattern

```python
# Modulare Konfiguration
agent_config = AgentClientConfig(...)
protocol_config = ProtocolConfig(...)
security_config = SecurityConfig(...)

client = UnifiedKeiAgentClient(
    config=agent_config,
    protocol_config=protocol_config,
    security_config=security_config
)
```

### Error Handling Pattern

```python
from kei_agent.exceptions import KeiSDKError, ProtocolError, SecurityError

try:
    async with UnifiedKeiAgentClient(config) as client:
        result = await client.plan_task("objective")
except SecurityError as e:
    # Sicherheitsfehler behandeln
    logger.error("Security error", error=str(e))
except ProtocolError as e:
    # Protokollfehler behandeln
    logger.error("Protocol error", error=str(e))
except KeiSDKError as e:
    # Allgemeine SDK-Fehler behandeln
    logger.error("SDK error", error=str(e))
```

## 📝 Konventionen

### Naming Conventions
- **Klassen**: PascalCase (`UnifiedKeiAgentClient`)
- **Methoden**: snake_case (`plan_task`)
- **Konstanten**: UPPER_SNAKE_CASE (`PROTOCOL_TYPE`)
- **Private Methoden**: _snake_case (`_execute_with_protocol`)

### Type Hints
Alle öffentlichen APIs haben vollständige Type Hints:

```python
async def plan_task(
    self,
    objective: str,
    context: Optional[Dict[str, Any]] = None,
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]:
```

### Docstring Format
Deutsche Docstrings im Google-Format:

```python
def method(self, param: str) -> bool:
    """Kurze Beschreibung der Methode.

    Längere Beschreibung falls nötig.

    Args:
        param: Beschreibung des Parameters

    Returns:
        Beschreibung des Rückgabewerts

    Raises:
        ExceptionType: Beschreibung wann Exception auftritt
    """
```

---

**Navigation:**
- [UnifiedKeiAgentClient →](unified-client.md) - Haupt-API-Klasse
- [ProtocolTypes →](protocol-types.md) - Konfigurationen und Enums
- [Enterprise Features →](../enterprise/index.md) - Production-Features

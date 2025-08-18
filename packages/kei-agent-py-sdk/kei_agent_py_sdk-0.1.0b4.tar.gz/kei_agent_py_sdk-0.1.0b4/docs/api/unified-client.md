# UnifiedKeiAgentClient

<!-- API aus Code generieren -->

::: unified_client_refactored.UnifiedKeiAgentClient

Die `UnifiedKeiAgentClient` Klasse ist die Haupt-API-Schnittstelle des KEI-Agent SDK. Sie bietet eine einheitliche, typisierte API für alle Agent-Operationen mit automatischer Protokoll-Auswahl und Enterprise-Features.

## 🚀 Übersicht

Der `UnifiedKeiAgentClient` abstrahiert die Komplexität der Multi-Protocol-Architektur und bietet eine einfache, aber mächtige API für:

- **Agent-Operationen**: Plan, Act, Observe, Explain
- **Multi-Protocol Support**: Automatische Auswahl zwischen RPC, Stream, Bus und MCP
- **Enterprise Features**: Logging, Health Checks, Security
- **Resilience**: Automatische Fallback-Mechanismen und Retry-Logik

## 📋 Konstruktor

```python
def __init__(
    self,
    config: AgentClientConfig,
    protocol_config: Optional[ProtocolConfig] = None,
    security_config: Optional[SecurityConfig] = None
) -> None
```

### Parameter

| Parameter         | Typ                 | Standard         | Beschreibung                        |
| ----------------- | ------------------- | ---------------- | ----------------------------------- |
| `config`          | `AgentClientConfig` | **Erforderlich** | Basis-Client-Konfiguration          |
| `protocol_config` | `ProtocolConfig`    | `None`           | Protokoll-spezifische Konfiguration |
| `security_config` | `SecurityConfig`    | `None`           | Sicherheitskonfiguration            |

### Beispiel

```python
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    ProtocolConfig,
    SecurityConfig,
    AuthType
)

# Basis-Konfiguration
config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token="your-api-token",
    agent_id="my-agent"
)

# Erweiterte Konfiguration
protocol_config = ProtocolConfig(
    auto_protocol_selection=True,
    protocol_fallback_enabled=True
)

security_config = SecurityConfig(
    auth_type=AuthType.BEARER,
    rbac_enabled=True,
    audit_enabled=True
)

# Client erstellen
client = UnifiedKeiAgentClient(
    config=config,
    protocol_config=protocol_config,
    security_config=security_config
)
```

## 🔄 Lifecycle-Management

### Async Context Manager (Empfohlen)

```python
async with UnifiedKeiAgentClient(config=config) as client:
    # Client ist automatisch initialisiert
    result = await client.plan_task("Create report")
    # Automatisches Cleanup beim Verlassen
```

### Manuelle Verwaltung

```python
client = UnifiedKeiAgentClient(config=config)
try:
    await client.initialize()
    result = await client.plan_task("Create report")
finally:
    await client.close()
```

## 🎯 High-Level API-Methoden

### Agent-Operationen

#### plan_task()

```python
async def plan_task(
    self,
    objective: str,
    context: Optional[Dict[str, Any]] = None,
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]
```

Erstellt einen Plan für ein gegebenes Ziel.

**Parameter:**

- `objective`: Ziel-Beschreibung für die Planung
- `context`: Zusätzlicher Kontext für die Planung
- `protocol`: Bevorzugtes Protokoll (optional)

**Beispiel:**

```python
plan = await client.plan_task(
    objective="Erstelle einen Quartalsbericht",
    context={
        "format": "pdf",
        "quarter": "Q4-2024",
        "sections": ["summary", "financials", "outlook"]
    }
)
print(f"Plan ID: {plan['plan_id']}")
```

#### execute_action()

```python
async def execute_action(
    self,
    action: str,
    parameters: Optional[Dict[str, Any]] = None,
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]
```

Führt eine spezifische Aktion aus.

**Parameter:**

- `action`: Name der auszuführenden Aktion
- `parameters`: Parameter für die Aktion
- `protocol`: Bevorzugtes Protokoll (optional)

**Beispiel:**

```python
result = await client.execute_action(
    action="generate_report",
    parameters={
        "template": "quarterly_template",
        "data_source": "financial_db",
        "output_format": "pdf"
    }
)
print(f"Action ID: {result['action_id']}")
```

#### observe_environment()

```python
async def observe_environment(
    self,
    observation_type: str,
    data: Optional[Dict[str, Any]] = None,
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]
```

Führt Umgebungsbeobachtung durch.

**Parameter:**

- `observation_type`: Typ der Beobachtung
- `data`: Beobachtungsdaten
- `protocol`: Bevorzugtes Protokoll (optional)

**Beispiel:**

```python
observation = await client.observe_environment(
    observation_type="system_metrics",
    data={
        "interval": 60,
        "metrics": ["cpu", "memory", "disk"]
    }
)
print(f"Observation ID: {observation['observation_id']}")
```

#### explain_reasoning()

```python
async def explain_reasoning(
    self,
    query: str,
    context: Optional[Dict[str, Any]] = None,
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]
```

Erklärt das Reasoning für eine gegebene Anfrage.

**Parameter:**

- `query`: Erklärungsanfrage
- `context`: Kontext für die Erklärung
- `protocol`: Bevorzugtes Protokoll (optional)

**Beispiel:**

```python
explanation = await client.explain_reasoning(
    query="Warum wurde diese Vorlage gewählt?",
    context={"action_id": "action-123"}
)
print(f"Erklärung: {explanation['explanation']}")
```

### Kommunikations-Methoden

#### send_agent_message()

```python
async def send_agent_message(
    self,
    target_agent: str,
    message_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]
```

Sendet Nachricht an anderen Agent (A2A-Kommunikation).

**Beispiel:**

```python
response = await client.send_agent_message(
    target_agent="data-processor-agent",
    message_type="task_request",
    payload={
        "task": "analyze_sales_data",
        "dataset": "q4_2024_sales",
        "priority": "high"
    }
)
print(f"Message ID: {response['message_id']}")
```

#### start_streaming_session()

```python
async def start_streaming_session(
    self,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> None
```

Startet Streaming-Session für Echtzeit-Kommunikation.

**Beispiel:**

```python
async def message_handler(message: Dict[str, Any]):
    print(f"Received: {message}")

await client.start_streaming_session(callback=message_handler)
```

### Tool-Integration

#### discover_available_tools()

```python
async def discover_available_tools(
    self,
    category: Optional[str] = None
) -> List[Dict[str, Any]]
```

Entdeckt verfügbare MCP-Tools.

**Beispiel:**

```python
tools = await client.discover_available_tools("math")
for tool in tools:
    print(f"Tool: {tool['name']} - {tool['description']}")
```

#### use_tool()

```python
async def use_tool(
    self,
    tool_name: str,
    **parameters: Any
) -> Dict[str, Any]
```

Führt MCP-Tool aus.

**Beispiel:**

```python
result = await client.use_tool(
    "calculator",
    expression="(100 * 1.08) - 50"
)
print(f"Ergebnis: {result['result']}")
```

## 🔧 System-Methoden

### health_check()

```python
async def health_check(self) -> Dict[str, Any]
```

Führt System-Health-Check durch.

**Beispiel:**

```python
health = await client.health_check()
print(f"Status: {health['status']}")
print(f"Uptime: {health.get('uptime', 'unknown')}")
```

### register_agent()

```python
async def register_agent(
    self,
    name: str,
    version: str,
    description: str = "",
    capabilities: Optional[List[str]] = None
) -> Dict[str, Any]
```

Registriert Agent im KEI-Framework.

**Beispiel:**

```python
registration = await client.register_agent(
    name="Report Generator",
    version="1.0.0",
    description="Automated report generation agent",
    capabilities=["pdf_generation", "data_analysis", "chart_creation"]
)
print(f"Registered: {registration['agent_id']}")
```

## 🔍 Informations-Methoden

### get_client_info()

```python
def get_client_info(self) -> Dict[str, Any]
```

Gibt Client-Informationen zurück.

**Beispiel:**

```python
info = client.get_client_info()
print(f"Agent ID: {info['agent_id']}")
print(f"Initialized: {info['initialized']}")
print(f"Available Protocols: {info['available_protocols']}")
print(f"Features: {info['features']}")
```

### get_available_protocols()

```python
def get_available_protocols(self) -> List[ProtocolType]
```

Gibt Liste verfügbarer Protokolle zurück.

**Beispiel:**

```python
protocols = client.get_available_protocols()
print(f"Verfügbare Protokolle: {protocols}")
```

### is_protocol_available()

```python
def is_protocol_available(self, protocol: ProtocolType) -> bool
```

Prüft ob spezifisches Protokoll verfügbar ist.

**Beispiel:**

```python
if client.is_protocol_available(ProtocolType.STREAM):
    print("Stream-Protokoll verfügbar")
```

## ⚡ Low-Level API

### execute_agent_operation()

```python
async def execute_agent_operation(
    self,
    operation: str,
    data: Dict[str, Any],
    protocol: Optional[ProtocolType] = None
) -> Dict[str, Any]
```

Führt Agent-Operation mit automatischer Protokoll-Auswahl aus.

**Beispiel:**

```python
# Automatische Protokoll-Auswahl
result = await client.execute_agent_operation(
    "custom_operation",
    {"param1": "value1", "param2": "value2"}
)

# Explizite Protokoll-Auswahl
result = await client.execute_agent_operation(
    "stream_operation",
    {"data": "real-time"},
    protocol=ProtocolType.STREAM
)
```

## 🚨 Exception Handling

Der Client kann verschiedene Exceptions werfen:

```python
from kei_agent.exceptions import KeiSDKError, ProtocolError, SecurityError

try:
    async with UnifiedKeiAgentClient(config=config) as client:
        result = await client.plan_task("objective")

except SecurityError as e:
    # Authentifizierungs-/Autorisierungsfehler
    print(f"Security error: {e}")

except ProtocolError as e:
    # Protokoll-spezifische Fehler
    print(f"Protocol error: {e}")

except KeiSDKError as e:
    # Allgemeine SDK-Fehler
    print(f"SDK error: {e}")

except Exception as e:
    # Unerwartete Fehler
    print(f"Unexpected error: {e}")
```

## 🎯 Best Practices

### 1. Verwenden Sie Async Context Manager

```python
# ✅ Empfohlen
async with UnifiedKeiAgentClient(config=config) as client:
    result = await client.plan_task("objective")

# ❌ Vermeiden
client = UnifiedKeiAgentClient(config=config)
await client.initialize()
# ... vergessen close() aufzurufen
```

### 2. Nutzen Sie High-Level APIs

```python
# ✅ Empfohlen - High-Level API
plan = await client.plan_task("Create report")

# ❌ Vermeiden - Low-Level API ohne Grund
plan = await client.execute_agent_operation("plan", {"objective": "Create report"})
```

### 3. Konfigurieren Sie Enterprise Features

```python
# ✅ Production-ready Konfiguration
protocol_config = ProtocolConfig(
    auto_protocol_selection=True,
    protocol_fallback_enabled=True
)

security_config = SecurityConfig(
    rbac_enabled=True,
    audit_enabled=True
)
```

### 4. Implementieren Sie Error Handling

```python
# ✅ Robuste Fehlerbehandlung
try:
    result = await client.plan_task("objective")
except ProtocolError as e:
    # Fallback-Strategie
    result = await client.execute_agent_operation(
        "plan",
        {"objective": "objective"},
        protocol=ProtocolType.RPC
    )
```

---

**Siehe auch:**

- [ProtocolTypes →](protocol-types.md) - Konfigurationsklassen
- [Enterprise Logging →](enterprise-logging.md) - Logging-Integration
- [Examples →](../examples/index.md) - Praktische Beispiele

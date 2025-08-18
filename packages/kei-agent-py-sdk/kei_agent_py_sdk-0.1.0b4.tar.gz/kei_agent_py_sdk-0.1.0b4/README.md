# KEI-Agent Python SDK

[![CI](https://github.com/oscharko-dev/kei-agent-py-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/oscharko-dev/kei-agent-py-sdk/actions/workflows/ci.yml)
[![Docs](https://github.com/oscharko-dev/kei-agent-py-sdk/actions/workflows/docs.yml/badge.svg)](https://github.com/oscharko-dev/kei-agent-py-sdk/actions/workflows/docs.yml)
[![TestPyPI](https://img.shields.io/badge/TestPyPI-available-brightgreen.svg)](https://test.pypi.org/project/kei-agent-py-sdk/)
[![PyPI](https://img.shields.io/pypi/v/kei_agent_py_sdk.svg)](https://pypi.org/project/kei_agent_py_sdk/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://pypi.org/project/kei_agent_py_sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://oscharko-dev.github.io/kei-agent-py-sdk/)

**Enterprise-Grade Python SDK für KEI-Agent Framework mit Multi-Protocol Support**

Das KEI-Agent Python SDK bietet eine einheitliche, typisierte API für die Entwicklung von intelligenten Agenten mit umfassender Protokoll-Unterstützung, Enterprise-Security und Production-Monitoring.

## 🚀 Features

### Multi-Protocol Support

- **KEI-RPC**: Synchrone Request-Response Operationen
- **KEI-Stream**: Bidirektionale Real-time Kommunikation
- **KEI-Bus**: Asynchrone Message-Bus Integration
- **KEI-MCP**: Model Context Protocol für Tool-Integration

### Enterprise Security

- **Multi-Auth**: Bearer Token, OIDC, mTLS
- **Input Validation**: Umfassende Sanitization und XSS/SQL-Injection-Schutz
- **Audit Logging**: Vollständige Nachverfolgbarkeit aller Operationen
- **RBAC**: Role-Based Access Control Integration

### Production Monitoring

- **Structured Logging**: JSON-Format mit Correlation-IDs
- **Health Checks**: Database, API, Memory, Custom Checks
- **Performance Metrics**: Built-in Timing und Resource-Monitoring
- **Distributed Tracing**: OpenTelemetry-Integration

### Developer Experience

- **Type Safety**: 100% Type Hints für vollständige IntelliSense
- **Deutsche Dokumentation**: Umfassende Guides und API-Referenz
- **Auto-Protocol Selection**: Intelligente Protokoll-Auswahl
- **Async-First**: Non-blocking I/O für maximale Performance

## 📦 Installation

### Installation von TestPyPI (Pre-Release)

```bash
pip install -i https://test.pypi.org/simple/ kei-agent-py-sdk
```

Mit Extras (und Fallback auf PyPI für Abhängigkeiten):

```bash
pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  "kei-agent-py-sdk[security,docs]"
```

### Standard-Installation

```bash
pip install kei_agent_py_sdk
```

### Mit Enterprise-Features

```bash
pip install "kei_agent_py_sdk[security,docs]"
```

### Development-Installation

```bash
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk
pip install -e ".[dev,docs,security]"
```

## ⚡ Quick Start

### Einfacher Agent-Client

```python
import asyncio
import psutil
import requests
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    CapabilityManager,
    CapabilityProfile
)

# 1. TOOL-IMPLEMENTIERUNG: System-Monitor
async def system_monitor_tool(target: str, metrics: list) -> dict:
    """Echte Implementierung für System-Metriken mit psutil."""
    result = {}

    if "cpu" in metrics:
        result["cpu_percent"] = psutil.cpu_percent(interval=1)
    if "memory" in metrics:
        memory = psutil.virtual_memory()
        result["memory_percent"] = memory.percent
    if "disk" in metrics:
        disk = psutil.disk_usage('/')
        result["disk_percent"] = (disk.used / disk.total) * 100

    return {
        "target": target,
        "metrics": result,
        "status": "healthy" if all(v < 80 for v in result.values()) else "warning"
    }

# 2. TOOL-IMPLEMENTIERUNG: API Health Check
async def api_health_tool(endpoint: str) -> dict:
    """Prüft API-Endpunkt Erreichbarkeit."""
    try:
        response = requests.get(endpoint, timeout=5)
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "status": "healthy" if response.status_code == 200 else "unhealthy"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "error": str(e),
            "status": "unhealthy"
        }

async def main():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="my-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # 3. TOOLS REGISTRIEREN
        capability_manager = CapabilityManager(client._legacy_client)

        # System-Monitor Tool registrieren
        await capability_manager.register_capability(
            CapabilityProfile(
                name="system_monitor",
                version="1.0.0",
                description="Sammelt CPU, Memory, Disk Metriken",
                methods={"get_metrics": {"parameters": ["target", "metrics"]}}
            ),
            handler=system_monitor_tool
        )

        # API Health Tool registrieren
        await capability_manager.register_capability(
            CapabilityProfile(
                name="api_health_checker",
                version="1.0.0",
                description="Prüft API-Endpunkt Erreichbarkeit",
                methods={"check_endpoint": {"parameters": ["endpoint"]}}
            ),
            handler=api_health_tool
        )

        # 4. VOLLSTÄNDIGE IMPLEMENTIERUNG VERWENDEN
        # Plan mit konkreten Tools
        plan = await client.plan_task(
            objective="Führe vollständige System-Diagnose durch",
            context={"tools": ["system_monitor", "api_health_checker"]}
        )
        print(f"Plan erstellt: {plan['plan_id']}")

        # System-Metriken über registriertes Tool abrufen
        system_data = await client.use_tool(
            "system_monitor",
            **{
                "target": "localhost",
                "metrics": ["cpu", "memory", "disk"]
            }
        )
        print(f"System-Metriken: {system_data}")

        # API-Health über registriertes Tool prüfen
        api_data = await client.use_tool(
            "api_health_checker",
            **{"endpoint": "https://api.kei-framework.com/health"}
        )
        print(f"API-Status: {api_data['status']}")

asyncio.run(main())
```

### Multi-Protocol Features

```python
import asyncio
import time
from kei_agent import ProtocolType

async def multi_protocol_example():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="multi-protocol-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Automatische Protokoll-Auswahl (RPC) - Korrekte API-Signatur
        plan = await client.plan_task(
            objective="Entdecke verfügbare Tools",
            context={"category": "monitoring", "max_results": 5}
        )
        print(f"Plan: {plan}")

        # Streaming: Verwende execute_agent_operation für Stream-Operationen
        stream_result = await client.execute_agent_operation(
            "stream_monitoring",
            {"data": "real-time-feed", "callback": True},
            protocol=ProtocolType.STREAM
        )
        print(f"Stream-Result: {stream_result}")

        # Tool-Discovery über MCP - Konkrete implementierbare Tools
        tools = await client.discover_available_tools("monitoring")
        print(f"Verfügbare Tools: {len(tools)}")

        # Verwende verfügbares Tool (falls vorhanden)
        if tools:
            tool_result = await client.use_tool(
                tools[0]["name"],
                **{"target": "system", "check_type": "basic"}
            )
            print(f"Tool-Result: {tool_result}")

        # Asynchrone Bus-Operation - Konkrete Implementierung
        bus_result = await client.execute_agent_operation(
            "async_health_check",
            {
                "target_agent": "monitoring-agent",
                "message_type": "health_check_request",
                "payload": {"scope": "basic", "timeout": 30}
            },
            protocol=ProtocolType.BUS
        )
        print(f"Bus-Result: {bus_result}")

asyncio.run(multi_protocol_example())
```

### Enterprise Features

```python
import time
from kei_agent import (
    get_logger,
    get_health_manager,
    LogContext,
    APIHealthCheck,
    MemoryHealthCheck,
    HealthStatus
)

# Structured Logging
logger = get_logger("enterprise_agent")
# create_correlation_id() setzt bereits den Kontext
correlation_id = logger.create_correlation_id()
logger.set_context(LogContext(
    user_id="user-123",
    agent_id="enterprise-agent"
))

# Health Monitoring
health_manager = get_health_manager()
health_manager.register_check(APIHealthCheck(
    name="external_api",
    url="https://api.external.com/health"
))
health_manager.register_check(MemoryHealthCheck(
    name="system_memory",
    warning_threshold=0.8
))

async def enterprise_example():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="enterprise-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Operation mit Logging
        operation_id = logger.log_operation_start("business_process")
        start_time = time.time()

        try:
            result = await client.plan_task("Enterprise task")
            logger.log_operation_end("business_process", operation_id, start_time, success=True)

            # Health Check
            summary = await health_manager.run_all_checks()
            logger.info(
                "Health check completed",
                overall_status=summary.overall_status.value,
                healthy_count=summary.healthy_count,
            )

        except Exception as e:
            logger.log_operation_end("business_process", operation_id, start_time, success=False)
            logger.error("Business process failed", error=str(e))
            raise

asyncio.run(enterprise_example())
```

## 🏗️ Architektur

Das SDK folgt einer modularen, Enterprise-Grade Architektur:

```
kei_agent/
├── unified_client_refactored.py    # Haupt-API-Klasse
├── protocol_types.py               # Typ-Definitionen und Konfigurationen
├── security_manager.py             # Authentifizierung und Token-Management
├── protocol_clients.py             # KEI-RPC, Stream, Bus, MCP Clients
├── protocol_selector.py            # Intelligente Protokoll-Auswahl
├── enterprise_logging.py           # Strukturiertes JSON-Logging
├── health_checks.py               # System-Monitoring und Health-Checks
└── input_validation.py            # Input-Validierung und Sanitization
```

### Design-Prinzipien

- **Clean Code**: Alle Module ≤200 Zeilen, Funktionen ≤20 Zeilen
- **Type Safety**: 100% Type Hints für alle öffentlichen APIs
- **Single Responsibility**: Jedes Modul hat eine klar definierte Verantwortlichkeit
- **Async-First**: Non-blocking I/O für maximale Performance
- **Enterprise-Ready**: Production-Monitoring und Security-Hardening

## 📚 Dokumentation

- **[Vollständige Dokumentation](https://oscharko-dev.github.io/kei-agent-py-sdk/)** - Umfassende Guides und API-Referenz

## 🔧 Konfiguration

### Basis-Konfiguration

```python
from kei_agent import AgentClientConfig, ProtocolConfig, SecurityConfig, AuthType

# Agent-Konfiguration
agent_config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token="your-api-token",
    agent_id="my-agent",
    timeout=30,
    max_retries=3
)

# Protokoll-Konfiguration
protocol_config = ProtocolConfig(
    rpc_enabled=True,
    stream_enabled=True,
    bus_enabled=True,
    mcp_enabled=True,
    auto_protocol_selection=True,
    protocol_fallback_enabled=True
)

# Sicherheitskonfiguration
security_config = SecurityConfig(
    auth_type=AuthType.BEARER,
    api_token="your-api-token",
    rbac_enabled=True,
    audit_enabled=True
)

# Client mit vollständiger Konfiguration
client = UnifiedKeiAgentClient(
    config=agent_config,
    protocol_config=protocol_config,
    security_config=security_config
)
```

### Umgebungsvariablen

```bash
export KEI_API_URL="https://api.kei-framework.com"
export KEI_API_TOKEN="your-api-token"
export KEI_AGENT_ID="my-agent"
export KEI_AUTH_TYPE="bearer"
export KEI_RBAC_ENABLED="true"
export KEI_AUDIT_ENABLED="true"
```

## 🧪 Testing

```bash
# Unit Tests ausführen
python -m pytest tests/ -v

# Mit Coverage
python -m pytest tests/ --cov=kei_agent --cov-report=html

# Spezifische Test-Kategorien
python -m pytest tests/ -m "unit"          # Unit Tests
python -m pytest tests/ -m "integration"   # Integration Tests
python -m pytest tests/ -m "security"      # Security Tests

# Performance Tests
python -m pytest tests/ -m "performance"
```

## 🤝 Contributing

Wir freuen uns über Beiträge! Bitte lesen Sie unseren [Development Guide](docs/development/index.md) und die [Contribution-Hinweise](PRE_COMMIT_SETUP.md).

### Development Setup

```bash
# Repository klonen
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk

# Development-Umgebung einrichten
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -e ".[dev,docs,security]"

# Pre-commit hooks installieren
pre-commit install

# Tests ausführen
make test

# Dokumentation erstellen
mkdocs build --strict
```

## 📄 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

## 🔗 Links

- **GitHub Repository**: [oscharko-dev/kei-agent-py-sdk](https://github.com/oscharko-dev/kei-agent-py-sdk)
- **TestPyPI Package**: [kei-agent-py-sdk](https://test.pypi.org/project/kei-agent-py-sdk/)
- **Dokumentation**: [GitHub Pages](https://oscharko-dev.github.io/kei-agent-py-sdk/)
- **Issues**: [GitHub Issues](https://github.com/oscharko-dev/kei-agent-py-sdk/issues)

## 📊 Status

- ✅ **Production Ready**: Vollständig getestet und dokumentiert
- ✅ **Type Safe**: 100% Type Hints für alle APIs
- ✅ **Enterprise Grade**: Security, Monitoring und Compliance-Features
- ✅ **Well Documented**: Umfassende deutsche Dokumentation
- ✅ **Actively Maintained**: Regelmäßige Updates und Support

---

**Bereit loszulegen?** Installieren Sie das SDK und folgen Sie unserem [Quick Start Guide](https://oscharko-dev.github.io/kei-agent-py-sdk/getting-started/quickstart/)!

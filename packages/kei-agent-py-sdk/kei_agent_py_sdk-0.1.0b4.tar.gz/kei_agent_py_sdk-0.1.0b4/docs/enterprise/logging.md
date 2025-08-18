# Structured Logging

*Diese Seite wird noch entwickelt.*

## Übersicht

Enterprise-Grade Structured Logging für das KEI-Agent SDK.

## Features

- **Structured JSON Logging**: Maschinenlesbare Log-Ausgaben
- **Correlation IDs**: Verfolgung von Requests über Service-Grenzen
- **Performance Metrics**: Automatische Latenz- und Durchsatz-Messungen
- **Security Audit**: Sicherheitsrelevante Events

## Verwendung

```python
from kei_agent import get_logger

logger = get_logger("my-component")
logger.info("Operation started", extra={
    "operation": "plan_task",
    "agent_id": "my-agent",
    "correlation_id": "req-123"
})
```

## Konfiguration

```python
logging_config = {
    "level": "INFO",
    "format": "json",
    "correlation_enabled": True,
    "audit_enabled": True
}
```

## Weitere Informationen

- [Health Checks](health-checks.md)
- [Monitoring](monitoring.md)

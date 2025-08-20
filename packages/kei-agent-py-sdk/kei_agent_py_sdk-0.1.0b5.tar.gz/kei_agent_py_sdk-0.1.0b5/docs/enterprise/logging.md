# Structured Logging

Enterprise-Grade Structured Logging für das KEI-Agent SDK.

## 🚀 Features

- **Structured JSON**: Maschinenlesbare Log-Ausgaben
- **Correlation IDs**: Request-Verfolgung über Service-Grenzen
- **Performance Metrics**: Automatische Latenz-Messungen
- **Security Audit**: Sicherheitsrelevante Events

## 📊 Verwendung

```python
from kei_agent import get_logger, LogContext

# Logger erstellen
logger = get_logger("my-component")

# Kontext setzen
correlation_id = logger.create_correlation_id()
logger.set_context(LogContext(
    user_id="user-123",
    agent_id="my-agent",
    operation="plan_task"
))

# Logging
logger.info("Operation gestartet")
logger.error("Fehler aufgetreten", error="Connection failed")
```

## ⚡ Performance Logging

```python
import time

# Operation-Timing
operation_id = logger.log_operation_start("plan_creation")

try:
    # Business Logic
    result = await client.plan_task("Demo-Plan")

    # Success Logging
    logger.log_operation_end("plan_creation", operation_id, time.time(), success=True)
    logger.info("Plan erfolgreich erstellt", plan_id=result.get('plan_id'))

except Exception as e:
    # Error Logging
    logger.log_operation_end("plan_creation", operation_id, time.time(), success=False)
    logger.error("Plan-Erstellung fehlgeschlagen", error=str(e))
```

## 🔒 Security Logging

```python
# Security Events
logger.log_security_event(
    event_type="authentication_failure",
    severity="high",
    description="Invalid login attempt",
    user_id="user-123",
    ip_address="192.168.1.100"
)

# Audit Events
logger.log_audit_event(
    action="agent_task_execution",
    resource="agent-456",
    user_id="user-123",
    result="success"
)
```

## 🔧 Konfiguration

```python
from kei_agent import configure_logging

# Logging konfigurieren
logger = configure_logging(
    level="INFO",
    enable_structured=True,
    enable_file=True,
    file_path="/var/log/kei-agent.log",
    extra_fields={
        "service": "kei-agent",
        "environment": "production",
        "version": "1.0.0"
    }
)
```

---

**Weitere Informationen:** [Health Checks](health-checks.md) | [Security](security.md)

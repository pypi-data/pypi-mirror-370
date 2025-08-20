# Health Checks

Umfassende Health Check-Funktionalität für produktive Umgebungen.

## 🚀 Features

- **System Health**: CPU, Memory, Disk Usage
- **Service Health**: API-Endpunkte und externe Services
- **Custom Checks**: Anwendungsspezifische Prüfungen
- **Kubernetes**: Readiness/Liveness-kompatible Endpoints

## 📊 Verwendung

```python
from kei_agent import get_health_manager, APIHealthCheck, MemoryHealthCheck

# Health Manager konfigurieren
health = get_health_manager()

# Checks registrieren
health.register_check(APIHealthCheck(
    name="kei_api",
    url="https://api.kei-framework.com/health"
))

health.register_check(MemoryHealthCheck(
    name="system_memory",
    warning_threshold=0.8,
    critical_threshold=0.95
))

# Health Check ausführen
summary = await health.run_all_checks()
print(f"Gesamtstatus: {summary.overall_status}")

for check in summary.checks:
    print(f"  {check.name}: {check.status}")
```

## 🔧 Custom Health Checks

```python
from kei_agent import BaseHealthCheck, HealthStatus

class DatabaseHealthCheck(BaseHealthCheck):
    def __init__(self, connection_string: str):
        super().__init__("database")
        self.connection_string = connection_string

    async def check(self) -> HealthStatus:
        try:
            # Database-Verbindung testen
            # ... connection logic ...
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNHEALTHY

# Registrieren
health.register_check(DatabaseHealthCheck("postgresql://..."))
```

## 🐳 Kubernetes Integration

```yaml
# Deployment mit Health Checks
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

**Weitere Informationen:** [Logging](logging.md) | [Monitoring](monitoring.md)

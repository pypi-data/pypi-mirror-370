# Health Checks

*Diese Seite wird noch entwickelt.*

## Übersicht

Umfassende Health Check-Funktionalität für produktive Umgebungen.

## Features

- **System Health**: CPU, Memory, Disk Usage
- **Service Health**: Abhängigkeiten und externe Services
- **Custom Checks**: Anwendungsspezifische Gesundheitsprüfungen
- **Readiness/Liveness**: Kubernetes-kompatible Endpoints

## Verwendung

```python
from kei_agent import get_health_manager

health = get_health_manager()
status = await health.check_health()

print(f"System Health: {status.overall}")
for check in status.checks:
    print(f"  {check.name}: {check.status}")
```

## Health Check Endpoints

- `/health` - Allgemeine Gesundheit
- `/health/ready` - Readiness Check
- `/health/live` - Liveness Check

## Weitere Informationen

- [Logging](logging.md)
- [Monitoring](monitoring.md)

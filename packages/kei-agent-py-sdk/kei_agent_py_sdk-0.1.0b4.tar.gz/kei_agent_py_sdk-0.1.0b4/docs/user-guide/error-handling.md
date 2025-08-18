# Fehlerbehandlung

*Diese Seite wird noch entwickelt.*

## Übersicht

Robuste Fehlerbehandlung und Retry-Strategien im KEI-Agent SDK.

## Exception-Hierarchie

```python
from kei_agent.exceptions import (
    KeiSDKError,
    ProtocolError,
    SecurityError,
    ValidationError
)

try:
    result = await client.plan_task("task")
except ProtocolError as e:
    print(f"Protokoll-Fehler: {e}")
except SecurityError as e:
    print(f"Sicherheits-Fehler: {e}")
except KeiSDKError as e:
    print(f"Allgemeiner SDK-Fehler: {e}")
```

## Retry-Strategien

Das SDK bietet automatische Retry-Mechanismen für transiente Fehler.

## Weitere Informationen

- [Basis-Konzepte](concepts.md)
- [Client-Verwendung](client-usage.md)

# Client-Verwendung

## Übersicht

Dieser Leitfaden zeigt praktische Patterns für den `UnifiedKeiAgentClient` inklusive Konfiguration, Protokollwahl und Enterprise-Features.

## Grundlegende Verwendung

```python
import asyncio
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

async def main():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="your-agent-id"
    )
    async with UnifiedKeiAgentClient(config=config) as client:
        plan = await client.plan_task("Ihre Aufgabe")
        print(plan)

asyncio.run(main())
```

## Protokoll explizit wählen

```python
from kei_agent import ProtocolType

async def run_with_stream(client: UnifiedKeiAgentClient):
    await client.execute_agent_operation(
        "subscribe",
        {"topic": "agent_events"},
        protocol=ProtocolType.STREAM
    )
```

## Enterprise-Logger verwenden

```python
from kei_agent import get_logger, LogContext

logger = get_logger("client-usage")
logger.set_context(LogContext(correlation_id=logger.create_correlation_id(), user_id="u-1"))
```

## Health-Checks ausführen

```python
from kei_agent import get_health_manager, APIHealthCheck

health = get_health_manager()
health.register_check(APIHealthCheck(name="kei_api", url="https://api.kei-framework.com/health"))
summary = await health.run_all_checks()
print(summary.overall_status)
```

## Weitere Informationen

- [Basis-Konzepte](concepts.md)
- [Protokolle](protocols.md)
- [Authentifizierung](authentication.md)

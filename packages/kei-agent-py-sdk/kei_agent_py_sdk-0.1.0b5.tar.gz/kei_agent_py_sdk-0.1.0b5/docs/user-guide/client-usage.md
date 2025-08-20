# Client-Verwendung

Praktische Patterns für den `UnifiedKeiAgentClient`.

## 🚀 Grundlegende Verwendung

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

## 🔌 Protokoll-Auswahl

```python
from kei_agent import ProtocolType

# Explizite Protokoll-Wahl
await client.execute_agent_operation(
    "subscribe",
    {"topic": "agent_events"},
    protocol=ProtocolType.STREAM
)
```

## 📊 Enterprise Features

```python
from kei_agent import get_logger, get_health_manager, APIHealthCheck

# Logging
logger = get_logger("client-usage")
logger.info("Operation gestartet")

# Health Checks
health = get_health_manager()
health.register_check(APIHealthCheck(name="kei_api", url="https://api.kei-framework.com/health"))
summary = await health.run_all_checks()
print(f"Status: {summary.overall_status}")
```

---

**Weitere Informationen:** [Konzepte](concepts.md) | [Protokolle](protocols.md)

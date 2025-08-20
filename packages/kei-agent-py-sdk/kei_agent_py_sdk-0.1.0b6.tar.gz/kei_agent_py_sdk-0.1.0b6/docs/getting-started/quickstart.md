# Quick Start

5-Minuten-Einstieg in das KEI-Agent SDK.

## 🚀 Erster Agent

```python
import asyncio
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

async def main():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="my-first-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        print("🎉 Client verbunden!")

        # Client-Info
        info = client.get_client_info()
        print(f"Agent ID: {info['agent_id']}")

asyncio.run(main())
```
## 🛠️ Tool-Integration

```python
from kei_agent import CapabilityManager, CapabilityProfile

async def tool_example():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-token",
        agent_id="tool-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Tool definieren
        async def system_info_tool(**kwargs):
            return {"status": "healthy", "cpu": "25%"}

        # Tool registrieren
        capability_manager = CapabilityManager(client._legacy_client)
        await capability_manager.register_capability(
            CapabilityProfile(
                name="system_info",
                version="1.0.0",
                description="System-Informationen"
            ),
            handler=system_info_tool
        )

        # Tool verwenden
        result = await client.use_tool("system_info")
        print(f"Tool-Ergebnis: {result}")

asyncio.run(tool_example())
## 🔌 Protokolle

```python
from kei_agent import ProtocolType

async def protocol_demo():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-token",
        agent_id="protocol-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # RPC für synchrone Operationen
        plan = await client.plan_task(
            objective="System-Check",
            context={"type": "basic"}
        )

        # Stream für Echtzeit-Daten
        stream_result = await client.execute_agent_operation(
            "monitor_stream",
            {"duration": 10},
            protocol=ProtocolType.STREAM
        )

        print(f"Plan: {plan['plan_id']}")
        print(f"Stream: {stream_result}")

asyncio.run(protocol_demo())
## 🛡️ Enterprise Features

```python
from kei_agent import get_logger, get_health_manager, get_input_validator

async def enterprise_demo():
    # Logging
    logger = get_logger("my_agent")
    logger.info("Operation gestartet")

    # Health Checks
    health_manager = get_health_manager()
    summary = await health_manager.run_all_checks()
    print(f"System-Status: {summary.overall_status.value}")

    # Input Validation
    validator = get_input_validator()
    result = validator.validate_agent_operation("plan", {"objective": "Test"})
    print(f"Validierung: {'✅' if result.valid else '❌'}")

asyncio.run(enterprise_demo())
```

## 🚨 Fehlerbehandlung

```python
from kei_agent.exceptions import KeiSDKError, ProtocolError, SecurityError

async def error_demo():
    try:
        # Fehlerhafter Client
        config = AgentClientConfig(base_url="invalid", api_token="invalid", agent_id="test")
        async with UnifiedKeiAgentClient(config=config) as client:
            await client.plan_task("Test")
    except SecurityError as e:
        print(f"🔒 Sicherheitsfehler: {e}")
    except ProtocolError as e:
        print(f"🔌 Protokollfehler: {e}")
    except KeiSDKError as e:
        print(f"⚠️ SDK-Fehler: {e}")

asyncio.run(error_demo())
```

---

**Nächste Schritte:** [Konzepte](../user-guide/concepts.md) | [Konfiguration](configuration.md)

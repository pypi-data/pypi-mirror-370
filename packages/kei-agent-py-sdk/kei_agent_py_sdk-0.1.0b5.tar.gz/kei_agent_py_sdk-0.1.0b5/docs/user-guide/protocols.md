# Protokolle

Multi-Protocol-Unterstützung des KEI-Agent SDK.

## 🔌 Unterstützte Protokolle

### RPC (Remote Procedure Call)
- **Synchrone** Request-Response-Kommunikation
- HTTP-basiert mit JSON-Payloads

```python
# RPC-Beispiel
result = await client.plan_task("Analysiere Daten")
```

### Stream (WebSocket)
- **Bidirektionale** Echtzeit-Kommunikation
- WebSocket-basiert

```python
# Stream-Beispiel
await client.execute_agent_operation(
    "monitor_stream",
    {"duration": 10},
    protocol=ProtocolType.STREAM
)
```

### Bus (Message Bus)
- **Asynchrone** Publish-Subscribe-Kommunikation
- Event-basierte Architektur

```python
# Bus-Beispiel
await client.send_agent_message("target-agent", "task_request", data)
```

### MCP (Model Context Protocol)
- **Tool-Discovery** und -Verwendung
- KI-Model-Integration

```python
# MCP-Beispiel
tools = await client.discover_available_tools()
result = await client.use_tool("calculator", expression="2+2")
```

## ⚙️ Protokoll-Konfiguration

```python
from kei_agent import ProtocolConfig

config = ProtocolConfig(
    rpc_enabled=True,
    stream_enabled=True,
    bus_enabled=True,
    mcp_enabled=True,
    auto_protocol_selection=True
)
```

---

**Weitere Informationen:** [Konzepte](concepts.md) | [Client-Verwendung](client-usage.md)

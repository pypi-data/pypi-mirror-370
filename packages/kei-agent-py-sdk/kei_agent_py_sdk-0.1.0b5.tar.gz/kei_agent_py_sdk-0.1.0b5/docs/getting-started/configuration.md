# Konfiguration

Client-Setup und Konfigurationsoptionen für das KEI-Agent SDK.

## 🔧 Basis-Konfiguration

```python
from kei_agent import AgentClientConfig

config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token="your-api-token",
    agent_id="my-agent",
    timeout=30,
    max_retries=3
)
```

## 🔌 Protokoll-Konfiguration

```python
from kei_agent import ProtocolConfig

protocol_config = ProtocolConfig(
    rpc_enabled=True,
    stream_enabled=True,
    bus_enabled=True,
    mcp_enabled=True,
    auto_protocol_selection=True
```

## 🛡️ Sicherheit

```python
from kei_agent import SecurityConfig, AuthType

security_config = SecurityConfig(
    auth_type=AuthType.BEARER,
    api_token="your-token",
    rbac_enabled=True,
    audit_enabled=True
```

## 🌍 Umgebungen

```python
import os

# Development
dev_config = AgentClientConfig(
    base_url="http://localhost:8000",
    api_token=os.getenv("KEI_API_TOKEN"),
    agent_id="dev-agent",
    timeout=10
)

# Production
prod_config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token=os.getenv("KEI_API_TOKEN"),
    agent_id="prod-agent",
    timeout=30,
    max_retries=5
)
```

## 🔐 Umgebungsvariablen

```bash
export KEI_API_URL="https://api.kei-framework.com"
export KEI_API_TOKEN="your-api-token"
export KEI_AGENT_ID="my-agent"
```

## ✅ Validierung

```python
async def validate_config():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="test-token",
        agent_id="test"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        info = client.get_client_info()
        print(f"✅ Client: {info['agent_id']}")

asyncio.run(validate_config())
```

---

**Nächster Schritt:** [Konzepte →](../user-guide/concepts.md)

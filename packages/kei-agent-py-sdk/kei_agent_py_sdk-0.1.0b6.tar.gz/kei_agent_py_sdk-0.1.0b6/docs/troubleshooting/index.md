# Troubleshooting

Lösungen für häufige Probleme und Debugging-Strategien für das KEI-Agent Python SDK.

## 🚨 Häufige Probleme

### Installation & Setup

#### Problem: ModuleNotFoundError

```bash
ModuleNotFoundError: No module named 'kei_agent'
```

**Ursachen & Lösungen:**

1. **SDK nicht installiert**

   ```bash
   pip install kei_agent_py_sdk
   ```

2. **Falsche virtuelle Umgebung**

   ```bash
   # Virtuelle Umgebung aktivieren
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

   # SDK installieren
   pip install kei_agent_py_sdk
   ```

3. **Python-Path-Problem**

   ```python
   import sys
   print(sys.path)  # Prüfe Python-Path

   # Temporärer Fix
   sys.path.append('/path/to/kei-agent')
   ```

#### Problem: Version-Konflikte

```bash
ERROR: pip's dependency resolver does not currently consider all the ways...
```

**Lösungen:**

1. **Dependency-Resolver verwenden**

   ```bash
   pip install --use-feature=2020-resolver kei_agent_py_sdk
   ```

2. **Pip aktualisieren**

   ```bash
   pip install --upgrade pip
   pip install kei_agent_py_sdk
   ```

3. **Saubere Installation**
   ```bash
   pip uninstall kei_agent_py_sdk
   pip cache purge
   pip install kei_agent_py_sdk
   ```

### Client-Initialisierung

#### Problem: Client nicht initialisiert

```python
RuntimeError: Client nicht initialisiert. Rufen Sie initialize() auf oder verwenden Sie async context manager.
```

**Lösung:**

```python
# ✅ Empfohlen: Async Context Manager
async with UnifiedKeiAgentClient(config=config) as client:
    result = await client.plan_task("objective")

# ✅ Alternative: Manuelle Initialisierung
client = UnifiedKeiAgentClient(config=config)
try:
    await client.initialize()
    result = await client.plan_task("objective")
finally:
    await client.close()
```

#### Problem: Ungültige Konfiguration

```python
ValidationError: Ungültige Sicherheitskonfiguration: API Token ist erforderlich für Bearer Auth
```

**Lösung:**

```python
# ✅ Vollständige Konfiguration
config = AgentClientConfig(
    base_url="https://api.kei-framework.com",
    api_token="your-api-token",  # Erforderlich!
    agent_id="unique-agent-id"   # Erforderlich!
)

# ✅ Umgebungsvariablen verwenden
import os
config = AgentClientConfig(
    base_url=os.getenv("KEI_API_URL"),
    api_token=os.getenv("KEI_API_TOKEN"),
    agent_id=os.getenv("KEI_AGENT_ID")
)
```

### Authentifizierung

#### Problem: 401 Unauthorized

```python
SecurityError: Authentifizierung fehlgeschlagen: 401 Unauthorized
```

**Debugging-Schritte:**

1. **Token validieren**

   ```python
   # Token-Format prüfen
   print(f"Token length: {len(api_token)}")
   print(f"Token starts with: {api_token[:10]}...")

   # Token-Gültigkeit testen
   import httpx
   response = httpx.get(
       "https://api.kei-framework.com/auth/validate",
       headers={"Authorization": f"Bearer {api_token}"}
   )
   print(f"Token validation: {response.status_code}")
   ```

2. **OIDC-Konfiguration prüfen**

   ```python
   # OIDC-Endpunkte testen
   import httpx
   response = httpx.get(f"{oidc_issuer}/.well-known/openid_configuration")
   print(f"OIDC discovery: {response.status_code}")
   ```

3. **mTLS-Zertifikate prüfen**
   ```bash
   # Zertifikat-Gültigkeit prüfen
   openssl x509 -in client.crt -text -noout
   openssl rsa -in client.key -check
   ```

#### Problem: Token-Refresh fehlgeschlagen

```python
SecurityError: OIDC Token-Request fehlgeschlagen: 400 Bad Request
```

**Lösungen:**

1. **OIDC-Konfiguration validieren**

   ```python
   security_config = SecurityConfig(
       auth_type=AuthType.OIDC,
       oidc_issuer="https://auth.example.com",  # Korrekte URL
       oidc_client_id="valid-client-id",
       oidc_client_secret="valid-client-secret",
       oidc_scope="openid profile kei-agent"    # Korrekte Scopes
   )
   ```

2. **Netzwerk-Konnektivität prüfen**
   ```python
   import httpx
   async with httpx.AsyncClient() as client:
       response = await client.get(oidc_issuer)
       print(f"OIDC issuer reachable: {response.status_code}")
   ```

### Protokoll-Probleme

#### Problem: Protokoll nicht verfügbar

```python
ProtocolError: Stream-Protokoll nicht verfügbar
```

**Debugging:**

```python
# Verfügbare Protokolle prüfen
client = UnifiedKeiAgentClient(config=config)
protocols = client.get_available_protocols()
print(f"Available protocols: {protocols}")

# Protokoll-Konfiguration prüfen
info = client.get_client_info()
print(f"Protocol config: {info['protocol_config']}")

# Spezifisches Protokoll prüfen
if client.is_protocol_available(ProtocolType.STREAM):
    print("Stream protocol available")
else:
    print("Stream protocol not available")
```

**Lösung:**

```python
# Protokoll explizit aktivieren
protocol_config = ProtocolConfig(
    stream_enabled=True,  # Explizit aktivieren
    auto_protocol_selection=True
)

client = UnifiedKeiAgentClient(
    config=config,
    protocol_config=protocol_config
)
```

#### Problem: WebSocket-Verbindung fehlgeschlagen

```python
ProtocolError: Stream-Verbindung fehlgeschlagen: Connection refused
```

**Debugging-Schritte:**

1. **WebSocket-Endpunkt prüfen**

   ```python
   import websockets

   async def test_websocket():
       try:
           async with websockets.connect("wss://api.kei-framework.com/ws") as ws:
               print("WebSocket connection successful")
       except Exception as e:
           print(f"WebSocket connection failed: {e}")

   asyncio.run(test_websocket())
   ```

2. **Firewall/Proxy prüfen**

   ```bash
   # Netzwerk-Konnektivität testen
   telnet api.kei-framework.com 443
   curl -I https://api.kei-framework.com/ws
   ```

3. **SSL-Zertifikate prüfen**
   ```bash
   openssl s_client -connect api.kei-framework.com:443
   ```

### Performance-Probleme

#### Problem: Langsame Responses

```python
# Response-Zeit messen
import time

start_time = time.time()
result = await client.plan_task(
    objective="System-Health-Check durchführen",
    context={"scope": "basic"}
)
duration = time.time() - start_time
print(f"Response time: {duration:.2f}s")
```

**Optimierungen:**

1. **Timeout anpassen**

   ```python
   from kei_agent import ConnectionConfig

   config = AgentClientConfig(
       base_url="https://api.kei-framework.com",
       api_token="your-token",
       agent_id="agent",
       connection=ConnectionConfig(timeout=60.0)  # Erhöhter Timeout
   )
   ```

2. **Connection Pooling optimieren**

   ```python
   # Wird automatisch vom SDK verwaltet
   # Bei Bedarf Client-Instanz wiederverwenden
   ```

3. **Protokoll-Auswahl optimieren**
   ```python
   # Für schnelle Operationen RPC verwenden
   result = await client.execute_agent_operation(
       "fast_operation",
       data,
       protocol=ProtocolType.RPC
   )
   ```

#### Problem: Memory Leaks

```python
import psutil
import gc

def monitor_memory():
    """Memory-Usage überwachen."""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")

    # Garbage Collection forcieren
    gc.collect()

    memory_after_gc = process.memory_info().rss / 1024 / 1024
    print(f"Memory after GC: {memory_after_gc:.2f} MB")

# Vor und nach Client-Operationen aufrufen
monitor_memory()
```

**Lösungen:**

1. **Async Context Manager verwenden**

   ```python
   # ✅ Automatisches Cleanup
   async with UnifiedKeiAgentClient(config=config) as client:
       result = await client.plan_task("objective")
   ```

2. **Explizites Cleanup**
   ```python
   client = UnifiedKeiAgentClient(config=config)
   try:
       await client.initialize()
       result = await client.plan_task("objective")
   finally:
       await client.close()  # Wichtig!
   ```

## 🔍 Debugging-Strategien

### Logging aktivieren

```python
import logging
from kei_agent import configure_logging

# Debug-Logging aktivieren
configure_logging(
    level=logging.DEBUG,
    enable_structured=True,
    enable_console=True
)

# Spezifische Logger konfigurieren
logging.getLogger("kei_agent").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("websockets").setLevel(logging.DEBUG)
```

### Request/Response Debugging

```python
import httpx

# HTTP-Client mit Logging
class DebugHTTPClient:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def request(self, method, url, **kwargs):
        print(f"🔍 {method} {url}")
        if 'json' in kwargs:
            print(f"📤 Request: {kwargs['json']}")

        response = await self.client.request(method, url, **kwargs)

        print(f"📥 Response: {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            print(f"📄 Body: {response.json()}")

        return response
```

### Health Check Debugging

```python
from kei_agent import get_health_manager

async def debug_health_checks():
    """Detailliertes Health Check Debugging."""

    health_manager = get_health_manager()
    summary = await health_manager.run_all_checks()

    print(f"Overall Status: {summary.overall_status}")
    print(f"Total Checks: {summary.total_checks}")

    for check in summary.checks:
        print(f"\n--- {check.name} ---")
        print(f"Status: {check.status}")
        print(f"Message: {check.message}")
        print(f"Duration: {check.duration_ms}ms")

        if check.error:
            print(f"Error: {check.error}")

        if check.details:
            print(f"Details: {check.details}")

asyncio.run(debug_health_checks())
```

### Network Debugging

```python
import socket
import ssl

def debug_network_connectivity(host: str, port: int = 443):
    """Netzwerk-Konnektivität debuggen."""

    try:
        # TCP-Verbindung testen
        sock = socket.create_connection((host, port), timeout=10)
        print(f"✅ TCP connection to {host}:{port} successful")

        if port == 443:
            # SSL-Verbindung testen
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            print(f"✅ SSL connection to {host} successful")
            print(f"SSL version: {ssl_sock.version()}")
            ssl_sock.close()
        else:
            sock.close()

    except socket.timeout:
        print(f"❌ Connection to {host}:{port} timed out")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed for {host}: {e}")
    except Exception as e:
        print(f"❌ Connection to {host}:{port} failed: {e}")

# Testen
debug_network_connectivity("api.kei-framework.com")
```

## 🛠️ Diagnostic Tools

### SDK-Diagnose-Script

```python
#!/usr/bin/env python3
"""KEI-Agent SDK Diagnose-Tool."""

import asyncio
import sys
import traceback
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    get_health_manager,
    get_logger
)

async def run_diagnostics():
    """Führt umfassende SDK-Diagnose aus."""

    print("🔍 KEI-Agent SDK Diagnostics")
    print("=" * 50)

    # 1. Import-Test
    try:
        import kei_agent
        print(f"✅ SDK Import: Version {kei_agent.__version__}")
    except Exception as e:
        print(f"❌ SDK Import failed: {e}")
        return False

    # 2. Konfiguration-Test
    try:
        config = AgentClientConfig(
            base_url="https://httpbin.org",  # Test-Endpunkt
            api_token="test-token",
            agent_id="diagnostic-agent"
        )
        print("✅ Configuration: Valid")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

    # 3. Client-Erstellung-Test
    try:
        client = UnifiedKeiAgentClient(config=config)
        info = client.get_client_info()
        print(f"✅ Client Creation: {info['agent_id']}")
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False

    # 4. Health Manager Test
    try:
        health_manager = get_health_manager()
        print("✅ Health Manager: Available")
    except Exception as e:
        print(f"❌ Health Manager failed: {e}")
        return False

    # 5. Logger Test
    try:
        logger = get_logger("diagnostic")
        logger.info("Diagnostic test message")
        print("✅ Logger: Working")
    except Exception as e:
        print(f"❌ Logger failed: {e}")
        return False

    print("\n🎉 All diagnostics passed!")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(run_diagnostics())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Diagnostic failed with exception: {e}")
        traceback.print_exc()
        sys.exit(1)
```

### Performance-Profiling

```python
import cProfile
import pstats
import asyncio

def profile_agent_operation():
    """Profiling für Agent-Operationen."""

    async def operation():
        config = AgentClientConfig(
            base_url="https://api.kei-framework.com",
            api_token="your-token",
            agent_id="profile-agent"
        )

        async with UnifiedKeiAgentClient(config=config) as client:
            return await client.plan_task("Profile test")

    # Profiling ausführen
    profiler = cProfile.Profile()
    profiler.enable()

    try:
        result = asyncio.run(operation())
    finally:
        profiler.disable()

    # Ergebnisse anzeigen
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 Funktionen

# Ausführen
profile_agent_operation()
```

---

**Weitere Troubleshooting-Ressourcen:**

- [Häufige Probleme →](common-issues.md) - Detaillierte Problemlösungen
- [Debugging →](debugging.md) - Erweiterte Debugging-Techniken
- [Performance →](performance.md) - Performance-Optimierung
- [Security →](security.md) - Sicherheits-Troubleshooting

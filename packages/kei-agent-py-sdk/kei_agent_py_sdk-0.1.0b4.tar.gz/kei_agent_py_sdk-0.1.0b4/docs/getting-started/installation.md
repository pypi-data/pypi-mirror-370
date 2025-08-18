# Installation

Diese Anleitung führt Sie durch die Installation des KEI-Agent Python SDK in verschiedenen Umgebungen.

## 📦 Installation mit pip

### Standard-Installation

Die einfachste Methode ist die Installation über PyPI:

```bash
pip install kei_agent_py_sdk
```

### Mit Enterprise-Features

Für vollständige Enterprise-Funktionalität installieren Sie alle optionalen Dependencies:

```bash
pip install "kei_agent_py_sdk[security,dev,docs]"
```

### Spezifische Version

```bash
# Neueste stabile Version
pip install "kei_agent_py_sdk>=0.1.0b1"

# Spezifische Version
pip install "kei_agent_py_sdk==0.1.0b1"

# Neueste Pre-Release
pip install --pre kei_agent_py_sdk
```

## 🐍 Installation mit conda

```bash
# Aus conda-forge (falls verfügbar)
conda install -c conda-forge kei_agent_py_sdk

# Oder mit pip in conda-Umgebung
conda create -n kei-agent python=3.11
conda activate kei-agent
pip install kei_agent_py_sdk
```

## 🔧 Development-Installation

Für Entwicklung und Beiträge zum SDK:

### Repository klonen

```bash
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk
```

### Editable Installation

```bash
# Mit allen Development-Dependencies
pip install -e ".[dev,docs,security]"

# Oder mit Make
make dev-setup
```

### Pre-Commit Hooks

```bash
pre-commit install
```

## 🐳 Docker-Installation

### Dockerfile-Beispiel

```dockerfile
FROM python:3.11-slim

# System-Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# KEI-Agent SDK
RUN pip install kei_agent_py_sdk

# Anwendung
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  kei-agent:
    build: .
    environment:
      - KEI_API_URL=https://api.kei-framework.com
      - KEI_API_TOKEN=${KEI_API_TOKEN}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## ✅ Installation verifizieren

### Basis-Verifikation

```python
import kei_agent
print(f"KEI-Agent SDK Version: {kei_agent.__version__}")
```

### Vollständige Verifikation

```python
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    ProtocolConfig,
    SecurityConfig,
    get_logger,
    get_health_manager
)

print("✅ Alle Hauptkomponenten erfolgreich importiert")

# Version und Features anzeigen
print(f"Version: {kei_agent.__version__}")
print(f"Verfügbare Features: {kei_agent.__all__[:5]}...")
```

### Test-Script

Erstellen Sie eine Datei `test_installation.py`:

```python
#!/usr/bin/env python3
"""Test-Script für KEI-Agent SDK Installation."""

import sys
import asyncio
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

async def test_installation():
    """Testet die SDK-Installation."""
    try:
        # Basis-Konfiguration
        config = AgentClientConfig(
            base_url="https://httpbin.org",  # Test-Endpunkt
            api_token="test-token",
            agent_id="installation-test"
        )

        # Client erstellen (ohne Verbindung)
        client = UnifiedKeiAgentClient(config=config)

        # Client-Info abrufen
        info = client.get_client_info()
        print(f"✅ Client erstellt: {info['agent_id']}")

        # Verfügbare Protokolle
        protocols = client.get_available_protocols()
        print(f"✅ Verfügbare Protokolle: {len(protocols)}")

        print("🎉 Installation erfolgreich!")
        return True

    except Exception as e:
        print(f"❌ Installation-Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_installation())
    sys.exit(0 if success else 1)
```

Ausführen:

```bash
python test_installation.py
```

## 🔧 Optionale Dependencies

### Security-Features

```bash
pip install "kei_agent_py_sdk[security]"
```

Enthält:

- `authlib` - OIDC-Authentifizierung
- `cryptography` - Kryptographische Funktionen
- `pyopenssl` - SSL/TLS-Unterstützung

### Development-Tools

```bash
pip install "kei_agent_py_sdk[dev]"
```

Enthält:

- `pytest` - Testing-Framework
- `ruff` - Linting und Formatierung
- `mypy` - Type-Checking
- `bandit` - Security-Linting

### Dokumentation

```bash
pip install "kei_agent_py_sdk[docs]"
```

Enthält:

- `mkdocs` - Dokumentations-Generator
- `mkdocs-material` - Material-Theme
- `mkdocstrings` - API-Dokumentation

## 🚨 Häufige Probleme

### Problem: ModuleNotFoundError

```bash
ModuleNotFoundError: No module named 'kei_agent'
```

**Lösung:**

```bash
# Virtuelle Umgebung aktivieren
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate     # Windows

# SDK neu installieren
pip install --upgrade kei_agent_py_sdk
```

### Problem: Version-Konflikte

```bash
ERROR: pip's dependency resolver does not currently consider all the ways...
```

**Lösung:**

```bash
# Dependency-Resolver verwenden
pip install --use-feature=2020-resolver kei_agent_py_sdk

# Oder neue pip-Version
pip install --upgrade pip
pip install kei_agent_py_sdk
```

### Problem: SSL-Zertifikat-Fehler

```bash
SSL: CERTIFICATE_VERIFY_FAILED
```

**Lösung:**

```bash
# Zertifikate aktualisieren (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Oder mit pip
pip install --trusted-host pypi.org --trusted-host pypi.python.org kei_agent_py_sdk
```

### Problem: Permission-Fehler

```bash
PermissionError: [Errno 13] Permission denied
```

**Lösung:**

```bash
# User-Installation
pip install --user kei_agent_py_sdk

# Oder virtuelle Umgebung verwenden
python -m venv venv
source venv/bin/activate
pip install kei_agent_py_sdk
```

## 🔄 Upgrade

### Auf neueste Version

```bash
pip install --upgrade kei_agent_py_sdk
```

### Upgrade mit Dependencies

```bash
pip install --upgrade "kei_agent_py_sdk[security,dev]"
```

### Upgrade-Verifikation

```python
import kei_agent
print(f"Neue Version: {kei_agent.__version__}")
```

## 🗑️ Deinstallation

```bash
pip uninstall kei_agent_py_sdk
```

Mit Dependencies:

```bash
# Liste installierter Packages
pip freeze | grep -E "(kei_agent_py_sdk|httpx|websockets|pydantic)"

# Manuell entfernen
pip uninstall kei_agent_py_sdk httpx websockets pydantic
```

---

**Nächster Schritt:** [Quick Start Guide →](quickstart.md)

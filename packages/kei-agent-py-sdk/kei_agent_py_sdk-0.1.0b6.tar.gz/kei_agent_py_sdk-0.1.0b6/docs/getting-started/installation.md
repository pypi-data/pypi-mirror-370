# Installation

## 📦 Standard-Installation

```bash
pip install kei_agent_py_sdk
```

## 🔧 Mit Enterprise-Features

```bash
pip install "kei_agent_py_sdk[security,dev,docs]"
```

## 🐍 Conda

```bash
conda create -n kei-agent python=3.11
conda activate kei-agent
pip install kei_agent_py_sdk
```

## 🔧 Development

```bash
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk
pip install -e ".[dev,docs,security]"
```

## 🐳 Docker

```dockerfile
FROM python:3.11-slim
RUN pip install kei_agent_py_sdk
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]
```

## ✅ Verifikation

```python
import kei_agent
print(f"Version: {kei_agent.__version__}")

# Test-Client
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
config = AgentClientConfig(base_url="test", api_token="test", agent_id="test")
client = UnifiedKeiAgentClient(config=config)
print("✅ Installation erfolgreich!")
```

## 🚨 Häufige Probleme

**ModuleNotFoundError**: Virtuelle Umgebung aktivieren und `pip install --upgrade kei_agent_py_sdk`

**Permission-Fehler**: `pip install --user kei_agent_py_sdk` oder virtuelle Umgebung verwenden

**SSL-Fehler**: `pip install --trusted-host pypi.org kei_agent_py_sdk`

## 🔄 Upgrade

```bash
pip install --upgrade kei_agent_py_sdk
```

---

**Nächster Schritt:** [Quick Start →](quickstart.md)

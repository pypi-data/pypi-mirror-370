# ⚠️ Breaking Changes

Übersicht über Breaking Changes zwischen Keiko Personal Assistant Versionen.

## 🔄 v1.x → v2.0 Breaking Changes

### 🏗️ Architektur-Änderungen

#### Agent-System Refactoring

**v1.x (Deprecated)**
```python
# Alte Agent-Klasse
class Agent:
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    def execute(self, task: dict) -> dict:
        # Synchrone Ausführung
        return {"result": "completed"}

# Alte Verwendung
agent = Agent("text-processor", {"type": "nlp"})
result = agent.execute({"text": "Hello World"})
```

**v2.0 (New)**
```python
# Neue Agent-Klasse
class Agent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = generate_uuid()

    async def execute_task(self, task: Task) -> TaskResult:
        # Asynchrone Ausführung
        return TaskResult.success({"result": "completed"})

# Neue Verwendung
config = AgentConfig(
    name="text-processor",
    type=AgentType.SPECIALIST,
    capabilities=["text_processing"]
)
agent = Agent(config)
result = await agent.execute_task(task)
```

**Migration-Schritte:**
1. Ersetzen Sie `dict`-basierte Konfiguration durch `AgentConfig`
2. Konvertieren Sie synchrone `execute()` zu asynchronem `execute_task()`
3. Verwenden Sie `Task` und `TaskResult` Objekte statt `dict`

#### Database-Schema-Änderungen

**Entfernte Tabellen:**
- `agent_configs` → Migriert zu `agents.configuration` (JSONB)
- `task_logs` → Migriert zu `audit_logs`
- `user_sessions` → Ersetzt durch JWT-Token

**Neue Tabellen:**
- `mcp_servers` - MCP-Server-Registrierung
- `audit_logs` - Umfassendes Audit-Logging
- `protocol_configs` - Protocol-Konfigurationen

**Schema-Migration:**
```sql
-- Entfernte Spalten
ALTER TABLE users DROP COLUMN IF EXISTS session_token;
ALTER TABLE agents DROP COLUMN IF EXISTS config_json;

-- Neue Spalten
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';
ALTER TABLE agents ADD COLUMN capabilities JSONB DEFAULT '[]';
ALTER TABLE agents ADD COLUMN metadata JSONB DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'normal';
ALTER TABLE tasks ADD COLUMN timeout_seconds INTEGER DEFAULT 300;
```

### 🔌 API-Änderungen

#### REST-API-Endpunkte

**Entfernte Endpunkte:**
- `GET /api/agents/{id}/config` → Verwenden Sie `GET /api/v1/agents/{id}`
- `POST /api/tasks/execute` → Verwenden Sie `POST /api/v1/agents/{id}/tasks`
- `GET /api/status` → Verwenden Sie `GET /health`

**Geänderte Endpunkte:**
```python
# v1.x
POST /api/agents
{
    "name": "agent-name",
    "type": "nlp",
    "config": {...}
}

# v2.0
POST /api/v1/agents
{
    "name": "agent-name",
    "type": "specialist",
    "capabilities": ["text_processing"],
    "configuration": {...}
}
```

**Neue Endpunkte:**
- `GET /api/v1/mcp/servers` - MCP-Server-Management
- `POST /api/v1/protocols/select` - Protocol-Selection
- `GET /api/v1/audit/logs` - Audit-Log-Zugriff

#### Response-Format-Änderungen

**v1.x Response:**
```json
{
    "status": "success",
    "data": {...},
    "message": "Operation completed"
}
```

**v2.0 Response:**
```json
{
    "success": true,
    "data": {...},
    "metadata": {
        "request_id": "uuid",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "2.0.0"
    }
}
```

### 🔧 Konfigurations-Änderungen

#### Environment-Variablen

**Entfernte Variablen:**
- `KEIKO_AGENT_CONFIG_PATH` → Verwenden Sie `KEIKO_CONFIG_PATH`
- `KEIKO_LOG_FILE` → Verwenden Sie `KEIKO_LOG_CONFIG`
- `KEIKO_DB_POOL_SIZE` → Verwenden Sie `DATABASE_POOL_SIZE`

**Neue Variablen:**
- `KEIKO_MCP_SERVERS_CONFIG` - MCP-Server-Konfiguration
- `KEIKO_PROTOCOL_SELECTOR_CONFIG` - Protocol-Selection-Konfiguration
- `KEIKO_AUDIT_LOG_LEVEL` - Audit-Logging-Level

**Geänderte Variablen:**
```bash
# v1.x
KEIKO_AGENTS_PATH=/opt/keiko/agents
KEIKO_TASKS_PATH=/opt/keiko/tasks

# v2.0
KEIKO_CONFIG_PATH=/opt/keiko/config
KEIKO_DATA_PATH=/opt/keiko/data
```

#### Konfigurationsdatei-Format

**v1.x config.yml:**
```yaml
server:
  host: 0.0.0.0
  port: 8000

database:
  url: postgresql://...
  pool_size: 10

agents:
  - name: agent1
    type: nlp
    config:
      model: gpt-3.5
```

**v2.0 config.yml:**
```yaml
version: "2.0.0"
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

database:
  default:
    url: postgresql://...
    pool_size: 20
    max_overflow: 30

agents:
  config_path: /opt/keiko/config/agents

mcp:
  servers_config: /opt/keiko/config/mcp-servers.yml

protocols:
  selector_config: /opt/keiko/config/protocols.yml
```

### 📦 Dependency-Änderungen

#### Python-Abhängigkeiten

**Entfernte Dependencies:**
- `flask` → Ersetzt durch `fastapi`
- `sqlalchemy<1.4` → Upgrade auf `sqlalchemy>=2.0`
- `redis-py<4.0` → Upgrade auf `redis>=4.0`

**Neue Dependencies:**
- `fastapi>=0.104.0` - Web-Framework
- `asyncpg>=0.29.0` - Async PostgreSQL-Driver
- `pydantic>=2.0.0` - Data-Validation
- `prometheus-client>=0.19.0` - Metrics

**Geänderte Dependencies:**
```txt
# v1.x requirements.txt
sqlalchemy==1.3.24
redis==3.5.3
requests==2.28.0

# v2.0 requirements.txt
sqlalchemy>=2.0.0
redis>=4.0.0
aiohttp>=3.9.0
```

#### Python-Version-Anforderungen

- **v1.x:** Python 3.7+
- **v2.0:** Python 3.9+ (Breaking Change)

### 🔐 Security-Änderungen

#### Authentifizierung

**v1.x Session-basiert:**
```python
# Session-Token in Database
session = create_session(user_id)
response.set_cookie("session_id", session.id)
```

**v2.0 JWT-basiert:**
```python
# JWT-Token
token = create_jwt_token(user_id, expires_in=3600)
response.headers["Authorization"] = f"Bearer {token}"
```

**Migration:** Alle bestehenden Sessions werden invalidiert. Benutzer müssen sich neu anmelden.

#### Berechtigungen

**v1.x Einfache Rollen:**
```python
user.role in ["admin", "user"]
```

**v2.0 RBAC-System:**
```python
user.has_permission("agents:create")
user.has_role("agent_operator")
```

## 🛠️ Migration-Strategien

### Automatische Migration

```bash
# Automatisches Migration-Script
./scripts/migrate-v1-to-v2.sh --backup --validate

# Schritte:
# 1. Backup erstellen
# 2. Database-Schema migrieren
# 3. Konfiguration konvertieren
# 4. Code-Anpassungen vorschlagen
# 5. Validierung durchführen
```

### Manuelle Anpassungen

#### 1. Code-Anpassungen

```python
# v1.x Code
def create_agent(name: str, config: dict):
    agent = Agent(name, config)
    return agent.execute({"task": "test"})

# v2.0 Code
async def create_agent(name: str, config: AgentConfig):
    agent = Agent(config)
    task = Task.create("test", {})
    return await agent.execute_task(task)
```

#### 2. Konfiguration-Migration

```python
# migration/config_converter.py
def convert_v1_config_to_v2(v1_config: dict) -> dict:
    """Konvertiert v1-Konfiguration zu v2-Format."""

    v2_config = {
        "version": "2.0.0",
        "server": {
            "host": v1_config.get("host", "0.0.0.0"),
            "port": v1_config.get("port", 8000),
            "workers": 4  # Neu in v2
        },
        "database": {
            "default": {
                "url": v1_config.get("database_url"),
                "pool_size": v1_config.get("db_pool_size", 20)
            }
        }
    }

    # Agents-Konfiguration konvertieren
    if "agents" in v1_config:
        v2_config["agents"] = {
            "config_path": "/opt/keiko/config/agents"
        }

        # Einzelne Agent-Configs in separate Dateien
        for agent in v1_config["agents"]:
            agent_config = {
                "name": agent["name"],
                "type": "specialist",  # Default-Typ in v2
                "capabilities": _extract_capabilities(agent),
                "configuration": agent.get("config", {})
            }

            # Agent-Config-Datei erstellen
            with open(f"/opt/keiko/config/agents/{agent['name']}.yml", "w") as f:
                yaml.dump(agent_config, f)

    return v2_config
```

### Rollback-Plan

```bash
# Rollback zu v1.x
./scripts/rollback-to-v1.sh

# Schritte:
# 1. v2.0 Services stoppen
# 2. Database-Backup wiederherstellen
# 3. v1.x Konfiguration wiederherstellen
# 4. v1.x Services starten
# 5. Funktionalität validieren
```

## 📋 Kompatibilitäts-Matrix

| Feature | v1.x | v2.0 | Migration-Aufwand |
|---------|------|------|-------------------|
| **Agent-System** | ✅ | ✅ (Refactored) | Hoch |
| **Task-Execution** | ✅ | ✅ (Async) | Mittel |
| **REST-API** | ✅ | ✅ (Versioned) | Niedrig |
| **Database** | ✅ | ✅ (Schema-Changes) | Hoch |
| **Authentication** | Session | JWT | Mittel |
| **Configuration** | YAML | YAML (Extended) | Niedrig |
| **MCP-Integration** | ❌ | ✅ | Neu |
| **Protocol-Selection** | ❌ | ✅ | Neu |
| **Audit-Logging** | Basic | Enterprise | Mittel |

## ⚠️ Wichtige Hinweise

### Nicht-rückwärts-kompatible Änderungen

1. **Python 3.9+ erforderlich** - Upgrade der Python-Version notwendig
2. **Async/Await überall** - Alle Agent-Methoden sind jetzt asynchron
3. **Neue Database-Schema** - Vollständige Schema-Migration erforderlich
4. **JWT statt Sessions** - Alle Benutzer müssen sich neu anmelden
5. **Neue Konfiguration-Struktur** - Konfigurationsdateien müssen migriert werden

### Empfohlene Migration-Reihenfolge

1. **Staging-Umgebung** - Testen Sie die Migration zuerst in Staging
2. **Backup erstellen** - Vollständiges Backup vor Migration
3. **Dependencies aktualisieren** - Python und Package-Updates
4. **Schema migrieren** - Database-Schema-Updates
5. **Code anpassen** - Async/Await und neue APIs
6. **Konfiguration migrieren** - Neue Konfiguration-Struktur
7. **Validierung** - Umfassende Tests nach Migration
8. **Produktions-Migration** - Mit Rollback-Plan

### Support-Timeline

- **v1.x Support:** Bis 31. Dezember 2024
- **v1.x Security-Updates:** Bis 30. Juni 2025
- **v2.0 LTS:** Langzeit-Support bis 2027

!!! danger "Kritische Breaking Changes"
    - **Sofortige Aktion erforderlich:** Python 3.9+ und Async/Await-Migration
    - **Daten-Migration:** Database-Schema-Änderungen sind nicht optional
    - **Security:** Session-basierte Auth wird nicht mehr unterstützt

!!! tip "Migration-Hilfe"
    Nutzen Sie die bereitgestellten Migration-Scripts und testen Sie ausführlich in einer Staging-Umgebung vor der Produktions-Migration.

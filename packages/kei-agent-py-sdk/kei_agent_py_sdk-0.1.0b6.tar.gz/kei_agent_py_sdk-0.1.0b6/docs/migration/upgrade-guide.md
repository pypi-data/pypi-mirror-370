# 🚀 Upgrade Guide

Schritt-für-Schritt-Anleitung für das Upgrade auf Keiko Personal Assistant v2.0.

## 📋 Pre-Upgrade Checklist

### System-Anforderungen prüfen

```bash
# Python-Version prüfen (3.9+ erforderlich)
python --version

# Verfügbarer Speicher prüfen (mindestens 4GB RAM)
free -h

# Disk-Space prüfen (mindestens 10GB frei)
df -h

# PostgreSQL-Version prüfen (13+ erforderlich)
psql --version

# Redis-Version prüfen (6+ erforderlich)
redis-server --version
```

### Backup erstellen

```bash
# Vollständiges System-Backup
./scripts/create-full-backup.sh

# Database-Backup
pg_dump -U keiko_user keiko_db > backup/keiko_db_$(date +%Y%m%d_%H%M%S).sql

# Konfiguration-Backup
tar -czf backup/config_$(date +%Y%m%d_%H%M%S).tar.gz /opt/keiko/config

# Daten-Backup
tar -czf backup/data_$(date +%Y%m%d_%H%M%S).tar.gz /opt/keiko/data

# Backup-Integrität prüfen
./scripts/verify-backup.sh backup/
```

## 🔄 Upgrade-Prozess

### Schritt 1: Vorbereitung

```bash
# 1. Wartungsmodus aktivieren
echo "Keiko wird gewartet. Bitte versuchen Sie es später erneut." > /var/www/maintenance.html

# 2. Services stoppen
systemctl stop keiko-api
systemctl stop keiko-workers
systemctl stop keiko-scheduler

# 3. Aktuelle Version sichern
cp -r /opt/keiko /opt/keiko-v1-backup

# 4. Upgrade-Tools herunterladen
curl -L https://github.com/oscharko/keiko-upgrade/releases/latest/download/upgrade-v2.tar.gz -o upgrade-v2.tar.gz
tar -xzf upgrade-v2.tar.gz
cd keiko-upgrade-v2
```

### Schritt 2: Dependencies aktualisieren

```bash
# Python-Dependencies aktualisieren
pip install --upgrade pip
pip install -r requirements-v2.txt

# System-Dependencies prüfen
./scripts/check-system-deps.sh

# Neue Dependencies installieren
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-dev python3.9-venv

# Virtual Environment neu erstellen
python3.9 -m venv /opt/keiko/venv
source /opt/keiko/venv/bin/activate
pip install -r requirements-v2.txt
```

### Schritt 3: Database-Migration

```bash
# Database-Migration-Script ausführen
./scripts/migrate-database.sh --from-version=1.9 --to-version=2.0

# Migration-Log prüfen
tail -f /var/log/keiko/migration.log

# Database-Schema validieren
./scripts/validate-schema.sh --version=2.0
```

**Database-Migration-Details:**

```sql
-- Automatische Schema-Updates
BEGIN;

-- Neue Spalten hinzufügen
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

ALTER TABLE agents ADD COLUMN IF NOT EXISTS capabilities JSONB DEFAULT '[]';
ALTER TABLE agents ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE agents ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '2.0.0';

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'normal';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS timeout_seconds INTEGER DEFAULT 300;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;

-- Neue Tabellen erstellen
CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    auth_config JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indizes erstellen
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX IF NOT EXISTS idx_agents_capabilities ON agents USING GIN(capabilities);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);

-- Daten migrieren
UPDATE agents SET capabilities = '["text_processing"]' WHERE type = 'nlp' AND capabilities = '[]';
UPDATE agents SET capabilities = '["image_generation"]' WHERE type = 'image' AND capabilities = '[]';
UPDATE tasks SET priority = 'high' WHERE created_at > NOW() - INTERVAL '1 hour';

COMMIT;
```

### Schritt 4: Konfiguration migrieren

```bash
# Konfiguration-Migration
./scripts/migrate-config.sh --source=/opt/keiko-v1-backup/config --target=/opt/keiko/config

# Neue Konfigurationsdateien erstellen
./scripts/generate-v2-config.sh
```

**Konfiguration-Migration-Script:**

```python
#!/usr/bin/env python3
# scripts/migrate-config.py

import yaml
import json
from pathlib import Path

def migrate_main_config():
    """Migriert Hauptkonfiguration von v1 zu v2."""

    # v1-Konfiguration laden
    with open('/opt/keiko-v1-backup/config/config.yml', 'r') as f:
        v1_config = yaml.safe_load(f)

    # v2-Konfiguration erstellen
    v2_config = {
        'version': '2.0.0',
        'environment': v1_config.get('env', 'production'),

        'server': {
            'host': v1_config.get('host', '0.0.0.0'),
            'port': v1_config.get('port', 8000),
            'workers': v1_config.get('workers', 4),
            'reload': False
        },

        'database': {
            'default': {
                'url': v1_config.get('database_url'),
                'pool_size': v1_config.get('db_pool_size', 20),
                'max_overflow': 30,
                'pool_timeout': 30,
                'pool_recycle': 3600
            }
        },

        'redis': {
            'url': v1_config.get('redis_url', 'redis://localhost:6379'),
            'max_connections': 20
        },

        'logging': {
            'level': v1_config.get('log_level', 'INFO'),
            'format': 'json',
            'structured': True,
            'file_path': '/var/log/keiko/app.log'
        },

        'monitoring': {
            'enabled': True,
            'metrics_port': 9090,
            'health_check_interval': 30
        },

        'security': {
            'jwt_secret': v1_config.get('secret_key'),
            'jwt_expiration': 3600,
            'password_min_length': 8,
            'session_timeout': 3600
        }
    }

    # v2-Konfiguration speichern
    with open('/opt/keiko/config/config.yml', 'w') as f:
        yaml.dump(v2_config, f, default_flow_style=False)

def migrate_agent_configs():
    """Migriert Agent-Konfigurationen."""

    v1_agents_file = '/opt/keiko-v1-backup/config/agents.yml'
    v2_agents_dir = Path('/opt/keiko/config/agents')
    v2_agents_dir.mkdir(exist_ok=True)

    with open(v1_agents_file, 'r') as f:
        v1_agents = yaml.safe_load(f)

    for agent in v1_agents.get('agents', []):
        v2_agent_config = {
            'name': agent['name'],
            'type': 'specialist',
            'capabilities': extract_capabilities(agent),
            'configuration': {
                'timeout_seconds': agent.get('timeout', 300),
                'max_concurrent_tasks': agent.get('max_tasks', 1),
                'retry_policy': {
                    'max_retries': 3,
                    'retry_delay': 1.0
                }
            },
            'external_config': agent.get('config', {})
        }

        # Agent-Konfiguration speichern
        agent_file = v2_agents_dir / f"{agent['name']}.yml"
        with open(agent_file, 'w') as f:
            yaml.dump(v2_agent_config, f, default_flow_style=False)

def extract_capabilities(v1_agent):
    """Extrahiert Capabilities aus v1-Agent."""
    capabilities = []

    agent_type = v1_agent.get('type', 'generic')
    if agent_type == 'nlp':
        capabilities.extend(['text_processing', 'summarization'])
    elif agent_type == 'image':
        capabilities.extend(['image_generation', 'image_editing'])
    elif agent_type == 'data':
        capabilities.extend(['data_analysis', 'data_processing'])

    return capabilities

if __name__ == '__main__':
    migrate_main_config()
    migrate_agent_configs()
    print("Konfiguration erfolgreich migriert")
```

### Schritt 5: Code-Updates

```bash
# Neue Keiko v2.0 Installation
git clone https://github.com/oscharko/keiko-personal-assistant.git /opt/keiko-v2
cd /opt/keiko-v2
git checkout v2.0.0

# Konfiguration kopieren
cp -r /opt/keiko/config /opt/keiko-v2/

# Custom-Code migrieren (falls vorhanden)
./scripts/migrate-custom-code.sh --source=/opt/keiko-v1-backup/custom --target=/opt/keiko-v2/custom
```

### Schritt 6: Services konfigurieren

```bash
# Neue Systemd-Services installieren
cp scripts/systemd/*.service /etc/systemd/system/
systemctl daemon-reload

# Services aktivieren
systemctl enable keiko-api-v2
systemctl enable keiko-workers-v2
systemctl enable keiko-scheduler-v2

# Nginx-Konfiguration aktualisieren
cp scripts/nginx/keiko-v2.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/keiko-v2.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### Schritt 7: Validierung und Tests

```bash
# Services starten
systemctl start keiko-api-v2
systemctl start keiko-workers-v2
systemctl start keiko-scheduler-v2

# Health-Check
curl http://localhost:8000/health

# Funktionalitäts-Tests
./scripts/run-upgrade-tests.sh

# Performance-Tests
./scripts/run-performance-tests.sh

# User-Acceptance-Tests
./scripts/run-acceptance-tests.sh
```

## 🧪 Test-Szenarien

### Funktionalitäts-Tests

```python
# tests/upgrade_tests.py
import asyncio
import pytest
from keiko.client import KeikoClient

@pytest.mark.asyncio
async def test_agent_creation():
    """Testet Agent-Erstellung nach Upgrade."""

    client = KeikoClient("http://localhost:8000")

    # Agent erstellen
    agent_config = {
        "name": "Test Agent",
        "type": "specialist",
        "capabilities": ["text_processing"]
    }

    agent = await client.create_agent(agent_config)
    assert agent["id"] is not None
    assert agent["name"] == "Test Agent"

@pytest.mark.asyncio
async def test_task_execution():
    """Testet Task-Ausführung nach Upgrade."""

    client = KeikoClient("http://localhost:8000")

    # Task ausführen
    task_request = {
        "task_type": "text_processing",
        "parameters": {"text": "Hello World"}
    }

    result = await client.execute_task("agent-id", task_request)
    assert result["success"] is True

@pytest.mark.asyncio
async def test_mcp_integration():
    """Testet neue MCP-Integration."""

    client = KeikoClient("http://localhost:8000")

    # MCP-Server registrieren
    mcp_config = {
        "server_name": "test-server",
        "base_url": "http://localhost:8080",
        "timeout_seconds": 30.0
    }

    server_id = await client.register_mcp_server(mcp_config)
    assert server_id is not None
```

### Performance-Tests

```bash
# Performance-Benchmark
./scripts/benchmark.sh --duration=300 --concurrent=50

# Erwartete Ergebnisse:
# - Response Time: < 200ms (95th percentile)
# - Throughput: > 1000 requests/second
# - Error Rate: < 0.1%
# - Memory Usage: < 2GB
```

## 🔄 Rollback-Verfahren

### Automatischer Rollback

```bash
# Rollback-Script ausführen
./scripts/rollback-upgrade.sh --to-version=1.9

# Schritte:
# 1. v2.0 Services stoppen
# 2. Database-Backup wiederherstellen
# 3. v1.x Konfiguration wiederherstellen
# 4. v1.x Code wiederherstellen
# 5. v1.x Services starten
# 6. Funktionalität validieren
```

### Manueller Rollback

```bash
# 1. Services stoppen
systemctl stop keiko-api-v2 keiko-workers-v2 keiko-scheduler-v2

# 2. Database wiederherstellen
psql -U postgres -d keiko_db < backup/keiko_db_backup.sql

# 3. Code wiederherstellen
rm -rf /opt/keiko
mv /opt/keiko-v1-backup /opt/keiko

# 4. v1.x Services starten
systemctl start keiko-api keiko-workers keiko-scheduler

# 5. Nginx-Konfiguration zurücksetzen
ln -sf /etc/nginx/sites-available/keiko-v1.conf /etc/nginx/sites-enabled/keiko.conf
systemctl reload nginx
```

## 📊 Post-Upgrade-Monitoring

### Monitoring-Setup

```bash
# Prometheus-Metriken aktivieren
curl http://localhost:9090/metrics

# Grafana-Dashboard importieren
./scripts/import-grafana-dashboard.sh dashboards/keiko-v2-dashboard.json

# Alerting-Regeln konfigurieren
cp monitoring/alerts/keiko-v2-alerts.yml /etc/prometheus/rules/
```

### Key-Metriken überwachen

- **Response Time:** < 200ms (95th percentile)
- **Error Rate:** < 0.1%
- **Memory Usage:** < 2GB
- **CPU Usage:** < 70%
- **Database Connections:** < 80% Pool-Auslastung
- **Task Success Rate:** > 99%

## 📋 Post-Upgrade-Checklist

### Sofort nach Upgrade

- [ ] **Health-Checks** bestanden
- [ ] **Funktionalitäts-Tests** erfolgreich
- [ ] **Performance-Tests** bestanden
- [ ] **User-Login** funktioniert
- [ ] **Agent-Erstellung** möglich
- [ ] **Task-Ausführung** erfolgreich

### 24 Stunden nach Upgrade

- [ ] **Monitoring-Metriken** normal
- [ ] **Error-Logs** überprüft
- [ ] **Performance** stabil
- [ ] **User-Feedback** positiv
- [ ] **Backup-Strategie** aktualisiert

### 1 Woche nach Upgrade

- [ ] **Langzeit-Performance** stabil
- [ ] **Memory-Leaks** ausgeschlossen
- [ ] **User-Training** abgeschlossen
- [ ] **Dokumentation** aktualisiert
- [ ] **v1.x Backup** archiviert

!!! success "Upgrade erfolgreich"
    Herzlichen Glückwunsch! Sie haben erfolgreich auf Keiko Personal Assistant v2.0 upgegraded.

!!! warning "Support-Hinweis"
    Bei Problemen nach dem Upgrade wenden Sie sich an das Support-Team oder erstellen Sie ein Issue im GitHub-Repository.

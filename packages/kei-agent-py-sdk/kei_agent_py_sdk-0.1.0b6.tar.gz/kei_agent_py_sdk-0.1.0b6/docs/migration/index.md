# 🔄 Migration Guide

Umfassender Leitfaden für die Migration zu Keiko Personal Assistant v2.0 und neueren Versionen.

## 📋 Migration-Übersicht

### Unterstützte Migration-Pfade

```mermaid
graph LR
    subgraph "Legacy Versions"
        V1_0[v1.0.x]
        V1_5[v1.5.x]
        V1_9[v1.9.x]
    end

    subgraph "Current Version"
        V2_0[v2.0.x]
    end

    subgraph "Migration Tools"
        AUTO[Automatic Migration]
        MANUAL[Manual Migration]
        HYBRID[Hybrid Migration]
    end

    V1_0 --> AUTO
    V1_5 --> HYBRID
    V1_9 --> MANUAL

    AUTO --> V2_0
    HYBRID --> V2_0
    MANUAL --> V2_0
```

### Migration-Strategien

| Von Version | Zu Version | Strategie | Aufwand | Downtime |
|-------------|------------|-----------|---------|----------|
| v1.0.x | v2.0.x | Vollständige Migration | Hoch | 4-8 Stunden |
| v1.5.x | v2.0.x | Hybride Migration | Mittel | 2-4 Stunden |
| v1.9.x | v2.0.x | Inkrementelle Migration | Niedrig | 1-2 Stunden |

## 🚀 Schnellstart-Migration

### Pre-Migration Checklist

```bash
# 1. Backup erstellen
./scripts/backup-system.sh --full --verify

# 2. Abhängigkeiten prüfen
./scripts/check-dependencies.sh

# 3. Migration-Tool herunterladen
curl -L https://github.com/oscharko/keiko-migration/releases/latest/download/migrate.sh -o migrate.sh
chmod +x migrate.sh

# 4. Migration-Plan erstellen
./migrate.sh --plan --from-version=1.9.0 --to-version=2.0.0

# 5. Dry-Run durchführen
./migrate.sh --dry-run --config=migration-config.yml
```

### Automatische Migration (v1.9.x → v2.0.x)

```bash
# Migration-Konfiguration
cat > migration-config.yml << EOF
source:
  version: "1.9.0"
  database_url: "postgresql://user:pass@localhost/keiko_v1"
  config_path: "/opt/keiko-v1/config"
  data_path: "/opt/keiko-v1/data"

target:
  version: "2.0.0"
  database_url: "postgresql://user:pass@localhost/keiko_v2"
  config_path: "/opt/keiko-v2/config"
  data_path: "/opt/keiko-v2/data"

migration:
  strategy: "automatic"
  preserve_data: true
  migrate_configs: true
  migrate_users: true
  migrate_agents: true
  migrate_tasks: true

backup:
  enabled: true
  path: "/backup/keiko-migration"
  verify: true

rollback:
  enabled: true
  create_checkpoint: true
EOF

# Migration ausführen
./migrate.sh --config=migration-config.yml --execute
```

## 📊 Daten-Migration

### Database Schema Migration

```python
# migration/database_migrator.py
from keiko.migration import DatabaseMigrator, MigrationStep

class KeikoV2DatabaseMigrator(DatabaseMigrator):
    """Database-Migrator für Keiko v2.0."""

    def __init__(self, source_db_url: str, target_db_url: str):
        super().__init__(source_db_url, target_db_url)
        self.migration_steps = self._define_migration_steps()

    def _define_migration_steps(self) -> List[MigrationStep]:
        """Definiert Migration-Schritte."""

        return [
            # Schritt 1: Schema-Updates
            MigrationStep(
                name="update_user_schema",
                description="Aktualisiert User-Schema für v2.0",
                sql_commands=[
                    "ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'",
                    "ALTER TABLE users ADD COLUMN last_login TIMESTAMP",
                    "ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}'",
                    "CREATE INDEX idx_users_role ON users(role)",
                    "CREATE INDEX idx_users_last_login ON users(last_login)"
                ],
                rollback_commands=[
                    "DROP INDEX IF EXISTS idx_users_last_login",
                    "DROP INDEX IF EXISTS idx_users_role",
                    "ALTER TABLE users DROP COLUMN IF EXISTS preferences",
                    "ALTER TABLE users DROP COLUMN IF EXISTS last_login",
                    "ALTER TABLE users DROP COLUMN IF EXISTS role"
                ]
            ),

            # Schritt 2: Agent-Schema
            MigrationStep(
                name="update_agent_schema",
                description="Aktualisiert Agent-Schema für v2.0",
                sql_commands=[
                    "ALTER TABLE agents ADD COLUMN capabilities JSONB DEFAULT '[]'",
                    "ALTER TABLE agents ADD COLUMN metadata JSONB DEFAULT '{}'",
                    "ALTER TABLE agents ADD COLUMN version VARCHAR(20) DEFAULT '2.0.0'",
                    "UPDATE agents SET capabilities = '[]' WHERE capabilities IS NULL",
                    "CREATE INDEX idx_agents_capabilities ON agents USING GIN(capabilities)",
                    "CREATE INDEX idx_agents_version ON agents(version)"
                ]
            ),

            # Schritt 3: Task-Schema
            MigrationStep(
                name="update_task_schema",
                description="Aktualisiert Task-Schema für v2.0",
                sql_commands=[
                    "ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'normal'",
                    "ALTER TABLE tasks ADD COLUMN timeout_seconds INTEGER DEFAULT 300",
                    "ALTER TABLE tasks ADD COLUMN retry_count INTEGER DEFAULT 0",
                    "ALTER TABLE tasks ADD COLUMN metadata JSONB DEFAULT '{}'",
                    "CREATE INDEX idx_tasks_priority ON tasks(priority)",
                    "CREATE INDEX idx_tasks_timeout ON tasks(timeout_seconds)"
                ]
            ),

            # Schritt 4: Neue Tabellen
            MigrationStep(
                name="create_new_tables",
                description="Erstellt neue Tabellen für v2.0",
                sql_commands=[
                    """
                    CREATE TABLE mcp_servers (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(100) UNIQUE NOT NULL,
                        base_url VARCHAR(500) NOT NULL,
                        auth_config JSONB DEFAULT '{}',
                        status VARCHAR(20) DEFAULT 'inactive',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                    """,
                    """
                    CREATE TABLE audit_logs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID REFERENCES users(id),
                        action VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(50) NOT NULL,
                        resource_id VARCHAR(100),
                        details JSONB DEFAULT '{}',
                        ip_address INET,
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                    """,
                    "CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action)",
                    "CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id)",
                    "CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at)"
                ]
            )
        ]

    async def migrate(self) -> MigrationResult:
        """Führt vollständige Migration durch."""

        result = MigrationResult()

        try:
            # Pre-Migration-Checks
            await self._pre_migration_checks()

            # Backup erstellen
            backup_path = await self._create_backup()
            result.backup_path = backup_path

            # Migration-Schritte ausführen
            for step in self.migration_steps:
                step_result = await self._execute_migration_step(step)
                result.add_step_result(step.name, step_result)

                if not step_result.success:
                    raise MigrationException(f"Migration-Schritt fehlgeschlagen: {step.name}")

            # Post-Migration-Validierung
            await self._post_migration_validation()

            result.success = True
            result.message = "Migration erfolgreich abgeschlossen"

        except Exception as e:
            result.success = False
            result.error = str(e)

            # Rollback bei Fehler
            await self._rollback_migration()

        return result

    async def _execute_migration_step(self, step: MigrationStep) -> StepResult:
        """Führt einzelnen Migration-Schritt aus."""

        step_result = StepResult(step_name=step.name)

        try:
            async with self.target_db.begin() as conn:
                for command in step.sql_commands:
                    await conn.execute(text(command))

            step_result.success = True
            step_result.message = f"Schritt {step.name} erfolgreich"

        except Exception as e:
            step_result.success = False
            step_result.error = str(e)

            # Rollback für diesen Schritt
            if step.rollback_commands:
                try:
                    async with self.target_db.begin() as conn:
                        for command in reversed(step.rollback_commands):
                            await conn.execute(text(command))
                except Exception as rollback_error:
                    step_result.rollback_error = str(rollback_error)

        return step_result
```

### Daten-Transformation

```python
# migration/data_transformer.py
class DataTransformer:
    """Transformiert Daten zwischen Versionen."""

    async def transform_agents_v1_to_v2(self, v1_agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transformiert Agent-Daten von v1 zu v2."""

        v2_agents = []

        for v1_agent in v1_agents:
            v2_agent = {
                'id': v1_agent['id'],
                'name': v1_agent['name'],
                'type': v1_agent.get('agent_type', 'generic'),
                'status': v1_agent.get('status', 'inactive'),
                'created_at': v1_agent['created_at'],
                'updated_at': v1_agent.get('updated_at', v1_agent['created_at']),

                # Neue Felder in v2
                'capabilities': self._extract_capabilities(v1_agent),
                'metadata': self._extract_metadata(v1_agent),
                'version': '2.0.0'
            }

            # Konfiguration transformieren
            if 'config' in v1_agent:
                v2_agent['configuration'] = self._transform_agent_config(v1_agent['config'])

            v2_agents.append(v2_agent)

        return v2_agents

    def _extract_capabilities(self, v1_agent: Dict[str, Any]) -> List[str]:
        """Extrahiert Capabilities aus v1-Agent."""

        capabilities = []

        # Aus v1-Konfiguration ableiten
        config = v1_agent.get('config', {})

        if config.get('supports_text_processing'):
            capabilities.append('text_processing')

        if config.get('supports_image_generation'):
            capabilities.append('image_generation')

        if config.get('supports_data_analysis'):
            capabilities.append('data_analysis')

        # Fallback basierend auf Agent-Typ
        agent_type = v1_agent.get('agent_type', 'generic')
        if agent_type == 'text_processor':
            capabilities.extend(['text_processing', 'summarization'])
        elif agent_type == 'image_generator':
            capabilities.extend(['image_generation', 'image_editing'])

        return list(set(capabilities))  # Duplikate entfernen

    def _extract_metadata(self, v1_agent: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahiert Metadata aus v1-Agent."""

        metadata = {
            'migrated_from': 'v1.x',
            'migration_date': datetime.utcnow().isoformat(),
            'original_type': v1_agent.get('agent_type')
        }

        # Zusätzliche Metadaten aus v1-Konfiguration
        config = v1_agent.get('config', {})
        if 'description' in config:
            metadata['description'] = config['description']

        if 'tags' in config:
            metadata['tags'] = config['tags']

        return metadata

    async def transform_tasks_v1_to_v2(self, v1_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transformiert Task-Daten von v1 zu v2."""

        v2_tasks = []

        for v1_task in v1_tasks:
            v2_task = {
                'id': v1_task['id'],
                'user_id': v1_task['user_id'],
                'agent_id': v1_task['agent_id'],
                'task_type': v1_task.get('type', 'generic'),
                'parameters': v1_task.get('params', {}),
                'status': self._map_task_status(v1_task.get('status')),
                'created_at': v1_task['created_at'],
                'started_at': v1_task.get('started_at'),
                'completed_at': v1_task.get('completed_at'),

                # Neue Felder in v2
                'priority': self._determine_priority(v1_task),
                'timeout_seconds': v1_task.get('timeout', 300),
                'retry_count': v1_task.get('retries', 0),
                'metadata': {
                    'migrated_from': 'v1.x',
                    'original_status': v1_task.get('status')
                }
            }

            v2_tasks.append(v2_task)

        return v2_tasks

    def _map_task_status(self, v1_status: str) -> str:
        """Mappt v1-Task-Status zu v2-Status."""

        status_mapping = {
            'created': 'pending',
            'queued': 'pending',
            'running': 'running',
            'finished': 'completed',
            'failed': 'failed',
            'cancelled': 'cancelled'
        }

        return status_mapping.get(v1_status, 'pending')

    def _determine_priority(self, v1_task: Dict[str, Any]) -> str:
        """Bestimmt Priorität basierend auf v1-Task-Daten."""

        # Priorität aus v1-Parametern ableiten
        params = v1_task.get('params', {})

        if params.get('urgent'):
            return 'high'
        elif params.get('background'):
            return 'low'
        else:
            return 'normal'
```

## ⚙️ Konfigurations-Migration

### Config-File-Migration

```python
# migration/config_migrator.py
import yaml
import json
from pathlib import Path

class ConfigMigrator:
    """Migriert Konfigurationsdateien zwischen Versionen."""

    def __init__(self, source_config_path: str, target_config_path: str):
        self.source_path = Path(source_config_path)
        self.target_path = Path(target_config_path)

    async def migrate_configs(self) -> ConfigMigrationResult:
        """Migriert alle Konfigurationsdateien."""

        result = ConfigMigrationResult()

        try:
            # Hauptkonfiguration migrieren
            main_config = await self._migrate_main_config()
            result.add_config('main', main_config)

            # Database-Konfiguration migrieren
            db_config = await self._migrate_database_config()
            result.add_config('database', db_config)

            # Agent-Konfigurationen migrieren
            agent_configs = await self._migrate_agent_configs()
            result.add_config('agents', agent_configs)

            # Security-Konfiguration migrieren
            security_config = await self._migrate_security_config()
            result.add_config('security', security_config)

            result.success = True

        except Exception as e:
            result.success = False
            result.error = str(e)

        return result

    async def _migrate_main_config(self) -> Dict[str, Any]:
        """Migriert Hauptkonfiguration."""

        # v1-Konfiguration laden
        v1_config_file = self.source_path / 'config.yml'
        with open(v1_config_file, 'r') as f:
            v1_config = yaml.safe_load(f)

        # v2-Konfiguration erstellen
        v2_config = {
            'version': '2.0.0',
            'environment': v1_config.get('env', 'development'),

            # Server-Konfiguration
            'server': {
                'host': v1_config.get('host', '0.0.0.0'),
                'port': v1_config.get('port', 8000),
                'workers': v1_config.get('workers', 4),
                'reload': v1_config.get('debug', False)
            },

            # Logging-Konfiguration
            'logging': {
                'level': v1_config.get('log_level', 'INFO'),
                'format': 'json',  # Neu in v2
                'structured': True,  # Neu in v2
                'file_path': v1_config.get('log_file', '/var/log/keiko/app.log')
            },

            # Monitoring-Konfiguration (neu in v2)
            'monitoring': {
                'enabled': True,
                'metrics_port': 9090,
                'health_check_interval': 30
            }
        }

        # v2-Konfiguration speichern
        v2_config_file = self.target_path / 'config.yml'
        v2_config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(v2_config_file, 'w') as f:
            yaml.dump(v2_config, f, default_flow_style=False)

        return v2_config

    async def _migrate_database_config(self) -> Dict[str, Any]:
        """Migriert Database-Konfiguration."""

        v1_db_file = self.source_path / 'database.yml'
        with open(v1_db_file, 'r') as f:
            v1_db_config = yaml.safe_load(f)

        v2_db_config = {
            'default': {
                'url': v1_db_config.get('database_url'),
                'pool_size': v1_db_config.get('pool_size', 20),
                'max_overflow': v1_db_config.get('max_overflow', 30),
                'pool_timeout': 30,  # Neu in v2
                'pool_recycle': 3600,  # Neu in v2
                'echo': False
            },

            # Read-Replicas (neu in v2)
            'read_replicas': v1_db_config.get('read_replicas', []),

            # Migration-Konfiguration
            'migrations': {
                'auto_upgrade': False,
                'backup_before_migration': True
            }
        }

        # v2-Database-Konfiguration speichern
        v2_db_file = self.target_path / 'database.yml'
        with open(v2_db_file, 'w') as f:
            yaml.dump(v2_db_config, f, default_flow_style=False)

        return v2_db_config

    async def _migrate_agent_configs(self) -> Dict[str, Any]:
        """Migriert Agent-Konfigurationen."""

        v1_agents_dir = self.source_path / 'agents'
        v2_agents_dir = self.target_path / 'agents'
        v2_agents_dir.mkdir(parents=True, exist_ok=True)

        migrated_configs = {}

        # Alle v1-Agent-Konfigurationen durchgehen
        for v1_config_file in v1_agents_dir.glob('*.yml'):
            with open(v1_config_file, 'r') as f:
                v1_agent_config = yaml.safe_load(f)

            # v2-Agent-Konfiguration erstellen
            v2_agent_config = {
                'name': v1_agent_config['name'],
                'type': v1_agent_config.get('type', 'generic'),
                'version': '2.0.0',

                # Capabilities (neu in v2)
                'capabilities': self._extract_agent_capabilities(v1_agent_config),

                # Konfiguration
                'configuration': {
                    'timeout_seconds': v1_agent_config.get('timeout', 300),
                    'max_concurrent_tasks': v1_agent_config.get('max_tasks', 1),
                    'retry_policy': {
                        'max_retries': v1_agent_config.get('max_retries', 3),
                        'retry_delay': v1_agent_config.get('retry_delay', 1.0)
                    }
                },

                # External-Konfiguration
                'external_config': v1_agent_config.get('external', {})
            }

            # v2-Konfiguration speichern
            v2_config_file = v2_agents_dir / v1_config_file.name
            with open(v2_config_file, 'w') as f:
                yaml.dump(v2_agent_config, f, default_flow_style=False)

            migrated_configs[v1_config_file.stem] = v2_agent_config

        return migrated_configs
```

## 🔄 Rollback-Strategien

### Automatischer Rollback

```bash
# rollback.sh
#!/bin/bash

BACKUP_PATH="/backup/keiko-migration"
ROLLBACK_LOG="/var/log/keiko/rollback.log"

echo "$(date): Starting Keiko rollback process" >> $ROLLBACK_LOG

# 1. Services stoppen
echo "Stopping Keiko v2 services..." >> $ROLLBACK_LOG
systemctl stop keiko-v2
systemctl stop keiko-workers-v2

# 2. Database rollback
echo "Rolling back database..." >> $ROLLBACK_LOG
psql -U postgres -d keiko_v2 < $BACKUP_PATH/database_rollback.sql

# 3. Konfiguration wiederherstellen
echo "Restoring configuration..." >> $ROLLBACK_LOG
cp -r $BACKUP_PATH/config/* /opt/keiko-v1/config/

# 4. Daten wiederherstellen
echo "Restoring data..." >> $ROLLBACK_LOG
rsync -av $BACKUP_PATH/data/ /opt/keiko-v1/data/

# 5. v1 Services starten
echo "Starting Keiko v1 services..." >> $ROLLBACK_LOG
systemctl start keiko-v1
systemctl start keiko-workers-v1

# 6. Health check
sleep 30
if curl -f http://localhost:8000/health; then
    echo "$(date): Rollback completed successfully" >> $ROLLBACK_LOG
    exit 0
else
    echo "$(date): Rollback failed - manual intervention required" >> $ROLLBACK_LOG
    exit 1
fi
```

## 📋 Migration-Checkliste

### Pre-Migration

- [ ] **Vollständiges Backup** erstellt und verifiziert
- [ ] **Abhängigkeiten** geprüft (Python 3.9+, PostgreSQL 13+, Redis 6+)
- [ ] **Disk-Space** ausreichend (mindestens 2x aktuelle Datengröße)
- [ ] **Downtime-Fenster** geplant und kommuniziert
- [ ] **Rollback-Plan** getestet
- [ ] **Migration-Tools** heruntergeladen und getestet

### During Migration

- [ ] **Services gestoppt** in korrekter Reihenfolge
- [ ] **Database-Migration** erfolgreich
- [ ] **Daten-Transformation** abgeschlossen
- [ ] **Konfigurations-Migration** durchgeführt
- [ ] **Post-Migration-Tests** bestanden

### Post-Migration

- [ ] **Funktionalitäts-Tests** erfolgreich
- [ ] **Performance-Tests** durchgeführt
- [ ] **User-Acceptance-Tests** bestanden
- [ ] **Monitoring** aktiviert und konfiguriert
- [ ] **Backup-Strategie** für v2 implementiert
- [ ] **Dokumentation** aktualisiert

!!! warning "Wichtige Hinweise"
    - Führen Sie immer einen vollständigen Backup vor der Migration durch
    - Testen Sie die Migration in einer Staging-Umgebung
    - Planen Sie ausreichend Zeit für unvorhergesehene Probleme ein
    - Halten Sie den Rollback-Plan bereit

!!! info "Support"
    Bei Problemen während der Migration wenden Sie sich an das Support-Team oder erstellen Sie ein Issue im GitHub-Repository.

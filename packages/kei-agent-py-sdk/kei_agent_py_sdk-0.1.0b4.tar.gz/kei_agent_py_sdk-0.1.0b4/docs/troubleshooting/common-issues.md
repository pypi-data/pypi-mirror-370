# 🔧 Common Issues & Solutions

Häufige Probleme und deren Lösungen bei Keiko Personal Assistant.

## 🚀 Startup-Probleme

### Application startet nicht

**Problem:** Keiko-Service startet nicht oder stürzt sofort ab.

**Symptome:**
```bash
systemctl status keiko-api
● keiko-api.service - Keiko Personal Assistant API
   Loaded: loaded (/etc/systemd/system/keiko-api.service; enabled)
   Active: failed (Result: exit-code)
```

**Diagnose:**
```bash
# Service-Logs prüfen
journalctl -u keiko-api -f

# Application-Logs prüfen
tail -f /var/log/keiko/app.log

# Konfiguration validieren
./scripts/validate-config.sh
```

**Häufige Ursachen & Lösungen:**

1. **Fehlende Dependencies**
```bash
# Python-Dependencies prüfen
pip check

# Fehlende Packages installieren
pip install -r requirements.txt

# System-Dependencies prüfen
sudo apt-get install python3-dev postgresql-client redis-tools
```

2. **Database-Verbindungsfehler**
```bash
# Database-Verbindung testen
psql -h localhost -U keiko_user -d keiko_db -c "SELECT 1;"

# Connection-String prüfen
echo $DATABASE_URL

# Database-Service starten
sudo systemctl start postgresql
```

3. **Port bereits belegt**
```bash
# Port-Nutzung prüfen
sudo netstat -tlnp | grep :8000

# Prozess beenden
sudo kill -9 <PID>

# Alternativen Port konfigurieren
export KEIKO_PORT=8001
```

4. **Berechtigungsprobleme**
```bash
# Log-Verzeichnis-Berechtigungen
sudo chown -R keiko:keiko /var/log/keiko
sudo chmod 755 /var/log/keiko

# Konfiguration-Berechtigungen
sudo chown -R keiko:keiko /opt/keiko/config
sudo chmod 600 /opt/keiko/config/*.yml
```

### Langsamer Startup

**Problem:** Application startet sehr langsam (>60 Sekunden).

**Diagnose:**
```bash
# Startup-Zeit messen
time systemctl start keiko-api

# Startup-Profiling aktivieren
export KEIKO_PROFILE_STARTUP=true
```

**Lösungen:**

1. **Database-Connection-Pool optimieren**
```yaml
# config/database.yml
database:
  default:
    pool_size: 5  # Reduzieren für schnelleren Startup
    max_overflow: 10
    pool_timeout: 10
```

2. **Lazy-Loading aktivieren**
```python
# config/app.py
LAZY_LOADING = True
PRELOAD_AGENTS = False
```

3. **Health-Check-Timeout erhöhen**
```yaml
# config/config.yml
monitoring:
  health_check_timeout: 30
  startup_timeout: 120
```

## 🗄️ Database-Probleme

### Connection-Pool-Erschöpfung

**Problem:** "QueuePool limit of size X overflow Y reached"

**Symptome:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 30 reached
```

**Diagnose:**
```bash
# Aktive Verbindungen prüfen
psql -d keiko_db -c "SELECT count(*) FROM pg_stat_activity WHERE datname='keiko_db';"

# Connection-Pool-Status
curl http://localhost:8000/debug/pool-status
```

**Lösungen:**

1. **Pool-Größe erhöhen**
```yaml
# config/database.yml
database:
  default:
    pool_size: 30
    max_overflow: 50
    pool_timeout: 60
```

2. **Connection-Leaks finden**
```python
# debug/connection_tracker.py
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    logging.info(f"New connection: {id(dbapi_connection)}")

@event.listens_for(Engine, "close")
def close_connection(dbapi_connection, connection_record):
    logging.info(f"Closed connection: {id(dbapi_connection)}")
```

3. **Connection-Recycling konfigurieren**
```yaml
database:
  default:
    pool_recycle: 3600  # 1 Stunde
    pool_pre_ping: true
```

### Slow Queries

**Problem:** Database-Queries sind langsam (>1 Sekunde).

**Diagnose:**
```sql
-- Langsame Queries identifizieren
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC;

-- Aktive Queries prüfen
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

**Lösungen:**

1. **Fehlende Indizes hinzufügen**
```sql
-- Häufig benötigte Indizes
CREATE INDEX CONCURRENTLY idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX CONCURRENTLY idx_agents_type_active ON agents(type) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_audit_logs_created_at ON audit_logs(created_at);
```

2. **Query-Optimierung**
```python
# Vorher: N+1 Query-Problem
agents = await session.execute(select(Agent))
for agent in agents:
    tasks = await session.execute(select(Task).where(Task.agent_id == agent.id))

# Nachher: Eager Loading
agents = await session.execute(
    select(Agent).options(selectinload(Agent.tasks))
)
```

3. **Database-Tuning**
```sql
-- PostgreSQL-Konfiguration optimieren
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();
```

## 🔄 Redis-Probleme

### Redis-Verbindungsfehler

**Problem:** "Connection refused" oder "Redis server went away"

**Diagnose:**
```bash
# Redis-Status prüfen
redis-cli ping

# Redis-Logs prüfen
tail -f /var/log/redis/redis-server.log

# Verbindung testen
redis-cli -h localhost -p 6379 info
```

**Lösungen:**

1. **Redis-Service starten**
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

2. **Redis-Konfiguration prüfen**
```bash
# Redis-Config
sudo nano /etc/redis/redis.conf

# Wichtige Einstellungen:
# bind 127.0.0.1
# port 6379
# maxmemory 512mb
# maxmemory-policy allkeys-lru
```

3. **Connection-Pool konfigurieren**
```python
# config/redis.py
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'max_connections': 20,
    'retry_on_timeout': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5
}
```

### Memory-Probleme

**Problem:** Redis läuft aus dem Speicher.

**Diagnose:**
```bash
# Redis-Memory-Usage
redis-cli info memory

# Top-Keys nach Speicherverbrauch
redis-cli --bigkeys

# Memory-Usage-Pattern
redis-cli info stats | grep keyspace
```

**Lösungen:**

1. **Memory-Policy konfigurieren**
```bash
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

2. **Key-Expiration setzen**
```python
# Cache mit TTL
await redis_client.setex("cache_key", 3600, value)  # 1 Stunde

# Batch-Expiration
for key in large_keys:
    await redis_client.expire(key, 1800)  # 30 Minuten
```

3. **Memory-Monitoring**
```python
# memory_monitor.py
async def monitor_redis_memory():
    info = await redis_client.info('memory')
    used_memory = info['used_memory']
    max_memory = info['maxmemory']

    if used_memory > max_memory * 0.9:
        logger.warning(f"Redis memory usage high: {used_memory}/{max_memory}")
```

## 🤖 Agent-Probleme

### Agent startet nicht

**Problem:** Agent kann nicht gestartet oder aktiviert werden.

**Diagnose:**
```bash
# Agent-Status prüfen
curl http://localhost:8000/api/v1/agents/{agent_id}/status

# Agent-Logs prüfen
grep "agent_id:{agent_id}" /var/log/keiko/app.log

# Agent-Konfiguration validieren
./scripts/validate-agent-config.sh {agent_id}
```

**Lösungen:**

1. **Konfigurationsfehler beheben**
```yaml
# agents/example-agent.yml
name: "Example Agent"
type: "specialist"
capabilities:
  - "text_processing"
configuration:
  timeout_seconds: 300
  max_concurrent_tasks: 1
```

2. **Dependencies prüfen**
```python
# Agent-Dependencies validieren
async def validate_agent_dependencies(agent_config):
    for capability in agent_config.capabilities:
        if capability == "text_processing":
            try:
                import transformers
            except ImportError:
                raise AgentDependencyError("transformers package required")
```

3. **Resource-Limits prüfen**
```bash
# Memory-Limits
ulimit -v

# File-Descriptor-Limits
ulimit -n

# Process-Limits
ulimit -u
```

### Task-Execution-Fehler

**Problem:** Tasks schlagen fehl oder hängen.

**Diagnose:**
```bash
# Fehlgeschlagene Tasks
curl http://localhost:8000/api/v1/tasks?status=failed

# Hängende Tasks
curl http://localhost:8000/api/v1/tasks?status=running | jq '.[] | select(.created_at < (now - 3600))'

# Task-Logs
grep "task_id:{task_id}" /var/log/keiko/app.log
```

**Lösungen:**

1. **Timeout-Konfiguration**
```python
# Task-Timeout erhöhen
task_config = {
    "timeout_seconds": 600,  # 10 Minuten
    "retry_policy": {
        "max_retries": 3,
        "retry_delay": 5.0
    }
}
```

2. **Error-Handling verbessern**
```python
async def execute_task_with_error_handling(task):
    try:
        result = await agent.execute_task(task)
        return result
    except TimeoutError:
        logger.error(f"Task {task.id} timed out")
        return TaskResult.failure("Task timed out")
    except Exception as e:
        logger.error(f"Task {task.id} failed: {e}", exc_info=True)
        return TaskResult.failure(str(e))
```

3. **Resource-Monitoring**
```python
# Task-Resource-Monitoring
async def monitor_task_resources(task_id):
    process = psutil.Process()

    while task_is_running(task_id):
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()

        if memory_usage > 1000:  # 1GB
            logger.warning(f"Task {task_id} high memory usage: {memory_usage}MB")

        if cpu_usage > 90:
            logger.warning(f"Task {task_id} high CPU usage: {cpu_usage}%")

        await asyncio.sleep(10)
```

## 🌐 API-Probleme

### 500 Internal Server Error

**Problem:** API-Endpunkte geben 500-Fehler zurück.

**Diagnose:**
```bash
# Error-Logs prüfen
tail -f /var/log/keiko/error.log

# API-Health-Check
curl http://localhost:8000/health

# Specific-Endpoint testen
curl -v http://localhost:8000/api/v1/agents
```

**Lösungen:**

1. **Exception-Handling prüfen**
```python
# Unbehandelte Exceptions finden
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "request_id": str(uuid.uuid4())}
    )
```

2. **Dependency-Injection-Probleme**
```python
# DI-Container validieren
async def validate_dependencies():
    try:
        container = get_container()
        container.check_dependencies()
    except Exception as e:
        logger.error(f"DI validation failed: {e}")
```

### Rate-Limiting-Probleme

**Problem:** "Too Many Requests" (429) Fehler.

**Diagnose:**
```bash
# Rate-Limit-Status prüfen
curl -I http://localhost:8000/api/v1/agents

# Redis-Rate-Limit-Keys prüfen
redis-cli keys "rate_limit:*"
```

**Lösungen:**

1. **Rate-Limits anpassen**
```python
# config/rate_limits.py
RATE_LIMITS = {
    "default": {"requests": 100, "window": 60},
    "auth": {"requests": 10, "window": 60},
    "tasks": {"requests": 50, "window": 60}
}
```

2. **Client-seitige Retry-Logic**
```python
import asyncio
from aiohttp import ClientSession

async def api_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    await asyncio.sleep(retry_after)
                    continue
                return await response.json()

    raise Exception("Max retries exceeded")
```

## 📊 Performance-Probleme

### Hohe Response-Zeiten

**Problem:** API-Responses sind langsam (>2 Sekunden).

**Diagnose:**
```bash
# Response-Zeit messen
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/agents

# APM-Metriken prüfen
curl http://localhost:8000/metrics | grep http_request_duration
```

**Lösungen:**

1. **Caching implementieren**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_agent_config(agent_id: str):
    # Expensive operation
    return await load_agent_config(agent_id)
```

2. **Database-Query-Optimierung**
```python
# Batch-Loading
async def get_agents_with_stats(agent_ids: List[str]):
    query = (
        select(Agent, func.count(Task.id))
        .outerjoin(Task)
        .where(Agent.id.in_(agent_ids))
        .group_by(Agent.id)
    )
    return await session.execute(query)
```

3. **Async-Optimierung**
```python
# Parallel-Processing
async def process_multiple_tasks(tasks: List[Task]):
    results = await asyncio.gather(*[
        process_single_task(task) for task in tasks
    ])
    return results
```

!!! tip "Debugging-Tools"
    Nutzen Sie die integrierten Debugging-Tools:
    - `/debug/health` - Detaillierte Health-Informationen
    - `/debug/metrics` - Performance-Metriken
    - `/debug/config` - Aktuelle Konfiguration
    - `/debug/logs` - Recent-Log-Entries

!!! info "Support-Kanäle"
    Bei persistenten Problemen:
    - GitHub Issues: https://github.com/oscharko/keiko-personal-assistant/issues
    - Community-Forum: https://community.keiko.ai
    - Enterprise-Support: support@keiko.ai

# 🐛 Debugging Guide

Umfassender Leitfaden für das Debugging von Keiko Personal Assistant.

## 🔍 Debug-Modus aktivieren

### Development-Debug-Modus

```bash
# Environment-Variable setzen
export KEIKO_DEBUG=true
export KEIKO_LOG_LEVEL=DEBUG

# Debug-Konfiguration
cat > config/debug.yml << EOF
debug:
  enabled: true
  log_level: DEBUG
  profiling: true
  trace_requests: true
  detailed_errors: true

logging:
  level: DEBUG
  format: detailed
  include_traceback: true
  log_sql_queries: true
EOF

# Application mit Debug-Modus starten
uvicorn main:app --reload --log-level debug
```

### Production-Debug-Modus

```bash
# Temporärer Debug-Modus (nur für spezifische Session)
export KEIKO_TEMP_DEBUG=true

# Debug-Endpunkt aktivieren
curl -X POST http://localhost:8000/debug/enable \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"duration_minutes": 30}'
```

## 📊 Logging & Tracing

### Strukturiertes Logging

```python
# logging_config.py
from kei_agent import get_logger

logger = get_logger("debug")
logger.info(
    "Agent-Task gestartet",
    agent_id="agent-123",
    task_id="task-456",
    task_type="text_processing",
    user_id="user-789",
)
```

### Request-Tracing

```python
# middleware/tracing.py
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware für Request-Tracing."""

    async def dispatch(self, request: Request, call_next):
        # Correlation-ID generieren
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Request-Start protokollieren
        logger.info(
            "Request gestartet",
            method=request.method,
            url=str(request.url),
            correlation_id=correlation_id,
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host
        )

        start_time = time.time()

        try:
            response = await call_next(request)

            # Request-Ende protokollieren
            duration = time.time() - start_time
            logger.info(
                "Request abgeschlossen",
                correlation_id=correlation_id,
                status_code=response.status_code,
                duration_seconds=duration
            )

            # Correlation-ID in Response-Header
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request fehlgeschlagen",
                correlation_id=correlation_id,
                error_type=type(e).__name__,
                error_message=str(e),
                duration_seconds=duration,
                exc_info=True
            )
            raise

# Middleware registrieren
app.add_middleware(TracingMiddleware)
```

### Distributed Tracing

```python
# tracing/jaeger_config.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def configure_tracing():
    """Konfiguriert Jaeger-Tracing."""

    # Tracer-Provider konfigurieren
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Jaeger-Exporter konfigurieren
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    # Span-Processor hinzufügen
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    return tracer

# Tracing in Agent-Execution
async def execute_task_with_tracing(self, task: Task) -> TaskResult:
    """Führt Task mit Tracing aus."""

    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("agent.execute_task") as span:
        # Span-Attribute setzen
        span.set_attribute("agent.id", self.id)
        span.set_attribute("agent.type", self.config.type)
        span.set_attribute("task.id", task.id)
        span.set_attribute("task.type", task.type)

        try:
            result = await self._execute_task_logic(task)

            span.set_attribute("task.success", True)
            span.set_attribute("task.duration", result.execution_time)

            return result

        except Exception as e:
            span.set_attribute("task.success", False)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

## 🔧 Debug-Tools

### Interactive Debugger

```python
# debug/interactive.py (vereinfachtes Beispiel)
import asyncio
from kei_agent import get_logger

async def start_debug_session():
    logger = get_logger("debug-session")
    logger.info("Debug-Session gestartet")

if __name__ == "__main__":
    asyncio.run(start_debug_session())
```

### Memory-Profiling

```python
# debug/memory_profiler.py
import psutil
import tracemalloc
from memory_profiler import profile

class MemoryProfiler:
    """Memory-Profiling für Keiko."""

    def __init__(self):
        self.process = psutil.Process()
        tracemalloc.start()

    def get_memory_usage(self) -> dict:
        """Ruft aktuelle Memory-Usage ab."""

        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        # Tracemalloc-Statistiken
        current, peak = tracemalloc.get_traced_memory()

        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': memory_percent,
            'traced_current_mb': current / 1024 / 1024,
            'traced_peak_mb': peak / 1024 / 1024
        }

    def get_top_memory_consumers(self, limit: int = 10) -> list:
        """Ruft Top-Memory-Consumer ab."""

        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        return [
            {
                'filename': stat.traceback.format()[0],
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count
            }
            for stat in top_stats[:limit]
        ]

# Memory-Profiling-Decorator
def memory_profile(func):
    """Decorator für Memory-Profiling."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = MemoryProfiler()

        # Memory vor Ausführung
        memory_before = profiler.get_memory_usage()

        try:
            result = await func(*args, **kwargs)

            # Memory nach Ausführung
            memory_after = profiler.get_memory_usage()

            # Memory-Diff protokollieren
            memory_diff = memory_after['rss_mb'] - memory_before['rss_mb']

            logger.info(
                f"Memory-Profiling: {func.__name__}",
                memory_before_mb=memory_before['rss_mb'],
                memory_after_mb=memory_after['rss_mb'],
                memory_diff_mb=memory_diff,
                function=func.__name__
            )

            return result

        except Exception as e:
            logger.error(f"Function {func.__name__} failed during memory profiling: {e}")
            raise

    return wrapper

# Verwendung
@memory_profile
async def process_large_dataset(data):
    """Verarbeitet große Datenmengen."""
    # Implementation
    pass
```

### Performance-Profiling

```python
# debug/performance_profiler.py
import cProfile
import pstats
import time
from functools import wraps

class PerformanceProfiler:
    """Performance-Profiling für Keiko."""

    def __init__(self):
        self.profiler = cProfile.Profile()
        self.stats = None

    def start_profiling(self):
        """Startet Profiling."""
        self.profiler.enable()

    def stop_profiling(self):
        """Stoppt Profiling."""
        self.profiler.disable()
        self.stats = pstats.Stats(self.profiler)

    def get_top_functions(self, limit: int = 20) -> list:
        """Ruft Top-Funktionen nach Ausführungszeit ab."""

        if not self.stats:
            return []

        # Nach cumulative time sortieren
        self.stats.sort_stats('cumulative')

        # Top-Funktionen extrahieren
        top_functions = []
        for func, (cc, nc, tt, ct, callers) in list(self.stats.stats.items())[:limit]:
            top_functions.append({
                'function': f"{func[0]}:{func[1]}({func[2]})",
                'calls': nc,
                'total_time': tt,
                'cumulative_time': ct,
                'per_call': ct / nc if nc > 0 else 0
            })

        return top_functions

    def save_profile(self, filename: str):
        """Speichert Profiling-Ergebnisse."""
        if self.stats:
            self.stats.dump_stats(filename)

# Performance-Profiling-Decorator
def performance_profile(func):
    """Decorator für Performance-Profiling."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = PerformanceProfiler()

        start_time = time.time()
        profiler.start_profiling()

        try:
            result = await func(*args, **kwargs)

            profiler.stop_profiling()
            execution_time = time.time() - start_time

            # Top-Funktionen protokollieren
            top_functions = profiler.get_top_functions(5)

            logger.info(
                f"Performance-Profiling: {func.__name__}",
                execution_time=execution_time,
                top_functions=top_functions,
                function=func.__name__
            )

            # Profiling-Daten speichern (optional)
            if execution_time > 5.0:  # Nur bei langsamen Funktionen
                filename = f"/tmp/profile_{func.__name__}_{int(time.time())}.prof"
                profiler.save_profile(filename)
                logger.info(f"Profiling-Daten gespeichert: {filename}")

            return result

        except Exception as e:
            profiler.stop_profiling()
            logger.error(f"Function {func.__name__} failed during profiling: {e}")
            raise

    return wrapper
```

## 🔍 Debug-Endpunkte

### Debug-API-Endpunkte

```python
# api/debug.py (Ausschnitt)
from fastapi import APIRouter
from datetime import datetime
from kei_agent import get_health_manager, APIHealthCheck

debug_router = APIRouter(prefix="/debug", tags=["debug"])

@debug_router.get("/health")
async def debug_health():
    health = get_health_manager()
    health.register_check(APIHealthCheck(name="kei_api", url="https://api.kei-framework.com/health"))
    summary = await health.run_all_checks()
    return {"timestamp": datetime.utcnow().isoformat(), "overall_status": summary.overall_status}

@debug_router.get("/metrics")
async def debug_metrics():
    """Performance-Metriken."""

    return {
        'request_metrics': get_request_metrics(),
        'database_metrics': get_database_metrics(),
        'agent_metrics': get_agent_metrics(),
        'task_metrics': get_task_metrics(),
        'system_metrics': get_system_metrics()
    }

@debug_router.get("/config")
async def debug_config(admin_user = Depends(require_admin)):
    """Aktuelle Konfiguration (nur für Admins)."""

    config = get_current_config()

    # Sensitive Daten entfernen
    sanitized_config = sanitize_config(config)

    return sanitized_config

@debug_router.get("/logs")
async def debug_logs(
    level: str = "INFO",
    limit: int = 100,
    admin_user = Depends(require_admin)
):
    """Recent-Log-Entries."""

    logs = await get_recent_logs(level=level, limit=limit)

    return {
        'logs': logs,
        'total_count': len(logs),
        'level_filter': level
    }

@debug_router.post("/gc")
async def debug_garbage_collection(admin_user = Depends(require_admin)):
    """Erzwingt Garbage Collection."""

    import gc

    before_count = len(gc.get_objects())
    collected = gc.collect()
    after_count = len(gc.get_objects())

    return {
        'objects_before': before_count,
        'objects_after': after_count,
        'objects_collected': collected,
        'objects_freed': before_count - after_count
    }

@debug_router.get("/agents/{agent_id}/debug")
async def debug_agent(agent_id: str):
    """Debug-Informationen für spezifischen Agent."""

    agent = await get_agent(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")

    debug_info = {
        'agent_id': agent_id,
        'status': agent.status,
        'current_tasks': await get_agent_current_tasks(agent_id),
        'recent_tasks': await get_agent_recent_tasks(agent_id, limit=10),
        'performance_stats': await get_agent_performance_stats(agent_id),
        'resource_usage': await get_agent_resource_usage(agent_id),
        'error_history': await get_agent_error_history(agent_id, limit=5)
    }

    return debug_info
```

### Debug-CLI-Tools

```python
# cli/debug.py (vereinfachtes Beispiel)
import click
from kei_agent import get_logger

@click.group()
def debug():
    pass

@debug.command()
def ping():
    logger = get_logger("debug-cli")
    logger.info("Debug CLI ping")

if __name__ == '__main__':
    debug()

@debug.command()
@click.option('--duration', default=60, help='Profiling-Dauer in Sekunden')
@click.option('--output', default='profile.prof', help='Output-Datei')
def profile(duration, output):
    """Startet Performance-Profiling."""

    async def run_profiling():
        profiler = PerformanceProfiler()

        print(f"Starte Profiling für {duration} Sekunden...")
        profiler.start_profiling()

        await asyncio.sleep(duration)

        profiler.stop_profiling()
        profiler.save_profile(output)

        print(f"Profiling-Daten gespeichert: {output}")

        # Top-Funktionen anzeigen
        top_functions = profiler.get_top_functions(10)
        print("\nTop-Funktionen:")
        for func in top_functions:
            print(f"  {func['function']}: {func['cumulative_time']:.3f}s")

    asyncio.run(run_profiling())

@debug.command()
@click.option('--level', default='ERROR', help='Log-Level')
@click.option('--follow', '-f', is_flag=True, help='Follow-Modus')
def logs(level, follow):
    """Zeigt Logs an."""

    if follow:
        # Tail-ähnliche Funktionalität
        import time

        while True:
            logs = get_recent_logs(level=level, limit=10)
            for log in logs:
                print(f"{log['timestamp']} [{log['level']}] {log['message']}")

            time.sleep(1)
    else:
        logs = get_recent_logs(level=level, limit=50)
        for log in logs:
            print(f"{log['timestamp']} [{log['level']}] {log['message']}")

if __name__ == '__main__':
    debug()
```

## 🧪 Testing & Debugging

### Unit-Test-Debugging

```python
# tests/debug_test.py (Beispielstruktur)
import pytest

@pytest.mark.asyncio
async def test_plan_task_happy_path():
    assert True
```

!!! tip "Debug-Best-Practices" - Verwenden Sie strukturiertes Logging für bessere Nachverfolgbarkeit - Aktivieren Sie Tracing nur bei Bedarf (Performance-Impact) - Nutzen Sie Memory-Profiling bei Verdacht auf Memory-Leaks - Implementieren Sie umfassende Debug-Endpunkte für Production-Debugging

!!! warning "Production-Debugging"
Seien Sie vorsichtig beim Aktivieren von Debug-Modi in Production: - Begrenzen Sie Debug-Sessions zeitlich - Beschränken Sie Zugriff auf Admin-Benutzer - Überwachen Sie Performance-Impact - Deaktivieren Sie Debug-Modi nach Problemlösung

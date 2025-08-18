# ⚡ Performance Troubleshooting

Leitfaden zur Diagnose und Behebung von Performance-Problemen in Keiko Personal Assistant.

## 📊 Performance-Monitoring

### Key Performance Indicators (KPIs)

```python
# monitoring/performance_kpis.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceKPIs:
    """Performance-KPIs für Keiko."""

    # Response-Zeit-Ziele
    api_response_time_p95: float = 200.0  # ms
    api_response_time_p99: float = 500.0  # ms

    # Durchsatz-Ziele
    requests_per_second: float = 1000.0
    tasks_per_minute: float = 500.0

    # Resource-Ziele
    cpu_usage_max: float = 70.0  # %
    memory_usage_max: float = 80.0  # %
    database_connections_max: float = 80.0  # % of pool

    # Fehler-Ziele
    error_rate_max: float = 0.1  # %
    task_failure_rate_max: float = 1.0  # %

class PerformanceMonitor:
    """Performance-Monitor für KPI-Überwachung."""

    def __init__(self):
        self.kpis = PerformanceKPIs()
        self.metrics_collector = MetricsCollector()

    async def check_performance_health(self) -> Dict[str, bool]:
        """Prüft Performance-Health gegen KPIs."""

        current_metrics = await self.metrics_collector.get_current_metrics()

        health_status = {
            'api_response_time': current_metrics['api_p95'] <= self.kpis.api_response_time_p95,
            'throughput': current_metrics['rps'] >= self.kpis.requests_per_second,
            'cpu_usage': current_metrics['cpu_percent'] <= self.kpis.cpu_usage_max,
            'memory_usage': current_metrics['memory_percent'] <= self.kpis.memory_usage_max,
            'error_rate': current_metrics['error_rate'] <= self.kpis.error_rate_max
        }

        return health_status

    async def get_performance_alerts(self) -> List[Dict[str, str]]:
        """Ruft aktuelle Performance-Alerts ab."""

        health_status = await self.check_performance_health()
        alerts = []

        for metric, is_healthy in health_status.items():
            if not is_healthy:
                alerts.append({
                    'metric': metric,
                    'severity': 'warning' if metric in ['cpu_usage', 'memory_usage'] else 'critical',
                    'message': f"Performance-KPI verletzt: {metric}"
                })

        return alerts
```

### Real-Time Performance Dashboard

```python
# monitoring/dashboard.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

performance_router = APIRouter(prefix="/performance", tags=["performance"])

@performance_router.get("/dashboard")
async def performance_dashboard():
    """Performance-Dashboard."""

    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Keiko Performance Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            .metric-card {
                border: 1px solid #ddd;
                padding: 20px;
                margin: 10px;
                border-radius: 5px;
            }
            .metric-value {
                font-size: 2em;
                font-weight: bold;
            }
            .metric-good { color: green; }
            .metric-warning { color: orange; }
            .metric-critical { color: red; }
        </style>
    </head>
    <body>
        <h1>Keiko Performance Dashboard</h1>

        <div id="metrics-container">
            <div class="metric-card">
                <h3>API Response Time (P95)</h3>
                <div id="response-time" class="metric-value">Loading...</div>
            </div>

            <div class="metric-card">
                <h3>Requests per Second</h3>
                <div id="rps" class="metric-value">Loading...</div>
            </div>

            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div id="cpu-usage" class="metric-value">Loading...</div>
            </div>

            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div id="memory-usage" class="metric-value">Loading...</div>
            </div>
        </div>

        <div id="response-time-chart" style="width:100%;height:400px;"></div>
        <div id="throughput-chart" style="width:100%;height:400px;"></div>

        <script>
            async function updateMetrics() {
                const response = await fetch('/performance/metrics');
                const metrics = await response.json();

                // Metriken aktualisieren
                document.getElementById('response-time').textContent =
                    metrics.api_p95.toFixed(1) + ' ms';
                document.getElementById('rps').textContent =
                    metrics.rps.toFixed(0);
                document.getElementById('cpu-usage').textContent =
                    metrics.cpu_percent.toFixed(1) + '%';
                document.getElementById('memory-usage').textContent =
                    metrics.memory_percent.toFixed(1) + '%';

                // Farben basierend auf Thresholds
                updateMetricColor('response-time', metrics.api_p95, 200, 500);
                updateMetricColor('cpu-usage', metrics.cpu_percent, 70, 90);
                updateMetricColor('memory-usage', metrics.memory_percent, 80, 95);
            }

            function updateMetricColor(elementId, value, warning, critical) {
                const element = document.getElementById(elementId);
                element.className = 'metric-value ' +
                    (value < warning ? 'metric-good' :
                     value < critical ? 'metric-warning' : 'metric-critical');
            }

            // Charts erstellen
            async function createCharts() {
                const response = await fetch('/performance/history');
                const history = await response.json();

                // Response-Time-Chart
                Plotly.newPlot('response-time-chart', [{
                    x: history.timestamps,
                    y: history.response_times,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Response Time (ms)'
                }], {
                    title: 'API Response Time History',
                    xaxis: { title: 'Time' },
                    yaxis: { title: 'Response Time (ms)' }
                });

                // Throughput-Chart
                Plotly.newPlot('throughput-chart', [{
                    x: history.timestamps,
                    y: history.throughput,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Requests/sec'
                }], {
                    title: 'Throughput History',
                    xaxis: { title: 'Time' },
                    yaxis: { title: 'Requests per Second' }
                });
            }

            // Initial load
            updateMetrics();
            createCharts();

            // Auto-refresh alle 5 Sekunden
            setInterval(updateMetrics, 5000);
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=dashboard_html)

@performance_router.get("/metrics")
async def get_current_metrics():
    """Aktuelle Performance-Metriken."""

    monitor = PerformanceMonitor()
    metrics = await monitor.metrics_collector.get_current_metrics()

    return metrics

@performance_router.get("/history")
async def get_performance_history(hours: int = 24):
    """Performance-Historie."""

    # Historie aus Monitoring-System abrufen
    history = await get_metrics_history(hours=hours)

    return {
        'timestamps': history['timestamps'],
        'response_times': history['api_p95'],
        'throughput': history['rps'],
        'cpu_usage': history['cpu_percent'],
        'memory_usage': history['memory_percent']
    }
```

## 🐌 Slow Query Diagnosis

### Database Performance Analysis

```python
# diagnosis/database_analyzer.py
import asyncio
from sqlalchemy import text

class DatabasePerformanceAnalyzer:
    """Analysiert Database-Performance."""

    def __init__(self, db_session):
        self.db_session = db_session

    async def analyze_slow_queries(self, min_duration_ms: int = 1000) -> List[Dict[str, Any]]:
        """Analysiert langsame Queries."""

        query = text("""
            SELECT
                query,
                mean_exec_time,
                calls,
                total_exec_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements
            WHERE mean_exec_time > :min_duration
            ORDER BY mean_exec_time DESC
            LIMIT 20
        """)

        result = await self.db_session.execute(query, {"min_duration": min_duration_ms})

        slow_queries = []
        for row in result:
            slow_queries.append({
                'query': row.query[:200] + '...' if len(row.query) > 200 else row.query,
                'mean_exec_time_ms': float(row.mean_exec_time),
                'calls': row.calls,
                'total_exec_time_ms': float(row.total_exec_time),
                'avg_rows': row.rows / row.calls if row.calls > 0 else 0,
                'cache_hit_percent': float(row.hit_percent or 0)
            })

        return slow_queries

    async def analyze_missing_indexes(self) -> List[Dict[str, Any]]:
        """Analysiert fehlende Indizes."""

        query = text("""
            SELECT
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE schemaname = 'public'
            AND n_distinct > 100
            AND correlation < 0.1
            ORDER BY n_distinct DESC
        """)

        result = await self.db_session.execute(query)

        missing_indexes = []
        for row in result:
            # Prüfen ob Index bereits existiert
            index_exists = await self._check_index_exists(row.tablename, row.attname)

            if not index_exists:
                missing_indexes.append({
                    'table': row.tablename,
                    'column': row.attname,
                    'distinct_values': row.n_distinct,
                    'correlation': float(row.correlation),
                    'suggested_index': f"CREATE INDEX idx_{row.tablename}_{row.attname} ON {row.tablename}({row.attname});"
                })

        return missing_indexes

    async def _check_index_exists(self, table_name: str, column_name: str) -> bool:
        """Prüft ob Index für Spalte existiert."""

        query = text("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename = :table_name
            AND indexdef LIKE '%' || :column_name || '%'
        """)

        result = await self.db_session.execute(query, {
            "table_name": table_name,
            "column_name": column_name
        })

        return result.scalar() > 0

    async def get_table_statistics(self) -> List[Dict[str, Any]]:
        """Ruft Tabellen-Statistiken ab."""

        query = text("""
            SELECT
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
        """)

        result = await self.db_session.execute(query)

        table_stats = []
        for row in result:
            table_stats.append({
                'table': f"{row.schemaname}.{row.tablename}",
                'inserts': row.inserts,
                'updates': row.updates,
                'deletes': row.deletes,
                'live_tuples': row.live_tuples,
                'dead_tuples': row.dead_tuples,
                'dead_tuple_ratio': row.dead_tuples / max(row.live_tuples, 1),
                'last_vacuum': row.last_vacuum,
                'last_analyze': row.last_analyze,
                'needs_vacuum': row.dead_tuples > 1000 and row.dead_tuples / max(row.live_tuples, 1) > 0.1
            })

        return table_stats
```

### Query Optimization Recommendations

```python
# diagnosis/query_optimizer.py
class QueryOptimizer:
    """Gibt Query-Optimierungs-Empfehlungen."""

    async def analyze_query_plan(self, query: str) -> Dict[str, Any]:
        """Analysiert Query-Execution-Plan."""

        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        result = await self.db_session.execute(text(explain_query))
        plan_data = result.scalar()

        analysis = {
            'total_cost': plan_data[0]['Plan']['Total Cost'],
            'execution_time': plan_data[0]['Execution Time'],
            'planning_time': plan_data[0]['Planning Time'],
            'recommendations': []
        }

        # Analyse des Plans
        plan = plan_data[0]['Plan']
        analysis['recommendations'].extend(self._analyze_plan_node(plan))

        return analysis

    def _analyze_plan_node(self, node: Dict[str, Any]) -> List[str]:
        """Analysiert einzelnen Plan-Node."""

        recommendations = []

        # Sequential Scan Detection
        if node.get('Node Type') == 'Seq Scan':
            table_name = node.get('Relation Name', 'unknown')
            recommendations.append(
                f"Sequential Scan auf {table_name} - Index könnte helfen"
            )

        # Nested Loop mit hohen Kosten
        if node.get('Node Type') == 'Nested Loop' and node.get('Total Cost', 0) > 1000:
            recommendations.append(
                "Nested Loop mit hohen Kosten - JOIN-Optimierung prüfen"
            )

        # Sort mit hohem Memory-Verbrauch
        if node.get('Node Type') == 'Sort' and node.get('Sort Space Used', 0) > 1000:
            recommendations.append(
                "Sort-Operation mit hohem Memory-Verbrauch - work_mem erhöhen"
            )

        # Hash Join ohne Index
        if node.get('Node Type') == 'Hash Join':
            recommendations.append(
                "Hash Join - Index auf JOIN-Spalten prüfen"
            )

        # Rekursive Analyse für Child-Nodes
        for child in node.get('Plans', []):
            recommendations.extend(self._analyze_plan_node(child))

        return recommendations

    async def suggest_index_optimizations(self, table_name: str) -> List[str]:
        """Schlägt Index-Optimierungen vor."""

        suggestions = []

        # Häufig verwendete WHERE-Spalten
        frequent_where_columns = await self._get_frequent_where_columns(table_name)
        for column in frequent_where_columns:
            suggestions.append(
                f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column});"
            )

        # Häufig verwendete ORDER BY-Spalten
        frequent_order_columns = await self._get_frequent_order_columns(table_name)
        for column in frequent_order_columns:
            suggestions.append(
                f"CREATE INDEX idx_{table_name}_{column}_order ON {table_name}({column});"
            )

        # Composite-Indizes für häufige WHERE-Kombinationen
        frequent_combinations = await self._get_frequent_column_combinations(table_name)
        for combination in frequent_combinations:
            columns = ', '.join(combination)
            suggestions.append(
                f"CREATE INDEX idx_{table_name}_{'_'.join(combination)} ON {table_name}({columns});"
            )

        return suggestions
```

## 🚀 Application Performance Tuning

### Async Performance Optimization

```python
# optimization/async_optimizer.py
import asyncio
from typing import List, Callable, Any

class AsyncPerformanceOptimizer:
    """Optimiert Async-Performance."""

    def __init__(self, max_concurrent: int = 100):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def batch_process_with_concurrency(
        self,
        items: List[Any],
        processor: Callable,
        batch_size: int = 50
    ) -> List[Any]:
        """Verarbeitet Items in Batches mit Concurrency-Control."""

        results = []

        # Items in Batches aufteilen
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # Batch parallel verarbeiten
            batch_tasks = [
                self._process_with_semaphore(processor, item)
                for item in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Erfolgreiche Ergebnisse sammeln
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)
                else:
                    logger.error(f"Batch processing error: {result}")

            # Kurze Pause zwischen Batches
            await asyncio.sleep(0.1)

        return results

    async def _process_with_semaphore(self, processor: Callable, item: Any) -> Any:
        """Verarbeitet Item mit Semaphore-Control."""

        async with self.semaphore:
            return await processor(item)

    async def optimize_database_operations(self, operations: List[Callable]) -> List[Any]:
        """Optimiert Database-Operationen."""

        # Operationen nach Typ gruppieren
        read_ops = [op for op in operations if getattr(op, 'is_read', True)]
        write_ops = [op for op in operations if not getattr(op, 'is_read', True)]

        # Read-Operationen parallel ausführen
        read_results = await asyncio.gather(*read_ops, return_exceptions=True)

        # Write-Operationen sequenziell ausführen (für Konsistenz)
        write_results = []
        for write_op in write_ops:
            try:
                result = await write_op()
                write_results.append(result)
            except Exception as e:
                logger.error(f"Write operation failed: {e}")
                write_results.append(e)

        return read_results + write_results
```

### Memory Optimization

```python
# optimization/memory_optimizer.py
import gc
import weakref
from typing import Dict, Any, Optional

class MemoryOptimizer:
    """Optimiert Memory-Nutzung."""

    def __init__(self):
        self.object_cache: Dict[str, weakref.WeakValueDictionary] = {}
        self.memory_threshold_mb = 1000  # 1GB

    def get_cached_object(self, cache_key: str, object_id: str) -> Optional[Any]:
        """Ruft Objekt aus Cache ab."""

        if cache_key not in self.object_cache:
            self.object_cache[cache_key] = weakref.WeakValueDictionary()

        return self.object_cache[cache_key].get(object_id)

    def cache_object(self, cache_key: str, object_id: str, obj: Any) -> None:
        """Cached Objekt."""

        if cache_key not in self.object_cache:
            self.object_cache[cache_key] = weakref.WeakValueDictionary()

        self.object_cache[cache_key][object_id] = obj

    def check_memory_usage(self) -> Dict[str, float]:
        """Prüft aktuelle Memory-Nutzung."""

        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }

    async def optimize_memory_if_needed(self) -> bool:
        """Optimiert Memory wenn nötig."""

        memory_usage = self.check_memory_usage()

        if memory_usage['rss_mb'] > self.memory_threshold_mb:
            logger.warning(f"High memory usage: {memory_usage['rss_mb']:.1f}MB")

            # Garbage Collection erzwingen
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")

            # Cache leeren
            self.clear_caches()

            # Memory-Usage nach Optimierung prüfen
            new_memory_usage = self.check_memory_usage()
            memory_freed = memory_usage['rss_mb'] - new_memory_usage['rss_mb']

            logger.info(f"Memory optimization freed {memory_freed:.1f}MB")

            return memory_freed > 50  # Erfolgreich wenn >50MB befreit

        return False

    def clear_caches(self) -> None:
        """Leert alle Caches."""

        for cache in self.object_cache.values():
            cache.clear()

        logger.info("All caches cleared")

# Memory-optimierter Decorator
def memory_optimized(func):
    """Decorator für Memory-Optimierung."""

    optimizer = MemoryOptimizer()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Memory vor Ausführung prüfen
        await optimizer.optimize_memory_if_needed()

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Memory nach Ausführung prüfen
            await optimizer.optimize_memory_if_needed()

    return wrapper
```

## 📈 Performance Testing

### Load Testing

```python
# testing/load_test.py
import asyncio
import aiohttp
import time
from dataclasses import dataclass
from typing import List

@dataclass
class LoadTestResult:
    """Load-Test-Ergebnis."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float

class LoadTester:
    """Load-Tester für Keiko API."""

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.auth_token = auth_token
        self.response_times: List[float] = []
        self.errors: List[str] = []

    async def run_load_test(
        self,
        endpoint: str,
        concurrent_users: int = 50,
        duration_seconds: int = 300,
        request_data: dict = None
    ) -> LoadTestResult:
        """Führt Load-Test aus."""

        start_time = time.time()
        end_time = start_time + duration_seconds

        # Semaphore für Concurrency-Control
        semaphore = asyncio.Semaphore(concurrent_users)

        # Tasks für alle User starten
        tasks = []
        for user_id in range(concurrent_users):
            task = asyncio.create_task(
                self._user_session(semaphore, endpoint, end_time, request_data, user_id)
            )
            tasks.append(task)

        # Auf alle Tasks warten
        await asyncio.gather(*tasks, return_exceptions=True)

        # Ergebnisse berechnen
        return self._calculate_results(duration_seconds)

    async def _user_session(
        self,
        semaphore: asyncio.Semaphore,
        endpoint: str,
        end_time: float,
        request_data: dict,
        user_id: int
    ):
        """Simuliert einzelne User-Session."""

        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                async with semaphore:
                    await self._make_request(session, endpoint, request_data, user_id)

                # Kurze Pause zwischen Requests
                await asyncio.sleep(0.1)

    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        request_data: dict,
        user_id: int
    ):
        """Macht einzelnen Request."""

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        start_time = time.time()

        try:
            if request_data:
                async with session.post(url, json=request_data, headers=headers) as response:
                    await response.text()  # Response lesen
                    response_time = time.time() - start_time
                    self.response_times.append(response_time * 1000)  # ms

                    if response.status >= 400:
                        self.errors.append(f"HTTP {response.status}")
            else:
                async with session.get(url, headers=headers) as response:
                    await response.text()
                    response_time = time.time() - start_time
                    self.response_times.append(response_time * 1000)  # ms

                    if response.status >= 400:
                        self.errors.append(f"HTTP {response.status}")

        except Exception as e:
            response_time = time.time() - start_time
            self.response_times.append(response_time * 1000)
            self.errors.append(str(e))

    def _calculate_results(self, duration_seconds: int) -> LoadTestResult:
        """Berechnet Test-Ergebnisse."""

        total_requests = len(self.response_times)
        failed_requests = len(self.errors)
        successful_requests = total_requests - failed_requests

        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            sorted_times = sorted(self.response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            p95_response_time = sorted_times[p95_index]
            p99_response_time = sorted_times[p99_index]
        else:
            avg_response_time = 0
            p95_response_time = 0
            p99_response_time = 0

        requests_per_second = total_requests / duration_seconds
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0

        return LoadTestResult(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )

# Load-Test ausführen
async def run_api_load_test():
    """Führt API-Load-Test aus."""

    tester = LoadTester(
        base_url="http://localhost:8000",
        auth_token="your-auth-token"
    )

    # Agent-Listing-Test
    result = await tester.run_load_test(
        endpoint="/api/v1/agents",
        concurrent_users=50,
        duration_seconds=300
    )

    print(f"Load Test Results:")
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful: {result.successful_requests}")
    print(f"Failed: {result.failed_requests}")
    print(f"Avg Response Time: {result.avg_response_time:.1f}ms")
    print(f"P95 Response Time: {result.p95_response_time:.1f}ms")
    print(f"P99 Response Time: {result.p99_response_time:.1f}ms")
    print(f"Requests/sec: {result.requests_per_second:.1f}")
    print(f"Error Rate: {result.error_rate:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_api_load_test())
```

!!! tip "Performance-Optimierung-Tipps"
    - Überwachen Sie kontinuierlich die Key-Performance-Indicators
    - Nutzen Sie Database-Query-Analyse für Optimierungen
    - Implementieren Sie effektive Caching-Strategien
    - Optimieren Sie Async-Operations für bessere Concurrency
    - Führen Sie regelmäßige Load-Tests durch

!!! warning "Performance-Monitoring"
    - Setzen Sie realistische Performance-Ziele
    - Überwachen Sie Trends, nicht nur absolute Werte
    - Berücksichtigen Sie Business-Kontext bei Optimierungen
    - Dokumentieren Sie Performance-Änderungen

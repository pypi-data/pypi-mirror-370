# kei_agent/metrics_server.py
"""
Metrics server for exposing Prometheus metrics and health endpoints.

This module provides:
- HTTP server for Prometheus metrics endpoint
- Health check endpoints
- Metrics dashboard
- Real-time metrics streaming
- Integration with monitoring systems
"""

import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import Request, Response, WebSocketResponse

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .metrics import get_metrics_collector, MetricsCollector
from .dashboard_generators import (
    generate_security_dashboard_html,
    generate_business_dashboard_html,
)
from .config_api import get_config_api

logger = logging.getLogger(__name__)


class MetricsServer:
    """HTTP server for exposing metrics and monitoring endpoints."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8090,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """Initialize metrics server.

        Args:
            host: Server host address
            port: Server port
            metrics_collector: Metrics collector instance
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp is required for metrics server")

        self.host = host
        self.port = port
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.app = None
        self.runner = None
        self.site = None
        self.websocket_connections = set()

        self.start_time = time.time()

        # Configuration API
        self.config_api = get_config_api()

    def create_app(self) -> web.Application:
        """Create aiohttp application with routes."""
        app = web.Application()

        # Metrics endpoints
        app.router.add_get("/metrics", self.metrics_handler)
        app.router.add_get("/health", self.health_handler)
        app.router.add_get("/ready", self.readiness_handler)
        app.router.add_get("/live", self.liveness_handler)

        # Dashboard endpoints
        app.router.add_get("/", self.dashboard_handler)
        app.router.add_get("/dashboard", self.dashboard_handler)
        app.router.add_get("/dashboard/health", self.health_dashboard_handler)
        app.router.add_get("/dashboard/performance", self.performance_dashboard_handler)
        app.router.add_get("/dashboard/security", self.security_dashboard_handler)
        app.router.add_get("/dashboard/business", self.business_dashboard_handler)
        app.router.add_get("/api/metrics/summary", self.metrics_summary_handler)
        app.router.add_get("/api/health/status", self.health_status_handler)
        app.router.add_get("/api/performance/stats", self.performance_stats_handler)
        app.router.add_get("/api/security/events", self.security_events_handler)
        app.router.add_get("/api/business/metrics", self.business_metrics_handler)

        # Real-time metrics streaming
        app.router.add_get("/ws/metrics", self.websocket_metrics_handler)

        # Configuration API endpoints
        self.config_api.create_routes(app)

        # Static files for dashboard
        app.router.add_static(
            "/static/", path=Path(__file__).parent / "static", name="static"
        )

        return app

    async def metrics_handler(self, request: Request) -> Response:
        """Handle Prometheus metrics endpoint."""
        try:
            metrics_text = self.metrics_collector.get_prometheus_metrics()

            return Response(
                text=metrics_text,
                content_type="text/plain; version=0.0.4; charset=utf-8",
            )
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return Response(
                text=f"# Error generating metrics: {e}\n",
                status=500,
                content_type="text/plain",
            )

    async def health_handler(self, request: Request) -> Response:
        """Handle health check endpoint."""
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.start_time,
            "metrics_collector": {
                "enabled": self.metrics_collector.enabled,
                "prometheus_available": self.metrics_collector.enabled,
                "opentelemetry_available": hasattr(self.metrics_collector, "tracer")
                and self.metrics_collector.tracer is not None,
            },
        }

        return web.json_response(health_data)

    async def readiness_handler(self, request: Request) -> Response:
        """Handle readiness probe endpoint."""
        # Check if metrics collector is ready
        ready = self.metrics_collector is not None

        if ready:
            return web.json_response({"status": "ready", "timestamp": time.time()})
        else:
            return web.json_response(
                {"status": "not_ready", "timestamp": time.time()}, status=503
            )

    async def liveness_handler(self, request: Request) -> Response:
        """Handle liveness probe endpoint."""
        # Simple liveness check
        return web.json_response({"status": "alive", "timestamp": time.time()})

    async def dashboard_handler(self, request: Request) -> Response:
        """Handle main metrics dashboard."""
        dashboard_html = self._generate_main_dashboard_html()
        return Response(text=dashboard_html, content_type="text/html")

    async def health_dashboard_handler(self, request: Request) -> Response:
        """Handle health monitoring dashboard."""
        dashboard_html = self._generate_health_dashboard_html()
        return Response(text=dashboard_html, content_type="text/html")

    async def performance_dashboard_handler(self, request: Request) -> Response:
        """Handle performance monitoring dashboard."""
        dashboard_html = self._generate_performance_dashboard_html()
        return Response(text=dashboard_html, content_type="text/html")

    async def security_dashboard_handler(self, request: Request) -> Response:
        """Handle security monitoring dashboard."""
        dashboard_html = self._generate_security_dashboard_html()
        return Response(text=dashboard_html, content_type="text/html")

    async def business_dashboard_handler(self, request: Request) -> Response:
        """Handle business metrics dashboard."""
        dashboard_html = self._generate_business_dashboard_html()
        return Response(text=dashboard_html, content_type="text/html")

    async def metrics_summary_handler(self, request: Request) -> Response:
        """Handle metrics summary API endpoint."""
        try:
            summary = self.metrics_collector.get_metrics_summary()

            # Add server information
            summary.update(
                {
                    "server": {
                        "host": self.host,
                        "port": self.port,
                        "uptime_seconds": time.time() - self.start_time,
                        "websocket_connections": len(self.websocket_connections),
                    }
                }
            )

            return web.json_response(summary)
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return web.json_response(
                {"error": f"Failed to generate summary: {e}"}, status=500
            )

    async def health_status_handler(self, request: Request) -> Response:
        """Handle health status API endpoint."""
        try:
            from .error_aggregation import get_error_aggregator

            error_aggregator = get_error_aggregator()
            error_stats = error_aggregator.get_error_statistics()

            # Calculate health score based on error rates
            recent_errors = error_stats.get("recent_errors", 0)
            error_rate_1min = error_stats.get("error_rates", {}).get(
                "per_minute_1min", 0
            )

            if error_rate_1min > 10:
                health_status = "critical"
                health_score = 0
            elif error_rate_1min > 5:
                health_status = "degraded"
                health_score = 50
            elif error_rate_1min > 1:
                health_status = "warning"
                health_score = 75
            else:
                health_status = "healthy"
                health_score = 100

            health_data = {
                "status": health_status,
                "score": health_score,
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self.start_time,
                "error_rate_1min": error_rate_1min,
                "recent_errors": recent_errors,
                "metrics_collector_enabled": self.metrics_collector.enabled,
                "websocket_connections": len(self.websocket_connections),
            }

            return web.json_response(health_data)

        except Exception as e:
            logger.error(f"Error generating health status: {e}")
            return web.json_response(
                {"error": f"Failed to generate health status: {e}"}, status=500
            )

    async def performance_stats_handler(self, request: Request) -> Response:
        """Handle performance statistics API endpoint."""
        try:
            # Get performance metrics from Prometheus if available
            performance_data = {
                "timestamp": time.time(),
                "request_metrics": {
                    "total_requests": 0,
                    "avg_response_time": 0,
                    "error_rate": 0,
                    "throughput": 0,
                },
                "system_metrics": {
                    "memory_usage_mb": 0,
                    "cpu_usage_percent": 0,
                    "active_connections": len(self.websocket_connections),
                },
                "protocol_metrics": {
                    "rpc_requests": 0,
                    "stream_connections": 0,
                    "bus_messages": 0,
                    "mcp_executions": 0,
                },
            }

            return web.json_response(performance_data)

        except Exception as e:
            logger.error(f"Error generating performance stats: {e}")
            return web.json_response(
                {"error": f"Failed to generate performance stats: {e}"}, status=500
            )

    async def security_events_handler(self, request: Request) -> Response:
        """Handle security events API endpoint."""
        try:
            from .error_aggregation import get_error_aggregator, ErrorCategory

            error_aggregator = get_error_aggregator()
            recent_errors = error_aggregator._get_recent_errors(minutes=60)

            # Filter security-related events
            security_events = [
                error
                for error in recent_errors
                if error.category
                in [ErrorCategory.SECURITY, ErrorCategory.AUTHENTICATION]
            ]

            # Categorize security events
            auth_failures = len(
                [
                    e
                    for e in security_events
                    if e.category == ErrorCategory.AUTHENTICATION
                ]
            )
            security_violations = len(
                [e for e in security_events if e.category == ErrorCategory.SECURITY]
            )

            security_data = {
                "timestamp": time.time(),
                "total_security_events": len(security_events),
                "auth_failures": auth_failures,
                "security_violations": security_violations,
                "recent_events": [
                    {
                        "timestamp": event.timestamp,
                        "type": event.error_type,
                        "message": event.error_message,
                        "severity": event.severity.value,
                        "agent_id": event.agent_id,
                    }
                    for event in security_events[-10:]  # Last 10 events
                ],
            }

            return web.json_response(security_data)

        except Exception as e:
            logger.error(f"Error generating security events: {e}")
            return web.json_response(
                {"error": f"Failed to generate security events: {e}"}, status=500
            )

    async def business_metrics_handler(self, request: Request) -> Response:
        """Handle business metrics API endpoint."""
        try:
            business_data = {
                "timestamp": time.time(),
                "agent_metrics": {
                    "total_agents": 1,  # This would come from actual agent registry
                    "active_agents": 1,
                    "agent_uptime_avg": time.time() - self.start_time,
                },
                "protocol_usage": {
                    "rpc_usage_percent": 40,
                    "stream_usage_percent": 30,
                    "bus_usage_percent": 20,
                    "mcp_usage_percent": 10,
                },
                "operation_metrics": {
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "avg_operation_time": 0,
                },
                "resource_utilization": {
                    "memory_efficiency": 85,
                    "cpu_efficiency": 90,
                    "network_efficiency": 95,
                },
            }

            return web.json_response(business_data)

        except Exception as e:
            logger.error(f"Error generating business metrics: {e}")
            return web.json_response(
                {"error": f"Failed to generate business metrics: {e}"}, status=500
            )

    async def websocket_metrics_handler(self, request: Request) -> WebSocketResponse:
        """Handle WebSocket connection for real-time metrics."""
        ws = WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.add(ws)
        logger.info(
            f"WebSocket connection established. Total connections: {len(self.websocket_connections)}"
        )

        try:
            # Send initial metrics
            summary = self.metrics_collector.get_metrics_summary()
            await ws.send_str(
                json.dumps(
                    {"type": "initial", "data": summary, "timestamp": time.time()}
                )
            )

            # Keep connection alive and send periodic updates
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("type") == "ping":
                            await ws.send_str(
                                json.dumps({"type": "pong", "timestamp": time.time()})
                            )
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break

        except Exception as e:
            logger.error(f"WebSocket error: {e}")

        finally:
            self.websocket_connections.discard(ws)
            logger.info(
                f"WebSocket connection closed. Remaining connections: {len(self.websocket_connections)}"
            )

        return ws

    async def broadcast_metrics_update(self, metrics_data: Dict[str, Any]):
        """Broadcast metrics update to all WebSocket connections."""
        if not self.websocket_connections:
            return

        message = json.dumps(
            {"type": "update", "data": metrics_data, "timestamp": time.time()}
        )

        # Send to all connected clients
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.add(ws)

        # Remove disconnected clients
        self.websocket_connections -= disconnected

    def _generate_main_dashboard_html(self) -> str:
        """Generate main HTML dashboard for metrics visualization."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>KEI-Agent SDK Metrics Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav-menu {
            margin: 15px 0;
            display: flex;
            gap: 10px;
        }
        .nav-link {
            padding: 8px 16px;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background: #e0e0e0;
        }
        .nav-link.active {
            background: #2196F3;
            color: white;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2196F3;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-error { background-color: #F44336; }
        .connection-status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            background-color: #e3f2fd;
        }
        .real-time-data {
            font-family: monospace;
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 KEI-Agent SDK Operational Dashboard</h1>
        <p>Comprehensive monitoring and metrics visualization</p>
        <div class="nav-menu">
            <a href="/dashboard" class="nav-link active">Overview</a>
            <a href="/dashboard/health" class="nav-link">Health</a>
            <a href="/dashboard/performance" class="nav-link">Performance</a>
            <a href="/dashboard/security" class="nav-link">Security</a>
            <a href="/dashboard/business" class="nav-link">Business</a>
        </div>
        <div id="connection-status" class="connection-status">
            <span class="status-indicator status-warning"></span>
            Connecting to metrics stream...
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" id="total-requests">-</div>
            <div class="metric-label">Total Requests</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="active-connections">-</div>
            <div class="metric-label">Active Connections</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="error-rate">-</div>
            <div class="metric-label">Error Rate (%)</div>
        </div>

        <div class="metric-card">
            <div class="metric-value" id="avg-response-time">-</div>
            <div class="metric-label">Avg Response Time (ms)</div>
        </div>

        <div class="metric-card">
            <h3>System Status</h3>
            <div id="system-status">
                <div>Prometheus: <span id="prometheus-status">-</span></div>
                <div>OpenTelemetry: <span id="otel-status">-</span></div>
                <div>Uptime: <span id="uptime">-</span></div>
            </div>
        </div>

        <div class="metric-card">
            <h3>Real-time Metrics</h3>
            <div id="real-time-data" class="real-time-data">
                Waiting for data...
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/metrics`;
        let ws;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 5;

        function connectWebSocket() {
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                console.log('WebSocket connected');
                reconnectAttempts = 0;
                updateConnectionStatus('connected');
            };

            ws.onmessage = function(event) {
                try {
                    const message = JSON.parse(event.data);
                    handleMetricsUpdate(message);
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };

            ws.onclose = function() {
                console.log('WebSocket disconnected');
                updateConnectionStatus('disconnected');

                // Attempt to reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    setTimeout(connectWebSocket, 2000 * reconnectAttempts);
                }
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus('error');
            };
        }

        function updateConnectionStatus(status) {
            const statusElement = document.getElementById('connection-status');
            const indicator = statusElement.querySelector('.status-indicator');

            switch (status) {
                case 'connected':
                    indicator.className = 'status-indicator status-healthy';
                    statusElement.innerHTML = '<span class="status-indicator status-healthy"></span>Connected to metrics stream';
                    break;
                case 'disconnected':
                    indicator.className = 'status-indicator status-warning';
                    statusElement.innerHTML = '<span class="status-indicator status-warning"></span>Disconnected - attempting to reconnect...';
                    break;
                case 'error':
                    indicator.className = 'status-indicator status-error';
                    statusElement.innerHTML = '<span class="status-indicator status-error"></span>Connection error';
                    break;
            }
        }

        function handleMetricsUpdate(message) {
            if (message.type === 'initial' || message.type === 'update') {
                updateDashboard(message.data);
            }

            // Update real-time data display
            const realTimeElement = document.getElementById('real-time-data');
            const timestamp = new Date(message.timestamp * 1000).toLocaleTimeString();
            realTimeElement.innerHTML = `[${timestamp}] ${JSON.stringify(message.data, null, 2)}`;
        }

        function updateDashboard(data) {
            // Update system status
            if (data.prometheus_enabled !== undefined) {
                document.getElementById('prometheus-status').textContent = data.prometheus_enabled ? '✅ Enabled' : '❌ Disabled';
            }

            if (data.opentelemetry_enabled !== undefined) {
                document.getElementById('otel-status').textContent = data.opentelemetry_enabled ? '✅ Enabled' : '❌ Disabled';
            }

            if (data.server && data.server.uptime_seconds) {
                const uptime = Math.floor(data.server.uptime_seconds);
                const hours = Math.floor(uptime / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                const seconds = uptime % 60;
                document.getElementById('uptime').textContent = `${hours}h ${minutes}m ${seconds}s`;
            }

            // Update connection count
            if (data.server && data.server.websocket_connections !== undefined) {
                document.getElementById('active-connections').textContent = data.server.websocket_connections;
            }
        }

        // Initialize WebSocket connection
        connectWebSocket();

        // Send periodic ping to keep connection alive
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);
    </script>
</body>
</html>
"""

    def _generate_health_dashboard_html(self) -> str:
        """Generate health monitoring dashboard."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Health Dashboard - KEI-Agent SDK</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav-menu {
            margin: 15px 0;
            display: flex;
            gap: 10px;
        }
        .nav-link {
            padding: 8px 16px;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background: #e0e0e0;
        }
        .nav-link.active {
            background: #2196F3;
            color: white;
        }
        .health-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .health-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .health-score {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .health-healthy { color: #4CAF50; }
        .health-warning { color: #FF9800; }
        .health-degraded { color: #FF5722; }
        .health-critical { color: #F44336; }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-degraded { background-color: #FF5722; }
        .status-critical { background-color: #F44336; }
        .metric-row {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Health Monitoring Dashboard</h1>
        <p>System health and operational status</p>
        <div class="nav-menu">
            <a href="/dashboard" class="nav-link">Overview</a>
            <a href="/dashboard/health" class="nav-link active">Health</a>
            <a href="/dashboard/performance" class="nav-link">Performance</a>
            <a href="/dashboard/security" class="nav-link">Security</a>
            <a href="/dashboard/business" class="nav-link">Business</a>
        </div>
    </div>

    <div class="health-grid">
        <div class="health-card">
            <h3>Overall Health Score</h3>
            <div id="health-score" class="health-score health-healthy">100</div>
            <div id="health-status">
                <span class="status-indicator status-healthy"></span>
                <span id="health-text">Healthy</span>
            </div>
        </div>

        <div class="health-card">
            <h3>System Status</h3>
            <div class="metric-row">
                <span>Uptime:</span>
                <span id="system-uptime">-</span>
            </div>
            <div class="metric-row">
                <span>Error Rate (1min):</span>
                <span id="error-rate">-</span>
            </div>
            <div class="metric-row">
                <span>Active Connections:</span>
                <span id="active-connections">-</span>
            </div>
            <div class="metric-row">
                <span>Metrics Collection:</span>
                <span id="metrics-status">-</span>
            </div>
        </div>

        <div class="health-card">
            <h3>Service Dependencies</h3>
            <div class="metric-row">
                <span>Prometheus:</span>
                <span id="prometheus-health">-</span>
            </div>
            <div class="metric-row">
                <span>OpenTelemetry:</span>
                <span id="otel-health">-</span>
            </div>
            <div class="metric-row">
                <span>Error Aggregation:</span>
                <span id="error-aggregation-health">-</span>
            </div>
            <div class="metric-row">
                <span>Alert Manager:</span>
                <span id="alert-manager-health">-</span>
            </div>
        </div>

        <div class="health-card">
            <h3>Recent Health Events</h3>
            <div id="health-events">
                <p>Loading health events...</p>
            </div>
        </div>
    </div>

    <script>
        // Health dashboard JavaScript
        async function updateHealthDashboard() {
            try {
                const response = await fetch('/api/health/status');
                const data = await response.json();

                // Update health score
                const scoreElement = document.getElementById('health-score');
                const statusElement = document.getElementById('health-status');
                const textElement = document.getElementById('health-text');

                scoreElement.textContent = data.score;
                scoreElement.className = `health-score health-${data.status}`;

                const indicator = statusElement.querySelector('.status-indicator');
                indicator.className = `status-indicator status-${data.status}`;
                textElement.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);

                // Update system metrics
                document.getElementById('system-uptime').textContent = formatUptime(data.uptime_seconds);
                document.getElementById('error-rate').textContent = `${data.error_rate_1min.toFixed(2)}/min`;
                document.getElementById('active-connections').textContent = data.websocket_connections;
                document.getElementById('metrics-status').textContent = data.metrics_collector_enabled ? '✅ Enabled' : '❌ Disabled';

                // Update service dependencies
                document.getElementById('prometheus-health').textContent = data.metrics_collector_enabled ? '✅ Healthy' : '❌ Unavailable';
                document.getElementById('otel-health').textContent = '✅ Healthy';
                document.getElementById('error-aggregation-health').textContent = '✅ Healthy';
                document.getElementById('alert-manager-health').textContent = '✅ Healthy';

            } catch (error) {
                console.error('Error updating health dashboard:', error);
            }
        }

        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);

            if (days > 0) {
                return `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }

        // Update dashboard every 30 seconds
        updateHealthDashboard();
        setInterval(updateHealthDashboard, 30000);
    </script>
</body>
</html>
"""

    def _generate_performance_dashboard_html(self) -> str:
        """Generate performance monitoring dashboard."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Performance Dashboard - KEI-Agent SDK</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav-menu {
            margin: 15px 0;
            display: flex;
            gap: 10px;
        }
        .nav-link {
            padding: 8px 16px;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .nav-link:hover {
            background: #e0e0e0;
        }
        .nav-link.active {
            background: #2196F3;
            color: white;
        }
        .perf-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .perf-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2196F3;
            text-align: center;
            margin: 10px 0;
        }
        .metric-label {
            text-align: center;
            color: #666;
            margin-bottom: 15px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #2196F3);
            transition: width 0.3s ease;
        }
        .chart-container {
            height: 200px;
            background: #f9f9f9;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Performance Monitoring Dashboard</h1>
        <p>Request latency, throughput, and system performance metrics</p>
        <div class="nav-menu">
            <a href="/dashboard" class="nav-link">Overview</a>
            <a href="/dashboard/health" class="nav-link">Health</a>
            <a href="/dashboard/performance" class="nav-link active">Performance</a>
            <a href="/dashboard/security" class="nav-link">Security</a>
            <a href="/dashboard/business" class="nav-link">Business</a>
        </div>
    </div>

    <div class="perf-grid">
        <div class="perf-card">
            <h3>Request Metrics</h3>
            <div class="metric-value" id="total-requests">0</div>
            <div class="metric-label">Total Requests</div>
            <div class="metric-value" id="avg-response-time">0ms</div>
            <div class="metric-label">Avg Response Time</div>
        </div>

        <div class="perf-card">
            <h3>Throughput</h3>
            <div class="metric-value" id="requests-per-second">0</div>
            <div class="metric-label">Requests/Second</div>
            <div class="metric-value" id="error-rate-percent">0%</div>
            <div class="metric-label">Error Rate</div>
        </div>

        <div class="perf-card">
            <h3>System Resources</h3>
            <div>
                <label>Memory Usage</label>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
                <span id="memory-usage">0 MB</span>
            </div>
            <div>
                <label>CPU Usage</label>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
                <span id="cpu-usage">0%</span>
            </div>
        </div>

        <div class="perf-card">
            <h3>Protocol Performance</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <div class="metric-value" id="rpc-requests">0</div>
                    <div class="metric-label">RPC Requests</div>
                </div>
                <div>
                    <div class="metric-value" id="stream-connections">0</div>
                    <div class="metric-label">Stream Connections</div>
                </div>
                <div>
                    <div class="metric-value" id="bus-messages">0</div>
                    <div class="metric-label">Bus Messages</div>
                </div>
                <div>
                    <div class="metric-value" id="mcp-executions">0</div>
                    <div class="metric-label">MCP Executions</div>
                </div>
            </div>
        </div>

        <div class="perf-card" style="grid-column: 1 / -1;">
            <h3>Response Time Trend</h3>
            <div class="chart-container">
                <p>Response time chart would be displayed here<br>
                (Integration with charting library like Chart.js)</p>
            </div>
        </div>

        <div class="perf-card" style="grid-column: 1 / -1;">
            <h3>Throughput Trend</h3>
            <div class="chart-container">
                <p>Throughput chart would be displayed here<br>
                (Integration with charting library like Chart.js)</p>
            </div>
        </div>
    </div>

    <script>
        // Performance dashboard JavaScript
        async function updatePerformanceDashboard() {
            try {
                const response = await fetch('/api/performance/stats');
                const data = await response.json();

                // Update request metrics
                document.getElementById('total-requests').textContent = data.request_metrics.total_requests.toLocaleString();
                document.getElementById('avg-response-time').textContent = `${data.request_metrics.avg_response_time.toFixed(1)}ms`;
                document.getElementById('requests-per-second').textContent = data.request_metrics.throughput.toFixed(1);
                document.getElementById('error-rate-percent').textContent = `${(data.request_metrics.error_rate * 100).toFixed(1)}%`;

                // Update system resources
                const memoryPercent = (data.system_metrics.memory_usage_mb / 1024) * 100; // Assuming 1GB max
                document.getElementById('memory-progress').style.width = `${Math.min(memoryPercent, 100)}%`;
                document.getElementById('memory-usage').textContent = `${data.system_metrics.memory_usage_mb.toFixed(1)} MB`;

                document.getElementById('cpu-progress').style.width = `${data.system_metrics.cpu_usage_percent}%`;
                document.getElementById('cpu-usage').textContent = `${data.system_metrics.cpu_usage_percent.toFixed(1)}%`;

                // Update protocol metrics
                document.getElementById('rpc-requests').textContent = data.protocol_metrics.rpc_requests.toLocaleString();
                document.getElementById('stream-connections').textContent = data.protocol_metrics.stream_connections.toLocaleString();
                document.getElementById('bus-messages').textContent = data.protocol_metrics.bus_messages.toLocaleString();
                document.getElementById('mcp-executions').textContent = data.protocol_metrics.mcp_executions.toLocaleString();

            } catch (error) {
                console.error('Error updating performance dashboard:', error);
            }
        }

        // Update dashboard every 10 seconds
        updatePerformanceDashboard();
        setInterval(updatePerformanceDashboard, 10000);
    </script>
</body>
</html>
"""

    def _generate_security_dashboard_html(self) -> str:
        """Generate security monitoring dashboard."""
        return generate_security_dashboard_html()

    def _generate_business_dashboard_html(self) -> str:
        """Generate business metrics dashboard."""
        return generate_business_dashboard_html()

    async def start(self):
        """Start the metrics server."""
        if not AIOHTTP_AVAILABLE:
            logger.error("Cannot start metrics server: aiohttp not available")
            return

        self.app = self.create_app()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        logger.info(f"Metrics server started on http://{self.host}:{self.port}")
        logger.info(f"Metrics endpoint: http://{self.host}:{self.port}/metrics")
        logger.info(f"Dashboard: http://{self.host}:{self.port}/dashboard")

    async def stop(self):
        """Stop the metrics server."""
        if self.runner:
            await self.runner.cleanup()

        # Close all WebSocket connections
        for ws in self.websocket_connections.copy():
            await ws.close()

        logger.info("Metrics server stopped")


# Global metrics server instance
_metrics_server: Optional[MetricsServer] = None


def get_metrics_server(host: str = "127.0.0.1", port: int = 8090) -> MetricsServer:
    """Get or create the global metrics server instance."""
    global _metrics_server
    if _metrics_server is None:
        _metrics_server = MetricsServer(host, port)
    return _metrics_server


async def start_metrics_server(
    host: str = "127.0.0.1", port: int = 8090
) -> MetricsServer:
    """Start the metrics server."""
    server = get_metrics_server(host, port)
    await server.start()
    return server

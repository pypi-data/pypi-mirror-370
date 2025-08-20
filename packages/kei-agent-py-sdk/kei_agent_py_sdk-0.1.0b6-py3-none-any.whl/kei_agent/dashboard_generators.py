# kei_agent/dashboard_generators.py
"""
Dashboard HTML generators for KEI-Agent Python SDK.

This module provides specialized dashboard generators for:
- Security monitoring dashboard
- Business metrics dashboard
- Additional operational dashboards
"""


def generate_security_dashboard_html() -> str:
    """Generate security monitoring dashboard."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Security Dashboard - KEI-Agent SDK</title>
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
        .security-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .security-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .alert-high { border-left: 4px solid #F44336; }
        .alert-medium { border-left: 4px solid #FF9800; }
        .alert-low { border-left: 4px solid #4CAF50; }
        .security-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 10px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .security-value {
            font-weight: bold;
            font-size: 1.2em;
        }
        .security-critical { color: #F44336; }
        .security-warning { color: #FF9800; }
        .security-ok { color: #4CAF50; }
        .event-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .event-item {
            padding: 10px;
            margin: 5px 0;
            background: #f9f9f9;
            border-radius: 4px;
            border-left: 3px solid #ddd;
        }
        .event-critical { border-left-color: #F44336; }
        .event-high { border-left-color: #FF9800; }
        .event-medium { border-left-color: #2196F3; }
        .event-low { border-left-color: #4CAF50; }
        .timestamp {
            font-size: 0.8em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Security Monitoring Dashboard</h1>
        <p>Authentication failures, security events, and threat detection</p>
        <div class="nav-menu">
            <a href="/dashboard" class="nav-link">Overview</a>
            <a href="/dashboard/health" class="nav-link">Health</a>
            <a href="/dashboard/performance" class="nav-link">Performance</a>
            <a href="/dashboard/security" class="nav-link active">Security</a>
            <a href="/dashboard/business" class="nav-link">Business</a>
        </div>
    </div>

    <div class="security-grid">
        <div class="security-card alert-high">
            <h3>🚨 Security Alerts</h3>
            <div class="security-metric">
                <span>Critical Events (24h):</span>
                <span class="security-value security-critical" id="critical-events">0</span>
            </div>
            <div class="security-metric">
                <span>High Priority Events:</span>
                <span class="security-value security-warning" id="high-events">0</span>
            </div>
            <div class="security-metric">
                <span>Total Security Events:</span>
                <span class="security-value" id="total-security-events">0</span>
            </div>
        </div>

        <div class="security-card alert-medium">
            <h3>🔐 Authentication Metrics</h3>
            <div class="security-metric">
                <span>Failed Logins (1h):</span>
                <span class="security-value" id="auth-failures">0</span>
            </div>
            <div class="security-metric">
                <span>Successful Logins:</span>
                <span class="security-value security-ok" id="auth-successes">0</span>
            </div>
            <div class="security-metric">
                <span>Token Refreshes:</span>
                <span class="security-value" id="token-refreshes">0</span>
            </div>
            <div class="security-metric">
                <span>Auth Success Rate:</span>
                <span class="security-value" id="auth-success-rate">100%</span>
            </div>
        </div>

        <div class="security-card alert-low">
            <h3>🛡️ Security Posture</h3>
            <div class="security-metric">
                <span>TLS Connections:</span>
                <span class="security-value security-ok" id="tls-connections">✅ Enabled</span>
            </div>
            <div class="security-metric">
                <span>Token Validation:</span>
                <span class="security-value security-ok" id="token-validation">✅ Active</span>
            </div>
            <div class="security-metric">
                <span>Rate Limiting:</span>
                <span class="security-value security-ok" id="rate-limiting">✅ Active</span>
            </div>
            <div class="security-metric">
                <span>Input Validation:</span>
                <span class="security-value security-ok" id="input-validation">✅ Active</span>
            </div>
        </div>

        <div class="security-card">
            <h3>📊 Threat Intelligence</h3>
            <div class="security-metric">
                <span>Blocked IPs:</span>
                <span class="security-value" id="blocked-ips">0</span>
            </div>
            <div class="security-metric">
                <span>Suspicious Patterns:</span>
                <span class="security-value" id="suspicious-patterns">0</span>
            </div>
            <div class="security-metric">
                <span>Vulnerability Scans:</span>
                <span class="security-value security-ok" id="vuln-scans">✅ Up to date</span>
            </div>
        </div>

        <div class="security-card" style="grid-column: 1 / -1;">
            <h3>🔍 Recent Security Events</h3>
            <div class="event-list" id="security-events">
                <p>Loading security events...</p>
            </div>
        </div>
    </div>

    <script>
        // Security dashboard JavaScript
        async function updateSecurityDashboard() {
            try {
                const response = await fetch('/api/security/events');
                const data = await response.json();

                // Update security metrics
                document.getElementById('total-security-events').textContent = data.total_security_events;
                document.getElementById('auth-failures').textContent = data.auth_failures;

                // Calculate derived metrics
                const totalAuth = data.auth_failures + (data.auth_successes || 0);
                const successRate = totalAuth > 0 ? ((data.auth_successes || 0) / totalAuth * 100).toFixed(1) : 100;
                document.getElementById('auth-success-rate').textContent = `${successRate}%`;

                // Update recent events
                const eventsContainer = document.getElementById('security-events');
                if (data.recent_events && data.recent_events.length > 0) {
                    eventsContainer.innerHTML = data.recent_events.map(event => `
                        <div class="event-item event-${event.severity}">
                            <div><strong>${event.type}</strong> - ${event.message}</div>
                            <div class="timestamp">${new Date(event.timestamp * 1000).toLocaleString()}</div>
                            <div class="timestamp">Agent: ${event.agent_id}</div>
                        </div>
                    `).join('');
                } else {
                    eventsContainer.innerHTML = '<p>No recent security events</p>';
                }

            } catch (error) {
                console.error('Error updating security dashboard:', error);
            }
        }

        // Update dashboard every 30 seconds
        updateSecurityDashboard();
        setInterval(updateSecurityDashboard, 30000);
    </script>
</body>
</html>
"""


def generate_business_dashboard_html() -> str:
    """Generate business metrics dashboard."""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Business Dashboard - KEI-Agent SDK</title>
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
        .business-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .business-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .kpi-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #2196F3;
            text-align: center;
            margin: 15px 0;
        }
        .kpi-label {
            text-align: center;
            color: #666;
            margin-bottom: 10px;
        }
        .kpi-change {
            text-align: center;
            font-size: 0.9em;
        }
        .kpi-up { color: #4CAF50; }
        .kpi-down { color: #F44336; }
        .kpi-stable { color: #666; }
        .donut-chart {
            width: 150px;
            height: 150px;
            margin: 20px auto;
            position: relative;
        }
        .efficiency-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .efficiency-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #2196F3);
            transition: width 0.3s ease;
        }
        .metric-row {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #f9f9f9;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Business Metrics Dashboard</h1>
        <p>Agent lifecycle, protocol usage, and operational efficiency</p>
        <div class="nav-menu">
            <a href="/dashboard" class="nav-link">Overview</a>
            <a href="/dashboard/health" class="nav-link">Health</a>
            <a href="/dashboard/performance" class="nav-link">Performance</a>
            <a href="/dashboard/security" class="nav-link">Security</a>
            <a href="/dashboard/business" class="nav-link active">Business</a>
        </div>
    </div>

    <div class="business-grid">
        <div class="business-card">
            <h3>🤖 Agent Metrics</h3>
            <div class="kpi-value" id="total-agents">1</div>
            <div class="kpi-label">Total Agents</div>
            <div class="kpi-change kpi-stable" id="agents-change">No change</div>

            <div class="metric-row">
                <span>Active Agents:</span>
                <span id="active-agents">1</span>
            </div>
            <div class="metric-row">
                <span>Avg Uptime:</span>
                <span id="avg-uptime">-</span>
            </div>
        </div>

        <div class="business-card">
            <h3>⚡ Operation Success</h3>
            <div class="kpi-value" id="success-rate">99.5%</div>
            <div class="kpi-label">Success Rate</div>
            <div class="kpi-change kpi-up" id="success-change">+0.2%</div>

            <div class="metric-row">
                <span>Successful Operations:</span>
                <span id="successful-ops">0</span>
            </div>
            <div class="metric-row">
                <span>Failed Operations:</span>
                <span id="failed-ops">0</span>
            </div>
        </div>

        <div class="business-card">
            <h3>🚀 Protocol Usage</h3>
            <div class="donut-chart">
                <canvas id="protocol-chart" width="150" height="150"></canvas>
            </div>
            <div class="metric-row">
                <span>RPC:</span>
                <span id="rpc-usage">40%</span>
            </div>
            <div class="metric-row">
                <span>Stream:</span>
                <span id="stream-usage">30%</span>
            </div>
            <div class="metric-row">
                <span>Bus:</span>
                <span id="bus-usage">20%</span>
            </div>
            <div class="metric-row">
                <span>MCP:</span>
                <span id="mcp-usage">10%</span>
            </div>
        </div>

        <div class="business-card">
            <h3>📈 Resource Efficiency</h3>
            <div>
                <label>Memory Efficiency</label>
                <div class="efficiency-bar">
                    <div class="efficiency-fill" id="memory-efficiency" style="width: 85%"></div>
                </div>
                <span id="memory-efficiency-text">85%</span>
            </div>
            <div>
                <label>CPU Efficiency</label>
                <div class="efficiency-bar">
                    <div class="efficiency-fill" id="cpu-efficiency" style="width: 90%"></div>
                </div>
                <span id="cpu-efficiency-text">90%</span>
            </div>
            <div>
                <label>Network Efficiency</label>
                <div class="efficiency-bar">
                    <div class="efficiency-fill" id="network-efficiency" style="width: 95%"></div>
                </div>
                <span id="network-efficiency-text">95%</span>
            </div>
        </div>

        <div class="business-card" style="grid-column: 1 / -1;">
            <h3>📊 Key Performance Indicators</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <div class="kpi-value" id="avg-response-time-kpi">125ms</div>
                    <div class="kpi-label">Avg Response Time</div>
                </div>
                <div>
                    <div class="kpi-value" id="throughput-kpi">1,250</div>
                    <div class="kpi-label">Requests/Hour</div>
                </div>
                <div>
                    <div class="kpi-value" id="availability-kpi">99.9%</div>
                    <div class="kpi-label">Availability</div>
                </div>
                <div>
                    <div class="kpi-value" id="error-rate-kpi">0.1%</div>
                    <div class="kpi-label">Error Rate</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Business dashboard JavaScript
        async function updateBusinessDashboard() {
            try {
                const response = await fetch('/api/business/metrics');
                const data = await response.json();

                // Update agent metrics
                document.getElementById('total-agents').textContent = data.agent_metrics.total_agents;
                document.getElementById('active-agents').textContent = data.agent_metrics.active_agents;
                document.getElementById('avg-uptime').textContent = formatUptime(data.agent_metrics.agent_uptime_avg);

                // Update operation metrics
                const totalOps = data.operation_metrics.successful_operations + data.operation_metrics.failed_operations;
                const successRate = totalOps > 0 ? (data.operation_metrics.successful_operations / totalOps * 100).toFixed(1) : 100;
                document.getElementById('success-rate').textContent = `${successRate}%`;
                document.getElementById('successful-ops').textContent = data.operation_metrics.successful_operations.toLocaleString();
                document.getElementById('failed-ops').textContent = data.operation_metrics.failed_operations.toLocaleString();

                // Update protocol usage
                document.getElementById('rpc-usage').textContent = `${data.protocol_usage.rpc_usage_percent}%`;
                document.getElementById('stream-usage').textContent = `${data.protocol_usage.stream_usage_percent}%`;
                document.getElementById('bus-usage').textContent = `${data.protocol_usage.bus_usage_percent}%`;
                document.getElementById('mcp-usage').textContent = `${data.protocol_usage.mcp_usage_percent}%`;

                // Update efficiency metrics
                document.getElementById('memory-efficiency').style.width = `${data.resource_utilization.memory_efficiency}%`;
                document.getElementById('memory-efficiency-text').textContent = `${data.resource_utilization.memory_efficiency}%`;
                document.getElementById('cpu-efficiency').style.width = `${data.resource_utilization.cpu_efficiency}%`;
                document.getElementById('cpu-efficiency-text').textContent = `${data.resource_utilization.cpu_efficiency}%`;
                document.getElementById('network-efficiency').style.width = `${data.resource_utilization.network_efficiency}%`;
                document.getElementById('network-efficiency-text').textContent = `${data.resource_utilization.network_efficiency}%`;

                // Draw protocol usage donut chart
                drawProtocolChart(data.protocol_usage);

            } catch (error) {
                console.error('Error updating business dashboard:', error);
            }
        }

        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);

            if (days > 0) {
                return `${days}d ${hours}h`;
            } else if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }

        function drawProtocolChart(usage) {
            const canvas = document.getElementById('protocol-chart');
            const ctx = canvas.getContext('2d');
            const centerX = 75;
            const centerY = 75;
            const radius = 60;

            // Clear canvas
            ctx.clearRect(0, 0, 150, 150);

            // Data
            const data = [
                { label: 'RPC', value: usage.rpc_usage_percent, color: '#2196F3' },
                { label: 'Stream', value: usage.stream_usage_percent, color: '#4CAF50' },
                { label: 'Bus', value: usage.bus_usage_percent, color: '#FF9800' },
                { label: 'MCP', value: usage.mcp_usage_percent, color: '#9C27B0' }
            ];

            // Draw donut chart
            let currentAngle = -Math.PI / 2;

            data.forEach(item => {
                const sliceAngle = (item.value / 100) * 2 * Math.PI;

                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
                ctx.arc(centerX, centerY, radius * 0.6, currentAngle + sliceAngle, currentAngle, true);
                ctx.closePath();
                ctx.fillStyle = item.color;
                ctx.fill();

                currentAngle += sliceAngle;
            });
        }

        // Update dashboard every 60 seconds
        updateBusinessDashboard();
        setInterval(updateBusinessDashboard, 60000);
    </script>
</body>
</html>
"""

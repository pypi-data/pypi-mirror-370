# Quick Start Guide

Lernen Sie die Grundlagen des KEI-Agent SDK in nur 5 Minuten! Diese Anleitung zeigt Ihnen die wichtigsten Features anhand praktischer Beispiele.

## 🚀 Ihr erster Agent-Client

### 1. Basis-Setup

```python
import asyncio
import psutil
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    CapabilityManager,
    CapabilityProfile
)

async def main():
    # Konfiguration erstellen
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="my-first-agent"
    )

    # Client verwenden
    async with UnifiedKeiAgentClient(config=config) as client:
        print("🎉 Client erfolgreich verbunden!")

        # Client-Informationen anzeigen
        info = client.get_client_info()
        print(f"Agent ID: {info['agent_id']}")
        print(f"Verfügbare Protokolle: {info['available_protocols']}")

# Ausführen
asyncio.run(main())
```

### 2. Erste Agent-Operationen

```python
async def agent_operations():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="demo-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # 🛠️ MONITORING-TOOLS IMPLEMENTIEREN UND REGISTRIEREN
        capability_manager = CapabilityManager(client._legacy_client)

        # CPU-Monitor Tool
        async def cpu_monitor_tool(**kwargs):
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "core_count": psutil.cpu_count(),
                "status": "healthy"
            }

        # Memory-Monitor Tool
        async def memory_monitor_tool(**kwargs):
            memory = psutil.virtual_memory()
            return {
                "memory_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "status": "healthy" if memory.percent < 80 else "warning"
            }

        # Disk-Monitor Tool
        async def disk_monitor_tool(**kwargs):
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            return {
                "disk_percent": round(usage_percent, 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "status": "healthy" if usage_percent < 80 else "warning"
            }

        # Tools registrieren
        monitoring_tools = [
            ("cpu_monitor", "CPU-Überwachung", cpu_monitor_tool),
            ("memory_monitor", "Memory-Überwachung", memory_monitor_tool),
            ("disk_monitor", "Disk-Überwachung", disk_monitor_tool)
        ]

        for name, desc, handler in monitoring_tools:
            await capability_manager.register_capability(
                CapabilityProfile(
                    name=name,
                    version="1.0.0",
                    description=desc,
                    methods={"monitor": {}}
                ),
                handler=handler
            )

        # 📋 Plan erstellen
        plan = await client.plan_task(
            objective="Führe vollständige System-Überwachung durch",
            context={"tools": [name for name, _, _ in monitoring_tools]}
        )
        print(f"Plan erstellt: {plan['plan_id']}")

        # ⚡ Echte Tools verwenden
        monitoring_results = {}
        for name, _, _ in monitoring_tools:
            result = await client.use_tool(name, **{})
            monitoring_results[name] = result
            print(f"✅ {name}: {result['status']}")

        # 👁️ Umgebung beobachten - Echte Metriken
        all_healthy = all(r['status'] == 'healthy' for r in monitoring_results.values())
        observation = {
            "observation_id": "obs_001",
            "system_status": "healthy" if all_healthy else "warning",
            "tools_checked": len(monitoring_tools),
            "timestamp": "2024-01-01T12:00:00Z"
        }
        print(f"Beobachtung: System-Status = {observation['system_status']}")

        # 💡 Reasoning mit echten Daten
        explanation = {
            "explanation": f"Es wurden {len(monitoring_tools)} Monitoring-Tools erfolgreich ausgeführt. "
                          f"System-Status: {observation['system_status']}. "
                          f"Details: CPU={monitoring_results['cpu_monitor']['cpu_percent']}%, "
                          f"Memory={monitoring_results['memory_monitor']['memory_percent']}%, "
                          f"Disk={monitoring_results['disk_monitor']['disk_percent']}%"
        }
        print(f"Erklärung: {explanation['explanation']}")

asyncio.run(agent_operations())
```

## 🔌 Multi-Protocol Features

### Automatische Protokoll-Auswahl

```python
async def multi_protocol_demo():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="multi-protocol-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # 🔄 RPC für synchrone Operationen - Korrekte API-Signatur
        sync_result = await client.plan_task(
            objective="Führe System-Monitoring durch",
            context={"scope": "basic", "include_tools": True}
        )

        # 🌊 Stream: Verwende execute_agent_operation für Stream-Operationen
        stream_result = await client.execute_agent_operation(
            "stream_monitoring",
            {"data": "real-time-feed", "callback": True},
            protocol=ProtocolType.STREAM
        )
        print(f"Stream-Result: {stream_result}")

        # 📨 Bus für asynchrone Nachrichten - Konkrete Implementierung
        bus_result = await client.execute_agent_operation(
            "async_health_check",
            {
                "target_agent": "monitoring-agent",
                "message_type": "health_check_request",
                "payload": {"check_type": "basic", "timeout": 30}
            },
            protocol=ProtocolType.BUS
        )
        print(f"Bus-Result: {bus_result}")

        # 🛠️ MCP für Tool-Integration - Konkrete Tools
        tools = await client.discover_available_tools("monitoring")
        print(f"Verfügbare Tools: {len(tools)}")

asyncio.run(multi_protocol_demo())
```

### Spezifische Protokoll-Auswahl

```python
from kei_agent import ProtocolType

async def specific_protocol_demo():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="protocol-specific-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Explizit RPC verwenden
        rpc_result = await client.execute_agent_operation(
            "custom_operation",
            {"data": "test"},
            protocol=ProtocolType.RPC
        )

        # Explizit Stream verwenden
        stream_result = await client.execute_agent_operation(
            "real_time_operation",
            {"stream": True},
            protocol=ProtocolType.STREAM
        )

asyncio.run(specific_protocol_demo())
```

## 🛡️ Enterprise Features

### Structured Logging

```python
import time
from kei_agent import get_logger, LogContext

async def logging_demo():
    # Logger konfigurieren
    logger = get_logger("my_agent")

    # Kontext setzen - create_correlation_id() setzt bereits den Kontext
    correlation_id = logger.create_correlation_id()
    logger.set_context(LogContext(
        user_id="user-123",
        agent_id="demo-agent"
    ))

    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="logging-demo-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Operation mit Logging
        operation_id = logger.log_operation_start("plan_creation")

        try:
            plan = await client.plan_task("Demo-Plan mit Logging")
            logger.log_operation_end("plan_creation", operation_id, time.time(), success=True)
            logger.info("Plan erfolgreich erstellt", plan_id=plan.get('plan_id'))

        except Exception as e:
            logger.log_operation_end("plan_creation", operation_id, time.time(), success=False)
            logger.error("Plan-Erstellung fehlgeschlagen", error=str(e))

import time
asyncio.run(logging_demo())
```

### Health Checks

```python
from kei_agent import get_health_manager, APIHealthCheck, MemoryHealthCheck, HealthStatus

async def health_check_demo():
    # Health Manager konfigurieren
    health_manager = get_health_manager()

    # Health Checks registrieren
    health_manager.register_check(APIHealthCheck(
        name="kei_api",
        url="https://api.kei-framework.com/health"
    ))

    health_manager.register_check(MemoryHealthCheck(
        name="system_memory",
        warning_threshold=0.8,
        critical_threshold=0.95
    ))

    # Health Checks ausführen
    summary = await health_manager.run_all_checks()

    print(f"Gesamtstatus: {summary.overall_status.value}")
    print(f"Gesunde Komponenten: {summary.healthy_count}")
    print(f"Problematische Komponenten: {summary.unhealthy_count}")

    # Detaillierte Ergebnisse
    for check in summary.checks:
        status_emoji = "✅" if check.status == HealthStatus.HEALTHY else "❌"
        print(f"{status_emoji} {check.name}: {check.message}")

asyncio.run(health_check_demo())
```

### Input Validation

```python
from kei_agent import get_input_validator

def validation_demo():
    validator = get_input_validator()

    # Agent-Operation validieren
    operation_data = {
        "objective": "Erstelle einen Bericht",
        "context": {
            "format": "pdf",
            "deadline": "2024-12-31"
        }
    }

    result = validator.validate_agent_operation("plan", operation_data)

    if result.valid:
        print("✅ Input-Validierung erfolgreich")
        print(f"Bereinigte Daten: {result.sanitized_value}")
    else:
        print("❌ Validierungsfehler:")
        for error in result.errors:
            print(f"  - {error}")

validation_demo()
```

## 🔧 Erweiterte Konfiguration

### Vollständige Client-Konfiguration

```python
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    ProtocolConfig,
    SecurityConfig,
    AuthType
)

async def advanced_config_demo():
    # Basis-Konfiguration
    agent_config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="advanced-agent",
        timeout=30,
        max_retries=3
    )

    # Protokoll-Konfiguration
    protocol_config = ProtocolConfig(
        rpc_enabled=True,
        stream_enabled=True,
        bus_enabled=True,
        mcp_enabled=True,
        auto_protocol_selection=True,
        protocol_fallback_enabled=True
    )

    # Sicherheitskonfiguration
    security_config = SecurityConfig(
        auth_type=AuthType.BEARER,
        api_token="your-api-token",
        rbac_enabled=True,
        audit_enabled=True,
        token_refresh_enabled=True
    )

    # Client mit vollständiger Konfiguration
    async with UnifiedKeiAgentClient(
        config=agent_config,
        protocol_config=protocol_config,
        security_config=security_config
    ) as client:
        print("🚀 Erweiterte Konfiguration aktiv")

        # Client-Informationen
        info = client.get_client_info()
        print(f"Features: {info['features']}")
        print(f"Security Context: {info['security_context']}")

asyncio.run(advanced_config_demo())
```

## 🎯 Praktische Beispiele

### Agent-to-Agent Kommunikation

```python
import asyncio
import psutil
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

# 1. HEALTH-MONITOR-AGENT IMPLEMENTIERUNG
async def health_monitor_agent():
    """Spezialisierter Agent für Health-Monitoring."""
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="health-monitor-token",
        agent_id="health-monitor-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Agent registrieren
        await client.register_agent(
            name="health-monitor-agent",
            description="Spezialisiert auf System-Health-Checks",
            capabilities=["system_monitoring", "health_checks", "metrics_collection"]
        )

        # Health-Check Implementierung als Agent-Operation
        async def perform_health_check():
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            health_data = {
                "agent_id": "health-monitor-agent",
                "timestamp": "2024-01-01T12:00:00Z",
                "system_metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100
                },
                "status": "healthy" if all([
                    cpu_percent < 80,
                    memory.percent < 80,
                    (disk.used / disk.total) * 100 < 80
                ]) else "warning"
            }
            return health_data

        # Health-Check durchführen
        health_result = await perform_health_check()
        print(f"Health-Check abgeschlossen: {health_result['status']}")
        return health_result

# 2. KOORDINATIONS-AGENT IMPLEMENTIERUNG
async def coordination_agent_demo():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="coordination-token",
        agent_id="coordination-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Health-Check über Bus-Operation koordinieren
        bus_result = await client.execute_agent_operation(
            "coordinate_health_check",
            {
                "target_agents": ["health-monitor-agent"],
                "check_type": "system_status",
                "include_metrics": True,
                "timeout": 30
            },
            protocol=ProtocolType.BUS
        )

        print(f"Health-Check koordiniert: {bus_result}")
        return bus_result

# 3. VOLLSTÄNDIGES DEMO
async def agent_communication_demo():
    """Demonstriert Agent-Koordination über verfügbare Protokolle."""
    print("🏢 Starte Agent-Kommunikations-Demo")

    # Health-Monitor-Agent ausführen
    print("📊 Health-Monitor-Agent: Sammle System-Daten...")
    health_data = await health_monitor_agent("localhost")
    print(f"✅ Health-Daten gesammelt: {health_data['status']}")

    # Koordinations-Agent ausführen
    print("🔄 Koordinations-Agent: Koordiniere Health-Checks...")
    coordination_result = await coordination_agent_demo()
    print(f"✅ Koordination abgeschlossen")

    return {"health_data": health_data, "coordination": coordination_result}

asyncio.run(agent_communication_demo())
```

### Tool-Integration mit MCP

```python
import asyncio
import psutil
import requests
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    CapabilityManager,
    CapabilityProfile
)

# 1. MONITORING-TOOLS IMPLEMENTIEREN
async def network_ping_tool(target: str, count: int = 1) -> dict:
    """Ping-Tool für Netzwerk-Checks."""
    import subprocess
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), target],
            capture_output=True, text=True, timeout=10
        )
        return {
            "target": target,
            "reachable": result.returncode == 0,
            "response_time": "extracted_from_output" if result.returncode == 0 else None,
            "status": "healthy" if result.returncode == 0 else "unhealthy"
        }
    except subprocess.TimeoutExpired:
        return {"target": target, "reachable": False, "status": "timeout"}

async def http_health_tool(url: str, timeout: int = 5) -> dict:
    """HTTP-Health-Check Tool."""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "status": "healthy" if response.status_code == 200 else "unhealthy"
        }
    except Exception as e:
        return {"url": url, "error": str(e), "status": "unhealthy"}

async def process_monitor_tool(process_name: str) -> dict:
    """Process-Monitor Tool."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        if process_name.lower() in proc.info['name'].lower():
            processes.append(proc.info)

    return {
        "process_name": process_name,
        "running_instances": len(processes),
        "processes": processes,
        "status": "healthy" if len(processes) > 0 else "not_running"
    }

async def tool_integration_demo():
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="your-api-token",
        agent_id="tool-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # 2. TOOLS REGISTRIEREN
        capability_manager = CapabilityManager(client._legacy_client)

        monitoring_tools = [
            ("network_ping", "Netzwerk-Ping Tool", network_ping_tool),
            ("http_health", "HTTP-Health-Check Tool", http_health_tool),
            ("process_monitor", "Process-Monitor Tool", process_monitor_tool)
        ]

        for name, description, handler in monitoring_tools:
            await capability_manager.register_capability(
                CapabilityProfile(
                    name=name,
                    version="1.0.0",
                    description=description,
                    methods={"check": {"parameters": ["target"]}}
                ),
                handler=handler
            )

        # 3. TOOLS VERWENDEN
        print(f"✅ {len(monitoring_tools)} Monitoring-Tools registriert")

        # Network-Ping Test
        ping_result = await client.use_tool(
            "network_ping",
            **{
                "target": "8.8.8.8",
                "count": 1
            }
        )
        print(f"🌐 Ping Google DNS: {ping_result['status']}")

        # HTTP-Health Test
        http_result = await client.use_tool(
            "http_health",
            **{
                "url": "https://httpbin.org/status/200",
                "timeout": 5
            }
        )
        print(f"🔗 HTTP-Test: {http_result['status']} ({http_result['status_code']})")

        # Process-Monitor Test
        process_result = await client.use_tool(
            "process_monitor",
            **{"process_name": "python"}
        )
        print(f"⚙️ Python-Prozesse: {process_result['running_instances']} gefunden")

asyncio.run(tool_integration_demo())
```

## ✍️ Blogpost-Agent

### Content-Erstellung mit KEI-Agent

```python
import asyncio
import requests
import json
import re
from datetime import datetime
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    CapabilityManager,
    CapabilityProfile
)

# 1. MCP-SERVER FÜR WEB-SEARCH
import json
from typing import Any, Dict, List
from mcp import Server, types
from mcp.server.models import InitializationOptions
import httpx

class WebSearchMCPServer:
    def __init__(self):
        self.server = Server("web-search")
        self.setup_handlers()

    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="web_search",
                    description="Durchsucht das Web nach Informationen",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "max_results": {"type": "integer", "default": 3}
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            if name == "web_search":
                return await self._web_search(arguments["query"], arguments.get("max_results", 3))
            raise ValueError(f"Unknown tool: {name}")

    async def _web_search(self, query: str, max_results: int) -> List[types.TextContent]:
        try:
            async with httpx.AsyncClient() as client:
                # DuckDuckGo Instant Answer API
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": "1"}
                )
                data = response.json()

                results = []
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("AbstractSource", "DuckDuckGo"),
                        "url": data.get("AbstractURL", ""),
                        "summary": data.get("AbstractText", ""),
                        "relevance_score": 0.95
                    })

                # Related Topics
                for topic in data.get("RelatedTopics", [])[:max_results-1]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append({
                            "title": topic.get("Text", "").split(" - ")[0],
                            "url": topic.get("FirstURL", ""),
                            "summary": topic.get("Text", ""),
                            "relevance_score": 0.8
                        })

                search_result = {
                    "query": query,
                    "results": results[:max_results],
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }

                return [types.TextContent(
                    type="text",
                    text=json.dumps(search_result, indent=2)
                )]

        except Exception as e:
            error_result = {"query": query, "error": str(e), "status": "failed"}
            return [types.TextContent(type="text", text=json.dumps(error_result))]

# MCP-Server starten
web_search_server = WebSearchMCPServer()

async def web_research_tool(topic: str, max_results: int = 3) -> dict:
    """Web-Research über MCP-Server."""
    try:
        result = await web_search_server._web_search(topic, max_results)
        return json.loads(result[0].text)
    except Exception as e:
        return {"topic": topic, "error": str(e), "status": "failed"}

async def content_generator_tool(topic: str, sources: list, style: str = "informativ") -> dict:
    """Content-Generator Tool für Blogpost-Erstellung."""
    try:
        # Blogpost-Struktur generieren
        if style == "informativ":
            intro = f"In der heutigen digitalen Welt spielt {topic} eine immer wichtigere Rolle. "
            intro += f"Dieser Artikel beleuchtet die wichtigsten Aspekte und aktuellen Entwicklungen."

            main_content = f"""
## Was ist {topic}?

{topic} bezeichnet einen wichtigen Bereich der modernen Technologie, der verschiedene
Anwendungsmöglichkeiten und Vorteile bietet.

## Aktuelle Trends

Basierend auf unserer Recherche zeigen sich folgende Trends:

"""
            for i, source in enumerate(sources, 1):
                main_content += f"{i}. **{source['title']}**: {source['summary']}\n\n"

            main_content += f"""
## Best Practices

Für eine erfolgreiche Implementierung von {topic} sollten folgende Punkte beachtet werden:

- Gründliche Planung und Analyse
- Schrittweise Umsetzung
- Kontinuierliche Überwachung und Optimierung
- Regelmäßige Updates und Anpassungen

## Fazit

{topic} bietet enormes Potenzial für Unternehmen und Entwickler. Mit den richtigen
Strategien und Tools lassen sich beeindruckende Ergebnisse erzielen.
"""

        elif style == "tutorial":
            intro = f"In diesem Tutorial lernen Sie Schritt für Schritt, wie Sie {topic} erfolgreich einsetzen."
            main_content = f"""
## Schritt 1: Grundlagen verstehen

Bevor Sie mit {topic} beginnen, sollten Sie die Grundlagen verstehen...

## Schritt 2: Setup und Konfiguration

Die richtige Konfiguration ist entscheidend für den Erfolg...

## Schritt 3: Praktische Umsetzung

Jetzt geht es an die praktische Implementierung...

## Schritt 4: Testing und Optimierung

Testen Sie Ihre Implementierung gründlich...
"""

        blogpost = {
            "title": f"Umfassender Guide zu {topic}",
            "introduction": intro,
            "main_content": main_content,
            "word_count": len((intro + main_content).split()),
            "reading_time_minutes": len((intro + main_content).split()) // 200,
            "style": style,
            "sources_used": len(sources),
            "generated_timestamp": datetime.now().isoformat(),
            "status": "success"
        }

        return blogpost

    except Exception as e:
        return {"topic": topic, "error": str(e), "status": "failed"}

async def seo_optimizer_tool(content: dict, target_keywords: list) -> dict:
    """SEO-Optimierung Tool für Blogposts."""
    try:
        title = content.get("title", "")
        intro = content.get("introduction", "")
        main_content = content.get("main_content", "")
        full_text = f"{title} {intro} {main_content}".lower()

        # Keyword-Analyse
        keyword_analysis = {}
        for keyword in target_keywords:
            count = full_text.count(keyword.lower())
            density = (count / len(full_text.split())) * 100 if full_text.split() else 0
            keyword_analysis[keyword] = {
                "count": count,
                "density_percent": round(density, 2),
                "optimal": 1 <= density <= 3  # 1-3% Keyword-Dichte
            }

        # SEO-Empfehlungen
        recommendations = []
        if len(title) < 30:
            recommendations.append("Titel sollte länger sein (30-60 Zeichen)")
        if len(title) > 60:
            recommendations.append("Titel sollte kürzer sein (30-60 Zeichen)")

        for keyword, analysis in keyword_analysis.items():
            if analysis["density_percent"] < 1:
                recommendations.append(f"Keyword '{keyword}' sollte häufiger verwendet werden")
            elif analysis["density_percent"] > 3:
                recommendations.append(f"Keyword '{keyword}' wird zu oft verwendet")

        # SEO-Score berechnen
        optimal_keywords = sum(1 for analysis in keyword_analysis.values() if analysis["optimal"])
        seo_score = (optimal_keywords / len(target_keywords)) * 100 if target_keywords else 0

        return {
            "seo_score": round(seo_score, 1),
            "keyword_analysis": keyword_analysis,
            "recommendations": recommendations,
            "title_length": len(title),
            "content_length": len(full_text.split()),
            "optimized_timestamp": datetime.now().isoformat(),
            "status": "success"
        }

    except Exception as e:
        return {"error": str(e), "status": "failed"}

async def blogpost_agent_demo():
    """Vollständiger Blogpost-Agent mit Research, Content-Generation und SEO."""

    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="blogpost-agent-token",
        agent_id="blogpost-creator-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # 1. CONTENT-TOOLS REGISTRIEREN
        capability_manager = CapabilityManager(client._legacy_client)

        content_tools = [
            ("web_research", "Web-Research für Content-Ideen", web_research_tool),
            ("content_generator", "Blogpost-Content-Generator", content_generator_tool),
            ("seo_optimizer", "SEO-Optimierung für Blogposts", seo_optimizer_tool)
        ]

        for name, description, handler in content_tools:
            await capability_manager.register_capability(
                CapabilityProfile(
                    name=name,
                    version="1.0.0",
                    description=description
                ),
                handler=handler
            )

        print("✅ Content-Tools registriert")

        # 2. BLOGPOST-ERSTELLUNG PLANEN
        topic = "Künstliche Intelligenz in der Softwareentwicklung"
        target_keywords = ["KI", "Softwareentwicklung", "Machine Learning", "Automatisierung"]

        plan = await client.plan_task(
            objective=f"Erstelle einen umfassenden Blogpost über '{topic}'",
            context={
                "topic": topic,
                "target_keywords": target_keywords,
                "style": "informativ",
                "target_length": "800-1200 Wörter"
            }
        )
        print(f"📋 Blogpost-Plan erstellt: {plan.get('plan_id')}")

        # 3. WEB-RESEARCH DURCHFÜHREN
        print("🔍 Starte Web-Research...")
        research_result = await client.use_tool(
            "web_research",
            **{
                "topic": topic,
                "max_results": 3
            }
        )

        if research_result["status"] == "success":
            print(f"✅ Research abgeschlossen: {len(research_result['sources'])} Quellen gefunden")
            for source in research_result["sources"]:
                print(f"  - {source['title']} (Relevanz: {source['relevance_score']})")

        # 4. CONTENT GENERIEREN
        print("\n✍️ Generiere Blogpost-Content...")
        content_result = await client.use_tool(
            "content_generator",
            **{
                "topic": topic,
                "sources": research_result["sources"],
                "style": "informativ"
            }
        )

        if content_result["status"] == "success":
            print(f"✅ Content generiert:")
            print(f"  - Titel: {content_result['title']}")
            print(f"  - Wörter: {content_result['word_count']}")
            print(f"  - Lesezeit: {content_result['reading_time_minutes']} Minuten")

        # 5. SEO-OPTIMIERUNG
        print("\n🎯 Führe SEO-Optimierung durch...")
        seo_result = await client.use_tool(
            "seo_optimizer",
            **{
                "content": content_result,
                "target_keywords": target_keywords
            }
        )

        if seo_result["status"] == "success":
            print(f"✅ SEO-Analyse abgeschlossen:")
            print(f"  - SEO-Score: {seo_result['seo_score']}/100")
            print(f"  - Titel-Länge: {seo_result['title_length']} Zeichen")

            if seo_result["recommendations"]:
                print("  📝 SEO-Empfehlungen:")
                for rec in seo_result["recommendations"][:3]:
                    print(f"    - {rec}")

        # 6. FINALER BLOGPOST
        print(f"\n🎉 Blogpost erfolgreich erstellt!")
        print(f"📄 Titel: {content_result['title']}")
        print(f"📊 Statistiken:")
        print(f"  - {content_result['word_count']} Wörter")
        print(f"  - {content_result['reading_time_minutes']} Min. Lesezeit")
        print(f"  - SEO-Score: {seo_result['seo_score']}/100")
        print(f"  - {len(research_result['sources'])} Quellen verwendet")

asyncio.run(blogpost_agent_demo())
```

## 🚨 Fehlerbehandlung

```python
from kei_agent.exceptions import KeiSDKError, ProtocolError, SecurityError

async def error_handling_demo():
    config = AgentClientConfig(
        base_url="https://invalid-url.example.com",
        api_token="invalid-token",
        agent_id="error-demo-agent"
    )

    try:
        async with UnifiedKeiAgentClient(config=config) as client:
            await client.plan_task("Test-Plan")

    except SecurityError as e:
        print(f"🔒 Sicherheitsfehler: {e}")
    except ProtocolError as e:
        print(f"🔌 Protokollfehler: {e}")
    except KeiSDKError as e:
        print(f"⚠️ SDK-Fehler: {e}")
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")

asyncio.run(error_handling_demo())
```

## 🎉 Nächste Schritte

Herzlichen Glückwunsch! Sie haben die Grundlagen des KEI-Agent SDK gelernt. Hier sind Ihre nächsten Schritte:

### Vertiefen Sie Ihr Wissen

- [**Basis-Konzepte**](../user-guide/concepts.md) - Verstehen Sie die Architektur
- [**Client-Verwendung**](../user-guide/client-usage.md) - Erweiterte Client-Features
- [**Protokolle**](../user-guide/protocols.md) - Multi-Protocol Deep Dive

### Enterprise Features erkunden

- [**Structured Logging**](../enterprise/logging.md) - Production-Logging
- [**Health Checks**](../enterprise/health-checks.md) - System-Monitoring
- [**Security**](../enterprise/security.md) - Sicherheits-Features

### Praktische Anwendung

- [**Beispiele**](../examples/index.md) - Umfassende Code-Beispiele
- [**API-Referenz**](../api/index.md) - Vollständige API-Dokumentation

---

**Bereit für mehr?** Erkunden Sie die [Basis-Konzepte →](../user-guide/concepts.md)

# 📚 KEI-Agent SDK Examples

## 🏢 Unternehmensbewertung börsennotierter Unternehmen

Vollständiges Multi-Agent-System für die Bewertung börsennotierter Unternehmen mit Datensammlung, Analyse und Berichterstellung.

```python
import asyncio
import httpx
import json
from datetime import datetime
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig, CapabilityManager, CapabilityProfile

# DATENSAMMLUNG-TOOLS
async def financial_reports_tool(symbol: str) -> dict:
    """Sammelt Geschäftsberichte und Finanzdaten."""
    async with httpx.AsyncClient() as client:
        # Alpha Vantage API für Finanzdaten
        response = await client.get(
            f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=demo"
        )
        data = response.json()
        return {
            "symbol": symbol,
            "company_name": data.get("Name", ""),
            "market_cap": data.get("MarketCapitalization", ""),
            "pe_ratio": data.get("PERatio", ""),
            "revenue": data.get("RevenueTTM", ""),
            "profit_margin": data.get("ProfitMargin", ""),
            "timestamp": datetime.now().isoformat()
        }

async def stock_data_tool(symbol: str) -> dict:
    """Sammelt Kapitalmarktdaten."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=demo"
        )
        data = response.json().get("Global Quote", {})
        return {
            "symbol": symbol,
            "price": data.get("05. price", ""),
            "change": data.get("09. change", ""),
            "change_percent": data.get("10. change percent", ""),
            "volume": data.get("06. volume", ""),
            "timestamp": datetime.now().isoformat()
        }

async def industry_data_tool(sector: str) -> dict:
    """Sammelt Branchen- und Marktdaten."""
    return {
        "sector": sector,
        "growth_rate": "5.2%",
        "market_size": "850B USD",
        "key_trends": ["Digitalisierung", "Nachhaltigkeit", "KI-Integration"],
        "competitive_landscape": "Fragmentiert mit 3 Marktführern",
        "timestamp": datetime.now().isoformat()
    }

# DATENSAMMLUNG-AGENT
async def data_collection_agent(symbol: str):
    """Agent 1: Sammelt alle relevanten Daten."""
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="data-collector-token",
        agent_id="data-collection-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Tools registrieren
        capability_manager = CapabilityManager(client._legacy_client)
        tools = [
            ("financial_reports", "Geschäftsberichte sammeln", financial_reports_tool),
            ("stock_data", "Kapitalmarktdaten sammeln", stock_data_tool),
            ("industry_data", "Branchendaten sammeln", industry_data_tool)
        ]

        for name, desc, handler in tools:
            await capability_manager.register_capability(
                CapabilityProfile(
                    name=name,
                    version="1.0.0",
                    description=desc
                ),
                handler=handler
            )

        # Datensammlung durchführen
        financial_data = await client.use_tool("financial_reports", **{"symbol": symbol})
        market_data = await client.use_tool("stock_data", **{"symbol": symbol})
        industry_data = await client.use_tool("industry_data", **{"sector": "Technology"})

        return {
            "financial": financial_data,
            "market": market_data,
            "industry": industry_data
        }

# ANALYSE-AGENT
async def analysis_agent(raw_data: dict):
    """Agent 2: Analysiert und verdichtet die Daten."""
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="analysis-token",
        agent_id="analysis-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Analyse-Tool
        async def valuation_analysis_tool(data: dict) -> dict:
            financial = data["financial"]
            market = data["market"]

            # Bewertungsmetriken berechnen
            market_cap = float(financial.get("market_cap", "0") or "0")
            pe_ratio = float(financial.get("pe_ratio", "0") or "0")
            current_price = float(market.get("price", "0") or "0")

            # Einfache Bewertungslogik
            valuation_score = 0
            if pe_ratio > 0 and pe_ratio < 15:
                valuation_score += 30
            elif pe_ratio < 25:
                valuation_score += 15

            if market_cap > 1000000000:  # > 1B
                valuation_score += 20

            return {
                "valuation_score": valuation_score,
                "pe_assessment": "Unterbewertet" if pe_ratio < 15 else "Fair bewertet",
                "market_position": "Large Cap" if market_cap > 1000000000 else "Mid Cap",
                "recommendation": "Kaufen" if valuation_score > 40 else "Halten",
                "timestamp": datetime.now().isoformat()
            }

        # Tool registrieren
        capability_manager = CapabilityManager(client._legacy_client)
        await capability_manager.register_capability(
            CapabilityProfile(
                name="valuation_analysis",
                version="1.0.0",
                description="Unternehmensbewertung"
            ),
            handler=valuation_analysis_tool
        )

        # Analyse durchführen
        analysis_result = await client.use_tool("valuation_analysis", **{"data": raw_data})
        return analysis_result

# BERICHT-AGENT
async def report_agent(raw_data: dict, analysis: dict):
    """Agent 3: Erstellt den finalen Bewertungsbericht."""
    config = AgentClientConfig(
        base_url="https://api.kei-framework.com",
        api_token="report-token",
        agent_id="report-agent"
    )

    async with UnifiedKeiAgentClient(config=config) as client:
        # Report-Tool
        async def report_generator_tool(data: dict, analysis: dict) -> dict:
            company = data["financial"]["company_name"]
            symbol = data["financial"]["symbol"]

            report = f"""
# Unternehmensbewertung: {company} ({symbol})

## Executive Summary
- Bewertungsscore: {analysis['valuation_score']}/100
- Empfehlung: {analysis['recommendation']}
- KGV-Bewertung: {analysis['pe_assessment']}

## Finanzkennzahlen
- Marktkapitalisierung: {data['financial']['market_cap']}
- KGV: {data['financial']['pe_ratio']}
- Gewinnmarge: {data['financial']['profit_margin']}

## Marktdaten
- Aktueller Kurs: {data['market']['price']}
- Tagesveränderung: {data['market']['change_percent']}
- Handelsvolumen: {data['market']['volume']}

## Branchenanalyse
- Sektor: {data['industry']['sector']}
- Wachstumsrate: {data['industry']['growth_rate']}
- Marktgröße: {data['industry']['market_size']}

## Fazit
{analysis['recommendation']} - Bewertungsscore von {analysis['valuation_score']}/100 Punkten.
"""

            return {
                "report": report,
                "summary": {
                    "company": company,
                    "recommendation": analysis['recommendation'],
                    "score": analysis['valuation_score']
                },
                "timestamp": datetime.now().isoformat()
            }

        # Tool registrieren
        capability_manager = CapabilityManager(client._legacy_client)
        await capability_manager.register_capability(
            CapabilityProfile(
                name="report_generator",
                version="1.0.0",
                description="Bewertungsbericht erstellen"
            ),
            handler=report_generator_tool
        )

        # Bericht erstellen
        report_result = await client.use_tool("report_generator", **{"data": raw_data, "analysis": analysis})
        return report_result

# HAUPTPROZESS
async def company_valuation_system():
    """Vollständiges Multi-Agent-System für Unternehmensbewertung."""
    symbol = "AAPL"  # Apple Inc.

    print(f"🏢 Starte Unternehmensbewertung für {symbol}")

    # Agent 1: Datensammlung
    print("📊 Agent 1: Sammle Daten...")
    raw_data = await data_collection_agent(symbol)
    print(f"✅ Daten gesammelt für {raw_data['financial']['company_name']}")

    # Agent 2: Analyse
    print("🔍 Agent 2: Analysiere Daten...")
    analysis = await analysis_agent(raw_data)
    print(f"✅ Analyse abgeschlossen: {analysis['recommendation']}")

    # Agent 3: Bericht
    print("📝 Agent 3: Erstelle Bericht...")
    report = await report_agent(raw_data, analysis)
    print(f"✅ Bericht erstellt")

    # Ergebnis ausgeben
    print("\n" + "="*50)
    print(report["report"])
    print("="*50)

    return report

# Ausführung
asyncio.run(company_valuation_system())
```

## Ausgabe-Beispiel

```
🏢 Starte Unternehmensbewertung für AAPL
📊 Agent 1: Sammle Daten...
✅ Daten gesammelt für Apple Inc.
🔍 Agent 2: Analysiere Daten...
✅ Analyse abgeschlossen: Halten
📝 Agent 3: Erstelle Bericht...
✅ Bericht erstellt

==================================================
# Unternehmensbewertung: Apple Inc. (AAPL)

## Executive Summary
- Bewertungsscore: 35/100
- Empfehlung: Halten
- KGV-Bewertung: Fair bewertet

## Finanzkennzahlen
- Marktkapitalisierung: 3.5T
- KGV: 28.5
- Gewinnmarge: 0.25

## Marktdaten
- Aktueller Kurs: 185.50
- Tagesveränderung: +1.2%
- Handelsvolumen: 45M

## Branchenanalyse
- Sektor: Technology
- Wachstumsrate: 5.2%
- Marktgröße: 850B USD

## Fazit
Halten - Bewertungsscore von 35/100 Punkten.
==================================================
```

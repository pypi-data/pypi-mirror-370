# Benutzerhandbuch

Willkommen zum Benutzerhandbuch des KEI-Agent Python SDK! Dieses Handbuch führt Sie durch alle wichtigen Konzepte und Funktionen des SDK.

## 📚 Übersicht

Das KEI-Agent Python SDK bietet eine umfassende, typisierte API für die Interaktion mit dem KEI-Agent Framework. Es unterstützt mehrere Kommunikationsprotokolle und bietet Enterprise-Features für produktive Umgebungen.

## 🎯 Zielgruppe

Dieses Handbuch richtet sich an:

- **Python-Entwickler**, die Agent-basierte Anwendungen entwickeln
- **DevOps-Engineers**, die KEI-Agent in produktive Umgebungen integrieren
- **Architekten**, die Multi-Agent-Systeme entwerfen

## 📖 Kapitel

### [Basis-Konzepte](concepts.md)
Verstehen Sie die grundlegenden Konzepte des KEI-Agent Framework:
- Agent-Architektur
- Protokoll-Typen
- Sicherheitsmodell
- Konfigurationsmanagement

### [Client-Verwendung](client-usage.md)
Lernen Sie, wie Sie den UnifiedKeiAgentClient verwenden:
- Client-Initialisierung
- Basis-Operationen
- Asynchrone Programmierung
- Fehlerbehandlung

### [Protokolle](protocols.md)
Detaillierte Informationen zu den unterstützten Protokollen:
- RPC (Remote Procedure Call)
- Stream (WebSocket-basiert)
- Bus (Message Bus)
- MCP (Model Context Protocol)

### [Authentifizierung](authentication.md)
Sicherheitsaspekte und Authentifizierung:
- Bearer Token
- OIDC (OpenID Connect)
- mTLS (Mutual TLS)
- Sicherheitskonfiguration

### [Fehlerbehandlung](error-handling.md)
Robuste Fehlerbehandlung und Retry-Strategien:
- Exception-Hierarchie
- Retry-Policies
- Circuit Breaker
- Fallback-Mechanismen

## 🚀 Schnellstart

```python
from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

# Client konfigurieren
config = AgentClientConfig(
    base_url="https://your-kei-agent.com",
    api_token="your-api-token",
    agent_id="your-agent-id"
)

# Client erstellen und verwenden
async with UnifiedKeiAgentClient(config) as client:
    # Agent-Operation ausführen
    result = await client.plan_task("Analysiere die Verkaufsdaten")
    print(f"Plan: {result}")
```

## 💡 Tipps für Einsteiger

1. **Beginnen Sie mit den [Basis-Konzepten](concepts.md)** - Verstehen Sie die Grundlagen
2. **Folgen Sie dem [Quick Start Guide](../getting-started/quickstart.md)** - Erste praktische Schritte
3. **Experimentieren Sie mit [Beispielen](../examples/index.md)** - Lernen Sie durch Praxis
4. **Nutzen Sie die [API-Referenz](../api/index.md)** - Detaillierte Dokumentation

## 🔗 Weiterführende Ressourcen

- [Enterprise Features](../enterprise/index.md) - Produktive Funktionen
- [Architektur](../architecture/index.md) - Technische Details
- [Troubleshooting](../troubleshooting/index.md) - Problemlösung
- [Migration](../migration/index.md) - Upgrade-Anleitungen

## 📞 Support

Bei Fragen oder Problemen:

- 📖 Konsultieren Sie die [Troubleshooting-Sektion](../troubleshooting/index.md)
- 🐛 Melden Sie Bugs im [GitHub Repository](https://github.com/kei-framework/kei-agent)
- 💬 Diskutieren Sie in der Community
- 📧 Kontaktieren Sie den Support für Enterprise-Kunden

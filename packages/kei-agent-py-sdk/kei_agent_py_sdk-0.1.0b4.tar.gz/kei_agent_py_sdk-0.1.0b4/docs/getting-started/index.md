# Erste Schritte

Willkommen zum KEI-Agent Python SDK! Diese Sektion führt Sie durch die ersten Schritte zur Verwendung des SDK in Ihren Projekten.

## 📋 Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Ihr System die folgenden Anforderungen erfüllt:

### System-Anforderungen
- **Python**: Version 3.9 oder höher
- **Betriebssystem**: Windows, macOS, Linux
- **Speicher**: Mindestens 512 MB RAM
- **Netzwerk**: Internetverbindung für Package-Installation

### Python-Version prüfen
```bash
python --version
# oder
python3 --version
```

!!! tip "Python-Version"
    Das KEI-Agent SDK nutzt moderne Python-Features und erfordert mindestens Python 3.9. Für die beste Performance empfehlen wir Python 3.11 oder höher.

## 🚀 Schnellstart-Übersicht

1. **[Installation](installation.md)** - SDK installieren und einrichten
2. **[Quick Start](quickstart.md)** - Erste Schritte in 5 Minuten
3. **[Konfiguration](configuration.md)** - Client-Setup und Optionen

## 🎯 Was Sie lernen werden

Nach Abschluss dieser Sektion können Sie:

- ✅ Das KEI-Agent SDK in verschiedenen Umgebungen installieren
- ✅ Einen einfachen Agent-Client erstellen und konfigurieren
- ✅ Basis-Operationen wie Plan, Act, Observe ausführen
- ✅ Enterprise-Features wie Logging und Health Checks nutzen
- ✅ Verschiedene Protokolle (RPC, Stream, Bus, MCP) verwenden

## 📚 Lernpfad

### Für Einsteiger
1. Beginnen Sie mit der [**Installation**](installation.md)
2. Folgen Sie dem [**Quick Start Guide**](quickstart.md)
3. Erkunden Sie die [**Basis-Konzepte**](../user-guide/concepts.md)

### Für erfahrene Entwickler
1. Überspringen Sie zur [**Konfiguration**](configuration.md)
2. Lesen Sie die [**API-Referenz**](../api/index.md)
3. Erkunden Sie [**Enterprise Features**](../enterprise/index.md)

### Für Migration von Legacy SDK
1. Lesen Sie den [**Migration Guide**](../migration/from-legacy.md)
2. Überprüfen Sie [**Breaking Changes**](../migration/breaking-changes.md)
3. Folgen Sie dem [**Upgrade Guide**](../migration/upgrade-guide.md)

## 🔧 Entwicklungsumgebung

### Empfohlene IDEs
- **PyCharm**: Vollständige Type Hints-Unterstützung
- **VS Code**: Mit Python-Extension
- **Vim/Neovim**: Mit LSP-Support

### Virtuelle Umgebung
Wir empfehlen die Verwendung einer virtuellen Umgebung:

```bash
# Mit venv
python -m venv kei-agent-env
source kei-agent-env/bin/activate  # Linux/macOS
# oder
kei-agent-env\Scripts\activate     # Windows

# Mit conda
conda create -n kei-agent python=3.11
conda activate kei-agent
```

## 🆘 Hilfe benötigt?

Falls Sie Probleme haben:

1. **Dokumentation durchsuchen**: Nutzen Sie die Suchfunktion oben
2. **Troubleshooting**: Besuchen Sie [Häufige Probleme](../troubleshooting/common-issues.md)
3. **Community**: Stellen Sie Fragen in [GitHub Discussions](https://github.com/kei-framework/kei-agent/discussions)
4. **Issues**: Melden Sie Bugs in [GitHub Issues](https://github.com/kei-framework/kei-agent/issues)

---

**Bereit?** Beginnen Sie mit der [Installation →](installation.md)

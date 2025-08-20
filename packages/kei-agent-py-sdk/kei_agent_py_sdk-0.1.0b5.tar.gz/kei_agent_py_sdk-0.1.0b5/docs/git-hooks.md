# Git Hooks für KEI Agent Python SDK

## Übersicht

Das KEI Agent Python SDK verwendet Git Hooks, um automatisch Code-Qualitätsprüfungen vor jedem Commit durchzuführen. Dies stellt sicher, dass nur sauberer, formatierter und fehlerfreier Code in das Repository gelangt.

## Verfügbare Hooks

### Pre-Commit Hook

Der Pre-Commit Hook wird automatisch vor jedem `git commit` ausgeführt und:

1. **Formatiert den Code** mit `ruff format`
2. **Führt Linting aus** mit `ruff check --fix`
3. **Fügt formatierte Dateien automatisch hinzu**
4. **Verhindert Commits bei Fehlern**

## Installation

### Automatische Installation

```bash
# Komplettes Development-Setup (empfohlen)
make dev-setup

# Oder nur Git Hooks installieren
make setup-hooks
```

### Manuelle Installation

```bash
# Git Hooks Pfad setzen
git config core.hooksPath .githooks

# Hooks ausführbar machen
chmod +x .githooks/*
```

## Verwendung

### Normaler Workflow

```bash
# Änderungen machen
echo "print('Hello World')" > test.py

# Commit versuchen
git add test.py
git commit -m "Add test file"

# Der Pre-Commit Hook läuft automatisch:
# 🔍 Pre-Commit Hook: Führe Code-Qualitätsprüfungen aus...
# 📝 Führe 'make lint' aus...
# ✅ Linting und Formatierung erfolgreich!
# ✅ Commit kann fortgesetzt werden.
```

### Bei Linting-Fehlern

```bash
# Wenn Linting-Fehler auftreten:
# ❌ Linting fehlgeschlagen!
# 💡 Bitte behebe die Fehler und versuche den Commit erneut.

# Fehler beheben und erneut versuchen
git commit -m "Add test file"
```

### Hook umgehen (Notfall)

```bash
# Nur in Notfällen verwenden!
git commit --no-verify -m "Emergency commit"
```

## Konfiguration

### Hook deaktivieren

```bash
# Temporär deaktivieren
git config core.hooksPath ""

# Wieder aktivieren
git config core.hooksPath .githooks
```

### Eigene Hooks hinzufügen

1. Neue Hook-Datei in `.githooks/` erstellen
2. Ausführbar machen: `chmod +x .githooks/mein-hook`
3. Hook-Setup erneut ausführen: `make setup-hooks`

## Fehlerbehebung

### "make: command not found"

```bash
# macOS
brew install make

# Ubuntu/Debian
sudo apt-get install make

# Windows (WSL)
sudo apt-get install make
```

### "ruff: command not found"

```bash
# Development-Dependencies installieren
make install-dev
```

### Hook wird nicht ausgeführt

```bash
# Prüfe Git-Konfiguration
git config core.hooksPath

# Sollte ".githooks" ausgeben
# Falls nicht, erneut installieren:
make setup-hooks
```

### Permissions-Fehler

```bash
# Hooks ausführbar machen
chmod +x .githooks/*
```

## Best Practices

1. **Immer `make dev-setup` nach dem Klonen ausführen**
2. **Kleine, atomare Commits machen**
3. **Hooks nicht umgehen** (außer in Notfällen)
4. **Bei Problemen zuerst `make lint` manuell ausführen**
5. **Regelmäßig `make quality` für vollständige Prüfung**

## Integration mit IDEs

### VS Code

```json
// .vscode/settings.json
{
    "python.linting.enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. Settings → Tools → External Tools
2. Add Tool: Name="Ruff Format", Program="ruff", Arguments="format $FilePath$"
3. Add Tool: Name="Ruff Check", Program="ruff", Arguments="check $FilePath$"

## Weitere Informationen

- [Ruff Dokumentation](https://docs.astral.sh/ruff/)
- [Git Hooks Dokumentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [KEI Agent SDK Entwicklungsrichtlinien](./development.md)

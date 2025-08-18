# 🧑‍💻 Entwicklung & Beitrag

Entwicklungs-Setup, Code-Qualität und Beitragsleitlinien.

## Lokales Setup

```bash
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev,docs,security]"
pre-commit install
```

## Qualitätsstandards

- PEP 8, PEP 257, PEP 484
- Deutsche Kommentare/Docstrings; englische Identifier
- Öffentliche APIs vollständig typisiert
- Funktionen < 20 Zeilen, Module < 200 Zeilen

## Tests & Linting

```bash
pytest -v
ruff check .
mypy .
```

## Dokumentation

```bash
mkdocs serve
mkdocs build --strict --verbose
```

## Release-Prozess (Kurz)

1. Version in `pyproject.toml` erhöhen
2. `CHANGELOG.md` aktualisieren
3. Tag pushen (`vX.Y.Z[.pre]`)
4. CI veröffentlicht (TestPyPI/PyPI)

## Pull Requests

- Kleine, fokussierte Änderungen
- Tests und Doku anpassen
- CI muss grün sein

## Sicherheit

- Keine Secrets commiten (GitHub Secrets / Azure Key Vault)
- Abhängigkeiten regelmäßig aktualisieren (Dependabot)

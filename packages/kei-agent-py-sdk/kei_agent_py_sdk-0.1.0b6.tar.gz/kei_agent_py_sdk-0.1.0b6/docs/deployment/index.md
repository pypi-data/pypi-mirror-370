# 🚀 Deployment & Setup

Diese Anleitung beschreibt Setup, Dokumentations-Build und Veröffentlichungen (TestPyPI/PyPI, GitHub Pages).

## Voraussetzungen

- Python 3.8–3.12
- Git, Make (optional)
- GitHub Actions Zugriff (für CI/CD)

## Lokale Installation

```bash
git clone https://github.com/oscharko-dev/kei-agent-py-sdk.git
cd kei-agent-py-sdk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev,docs,security]"
pre-commit install
```

## Dokumentation lokal bauen

```bash
mkdocs serve
# http://127.0.0.1:8000
```

CI-Validierung lokal:

```bash
mkdocs build --strict --verbose
```

## GitHub Pages Deployment

Der Workflow `.github/workflows/docs.yml` baut und deployed auf Push nach `main`/`master`.

Manuell triggern: GitHub → Actions → „Documentation“ → Run workflow.

## Release nach TestPyPI

Workflow: `.github/workflows/release-test-pypi.yml`

Vorgehen:

- Version in `pyproject.toml` erhöhen
- Tag pushen (z. B. `v0.1.0b2`)
- Workflow veröffentlicht nach TestPyPI

Prüfen:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "kei_agent_py_sdk[security,docs]"
python -c "import kei_agent; print(kei_agent.__version__)"
```

## Release nach PyPI

Workflow: `.github/workflows/release-pypi.yml`

```bash
pip install kei_agent_py_sdk
```

## Qualitätssicherung vor Release

- Tests: `pytest -v`
- Lint/Typing: `ruff check . && mypy .`
- Sicherheit: `bandit -r .`
- Docs-Build: `mkdocs build --strict`

## Azure-Integration (optional)

- Secrets in GitHub Actions als Encrypted Secrets
- Azure Key Vault/Managed Identity
- OpenTelemetry Export (Jaeger/Zipkin)

Weitere Details: `enterprise/monitoring.md`, `enterprise/security.md`.

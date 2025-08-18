#!/usr/bin/env python3
# validate_setup.py
"""
Setup-Validierung für KEI-Agent Python SDK.

Prüft alle Aspekte der SDK-Installation, Konfiguration und Dokumentation
vor der PyPI-Veröffentlichung.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Basis-Verzeichnis
BASE_DIR = Path(__file__).parent.absolute()


class ValidationResult:
    """Ergebnis einer Validierung."""

    def __init__(
        self,
        name: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.success = success
        self.message = message
        self.details = details or {}


class SetupValidator:
    """Validator für SDK-Setup."""

    def __init__(self):
        self.results: List[ValidationResult] = []

    def add_result(
        self,
        name: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Fügt Validierungsergebnis hinzu."""
        result = ValidationResult(name, success, message, details)
        self.results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")

        if details and not success:
            for key, value in details.items():
                print(f"    {key}: {value}")

    def validate_python_version(self) -> bool:
        """Validiert Python-Version."""
        version = sys.version_info
        required_major, required_minor = 3, 8

        if version.major >= required_major and version.minor >= required_minor:
            self.add_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (erforderlich: {required_major}.{required_minor}+)",
            )
            return True
        else:
            self.add_result(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor}.{version.micro} zu alt (erforderlich: {required_major}.{required_minor}+)",
            )
            return False

    def validate_dependencies(self) -> bool:
        """Validiert installierte Dependencies."""
        required_deps = [
            "httpx",
            "websockets",
            "pydantic",
            "typing_extensions",
            "opentelemetry-api",
            "tenacity",
            "msgpack",
            "packaging",
            "python-dateutil",
            "psutil",
            "structlog",
        ]

        dev_deps = [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-mock",
            "ruff",
            "mypy",
            "bandit",
            "build",
            "twine",
        ]

        docs_deps = ["mkdocs", "mkdocs-material", "mkdocstrings"]

        missing_required = []
        missing_dev = []
        missing_docs = []

        for dep in required_deps:
            if not self._check_dependency(dep):
                missing_required.append(dep)

        for dep in dev_deps:
            if not self._check_dependency(dep):
                missing_dev.append(dep)

        for dep in docs_deps:
            if not self._check_dependency(dep):
                missing_docs.append(dep)

        if missing_required:
            self.add_result(
                "Required Dependencies",
                False,
                f"Fehlende erforderliche Dependencies: {missing_required}",
            )
            return False
        else:
            self.add_result(
                "Required Dependencies",
                True,
                "Alle erforderlichen Dependencies installiert",
            )

        if missing_dev:
            self.add_result(
                "Development Dependencies",
                False,
                f"Fehlende Development-Dependencies: {missing_dev}",
                {"install_command": f"pip install {' '.join(missing_dev)}"},
            )
        else:
            self.add_result(
                "Development Dependencies",
                True,
                "Alle Development-Dependencies installiert",
            )

        if missing_docs:
            self.add_result(
                "Documentation Dependencies",
                False,
                f"Fehlende Dokumentations-Dependencies: {missing_docs}",
                {"install_command": f"pip install {' '.join(missing_docs)}"},
            )
        else:
            self.add_result(
                "Documentation Dependencies",
                True,
                "Alle Dokumentations-Dependencies installiert",
            )

        return len(missing_required) == 0

    def _check_dependency(self, package_name: str) -> bool:
        """Prüft ob Package installiert ist."""
        try:
            __import__(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False

    def validate_file_structure(self) -> bool:
        """Validiert Datei-Struktur."""
        required_files = [
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "MANIFEST.in",
            "__init__.py",
            "unified_client_refactored.py",
            "protocol_types.py",
            "security_manager.py",
            "protocol_clients.py",
            "protocol_selector.py",
            "enterprise_logging.py",
            "health_checks.py",
            "input_validation.py",
            "docs/index.md",
            "mkdocs.yml",
        ]

        missing_files = []

        for file_path in required_files:
            full_path = BASE_DIR / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            self.add_result(
                "File Structure", False, f"Fehlende Dateien: {missing_files}"
            )
            return False
        else:
            self.add_result(
                "File Structure", True, "Alle erforderlichen Dateien vorhanden"
            )
            return True

    def validate_imports(self) -> bool:
        """Validiert SDK-Imports."""
        try:
            # Hauptmodul importieren
            sys.path.insert(0, str(BASE_DIR))
            import kei_agent

            # Test basic import
            _ = (
                kei_agent.__version__
                if hasattr(kei_agent, "__version__")
                else "unknown"
            )

            self.add_result(
                "SDK Imports",
                True,
                "Alle Hauptkomponenten erfolgreich importiert",
                {"version": getattr(kei_agent, "__version__", "unknown")},
            )
            return True

        except ImportError as e:
            self.add_result("SDK Imports", False, f"Import-Fehler: {e}")
            return False
        except Exception as e:
            self.add_result(
                "SDK Imports", False, f"Unerwarteter Fehler beim Import: {e}"
            )
            return False

    def validate_documentation(self) -> bool:
        """Validiert Dokumentation."""
        docs_dir = BASE_DIR / "docs"
        mkdocs_config = BASE_DIR / "mkdocs.yml"

        if not docs_dir.exists():
            self.add_result(
                "Documentation", False, "Dokumentationsverzeichnis nicht gefunden"
            )
            return False

        if not mkdocs_config.exists():
            self.add_result("Documentation", False, "mkdocs.yml nicht gefunden")
            return False

        # Wichtige Dokumentations-Dateien prüfen
        required_docs = [
            "index.md",
            "getting-started/installation.md",
            "getting-started/quickstart.md",
            "api/index.md",
            "api/unified-client.md",
            "enterprise/index.md",
            "examples/index.md",
            "troubleshooting/index.md",
        ]

        missing_docs = []
        for doc in required_docs:
            if not (docs_dir / doc).exists():
                missing_docs.append(doc)

        if missing_docs:
            self.add_result(
                "Documentation",
                False,
                f"Fehlende Dokumentations-Dateien: {missing_docs}",
            )
            return False

        # MkDocs Build testen
        try:
            result = subprocess.run(
                ["mkdocs", "build", "--strict"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.add_result(
                    "Documentation",
                    True,
                    "Dokumentation vollständig und MkDocs-Build erfolgreich",
                )
                return True
            else:
                self.add_result(
                    "Documentation",
                    False,
                    f"MkDocs-Build fehlgeschlagen: {result.stderr}",
                )
                return False

        except subprocess.TimeoutExpired:
            self.add_result("Documentation", False, "MkDocs-Build Timeout")
            return False
        except FileNotFoundError:
            self.add_result("Documentation", False, "MkDocs nicht installiert")
            return False

    def validate_tests(self) -> bool:
        """Validiert Test-Suite."""
        tests_dir = BASE_DIR / "tests"

        if not tests_dir.exists():
            self.add_result("Tests", False, "Tests-Verzeichnis nicht gefunden")
            return False

        # Test-Dateien zählen
        test_files = list(tests_dir.glob("test_*.py"))

        if len(test_files) == 0:
            self.add_result("Tests", False, "Keine Test-Dateien gefunden")
            return False

        # Pytest ausführen (nur Syntax-Check)
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-q"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.add_result(
                    "Tests",
                    True,
                    "Test-Suite erfolgreich ausgeführt",
                )
                return True
            else:
                self.add_result(
                    "Tests",
                    False,
                    f"Tests fehlgeschlagen: {result.stdout or result.stderr}",
                )
                return False

        except subprocess.TimeoutExpired:
            self.add_result("Tests", False, "Test-Ausführung Timeout")
            return False
        except FileNotFoundError:
            self.add_result("Tests", False, "Pytest nicht installiert")
            return False

    def validate_package_metadata(self) -> bool:
        """Validiert Package-Metadaten."""
        pyproject_file = BASE_DIR / "pyproject.toml"

        try:
            import tomli

            with open(pyproject_file, "rb") as f:
                pyproject_data = tomli.load(f)

            project = pyproject_data.get("project", {})

            required_fields = ["name", "version", "description", "authors"]
            missing_fields = []

            for field in required_fields:
                if field not in project:
                    missing_fields.append(field)

            if missing_fields:
                self.add_result(
                    "Package Metadata",
                    False,
                    f"Fehlende Metadaten-Felder: {missing_fields}",
                )
                return False

            # Version-Format prüfen
            version = project["version"]
            if not version or len(version.split(".")) < 2:
                self.add_result(
                    "Package Metadata", False, f"Ungültiges Versions-Format: {version}"
                )
                return False

            self.add_result(
                "Package Metadata",
                True,
                f"Metadaten vollständig (v{version})",
                {
                    "name": project["name"],
                    "version": version,
                    "description": project["description"][:50] + "...",
                },
            )
            return True

        except Exception as e:
            self.add_result(
                "Package Metadata", False, f"Fehler beim Lesen der pyproject.toml: {e}"
            )
            return False

    def run_all_validations(self) -> bool:
        """Führt alle Validierungen aus."""
        print("🔍 KEI-Agent SDK Setup-Validierung")
        print("=" * 60)

        validations = [
            self.validate_python_version,
            self.validate_dependencies,
            self.validate_file_structure,
            self.validate_package_metadata,
            self.validate_imports,
            self.validate_documentation,
            self.validate_tests,
        ]

        all_passed = True

        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.add_result(
                    validation.__name__, False, f"Validierung fehlgeschlagen: {e}"
                )
                all_passed = False

        print("\n" + "=" * 60)

        if all_passed:
            print("🎉 Alle Validierungen erfolgreich!")
            print("✅ SDK ist bereit für PyPI-Veröffentlichung")
        else:
            failed_count = sum(1 for r in self.results if not r.success)
            print(f"❌ {failed_count} Validierung(en) fehlgeschlagen")
            print("🔧 Beheben Sie die Probleme vor der Veröffentlichung")

        return all_passed

    def generate_report(self) -> Dict[str, Any]:
        """Generiert Validierungs-Report."""
        report = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "overall_success": all(r.success for r in self.results),
            "total_validations": len(self.results),
            "passed": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        # Report speichern
        report_file = BASE_DIR / "validation-report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Validierungs-Report gespeichert: {report_file}")
        return report


def main():
    """Hauptfunktion."""
    validator = SetupValidator()

    try:
        success = validator.run_all_validations()
        validator.generate_report()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Validierung abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validierung fehlgeschlagen: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

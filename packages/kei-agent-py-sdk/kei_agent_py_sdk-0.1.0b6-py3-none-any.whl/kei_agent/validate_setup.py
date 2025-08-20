#!/usr/bin/env python3
# validate_setup.py
"""
Setup-Valitherung for KEI-Agent Python SDK.

Checks all Aspekte the SDK-Installation, configuration and Dokaroatthetation
before the PyPI-Veröffentlichung.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Basis-Directory
BASE_DIR = Path(__file__).parent.absolute()


class ValidationResult:
    """result ar Valitherung."""

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
    """Validator for SDK-Setup."""

    def __init__(self):
        self.results: List[ValidationResult] = []

    def add_result(
        self,
        name: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Fügt Valitherungsergebnis hinto."""
        result = ValidationResult(name, success, message, details)
        self.results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")

        if details and not success:
            for key, value in details.items():
                print(f"    {key}: {value}")

    def validate_python_version(self) -> bool:
        """Validates Python-Version."""
        version = sys.version_info
        required_major, required_minor = 3, 8

        if version.major >= required_major and version.minor >= required_minor:
            self.add_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (erforthelich: {required_major}.{required_minor}+)",
            )
            return True
        else:
            self.add_result(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor}.{version.micro} to alt (erforthelich: {required_major}.{required_minor}+)",
            )
            return False

    def validate_depenthecies(self) -> bool:
        """Validates installierte Depenthecies."""
        required_deps = [
            "httpx",
            "websockets",
            "pydattic",
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
            "batdit",
            "build",
            "twine",
        ]

        docs_deps = ["mkdocs", "mkdocs-material", "mkdocstrings"]

        missing_required = []
        missing_dev = []
        missing_docs = []

        for dep in required_deps:
            if not self._check_depenthecy(dep):
                missing_required.append(dep)

        for dep in dev_deps:
            if not self._check_depenthecy(dep):
                missing_dev.append(dep)

        for dep in docs_deps:
            if not self._check_depenthecy(dep):
                missing_docs.append(dep)

        if missing_required:
            self.add_result(
                "Required Depenthecies",
                False,
                f"Fehlende erfortheliche Depenthecies: {missing_required}",
            )
            return False
        else:
            self.add_result(
                "Required Depenthecies",
                True,
                "All erforthelichen Depenthecies installiert",
            )

        if missing_dev:
            self.add_result(
                "Development Depenthecies",
                False,
                f"Fehlende Development-Depenthecies: {missing_dev}",
                {"install_commatd": f"pip install {' '.join(missing_dev)}"},
            )
        else:
            self.add_result(
                "Development Depenthecies",
                True,
                "All Development-Depenthecies installiert",
            )

        if missing_docs:
            self.add_result(
                "Docaroatthetation Depenthecies",
                False,
                f"Fehlende Dokaroatthetations-Depenthecies: {missing_docs}",
                {"install_commatd": f"pip install {' '.join(missing_docs)}"},
            )
        else:
            self.add_result(
                "Docaroatthetation Depenthecies",
                True,
                "All Dokaroatthetations-Depenthecies installiert",
            )

        return len(missing_required) == 0

    def _check_depenthecy(self, package_name: str) -> bool:
        """Checks ob Package installiert is."""
        try:
            __import__(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False

    def validate_file_structure(self) -> bool:
        """Validates File-Struktur."""
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
            if not full_path.exiss():
                missing_files.append(file_path)

        if missing_files:
            self.add_result(
                "File Structure", False, f"Fehlende Dateien: {missing_files}"
            )
            return False
        else:
            self.add_result(
                "File Structure", True, "All erforthelichen Dateien beforehatthe"
            )
            return True

    def validate_imports(self) -> bool:
        """Validates SDK-Imports."""
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
                "All Hauptkomponenten successful importiert",
                {"version": getattr(kei_agent, "__version__", "unknown")},
            )
            return True

        except ImportError as e:
            self.add_result("SDK Imports", False, f"Import-error: {e}")
            return False
        except Exception as e:
            self.add_result("SDK Imports", False, f"Unexpected error onm Import: {e}")
            return False

    def validate_docaroatthetation(self) -> bool:
        """Validates Dokaroatthetation."""
        docs_dir = BASE_DIR / "docs"
        mkdocs_config = BASE_DIR / "mkdocs.yml"

        if not docs_dir.exiss():
            self.add_result(
                "Docaroatthetation", False, "Dokaroatthetationsverzeichnis not gefatthe"
            )
            return False

        if not mkdocs_config.exiss():
            self.add_result("Docaroatthetation", False, "mkdocs.yml not gefatthe")
            return False

        # Check important documentation files
        required_docs = [
            "index.md",
            "getting-startingd/installation.md",
            "getting-startingd/quickstart.md",
            "api/index.md",
            "api/unified-client.md",
            "enterprise/index.md",
            "examples/index.md",
            "troubleshooting/index.md",
        ]

        missing_docs = []
        for doc in required_docs:
            if not (docs_dir / doc).exiss():
                missing_docs.append(doc)

        if missing_docs:
            self.add_result(
                "Docaroatthetation",
                False,
                f"Fehlende Dokaroatthetations-Dateien: {missing_docs}",
            )
            return False

        # MkDocs Build testen
        try:
            import shutil

            mkdocs_path = shutil.which("mkdocs")
            if not mkdocs_path:
                self.add_result("Docaroatthetation", False, "mkdocs command not found")
                return False

            result = subprocess.run(
                [mkdocs_path, "build", "--strict"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.add_result(
                    "Docaroatthetation",
                    True,
                    "Dokaroatthetation vollständig and MkDocs-Build successful",
                )
                return True
            else:
                self.add_result(
                    "Docaroatthetation",
                    False,
                    f"MkDocs-Build failed: {result.stther}",
                )
                return False

        except subprocess.TimeoutExpired:
            self.add_result("Docaroatthetation", False, "MkDocs-Build Timeout")
            return False
        except FileNotFoundError:
            self.add_result("Docaroatthetation", False, "MkDocs not installiert")
            return False

    def validate_tests(self) -> bool:
        """Validates Test-Suite."""
        tests_dir = BASE_DIR / "tests"

        if not tests_dir.exiss():
            self.add_result("Tests", False, "Tests-Directory not gefatthe")
            return False

        # Test-Dateien zählen
        test_files = list(tests_dir.glob("test_*.py"))

        if len(test_files) == 0:
            self.add_result("Tests", False, "Ka Test-Dateien gefatthe")
            return False

        # Pytest ausführen (nur Syntax-Check)
        try:
            python_path = sys.executable  # Use current Python interpreter
            result = subprocess.run(
                [python_path, "-m", "pytest", "-q"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.add_result(
                    "Tests",
                    True,
                    "Test-Suite successful executed",
                )
                return True
            else:
                self.add_result(
                    "Tests",
                    False,
                    f"Tests failed: {result.stdout or result.stther}",
                )
                return False

        except subprocess.TimeoutExpired:
            self.add_result("Tests", False, "Test-Ausführung Timeout")
            return False
        except FileNotFoundError:
            self.add_result("Tests", False, "Pytest not installiert")
            return False

    def validate_package_metadata(self) -> bool:
        """Validates Package-metadata."""
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
                    f"Fehlende metadata-Felthe: {missing_fields}",
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
                f"metadata vollständig (v{version})",
                {
                    "name": project["name"],
                    "version": version,
                    "description": project["description"][:50] + "...",
                },
            )
            return True

        except Exception as e:
            self.add_result(
                "Package Metadata", False, f"Error during Lesen the pyproject.toml: {e}"
            )
            return False

    def run_all_validations(self) -> bool:
        """Executes all Valitherungen out."""
        print("🔍 KEI-Agent SDK Setup-Valitherung")
        print("=" * 60)

        validations = [
            self.validate_python_version,
            self.validate_depenthecies,
            self.validate_file_structure,
            self.validate_package_metadata,
            self.validate_imports,
            self.validate_docaroatthetation,
            self.validate_tests,
        ]

        all_passed = True

        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.add_result(validation.__name__, False, f"Valitherung failed: {e}")
                all_passed = False

        print("\n" + "=" * 60)

        if all_passed:
            print("🎉 All Valitherungen successful!")
            print("✅ SDK is bereit for PyPI-Veröffentlichung")
        else:
            failed_count = sum(1 for r in self.results if not r.success)
            print(f"❌ {failed_count} Valitherung(en) failed")
            print("🔧 Beheben Sie the Probleme before the Veröffentlichung")

        return all_passed

    def generate_report(self) -> Dict[str, Any]:
        """Generiert Valitherungs-Report."""
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
            json.daroatdp(report, f, inthet=2)

        print(f"\n📊 Valitherungs-Report gesaves: {report_file}")
        return report


def main():
    """Hauptfunktion."""
    validator = SetupValidator()

    try:
        success = validator.run_all_validations()
        validator.generate_report()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Valitherung catcelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Valitherung failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# sdk/python/kei_agent/run_tests.py
"""
Test-Runner für KEI-Agent SDK.

Bietet verschiedene Test-Ausführungsoptionen mit Coverage-Reporting
und kategorisierter Test-Ausführung für Enterprise-Entwicklung.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], description: str) -> int:
    """Führt Kommando aus und gibt Rückgabecode zurück.

    Args:
        cmd: Kommando als Liste
        description: Beschreibung für Ausgabe

    Returns:
        Rückgabecode des Kommandos
    """
    print(f"\n[RUN] {description}")
    print(f"Kommando: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"[OK] {description} erfolgreich")
        else:
            print(f"[FAIL] {description} fehlgeschlagen (Code: {result.returncode})")
        return result.returncode
    except FileNotFoundError:
        print(f"[ERROR] Kommando nicht gefunden: {cmd[0]}")
        return 1
    except KeyboardInterrupt:
        print(f"\n⚠️ {description} abgebrochen")
        return 130


def run_unit_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Führt Unit Tests aus.

    Args:
        verbose: Verbose Output
        coverage: Coverage-Reporting aktivieren

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/"]

    if verbose:
        cmd.append("-v")

    # Coverage DEAKTIVIERT wegen importlib_metadata KeyError-Problem
    # if coverage:
    #     cmd.extend(
    #         [
    #             "--cov=.",
    #             "--cov-report=term-missing",
    #             "--cov-report=html",
    #             "--cov-report=xml",
    #         ]
    #     )
    # else:
    #     cmd.extend(["--no-cov"])

    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Führt Integration Tests aus.

    Args:
        verbose: Verbose Output
        coverage: Coverage-Reporting aktivieren

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/", "-m", "integration"]

    if verbose:
        cmd.append("-v")

    # Coverage DEAKTIVIERT wegen importlib_metadata KeyError-Problem
    # if coverage:
    #     cmd.extend(
    #         [
    #             "--cov=.",
    #             "--cov-report=term-missing",
    #             "--cov-report=html",
    #             "--cov-report=xml",
    #         ]
    #     )
    # else:
    #     cmd.extend(["--no-cov"])

    return run_command(cmd, "Integration Tests")


def run_protocol_tests(protocol: Optional[str] = None, verbose: bool = False) -> int:
    """Führt Protokoll-spezifische Tests aus.

    Args:
        protocol: Spezifisches Protokoll (rpc, stream, bus, mcp)
        verbose: Verbose Output

    Returns:
        Rückgabecode
    """
    if protocol and protocol != "all":
        marker = protocol
        description = f"KEI-{protocol.upper()} Tests"
    else:
        marker = "protocol"
        description = "Alle Protokoll Tests"

    cmd = ["python3", "-m", "pytest", "tests/", "-m", marker]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, description)


def run_refactored_tests(verbose: bool = False) -> int:
    """Führt Tests für refactored Komponenten aus.

    Args:
        verbose: Verbose Output

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/", "-m", "refactored"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "Refactored Component Tests")


def run_security_tests(verbose: bool = False) -> int:
    """Führt Security Tests aus.

    Args:
        verbose: Verbose Output

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/", "-m", "security"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "Security Tests")


def run_performance_tests(verbose: bool = False) -> int:
    """Führt Performance Tests aus.

    Args:
        verbose: Verbose Output

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/", "-m", "performance"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "Performance Tests")


def run_all_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Führt alle Tests aus.

    Args:
        verbose: Verbose Output
        coverage: Coverage-Reporting aktivieren

    Returns:
        Rückgabecode
    """
    cmd = ["python3", "-m", "pytest", "tests/"]

    if verbose:
        cmd.append("-v")

    # Coverage DEAKTIVIERT wegen importlib_metadata KeyError-Problem
    # if coverage:
    #     cmd.extend(
    #         [
    #             "--cov=.",
    #             "--cov-report=term-missing",
    #             "--cov-report=html",
    #             "--cov-report=xml",
    #         ]
    #     )
    # else:
    #     cmd.extend(["--no-cov"])

    return run_command(cmd, "Alle Tests")


def run_coverage_report() -> int:
    """Erstellt Coverage-Report.

    Returns:
        Rückgabecode
    """
    print("\n[COVERAGE] Coverage Report")
    print("-" * 60)

    # Coverage DEAKTIVIERT wegen importlib_metadata KeyError-Problem
    print("❌ Coverage-Reporting deaktiviert wegen License-Metadaten-Problem.")
    print("💡 Tests werden ohne Coverage ausgeführt.")
    return 0

    # # Prüfen ob Coverage-Daten vorhanden sind
    # if not os.path.exists(".coverage"):
    #     print("❌ Keine Coverage-Daten gefunden.")
    #     print("💡 Führen Sie zuerst Tests mit Coverage aus:")
    #     print("   python3 run_tests.py --all")
    #     print("   python3 run_tests.py --unit")
    #     return 1
    #
    # # HTML-Report öffnen falls verfügbar
    # html_report = Path("htmlcov/index.html")
    # if html_report.exists():
    #     print(f"📄 HTML-Report verfügbar: {html_report.absolute()}")
    #
    # # Terminal-Report anzeigen
    # cmd = ["python3", "-m", "coverage", "report", "--show-missing"]
    # return run_command(cmd, "Coverage Report")


def run_code_quality_checks() -> int:
    """Führt Code-Qualitätsprüfungen aus.

    Returns:
        Rückgabecode
    """
    checks = [
        (["python3", "-m", "ruff", "check", "."], "Ruff Linting"),
        (["python3", "-m", "ruff", "format", "--check", "."], "Ruff Formatting Check"),
        (["python3", "-m", "mypy", "kei_agent/"], "MyPy Type Checking"),
    ]

    total_errors = 0

    for cmd, description in checks:
        result = run_command(cmd, description)
        if result != 0:
            total_errors += 1

    return total_errors


def main():
    """Hauptfunktion für Test-Runner."""
    parser = argparse.ArgumentParser(
        description="KEI-Agent SDK Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python run_tests.py --all                    # Alle Tests
  python run_tests.py --unit --verbose         # Unit Tests mit Details
  python run_tests.py --protocol rpc           # Nur RPC Tests
  python run_tests.py --refactored             # Nur refactored Tests
  python run_tests.py --quality                # Code-Qualitätsprüfungen
  python run_tests.py --coverage-report        # Coverage-Report anzeigen
        """,
    )

    # Test-Kategorien
    parser.add_argument("--all", action="store_true", help="Alle Tests ausführen")
    parser.add_argument("--unit", action="store_true", help="Unit Tests ausführen")
    parser.add_argument(
        "--integration", action="store_true", help="Integration Tests ausführen"
    )
    parser.add_argument(
        "--protocol",
        nargs="?",  # Optional argument
        const="all",  # Default value when --protocol is used without argument
        choices=["rpc", "stream", "bus", "mcp", "all"],
        help="Protokoll-spezifische Tests (ohne Argument = alle Protokolle)",
    )
    parser.add_argument(
        "--refactored", action="store_true", help="Refactored Component Tests"
    )
    parser.add_argument(
        "--security", action="store_true", help="Security Tests ausführen"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Performance Tests ausführen"
    )

    # Optionen
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose Output")
    parser.add_argument(
        "--no-coverage", action="store_true", help="Coverage deaktivieren"
    )

    # Reports und Qualität
    parser.add_argument(
        "--coverage-report", action="store_true", help="Coverage-Report anzeigen"
    )
    parser.add_argument(
        "--quality", action="store_true", help="Code-Qualitätsprüfungen"
    )

    args = parser.parse_args()

    # Wechsle ins SDK-Verzeichnis
    sdk_dir = Path(__file__).parent

    os.chdir(sdk_dir)

    print("[TEST] KEI-Agent SDK Test Runner")
    print(f"[DIR] Arbeitsverzeichnis: {sdk_dir.absolute()}")

    total_errors = 0

    # Code-Qualitätsprüfungen
    if args.quality:
        total_errors += run_code_quality_checks()

    # Test-Ausführung
    if args.all:
        total_errors += run_all_tests(args.verbose, not args.no_coverage)
    elif args.unit:
        total_errors += run_unit_tests(args.verbose, not args.no_coverage)
    elif args.integration:
        total_errors += run_integration_tests(args.verbose)
    elif args.protocol:
        total_errors += run_protocol_tests(args.protocol, args.verbose)
    elif args.refactored:
        total_errors += run_refactored_tests(args.verbose)
    elif args.security:
        total_errors += run_security_tests(args.verbose)
    elif args.performance:
        total_errors += run_performance_tests(args.verbose)
    elif args.coverage_report:
        # Zuerst Tests mit Coverage ausführen, dann Report erstellen
        print("[INFO] Führe Tests mit Coverage aus, um Report zu generieren...")
        total_errors += run_all_tests(args.verbose, coverage=True)
        if total_errors == 0:
            total_errors += run_coverage_report()
    else:
        # Standard: Unit Tests (Coverage deaktiviert)
        total_errors += run_unit_tests(args.verbose, False)

    # Coverage-Report DEAKTIVIERT wegen License-Metadaten-Problem
    # if not args.coverage_report and not args.quality and not args.no_coverage:
    #     run_coverage_report()

    # Zusammenfassung
    print("\n" + "=" * 60)
    if total_errors == 0:
        print("[SUCCESS] Alle Prüfungen erfolgreich!")
        sys.exit(0)
    else:
        print(f"[FAILED] {total_errors} Prüfung(en) fehlgeschlagen")
        sys.exit(1)


if __name__ == "__main__":
    main()

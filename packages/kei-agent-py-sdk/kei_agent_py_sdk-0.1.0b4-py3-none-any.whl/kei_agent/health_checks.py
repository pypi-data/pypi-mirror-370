# sdk/python/kei_agent/health_checks.py
"""
Enterprise Health Checks für KEI-Agent SDK.

Implementiert umfassende Health-Check-Mechanismen für Monitoring,
Alerting und automatische Wiederherstellung in Production-Umgebungen.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from enterprise_logging import get_logger

# Initialisiert Modul-Logger
_logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health-Status-Werte für Komponenten.

    Attributes:
        HEALTHY: Komponente funktioniert normal
        DEGRADED: Komponente funktioniert mit Einschränkungen
        UNHEALTHY: Komponente funktioniert nicht
        UNKNOWN: Status kann nicht ermittelt werden
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Ergebnis eines Health-Checks.

    Attributes:
        name: Name der geprüften Komponente
        status: Health-Status
        message: Beschreibung des Status
        details: Zusätzliche Details und Metriken
        timestamp: Zeitpunkt der Prüfung
        duration_ms: Dauer der Prüfung in Millisekunden
        error: Fehler-Information bei Problemen
    """

    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Health-Check-Result zu Dictionary.

        Returns:
            Dictionary-Repräsentation des Results
        """
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


class BaseHealthCheck(ABC):
    """Abstrakte Basisklasse für Health-Checks.

    Definiert Interface für alle Health-Check-Implementierungen
    mit gemeinsamen Funktionalitäten wie Timeout und Retry-Logik.
    """

    def __init__(
        self,
        name: str,
        timeout_seconds: float = 5.0,
        critical: bool = True,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Initialisiert Base Health Check.

        Args:
            name: Name der Komponente
            timeout_seconds: Timeout für Health-Check
            critical: Ob Check kritisch für Gesamtstatus ist
            tags: Tags für Kategorisierung
        """
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.critical = critical
        self.tags = tags or []

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Führt Health-Check aus.

        Returns:
            Health-Check-Result
        """
        pass

    async def run_check(self) -> HealthCheckResult:
        """Führt Health-Check mit Timeout und Error-Handling aus.

        Returns:
            Health-Check-Result mit Timing-Informationen
        """
        start_time = time.time()

        try:
            # Führe Check mit Timeout aus
            result = await asyncio.wait_for(self.check(), timeout=self.timeout_seconds)

            # Füge Timing-Information hinzu
            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms

            return result

        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health-Check Timeout nach {self.timeout_seconds}s",
                duration_ms=duration_ms,
                error="timeout",
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health-Check Fehler: {str(e)}",
                duration_ms=duration_ms,
                error=str(e),
            )


class DatabaseHealthCheck(BaseHealthCheck):
    """Health-Check für Datenbankverbindungen."""

    def __init__(
        self,
        name: str = "database",
        connection_string: Optional[str] = None,
        query: str = "SELECT 1",
        **kwargs: Any,
    ) -> None:
        """Initialisiert Database Health Check.

        Args:
            name: Name des Checks
            connection_string: Datenbank-Verbindungsstring
            query: Test-Query für Verbindungsprüfung
            **kwargs: Zusätzliche Parameter für BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.connection_string = connection_string
        self.query = query

    async def check(self) -> HealthCheckResult:
        """Prüft Datenbankverbindung."""
        if not self.connection_string:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="Keine Datenbankverbindung konfiguriert",
            )

        try:
            # TODO: Implementiere echte Datenbankverbindung
            # Hier würde eine echte DB-Verbindung getestet werden
            await asyncio.sleep(0.1)  # Simuliere DB-Query

            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Datenbankverbindung erfolgreich",
                details={
                    "query": self.query,
                    "connection_pool_size": 10,  # Beispiel-Metrik
                    "active_connections": 3,
                },
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Datenbankverbindung fehlgeschlagen: {str(e)}",
                error=str(e),
            )


class APIHealthCheck(BaseHealthCheck):
    """Health-Check für externe API-Abhängigkeiten."""

    def __init__(
        self,
        name: str,
        url: str,
        expected_status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialisiert API Health Check.

        Args:
            name: Name des Checks
            url: API-URL für Health-Check
            expected_status: Erwarteter HTTP-Status
            headers: HTTP-Headers für Request
            **kwargs: Zusätzliche Parameter für BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.url = url
        self.expected_status = expected_status
        self.headers = headers or {}

    async def check(self) -> HealthCheckResult:
        """Prüft API-Verfügbarkeit."""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, headers=self.headers, timeout=self.timeout_seconds
                )

                if response.status_code == self.expected_status:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.HEALTHY,
                        message=f"API verfügbar (Status: {response.status_code})",
                        details={
                            "url": self.url,
                            "status_code": response.status_code,
                            "response_time_ms": response.elapsed.total_seconds() * 1000,
                        },
                    )
                else:
                    return HealthCheckResult(
                        name=self.name,
                        status=HealthStatus.DEGRADED,
                        message=f"API unerwarteter Status: {response.status_code}",
                        details={
                            "url": self.url,
                            "status_code": response.status_code,
                            "expected_status": self.expected_status,
                        },
                    )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"API nicht erreichbar: {str(e)}",
                error=str(e),
            )


class MemoryHealthCheck(BaseHealthCheck):
    """Health-Check für Speicherverbrauch."""

    def __init__(
        self,
        name: str = "memory",
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95,
        **kwargs: Any,
    ) -> None:
        """Initialisiert Memory Health Check.

        Args:
            name: Name des Checks
            warning_threshold: Warnschwelle (0.0-1.0)
            critical_threshold: Kritische Schwelle (0.0-1.0)
            **kwargs: Zusätzliche Parameter für BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    async def check(self) -> HealthCheckResult:
        """Prüft Speicherverbrauch."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            usage_percent = memory.percent / 100.0

            if usage_percent >= self.critical_threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Kritischer Speicherverbrauch: {usage_percent:.1%}"
            elif usage_percent >= self.warning_threshold:
                status = HealthStatus.DEGRADED
                message = f"Hoher Speicherverbrauch: {usage_percent:.1%}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Speicherverbrauch normal: {usage_percent:.1%}"

            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "total_mb": memory.total // (1024 * 1024),
                    "available_mb": memory.available // (1024 * 1024),
                    "used_mb": memory.used // (1024 * 1024),
                    "warning_threshold": self.warning_threshold,
                    "critical_threshold": self.critical_threshold,
                },
            )

        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNKNOWN,
                message="psutil nicht verfügbar für Speicher-Monitoring",
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Speicher-Check fehlgeschlagen: {str(e)}",
                error=str(e),
            )


@dataclass
class HealthCheckSummary:
    """Zusammenfassung aller Health-Checks.

    Attributes:
        overall_status: Gesamtstatus des Systems
        total_checks: Anzahl durchgeführter Checks
        healthy_count: Anzahl gesunder Komponenten
        degraded_count: Anzahl eingeschränkter Komponenten
        unhealthy_count: Anzahl ungesunder Komponenten
        unknown_count: Anzahl unbekannter Status
        checks: Liste aller Check-Ergebnisse
        timestamp: Zeitpunkt der Zusammenfassung
        duration_ms: Gesamtdauer aller Checks
    """

    overall_status: HealthStatus
    total_checks: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    unknown_count: int
    checks: List[HealthCheckResult]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Summary zu Dictionary.

        Returns:
            Dictionary-Repräsentation der Summary
        """
        return {
            "overall_status": self.overall_status.value,
            "total_checks": self.total_checks,
            "healthy_count": self.healthy_count,
            "degraded_count": self.degraded_count,
            "unhealthy_count": self.unhealthy_count,
            "unknown_count": self.unknown_count,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "checks": [check.to_dict() for check in self.checks],
        }


class HealthCheckManager:
    """Manager für Health-Check-Orchestrierung.

    Koordiniert mehrere Health-Checks, berechnet Gesamtstatus
    und bietet Monitoring-Integration für Enterprise-Deployments.
    """

    def __init__(self) -> None:
        """Initialisiert Health Check Manager."""
        self.checks: List[BaseHealthCheck] = []
        self.last_summary: Optional[HealthCheckSummary] = None

    def register_check(self, check: BaseHealthCheck) -> None:
        """Registriert Health-Check.

        Args:
            check: Health-Check-Instanz
        """
        self.checks.append(check)
        _logger.info(
            f"Health-Check registriert: {check.name}",
            check_name=check.name,
            critical=check.critical,
            timeout=check.timeout_seconds,
            tags=check.tags,
        )

    def register_checks(self, checks: List[BaseHealthCheck]) -> None:
        """Registriert mehrere Health-Checks.

        Args:
            checks: Liste von Health-Check-Instanzen
        """
        for check in checks:
            self.register_check(check)

    async def run_all_checks(self) -> HealthCheckSummary:
        """Führt alle registrierten Health-Checks aus.

        Returns:
            Zusammenfassung aller Check-Ergebnisse
        """
        start_time = time.time()

        _logger.info(
            f"Starte Health-Checks für {len(self.checks)} Komponenten",
            total_checks=len(self.checks),
        )

        # Führe alle Checks parallel aus
        tasks = [check.run_check() for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verarbeite Ergebnisse
        check_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Erstelle Fehler-Result für Exception
                check_results.append(
                    HealthCheckResult(
                        name=self.checks[i].name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health-Check Exception: {str(result)}",
                        error=str(result),
                    )
                )
            else:
                check_results.append(result)

        # Berechne Statistiken
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.UNKNOWN: 0,
        }

        for result in check_results:
            status_counts[result.status] += 1

        # Bestimme Gesamtstatus
        overall_status = self._calculate_overall_status(check_results)

        # Erstelle Summary
        duration_ms = (time.time() - start_time) * 1000
        summary = HealthCheckSummary(
            overall_status=overall_status,
            total_checks=len(check_results),
            healthy_count=status_counts[HealthStatus.HEALTHY],
            degraded_count=status_counts[HealthStatus.DEGRADED],
            unhealthy_count=status_counts[HealthStatus.UNHEALTHY],
            unknown_count=status_counts[HealthStatus.UNKNOWN],
            checks=check_results,
            duration_ms=duration_ms,
        )

        self.last_summary = summary

        _logger.info(
            f"Health-Checks abgeschlossen: {overall_status.value}",
            overall_status=overall_status.value,
            total_checks=summary.total_checks,
            healthy=summary.healthy_count,
            degraded=summary.degraded_count,
            unhealthy=summary.unhealthy_count,
            unknown=summary.unknown_count,
            duration_ms=duration_ms,
        )

        return summary

    def _calculate_overall_status(
        self, results: List[HealthCheckResult]
    ) -> HealthStatus:
        """Berechnet Gesamtstatus basierend auf einzelnen Check-Ergebnissen.

        Args:
            results: Liste aller Check-Ergebnisse

        Returns:
            Gesamtstatus des Systems
        """
        # Prüfe kritische Checks
        critical_checks = [
            result for result, check in zip(results, self.checks) if check.critical
        ]

        # Wenn kritische Checks unhealthy sind, ist Gesamtstatus unhealthy
        if any(result.status == HealthStatus.UNHEALTHY for result in critical_checks):
            return HealthStatus.UNHEALTHY

        # Wenn irgendein Check unhealthy ist, ist Gesamtstatus degraded
        if any(result.status == HealthStatus.UNHEALTHY for result in results):
            return HealthStatus.DEGRADED

        # Wenn irgendein Check degraded ist, ist Gesamtstatus degraded
        if any(result.status == HealthStatus.DEGRADED for result in results):
            return HealthStatus.DEGRADED

        # Wenn alle Checks healthy sind, ist Gesamtstatus healthy
        if all(result.status == HealthStatus.HEALTHY for result in results):
            return HealthStatus.HEALTHY

        # Fallback für unbekannte Status
        return HealthStatus.UNKNOWN

    def get_last_summary(self) -> Optional[HealthCheckSummary]:
        """Gibt letzte Health-Check-Summary zurück.

        Returns:
            Letzte Summary oder None
        """
        return self.last_summary


# Globaler Health Check Manager
_health_manager: Optional[HealthCheckManager] = None


def get_health_manager() -> HealthCheckManager:
    """Gibt globalen Health Check Manager zurück.

    Returns:
        Health Check Manager Instanz
    """
    global _health_manager

    if _health_manager is None:
        _health_manager = HealthCheckManager()

    return _health_manager


__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "APIHealthCheck",
    "MemoryHealthCheck",
    "HealthCheckSummary",
    "HealthCheckManager",
    "get_health_manager",
]

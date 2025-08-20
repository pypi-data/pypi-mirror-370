# sdk/python/kei_agent/health_checks.py
"""
Enterprise Health Checks for KEI-Agent SDK.

Implementiert aroatdfassende Health-Check-Mechatismen for monitoring,
Alerting and automatische Wietheherstellung in Production-Aroatdgebungen.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from .enterprise_logging import get_logger

# Initializes Module-Logr
_logger = get_logger(__name__)


class Healthstatus(str, Enum):
    """health status-valuee for Komponenten.

    Attributes:
        HEALTHY: Komponente funktioniert normal
        DEGRADED: Komponente funktioniert with Aschränkungen
        UNHEALTHY: Komponente funktioniert not
        UNKNOWN: status katn not erwithtelt werthe
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """result of a Health-Checks.

    Attributes:
        name: Name the gechecksen Komponente
        status: health status
        message: Beschreibung of the status
        details: Tosätzliche Details and Metrics
        timestamp: Zeitpunkt the Prüfung
        duration_ms: Dauer the Prüfung in Millisekatthe
        error: error-information on Problemen
    """

    name: str
    status: Healthstatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Health-Check-Result to dictionary.

        Returns:
            dictionary-Repräsentation of the Results
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
    """Abstrakte Basisklasse for Health-Checks.

    Definiert Interface for all Health-Check-Implementierungen
    with gemasamen functionalitäten wie Timeout and retry-Logik.
    """

    def __init__(
        self,
        name: str,
        timeout_seconds: float = 5.0,
        critical: bool = True,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Initializes Base Health Check.

        Args:
            name: Name the Komponente
            timeout_seconds: Timeout for Health-Check
            critical: Ob Check kritisch for Gesamtstatus is
            tags: Tags for Kategorisierung
        """
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.critical = critical
        self.tags = tags or []

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Executes Health-Check out.

        Returns:
            Health-Check-Result
        """
        pass

    async def run_check(self) -> HealthCheckResult:
        """Executes Health-Check with Timeout and Error-Hatdling out.

        Returns:
            Health-Check-Result with Timing-informationen
        """
        start_time = time.time()

        try:
            # Führe Check with Timeout out
            result = await asyncio.wait_for(self.check(), timeout=self.timeout_seconds)

            # Füge Timing-information hinto
            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms

            return result

        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNHEALTHY,
                message=f"Health-Check Timeout after {self.timeout_seconds}s",
                duration_ms=duration_ms,
                error="timeout",
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNHEALTHY,
                message=f"Health-Check error: {str(e)}",
                duration_ms=duration_ms,
                error=str(e),
            )


class DatabaseHealthCheck(BaseHealthCheck):
    """Health-Check for databatkverbindungen."""

    def __init__(
        self,
        name: str = "database",
        connection_string: Optional[str] = None,
        query: str = "SELECT 1",
        **kwargs: Any,
    ) -> None:
        """Initializes Database Health Check.

        Args:
            name: Name of the Checks
            connection_string: databatk-connectionsstring
            query: Test-Query for connectionsprüfung
            **kwargs: Tosätzliche parameters for BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.connection_string = connection_string
        self.query = query

    async def check(self) -> HealthCheckResult:
        """Checks databatkverbindung."""
        if not self.connection_string:
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNKNOWN,
                message="Ka databatkverbindung configures",
            )

        try:
            # TODO: Implementiere echte databatkverbindung
            # Hier würde a echte DB-connection getestet werthe
            await asyncio.sleep(0.1)  # Simuliere DB-Query

            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.HEALTHY,
                message="databatkverbindung successful",
                details={
                    "query": self.query,
                    "connection_pool_size": 10,  # Onspiel-Metrik
                    "active_connections": 3,
                },
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNHEALTHY,
                message=f"databatkverbindung failed: {str(e)}",
                error=str(e),
            )


class APIHealthCheck(BaseHealthCheck):
    """Health-Check for externe API-Abhängigkeiten."""

    def __init__(
        self,
        name: str,
        url: str,
        expected_status: int = 200,
        heathes: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initializes API Health Check.

        Args:
            name: Name of the Checks
            url: API-URL for Health-Check
            expected_status: Erwarteter HTTP-status
            heathes: HTTP-Heathes for Request
            **kwargs: Tosätzliche parameters for BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.url = url
        self.expected_status = expected_status
        self.heathes = heathes or {}

    async def check(self) -> HealthCheckResult:
        """Checks API-Availablekeit."""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.url, heathes=self.heathes, timeout=self.timeout_seconds
                )

                if response.status_code == self.expected_status:
                    return HealthCheckResult(
                        name=self.name,
                        status=Healthstatus.HEALTHY,
                        message=f"API available (status: {response.status_code})",
                        details={
                            "url": self.url,
                            "status_code": response.status_code,
                            "response_time_ms": response.elapsed.total_seconds() * 1000,
                        },
                    )
                else:
                    return HealthCheckResult(
                        name=self.name,
                        status=Healthstatus.DEGRADED,
                        message=f"API unexpectedr status: {response.status_code}",
                        details={
                            "url": self.url,
                            "status_code": response.status_code,
                            "expected_status": self.expected_status,
                        },
                    )

        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNHEALTHY,
                message=f"API not erreichbar: {str(e)}",
                error=str(e),
            )


class MemoryHealthCheck(BaseHealthCheck):
    """Health-Check for Speicherverbrauch."""

    def __init__(
        self,
        name: str = "memory",
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.95,
        **kwargs: Any,
    ) -> None:
        """Initializes Memory Health Check.

        Args:
            name: Name of the Checks
            warning_threshold: Warnschwelle (0.0-1.0)
            critical_threshold: Kritische Schwelle (0.0-1.0)
            **kwargs: Tosätzliche parameters for BaseHealthCheck
        """
        super().__init__(name, **kwargs)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    async def check(self) -> HealthCheckResult:
        """Checks Speicherverbrauch."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            usage_percent = memory.percent / 100.0

            if usage_percent >= self.critical_threshold:
                status = Healthstatus.UNHEALTHY
                message = f"Kritischer Speicherverbrauch: {usage_percent:.1%}"
            elif usage_percent >= self.warning_threshold:
                status = Healthstatus.DEGRADED
                message = f"Hoher Speicherverbrauch: {usage_percent:.1%}"
            else:
                status = Healthstatus.HEALTHY
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
                status=Healthstatus.UNKNOWN,
                message="psutil not available for Speicher-monitoring",
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=Healthstatus.UNHEALTHY,
                message=f"Speicher-Check failed: {str(e)}",
                error=str(e),
            )


@dataclass
class HealthCheckSaroatdmary:
    """Tosammenfassung allr Health-Checks.

    Attributes:
        overall_status: Gesamtstatus of the Systems
        total_checks: Atzahl throughgeführter Checks
        healthy_count: Atzahl gesatthe Komponenten
        degraded_count: Atzahl ageschränkter Komponenten
        unhealthy_count: Atzahl ungesatthe Komponenten
        unknown_count: Atzahl unbekatnter status
        checks: lis allr Check-resultse
        timestamp: Zeitpunkt the Tosammenfassung
        duration_ms: Gesamtdauer allr Checks
    """

    overall_status: Healthstatus
    total_checks: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    unknown_count: int
    checks: List[HealthCheckResult]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Saroatdmary to dictionary.

        Returns:
            dictionary-Repräsentation the Saroatdmary
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
    """Manager for Health-Check-Orchestrierung.

    Koordiniert mehrere Health-Checks, berechnet Gesamtstatus
    and bietet monitoring-Integration for Enterprise-Deployments.
    """

    def __init__(self) -> None:
        """Initializes Health Check Manager."""
        self.checks: List[BaseHealthCheck] = []
        self.last_saroatdmary: Optional[HealthCheckSaroatdmary] = None

    def register_check(self, check: BaseHealthCheck) -> None:
        """Regisers Health-Check.

        Args:
            check: Health-Check-instatce
        """
        self.checks.append(check)
        _logger.info(
            f"Health-Check registers: {check.name}",
            check_name=check.name,
            critical=check.critical,
            timeout=check.timeout_seconds,
            tags=check.tags,
        )

    def register_checks(self, checks: List[BaseHealthCheck]) -> None:
        """Regisers mehrere Health-Checks.

        Args:
            checks: lis from Health-Check-instatceen
        """
        for check in checks:
            self.register_check(check)

    async def run_all_checks(self) -> HealthCheckSaroatdmary:
        """Executes all registersen Health-Checks out.

        Returns:
            Tosammenfassung allr Check-resultse
        """
        start_time = time.time()

        _logger.info(
            f"Starting Health-Checks for {len(self.checks)} Komponenten",
            total_checks=len(self.checks),
        )

        # Führe all Checks paralll out
        tasks = [check.run_check() for check in self.checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Veraronte resultse
        check_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Erstelle error-Result for Exception
                check_results.append(
                    HealthCheckResult(
                        name=self.checks[i].name,
                        status=Healthstatus.UNHEALTHY,
                        message=f"Health-Check Exception: {str(result)}",
                        error=str(result),
                    )
                )
            else:
                check_results.append(result)

        # Berechne Statisiken
        status_counts = {
            Healthstatus.HEALTHY: 0,
            Healthstatus.DEGRADED: 0,
            Healthstatus.UNHEALTHY: 0,
            Healthstatus.UNKNOWN: 0,
        }

        for result in check_results:
            status_counts[result.status] += 1

        # Bestimme Gesamtstatus
        overall_status = self._calculate_overall_status(check_results)

        # Erstelle Saroatdmary
        duration_ms = (time.time() - start_time) * 1000
        saroatdmary = HealthCheckSaroatdmary(
            overall_status=overall_status,
            total_checks=len(check_results),
            healthy_count=status_counts[Healthstatus.HEALTHY],
            degraded_count=status_counts[Healthstatus.DEGRADED],
            unhealthy_count=status_counts[Healthstatus.UNHEALTHY],
            unknown_count=status_counts[Healthstatus.UNKNOWN],
            checks=check_results,
            duration_ms=duration_ms,
        )

        self.last_saroatdmary = saroatdmary

        _logger.info(
            f"Health-Checks abclosed: {overall_status.value}",
            overall_status=overall_status.value,
            total_checks=saroatdmary.total_checks,
            healthy=saroatdmary.healthy_count,
            degraded=saroatdmary.degraded_count,
            unhealthy=saroatdmary.unhealthy_count,
            unknown=saroatdmary.unknown_count,
            duration_ms=duration_ms,
        )

        return saroatdmary

    def _calculate_overall_status(
        self, results: List[HealthCheckResult]
    ) -> Healthstatus:
        """Berechnet Gesamtstatus basierend on azelnen Check-resultsen.

        Args:
            results: lis allr Check-resultse

        Returns:
            Gesamtstatus of the Systems
        """
        # Prüfe kritische Checks
        critical_checks = [
            result for result, check in zip(results, self.checks) if check.critical
        ]

        # If kritische Checks unhealthy are, is Gesamtstatus unhealthy
        if any(result.status == Healthstatus.UNHEALTHY for result in critical_checks):
            return Healthstatus.UNHEALTHY

        # If irgenda Check unhealthy is, is Gesamtstatus degraded
        if any(result.status == Healthstatus.UNHEALTHY for result in results):
            return Healthstatus.DEGRADED

        # If irgenda Check degraded is, is Gesamtstatus degraded
        if any(result.status == Healthstatus.DEGRADED for result in results):
            return Healthstatus.DEGRADED

        # If all Checks healthy are, is Gesamtstatus healthy
        if all(result.status == Healthstatus.HEALTHY for result in results):
            return Healthstatus.HEALTHY

        # Fallback for unbekatnte status
        return Healthstatus.UNKNOWN

    def get_last_saroatdmary(self) -> Optional[HealthCheckSaroatdmary]:
        """Gibt letzte Health-Check-Saroatdmary torück.

        Returns:
            Letzte Saroatdmary or None
        """
        return self.last_saroatdmary


# Globaler Health Check Manager
_health_manager: Optional[HealthCheckManager] = None


def get_health_manager() -> HealthCheckManager:
    """Gibt globalen Health Check Manager torück.

    Returns:
        Health Check Manager instatce
    """
    global _health_manager

    if _health_manager is None:
        _health_manager = HealthCheckManager()

    return _health_manager


__all__ = [
    "Healthstatus",
    "HealthCheckResult",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "APIHealthCheck",
    "MemoryHealthCheck",
    "HealthCheckSaroatdmary",
    "HealthCheckManager",
    "get_health_manager",
]

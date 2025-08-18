# sdk/python/kei_agent_sdk/retry.py
"""
Retry-Mechanismen für KEI-Agent-Framework SDK.

Implementiert intelligente Retry-Strategien, Circuit Breaker Pattern
und Dead Letter Queue für robuste Agent-Kommunikation.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable
from collections import deque
import logging

from exceptions import RetryExhaustedError, CircuitBreakerOpenError

# Initialisiert Modul-Logger für Retry/CB
_logger = logging.getLogger("kei_agent.retry")


class RetryStrategy(str, Enum):
    """Retry-Strategien."""

    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    CUSTOM = "custom"


class CircuitBreakerState(str, Enum):
    """Circuit-Breaker-Zustände."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RetryPolicy:
    """Konfiguration für Retry-Verhalten."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF

    # Retry-Bedingungen
    retry_on_exceptions: List[type] = field(default_factory=list)
    retry_on_status_codes: List[int] = field(
        default_factory=lambda: [429, 502, 503, 504]
    )

    # Custom Retry-Funktion
    custom_retry_condition: Optional[Callable[[Exception], bool]] = None
    custom_delay_function: Optional[Callable[[int], float]] = None

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Prüft ob Retry durchgeführt werden soll.

        Args:
            exception: Aufgetretene Exception
            attempt: Aktueller Versuch (0-basiert)

        Returns:
            True wenn Retry durchgeführt werden soll
        """
        # Maximale Versuche erreicht
        if attempt >= self.max_attempts:
            return False

        # Custom Retry-Bedingung
        if self.custom_retry_condition:
            return self.custom_retry_condition(exception)

        # Exception-basierte Retry-Bedingung
        if self.retry_on_exceptions:
            return any(
                isinstance(exception, exc_type) for exc_type in self.retry_on_exceptions
            )

        # Status-Code-basierte Retry-Bedingung (für HTTP-Fehler)
        if hasattr(exception, "status_code"):
            return exception.status_code in self.retry_on_status_codes

        # Default: Retry bei allen Exceptions
        return True

    def calculate_delay(self, attempt: int) -> float:
        """Berechnet Delay für Retry-Versuch.

        Args:
            attempt: Aktueller Versuch (0-basiert)

        Returns:
            Delay in Sekunden
        """
        if self.custom_delay_function:
            delay = self.custom_delay_function(attempt)
        elif self.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (self.exponential_base**attempt)
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * (attempt + 1)
        elif self.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = self.base_delay * self._fibonacci(attempt + 1)
        else:
            delay = self.base_delay

        # Max-Delay begrenzen
        delay = min(delay, self.max_delay)

        # Jitter hinzufügen
        if self.jitter:
            import secrets

            jitter_range = delay * 0.1  # 10% Jitter
            # Verwende kryptographisch sicheren Random für Jitter
            jitter_factor = (secrets.randbelow(2000) - 1000) / 10000.0  # -0.1 bis 0.1
            delay += jitter_range * jitter_factor

        return max(0.0, delay)

    def _fibonacci(self, n: int) -> int:
        """Berechnet Fibonacci-Zahl.

        Args:
            n: Position in Fibonacci-Sequenz

        Returns:
            Fibonacci-Zahl
        """
        if n <= 1:
            return n

        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b

        return b


@dataclass
class CircuitBreakerConfig:
    """Konfiguration für Circuit Breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

    # Failure-Detection
    failure_rate_threshold: float = 0.5  # 50% Fehlerrate
    minimum_throughput: int = 10  # Mindest-Requests für Bewertung

    # Monitoring
    sliding_window_size: int = 100
    sliding_window_type: str = "count"  # count, time

    # Callbacks
    on_state_change: Optional[
        Callable[[CircuitBreakerState, CircuitBreakerState], Awaitable[None]]
    ] = None
    on_call_rejected: Optional[Callable[[], Awaitable[None]]] = None


class CircuitBreaker:
    """Circuit Breaker für Fehlerbehandlung."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        """Initialisiert Circuit Breaker.

        Args:
            name: Name des Circuit Breakers
            config: Circuit-Breaker-Konfiguration
        """
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED

        # Failure-Tracking
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0

        # Sliding Window für Failure-Rate
        self._call_history: deque = deque(maxlen=config.sliding_window_size)

        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._state_changes = 0

    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Führt Funktion mit Circuit-Breaker-Schutz aus.

        Args:
            func: Auszuführende Funktion
            *args: Funktions-Argumente
            **kwargs: Funktions-Keyword-Argumente

        Returns:
            Funktions-Ergebnis

        Raises:
            CircuitBreakerOpenError: Wenn Circuit Breaker offen ist
        """
        # Prüfe Circuit-Breaker-Status
        if not await self._can_execute():
            if self.config.on_call_rejected:
                await self.config.on_call_rejected()

            raise CircuitBreakerOpenError(
                f"Circuit Breaker '{self.name}' ist offen. "
                f"Nächster Versuch in {self._time_until_retry():.1f}s"
            )

        self._total_calls += 1

        try:
            # Führe Funktion aus
            result = await func(*args, **kwargs)

            # Erfolgreicher Call
            await self._on_success()

            return result

        except Exception:
            # Fehlgeschlagener Call
            await self._on_failure()
            raise

    async def _can_execute(self) -> bool:
        """Prüft ob Ausführung erlaubt ist.

        Returns:
            True wenn Ausführung erlaubt
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Prüfe ob Recovery-Timeout erreicht
            if time.time() - self._last_failure_time >= self.config.recovery_timeout:
                await self._transition_to_half_open()
                return True
            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Erlaube begrenzte Anzahl von Calls
            return self._half_open_calls < self.config.half_open_max_calls

        return False

    async def _on_success(self) -> None:
        """Behandelt erfolgreichen Call."""
        self._success_count += 1
        self._call_history.append(True)  # True = Erfolg

        if self.state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls += 1

            # Wenn genug erfolgreiche Calls, schließe Circuit Breaker
            if self._half_open_calls >= self.config.half_open_max_calls:
                await self._transition_to_closed()

        elif self.state == CircuitBreakerState.CLOSED:
            # Reset Failure-Counter bei Erfolg
            self._failure_count = 0

    async def _on_failure(self) -> None:
        """Behandelt fehlgeschlagenen Call."""
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.time()
        self._call_history.append(False)  # False = Fehler

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Bei Fehler in Half-Open zurück zu Open
            await self._transition_to_open()

        elif self.state == CircuitBreakerState.CLOSED:
            # Prüfe ob Failure-Threshold erreicht
            if self._should_open():
                await self._transition_to_open()

    def _should_open(self) -> bool:
        """Prüft ob Circuit Breaker geöffnet werden soll.

        Returns:
            True wenn Circuit Breaker geöffnet werden soll
        """
        # Einfache Failure-Count-Prüfung
        if self._failure_count >= self.config.failure_threshold:
            return True

        # Failure-Rate-Prüfung (wenn genug Calls vorhanden)
        if len(self._call_history) >= self.config.minimum_throughput:
            failure_rate = sum(
                1 for success in self._call_history if not success
            ) / len(self._call_history)
            return failure_rate >= self.config.failure_rate_threshold

        return False

    async def _transition_to_open(self) -> None:
        """Übergang zu OPEN-Status."""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self._state_changes += 1

        if self.config.on_state_change:
            await self.config.on_state_change(old_state, self.state)

    async def _transition_to_half_open(self) -> None:
        """Übergang zu HALF_OPEN-Status."""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        self._half_open_calls = 0
        self._state_changes += 1

        if self.config.on_state_change:
            await self.config.on_state_change(old_state, self.state)

    async def _transition_to_closed(self) -> None:
        """Übergang zu CLOSED-Status."""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._state_changes += 1

        if self.config.on_state_change:
            await self.config.on_state_change(old_state, self.state)

    def _time_until_retry(self) -> float:
        """Berechnet Zeit bis zum nächsten Retry-Versuch.

        Returns:
            Zeit in Sekunden
        """
        if self.state == CircuitBreakerState.OPEN:
            elapsed = time.time() - self._last_failure_time
            return max(0.0, self.config.recovery_timeout - elapsed)

        return 0.0

    def get_metrics(self) -> Dict[str, Any]:
        """Holt Circuit-Breaker-Metriken.

        Returns:
            Circuit-Breaker-Metriken
        """
        failure_rate = (
            self._total_failures / max(self._total_calls, 1)
            if self._total_calls > 0
            else 0.0
        )

        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "failure_rate": failure_rate,
            "current_failure_count": self._failure_count,
            "time_until_retry": self._time_until_retry(),
            "state_changes": self._state_changes,
            "half_open_calls": self._half_open_calls,
        }


@dataclass
class DeadLetterMessage:
    """Nachricht in Dead Letter Queue."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_payload: Dict[str, Any] = field(default_factory=dict)
    failure_reason: str = ""
    failure_count: int = 0
    first_failure_time: float = field(default_factory=time.time)
    last_failure_time: float = field(default_factory=time.time)

    # Retry-Informationen
    max_retries_reached: bool = False
    circuit_breaker_open: bool = False

    # Metadaten
    source_agent: str = ""
    target_agent: str = ""
    operation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "message_id": self.message_id,
            "original_payload": self.original_payload,
            "failure_reason": self.failure_reason,
            "failure_count": self.failure_count,
            "first_failure_time": self.first_failure_time,
            "last_failure_time": self.last_failure_time,
            "max_retries_reached": self.max_retries_reached,
            "circuit_breaker_open": self.circuit_breaker_open,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "operation": self.operation,
        }


class DeadLetterQueue:
    """Dead Letter Queue für fehlgeschlagene Nachrichten."""

    def __init__(self, max_size: int = 1000):
        """Initialisiert Dead Letter Queue.

        Args:
            max_size: Maximale Queue-Größe
        """
        self.max_size = max_size
        self._messages: Dict[str, DeadLetterMessage] = {}
        self._message_order: deque = deque()

        # Callbacks
        self.on_message_added: Optional[
            Callable[[DeadLetterMessage], Awaitable[None]]
        ] = None
        self.on_queue_full: Optional[Callable[[int], Awaitable[None]]] = None

    async def add_message(
        self,
        payload: Dict[str, Any],
        failure_reason: str,
        source_agent: str = "",
        target_agent: str = "",
        operation: str = "",
    ) -> str:
        """Fügt Nachricht zur Dead Letter Queue hinzu.

        Args:
            payload: Original-Payload
            failure_reason: Grund für Fehler
            source_agent: Quell-Agent
            target_agent: Ziel-Agent
            operation: Operation

        Returns:
            Message-ID
        """
        message = DeadLetterMessage(
            original_payload=payload,
            failure_reason=failure_reason,
            source_agent=source_agent,
            target_agent=target_agent,
            operation=operation,
        )

        # Prüfe Queue-Größe
        if len(self._messages) >= self.max_size:
            # Entferne älteste Nachricht
            oldest_id = self._message_order.popleft()
            del self._messages[oldest_id]

            if self.on_queue_full:
                await self.on_queue_full(self.max_size)

        # Füge neue Nachricht hinzu
        self._messages[message.message_id] = message
        self._message_order.append(message.message_id)

        if self.on_message_added:
            await self.on_message_added(message)

        return message.message_id

    def get_message(self, message_id: str) -> Optional[DeadLetterMessage]:
        """Holt Nachricht aus Queue.

        Args:
            message_id: Message-ID

        Returns:
            Dead-Letter-Message oder None
        """
        return self._messages.get(message_id)

    def list_messages(
        self,
        limit: int = 100,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
    ) -> List[DeadLetterMessage]:
        """Listet Nachrichten in Queue auf.

        Args:
            limit: Maximale Anzahl Nachrichten
            source_agent: Filter nach Quell-Agent
            target_agent: Filter nach Ziel-Agent

        Returns:
            Liste von Dead-Letter-Messages
        """
        messages = []

        for message_id in reversed(self._message_order):
            if len(messages) >= limit:
                break

            message = self._messages[message_id]

            # Filter anwenden
            if source_agent and message.source_agent != source_agent:
                continue

            if target_agent and message.target_agent != target_agent:
                continue

            messages.append(message)

        return messages

    def remove_message(self, message_id: str) -> bool:
        """Entfernt Nachricht aus Queue.

        Args:
            message_id: Message-ID

        Returns:
            True wenn Nachricht entfernt wurde
        """
        if message_id in self._messages:
            del self._messages[message_id]

            # Entferne aus Order-Queue
            try:
                self._message_order.remove(message_id)
            except ValueError:
                pass  # Bereits entfernt

            return True

        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Holt Dead-Letter-Queue-Metriken.

        Returns:
            DLQ-Metriken
        """
        return {
            "total_messages": len(self._messages),
            "max_size": self.max_size,
            "utilization": len(self._messages) / self.max_size,
            "oldest_message_age": (
                time.time()
                - min(msg.first_failure_time for msg in self._messages.values())
                if self._messages
                else 0.0
            ),
        }


class RetryManager:
    """Manager für Retry-Mechanismen."""

    def __init__(self, config):
        """Initialisiert Retry-Manager.

        Args:
            config: Retry-Konfiguration
        """
        self.config = config

        # Circuit Breakers
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Dead Letter Queue
        self._dead_letter_queue = DeadLetterQueue()

        # Default Retry-Policy
        self._default_policy = RetryPolicy(
            max_attempts=config.max_attempts,
            base_delay=config.base_delay,
            max_delay=config.max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            strategy=getattr(config, "strategy", RetryStrategy.EXPONENTIAL_BACKOFF),
        )

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Holt oder erstellt Circuit Breaker.

        Args:
            name: Circuit-Breaker-Name

        Returns:
            Circuit Breaker
        """
        if name not in self._circuit_breakers:
            cb_config = CircuitBreakerConfig(
                failure_threshold=self.config.failure_threshold,
                recovery_timeout=self.config.recovery_timeout,
                half_open_max_calls=self.config.half_open_max_calls,
            )

            self._circuit_breakers[name] = CircuitBreaker(name, cb_config)
            _logger.info(
                "Circuit Breaker initialisiert: %s (threshold=%s, recovery=%ss, half_open=%s)",
                name,
                cb_config.failure_threshold,
                cb_config.recovery_timeout,
                cb_config.half_open_max_calls,
            )

        return self._circuit_breakers[name]

    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Führt Funktion mit Retry-Mechanismus aus.

        Args:
            func: Auszuführende Funktion
            *args: Funktions-Argumente
            retry_policy: Retry-Policy (optional)
            circuit_breaker_name: Circuit-Breaker-Name (optional)
            **kwargs: Funktions-Keyword-Argumente

        Returns:
            Funktions-Ergebnis

        Raises:
            RetryExhaustedError: Bei erschöpften Retry-Versuchen
        """
        policy = retry_policy or self._default_policy
        last_exception = None

        # Circuit Breaker verwenden falls angegeben (mit Retry-Schleife kombiniert)
        if circuit_breaker_name and self.config.circuit_breaker_enabled:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_name)
            _logger.info("Circuit Breaker verwendet: %s", circuit_breaker_name)

            # Protokoll und Operation für Logs extrahieren
            proto, op = ("", circuit_breaker_name)
            if "." in circuit_breaker_name:
                proto, op = circuit_breaker_name.split(".", 1)

            for attempt in range(policy.max_attempts):
                try:
                    return await circuit_breaker.call(func, *args, **kwargs)
                except CircuitBreakerOpenError:
                    # Circuit Breaker offen - füge zu Dead Letter Queue hinzu
                    await self._dead_letter_queue.add_message(
                        payload={"args": args, "kwargs": kwargs},
                        failure_reason="Circuit Breaker Open",
                        operation=circuit_breaker_name,
                    )
                    _logger.warning(
                        "Circuit Breaker offen: %s - Aufruf verworfen und in DLQ verschoben",
                        circuit_breaker_name,
                    )
                    raise
                except Exception as e:
                    last_exception = e

                    # Prüfe ob Retry durchgeführt werden soll
                    if not policy.should_retry(e, attempt):
                        _logger.debug(
                            "Kein Retry nach Versuch %d für Protokoll '%s' Operation '%s': %s",
                            attempt + 1,
                            proto,
                            op,
                            repr(e),
                        )
                        break

                    # Letzter Versuch - kein weiterer Retry
                    if attempt >= policy.max_attempts - 1:
                        _logger.debug(
                            "Letzter Versuch %d erreicht (Protokoll '%s' Operation '%s'), kein weiterer Retry",
                            attempt + 1,
                            proto,
                            op,
                        )
                        break

                    # Warte vor nächstem Versuch
                    delay = policy.calculate_delay(attempt)
                    _logger.debug(
                        "Retry-Versuch %d/%d für Protokoll '%s' Operation '%s' (Delay=%.3fs): %s",
                        attempt + 2,
                        policy.max_attempts,
                        proto,
                        op,
                        delay,
                        repr(e),
                    )
                    await asyncio.sleep(delay)

            # Alle Retry-Versuche erschöpft - füge zu Dead Letter Queue hinzu
            await self._dead_letter_queue.add_message(
                payload={"args": args, "kwargs": kwargs},
                failure_reason=f"Max retries exceeded: {last_exception}",
                operation=circuit_breaker_name,
            )
            raise RetryExhaustedError(
                f"Funktion nach {policy.max_attempts} Versuchen fehlgeschlagen",
                last_exception=last_exception,
            )

        # Standard-Retry-Mechanismus ohne Circuit Breaker
        for attempt in range(policy.max_attempts):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Prüfe ob Retry durchgeführt werden soll
                if not policy.should_retry(e, attempt):
                    _logger.debug(
                        "Kein Retry nach Versuch %d: %s", attempt + 1, repr(e)
                    )
                    break

                # Letzter Versuch - kein weiterer Retry
                if attempt >= policy.max_attempts - 1:
                    _logger.debug(
                        "Letzter Versuch %d erreicht, kein weiterer Retry", attempt + 1
                    )
                    break

                # Warte vor nächstem Versuch
                delay = policy.calculate_delay(attempt)
                _logger.debug(
                    "Retry-Versuch %d/%d (Delay=%.3fs): %s",
                    attempt + 2,
                    policy.max_attempts,
                    delay,
                    repr(e),
                )
                await asyncio.sleep(delay)

        # Alle Retry-Versuche erschöpft - füge zu Dead Letter Queue hinzu
        await self._dead_letter_queue.add_message(
            payload={"args": args, "kwargs": kwargs},
            failure_reason=f"Max retries exceeded: {last_exception}",
            operation=func.__name__ if hasattr(func, "__name__") else "unknown",
        )

        raise RetryExhaustedError(
            f"Funktion nach {policy.max_attempts} Versuchen fehlgeschlagen",
            last_exception=last_exception,
        )

    def get_dead_letter_queue(self) -> DeadLetterQueue:
        """Holt Dead Letter Queue.

        Returns:
            Dead Letter Queue
        """
        return self._dead_letter_queue

    def get_metrics(self) -> Dict[str, Any]:
        """Holt Retry-Manager-Metriken.

        Returns:
            Retry-Metriken
        """
        circuit_breaker_metrics = {
            name: cb.get_metrics() for name, cb in self._circuit_breakers.items()
        }

        return {
            "circuit_breakers": circuit_breaker_metrics,
            "dead_letter_queue": self._dead_letter_queue.get_metrics(),
            "default_policy": {
                "max_attempts": self._default_policy.max_attempts,
                "base_delay": self._default_policy.base_delay,
                "strategy": self._default_policy.strategy.value,
            },
        }

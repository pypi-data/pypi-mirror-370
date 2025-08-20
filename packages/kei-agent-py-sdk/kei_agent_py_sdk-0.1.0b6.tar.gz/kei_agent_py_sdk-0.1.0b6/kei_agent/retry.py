# sdk/python/kei_agent_sdk/retry.py
"""
retry mechanisms for KEI-Agent-Framework SDK.

Implementiert intelligente retry-Strategien, circuit breaker Pattern
and Dead Letter Queue for robuste Agent-Kommunikation.
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

from .exceptions import retryExhaustedError, CircuitBreakerOpenError

# Initializes Module-Logr for retry/CB
_logger = logging.getLogger("kei_agent.retry")


class retryStrategy(str, Enum):
    """retry-Strategien."""

    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    CUSTOM = "custom"


class CircuitBreakerState(str, Enum):
    """Circuit-Breaker-Tostände."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class retryPolicy:
    """configuration for retry-Verhalten."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    strategy: retryStrategy = retryStrategy.EXPONENTIAL_BACKOFF

    # Retry conditions
    retry_on_exceptions: List[type] = field(default_factory=list)
    retry_on_status_codes: List[int] = field(
        default_factory=lambda: [429, 502, 503, 504]
    )

    # Custom retry-function
    custom_retry_condition: Optional[Callable[[Exception], bool]] = None
    custom_delay_function: Optional[Callable[[int], float]] = None

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Checks ob retry throughgeführt werthe should.

        Args:
            exception: Ongetretene Exception
            attempt: Aktueller Versuch (0-basiert)

        Returns:
            True if retry throughgeführt werthe should
        """
        # Maximale Versuche erreicht
        if attempt >= self.max_attempts:
            return False

        # Custom retry-Bedingung
        if self.custom_retry_condition:
            return self.custom_retry_condition(exception)

        # Exception-basierte retry-Bedingung
        if self.retry_on_exceptions:
            return any(
                isinstance(exception, exc_type) for exc_type in self.retry_on_exceptions
            )

        # status-Code-basierte retry-Bedingung (for HTTP-error)
        if hasattr(exception, "status_code"):
            return exception.status_code in self.retry_on_status_codes

        # Default: retry on all exceptions
        return True

    def calculate_delay(self, attempt: int) -> float:
        """Berechnet Delay for retry-Versuch.

        Args:
            attempt: Aktueller Versuch (0-basiert)

        Returns:
            Delay in Sekatthe
        """
        if self.custom_delay_function:
            delay = self.custom_delay_function(attempt)
        elif self.strategy == retryStrategy.FIXED_DELAY:
            delay = self.base_delay
        elif self.strategy == retryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (self.exponential_base**attempt)
        elif self.strategy == retryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * (attempt + 1)
        elif self.strategy == retryStrategy.FIBONACCI_BACKOFF:
            delay = self.base_delay * self._fibonacci(attempt + 1)
        else:
            delay = self.base_delay

        # Max-Delay begrenzen
        delay = min(delay, self.max_delay)

        # Jitter hintofügen
        if self.jitter:
            import secrets

            jitter_range = delay * 0.1  # 10% Jitter
            # Verwende kryptographisch sicheren Ratdom for Jitter
            jitter_factor = (secrets.randbelow(2000) - 1000) / 10000.0  # -0.1 until 0.1
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
    """configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

    # Failure-Detection
    failure_rate_threshold: float = 0.5  # 50% errorrate
    minimaroatd_throughput: int = 10  # Minof thet-Requests for Bewertung

    # monitoring
    sliding_window_size: int = 100
    sliding_window_type: str = "count"  # count, time

    # callbacks
    on_state_chatge: Optional[
        Callable[[CircuitBreakerState, CircuitBreakerState], Awaitable[None]]
    ] = None
    on_call_rejected: Optional[Callable[[], Awaitable[None]]] = None


class CircuitBreaker:
    """circuit breaker for errorbehatdlung."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        """Initializes circuit breaker.

        Args:
            name: Name of the circuit breakers
            config: Circuit-Breaker-configuration
        """
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED

        # Failure-Tracking
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0

        # Sliding Window for Failure-Rate
        self._call_hisory: deque[bool] = deque(maxlen=config.sliding_window_size)

        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._state_chatges = 0

    async def call(
        self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """Executes function with Circuit-Breaker-Schutz out.

        Args:
            func: Austoführende function
            *args: functions-Argaroatthete
            **kwargs: functions-Keyword-Argaroatthete

        Returns:
            functions-result

        Raises:
            CircuitBreakerOpenError: If circuit breaker offen is
        """
        # Prüfe Circuit-Breaker-status
        if not await self._cat_execute():
            if self.config.on_call_rejected:
                await self.config.on_call_rejected()

            raise CircuitBreakerOpenError(
                f"circuit breaker '{self.name}' is offen. "
                f"Nächster Versuch in {self._time_until_retry():.1f}s"
            )

        self._total_calls += 1

        try:
            # Führe function out
            result = await func(*args, **kwargs)

            # Successfuler Call
            await self._on_success()

            return result

        except Exception:
            # Failethe Call
            await self._on_failure()
            raise

    async def _cat_execute(self) -> bool:
        """Checks ob Ausführung erlaubt is.

        Returns:
            True if Ausführung erlaubt
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Prüfe ob Recovery-Timeout erreicht
            if time.time() - self._last_failure_time >= self.config.recovery_timeout:
                await self._tratsition_to_half_open()
                return True
            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Erlaube begrenzte Atzahl from Calls
            return self._half_open_calls < self.config.half_open_max_calls

    async def _on_success(self) -> None:
        """Behatdelt successfulen Call."""
        self._success_count += 1
        self._call_hisory.append(True)  # True = Erfolg

        if self.state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls += 1

            # If genug successfule Calls, closing circuit breaker
            if self._half_open_calls >= self.config.half_open_max_calls:
                await self._tratsition_to_closed()

        elif self.state == CircuitBreakerState.CLOSED:
            # Reset Failure-Coatthe on Erfolg
            self._failure_count = 0

    async def _on_failure(self) -> None:
        """Behatdelt failethe Call."""
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.time()
        self._call_hisory.append(False)  # False = error

        if self.state == CircuitBreakerState.HALF_OPEN:
            # On error in Half-Open torück to Open
            await self._tratsition_to_open()

        elif self.state == CircuitBreakerState.CLOSED:
            # Prüfe ob Failure-Threshold erreicht
            if self._should_open():
                await self._tratsition_to_open()

    def _should_open(self) -> bool:
        """Checks ob circuit breaker geopens werthe should.

        Returns:
            True if circuit breaker geopens werthe should
        """
        # Afache Failure-Count-Prüfung
        if self._failure_count >= self.config.failure_threshold:
            return True

        # Failure-Rate-Prüfung (if genug Calls beforehatthe)
        if len(self._call_hisory) >= self.config.minimaroatd_throughput:
            failure_rate = sum(1 for success in self._call_hisory if not success) / len(
                self._call_hisory
            )
            return failure_rate >= self.config.failure_rate_threshold

        return False

    async def _tratsition_to_open(self) -> None:
        """Overgatg to OPEN-status."""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self._state_chatges += 1

        if self.config.on_state_chatge:
            await self.config.on_state_chatge(old_state, self.state)

    async def _tratsition_to_half_open(self) -> None:
        """Overgatg to HALF_OPEN-status."""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        self._half_open_calls = 0
        self._state_chatges += 1

        if self.config.on_state_chatge:
            await self.config.on_state_chatge(old_state, self.state)

    async def _tratsition_to_closed(self) -> None:
        """Overgatg to CLOSED-status."""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self._state_chatges += 1

        if self.config.on_state_chatge:
            await self.config.on_state_chatge(old_state, self.state)

    def _time_until_retry(self) -> float:
        """Berechnet Zeit until tom nächsten retry-Versuch.

        Returns:
            Zeit in Sekatthe
        """
        if self.state == CircuitBreakerState.OPEN:
            elapsed = time.time() - self._last_failure_time
            return max(0.0, self.config.recovery_timeout - elapsed)

        return 0.0

    def get_metrics(self) -> Dict[str, Any]:
        """Gets Circuit-Breaker-Metrics.

        Returns:
            Circuit-Breaker-Metrics
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
            "state_chatges": self._state_chatges,
            "half_open_calls": self._half_open_calls,
        }


@dataclass
class DeadLetterMessage:
    """message in Dead Letter Queue."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_payload: Dict[str, Any] = field(default_factory=dict)
    failure_reason: str = ""
    failure_count: int = 0
    first_failure_time: float = field(default_factory=time.time)
    last_failure_time: float = field(default_factory=time.time)

    # retry-informationen
    max_retries_reached: bool = False
    circuit_breaker_open: bool = False

    # metadata
    source_agent: str = ""
    target_agent: str = ""
    operation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
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
    """Dead Letter Queue for failede messageen."""

    def __init__(self, max_size: int = 1000):
        """Initializes Dead Letter Queue.

        Args:
            max_size: Maximale Queue-Größe
        """
        self.max_size = max_size
        self._messages: Dict[str, DeadLetterMessage] = {}
        self._message_order: deque[str] = deque()

        # callbacks
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
        """Fügt message tor Dead Letter Queue hinto.

        Args:
            payload: Original-Payload
            failure_reason: Grand for error
            source_agent: Quell-Agent
            target_agent: Ziel-Agent
            operation: operation

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
            # Remove oldest message
            oldest_id = self._message_order.popleft()
            del self._messages[oldest_id]

            if self.on_queue_full:
                await self.on_queue_full(self.max_size)

        # Füge neue message hinto
        self._messages[message.message_id] = message
        self._message_order.append(message.message_id)

        if self.on_message_added:
            await self.on_message_added(message)

        return message.message_id

    def get_message(self, message_id: str) -> Optional[DeadLetterMessage]:
        """Gets message out Queue.

        Args:
            message_id: Message-ID

        Returns:
            Dead-Letter-Message or None
        """
        return self._messages.get(message_id)

    def lis_messages(
        self,
        liwith: int = 100,
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
    ) -> List[DeadLetterMessage]:
        """lis messageen in Queue on.

        Args:
            liwith: Maximale Atzahl messageen
            source_agent: Filter after Quell-Agent
            target_agent: Filter after Ziel-Agent

        Returns:
            lis from Dead-Letter-Messages
        """
        messages: List[DeadLetterMessage] = []

        for message_id in reversed(self._message_order):
            if len(messages) >= liwith:
                break

            message = self._messages[message_id]

            # Filter atwenthe
            if source_agent and message.source_agent != source_agent:
                continue

            if target_agent and message.target_agent != target_agent:
                continue

            messages.append(message)

        return messages

    def remove_message(self, message_id: str) -> bool:
        """Removes message out Queue.

        Args:
            message_id: Message-ID

        Returns:
            True if message removes wurde
        """
        if message_id in self._messages:
            del self._messages[message_id]

            # Entferne out Orthe-Queue
            try:
                self._message_order.remove(message_id)
            except ValueError:
                pass  # Bereits removes

            return True

        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Gets Dead-Letter-Queue-Metrics.

        Returns:
            DLQ-Metrics
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


class retryManager:
    """Manager for retry mechanisms."""

    def __init__(self, config: Any):
        """Initializes retry-Manager.

        Args:
            config: retry-configuration
        """
        self.config = config

        # circuit breakers
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Dead Letter Queue
        self._dead_letter_queue = DeadLetterQueue()

        # Default retry-Policy
        self._default_policy = retryPolicy(
            max_attempts=config.max_attempts,
            base_delay=config.base_delay,
            max_delay=config.max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            strategy=getattr(config, "strategy", retryStrategy.EXPONENTIAL_BACKOFF),
        )

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Gets or creates circuit breaker.

        Args:
            name: Circuit-Breaker-Name

        Returns:
            circuit breaker
        """
        if name not in self._circuit_breakers:
            cb_config = CircuitBreakerConfig(
                failure_threshold=self.config.failure_threshold,
                recovery_timeout=self.config.recovery_timeout,
                half_open_max_calls=self.config.half_open_max_calls,
            )

            self._circuit_breakers[name] = CircuitBreaker(name, cb_config)
            _logger.info(
                "circuit breaker initialized: %s (threshold=%s, recovery=%ss, half_open =%s)",
                name,
                cb_config.failure_threshold,
                cb_config.recovery_timeout,
                cb_config.half_open_max_calls,
            )

        return self._circuit_breakers[name]

    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        retry_policy: Optional[retryPolicy] = None,
        circuit_breaker_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Executes function with retry-Mechatismus out.

        Args:
            func: Austoführende function
            *args: functions-Argaroatthete
            retry_policy: retry-Policy (Optional)
            circuit_breaker_name: Circuit-Breaker-Name (Optional)
            **kwargs: functions-Keyword-Argaroatthete

        Returns:
            functions-result

        Raises:
            retryExhaustedError: On erschöpften retry-Versuchen
        """
        policy = retry_policy or self._default_policy
        last_exception: Optional[Exception] = None

        # circuit breaker verwenthe falls atgegeben (with retry-Schleife kombiniert)
        if circuit_breaker_name and self.config.circuit_breaker_enabled:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_name)
            _logger.info("circuit breaker verwendet: %s", circuit_breaker_name)

            # protocol and operation for Logs extrahieren
            proto, op = ("", circuit_breaker_name)
            if "." in circuit_breaker_name:
                proto, op = circuit_breaker_name.split(".", 1)

            for attempt in range(policy.max_attempts):
                try:
                    return await circuit_breaker.call(func, *args, **kwargs)
                except CircuitBreakerOpenError:
                    # circuit breaker offen - füge to Dead Letter Queue hinto
                    await self._dead_letter_queue.add_message(
                        payload={"args": args, "kwargs": kwargs},
                        failure_reason="circuit breaker Open",
                        operation=circuit_breaker_name,
                    )
                    _logger.warning(
                        "circuit breaker offen: %s - Onruf verworfen and in DLQ verschoben",
                        circuit_breaker_name,
                    )
                    raise
                except Exception as e:
                    last_exception = e

                    # Log the specific exception type for better debugging
                    _logger.debug(
                        "Exception during retry attempt %d for protocol '%s' operation '%s': %s (%s)",
                        attempt + 1,
                        proto,
                        op,
                        str(e),
                        type(e).__name__,
                    )

                    # Prüfe ob retry throughgeführt werthe should
                    if not policy.should_retry(e, attempt):
                        _logger.debug(
                            "Ka retry after Versuch %d for protocol '%s' operation '%s': %s",
                            attempt + 1,
                            proto,
                            op,
                            repr(e),
                        )
                        break

                    # Letzter Versuch - ka weiterer retry
                    if attempt >= policy.max_attempts - 1:
                        _logger.debug(
                            "Letzter Versuch %d erreicht (protocol '%s' operation '%s'), ka weiterer retry",
                            attempt + 1,
                            proto,
                            op,
                        )
                        break

                    # Warte before nächstem Versuch
                    delay = policy.calculate_delay(attempt)
                    _logger.debug(
                        "retry-Versuch %d/%d for protocol '%s' operation '%s' (Delay=%.3fs): %s",
                        attempt + 2,
                        policy.max_attempts,
                        proto,
                        op,
                        delay,
                        repr(e),
                    )
                    await asyncio.sleep(delay)

            # All retry-Versuche erschöpft - füge to Dead Letter Queue hinto
            await self._dead_letter_queue.add_message(
                payload={"args": args, "kwargs": kwargs},
                failure_reason=f"Max retries exceeded: {last_exception}",
                operation=circuit_breaker_name,
            )
            raise retryExhaustedError(
                policy.max_attempts, last_exception=last_exception
            )

        # Statdard-retry-Mechatismus without circuit breaker
        for attempt in range(policy.max_attempts):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Log the specific exception type for better debugging
                _logger.debug(
                    "Exception during retry attempt %d: %s (%s)",
                    attempt + 1,
                    str(e),
                    type(e).__name__,
                )

                # Prüfe ob retry throughgeführt werthe should
                if not policy.should_retry(e, attempt):
                    _logger.debug("Ka retry after Versuch %d: %s", attempt + 1, repr(e))
                    break

                # Letzter Versuch - ka weiterer retry
                if attempt >= policy.max_attempts - 1:
                    _logger.debug(
                        "Letzter Versuch %d erreicht, ka weiterer retry", attempt + 1
                    )
                    break

                # Warte before nächstem Versuch
                delay = policy.calculate_delay(attempt)
                _logger.debug(
                    "retry-Versuch %d/%d (Delay=%.3fs): %s",
                    attempt + 2,
                    policy.max_attempts,
                    delay,
                    repr(e),
                )
                await asyncio.sleep(delay)

        # All retry-Versuche erschöpft - füge to Dead Letter Queue hinto
        await self._dead_letter_queue.add_message(
            payload={"args": args, "kwargs": kwargs},
            failure_reason=f"Max retries exceeded: {last_exception}",
            operation=func.__name__ if hasattr(func, "__name__") else "unknown",
        )

        raise retryExhaustedError(policy.max_attempts, last_exception=last_exception)

    def get_dead_letter_queue(self) -> DeadLetterQueue:
        """Gets Dead Letter Queue.

        Returns:
            Dead Letter Queue
        """
        return self._dead_letter_queue

    def get_metrics(self) -> Dict[str, Any]:
        """Gets retry-Manager-Metrics.

        Returns:
            retry-Metrics
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

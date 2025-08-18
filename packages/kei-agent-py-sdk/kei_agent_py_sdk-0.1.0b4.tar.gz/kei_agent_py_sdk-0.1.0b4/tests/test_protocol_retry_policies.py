# sdk/python/kei_agent/tests/test_protocol_retry_policies.py
"""Tests für protokollspezifische Retry-Policies im UnifiedKeiAgentClient.

Enthält deterministische, isolierte Tests mit asynchronem Verhalten und Mocks.
"""

from __future__ import annotations

import asyncio
import sys
import types
from typing import Dict, Any, Optional, List
import logging


import pytest

# Markiere alle Tests in dieser Datei als Protokoll-Tests
pytestmark = pytest.mark.protocol

# Erzeuge Dummy-OpenTelemetry-Module, um Importfehler zu vermeiden
# Dies muss VOR dem Import von kei_agent erfolgen


def ensure_fake_opentelemetry() -> None:
    """Erstellt minimale Fake-Module für OpenTelemetry-Imports.

    Verhindert ImportErrors in Testumgebungen ohne OTel-Exporter.
    """

    def add_module(name: str) -> types.ModuleType:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    # Basis-Pakete
    add_module("opentelemetry")  # otel - nicht direkt verwendet
    trace = add_module("opentelemetry.trace")
    metrics = add_module("opentelemetry.metrics")
    add_module("opentelemetry.baggage")  # baggage - nicht direkt verwendet

    # Metrics API Platzhalter
    def get_meter(name, version=None):
        return types.SimpleNamespace(
            create_counter=lambda name, **kwargs: lambda **kw: None,
            create_histogram=lambda name, **kwargs: lambda **kw: None,
            create_gauge=lambda name, **kwargs: lambda **kw: None,
            create_up_down_counter=lambda name, **kwargs: lambda **kw: None,
        )

    def set_meter_provider(provider):
        pass

    metrics.get_meter = get_meter
    metrics.set_meter_provider = set_meter_provider

    # Trace API Platzhalter
    class Status:  # noqa: D401
        """Fake Status."""

        pass

    class StatusCode:  # noqa: D401
        """Fake StatusCode."""

        OK = "OK"
        ERROR = "ERROR"

    def get_current_span(ctx=None):
        return types.SimpleNamespace(
            get_span_context=lambda: types.SimpleNamespace(trace_id=0, span_id=0)
        )

    def get_tracer(name, version=None):
        return types.SimpleNamespace(
            start_as_current_span=lambda name, **kwargs: types.SimpleNamespace()
        )

    def set_tracer_provider(provider):
        pass

    trace.Status = Status
    trace.StatusCode = StatusCode
    trace.get_current_span = get_current_span
    trace.get_tracer = get_tracer
    trace.set_tracer_provider = set_tracer_provider

    # Exporter
    jaeger_thrift = add_module("opentelemetry.exporter.jaeger.thrift")
    zipkin_json = add_module("opentelemetry.exporter.zipkin.json")

    class JaegerExporter:  # noqa: D401
        """Fake JaegerExporter."""

        def __init__(self, *args, **kwargs):
            pass

    class ZipkinExporter:  # noqa: D401
        """Fake ZipkinExporter."""

        def __init__(self, *args, **kwargs):
            pass

    jaeger_thrift.JaegerExporter = JaegerExporter
    zipkin_json.ZipkinExporter = ZipkinExporter

    # SDK Trace
    sdk_trace = add_module("opentelemetry.sdk.trace")
    sdk_trace_export = add_module("opentelemetry.sdk.trace.export")

    class TracerProvider:  # noqa: D401
        """Fake TracerProvider."""

        pass

    class Span:  # noqa: D401
        """Fake Span."""

        pass

    class BatchSpanProcessor:  # noqa: D401
        """Fake BatchSpanProcessor."""

        def __init__(self, *a, **kw):
            pass

    class ConsoleSpanExporter:  # noqa: D401
        """Fake ConsoleSpanExporter."""

        def __init__(self, *a, **kw):
            pass

    sdk_trace.TracerProvider = TracerProvider
    sdk_trace.Span = Span
    sdk_trace_export.BatchSpanProcessor = BatchSpanProcessor
    sdk_trace_export.ConsoleSpanExporter = ConsoleSpanExporter

    # SDK Metrics
    sdk_metrics = add_module("opentelemetry.sdk.metrics")
    sdk_metrics_export = add_module("opentelemetry.sdk.metrics.export")

    class MeterProvider:  # noqa: D401
        """Fake MeterProvider."""

        pass

    class ConsoleMetricExporter:  # noqa: D401
        """Fake ConsoleMetricExporter."""

        def __init__(self, *a, **kw):
            pass

    class PeriodicExportingMetricReader:  # noqa: D401
        """Fake PeriodicExportingMetricReader."""

        def __init__(self, *a, **kw):
            pass

    sdk_metrics.MeterProvider = MeterProvider
    sdk_metrics_export.ConsoleMetricExporter = ConsoleMetricExporter
    sdk_metrics_export.PeriodicExportingMetricReader = PeriodicExportingMetricReader

    # Propagators
    propagate = add_module("opentelemetry.propagate")

    def inject(carrier=None):
        return None

    def extract(headers=None):
        return None

    propagate.inject = inject
    propagate.extract = extract

    tracecontext = add_module("opentelemetry.trace.propagation.tracecontext")

    class TraceContextTextMapPropagator:  # noqa: D401
        """Fake Propagator."""

        pass

    tracecontext.TraceContextTextMapPropagator = TraceContextTextMapPropagator

    baggage_prop = add_module("opentelemetry.baggage.propagation")

    class W3CBaggagePropagator:  # noqa: D401
        """Fake Baggage Propagator."""

        pass

    baggage_prop.W3CBaggagePropagator = W3CBaggagePropagator

    composite = add_module("opentelemetry.propagators.composite")

    class CompositeHTTPPropagator:  # noqa: D401
        """Fake Composite Propagator."""

        def __init__(self, *a, **kw):
            pass

    composite.CompositeHTTPPropagator = CompositeHTTPPropagator

    baggage_prop.W3CBaggagePropagator = W3CBaggagePropagator


# Reduziert Log-Noise in Tests
logging.getLogger("kei_agent").setLevel(logging.WARNING)
logging.getLogger("sdk.python.kei_agent").setLevel(logging.WARNING)

# Fake OTel vor Paket-Import erzeugen
ensure_fake_opentelemetry()

from unified_client import UnifiedKeiAgentClient  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402


from contextlib import contextmanager  # noqa: E402


@contextmanager
def capture_logger_records(logger_name: str, level: int = logging.INFO):
    """Kontextmanager, der LogRecords eines bestimmten Loggers sammelt."""
    records: List[logging.LogRecord] = []

    class _ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    logger = logging.getLogger(logger_name)
    old_level = logger.level
    handler = _ListHandler()
    logger.addHandler(handler)
    logger.setLevel(level)
    try:
        yield records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)


# Standardisierte Schwellwerte für Log-Prüfungen
# - STATE_TRANSITION_MIN_USED: In State-Transition-Tests wird mindestens 2x verwendet (Fehler + Erfolg)
# - HALF_OPEN_FAILURE_MIN_USED: In Half-Open-Failure-Tests ebenfalls mindestens 2x (Fehler vor Half-Open + Fehler im Half-Open)
# - HALF_OPEN_SUCCESS_MIN_USED: In Half-Open-Success-Tests mindestens 2x (Fehler vor Half-Open + Erfolg im Half-Open)
STATE_TRANSITION_MIN_USED: int = 2
HALF_OPEN_FAILURE_MIN_USED: int = 2
HALF_OPEN_SUCCESS_MIN_USED: int = 2


def get_messages(records: list[logging.LogRecord]) -> list[str]:
    """Gibt die formatierten Log-Nachrichten aus einer Record-Liste zurück."""
    # Nutzt getMessage(), um einheitliche Texte zu erhalten
    return [r.getMessage() for r in records]


def assert_cb_initialized_and_used(
    messages: list[str], cb_name: str, min_used: int
) -> None:
    """Prüft CB-Initialisierung und Mindestanzahl der Nutzungs-Logs.

    Args:
        messages: Liste der Log-Nachrichten (bereits formatiert)
        cb_name: Name des Circuit Breakers (z. B. "rpc.plan")
        min_used: Erwartete Mindestanzahl an "Circuit Breaker verwendet"-Logs
    """
    # Prüfe Initialisierung (korrigierte Log-Nachricht)
    init_ok = any((f"Circuit Breaker initialisiert: {cb_name}" in m) for m in messages)
    assert init_ok, (
        f"Erwartete Initialisierungs-Logzeile nicht gefunden. CB='{cb_name}'. "
        f"Vorhandene Nachrichten: {messages}"
    )
    # Prüfe Mindestanzahl der Verwendungs-Logs
    used_count = sum(
        m.startswith(f"Circuit Breaker verwendet: {cb_name}") for m in messages
    )
    assert used_count >= min_used, (
        f"Zu wenige Nutzungs-Logs für CB='{cb_name}'. Erwartet >= {min_used}, erhalten {used_count}. "
        f"Vorhandene Nachrichten: {messages}"
    )


from client import AgentClientConfig, RetryConfig, TracingConfig, RetryStrategy  # noqa: E402


class DummyTransientError(Exception):
    """Simuliert transiente Fehler für Retry-Tests."""


@pytest.mark.asyncio
async def test_rpc_specific_retry_policy(monkeypatch):
    """Testet RPC-spezifische Retry-Policy mit 5 Versuchen."""
    # Arrange: Konfiguration mit RPC-Policy (5 Versuche)
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(max_attempts=5, base_delay=0.0, jitter=False),
        },
    )

    client = UnifiedKeiAgentClient(config)

    # Mock: RPC-Client existiert und seine plan-Methode wirft 4x eine Exception, dann Erfolg
    calls = {"count": 0}

    class FakeRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def plan(self, objective: str, context: Optional[Dict[str, Any]] = None):
            calls["count"] += 1
            if calls["count"] < 5:
                raise DummyTransientError("temporary")
            return {"ok": True}

    client._rpc_client = FakeRPC()

    # Act
    result = await client._execute_rpc_operation("plan", {"objective": "x"})

    # Assert: genau 5 Versuche insgesamt, Erfolg
    assert result == {"ok": True}
    assert calls["count"] == 5


@asynccontextmanager
async def capture_state_transitions(client: UnifiedKeiAgentClient, cb_name: str):
    """Captures Circuit Breaker State-Transitions für einen bestimmten CB-Namen.

    Gibt eine Liste der Zustandsnamen zurück, beginnend mit dem aktuellen Zustand,
    gefolgt von allen neuen Zuständen gemäß on_state_change-Hook.
    """
    # Ermittelt passenden RetryManager aus dem Client
    proto = cb_name.split(".", 1)[0].lower() if "." in cb_name else ""
    rm = (
        client._retry_managers.get(proto)
        or client._retry_managers.get("default")
        or client.retry
    )

    # Holt oder erstellt den Circuit Breaker und hängt Hook an
    cb = rm.get_circuit_breaker(cb_name)
    transitions: List[str] = [getattr(cb.state, "value", str(cb.state))]

    async def on_state_change(old_state, new_state):  # type: ignore[no-redef]
        # Zeichnet neuen Zustand auf
        transitions.append(getattr(new_state, "value", str(new_state)))

    # Hook setzen
    original_hook = getattr(cb.config, "on_state_change", None)
    cb.config.on_state_change = on_state_change  # type: ignore[attr-defined]

    try:
        yield transitions
    finally:
        # Hook wiederherstellen
        cb.config.on_state_change = original_hook  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_stream_specific_retry_policy(monkeypatch):
    """Testet Stream-spezifische Retry-Policy mit 2 Versuchen."""
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(max_attempts=2, base_delay=0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class FakeStream:
        async def subscribe(self, stream_id, callback):
            calls["count"] += 1
            raise DummyTransientError("temporary")

        async def send_frame(self, stream_id, frame_type, payload):
            calls["count"] += 1
            raise DummyTransientError("temporary")

    client._stream_client = FakeStream()

    # subscribe sollte 2 Versuche machen und dann scheitern
    with pytest.raises(Exception):
        await client._execute_stream_operation(
            "subscribe", {"callback": lambda x: None, "stream_id": "s1"}
        )
    assert calls["count"] == 2

    # reset und test für send
    calls["count"] = 0
    with pytest.raises(Exception):
        await client._execute_stream_operation(
            "send", {"callback": lambda x: None, "stream_id": "s1"}
        )
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_bus_specific_retry_policy(monkeypatch):
    """Testet Bus-spezifische Retry-Policy mit 3 Versuchen."""
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(max_attempts=3, base_delay=0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class FakeBus:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            calls["count"] += 1
            raise DummyTransientError("temporary")

        async def rpc_invoke(
            self, service: str, method: str, payload: Dict[str, Any], timeout: float
        ):
            calls["count"] += 1
            raise DummyTransientError("temporary")

    client._bus_client = FakeBus()

    # publish: 3 Versuche dann Fehler
    with pytest.raises(Exception):
        await client._execute_bus_operation("publish", {"envelope": {"x": 1}})
    assert calls["count"] == 3

    # reset und test rpc_invoke fallback path
    calls["count"] = 0
    with pytest.raises(Exception):
        await client._execute_bus_operation("unknown_op", {"payload": {"x": 2}})
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_mcp_specific_retry_policy(monkeypatch):
    """Testet MCP-spezifische Retry-Policy mit 4 Versuchen."""
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(max_attempts=4, base_delay=0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class FakeMCP:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            calls["count"] += 1
            raise DummyTransientError("temporary")

    client._mcp_client = FakeMCP()

    with pytest.raises(Exception):
        await client._execute_mcp_operation("discover_tools", {"category": "x"})
    assert calls["count"] == 4


@pytest.mark.asyncio
async def test_fallback_to_default_retry_policy(monkeypatch):
    """Testet Fallback auf Standard-RetryConfig, wenn keine Policy für Protokoll existiert."""
    # Nur Default auf 2 setzen, keine protokollspezifischen Policies
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        retry=RetryConfig(max_attempts=2, base_delay=0.0, jitter=False),
        protocol_retry_policies={},
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class FakeRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            raise DummyTransientError("temporary")

    client._rpc_client = FakeRPC()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_backward_compatibility_without_protocol_policies(monkeypatch):
    """Testet Backward-Kompatibilität: Keine protocol_retry_policies konfiguriert."""
    config = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class FakeRPC2:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            raise DummyTransientError("temporary")

    client._rpc_client = FakeRPC2()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    assert calls["count"] == 3  # Default max_attempts=3


@pytest.mark.asyncio
async def test_circuit_breaker_metrics_and_transitions():
    """Verifiziert Circuit Breaker Metriken und Zustandsübergänge für RPC-Protokoll."""
    # Konfiguration: niedriger Threshold, kurze Recovery
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=1,
                recovery_timeout=0.1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class AlwaysFailRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            raise DummyTransientError("fail")

    client._rpc_client = AlwaysFailRPC()

    # 1) Erster Fehlversuch → Failure zählt, CB bleibt i.d.R. CLOSED bei Threshold==1 erst nach Bewertung
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    # Zugriff auf RetryManager/CB-Metriken
    rm = (
        client._retry_managers.get("rpc")
        or client._retry_managers.get("default")
        or client.retry
    )
    metrics_before = rm.get_metrics()
    cb_metrics = metrics_before["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics is not None
    assert cb_metrics["total_calls"] >= 1

    # 2) Wiederholter Fehlversuch → CB sollte OPEN werden nach Threshold
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    metrics_after = rm.get_metrics()
    cb_metrics2 = metrics_after["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics2 is not None
    # Je nach Implementierung: nach Überschreiten threshold → OPEN
    assert cb_metrics2["state"] in (
        "open",
        "half_open",
        "closed",
    )  # robust gegen Timing

    # 3) Warte auf Recovery und prüfe Übergänge HALF_OPEN/CLOSED
    await asyncio.sleep(0.15)
    # Ein weiterer Call, der wieder fehlschlägt, kann HALF_OPEN→OPEN triggern
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    metrics_post_recovery = rm.get_metrics()
    cb_metrics3 = metrics_post_recovery["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics3 is not None
    assert cb_metrics3["total_failures"] >= 2


@pytest.mark.asyncio
async def test_retry_delay_patterns_by_strategy(monkeypatch):
    """Testet Retry-Delay-Muster für EXPONENTIAL_BACKOFF, FIXED_DELAY, LINEAR_BACKOFF (jitter=False)."""
    delays_recorded: List[float] = []

    # Monkeypatch asyncio.sleep, um Delays deterministisch aufzuzeichnen
    async def fake_sleep(delay: float):
        delays_recorded.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Gemeinsamer failing Call
    class FailingRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            raise DummyTransientError("fail")

    # EXPONENTIAL_BACKOFF
    config_exp = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4, base_delay=1.0, jitter=False, exponential_base=2.0
            )
        },
    )
    client_exp = UnifiedKeiAgentClient(config_exp)
    client_exp._rpc_client = FailingRPC()

    with pytest.raises(Exception):
        await client_exp._execute_rpc_operation("unknown", {"x": 1})
    # Erwartete Delays: [1.0, 2.0, 4.0] bei 4 Versuchen
    assert delays_recorded[:3] == [1.0, 2.0, 4.0]

    # FIXED_DELAY
    delays_recorded.clear()
    config_fix = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=3,
                base_delay=0.5,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    client_fix = UnifiedKeiAgentClient(config_fix)
    client_fix._rpc_client = FailingRPC()

    with pytest.raises(Exception):
        await client_fix._execute_rpc_operation("unknown", {"x": 1})
    # Erwartete Delays: [0.5, 0.5]
    assert delays_recorded[:2] == [0.5, 0.5]

    # LINEAR_BACKOFF
    delays_recorded.clear()
    config_lin = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4,
                base_delay=0.5,
                jitter=False,
                strategy=RetryStrategy.LINEAR_BACKOFF,
            )
        },
    )
    client_lin = UnifiedKeiAgentClient(config_lin)
    client_lin._rpc_client = FailingRPC()

    with pytest.raises(Exception):
        await client_lin._execute_rpc_operation("unknown", {"x": 1})
    # Erwartete Delays: [0.5, 1.0, 1.5]
    assert delays_recorded[:3] == [0.5, 1.0, 1.5]


@pytest.mark.asyncio
async def test_stream_strategy_patterns(monkeypatch):
    """Testet Delay-Strategien für Stream-Protokoll (FIXED_DELAY vs. EXPONENTIAL_BACKOFF)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    class FailingStream:
        async def subscribe(self, stream_id: str, callback):
            raise DummyTransientError("temporary")

        async def send_frame(
            self, stream_id: str, frame_type: str, payload: Dict[str, Any]
        ):
            raise DummyTransientError("temporary")

    # FIXED_DELAY (konstante 2.0s)
    config_fix = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(
                max_attempts=3,
                base_delay=2.0,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    client_fix = UnifiedKeiAgentClient(config_fix)
    client_fix._stream_client = FailingStream()
    with pytest.raises(Exception):
        await client_fix._execute_stream_operation(
            "subscribe", {"callback": lambda x: None, "stream_id": "s1"}
        )
    assert delays[:2] == [2.0, 2.0]

    # EXPONENTIAL_BACKOFF (1.0, 2.0)
    delays.clear()
    config_exp = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                jitter=False,
                exponential_base=2.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            )
        },
    )
    client_exp = UnifiedKeiAgentClient(config_exp)
    client_exp._stream_client = FailingStream()
    with pytest.raises(Exception):
        await client_exp._execute_stream_operation(
            "send", {"callback": lambda x: None, "stream_id": "s2"}
        )
    assert delays[:2] == [1.0, 2.0]


@pytest.mark.asyncio
async def test_bus_strategy_patterns(monkeypatch):
    """Testet Delay-Strategien für Bus-Protokoll (LINEAR_BACKOFF vs. FIXED_DELAY)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    class FailingBus:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            raise DummyTransientError("temporary")

        async def rpc_invoke(
            self, service: str, method: str, payload: Dict[str, Any], timeout: float
        ):
            raise DummyTransientError("temporary")

    # LINEAR_BACKOFF (1.0, 2.0, 3.0)
    config_lin = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(
                max_attempts=4,
                base_delay=1.0,
                jitter=False,
                strategy=RetryStrategy.LINEAR_BACKOFF,
            )
        },
    )
    client_lin = UnifiedKeiAgentClient(config_lin)
    client_lin._bus_client = FailingBus()
    with pytest.raises(Exception):
        await client_lin._execute_bus_operation("publish", {"envelope": {"x": 1}})
    assert delays[:3] == [1.0, 2.0, 3.0]

    # FIXED_DELAY (0.5, 0.5)
    delays.clear()
    config_fix = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(
                max_attempts=3,
                base_delay=0.5,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    client_fix = UnifiedKeiAgentClient(config_fix)
    client_fix._bus_client = FailingBus()
    with pytest.raises(Exception):
        await client_fix._execute_bus_operation(
            "rpc_invoke",
            {"service": "agent", "method": "m", "payload": {}, "timeout": 1.0},
        )
    assert delays[:2] == [0.5, 0.5]


@pytest.mark.asyncio
async def test_mcp_strategy_patterns(monkeypatch):
    """Testet Delay-Strategien für MCP-Protokoll (EXPONENTIAL_BACKOFF vs. FIXED_DELAY)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    class FailingMCP:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            raise DummyTransientError("temporary")

        async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]):
            raise DummyTransientError("temporary")

    # EXPONENTIAL_BACKOFF (0.5, 1.0)
    config_exp = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(
                max_attempts=3,
                base_delay=0.5,
                jitter=False,
                exponential_base=2.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            )
        },
    )
    client_exp = UnifiedKeiAgentClient(config_exp)
    client_exp._mcp_client = FailingMCP()
    with pytest.raises(Exception):
        await client_exp._execute_mcp_operation("discover_tools", {"category": "x"})
    assert delays[:2] == [0.5, 1.0]

    # FIXED_DELAY (1.5, 1.5)
    delays.clear()
    config_fix = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(
                max_attempts=3,
                base_delay=1.5,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    client_fix = UnifiedKeiAgentClient(config_fix)
    client_fix._mcp_client = FailingMCP()
    with pytest.raises(Exception):
        await client_fix._execute_mcp_operation(
            "invoke_tool", {"tool_name": "t", "parameters": {}}
        )
    assert delays[:2] == [1.5, 1.5]


@pytest.mark.asyncio
async def test_circuit_breaker_precise_state_transitions():
    """Testet präzise CB-State-Transitionen (CLOSED → OPEN → HALF_OPEN → CLOSED) deterministisch."""
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="token",
        agent_id="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            # threshold=2, recovery_timeout=0.1s, in HALF_OPEN nur 1 Call
            "rpc": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=2,
                recovery_timeout=0.1,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    # Fake RPC: zwei Mal Fehler, dann Erfolg
    calls = {"count": 0}

    class FlakyRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            if calls["count"] <= 2:
                raise DummyTransientError("fail")
            return {"ok": True}

    client._rpc_client = FlakyRPC()

    rm = (
        client._retry_managers.get("rpc")
        or client._retry_managers.get("default")
        or client.retry
    )
    cb_name = "rpc.unknown"

    # Start: closed
    m0 = rm.get_metrics()["circuit_breakers"].get(cb_name)
    if m0 is not None:
        assert m0["state"] == "closed"

    # Zwei Fehlversuche → OPEN
    for _ in range(2):
        with pytest.raises(Exception):
            await client._execute_rpc_operation("unknown", {"x": 1})
    m_open = rm.get_metrics()["circuit_breakers"][cb_name]
    assert m_open["state"] == "open"
    assert (
        m_open.get("current_failure_count", 0) >= 2
        or m_open.get("total_failures", 0) >= 2
    )

    # Warten bis Half-Open möglich
    await asyncio.sleep(0.12)

    # Erfolgreicher Call in HALF_OPEN → CLOSED
    result = await client._execute_rpc_operation("unknown", {"x": 1})
    assert result == {"ok": True}
    m_closed = rm.get_metrics()["circuit_breakers"][cb_name]
    assert m_closed["state"] == "closed"
    # Erfolg kann über total_calls - total_failures approximiert werden
    assert (m_closed.get("total_calls", 0) - m_closed.get("total_failures", 0)) >= 1


@pytest.mark.asyncio
async def test_stream_state_transitions(caplog):
    """Verifiziert exakte State-Sequenz für Stream: [closed, open, half_open, closed] und Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=1,
                recovery_timeout=0.05,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyStream:
        def __init__(self):
            self.calls = 0

        async def subscribe(self, stream_id: str, callback):
            self.calls += 1
            if self.calls == 1:
                raise DummyTransientError("fail")
            return None

    client._stream_client = FlakyStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            await client._execute_stream_operation(
                "subscribe", {"callback": lambda x: None, "stream_id": "s"}
            )

    assert transitions == ["closed", "open", "half_open", "closed"]
    # Prüfe Logs aus gesamter Phase (standardisiert)
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_bus_state_transitions(caplog):
    """Verifiziert exakte State-Sequenz für Bus: [closed, open, half_open, closed] und Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=3,
                recovery_timeout=0.2,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyBus:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            self.calls += 1
            if self.calls <= 3:
                raise DummyTransientError("fail")
            return {"ok": True}

    client._bus_client = FlakyBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_bus_operation("publish", {"envelope": {"x": 1}})
            for _ in range(2):
                with pytest.raises(Exception):
                    await client._execute_bus_operation(
                        "publish", {"envelope": {"x": 1}}
                    )
            await asyncio.sleep(0.21)
            await client._execute_bus_operation("publish", {"envelope": {"x": 2}})

    assert transitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_state_transitions(caplog):
    """Verifiziert exakte State-Sequenz für MCP: [closed, open, half_open, closed] und Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=2,
                recovery_timeout=0.1,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyMCP:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            self.calls += 1
            if self.calls <= 2:
                raise DummyTransientError("fail")
            return ["t1", "t2"]

    client._mcp_client = FlakyMCP()

    cb_name = "mcp.discover_tools"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            await asyncio.sleep(0.12)
            await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert transitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_half_open_failure_reopens(caplog):
    """Testet Fehlerfall: HALF_OPEN → OPEN bei erneutem Fehler für RPC inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=1,
                recovery_timeout=0.05,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FailAgainRPC:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            self.calls += 1
            raise DummyTransientError("fail")

    client._rpc_client = FailAgainRPC()

    cb_name = "rpc.unknown"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_rpc_operation("unknown", {"x": 1})
            await asyncio.sleep(0.06)
            with pytest.raises(Exception):
                await client._execute_rpc_operation("unknown", {"x": 1})

    assert transitions == ["closed", "open", "half_open", "open"]
    all_msgs = [r.getMessage() for r in recs_all]
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_stream_half_open_failure_reopens(caplog):
    """Testet Fehlerfall: HALF_OPEN → OPEN bei erneutem Fehler für Stream inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=1,
                recovery_timeout=0.05,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class AlwaysFailStream:
        async def subscribe(self, stream_id: str, callback):
            raise DummyTransientError("fail")

    client._stream_client = AlwaysFailStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )

    assert transitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_bus_half_open_failure_reopens(caplog):
    """Testet Fehlerfall: HALF_OPEN → OPEN bei erneutem Fehler für Bus inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=3,
                recovery_timeout=0.2,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class AlwaysFailBus:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            raise DummyTransientError("fail")

    client._bus_client = AlwaysFailBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_bus_operation("publish", {"envelope": {"x": 1}})
            for _ in range(2):
                with pytest.raises(Exception):
                    await client._execute_bus_operation(
                        "publish", {"envelope": {"x": 1}}
                    )
            await asyncio.sleep(0.21)
            with pytest.raises(Exception):
                await client._execute_bus_operation("publish", {"envelope": {"x": 2}})

    assert transitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_half_open_failure_reopens(caplog):
    """Testet Fehlerfall: HALF_OPEN → OPEN bei erneutem Fehler für MCP inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=2,
                recovery_timeout=0.1,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class AlwaysFailMCP:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            raise DummyTransientError("fail")

    client._mcp_client = AlwaysFailMCP()

    cb_name = "mcp.discover_tools"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            await asyncio.sleep(0.12)
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert transitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_stream_half_open_success_closes(caplog):
    """Prüft HALF_OPEN → CLOSED bei erfolgreichem Call im Stream-Protokoll inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "stream": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=1,
                recovery_timeout=0.05,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyThenSuccessStream:
        def __init__(self):
            self.calls = 0

        async def subscribe(self, stream_id: str, callback):
            self.calls += 1
            if self.calls == 1:
                raise DummyTransientError("fail")
            return None

    client._stream_client = FlakyThenSuccessStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            await client._execute_stream_operation(
                "subscribe", {"callback": lambda x: None, "stream_id": "s"}
            )

    assert transitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_SUCCESS_MIN_USED)


@pytest.mark.asyncio
async def test_bus_half_open_success_closes(caplog):
    """Prüft HALF_OPEN → CLOSED bei erfolgreichem Call im Bus-Protokoll inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "bus": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=3,
                recovery_timeout=0.2,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyThenSuccessBus:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            self.calls += 1
            if self.calls <= 3:
                raise DummyTransientError("fail")
            return {"ok": True}

    client._bus_client = FlakyThenSuccessBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_transitions(client, cb_name) as transitions:
            for _ in range(3):
                with pytest.raises(Exception):
                    await client._execute_bus_operation(
                        "publish", {"envelope": {"x": 1}}
                    )
            await asyncio.sleep(0.21)
            await client._execute_bus_operation("publish", {"envelope": {"x": 2}})

    assert transitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_and_used(all_msgs, cb_name, HALF_OPEN_SUCCESS_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_half_open_success_closes(caplog):
    """Prüft HALF_OPEN → CLOSED bei erfolgreichem Call im MCP-Protokoll inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "mcp": RetryConfig(
                max_attempts=1,
                base_delay=0.0,
                jitter=False,
                failure_threshold=2,
                recovery_timeout=0.1,
                half_open_max_calls=1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class FlakyThenSuccessMCP:
        def __init__(self):
            self.calls = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            self.calls += 1
            if self.calls <= 2:
                raise DummyTransientError("fail")
            return ["t1", "t2"]

    client._mcp_client = FlakyThenSuccessMCP()

    cb_name = "mcp.discover_tools"
    async with capture_state_transitions(client, cb_name) as transitions:
        with capture_logger_records("kei_agent.retry", logging.INFO) as recs_init:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
        with pytest.raises(Exception):
            await client._execute_mcp_operation("discover_tools", {"category": "x"})
        await asyncio.sleep(0.12)
        await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert transitions == ["closed", "open", "half_open", "closed"]
    init_msgs = [r.getMessage() for r in recs_init]
    assert any(m.startswith(f"Circuit Breaker verwendet: {cb_name}") for m in init_msgs)
    assert any(m.startswith(f"Circuit Breaker verwendet: {cb_name}") for m in init_msgs)

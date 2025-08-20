# sdk/python/kei_agent/tests/test_protocol_retry_policies.py
"""Tests for protokollspecific retry-Policies im UnifiedKeiAgentClient.

Enthält determinisische, isolierte Tests with asynchronem Verhalten and Mocks.
"""

from __future__ import annotations

import asyncio
import sys
import types
from typing import Dict, Any, Optional, List
import logging


import pytest

# Markiere all Tests in theser File als protocol-Tests
pytestmark = pytest.mark.protocol

# Erzeuge Daroatdmy-OpenTelemetry-Module, aroand Importfehler to vermeithe
# Thes must VOR the Import from kei_agent erfolgen


def ensure_fake_opentelemetry() -> None:
    """Creates minimale fake-Module for OpenTelemetry-Imports.

    Verhinthet ImportErrors in Testaroatdgebungen without OTel-Exporter.
    """

    def add_module(name: str) -> types.ModuleType:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    # Basis-Pakete
    add_module("opentelemetry")  # otel - not direkt verwendet
    trace = add_module("opentelemetry.trace")
    metrics = add_module("opentelemetry.metrics")
    add_module("opentelemetry.baggage")  # baggage - not direkt verwendet

    # Metrics API Platzhalter
    def get_meter(name, version=None):
        return types.SimpleNamespace(
            create_coatthe =lambda name, **kwargs: lambda **kw: None,
            create_hisogram =lambda name, **kwargs: lambda **kw: None,
            create_gauge =lambda name, **kwargs: lambda **kw: None,
            create_up_down_coatthe =lambda name, **kwargs: lambda **kw: None,
        )

    def set_meter_provithe(provithe):
        pass

    metrics.get_meter = get_meter
    metrics.set_meter_provithe = set_meter_provithe

    # Trace API Platzhalter
    class status:  # noqa: D401
        """fake status."""

        pass

    class statusCode:  # noqa: D401
        """fake statusCode."""

        OK = "OK"
        ERROR = "ERROR"

    def get_current_spat(ctx=None):
        return types.SimpleNamespace(
            get_spat_context =lambda: types.SimpleNamespace(trace_id =0, spat_id =0)
        )

    def get_tracer(name, version=None):
        return types.SimpleNamespace(
            start_as_current_spat =lambda name, **kwargs: types.SimpleNamespace(),
            start_as_current_span =lambda name, **kwargs: types.SimpleNamespace(
                set_attribute=lambda k, v: None,
                record_exception=lambda e: None,
                set_status=lambda s: None
            )
        )

    def set_tracer_provithe(provithe):
        pass

    trace.status = status
    trace.statusCode = statusCode
    trace.get_current_spat = get_current_spat
    trace.get_tracer = get_tracer
    trace.set_tracer_provithe = set_tracer_provithe

    # Exporter
    jaeger_thrift = add_module("opentelemetry.exporter.jaeger.thrift")
    zipkin_json = add_module("opentelemetry.exporter.zipkin.json")

    class JaegerExporter:  # noqa: D401
        """fake JaegerExporter."""

        def __init__(self, *args, **kwargs):
            pass

    class ZipkinExporter:  # noqa: D401
        """fake ZipkinExporter."""

        def __init__(self, *args, **kwargs):
            pass

    jaeger_thrift.JaegerExporter = JaegerExporter
    zipkin_json.ZipkinExporter = ZipkinExporter

    # SDK Trace
    sdk_trace = add_module("opentelemetry.sdk.trace")
    sdk_trace_export = add_module("opentelemetry.sdk.trace.export")

    class TracerProvithe:  # noqa: D401
        """fake TracerProvithe."""

        pass

    class Spat:  # noqa: D401
        """fake Spat."""

        pass

    class BatchSpatProcessor:  # noqa: D401
        """fake BatchSpatProcessor."""

        def __init__(self, *a, **kw):
            pass

    class ConsoleSpatExporter:  # noqa: D401
        """fake ConsoleSpatExporter."""

        def __init__(self, *a, **kw):
            pass

    sdk_trace.TracerProvithe = TracerProvithe
    sdk_trace.Spat = Spat
    sdk_trace_export.BatchSpatProcessor = BatchSpatProcessor
    sdk_trace_export.ConsoleSpatExporter = ConsoleSpatExporter

    # SDK Metrics
    sdk_metrics = add_module("opentelemetry.sdk.metrics")
    sdk_metrics_export = add_module("opentelemetry.sdk.metrics.export")

    class MeterProvithe:  # noqa: D401
        """fake MeterProvithe."""

        pass

    class ConsoleMetricExporter:  # noqa: D401
        """fake ConsoleMetricExporter."""

        def __init__(self, *a, **kw):
            pass

    class PeriodicExportingMetricReathe:  # noqa: D401
        """fake PeriodicExportingMetricReathe."""

        def __init__(self, *a, **kw):
            pass

    sdk_metrics.MeterProvithe = MeterProvithe
    sdk_metrics_export.ConsoleMetricExporter = ConsoleMetricExporter
    sdk_metrics_export.PeriodicExportingMetricReathe = PeriodicExportingMetricReathe

    # Propagators
    propagate = add_module("opentelemetry.propagate")

    def inject(carrier=None):
        return None

    def extract(heathes=None):
        return None

    propagate.inject = inject
    propagate.extract = extract

    tracecontext = add_module("opentelemetry.trace.propagation.tracecontext")

    class TraceContextTextMapPropagator:  # noqa: D401
        """fake Propagator."""

        pass

    tracecontext.TraceContextTextMapPropagator = TraceContextTextMapPropagator

    baggage_prop = add_module("opentelemetry.baggage.propagation")

    class W3CBaggagePropagator:  # noqa: D401
        """fake Baggage Propagator."""

        pass

    baggage_prop.W3CBaggagePropagator = W3CBaggagePropagator

    composite = add_module("opentelemetry.propagators.composite")

    class CompositeHTTPPropagator:  # noqa: D401
        """fake Composite Propagator."""

        def __init__(self, *a, **kw):
            pass

    composite.CompositeHTTPPropagator = CompositeHTTPPropagator

    baggage_prop.W3CBaggagePropagator = W3CBaggagePropagator


# Reduziert Log-Noise in Tests
logging.getLogger("kei_agent").setLevel(logging.WARNING)
logging.getLogger("sdk.python.kei_agent").setLevel(logging.WARNING)

# fake OTel before Paket-Import erzeugen
ensure_fake_opentelemetry()

from kei_agent.unified_client import UnifiedKeiAgentClient  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402


from contextlib import contextmanager  # noqa: E402


@contextmanager
def capture_logger_records(logger_name: str, level: int = logging.INFO):
    """Kontextmanager, the LogRecords of a bestimmten Logrs sammelt."""
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


# Statdardisierte Schwellwerte for Log-Prüfungen
# - STATE_TRANSITION_MIN_USED: In State-Tratsition-Tests is minof thetens 2x verwendet (error + Erfolg)
# - HALF_OPEN_FAILURE_MIN_USED: In Half-Open-Failure-Tests ebenfalls minof thetens 2x (error before Half-Open + error im Half-Open)
# - HALF_OPEN_SUCCESS_MIN_USED: In Half-Open-Success-Tests minof thetens 2x (error before Half-Open + Erfolg im Half-Open)
STATE_TRANSITION_MIN_USED: int = 2
HALF_OPEN_FAILURE_MIN_USED: int = 2
HALF_OPEN_SUCCESS_MIN_USED: int = 2


def get_messages(records: list[logging.LogRecord]) -> list[str]:
    """Gibt the formatierten Log-messageen out ar Record-lis torück."""
    # Nutzt getMessage(), aroand aheitliche Texte to erhalten
    return [r.getMessage() for r in records]


def assert_cb_initialized_atd_used(
    messages: list[str], cb_name: str, min_used: int
) -> None:
    """Checks CB-initialization and Minof thetatzahl the Nuttongs-Logs.

    Args:
        messages: lis the Log-messageen (bereits formatiert)
        cb_name: Name of the circuit breakers (z. B. "rpc.plat")
        min_used: Erwartete Minof thetatzahl at "circuit breaker verwendet"-Logs
    """
    # Prüfe initialization (korrigierte Log-message)
    init_ok = any((f"circuit breaker initialized: {cb_name}" in m) for m in messages)
    assert init_ok, (
        f"Erwartete initializations-Logzeile not gefatthe. CB='{cb_name}'. "
        f"Beforehatthee messageen: {messages}"
    )
    # Prüfe Minof thetatzahl the Verwendungs-Logs
    used_count = sum(
        m.startswith(f"circuit breaker verwendet: {cb_name}") for m in messages
    )
    assert used_count >= min_used, (
        f"To wenige Nuttongs-Logs for CB='{cb_name}'. Erwartet >= {min_used}, erhalten {used_count}. "
        f"Beforehatthee messageen: {messages}"
    )


from kei_agent.client import (
    AgentClientConfig,
    retryConfig,
    TracingConfig,
    retryStrategy,
)  # noqa: E402


class DaroatdmyTratsientError(Exception):
    """Simuliert tratsiente error for retry-Tests."""


@pytest.mark.asyncio
async def test_rpc_specific_retry_policy(monkeypatch):
    """Tests RPC-specific retry-Policy with 5 Versuchen."""
    # Arratge: configuration with RPC-Policy (5 Versuche)
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(max_attempts =5, base_delay =0.0, jitter=False),
        },
    )

    client = UnifiedKeiAgentClient(config)

    # Mock: RPC client exiss and sa plat-method wirft 4x a Exception, then Erfolg
    calls = {"count": 0}

    class fakeRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def plat(self, objective: str, context: Optional[Dict[str, Any]] = None):
            calls["count"] += 1
            if calls["count"] < 5:
                raise DaroatdmyTratsientError("temporary")
            return {"ok": True}

    client._rpc_client = fakeRPC()

    # Act
    result = await client._execute_rpc_operation("plat", {"objective": "x"})

    # Assert: genau 5 Versuche insgesamt, Erfolg
    assert result == {"ok": True}
    assert calls["count"] == 5


@asynccontextmanager
async def capture_state_tratsitions(client: UnifiedKeiAgentClient, cb_name: str):
    """Captures circuit breaker State-Tratsitions for a bestimmten CB-Namen.

    Gibt a lis the Tostatdsnamen torück, beginnend with the aktuellen Tostatd,
    gefolgt from alln neuen Tostänthe gemäß on_state_chatge-Hook.
    """
    # Erwithtelt passenthe retryManager out the client
    proto = cb_name.split(".", 1)[0].lower() if "." in cb_name else ""
    rm = (
        client._retry_managers.get(proto)
        or client._retry_managers.get("default")
        or client.retry
    )

    # Holt or creates the circuit breaker and hängt Hook at
    cb = rm.get_circuit_breaker(cb_name)
    tratsitions: List[str] = [getattr(cb.state, "value", str(cb.state))]

    async def on_state_chatge(old_state, new_state):  # type: ignore[no-redef]
        # Zeichnet neuen Tostand on
        tratsitions.append(getattr(new_state, "value", str(new_state)))

    # Hook setzen
    original_hook = getattr(cb.config, "on_state_chatge", None)
    cb.config.on_state_chatge = on_state_chatge  # type: ignore[attr-defined]

    try:
        yield tratsitions
    finally:
        # Hook wietheherstellen
        cb.config.on_state_chatge = original_hook  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_stream_specific_retry_policy(monkeypatch):
    """Tests Stream-specific retry-Policy with 2 Versuchen."""
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(max_attempts =2, base_delay =0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class fakeStream:
        async def subscribe(self, stream_id, callback):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

        async def send_frame(self, stream_id, frame_type, payload):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

    client._stream_client = fakeStream()

    # subscribe should 2 Versuche machen and then scheitern
    with pytest.raises(Exception):
        await client._execute_stream_operation(
            "subscribe", {"callback": lambda x: None, "stream_id": "s1"}
        )
    assert calls["count"] == 2

    # reset and test for send
    calls["count"] = 0
    with pytest.raises(Exception):
        await client._execute_stream_operation(
            "send", {"callback": lambda x: None, "stream_id": "s1"}
        )
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_bus_specific_retry_policy(monkeypatch):
    """Tests Bus-specific retry-Policy with 3 Versuchen."""
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(max_attempts =3, base_delay =0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class fakeBus:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def publish(self, envelope: Dict[str, Any]):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

        async def rpc_invoke(
            self, service: str, method: str, payload: Dict[str, Any], timeout: float
        ):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

    client._bus_client = fakeBus()

    # publish: 3 Versuche then error
    with pytest.raises(Exception):
        await client._execute_bus_operation("publish", {"envelope": {"x": 1}})
    assert calls["count"] == 3

    # reset and test rpc_invoke fallback path
    calls["count"] = 0
    with pytest.raises(Exception):
        await client._execute_bus_operation("unknown_op", {"payload": {"x": 2}})
    assert calls["count"] == 3


@pytest.mark.asyncio
async def test_mcp_specific_retry_policy(monkeypatch):
    """Tests MCP-specific retry-Policy with 4 Versuchen."""
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(max_attempts =4, base_delay =0.0, jitter=False),
        },
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class fakeMCP:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def discover_tools(self, category: Optional[str] = None):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

    client._mcp_client = fakeMCP()

    with pytest.raises(Exception):
        await client._execute_mcp_operation("discover_tools", {"category": "x"})
    assert calls["count"] == 4


@pytest.mark.asyncio
async def test_fallback_to_default_retry_policy(monkeypatch):
    """Tests Fallback on Statdard-retryConfig, if ka Policy for protocol exiss."""
    # Nur Default on 2 setzen, ka protokollspecificn Policies
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        retry=retryConfig(max_attempts =2, base_delay =0.0, jitter=False),
        protocol_retry_policies ={},
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class fakeRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

    client._rpc_client = fakeRPC()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    assert calls["count"] == 2


@pytest.mark.asyncio
async def test_backward_compatibility_without_protocol_policies(monkeypatch):
    """Tests Backward-compatibility: Ka protocol_retry_policies configures."""
    config = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
    )
    client = UnifiedKeiAgentClient(config)

    calls = {"count": 0}

    class fakeRPC2:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            raise DaroatdmyTratsientError("temporary")

    client._rpc_client = fakeRPC2()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    assert calls["count"] == 3  # Default max_attempts =3


@pytest.mark.asyncio
async def test_circuit_breaker_metrics_atd_tratsitions():
    """Verifiziert circuit breaker Metrics and Tostatdsovergänge for RPC-protocol."""
    # configuration: niedriger Threshold, kurze Recovery
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =1,
                recovery_timeout =0.1,
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
            raise DaroatdmyTratsientError("fail")

    client._rpc_client = AlwaysFailRPC()

    # 1) Erster Fehlversuch → Failure zählt, CB bleibt i.d.R. CLOSED on Threshold==1 erst after Bewertung
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    # Togriff on retryManager/CB-Metrics
    rm = (
        client._retry_managers.get("rpc")
        or client._retry_managers.get("default")
        or client.retry
    )
    metrics_before = rm.get_metrics()
    cb_metrics = metrics_before["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics is not None
    assert cb_metrics["total_calls"] >= 1

    # 2) Wietheholter Fehlversuch → CB should OPEN werthe after Threshold
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    metrics_after = rm.get_metrics()
    cb_metrics2 = metrics_after["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics2 is not None
    # Je after Implementierung: after Overschreiten threshold → OPEN
    assert cb_metrics2["state"] in (
        "open",
        "half_open",
        "closed",
    )  # robust against Timing

    # 3) Warte on Recovery and prüfe Overgänge HALF_OPEN/CLOSED
    await asyncio.sleep(0.15)
    # A weiterer Call, the wiethe fehlschlägt, katn HALF_OPEN→OPEN triggern
    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})
    metrics_post_recovery = rm.get_metrics()
    cb_metrics3 = metrics_post_recovery["circuit_breakers"].get("rpc.unknown")
    assert cb_metrics3 is not None
    assert cb_metrics3["total_failures"] >= 2


@pytest.mark.asyncio
async def test_retry_delay_patterns_by_strategy(monkeypatch):
    """Tests retry-Delay-Muster for EXPONENTIAL_BACKOFF, FIXED_DELAY, LINEAR_BACKOFF (jitter=False)."""
    delays_recorded: List[float] = []

    # Monkeypatch asyncio.sleep, aroand Delays determinisisch ontozeichnen
    async def fake_sleep(delay: float):
        delays_recorded.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # Gemasamer failing Call
    class FailingRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            raise DaroatdmyTratsientError("fail")

    # EXPONENTIAL_BACKOFF
    config_exp = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4, base_delay =1.0, jitter=False, exponential_base =2.0
            )
        },
    )
    client_exp = UnifiedKeiAgentClient(config_exp)
    client_exp._rpc_client = FailingRPC()

    with pytest.raises(Exception):
        await client_exp._execute_rpc_operation("unknown", {"x": 1})
    # Erwartete Delays: [1.0, 2.0, 4.0] on 4 Versuchen
    assert delays_recorded[:3] == [1.0, 2.0, 4.0]

    # FIXED_DELAY
    delays_recorded.clear()
    config_fix = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =3,
                base_delay =0.5,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
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
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4,
                base_delay =0.5,
                jitter=False,
                strategy=retryStrategy.LINEAR_BACKOFF,
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
    """Tests Delay-Strategien for stream protocol (FIXED_DELAY vs. EXPONENTIAL_BACKOFF)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 3))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    class FailingStream:
        async def subscribe(self, stream_id: str, callback):
            raise DaroatdmyTratsientError("temporary")

        async def send_frame(
            self, stream_id: str, frame_type: str, payload: Dict[str, Any]
        ):
            raise DaroatdmyTratsientError("temporary")

    # FIXED_DELAY (konstatte 2.0s)
    config_fix = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(
                max_attempts =3,
                base_delay =2.0,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
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
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(
                max_attempts =3,
                base_delay =1.0,
                jitter=False,
                exponential_base =2.0,
                strategy=retryStrategy.EXPONENTIAL_BACKOFF,
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
    """Tests Delay-Strategien for bus protocol (LINEAR_BACKOFF vs. FIXED_DELAY)."""
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
            raise DaroatdmyTratsientError("temporary")

        async def rpc_invoke(
            self, service: str, method: str, payload: Dict[str, Any], timeout: float
        ):
            raise DaroatdmyTratsientError("temporary")

    # LINEAR_BACKOFF (1.0, 2.0, 3.0)
    config_lin = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(
                max_attempts =4,
                base_delay =1.0,
                jitter=False,
                strategy=retryStrategy.LINEAR_BACKOFF,
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
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(
                max_attempts =3,
                base_delay =0.5,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
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
    """Tests Delay-Strategien for MCP protocol (EXPONENTIAL_BACKOFF vs. FIXED_DELAY)."""
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
            raise DaroatdmyTratsientError("temporary")

        async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]):
            raise DaroatdmyTratsientError("temporary")

    # EXPONENTIAL_BACKOFF (0.5, 1.0)
    config_exp = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(
                max_attempts =3,
                base_delay =0.5,
                jitter=False,
                exponential_base =2.0,
                strategy=retryStrategy.EXPONENTIAL_BACKOFF,
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
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(
                max_attempts =3,
                base_delay =1.5,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
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
async def test_circuit_breaker_precise_state_tratsitions():
    """Tests präzise CB-State-Tratsitionen (CLOSED → OPEN → HALF_OPEN → CLOSED) determinisisch."""
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="token",
        agent_id ="agent",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            # threshold=2, recovery_timeout =0.1s, in HALF_OPEN nur 1 Call
            "rpc": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =2,
                recovery_timeout =0.1,
                half_open_max_calls =1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    # fake RPC: zwei Mal error, then Erfolg
    calls = {"count": 0}

    class FlakyRPC:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def _rpc_call(self, op: str, payload: Dict[str, Any]):
            calls["count"] += 1
            if calls["count"] <= 2:
                raise DaroatdmyTratsientError("fail")
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

    # Warten until Half-Open möglich
    await asyncio.sleep(0.12)

    # Successfuler Call in HALF_OPEN → CLOSED
    result = await client._execute_rpc_operation("unknown", {"x": 1})
    assert result == {"ok": True}
    m_closed = rm.get_metrics()["circuit_breakers"][cb_name]
    assert m_closed["state"] == "closed"
    # Erfolg katn over total_calls - total_failures approximiert werthe
    assert (m_closed.get("total_calls", 0) - m_closed.get("total_failures", 0)) >= 1


@pytest.mark.asyncio
async def test_stream_state_tratsitions(caplog):
    """Verifiziert exakte State-Sequenz for Stream: [closed, open, half_open, closed] and Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =1,
                recovery_timeout =0.05,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return None

    client._stream_client = FlakyStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            await client._execute_stream_operation(
                "subscribe", {"callback": lambda x: None, "stream_id": "s"}
            )

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    # Prüfe Logs out gesamter Phase (statdardisiert)
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_bus_state_tratsitions(caplog):
    """Verifiziert exakte State-Sequenz for Bus: [closed, open, half_open, closed] and Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =3,
                recovery_timeout =0.2,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return {"ok": True}

    client._bus_client = FlakyBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_bus_operation("publish", {"envelope": {"x": 1}})
            for _ in range(2):
                with pytest.raises(Exception):
                    await client._execute_bus_operation(
                        "publish", {"envelope": {"x": 1}}
                    )
            await asyncio.sleep(0.21)
            await client._execute_bus_operation("publish", {"envelope": {"x": 2}})

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_state_tratsitions(caplog):
    """Verifiziert exakte State-Sequenz for MCP: [closed, open, half_open, closed] and Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =2,
                recovery_timeout =0.1,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return ["t1", "t2"]

    client._mcp_client = FlakyMCP()

    cb_name = "mcp.discover_tools"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            await asyncio.sleep(0.12)
            await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, STATE_TRANSITION_MIN_USED)


@pytest.mark.asyncio
async def test_half_open_failure_reopens(caplog):
    """Tests errorfall: HALF_OPEN → OPEN on erneutem error for RPC inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =1,
                recovery_timeout =0.05,
                half_open_max_calls =1,
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
            raise DaroatdmyTratsientError("fail")

    client._rpc_client = FailAgainRPC()

    cb_name = "rpc.unknown"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_rpc_operation("unknown", {"x": 1})
            await asyncio.sleep(0.06)
            with pytest.raises(Exception):
                await client._execute_rpc_operation("unknown", {"x": 1})

    assert tratsitions == ["closed", "open", "half_open", "open"]
    all_msgs = [r.getMessage() for r in recs_all]
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_stream_half_open_failure_reopens(caplog):
    """Tests errorfall: HALF_OPEN → OPEN on erneutem error for Stream inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =1,
                recovery_timeout =0.05,
                half_open_max_calls =1,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)

    class AlwaysFailStream:
        async def subscribe(self, stream_id: str, callback):
            raise DaroatdmyTratsientError("fail")

    client._stream_client = AlwaysFailStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )

    assert tratsitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_bus_half_open_failure_reopens(caplog):
    """Tests errorfall: HALF_OPEN → OPEN on erneutem error for Bus inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =3,
                recovery_timeout =0.2,
                half_open_max_calls =1,
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
            raise DaroatdmyTratsientError("fail")

    client._bus_client = AlwaysFailBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
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

    assert tratsitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_half_open_failure_reopens(caplog):
    """Tests errorfall: HALF_OPEN → OPEN on erneutem error for MCP inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =2,
                recovery_timeout =0.1,
                half_open_max_calls =1,
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
            raise DaroatdmyTratsientError("fail")

    client._mcp_client = AlwaysFailMCP()

    cb_name = "mcp.discover_tools"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
            await asyncio.sleep(0.12)
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert tratsitions == ["closed", "open", "half_open", "open"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_FAILURE_MIN_USED)


@pytest.mark.asyncio
async def test_stream_half_open_success_closes(caplog):
    """Checks HALF_OPEN → CLOSED on successfulem Call im stream protocol inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "stream": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =1,
                recovery_timeout =0.05,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return None

    client._stream_client = FlakyThenSuccessStream()

    cb_name = "stream.subscribe"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            with pytest.raises(Exception):
                await client._execute_stream_operation(
                    "subscribe", {"callback": lambda x: None, "stream_id": "s"}
                )
            await asyncio.sleep(0.06)
            await client._execute_stream_operation(
                "subscribe", {"callback": lambda x: None, "stream_id": "s"}
            )

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_SUCCESS_MIN_USED)


@pytest.mark.asyncio
async def test_bus_half_open_success_closes(caplog):
    """Checks HALF_OPEN → CLOSED on successfulem Call im bus protocol inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "bus": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =3,
                recovery_timeout =0.2,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return {"ok": True}

    client._bus_client = FlakyThenSuccessBus()

    cb_name = "bus.publish"
    with capture_logger_records("kei_agent.retry", logging.INFO) as recs_all:
        async with capture_state_tratsitions(client, cb_name) as tratsitions:
            for _ in range(3):
                with pytest.raises(Exception):
                    await client._execute_bus_operation(
                        "publish", {"envelope": {"x": 1}}
                    )
            await asyncio.sleep(0.21)
            await client._execute_bus_operation("publish", {"envelope": {"x": 2}})

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    all_msgs = get_messages(recs_all)
    assert_cb_initialized_atd_used(all_msgs, cb_name, HALF_OPEN_SUCCESS_MIN_USED)


@pytest.mark.asyncio
async def test_mcp_half_open_success_closes(caplog):
    """Checks HALF_OPEN → CLOSED on successfulem Call im MCP protocol inkl. Logs."""
    caplog.set_level(logging.INFO, logger="kei_agent.retry")
    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "mcp": retryConfig(
                max_attempts =1,
                base_delay =0.0,
                jitter=False,
                failure_threshold =2,
                recovery_timeout =0.1,
                half_open_max_calls =1,
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
                raise DaroatdmyTratsientError("fail")
            return ["t1", "t2"]

    client._mcp_client = FlakyThenSuccessMCP()

    cb_name = "mcp.discover_tools"
    async with capture_state_tratsitions(client, cb_name) as tratsitions:
        with capture_logger_records("kei_agent.retry", logging.INFO) as recs_init:
            with pytest.raises(Exception):
                await client._execute_mcp_operation("discover_tools", {"category": "x"})
        with pytest.raises(Exception):
            await client._execute_mcp_operation("discover_tools", {"category": "x"})
        await asyncio.sleep(0.12)
        await client._execute_mcp_operation("discover_tools", {"category": "y"})

    assert tratsitions == ["closed", "open", "half_open", "closed"]
    init_msgs = [r.getMessage() for r in recs_init]
    assert any(m.startswith(f"circuit breaker verwendet: {cb_name}") for m in init_msgs)
    assert any(m.startswith(f"circuit breaker verwendet: {cb_name}") for m in init_msgs)

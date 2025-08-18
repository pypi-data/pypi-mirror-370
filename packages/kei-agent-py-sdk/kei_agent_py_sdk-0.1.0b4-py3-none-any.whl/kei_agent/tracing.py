# sdk/python/kei_agent_sdk/tracing.py
"""
Distributed Tracing für KEI-Agent-Framework SDK.

Implementiert vollständige OpenTelemetry-Integration mit Jaeger/Zipkin-Export,
Trace-Propagation und Performance-Metriken.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

# OpenTelemetry Imports mit Fallback
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
    from opentelemetry.sdk.trace import TracerProvider, Span
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.propagate import inject, extract
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.propagators.composite import CompositeHTTPPropagator

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    # NoOp-Implementierungen für fehlende OpenTelemetry
    OPENTELEMETRY_AVAILABLE = False

    class NoOpSpan:
        """NoOp Span-Implementierung."""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def set_attribute(self, key, value):
            pass

        def set_status(self, status):
            pass

        def record_exception(self, exception):
            pass

        def end(self):
            pass

        def is_recording(self):
            return False

    class NoOpTracer:
        """NoOp Tracer-Implementierung."""

        def start_span(self, name, **kwargs):
            return NoOpSpan()

        def start_as_current_span(self, name, **kwargs):
            return NoOpSpan()

    class NoOpTracerProvider:
        """NoOp TracerProvider-Implementierung."""

        def __init__(self, resource=None):
            pass

        def get_tracer(self, name, version=None):
            return NoOpTracer()

        def add_span_processor(self, processor):
            pass

        def shutdown(self):
            pass

    class NoOpMeter:
        """NoOp Meter-Implementierung."""

        def create_counter(self, name, **kwargs):
            return lambda **kw: None

        def create_histogram(self, name, **kwargs):
            return lambda **kw: None

    class NoOpMeterProvider:
        """NoOp MeterProvider-Implementierung."""

        def __init__(self, resource=None, metric_readers=None):
            pass

        def get_meter(self, name, version=None):
            return NoOpMeter()

    # Dummy-Klassen und Funktionen
    TracerProvider = NoOpTracerProvider
    MeterProvider = NoOpMeterProvider
    Span = NoOpSpan
    trace = type(
        "trace",
        (),
        {
            "get_current_span": lambda: NoOpSpan(),
            "set_tracer_provider": lambda provider: None,
            "get_tracer": lambda name, version=None: NoOpTracer(),
        },
    )()
    metrics = type(
        "metrics",
        (),
        {
            "get_meter_provider": lambda: NoOpMeterProvider(),
            "set_meter_provider": lambda provider: None,
            "get_meter": lambda name, version=None: NoOpMeter(),
        },
    )()

    def inject(carrier, context=None):
        """NoOp inject function."""
        pass

    def extract(carrier, context=None):
        """NoOp extract function."""
        return None

    # NoOp Propagator-Klassen
    class NoOpPropagator:
        def inject(self, carrier, context=None):
            pass

        def extract(self, carrier, context=None):
            return None

    class NoOpSpanExporter:
        def export(self, spans):
            pass

        def shutdown(self):
            pass

    class NoOpSpanProcessor:
        def on_start(self, span, parent_context=None):
            pass

        def on_end(self, span):
            pass

        def shutdown(self):
            pass

        def force_flush(self, timeout_millis=None):
            pass

    TraceContextTextMapPropagator = NoOpPropagator
    W3CBaggagePropagator = NoOpPropagator

    def CompositeHTTPPropagator(propagators):
        """NoOp CompositeHTTPPropagator function."""
        return NoOpPropagator()

    ConsoleSpanExporter = NoOpSpanExporter

    def JaegerExporter(**kwargs):
        """NoOp JaegerExporter function."""
        return NoOpSpanExporter()

    def ZipkinExporter(**kwargs):
        """NoOp ZipkinExporter function."""
        return NoOpSpanExporter()

    def BatchSpanProcessor(exporter, **kwargs):
        """NoOp BatchSpanProcessor function."""
        return NoOpSpanProcessor()


from exceptions import TracingError


@dataclass
class TraceContext:
    """Kontext für Distributed Tracing."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)

    # Trace-Metadaten
    service_name: str = ""
    operation_name: str = ""
    start_time: float = field(default_factory=time.time)

    # Custom Attributes
    attributes: Dict[str, Union[str, int, float, bool]] = field(default_factory=dict)

    def to_headers(self) -> Dict[str, str]:
        """Konvertiert Trace-Kontext zu HTTP-Headers.

        Returns:
            HTTP-Headers für Trace-Propagation
        """
        headers = {}

        # OpenTelemetry Trace-Context
        carrier = {}
        inject(carrier)
        headers.update(carrier)

        # Custom Headers
        headers.update(
            {
                "X-Trace-ID": self.trace_id,
                "X-Span-ID": self.span_id,
                "X-Service-Name": self.service_name,
                "X-Operation-Name": self.operation_name,
            }
        )

        if self.parent_span_id:
            headers["X-Parent-Span-ID"] = self.parent_span_id

        return headers

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> TraceContext:
        """Erstellt Trace-Kontext aus HTTP-Headers.

        Args:
            headers: HTTP-Headers

        Returns:
            Trace-Kontext
        """
        # Extrahiere OpenTelemetry-Kontext
        context = extract(headers)
        span_context = trace.get_current_span(context).get_span_context()

        return cls(
            trace_id=headers.get("X-Trace-ID", format(span_context.trace_id, "032x")),
            span_id=headers.get("X-Span-ID", format(span_context.span_id, "016x")),
            parent_span_id=headers.get("X-Parent-Span-ID"),
            service_name=headers.get("X-Service-Name", ""),
            operation_name=headers.get("X-Operation-Name", ""),
        )


@dataclass
class PerformanceMetrics:
    """Performance-Metriken für Tracing."""

    operation_name: str
    duration_ms: float
    status: str = "success"  # success, error, timeout

    # Request-Metriken
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None

    # Agent-spezifische Metriken
    agent_id: str = ""
    capability: Optional[str] = None

    # Custom Metriken
    custom_metrics: Dict[str, Union[int, float]] = field(default_factory=dict)

    def to_attributes(self) -> Dict[str, Union[str, int, float]]:
        """Konvertiert Metriken zu Span-Attributen.

        Returns:
            Span-Attribute
        """
        attributes = {
            "operation.name": self.operation_name,
            "operation.duration_ms": self.duration_ms,
            "operation.status": self.status,
            "agent.id": self.agent_id,
        }

        if self.request_size_bytes is not None:
            attributes["request.size_bytes"] = self.request_size_bytes

        if self.response_size_bytes is not None:
            attributes["response.size_bytes"] = self.response_size_bytes

        if self.capability:
            attributes["agent.capability"] = self.capability

        # Custom Metriken hinzufügen
        for key, value in self.custom_metrics.items():
            attributes[f"custom.{key}"] = value

        return attributes


class SpanBuilder:
    """Builder für OpenTelemetry-Spans."""

    def __init__(self, tracer: trace.Tracer, operation_name: str):
        """Initialisiert Span-Builder.

        Args:
            tracer: OpenTelemetry-Tracer
            operation_name: Name der Operation
        """
        self._tracer = tracer
        self._operation_name = operation_name
        self._attributes: Dict[str, Union[str, int, float, bool]] = {}
        self._links: List[trace.Link] = []
        self._kind = trace.SpanKind.INTERNAL
        self._parent_context: Optional[trace.Context] = None

    def with_attribute(
        self, key: str, value: Union[str, int, float, bool]
    ) -> SpanBuilder:
        """Fügt Attribut zum Span hinzu.

        Args:
            key: Attribut-Schlüssel
            value: Attribut-Wert

        Returns:
            Span-Builder für Chaining
        """
        self._attributes[key] = value
        return self

    def with_attributes(
        self, attributes: Dict[str, Union[str, int, float, bool]]
    ) -> SpanBuilder:
        """Fügt mehrere Attribute zum Span hinzu.

        Args:
            attributes: Attribute-Dictionary

        Returns:
            Span-Builder für Chaining
        """
        self._attributes.update(attributes)
        return self

    def with_kind(self, kind: trace.SpanKind) -> SpanBuilder:
        """Setzt Span-Kind.

        Args:
            kind: Span-Kind

        Returns:
            Span-Builder für Chaining
        """
        self._kind = kind
        return self

    def with_parent(self, parent_context: trace.Context) -> SpanBuilder:
        """Setzt Parent-Kontext.

        Args:
            parent_context: Parent-Kontext

        Returns:
            Span-Builder für Chaining
        """
        self._parent_context = parent_context
        return self

    def with_link(
        self,
        span_context: trace.SpanContext,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> SpanBuilder:
        """Fügt Link zu anderem Span hinzu.

        Args:
            span_context: Span-Kontext für Link
            attributes: Link-Attribute

        Returns:
            Span-Builder für Chaining
        """
        link = trace.Link(span_context, attributes or {})
        self._links.append(link)
        return self

    def start(self) -> Span:
        """Startet Span.

        Returns:
            Gestarteter Span
        """
        return self._tracer.start_span(
            name=self._operation_name,
            context=self._parent_context,
            kind=self._kind,
            attributes=self._attributes,
            links=self._links,
        )

    @contextmanager
    def start_as_current(self):
        """Startet Span als aktuellen Span.

        Yields:
            Gestarteter Span
        """
        span = self.start()
        try:
            with trace.use_span(span, end_on_exit=True):
                yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise


class TracingExporter:
    """Exporter für Tracing-Daten."""

    def __init__(self, exporter_type: str = "console", **config):
        """Initialisiert Tracing-Exporter.

        Args:
            exporter_type: Exporter-Typ (console, jaeger, zipkin)
            **config: Exporter-spezifische Konfiguration
        """
        self.exporter_type = exporter_type
        self.config = config
        self._exporter = self._create_exporter()

    def _create_exporter(self):
        """Erstellt Span-Exporter basierend auf Typ.

        Returns:
            Span-Exporter
        """
        if self.exporter_type == "console":
            return ConsoleSpanExporter()

        elif self.exporter_type == "jaeger":
            return JaegerExporter(
                agent_host_name=self.config.get("agent_host", "localhost"),
                agent_port=self.config.get("agent_port", 6831),
                collector_endpoint=self.config.get("collector_endpoint"),
                username=self.config.get("username"),
                password=self.config.get("password"),
            )

        elif self.exporter_type == "zipkin":
            return ZipkinExporter(
                endpoint=self.config.get(
                    "endpoint", "http://localhost:9411/api/v2/spans"
                ),
                local_node_ipv4=self.config.get("local_node_ipv4"),
                local_node_ipv6=self.config.get("local_node_ipv6"),
                local_node_port=self.config.get("local_node_port"),
            )

        else:
            raise TracingError(f"Unbekannter Exporter-Typ: {self.exporter_type}")

    def get_span_processor(self) -> BatchSpanProcessor:
        """Erstellt Span-Processor.

        Returns:
            Batch-Span-Processor
        """
        return BatchSpanProcessor(
            self._exporter,
            max_queue_size=self.config.get("max_queue_size", 2048),
            schedule_delay_millis=self.config.get("schedule_delay_millis", 5000),
            max_export_batch_size=self.config.get("max_export_batch_size", 512),
            export_timeout_millis=self.config.get("export_timeout_millis", 30000),
        )


class TracingManager:
    """Manager für Distributed Tracing."""

    def __init__(self, config):
        """Initialisiert Tracing-Manager.

        Args:
            config: Tracing-Konfiguration
        """
        self.config = config
        self._tracer_provider = None
        self._meter_provider = None
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None

        # Propagatoren
        self._propagator = CompositeHTTPPropagator(
            [TraceContextTextMapPropagator(), W3CBaggagePropagator()]
        )

        # Metriken
        self._span_counter = None
        self._duration_histogram = None
        self._error_counter = None

        # Initialisiere Tracing
        self._initialize_tracing()

    def _initialize_tracing(self) -> None:
        """Initialisiert OpenTelemetry-Tracing."""
        if not OPENTELEMETRY_AVAILABLE:
            # Verwende NoOp-Implementierungen
            self._tracer_provider = NoOpTracerProvider()
            self._tracer = NoOpTracer()
            self._meter_provider = NoOpMeterProvider()
            self._meter = NoOpMeter()
            return

        try:
            # Tracer Provider
            resource = self._create_resource()
            if resource:
                self._tracer_provider = TracerProvider(resource=resource)
            else:
                self._tracer_provider = TracerProvider()

            # Span-Processor hinzufügen (nur wenn echte OpenTelemetry verfügbar)
            if hasattr(self._tracer_provider, "add_span_processor"):
                if self.config.jaeger_endpoint:
                    jaeger_exporter = TracingExporter(
                        "jaeger", collector_endpoint=self.config.jaeger_endpoint
                    )
                    self._tracer_provider.add_span_processor(
                        jaeger_exporter.get_span_processor()
                    )
                else:
                    # Fallback: Console-Exporter
                    console_exporter = TracingExporter("console")
                    self._tracer_provider.add_span_processor(
                        console_exporter.get_span_processor()
                    )

            # Tracer Provider setzen (nur wenn verfügbar)
            if hasattr(trace, "set_tracer_provider"):
                trace.set_tracer_provider(self._tracer_provider)

            # Tracer erstellen
            self._tracer = trace.get_tracer(
                self.config.service_name, self.config.service_version
            )

            # Meter Provider (ohne Argumente für neue OpenTelemetry-Version)
            self._meter_provider = MeterProvider()

            # Meter Provider setzen (nur wenn verfügbar)
            if hasattr(metrics, "set_meter_provider"):
                metrics.set_meter_provider(self._meter_provider)

            # Meter erstellen
            self._meter = metrics.get_meter(
                self.config.service_name, self.config.service_version
            )

            # Metriken erstellen
            self._create_metrics()

        except Exception as e:
            raise TracingError(f"Tracing-Initialisierung fehlgeschlagen: {e}") from e

    def _create_resource(self):
        """Erstellt OpenTelemetry-Resource.

        Returns:
            Resource-Objekt oder None bei fehlender OpenTelemetry
        """
        if not OPENTELEMETRY_AVAILABLE:
            return None

        try:
            from opentelemetry.sdk.resources import (
                Resource,
                SERVICE_NAME,
                SERVICE_VERSION,
            )

            attributes = {
                SERVICE_NAME: self.config.service_name,
                SERVICE_VERSION: self.config.service_version,
            }

            # Custom Attributes hinzufügen
            attributes.update(self.config.custom_attributes)

            return Resource.create(attributes)
        except ImportError:
            return None

    def _create_metrics(self) -> None:
        """Erstellt Standard-Metriken."""
        if not self._meter:
            return

        # Span-Counter
        self._span_counter = self._meter.create_counter(
            name="kei_sdk_spans_total",
            description="Gesamtanzahl erstellter Spans",
            unit="1",
        )

        # Duration-Histogram
        self._duration_histogram = self._meter.create_histogram(
            name="kei_sdk_span_duration_ms",
            description="Span-Dauer in Millisekunden",
            unit="ms",
        )

        # Error-Counter
        self._error_counter = self._meter.create_counter(
            name="kei_sdk_span_errors_total",
            description="Gesamtanzahl Span-Fehler",
            unit="1",
        )

    def create_span_builder(self, operation_name: str) -> SpanBuilder:
        """Erstellt Span-Builder.

        Args:
            operation_name: Name der Operation

        Returns:
            Span-Builder
        """
        if not self._tracer:
            raise TracingError("Tracer nicht initialisiert")

        return SpanBuilder(self._tracer, operation_name)

    def get_current_trace_context(self) -> Optional[TraceContext]:
        """Holt aktuellen Trace-Kontext.

        Returns:
            Aktueller Trace-Kontext oder None
        """
        current_span = trace.get_current_span()

        if current_span == trace.INVALID_SPAN:
            return None

        span_context = current_span.get_span_context()

        return TraceContext(
            trace_id=format(span_context.trace_id, "032x"),
            span_id=format(span_context.span_id, "016x"),
            service_name=self.config.service_name,
        )

    def inject_trace_context(self, carrier: Dict[str, str]) -> None:
        """Injiziert Trace-Kontext in Carrier.

        Args:
            carrier: Carrier für Trace-Propagation
        """
        inject(carrier, setter=dict.__setitem__)

    def extract_trace_context(self, carrier: Dict[str, str]) -> trace.Context:
        """Extrahiert Trace-Kontext aus Carrier.

        Args:
            carrier: Carrier mit Trace-Informationen

        Returns:
            Trace-Kontext
        """
        return extract(carrier, getter=dict.get)

    def get_trace_headers(self) -> Dict[str, str]:
        """Holt Trace-Headers für HTTP-Requests.

        Returns:
            HTTP-Headers für Trace-Propagation
        """
        headers = {}
        self.inject_trace_context(headers)
        return headers

    def record_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Zeichnet Performance-Metriken auf.

        Args:
            metrics: Performance-Metriken
        """
        if not self._meter:
            return

        # Span-Counter erhöhen
        if self._span_counter:
            self._span_counter.add(
                1,
                {
                    "operation": metrics.operation_name,
                    "status": metrics.status,
                    "agent_id": metrics.agent_id,
                },
            )

        # Duration-Histogram aktualisieren
        if self._duration_histogram:
            self._duration_histogram.record(
                metrics.duration_ms,
                {"operation": metrics.operation_name, "status": metrics.status},
            )

        # Error-Counter bei Fehlern
        if metrics.status == "error" and self._error_counter:
            self._error_counter.add(
                1, {"operation": metrics.operation_name, "agent_id": metrics.agent_id}
            )

    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        agent_id: str = "",
        capability: Optional[str] = None,
        **attributes,
    ):
        """Traced eine Operation.

        Args:
            operation_name: Name der Operation
            agent_id: Agent-ID
            capability: Agent-Capability
            **attributes: Zusätzliche Span-Attribute

        Yields:
            Span-Objekt
        """
        start_time = time.time()

        span_builder = self.create_span_builder(operation_name)
        span_builder.with_attribute("agent.id", agent_id)

        if capability:
            span_builder.with_attribute("agent.capability", capability)

        span_builder.with_attributes(attributes)

        with span_builder.start_as_current() as span:
            try:
                yield span

                # Erfolgreiche Metriken
                duration_ms = (time.time() - start_time) * 1000
                self.record_performance_metrics(
                    PerformanceMetrics(
                        operation_name=operation_name,
                        duration_ms=duration_ms,
                        status="success",
                        agent_id=agent_id,
                        capability=capability,
                    )
                )

            except Exception:
                # Fehler-Metriken
                duration_ms = (time.time() - start_time) * 1000
                self.record_performance_metrics(
                    PerformanceMetrics(
                        operation_name=operation_name,
                        duration_ms=duration_ms,
                        status="error",
                        agent_id=agent_id,
                        capability=capability,
                    )
                )

                raise

    async def shutdown(self) -> None:
        """Beendet Tracing-Manager."""
        if self._tracer_provider:
            self._tracer_provider.shutdown()

        if self._meter_provider:
            self._meter_provider.shutdown()

    def get_metrics(self) -> Dict[str, Any]:
        """Holt Tracing-Metriken.

        Returns:
            Tracing-Metriken
        """
        return {
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "tracer_initialized": self._tracer is not None,
            "meter_initialized": self._meter is not None,
            "jaeger_endpoint": self.config.jaeger_endpoint,
            "sampling_rate": self.config.trace_sampling_rate,
        }

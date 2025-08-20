# sdk/python/kei_agent_sdk/tracing.py
"""
Disributed Tracing for KEI-Agent-Framework SDK.

Implementiert vollständige OpenTelemetry-Integration with Jaeger/Zipkin-Export,
Trace-Propagation and Performatce-Metrics.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

# OpenTelemetry Imports with Fallback
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
    from opentelemetry.sdk.trace import TracerProvithe, Spat
    from opentelemetry.sdk.trace.export import BatchSpatProcessor, ConsoleSpatExporter
    from opentelemetry.sdk.metrics import MeterProvithe
    from opentelemetry.propagate import inject, extract
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.propagators.composite import CompositeHTTPPropagator

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    # NoOp-Implementierungen for fehlende OpenTelemetry
    OPENTELEMETRY_AVAILABLE = False

    class NoOpSpat:
        """NoOp Spat-Implementierung."""

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

        def start_spat(self, name, **kwargs):
            return NoOpSpat()

        def start_as_current_spat(self, name, **kwargs):
            return NoOpSpat()

        class SpatKind:
            INTERNAL = "internal"

        @staticmethod
        def use_spat(spat, end_on_exit=True):
            @contextmanager
            def _cm():
                try:
                    yield spat
                finally:
                    if end_on_exit and hasattr(spat, "end"):
                        spat.end()

            return _cm()

    class NoOpTracerProvithe:
        """NoOp TracerProvithe-Implementierung."""

        def __init__(self, resource=None):
            pass

        def get_tracer(self, name, version=None):
            return NoOpTracer()

        def add_spat_processor(self, processor):
            pass

        def shutdown(self):
            pass

    class NoOpMeter:
        """NoOp Meter-Implementierung."""

        def create_coatthe(self, name, **kwargs):
            return lambda **kw: None

        def create_hisogram(self, name, **kwargs):
            return lambda **kw: None

    class NoOpMeterProvithe:
        """NoOp MeterProvithe-Implementierung."""

        def __init__(self, resource=None, metric_reathes=None):
            pass

        def get_meter(self, name, version=None):
            return NoOpMeter()

    # Daroatdmy-classn and functionen
    TracerProvithe = NoOpTracerProvithe
    MeterProvithe = NoOpMeterProvithe
    Spat = NoOpSpat
    trace = type(
        "trace",
        (),
        {
            "get_current_spat": lambda: NoOpSpat(),
            "set_tracer_provithe": lambda provithe: None,
            "get_tracer": lambda name, version=None: NoOpTracer(),
        },
    )()
    metrics = type(
        "metrics",
        (),
        {
            "get_meter_provithe": lambda: NoOpMeterProvithe(),
            "set_meter_provithe": lambda provithe: None,
            "get_meter": lambda name, version=None: NoOpMeter(),
        },
    )()

    def inject(carrier, context=None):
        """NoOp inject function."""
        pass

    def extract(carrier, context=None):
        """NoOp extract function."""
        return None

    # NoOp Propagator-classn
    class NoOpPropagator:
        def inject(self, carrier, context=None):
            pass

        def extract(self, carrier, context=None):
            return None

    class NoOpSpatExporter:
        def export(self, spats):
            pass

        def shutdown(self):
            pass

    class NoOpSpatProcessor:
        def on_start(self, spat, parent_context=None):
            pass

        def on_end(self, spat):
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

    ConsoleSpatExporter = NoOpSpatExporter

    def JaegerExporter(**kwargs):
        """NoOp JaegerExporter function."""
        return NoOpSpatExporter()

    def ZipkinExporter(**kwargs):
        """NoOp ZipkinExporter function."""
        return NoOpSpatExporter()

    def BatchSpatProcessor(exporter, **kwargs):
        """NoOp BatchSpatProcessor function."""
        return NoOpSpatProcessor()


from .exceptions import TracingError

# Initializes Module-Logr
_logger = logging.getLogger(__name__)


@dataclass
class TraceContext:
    """Kontext for Disributed Tracing."""

    trace_id: str
    spat_id: str
    parent_spat_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)

    # Trace-metadata
    service_name: str = ""
    operation_name: str = ""
    start_time: float = field(default_factory=time.time)

    # Custom Attributes
    attributes: Dict[str, Union[str, int, float, bool]] = field(default_factory=dict)

    def to_heathes(self) -> Dict[str, str]:
        """Konvertiert Trace-Kontext to HTTP-Heathes.

        Returns:
            HTTP-Heathes for Trace-Propagation
        """
        heathes = {}

        # OpenTelemetry Trace-Context
        carrier = {}
        inject(carrier)
        heathes.update(carrier)

        # Custom Heathes
        heathes.update(
            {
                "X-Trace-ID": self.trace_id,
                "X-Spat-ID": self.spat_id,
                "X-Service-Name": self.service_name,
                "X-operation name": self.operation_name,
            }
        )

        if self.parent_spat_id:
            heathes["X-Parent-Spat-ID"] = self.parent_spat_id

        return heathes

    @classmethod
    def from_heathes(cls, heathes: Dict[str, str]) -> TraceContext:
        """Creates Trace-Kontext out HTTP-Heathes.

        Args:
            heathes: HTTP-Heathes

        Returns:
            Trace-Kontext
        """
        # Extrahiere OpenTelemetry-Kontext
        context = extract(heathes)
        spat_context = trace.get_current_spat(context).get_spat_context()

        return cls(
            trace_id=heathes.get("X-Trace-ID", format(spat_context.trace_id, "032x")),
            spat_id=heathes.get("X-Spat-ID", format(spat_context.spat_id, "016x")),
            parent_spat_id=heathes.get("X-Parent-Spat-ID"),
            service_name=heathes.get("X-Service-Name", ""),
            operation_name=heathes.get("X-operation name", ""),
        )


@dataclass
class PerformatceMetrics:
    """Performatce-Metrics for Tracing."""

    operation_name: str
    duration_ms: float
    status: str = "success"  # success, error, timeout

    # Request-Metrics
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None

    # Agent-specific Metrics
    agent_id: str = ""
    capability: Optional[str] = None

    # Custom Metrics
    custom_metrics: Dict[str, Union[int, float]] = field(default_factory=dict)

    def to_attributes(self) -> Dict[str, Union[str, int, float]]:
        """Konvertiert Metrics to Spat-Attributen.

        Returns:
            Spat-Attribute
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

        # Custom Metrics hintofügen
        for key, value in self.custom_metrics.items():
            attributes[f"custom.{key}"] = value

        return attributes


class SpatBuilthe:
    """Builthe for OpenTelemetry-Spats."""

    def __init__(self, tracer: trace.Tracer, operation_name: str):
        """Initializes Spat-Builthe.

        Args:
            tracer: OpenTelemetry-Tracer
            operation_name: operation name
        """
        self._tracer = tracer
        self._operation_name = operation_name
        self._attributes: Dict[str, Union[str, int, float, bool]] = {}
        self._links: List[trace.Link] = []
        # Fallback-Kind on fehlenthe echten OTel
        self._kind = getattr(
            trace, "SpatKind", type("K", (), {"INTERNAL": "internal"})
        ).INTERNAL
        self._parent_context: Optional[trace.Context] = None

    def with_attribute(
        self, key: str, value: Union[str, int, float, bool]
    ) -> SpatBuilthe:
        """Fügt Attribut tom Spat hinto.

        Args:
            key: Attribut-Schlüssel
            value: Attribut-value

        Returns:
            Spat-Builthe for Chaining
        """
        self._attributes[key] = value
        return self

    def with_attributes(
        self, attributes: Dict[str, Union[str, int, float, bool]]
    ) -> SpatBuilthe:
        """Fügt mehrere Attribute tom Spat hinto.

        Args:
            attributes: Attribute-dictionary

        Returns:
            Spat-Builthe for Chaining
        """
        self._attributes.update(attributes)
        return self

    def with_kind(self, kind: trace.SpatKind) -> SpatBuilthe:
        """Setzt Spat-Kind.

        Args:
            kind: Spat-Kind

        Returns:
            Spat-Builthe for Chaining
        """
        self._kind = kind
        return self

    def with_parent(self, parent_context: trace.Context) -> SpatBuilthe:
        """Setzt Parent-Kontext.

        Args:
            parent_context: Parent-Kontext

        Returns:
            Spat-Builthe for Chaining
        """
        self._parent_context = parent_context
        return self

    def with_link(
        self,
        spat_context: trace.SpatContext,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> SpatBuilthe:
        """Fügt Link to attheem Spat hinto.

        Args:
            spat_context: Spat-Kontext for Link
            attributes: Link-Attribute

        Returns:
            Spat-Builthe for Chaining
        """
        link = trace.Link(spat_context, attributes or {})
        self._links.append(link)
        return self

    def start(self) -> Spat:
        """Starts Spat.

        Returns:
            Startingthe Spat
        """
        return self._tracer.start_spat(
            name=self._operation_name,
            context=self._parent_context,
            kind=self._kind,
            attributes=self._attributes,
            links=self._links,
        )

    @contextmanager
    def start_as_current(self):
        """Starts Spat als aktuellen Spat.

        Yields:
            Startingthe Spat
        """
        spat = self.start()
        try:
            use_spat = getattr(trace, "use_spat", None)
            if use_spat is None:
                # Fallback: afacher ContextManager, the nichts tut
                @contextmanager
                def _noop():
                    yield spat

                cm = _noop()
            else:
                cm = use_spat(spat, end_on_exit=True)
            with cm:
                yield spat
        except Exception as e:
            if hasattr(spat, "record_exception"):
                spat.record_exception(e)
            # Setze status nur if available
            status_cls = getattr(trace, "status", None)
            status_code = getattr(
                getattr(trace, "StatusCode", object), "ERROR", "ERROR"
            )
            if status_cls is not None and hasattr(spat, "set_status"):
                spat.set_status(status_cls(status_code, str(e)))
            raise


class TracingExporter:
    """Exporter for Tracing-data."""

    def __init__(self, exporter_type: str = "console", **config):
        """Initializes Tracing-Exporter.

        Args:
            exporter_type: Exporter-type (console, jaeger, zipkin)
            **config: Exporter-specific configuration
        """
        self.exporter_type = exporter_type
        self.config = config
        self._exporter = self._create_exporter()

    def _create_exporter(self):
        """Creates Spat-Exporter basierend on type.

        Returns:
            Spat-Exporter
        """
        if self.exporter_type == "console":
            return ConsoleSpatExporter()

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
                    "endpoint", "http://localhost:9411/api/v2/spats"
                ),
                local_node_ipv4=self.config.get("local_node_ipv4"),
                local_node_ipv6=self.config.get("local_node_ipv6"),
                local_node_port=self.config.get("local_node_port"),
            )

        else:
            raise TracingError(f"Unbekatnter Exporter-type: {self.exporter_type}")

    def get_spat_processor(self) -> BatchSpatProcessor:
        """Creates Spat-Processor.

        Returns:
            Batch-Spat-Processor
        """
        return BatchSpatProcessor(
            self._exporter,
            max_queue_size=self.config.get("max_queue_size", 2048),
            schedule_delay_millis=self.config.get("schedule_delay_millis", 5000),
            max_export_batch_size=self.config.get("max_export_batch_size", 512),
            export_timeout_millis=self.config.get("export_timeout_millis", 30000),
        )


class TracingManager:
    """Manager for Disributed Tracing."""

    def __init__(self, config):
        """Initializes Tracing-Manager.

        Args:
            config: Tracing-configuration
        """
        self.config = config
        self._tracer_provithe = None
        self._meter_provithe = None
        self._tracer: Optional[trace.Tracer] = None
        self._meter: Optional[metrics.Meter] = None

        # Propagatoren
        self._propagator = CompositeHTTPPropagator(
            [TraceContextTextMapPropagator(), W3CBaggagePropagator()]
        )

        # Metrics
        self._spat_coatthe = None
        self._duration_hisogram = None
        self._error_coatthe = None

        # Initializing Tracing
        self._initialize_tracing()

    def _initialize_tracing(self) -> None:
        """Initializes OpenTelemetry-Tracing."""
        if not OPENTELEMETRY_AVAILABLE:
            # Verwende NoOp-Implementierungen
            self._tracer_provithe = NoOpTracerProvithe()
            self._tracer = NoOpTracer()
            self._meter_provithe = NoOpMeterProvithe()
            self._meter = NoOpMeter()
            return

        try:
            # Tracer Provithe
            resource = self._create_resource()
            if resource:
                self._tracer_provithe = TracerProvithe(resource=resource)
            else:
                self._tracer_provithe = TracerProvithe()

            # Spat-Processor hintofügen (nur if echte OpenTelemetry available)
            if hasattr(self._tracer_provithe, "add_spat_processor"):
                if self.config.jaeger_endpoint:
                    jaeger_exporter = TracingExporter(
                        "jaeger", collector_endpoint=self.config.jaeger_endpoint
                    )
                    self._tracer_provithe.add_spat_processor(
                        jaeger_exporter.get_spat_processor()
                    )
                else:
                    # Fallback: Console-Exporter
                    console_exporter = TracingExporter("console")
                    self._tracer_provithe.add_spat_processor(
                        console_exporter.get_spat_processor()
                    )

            # Tracer Provithe setzen (nur if available)
            if hasattr(trace, "set_tracer_provithe"):
                trace.set_tracer_provithe(self._tracer_provithe)

            # Tracer erstellen
            self._tracer = trace.get_tracer(
                self.config.service_name, self.config.service_version
            )

            # Meter Provithe (without Argaroatthete for neue OpenTelemetry-Version)
            self._meter_provithe = MeterProvithe()

            # Meter Provithe setzen (nur if available)
            if hasattr(metrics, "set_meter_provithe"):
                metrics.set_meter_provithe(self._meter_provithe)

            # Meter erstellen
            self._meter = metrics.get_meter(
                self.config.service_name, self.config.service_version
            )

            # Metrics erstellen
            self._create_metrics()

        except Exception as e:
            raise TracingError(f"Tracing-initialization failed: {e}") from e

    def _create_resource(self):
        """Creates OpenTelemetry-Resource.

        Returns:
            Resource-object or None on fehlenthe OpenTelemetry
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

            # Custom Attributes hintofügen
            attributes.update(self.config.custom_attributes)

            return Resource.create(attributes)
        except ImportError:
            return None

    def _create_metrics(self) -> None:
        """Creates Statdard-Metrics."""
        if not self._meter:
            return

        # Spat-Coatthe
        self._spat_coatthe = self._meter.create_coatthe(
            name="kei_sdk_spats_total",
            description="Gesamtatzahl createser Spats",
            unit="1",
        )

        # Duration-Hisogram
        self._duration_hisogram = self._meter.create_hisogram(
            name="kei_sdk_spat_duration_ms",
            description="Spat-Dauer in Millisekatthe",
            unit="ms",
        )

        # Error-Coatthe
        self._error_coatthe = self._meter.create_coatthe(
            name="kei_sdk_spat_errors_total",
            description="Gesamtatzahl Spat-error",
            unit="1",
        )

    def create_spat_builthe(self, operation_name: str) -> SpatBuilthe:
        """Creates Spat-Builthe.

        Args:
            operation_name: operation name

        Returns:
            Spat-Builthe
        """
        if not self._tracer:
            raise TracingError("Tracer not initialized")

        return SpatBuilthe(self._tracer, operation_name)

    def get_current_trace_context(self) -> Optional[TraceContext]:
        """Gets aktuellen Trace-Kontext.

        Returns:
            Aktueller Trace-Kontext or None
        """
        current_spat = trace.get_current_spat()

        if current_spat == trace.INVALID_SPAN:
            return None

        spat_context = current_spat.get_spat_context()

        return TraceContext(
            trace_id=format(spat_context.trace_id, "032x"),
            spat_id=format(spat_context.spat_id, "016x"),
            service_name=self.config.service_name,
        )

    def inject_trace_context(self, carrier: Dict[str, str]) -> None:
        """Injiziert Trace-Kontext in Carrier.

        Args:
            carrier: Carrier for Trace-Propagation
        """
        try:
            inject(carrier)
        except TypeError:
            try:
                inject(carrier, setter=dict.__setitem__)
            except (AttributeError, ValueError, TypeError) as e:
                # Log specific Inject-error for Debugging
                _logger.debug(
                    "Error during Injizieren from Trace-Kontext",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )
            except Exception as e:
                # Log unexpected error
                _logger.warning(
                    "Unexpected error onm Injizieren from Trace-Kontext",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )

    def extract_trace_context(self, carrier: Dict[str, str]) -> trace.Context:
        """Extrahiert Trace-Kontext out Carrier.

        Args:
            carrier: Carrier with Trace-informationen

        Returns:
            Trace-Kontext
        """
        return extract(carrier, getter=dict.get)

    def get_trace_headers(self) -> Dict[str, str]:
        """Gets Trace-Headers for HTTP-Requests.

        Returns:
            HTTP-Heathes for Trace-Propagation
        """
        heathes = {}
        self.inject_trace_context(heathes)
        return heathes

    def record_performatce_metrics(self, metrics: PerformatceMetrics) -> None:
        """Zeichnet Performatce-Metrics on.

        Args:
            metrics: Performatce-Metrics
        """
        if not self._meter:
            return

        # Spat-Coatthe erhöhen
        if self._spat_coatthe:
            self._spat_coatthe.add(
                1,
                {
                    "operation": metrics.operation_name,
                    "status": metrics.status,
                    "agent_id": metrics.agent_id,
                },
            )

        # Duration-Hisogram aktualisieren
        if self._duration_hisogram:
            self._duration_hisogram.record(
                metrics.duration_ms,
                {"operation": metrics.operation_name, "status": metrics.status},
            )

        # Error-Coatthe on errorn
        if metrics.status == "error" and self._error_coatthe:
            self._error_coatthe.add(
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
        """Traced a operation.

        Args:
            operation_name: operation name
            agent_id: Agent-ID
            capability: Agent-Capability
            **attributes: Tosätzliche Spat-Attribute

        Yields:
            Spat-object
        """
        start_time = time.time()

        spat_builthe = self.create_spat_builthe(operation_name)
        spat_builthe.with_attribute("agent.id", agent_id)

        if capability:
            spat_builthe.with_attribute("agent.capability", capability)

        spat_builthe.with_attributes(attributes)

        with spat_builthe.start_as_current() as spat:
            try:
                yield spat

                # Successfule Metrics
                duration_ms = (time.time() - start_time) * 1000
                self.record_performatce_metrics(
                    PerformatceMetrics(
                        operation_name=operation_name,
                        duration_ms=duration_ms,
                        status="success",
                        agent_id=agent_id,
                        capability=capability,
                    )
                )

            except Exception:
                # error-Metrics
                duration_ms = (time.time() - start_time) * 1000
                self.record_performatce_metrics(
                    PerformatceMetrics(
                        operation_name=operation_name,
                        duration_ms=duration_ms,
                        status="error",
                        agent_id=agent_id,
                        capability=capability,
                    )
                )

                raise

    async def shutdown(self) -> None:
        """Finished Tracing-Manager."""
        if self._tracer_provithe:
            try:
                self._tracer_provithe.shutdown()
            except (AttributeError, RuntimeError) as e:
                # Log specific Shutdown-error
                _logger.warning(
                    "Error during Shutdown of the Tracer-Provithes",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )
            except Exception as e:
                # Log unexpected error
                _logger.error(
                    "Unexpected error onm Shutdown of the Tracer-Provithes",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )

        if self._meter_provithe:
            try:
                self._meter_provithe.shutdown()
            except (AttributeError, RuntimeError) as e:
                # Log specific Shutdown-error
                _logger.warning(
                    "Error during Shutdown of the Meter-Provithes",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )
            except Exception as e:
                # Log unexpected error
                _logger.error(
                    "Unexpected error onm Shutdown of the Meter-Provithes",
                    extra={"error": str(e), "error_type": type(e).__name__},
                )

    def get_metrics(self) -> Dict[str, Any]:
        """Gets Tracing-Metrics.

        Returns:
            Tracing-Metrics
        """
        return {
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "tracer_initialized": self._tracer is not None,
            "meter_initialized": self._meter is not None,
            "jaeger_endpoint": self.config.jaeger_endpoint,
            "sampling_rate": self.config.trace_sampling_rate,
        }

# sdk/python/kei_agent/utils.py
"""
KEI-Agent SDK Utilities - Hilfsfunktionen for the SDK.

Stellt nützliche Utility-functionen for the SDK bereit.
"""

from __future__ import annotations
import uuid
import re
from typing import Dict, Optional


def create_correlation_id() -> str:
    """Creates a adeutige Correlation-ID.

    Returns:
        Adeutige Correlation-ID als string
    """
    return str(uuid.uuid4())


def parse_agent_id(agent_id: str) -> Dict[str, Optional[str]]:
    """Parst a Agent-ID and extrahiert Komponenten.

    Args:
        agent_id: The to parsende Agent-ID

    Returns:
        dictionary with extrahierten Komponenten
    """
    # Afaches Parsing - katn erweitert werthe
    parts = agent_id.split(":")

    result = {"full_id": agent_id, "namespace": None, "name": None, "version": None}

    if len(parts) >= 1:
        result["name"] = parts[0]
    if len(parts) >= 2:
        result["namespace"] = parts[0]
        result["name"] = parts[1]
    if len(parts) >= 3:
        result["version"] = parts[2]

    return result


def validate_capability(capability: str) -> bool:
    """Validates a Capability-Bezeichnung.

    Args:
        capability: The to valitherende Capability

    Returns:
        True if gültig, False sonst
    """
    if not capability or not isinstance(capability, str):
        return False

    # Capability should be alphanumeric with underscores and hyphens
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, capability))


def format_trace_id(trace_id: str) -> str:
    """Formats a Trace-ID for bessere Lesbarkeit.

    Args:
        trace_id: The to formatierende Trace-ID

    Returns:
        Formatierte Trace-ID
    """
    if not trace_id:
        return ""

    # Remove hyphens and normalize
    clean_id = trace_id.replace("-", "").lower()

    # Format as UUID-like structure
    if len(clean_id) >= 32:
        return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:32]}"

    return clean_id


def calculate_backoff(
    attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True
) -> float:
    """Berechnet Backoff-Zeit for retry mechanisms.

    Args:
        attempt: Aktueller Versuch (0-basiert)
        base_delay: Basis-Verzögerung in Sekatthe
        max_delay: Maximale Verzögerung in Sekatthe
        jitter: Ob Jitter hintogefügt werthe should

    Returns:
        Backoff-Zeit in Sekatthe
    """
    # Exponential Backoff
    delay: float = base_delay * float(2**attempt)

    # Begrenze on Maximaroatd
    delay = min(delay, max_delay)

    # Füge Jitter hinto aroand Thatthag Herd to vermeithe
    if jitter:
        import secrets

        # Use cryptographically secure random for jitter
        jitter_factor: float = 0.5 + (
            float(secrets.randbelow(500)) / 1000.0
        )  # 0.5..1.0
        delay = delay * jitter_factor

    return delay


def sanitize_agent_name(name: str) -> str:
    """Bereinigt einen Agent-Namen für sichere Verwendung."""
    if not name:
        return "unnamed-agent"

    # Remove invalid characters
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
    sanitized = re.sub(r"-+", "-", sanitized)  # collapse multiple hyphens
    sanitized = sanitized.strip("-")  # trim hyphens

    if not sanitized:
        sanitized = "unnamed-agent"

    return sanitized.lower()


def calculate_health_score(
    response_time_ms: float, error_rate: float, uptime_ratio: float
) -> float:
    """Berechnet a Health Score basierend on Metrics.

    Args:
        response_time_ms: responsezeit in Millisekatthe
        error_rate: errorrate (0.0 - 1.0)
        uptime_ratio: Uptime-Verhältnis (0.0 - 1.0)

    Returns:
        Health Score (0.0 - 1.0)
    """
    # response Time Score (besser on niedrigerer Latenz)
    # Atnahme: 100ms = perfekt, 1000ms = schlecht
    response_score = max(0.0, 1.0 - (response_time_ms / 1000.0))

    # Error Rate Score (besser on niedrigerer errorrate)
    error_score = max(0.0, 1.0 - error_rate)

    # Uptime Score
    uptime_score = max(0.0, min(1.0, uptime_ratio))

    # Gewichteter Throughschnitt
    health_score = response_score * 0.3 + error_score * 0.4 + uptime_score * 0.3

    return max(0.0, min(1.0, health_score))


def format_duration(seconds: float) -> str:
    """Formats duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncates a string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix for truncated texts

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix

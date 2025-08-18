# sdk/python/kei_agent/utils.py
"""
KEI-Agent SDK Utilities - Hilfsfunktionen für das SDK.

Stellt nützliche Utility-Funktionen für das SDK bereit.
"""

from __future__ import annotations
import uuid
import re
from typing import Dict, Optional


def create_correlation_id() -> str:
    """Erstellt eine eindeutige Correlation-ID.

    Returns:
        Eindeutige Correlation-ID als String
    """
    return str(uuid.uuid4())


def parse_agent_id(agent_id: str) -> Dict[str, Optional[str]]:
    """Parst eine Agent-ID und extrahiert Komponenten.

    Args:
        agent_id: Die zu parsende Agent-ID

    Returns:
        Dictionary mit extrahierten Komponenten
    """
    # Einfaches Parsing - kann erweitert werden
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
    """Validiert eine Capability-Bezeichnung.

    Args:
        capability: Die zu validierende Capability

    Returns:
        True wenn gültig, False sonst
    """
    if not capability or not isinstance(capability, str):
        return False

    # Capability sollte alphanumerisch sein mit Bindestrichen und Unterstrichen
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, capability))


def format_trace_id(trace_id: str) -> str:
    """Formatiert eine Trace-ID für bessere Lesbarkeit.

    Args:
        trace_id: Die zu formatierende Trace-ID

    Returns:
        Formatierte Trace-ID
    """
    if not trace_id:
        return ""

    # Entferne Bindestriche und formatiere neu
    clean_id = trace_id.replace("-", "").lower()

    # Formatiere als UUID-ähnliche Struktur
    if len(clean_id) >= 32:
        return f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:32]}"

    return clean_id


def calculate_backoff(
    attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True
) -> float:
    """Berechnet Backoff-Zeit für Retry-Mechanismen.

    Args:
        attempt: Aktueller Versuch (0-basiert)
        base_delay: Basis-Verzögerung in Sekunden
        max_delay: Maximale Verzögerung in Sekunden
        jitter: Ob Jitter hinzugefügt werden soll

    Returns:
        Backoff-Zeit in Sekunden
    """
    # Exponential Backoff
    delay = base_delay * (2**attempt)

    # Begrenze auf Maximum
    delay = min(delay, max_delay)

    # Füge Jitter hinzu um Thundering Herd zu vermeiden
    if jitter:
        import secrets

        # Verwende kryptographisch sicheren Random für Jitter
        jitter_factor = 0.5 + (secrets.randbelow(500) / 1000.0)  # 0.5 bis 1.0
        delay = delay * jitter_factor

    return delay


def sanitize_agent_name(name: str) -> str:
    """Bereinigt einen Agent-Namen für sichere Verwendung.

    Args:
        name: Der zu bereinigende Name

    Returns:
        Bereinigter Name
    """
    if not name:
        return "unnamed-agent"

    # Entferne ungültige Zeichen
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", name)

    # Entferne mehrfache Bindestriche
    sanitized = re.sub(r"-+", "-", sanitized)

    # Entferne führende/nachfolgende Bindestriche
    sanitized = sanitized.strip("-")

    # Stelle sicher, dass der Name nicht leer ist
    if not sanitized:
        sanitized = "unnamed-agent"

    return sanitized.lower()


def calculate_health_score(
    response_time_ms: float, error_rate: float, uptime_ratio: float
) -> float:
    """Berechnet einen Health Score basierend auf Metriken.

    Args:
        response_time_ms: Antwortzeit in Millisekunden
        error_rate: Fehlerrate (0.0 - 1.0)
        uptime_ratio: Uptime-Verhältnis (0.0 - 1.0)

    Returns:
        Health Score (0.0 - 1.0)
    """
    # Response Time Score (besser bei niedrigerer Latenz)
    # Annahme: 100ms = perfekt, 1000ms = schlecht
    response_score = max(0.0, 1.0 - (response_time_ms / 1000.0))

    # Error Rate Score (besser bei niedrigerer Fehlerrate)
    error_score = max(0.0, 1.0 - error_rate)

    # Uptime Score
    uptime_score = max(0.0, min(1.0, uptime_ratio))

    # Gewichteter Durchschnitt
    health_score = response_score * 0.3 + error_score * 0.4 + uptime_score * 0.3

    return max(0.0, min(1.0, health_score))


def format_duration(seconds: float) -> str:
    """Formatiert eine Dauer in menschenlesbarer Form.

    Args:
        seconds: Dauer in Sekunden

    Returns:
        Formatierte Dauer
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
    """Kürzt einen String auf eine maximale Länge.

    Args:
        text: Der zu kürzende Text
        max_length: Maximale Länge
        suffix: Suffix für gekürzte Texte

    Returns:
        Gekürzter Text
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix

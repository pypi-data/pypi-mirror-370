import re

from kei_agent.utils import (
    validate_capability,
    format_trace_id,
    calculate_backoff,
    sanitize_agent_name,
)


def test_validate_capability_invalid_inputs():
    assert validate_capability("") is False
    assert validate_capability(None) is False  # type: ignore[arg-type]
    assert validate_capability("with space") is False
    assert validate_capability("slash/") is False
    assert validate_capability("dot.") is False


def test_validate_capability_valid_inputs():
    assert validate_capability("cap_01") is True
    assert validate_capability("CAP-XY") is True


def test_format_trace_id_edge_lengths():
    raw = "A" * 16
    assert format_trace_id(raw) == raw.lower()

    long = "b" * 32
    out = format_trace_id(long)
    assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", out)

    with_hyphens = "12345678-1234-1234-1234-1234567890ab"
    assert format_trace_id(with_hyphens) == with_hyphens.lower()


def test_calculate_backoff_bounds_and_jitter():
    d0 = calculate_backoff(0, base_delay=1.0, max_delay=10.0, jitter=False)
    assert d0 == 1.0
    d3 = calculate_backoff(3, base_delay=1.0, max_delay=3.0, jitter=False)
    assert d3 == 3.0  # capped at max

    # With jitter, should be within [0.5*delay, 1.0*delay]
    base = calculate_backoff(2, base_delay=2.0, max_delay=10.0, jitter=False)
    jittered = calculate_backoff(2, base_delay=2.0, max_delay=10.0, jitter=True)
    assert 0.5 * base <= jittered <= base


def test_sanitize_agent_name():
    assert sanitize_agent_name("") == "unnamed-agent"
    assert sanitize_agent_name("A B!C") == "a-b-c"
    assert sanitize_agent_name("--X__Y--") == "x__y"
    # Non-ASCII becomes empty after sanitization, then default is applied
    assert sanitize_agent_name("äöüß") == "unnamed-agent"
    assert sanitize_agent_name("@@@@") == "unnamed-agent"

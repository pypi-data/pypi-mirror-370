"""Edge-Case-Tests für RetryPolicy-Verhalten."""

from __future__ import annotations

import asyncio
import random
from typing import List

import pytest

from client import AgentClientConfig, RetryConfig, RetryStrategy, TracingConfig
from unified_client import UnifiedKeiAgentClient


class AlwaysFailRPC:
    """Hilfsklasse: schlägt immer fehl."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def _rpc_call(self, op: str, payload):
        raise RuntimeError("fail")


@pytest.mark.asyncio
async def test_max_delay_cap(monkeypatch):
    """Testet, dass max_delay korrekt greift (Kappung)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 2))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4,
                base_delay=10.0,
                max_delay=5.0,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)
    client._rpc_client = AlwaysFailRPC()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    # Erwartet: Delays sind auf 5.0 gekappt
    assert delays[:3] == [5.0, 5.0, 5.0]


@pytest.mark.asyncio
async def test_exponential_base_edge_cases(monkeypatch):
    """Testet Exponentialfaktor 1.0 (linear) und 10.0 (aggressiv)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 2))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # exponential_base = 1.0 → Delay immer base_delay (bei EXPONENTIAL_BACKOFF)
    cfg1 = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4,
                base_delay=0.5,
                exponential_base=1.0,
                jitter=False,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            )
        },
    )
    c1 = UnifiedKeiAgentClient(cfg1)
    c1._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c1._execute_rpc_operation("unknown", {"x": 1})
    assert delays[:3] == [0.5, 0.5, 0.5]

    # exponential_base = 10.0 → Delay 0.5, 5.0, 50.0 (vor max_delay-Kappung)
    delays.clear()
    cfg2 = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4,
                base_delay=0.5,
                exponential_base=10.0,
                jitter=False,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            )
        },
    )
    c2 = UnifiedKeiAgentClient(cfg2)
    c2._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c2._execute_rpc_operation("unknown", {"x": 1})
    assert delays[:3] == [0.5, 5.0, 50.0]


@pytest.mark.asyncio
async def test_jitter_behavior(monkeypatch):
    """Testet Jitter-Verhalten (±10% des Delays) deterministisch mit Seed."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(delay)
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    random.seed(42)

    cfg = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=4,
                base_delay=1.0,
                jitter=True,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    c = UnifiedKeiAgentClient(cfg)
    c._rpc_client = AlwaysFailRPC()

    with pytest.raises(Exception):
        await c._execute_rpc_operation("unknown", {"x": 1})

    # Ohne rounding; prüfen, dass Werte innerhalb ±10% um 1.0 liegen
    assert all(0.9 <= d <= 1.1 for d in delays[:3])


@pytest.mark.asyncio
async def test_max_attempts_boundaries(monkeypatch):
    """Testet max_attempts=1 (kein Retry) vs. max_attempts=100 (viele Retries, gekappt)."""
    # max_attempts=1 → keine Verzögerung, nur 1 Versuch
    cfg1 = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=1,
                base_delay=1.0,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    c1 = UnifiedKeiAgentClient(cfg1)
    c1._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c1._execute_rpc_operation("unknown", {"x": 1})

    # max_attempts=100 → viele Retries; wir prüfen, dass mind. 3 Delays erzeugt werden
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(delay)
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    cfg2 = AgentClientConfig(
        base_url="https://example.invalid",
        api_token="t",
        agent_id="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies={
            "rpc": RetryConfig(
                max_attempts=100,
                base_delay=0.01,
                jitter=False,
                strategy=RetryStrategy.FIXED_DELAY,
            )
        },
    )
    c2 = UnifiedKeiAgentClient(cfg2)
    c2._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c2._execute_rpc_operation("unknown", {"x": 1})
    assert len(delays) >= 3

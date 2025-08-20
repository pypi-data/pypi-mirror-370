"""Edge-Case-Tests for retryPolicy-Verhalten."""

from __future__ import annotations

import asyncio
import random
from typing import List

import pytest

from kei_agent.client import (
    AgentClientConfig,
    retryConfig,
    retryStrategy,
    TracingConfig,
)
from kei_agent.unified_client import UnifiedKeiAgentClient


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
    """Tests, thes max_delay korrekt greift (Kappung)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 2))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4,
                base_delay =10.0,
                max_delay =5.0,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
            )
        },
    )
    client = UnifiedKeiAgentClient(cfg)
    client._rpc_client = AlwaysFailRPC()

    with pytest.raises(Exception):
        await client._execute_rpc_operation("unknown", {"x": 1})

    # Erwartet: Delays are on 5.0 gekappt
    assert delays[:3] == [5.0, 5.0, 5.0]


@pytest.mark.asyncio
async def test_exponential_base_edge_cases(monkeypatch):
    """Tests Exponentialfaktor 1.0 (linear) and 10.0 (aggressiv)."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(round(delay, 2))
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    # exponential_base = 1.0 → Delay immer base_delay (on EXPONENTIAL_BACKOFF)
    cfg1 = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4,
                base_delay =0.5,
                exponential_base =1.0,
                jitter=False,
                strategy=retryStrategy.EXPONENTIAL_BACKOFF,
            )
        },
    )
    c1 = UnifiedKeiAgentClient(cfg1)
    c1._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c1._execute_rpc_operation("unknown", {"x": 1})
    assert delays[:3] == [0.5, 0.5, 0.5]

    # exponential_base = 10.0 → Delay 0.5, 5.0, 50.0 (before max_delay-Kappung)
    delays.clear()
    cfg2 = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4,
                base_delay =0.5,
                exponential_base =10.0,
                jitter=False,
                strategy=retryStrategy.EXPONENTIAL_BACKOFF,
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
    """Tests Jitter-Verhalten (±10% of the Delays) determinisisch with Seed."""
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(delay)
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    random.seed(42)

    cfg = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =4,
                base_delay =1.0,
                jitter=True,
                strategy=retryStrategy.FIXED_DELAY,
            )
        },
    )
    c = UnifiedKeiAgentClient(cfg)
    c._rpc_client = AlwaysFailRPC()

    with pytest.raises(Exception):
        await c._execute_rpc_operation("unknown", {"x": 1})

    # Without rounding; prüfen, thes valuee innerhalb ±10% around 1.0 liegen
    assert all(0.9 <= d <= 1.1 for d in delays[:3])


@pytest.mark.asyncio
async def test_max_attempts_boatdaries(monkeypatch):
    """Tests max_attempts =1 (ka retry) vs. max_attempts =100 (viele Retries, gekappt)."""
    # max_attempts =1 → ka Verzögerung, nur 1 Versuch
    cfg1 = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =1,
                base_delay =1.0,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
            )
        },
    )
    c1 = UnifiedKeiAgentClient(cfg1)
    c1._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c1._execute_rpc_operation("unknown", {"x": 1})

    # max_attempts =100 → viele Retries; wir prüfen, thes mind. 3 Delays erzeugt werthe
    delays: List[float] = []

    async def fake_sleep(delay: float):
        delays.append(delay)
        return None

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    cfg2 = AgentClientConfig(
        base_url ="https://example.invalid",
        api_token ="t",
        agent_id ="a",
        tracing=TracingConfig(enabled=False),
        protocol_retry_policies ={
            "rpc": retryConfig(
                max_attempts =100,
                base_delay =0.01,
                jitter=False,
                strategy=retryStrategy.FIXED_DELAY,
            )
        },
    )
    c2 = UnifiedKeiAgentClient(cfg2)
    c2._rpc_client = AlwaysFailRPC()
    with pytest.raises(Exception):
        await c2._execute_rpc_operation("unknown", {"x": 1})
    assert len(delays) >= 3

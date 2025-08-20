import asyncio
from typing import Any

import pytest
import httpx


@pytest.mark.asyncio
async def test_httpx_timeout_and_basic_request():
    async def app(scope, receive, send):
        assert scope["type"] == "http"
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, timeout=httpx.Timeout(0.5)) as client:
        r = await client.get("http://test/")
        assert r.status_code == 200
        assert r.text == "ok"

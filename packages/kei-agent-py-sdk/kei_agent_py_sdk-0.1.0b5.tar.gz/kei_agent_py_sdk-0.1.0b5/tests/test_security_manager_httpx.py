from typing import Any, Dict, List

import httpx
import pytest

from kei_agent.security_manager import SecurityManager
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.exceptions import SecurityError


class DummyResponse:
    def __init__(self, status_code: int, json_data: Dict[str, Any]):
        self.status_code = status_code
        self._json = json_data
        self.extensions = {}

    def raise_for_status(self) -> None:
        if not (200 <= self.status_code < 300):
            raise httpx.HTTPStatusError("error", request=None, response=self)  # type: ignore[arg-type]

    def json(self) -> Dict[str, Any]:
        return self._json


class DummyClient:
    def __init__(self, responses: List[Any]):
        self._responses = responses
        self._i = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def post(self, *_args, **_kwargs):
        if self._i >= len(self._responses):
            return DummyResponse(200, {"access_token": "tok"})
        r = self._responses[self._i]
        self._i += 1
        if isinstance(r, Exception):
            raise r
        return r


@pytest.mark.asyncio
async def test_oidc_success(monkeypatch):
    cfg = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_issuer="https://issuer.example",
        oidc_client_id="idclient",
        oidc_client_secret="supersecret123",
    )

    dc = DummyClient([DummyResponse(200, {"access_token": "abc"})])
    def client_factory(*, timeout, verify):
        return dc

    sm = SecurityManager(cfg, client_factory=client_factory)

    token_data = await sm._fetch_oidc_token()
    assert token_data["access_token"] == "abc"


@pytest.mark.asyncio
async def test_oidc_retry_5xx(monkeypatch):
    cfg = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_issuer="https://issuer.example",
        oidc_client_id="idclient",
        oidc_client_secret="supersecret123",
    )

    calls = [DummyResponse(500, {}), DummyResponse(502, {}), DummyResponse(200, {"access_token": "tok"})]
    dc = DummyClient(calls)
    def client_factory(*, timeout, verify):
        return dc

    sm = SecurityManager(cfg, client_factory=client_factory)


    token_data = await sm._fetch_oidc_token()
    assert token_data["access_token"] == "tok"


@pytest.mark.asyncio
async def test_oidc_no_retry_on_400(monkeypatch):
    cfg = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_issuer="https://issuer.example",
        oidc_client_id="idclient",
        oidc_client_secret="supersecret123",
    )

    calls = [DummyResponse(400, {})]
    dc = DummyClient(calls)
    def client_factory(*, timeout, verify):
        return dc

    sm = SecurityManager(cfg, client_factory=client_factory)

    with pytest.raises(SecurityError):
        await sm._fetch_oidc_token()


@pytest.mark.asyncio
async def test_oidc_retry_request_error(monkeypatch):
    cfg = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_issuer="https://issuer.example",
        oidc_client_id="idclient",
        oidc_client_secret="supersecret123",
    )

    calls = [httpx.RequestError("conn"), DummyResponse(200, {"access_token": "tok2"})]
    dc = DummyClient(calls)
    def client_factory(*, timeout, verify):
        return dc

    sm = SecurityManager(cfg, client_factory=client_factory)

    token_data = await sm._fetch_oidc_token()
    assert token_data["access_token"] == "tok2"


class _FakeSSLObject:
    def __init__(self, cert_bytes: bytes):
        self._cert = cert_bytes

    def getpeercert(self, binary_form: bool = False):
        return self._cert if binary_form else None


class _FakeNetworkStream:
    def __init__(self, sslobj):
        self._sslobj = sslobj

    def get_extra_info(self, name: str):
        if name == "ssl_object":
            return self._sslobj
        return None


@pytest.mark.asyncio
async def test_tls_pinning_mismatch(monkeypatch):
    # Build a cert byte string that yields a known SHA-256 digest
    import hashlib

    cert = b"dummy-cert"
    fp = hashlib.sha256(cert).hexdigest()

    # Configure a different fingerprint to force mismatch
    cfg = SecurityConfig(
        auth_type=Authtypee.OIDC,
        oidc_issuer="https://issuer.example",
        oidc_client_id="idclient",
        oidc_client_secret="supersecret123",
        tls_pinned_sha256="0" * 64,
    )

    resp = DummyResponse(200, {"access_token": "ok"})
    resp.extensions["network_stream"] = _FakeNetworkStream(_FakeSSLObject(cert))
    dc = DummyClient([resp])
    def client_factory(*, timeout, verify):
        return dc

    sm = SecurityManager(cfg, client_factory=client_factory)

    with pytest.raises(SecurityError):
        await sm._fetch_oidc_token()

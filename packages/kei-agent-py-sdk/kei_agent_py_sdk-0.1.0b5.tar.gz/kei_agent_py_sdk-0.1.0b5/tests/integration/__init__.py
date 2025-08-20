# tests/integration/__init__.py
"""
Integration tests for KEI-Agent Python SDK.

This package contains comprehensive integration tests that validate:
- End-to-end protocol functionality (RPC, Stream, Bus, MCP)
- Authentication flows (Bearer, OIDC, mTLS)
- Real-world scenarios and workflows
- Contract testing with external services
- Chaos engineering and resilience testing
- Performance regression testing

Integration tests require external services and are designed to run
in CI/CD environments with proper test infrastructure setup.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# Test configuration
INTEGRATION_TEST_CONFIG = {
    "timeout": int(os.getenv("INTEGRATION_TEST_TIMEOUT", "30")),
    "retry_attempts": int(os.getenv("INTEGRATION_TEST_RETRIES", "3")),
    "mock_services": os.getenv("USE_MOCK_SERVICES", "true").lower() == "true",
    "chaos_testing": os.getenv("ENABLE_CHAOS_TESTING", "false").lower() == "true",
    "performance_testing": os.getenv("ENABLE_PERFORMANCE_TESTING", "false").lower() == "true",
}

# Test service endpoints
TEST_ENDPOINTS = {
    "api_base": os.getenv("TEST_API_BASE_URL", "http://localhost:8000"),
    "auth_server": os.getenv("TEST_AUTH_SERVER_URL", "http://localhost:8080"),
    "websocket_endpoint": os.getenv("TEST_WS_ENDPOINT", "ws://localhost:8001"),
    "message_bus": os.getenv("TEST_MESSAGE_BUS_URL", "http://localhost:8002"),
}

# Test credentials (for testing only)
TEST_CREDENTIALS = {
    "api_token": os.getenv("KEI_API_TOKEN", "ci_api_token_abcd1234567890efgh1234567890ijkl"),
    "oidc_client_id": os.getenv("OIDC_CLIENT_ID", "ci-oidc-client-12345"),
    "oidc_client_secret": os.getenv("OIDC_CLIENT_SECRET", "ci_oidc_secret_abcd1234567890efgh1234567890ijkl"),
    "mtls_cert_path": os.getenv("TEST_MTLS_CERT_PATH", "tests/fixtures/test-cert.pem"),
    "mtls_key_path": os.getenv("TEST_MTLS_KEY_PATH", "tests/fixtures/test-key.pem"),
}


def skip_if_no_integration_env():
    """Decorator to skip tests if integration environment is not available."""
    import pytest

    def decorator(func):
        return pytest.mark.skipif(
            not os.getenv("RUN_INTEGRATION_TESTS"),
            reason="Integration tests require RUN_INTEGRATION_TESTS environment variable"
        )(func)
    return decorator


def requires_service(service_name: str):
    """Decorator to skip tests if specific service is not available."""
    import pytest

    def decorator(func):
        return pytest.mark.skipif(
            not _check_service_availability(service_name),
            reason=f"Integration test requires {service_name} service"
        )(func)
    return decorator


def _check_service_availability(service_name: str) -> bool:
    """Check if a test service is available."""
    import aiohttp

    endpoint = TEST_ENDPOINTS.get(service_name)
    if not endpoint:
        return False

    try:
        # Simple health check
        import requests
        response = requests.get(f"{endpoint}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


class IntegrationTestBase:
    """Base class for integration tests with common setup and utilities."""

    def __init__(self):
        self.config = INTEGRATION_TEST_CONFIG.copy()
        self.endpoints = TEST_ENDPOINTS.copy()
        self.credentials = TEST_CREDENTIALS.copy()

    async def setup_test_environment(self):
        """Set up test environment and services."""
        # This would typically start test containers or connect to test services
        pass

    async def teardown_test_environment(self):
        """Clean up test environment."""
        # This would typically stop test containers or clean up test data
        pass

    def get_test_config(self, **overrides) -> Dict[str, Any]:
        """Get test configuration with optional overrides."""
        config = {
            "base_url": self.endpoints["api_base"],
            "api_token": self.credentials["api_token"],
            "agent_id": "integration-test-agent",
            "timeout": self.config["timeout"],
            "max_retries": self.config["retry_attempts"],
        }
        config.update(overrides)
        return config


# Pytest fixtures for integration tests
import pytest


@pytest.fixture(scope="session")
def integration_config():
    """Session-scoped integration test configuration."""
    return INTEGRATION_TEST_CONFIG


@pytest.fixture(scope="session")
def test_endpoints():
    """Session-scoped test endpoints configuration."""
    return TEST_ENDPOINTS


@pytest.fixture(scope="session")
def test_credentials():
    """Session-scoped test credentials."""
    return TEST_CREDENTIALS


@pytest.fixture(scope="function")
async def integration_test_base():
    """Function-scoped integration test base with setup/teardown."""
    base = IntegrationTestBase()
    await base.setup_test_environment()
    yield base
    await base.teardown_test_environment()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test markers
pytest_plugins = []

# Custom markers for integration tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "protocol_rpc: mark test as RPC protocol test"
    )
    config.addinivalue_line(
        "markers", "protocol_stream: mark test as Stream protocol test"
    )
    config.addinivalue_line(
        "markers", "protocol_bus: mark test as Bus protocol test"
    )
    config.addinivalue_line(
        "markers", "protocol_mcp: mark test as MCP protocol test"
    )
    config.addinivalue_line(
        "markers", "auth_bearer: mark test as Bearer authentication test"
    )
    config.addinivalue_line(
        "markers", "auth_oidc: mark test as OIDC authentication test"
    )
    config.addinivalue_line(
        "markers", "auth_mtls: mark test as mTLS authentication test"
    )
    config.addinivalue_line(
        "markers", "chaos: mark test as chaos engineering test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "contract: mark test as contract test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running test"
    )


# Test utilities
class TestServiceManager:
    """Manages test services for integration testing."""

    def __init__(self):
        self.services = {}
        self.containers = {}

    async def start_mock_api_server(self, port: int = 8000):
        """Start mock API server for testing."""
        # Implementation would start a mock server
        pass

    async def start_mock_auth_server(self, port: int = 8080):
        """Start mock authentication server."""
        # Implementation would start a mock auth server
        pass

    async def start_mock_websocket_server(self, port: int = 8001):
        """Start mock WebSocket server."""
        # Implementation would start a mock WebSocket server
        pass

    async def stop_all_services(self):
        """Stop all test services."""
        # Implementation would stop all mock services
        pass


# Export commonly used items
__all__ = [
    "INTEGRATION_TEST_CONFIG",
    "TEST_ENDPOINTS",
    "TEST_CREDENTIALS",
    "skip_if_no_integration_env",
    "requires_service",
    "IntegrationTestBase",
    "TestServiceManager",
]

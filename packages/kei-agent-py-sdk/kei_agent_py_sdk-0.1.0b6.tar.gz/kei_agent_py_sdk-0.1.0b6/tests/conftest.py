"""
Global pytest configuration and fixtures.

This file automatically sets up test environment variables
to ensure all tests have valid credentials that pass validation.
"""

import os
import pytest
from unittest.mock import patch


# Valid test credentials that pass validation
TEST_ENV_VARS = {
    "KEI_API_TOKEN": "ci_api_token_abcd1234567890efgh1234567890ijkl",
    "KEI_API_URL": "https://api.ci.example.com",
    "KEI_AGENT_ID": "ci-agent-12345",
    "KEI_AUTH_TYPE": "bearer",
    "OIDC_CLIENT_SECRET": "ci_oidc_secret_abcd1234567890efgh1234567890ijkl",
    "OIDC_CLIENT_ID": "ci-oidc-client-12345",
    "OIDC_ISSUER": "https://auth.ci.example.com",
    # Integration test configuration
    "INTEGRATION_TEST_TIMEOUT": "30",
    "INTEGRATION_TEST_RETRIES": "3",
    "USE_MOCK_SERVICES": "true",
    "ENABLE_CHAOS_TESTING": "false",
    "ENABLE_PERFORMANCE_TESTING": "false",
    # Test service endpoints
    "TEST_API_BASE_URL": "https://api.ci.example.com",
    "TEST_AUTH_SERVER_URL": "https://auth.ci.example.com",
    "TEST_WS_ENDPOINT": "wss://ws.ci.example.com",
    "TEST_MESSAGE_BUS_URL": "https://bus.ci.example.com",
}


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Automatically setup test environment variables for all tests."""
    # Only set environment variables if they're not already set
    env_patch = {}
    for key, value in TEST_ENV_VARS.items():
        if key not in os.environ:
            env_patch[key] = value
    
    if env_patch:
        with patch.dict(os.environ, env_patch):
            yield
    else:
        yield


@pytest.fixture
def test_credentials():
    """Provide test credentials for individual tests."""
    return {
        "api_token": os.getenv("KEI_API_TOKEN", TEST_ENV_VARS["KEI_API_TOKEN"]),
        "base_url": os.getenv("KEI_API_URL", TEST_ENV_VARS["KEI_API_URL"]),
        "agent_id": os.getenv("KEI_AGENT_ID", TEST_ENV_VARS["KEI_AGENT_ID"]),
        "oidc_client_secret": os.getenv("OIDC_CLIENT_SECRET", TEST_ENV_VARS["OIDC_CLIENT_SECRET"]),
        "oidc_client_id": os.getenv("OIDC_CLIENT_ID", TEST_ENV_VARS["OIDC_CLIENT_ID"]),
        "oidc_issuer": os.getenv("OIDC_ISSUER", TEST_ENV_VARS["OIDC_ISSUER"]),
    }


@pytest.fixture
def mock_environment():
    """Provide a clean mock environment for tests that need isolation."""
    with patch.dict(os.environ, TEST_ENV_VARS, clear=False):
        yield


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, external dependencies)"
    )
    config.addinivalue_line(
        "markers", "security: Security-related tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )


# Skip integration tests by default unless explicitly enabled
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle integration test skipping."""
    if not os.getenv("RUN_INTEGRATION_TESTS"):
        skip_integration = pytest.mark.skip(reason="Integration tests require RUN_INTEGRATION_TESTS=1")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

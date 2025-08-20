"""
Test configuration for CI environments.

Provides valid test credentials that pass validation but are not real secrets.
"""

import os
from typing import Dict, Any

# Valid test credentials that pass validation
TEST_CREDENTIALS = {
    "api_token": "ci_api_token_abcd1234567890efgh1234567890ijkl",
    "base_url": "https://api.ci.example.com",
    "agent_id": "ci-agent-12345",
    "auth_type": "bearer",
    "oidc_client_secret": "ci_oidc_secret_abcd1234567890efgh1234567890ijkl",
    "oidc_client_id": "ci-oidc-client-12345",
    "oidc_issuer": "https://auth.ci.example.com",
}

# Integration test endpoints
TEST_ENDPOINTS = {
    "api_base": "https://api.ci.example.com",
    "auth_server": "https://auth.ci.example.com",
    "websocket_endpoint": "wss://ws.ci.example.com",
    "message_bus": "https://bus.ci.example.com",
}


def get_test_credentials() -> Dict[str, str]:
    """Get test credentials from environment or defaults."""
    return {
        "api_token": os.getenv("KEI_API_TOKEN", TEST_CREDENTIALS["api_token"]),
        "oidc_client_secret": os.getenv("OIDC_CLIENT_SECRET", TEST_CREDENTIALS["oidc_client_secret"]),
        "oidc_client_id": os.getenv("OIDC_CLIENT_ID", TEST_CREDENTIALS["oidc_client_id"]),
        "oidc_issuer": os.getenv("OIDC_ISSUER", TEST_CREDENTIALS["oidc_issuer"]),
    }


def get_test_config() -> Dict[str, Any]:
    """Get complete test configuration."""
    credentials = get_test_credentials()
    
    return {
        "base_url": os.getenv("KEI_API_URL", TEST_CREDENTIALS["base_url"]),
        "api_token": credentials["api_token"],
        "agent_id": os.getenv("KEI_AGENT_ID", TEST_CREDENTIALS["agent_id"]),
        "auth_type": os.getenv("KEI_AUTH_TYPE", TEST_CREDENTIALS["auth_type"]),
        "timeout": 30.0,
        "max_retries": 3,
        "oidc_client_secret": credentials["oidc_client_secret"],
        "oidc_client_id": credentials["oidc_client_id"],
        "oidc_issuer": credentials["oidc_issuer"],
    }


def setup_test_environment():
    """Setup test environment variables if not already set."""
    for key, value in TEST_CREDENTIALS.items():
        env_key = f"KEI_{key.upper()}" if not key.startswith("oidc") else key.upper()
        if env_key not in os.environ:
            os.environ[env_key] = value
    
    # Set integration test flags
    os.environ.setdefault("USE_MOCK_SERVICES", "true")
    os.environ.setdefault("ENABLE_CHAOS_TESTING", "false")
    os.environ.setdefault("ENABLE_PERFORMANCE_TESTING", "false")

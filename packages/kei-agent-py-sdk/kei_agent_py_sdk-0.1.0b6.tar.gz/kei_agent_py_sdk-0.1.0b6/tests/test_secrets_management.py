# tests/test_secrets_management.py
"""
Tests for secrets management functionality.

This test validates that:
1. Secrets are properly loaded from environment variables
2. Validation works correctly
3. No hardcoded credentials are used
4. External secret store integration works (when implemented)
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from kei_agent.secrets_manager import (
    SecretsManager, SecretConfig, get_secrets_manager, configure_secrets
)
from kei_agent.exceptions import SecurityError


class TestSecretsManager:
    """Tests for SecretsManager class."""

    def setup_method(self):
        """Setup for each test method."""
        # Clear any existing global instance
        import kei_agent.secrets_manager
        kei_agent.secrets_manager._secrets_manager = None

    def test_get_secret_from_environment(self):
        """Test getting secret from environment variable."""
        config = SecretConfig(env_prefix="TEST_")
        manager = SecretsManager(config)

        with patch.dict(os.environ, {"TEST_API_TOKEN": "env-token-123"}):
            token = manager.get_secret("API_TOKEN")
            assert token == "env-token-123"

    def test_get_secret_with_default(self):
        """Test getting secret with default value."""
        manager = SecretsManager()

        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            token = manager.get_secret("NONEXISTENT_TOKEN", default="default-value")
            assert token == "default-value"

    def test_get_secret_required_missing(self):
        """Test that required secret raises error when missing."""
        manager = SecretsManager()

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SecurityError, match="Required secret 'MISSING_TOKEN' not found"):
                manager.get_secret("MISSING_TOKEN", required=True)

    def test_get_api_token_validation(self):
        """Test API token validation."""
        manager = SecretsManager()

        # Test valid token
        with patch.dict(os.environ, {"KEI_API_TOKEN": "valid-token-123456"}):
            token = manager.get_api_token()
            assert token == "valid-token-123456"

        # Test missing token
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SecurityError, match="API token is required"):
                manager.get_api_token()

        # Test invalid token (too short)
        with patch.dict(os.environ, {"KEI_API_TOKEN": "short"}):
            with pytest.raises(SecurityError, match="API token appears to be invalid"):
                manager.get_api_token()

    def test_get_oidc_credentials(self):
        """Test OIDC credentials retrieval."""
        manager = SecretsManager()

        env_vars = {
            "KEI_OIDC_ISSUER": "https://auth.example.com",
            "KEI_OIDC_CLIENT_ID": "client-123",
            "KEI_OIDC_CLIENT_SECRET": "secret-456",
            "KEI_OIDC_SCOPE": "openid profile email"
        }

        with patch.dict(os.environ, env_vars):
            credentials = manager.get_oidc_credentials()

            assert credentials["issuer"] == "https://auth.example.com"
            assert credentials["client_id"] == "client-123"
            assert credentials["client_secret"] == "secret-456"
            assert credentials["scope"] == "openid profile email"

    def test_get_oidc_credentials_missing(self):
        """Test OIDC credentials with missing required values."""
        manager = SecretsManager()

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SecurityError, match="Required secret 'OIDC_ISSUER' not found"):
                manager.get_oidc_credentials()

    def test_get_mtls_paths(self):
        """Test mTLS certificate paths retrieval."""
        manager = SecretsManager()

        # Create temporary files for testing
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as cert_file, \
             tempfile.NamedTemporaryFile(delete=False) as key_file:

            env_vars = {
                "KEI_MTLS_CERT_PATH": cert_file.name,
                "KEI_MTLS_KEY_PATH": key_file.name,
            }

            try:
                with patch.dict(os.environ, env_vars):
                    paths = manager.get_mtls_paths()

                    assert paths["cert_path"] == cert_file.name
                    assert paths["key_path"] == key_file.name
                    assert paths["ca_path"] is None
            finally:
                # Clean up
                os.unlink(cert_file.name)
                os.unlink(key_file.name)

    def test_mtls_paths_file_not_found(self):
        """Test mTLS paths validation when files don't exist."""
        manager = SecretsManager()

        env_vars = {
            "KEI_MTLS_CERT_PATH": "/nonexistent/cert.pem",
            "KEI_MTLS_KEY_PATH": "/nonexistent/key.pem",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(SecurityError, match="mTLS cert_path file not found"):
                manager.get_mtls_paths()

    def test_secret_validation(self):
        """Test secret validation functionality."""
        config = SecretConfig(validate_secrets=True)
        manager = SecretsManager(config)

        # Test empty secret
        with patch.dict(os.environ, {"KEI_EMPTY_SECRET": ""}):
            with pytest.raises(SecurityError, match="Secret 'EMPTY_SECRET' is empty"):
                manager.get_secret("EMPTY_SECRET", required=True)

        # Test placeholder token
        with patch.dict(os.environ, {"KEI_API_TOKEN": "your-token-here"}):
            with pytest.raises(SecurityError, match="appears to be a placeholder"):
                manager.get_api_token()

    def test_url_validation(self):
        """Test URL validation."""
        config = SecretConfig(validate_secrets=True)
        manager = SecretsManager(config)

        # Test invalid URL
        with patch.dict(os.environ, {"KEI_API_URL": "not-a-url"}):
            with pytest.raises(SecurityError, match="URL 'API_URL' must start with http"):
                manager.get_secret("API_URL", required=True)

        # Test valid URL
        with patch.dict(os.environ, {"KEI_API_URL": "https://api.example.com"}):
            url = manager.get_secret("API_URL")
            assert url == "https://api.example.com"

    def test_cache_functionality(self):
        """Test secret caching."""
        manager = SecretsManager()

        with patch.dict(os.environ, {"KEI_CACHED_SECRET": "cached-value"}):
            # First call should read from environment
            value1 = manager.get_secret("CACHED_SECRET")
            assert value1 == "cached-value"

            # Second call should use cache
            with patch.dict(os.environ, {}, clear=True):
                value2 = manager.get_secret("CACHED_SECRET")
                assert value2 == "cached-value"  # Still cached

            # Clear cache and try again
            manager.clear_cache()
            value3 = manager.get_secret("CACHED_SECRET")
            assert value3 is None  # No longer cached

    def test_validate_configuration(self):
        """Test configuration validation."""
        manager = SecretsManager()

        # Test with valid configuration
        with patch.dict(os.environ, {"KEI_API_TOKEN": "valid-token-123456"}):
            assert manager.validate_configuration() is True

        # Test with missing required configuration
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SecurityError, match="Missing required secrets"):
                manager.validate_configuration()

    def test_global_secrets_manager(self):
        """Test global secrets manager functionality."""
        # Test getting default instance
        manager1 = get_secrets_manager()
        manager2 = get_secrets_manager()
        assert manager1 is manager2  # Should be same instance

        # Test configuring global instance
        config = SecretConfig(env_prefix="CUSTOM_")
        manager3 = configure_secrets(config)
        assert manager3.config.env_prefix == "CUSTOM_"

        # Test that new instance is returned
        manager4 = get_secrets_manager()
        assert manager4 is manager3

    def test_external_store_not_implemented(self):
        """Test external store functionality (not implemented yet)."""
        config = SecretConfig(use_external_store=True, store_type="aws_secrets")
        manager = SecretsManager(config)

        # Should fall back to environment variables
        with patch.dict(os.environ, {"KEI_TEST_SECRET": "env-value"}):
            value = manager.get_secret("TEST_SECRET")
            assert value == "env-value"


class TestSecretsIntegration:
    """Integration tests for secrets management."""

    def test_cli_uses_secrets_manager(self):
        """Test that CLI uses secrets manager."""
        from kei_agent.cli import CLIContext

        cli = CLIContext()

        with patch.dict(os.environ, {
            "KEI_API_URL": "https://api.ci.example.com",
            "KEI_API_TOKEN": "ci_api_token_abcd1234567890efgh1234567890ijkl",
            "KEI_AGENT_ID": "ci-agent-12345",
        }):
            config = cli.load_config()

            assert config.base_url == "https://test.example.com"
            assert config.api_token == "ci_api_token_abcd1234567890efgh1234567890ijkl"
            assert config.agent_id == "test-agent"

    def test_no_hardcoded_secrets_in_production_code(self):
        """Test that production code doesn't contain hardcoded secrets."""
        import subprocess
        import sys
        from pathlib import Path

        # Run the secrets validation script
        script_path = Path(__file__).parent.parent / "scripts" / "validate_no_secrets.py"
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True)

        # Should pass (return code 0)
        assert result.returncode == 0, f"Secrets validation failed: {result.stdout}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

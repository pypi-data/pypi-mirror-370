# tests/test_input_validation.py
"""
Tests for comprehensive input validation functionality.

This test validates that:
1. Pydantic models validate configuration correctly
2. Input sanitization works for all input types
3. Rate limiting is enforced
4. Security patterns are detected and blocked
5. CLI arguments are properly sanitized
"""

import json
import pytest
from unittest.mock import patch, mock_open

from kei_agent.validation_models import (
    SecurityConfigValidation, AgentClientConfigValidation,
    ProtocolConfigValidation, validate_configuration
)
from kei_agent.input_sanitizer import InputSanitizer, RateLimiter, get_sanitizer
from kei_agent.exceptions import ValidationError


class TestValidationModels:
    """Tests for Pydantic validation models."""

    def test_security_config_validation_valid(self):
        """Test valid security configuration."""
        config = {
            'auth_type': 'bearer',
            'api_token': 'valid-token-123456',
            'rbac_enabled': True,
            'audit_enabled': True,
            'token_cache_ttl': 3600
        }

        validated = validate_configuration(config, 'security')
        assert validated['auth_type'] == 'bearer'
        assert validated['api_token'] == 'valid-token-123456'

    def test_security_config_validation_invalid_token(self):
        """Test security configuration with invalid token."""
        config = {
            'auth_type': 'bearer',
            'api_token': 'your-token-here',  # Placeholder
            'rbac_enabled': True
        }

        with pytest.raises(ValidationError, match="placeholder value"):
            validate_configuration(config, 'security')

    def test_security_config_validation_weak_token(self):
        """Test security configuration with weak token."""
        config = {
            'auth_type': 'bearer',
            'api_token': 'weak',  # Too short
            'rbac_enabled': True
        }

        with pytest.raises(ValidationError):
            validate_configuration(config, 'security')

    def test_security_config_oidc_validation(self):
        """Test OIDC configuration validation."""
        config = {
            'auth_type': 'oidc',
            'oidc_issuer': 'https://auth.example.com',
            'oidc_client_id': 'client-123',
            'oidc_client_secret': 'secret-456789',
            'oidc_scope': 'openid profile'
        }

        validated = validate_configuration(config, 'security')
        assert validated['oidc_issuer'] == 'https://auth.example.com'

    def test_security_config_oidc_missing_fields(self):
        """Test OIDC configuration with missing fields."""
        config = {
            'auth_type': 'oidc',
            'oidc_issuer': 'https://auth.example.com',
            # Missing client_id and client_secret
        }

        with pytest.raises(ValidationError, match="OIDC authentication requires"):
            validate_configuration(config, 'security')

    def test_agent_config_validation_valid(self):
        """Test valid agent configuration."""
        config = {
            'base_url': 'https://api.example.com',
            'api_token': 'valid-token-123456',
            'agent_id': 'test-agent',
            'timeout': 30.0,
            'max_retries': 3
        }

        validated = validate_configuration(config, 'agent')
        assert validated['base_url'] == 'https://api.example.com'
        assert validated['agent_id'] == 'test-agent'

    def test_agent_config_validation_invalid_url(self):
        """Test agent configuration with invalid URL."""
        config = {
            'base_url': 'http://insecure.example.com',  # HTTP not allowed
            'api_token': 'valid-token-123456',
            'agent_id': 'test-agent'
        }

        with pytest.raises(ValidationError, match="must use HTTPS"):
            validate_configuration(config, 'agent')

    def test_agent_config_validation_reserved_agent_id(self):
        """Test agent configuration with reserved agent ID."""
        config = {
            'base_url': 'https://api.example.com',
            'api_token': 'valid-token-123456',
            'agent_id': 'admin'  # Reserved name
        }

        with pytest.raises(ValidationError, match="is reserved"):
            validate_configuration(config, 'agent')

    def test_protocol_config_validation_valid(self):
        """Test valid protocol configuration."""
        config = {
            'rpc_enabled': True,
            'stream_enabled': True,
            'bus_enabled': False,
            'mcp_enabled': True,
            'preferred_protocol': 'rpc',
            'max_connections_per_protocol': 10
        }

        validated = validate_configuration(config, 'protocol')
        assert validated['preferred_protocol'] == 'rpc'

    def test_protocol_config_validation_no_protocols(self):
        """Test protocol configuration with no protocols enabled."""
        config = {
            'rpc_enabled': False,
            'stream_enabled': False,
            'bus_enabled': False,
            'mcp_enabled': False
        }

        with pytest.raises(ValidationError, match="At least one protocol must be enabled"):
            validate_configuration(config, 'protocol')

    def test_protocol_config_validation_invalid_preferred(self):
        """Test protocol configuration with invalid preferred protocol."""
        config = {
            'rpc_enabled': False,
            'stream_enabled': True,
            'preferred_protocol': 'rpc'  # RPC not enabled
        }

        with pytest.raises(ValidationError, match="Preferred protocol 'rpc' is not enabled"):
            validate_configuration(config, 'protocol')


class TestInputSanitizer:
    """Tests for input sanitization functionality."""

    def test_sanitize_string_valid(self):
        """Test string sanitization with valid input."""
        sanitizer = InputSanitizer()

        result = sanitizer.sanitize_string("Hello World", field_name="test")
        assert result == "Hello World"

    def test_sanitize_string_with_control_chars(self):
        """Test string sanitization removes control characters."""
        sanitizer = InputSanitizer()

        input_str = "Hello\x00\x01World\x1f"
        result = sanitizer.sanitize_string(input_str, field_name="test")
        assert result == "HelloWorld"

    def test_sanitize_string_too_long(self):
        """Test string sanitization with length limit."""
        sanitizer = InputSanitizer()

        long_string = "a" * 1001
        with pytest.raises(ValidationError, match="exceeds maximum length"):
            sanitizer.sanitize_string(long_string, max_length=1000, field_name="test")

    def test_sanitize_string_dangerous_content(self):
        """Test string sanitization detects dangerous content."""
        sanitizer = InputSanitizer()

        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "SELECT * FROM users",
            "rm -rf /",
            "../../../etc/passwd"
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises(ValidationError, match="potentially dangerous content"):
                sanitizer.sanitize_string(dangerous_input, field_name="test")

    def test_sanitize_url_valid(self):
        """Test URL sanitization with valid URLs."""
        sanitizer = InputSanitizer()

        valid_urls = [
            "https://example.com",
            "http://localhost:8000",
            "https://api.example.com/v1/endpoint"
        ]

        for url in valid_urls:
            result = sanitizer.sanitize_url(url, field_name="test_url")
            assert result == url

    def test_sanitize_url_invalid_scheme(self):
        """Test URL sanitization with invalid schemes."""
        sanitizer = InputSanitizer()

        invalid_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert('xss')"
        ]

        for url in invalid_urls:
            with pytest.raises(ValidationError, match="must use HTTP or HTTPS"):
                sanitizer.sanitize_url(url, field_name="test_url")

    def test_sanitize_file_path_valid(self):
        """Test file path sanitization with valid paths."""
        sanitizer = InputSanitizer()

        valid_paths = [
            "config.json",
            "/etc/ssl/cert.pem",
            "data/file.txt"
        ]

        for path in valid_paths:
            result = sanitizer.sanitize_file_path(path, field_name="test_path")
            assert result == path

    def test_sanitize_file_path_traversal(self):
        """Test file path sanitization detects path traversal."""
        sanitizer = InputSanitizer()

        dangerous_paths = [
            "../../../etc/passwd",
            "config/../../../secret.txt",
            "..\\windows\\system32"
        ]

        for path in dangerous_paths:
            with pytest.raises(ValidationError, match="path traversal"):
                sanitizer.sanitize_file_path(path, field_name="test_path")

    def test_sanitize_file_path_dangerous_extension(self):
        """Test file path sanitization detects dangerous extensions."""
        sanitizer = InputSanitizer()

        dangerous_files = [
            "malware.exe",
            "script.bat",
            "virus.vbs"
        ]

        for file in dangerous_files:
            with pytest.raises(ValidationError, match="dangerous file extension"):
                sanitizer.sanitize_file_path(file, field_name="test_file")

    def test_sanitize_json_valid(self):
        """Test JSON sanitization with valid JSON."""
        sanitizer = InputSanitizer()

        valid_json = '{"key": "value", "number": 42}'
        result = sanitizer.sanitize_json(valid_json, field_name="test_json")

        assert result == {"key": "value", "number": 42}

    def test_sanitize_json_invalid_format(self):
        """Test JSON sanitization with invalid JSON."""
        sanitizer = InputSanitizer()

        invalid_json = '{"key": "value"'  # Missing closing brace
        with pytest.raises(ValidationError, match="Invalid test_json format"):
            sanitizer.sanitize_json(invalid_json, field_name="test_json")

    def test_sanitize_json_too_deep(self):
        """Test JSON sanitization with excessive depth."""
        sanitizer = InputSanitizer()

        # Create deeply nested JSON
        deep_json = {"level": 1}
        current = deep_json
        for i in range(2, 15):  # Exceed MAX_JSON_DEPTH
            current["nested"] = {"level": i}
            current = current["nested"]

        with pytest.raises(ValidationError, match="exceeds maximum depth"):
            sanitizer.sanitize_json(deep_json, field_name="test_json")

    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        rate_limiter = RateLimiter(max_requests=2, window_seconds=60)

        # First two requests should be allowed
        assert rate_limiter.is_allowed() is True
        assert rate_limiter.is_allowed() is True

        # Third request should be denied
        assert rate_limiter.is_allowed() is False

    def test_sanitizer_with_rate_limiting(self):
        """Test sanitizer with rate limiting."""
        rate_limiter = RateLimiter(max_requests=1, window_seconds=60)
        sanitizer = InputSanitizer(rate_limiter)

        # First request should work
        sanitizer.sanitize_string("test", field_name="test")

        # Second request should be rate limited
        with pytest.raises(ValidationError, match="Rate limit exceeded"):
            sanitizer.sanitize_string("test2", field_name="test")


class TestInputValidationIntegration:
    """Integration tests for input validation."""

    def test_cli_config_validation(self):
        """Test CLI configuration validation."""
        from kei_agent.cli import CLIContext

        # Mock file content
        config_content = json.dumps({
            "base_url": "https://api.example.com",
            "api_token": "valid-token-123456",
            "agent_id": "test-agent"
        })

        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("pathlib.Path.exists", return_value=True):
                cli = CLIContext()
                config = cli.load_config(Path("test_config.json"))

                assert config.base_url == "https://api.example.com"
                assert config.api_token == "valid-token-123456"
                assert config.agent_id == "test-agent"

    def test_cli_config_validation_dangerous_content(self):
        """Test CLI configuration validation with dangerous content."""
        from kei_agent.cli import CLIContext

        # Mock file with dangerous content
        config_content = json.dumps({
            "base_url": "https://api.example.com",
            "api_token": "<script>alert('xss')</script>",
            "agent_id": "test-agent"
        })

        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("pathlib.Path.exists", return_value=True):
                cli = CLIContext()

                with pytest.raises(ValidationError, match="potentially dangerous content"):
                    cli.load_config(Path("test_config.json"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

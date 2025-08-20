# kei_agent/validation_models.py
"""
Pydantic validation models for KEI-Agent SDK.

Provides comprehensive input validation for all configuration classes
with proper error handling, sanitization, and security validation.
"""

from __future__ import annotations

import urllib.parse
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic.networks import HttpUrl

from .exceptions import ValidationError


class BaseValidationModel(BaseModel):
    """Base validation model with common configuration."""

    model_config = ConfigDict(
        # Validate assignment to catch runtime changes
        validate_assignment=True,
        # Allow extra fields but validate known ones
        extra="allow",
        # Use enum values instead of names
        use_enum_values=True,
        # Validate default values (Pydantic V2 compatible)
        validate_default=True,
    )


class SecurityConfigValidation(BaseValidationModel):
    """Validation model for SecurityConfig."""

    # Authentication type
    auth_type: str = Field(..., description="Authentication type")

    # API Token validation
    api_token: Optional[str] = Field(
        None, min_length=10, max_length=500, description="API token for authentication"
    )

    # OIDC Configuration
    oidc_issuer: Optional[HttpUrl] = Field(None, description="OIDC issuer URL")
    oidc_client_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="OIDC client ID",
    )
    oidc_client_secret: Optional[str] = Field(
        None, min_length=10, max_length=500, description="OIDC client secret"
    )
    oidc_scope: str = Field(
        "openid profile", min_length=1, max_length=200, description="OIDC scope"
    )

    # mTLS Configuration
    mtls_cert_path: Optional[str] = Field(None, description="mTLS certificate path")
    mtls_key_path: Optional[str] = Field(None, description="mTLS private key path")
    mtls_ca_path: Optional[str] = Field(None, description="mTLS CA certificate path")

    # TLS Options
    tls_verify: bool = Field(True, description="Enable TLS certificate verification")
    tls_ca_bundle: Optional[str] = Field(None, description="Path to custom CA bundle")
    tls_pinned_sha256: Optional[str] = Field(
        None, description="Pinned certificate SHA-256 fingerprint"
    )

    # Security Features
    rbac_enabled: bool = Field(True, description="Enable RBAC")
    audit_enabled: bool = Field(True, description="Enable audit logging")
    token_refresh_enabled: bool = Field(True, description="Enable token refresh")
    token_cache_ttl: int = Field(
        3600, ge=60, le=86400, description="Token cache TTL in seconds"
    )

    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls, v):
        """Validate API token format and security."""
        if v is None:
            return v

        # Check for placeholder values
        placeholder_patterns = [
            "your-",
            "example-",
            "placeholder",
            "dummy",
            "fake",
        ]
        if any(pattern in v.lower() for pattern in placeholder_patterns):
            raise ValidationError("API token appears to be a placeholder value")

        # Check for common weak patterns
        if v.lower() in ["token", "password", "123456", "secret"]:
            raise ValidationError("API token is too weak")

        # Ensure token has sufficient entropy
        if len(set(v)) < 5:
            raise ValidationError("API token has insufficient character diversity")

        return v

    @field_validator("oidc_client_secret")
    @classmethod
    def validate_oidc_client_secret(cls, v):
        """Validate OIDC client secret."""
        if v is None:
            return v

        # Similar validation as API token
        placeholder_patterns = [
            "your-",
            "example-",
            "placeholder",
            "dummy",
            "fake",
        ]
        if any(pattern in v.lower() for pattern in placeholder_patterns):
            raise ValidationError(
                "OIDC client secret appears to be a placeholder value"
            )

        return v

    @field_validator("mtls_cert_path", "mtls_key_path", "mtls_ca_path", "tls_ca_bundle")
    @classmethod
    def validate_file_paths(cls, v):
        """Validate certificate/CA file paths."""
        if v is None:
            return v

        path = Path(v)

        # Check for path traversal attempts
        if ".." in str(path) or str(path).startswith("/"):
            if not path.is_absolute() or ".." in path.parts:
                raise ValidationError(f"Invalid file path: {v}")

        # Validate file extension
        valid_extensions = [".pem", ".crt", ".key", ".p12", ".pfx"]
        if path.suffix.lower() not in valid_extensions:
            raise ValidationError(f"Invalid certificate file extension: {path.suffix}")

        return str(path)

    @model_validator(mode="after")
    def validate_auth_configuration(self):
        """Validate authentication configuration consistency."""
        auth_type = self.auth_type

        if auth_type == "bearer":
            if not self.api_token:
                raise ValidationError("API token is required for Bearer authentication")

        elif auth_type == "oidc":
            required_fields = ["oidc_issuer", "oidc_client_id", "oidc_client_secret"]
            missing_fields = []
            if not self.oidc_issuer:
                missing_fields.append("oidc_issuer")
            if not self.oidc_client_id:
                missing_fields.append("oidc_client_id")
            if not self.oidc_client_secret:
                missing_fields.append("oidc_client_secret")

            if missing_fields:
                raise ValidationError(
                    f"OIDC authentication requires: {', '.join(missing_fields)}"
                )

        elif auth_type == "mtls":
            required_fields = []
            if not self.mtls_cert_path:
                required_fields.append("mtls_cert_path")
            if not self.mtls_key_path:
                required_fields.append("mtls_key_path")

            if required_fields:
                raise ValidationError(
                    f"mTLS authentication requires: {', '.join(required_fields)}"
                )

        # Validate pinned fingerprint format if provided (for any auth type)
        pinned = getattr(self, "tls_pinned_sha256", None)
        if pinned is not None:
            normalized = pinned.replace(":", "").lower()
            if len(normalized) != 64 or not all(
                c in "0123456789abcdef" for c in normalized
            ):
                raise ValidationError(
                    "Invalid tls_pinned_sha256 format; expected 64 hex chars"
                )

        return self


class AgentClientConfigValidation(BaseValidationModel):
    """Validation model for AgentClientConfig."""

    # Required fields
    base_url: HttpUrl = Field(..., description="Base URL for the KEI-Agent API")
    api_token: str = Field(
        ..., min_length=10, max_length=500, description="API token for authentication"
    )
    agent_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique agent identifier",
    )

    # Optional fields
    tenant_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Tenant identifier",
    )
    user_agent: str = Field(
        "KEI-Agent-SDK/1.0.0",
        min_length=1,
        max_length=200,
        description="User agent string",
    )

    # Timeout and retry settings
    timeout: float = Field(30.0, gt=0, le=300, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum number of retries")
    retry_delay: float = Field(
        1.0, ge=0, le=60, description="Delay between retries in seconds"
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v):
        """Validate base URL format and security."""
        url_str = str(v)

        # Ensure HTTPS in production
        if not url_str.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise ValidationError("Base URL must use HTTPS or be localhost")

        # Check for suspicious patterns (excluding normal URL patterns)
        suspicious_patterns = ["..", "\\", "<", ">", '"', "'"]
        # Check for double slashes not part of protocol
        if "//" in url_str and not url_str.startswith(("http://", "https://")):
            raise ValidationError("Base URL contains suspicious characters")
        if any(pattern in url_str for pattern in suspicious_patterns):
            raise ValidationError("Base URL contains suspicious characters")

        return v

    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls, v):
        """Validate API token."""
        # Reuse validation from SecurityConfigValidation
        return SecurityConfigValidation.validate_api_token(v)

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, v):
        """Validate agent ID format."""
        # Check for reserved names
        reserved_names = ["admin", "root", "system", "api", "test", "debug"]
        if v.lower() in reserved_names:
            raise ValidationError(f"Agent ID '{v}' is reserved")

        return v


class ProtocolConfigValidation(BaseValidationModel):
    """Validation model for ProtocolConfig."""

    # Protocol enablement
    rpc_enabled: bool = Field(True, description="Enable RPC protocol")
    stream_enabled: bool = Field(True, description="Enable Stream protocol")
    bus_enabled: bool = Field(True, description="Enable Bus protocol")
    mcp_enabled: bool = Field(True, description="Enable MCP protocol")

    # Protocol selection
    auto_protocol_selection: bool = Field(
        True, description="Enable automatic protocol selection"
    )
    protocol_fallback_enabled: bool = Field(
        True, description="Enable protocol fallback"
    )
    preferred_protocol: Optional[str] = Field(
        None, pattern=r"^(rpc|stream|bus|mcp)$", description="Preferred protocol"
    )

    # Connection settings
    max_connections_per_protocol: int = Field(
        10, ge=1, le=100, description="Maximum connections per protocol"
    )
    connection_timeout: float = Field(
        30.0, gt=0, le=300, description="Connection timeout in seconds"
    )

    @model_validator(mode="after")
    def validate_protocol_configuration(self):
        """Validate protocol configuration consistency."""
        enabled_protocols = []
        if self.rpc_enabled:
            enabled_protocols.append("rpc")
        if self.stream_enabled:
            enabled_protocols.append("stream")
        if self.bus_enabled:
            enabled_protocols.append("bus")
        if self.mcp_enabled:
            enabled_protocols.append("mcp")

        if not enabled_protocols:
            raise ValidationError("At least one protocol must be enabled")

        if self.preferred_protocol:
            if self.preferred_protocol == "rpc" and not self.rpc_enabled:
                raise ValidationError("Preferred protocol 'rpc' is not enabled")
            elif self.preferred_protocol == "stream" and not self.stream_enabled:
                raise ValidationError("Preferred protocol 'stream' is not enabled")
            elif self.preferred_protocol == "bus" and not self.bus_enabled:
                raise ValidationError("Preferred protocol 'bus' is not enabled")
            elif self.preferred_protocol == "mcp" and not self.mcp_enabled:
                raise ValidationError("Preferred protocol 'mcp' is not enabled")

        return self


class InputSanitizer:
    """Utility class for input sanitization."""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")

        # Remove null bytes and control characters
        sanitized = "".join(
            char for char in value if ord(char) >= 32 or char in "\t\n\r"
        )

        # Limit length
        if len(sanitized) > max_length:
            raise ValidationError(f"String too long (max {max_length} characters)")

        return sanitized.strip()

    @staticmethod
    def sanitize_url(value: str) -> str:
        """Sanitize URL input."""
        sanitized = InputSanitizer.sanitize_string(value)

        # Parse and validate URL
        try:
            parsed = urllib.parse.urlparse(sanitized)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError("Invalid URL format")
        except Exception as e:
            raise ValidationError(f"URL parsing error: {e}")

        return sanitized

    @staticmethod
    def sanitize_file_path(value: str) -> str:
        """Sanitize file path input."""
        sanitized = InputSanitizer.sanitize_string(value)

        # Check for path traversal
        if ".." in sanitized or sanitized.startswith("/"):
            path = Path(sanitized)
            if not path.is_absolute() or ".." in path.parts:
                raise ValidationError("Path traversal detected")

        return sanitized


def validate_configuration(
    config_dict: Dict[str, Any], config_type: str
) -> Dict[str, Any]:
    """Validate configuration dictionary using appropriate model.

    Args:
        config_dict: Configuration dictionary to validate
        config_type: Type of configuration ('security', 'agent', 'protocol')

    Returns:
        Validated configuration dictionary

    Raises:
        ValidationError: If validation fails
    """
    try:
        if config_type == "security":
            model = SecurityConfigValidation(**config_dict)
        elif config_type == "agent":
            model = AgentClientConfigValidation(**config_dict)
        elif config_type == "protocol":
            model = ProtocolConfigValidation(**config_dict)
        else:
            raise ValidationError(f"Unknown configuration type: {config_type}")

        return model.dict()

    except Exception as e:
        raise ValidationError(f"Configuration validation failed: {e}") from e

# kei_agent/secrets_manager.py
"""
Secrets Management for KEI-Agent SDK.

Provides secure handling of API keys, tokens, and other sensitive configuration
with support for environment variables, external secret stores, and validation.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .exceptions import SecurityError

_logger = logging.getLogger(__name__)


@dataclass
class SecretConfig:
    """Configuration for secret management."""

    # Environment variable prefix
    env_prefix: str = "KEI_"

    # External secret store configuration
    use_external_store: bool = False
    store_type: Optional[str] = (
        None  # "aws_secrets", "azure_keyvault", "hashicorp_vault"
    )
    store_config: Optional[Dict[str, Any]] = None

    # Validation settings
    validate_secrets: bool = True
    require_all_secrets: bool = False

    def __post_init__(self) -> None:
        if self.store_config is None:
            self.store_config = {}


class SecretsManager:
    """Manages secrets and sensitive configuration for KEI-Agent SDK."""

    def __init__(self, config: Optional[SecretConfig] = None):
        """Initialize secrets manager.

        Args:
            config: Secret management configuration
        """
        self.config = config or SecretConfig()
        self._cache: Dict[str, str] = {}
        self._external_client = None

        _logger.info(
            "Secrets manager initialized",
            extra={
                "env_prefix": self.config.env_prefix,
                "external_store": self.config.use_external_store,
                "store_type": self.config.store_type,
            },
        )

    def get_secret(
        self, key: str, default: Optional[str] = None, required: bool = False
    ) -> Optional[str]:
        """Get a secret value from environment or external store.

        Args:
            key: Secret key (without prefix)
            default: Default value if secret not found
            required: Whether the secret is required

        Returns:
            Secret value or default

        Raises:
            SecurityError: If required secret is missing or invalid
        """
        # Check cache first
        cache_key = f"{self.config.env_prefix}{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try environment variable
        env_value = os.getenv(cache_key)
        if env_value:
            # Validate if enabled
            if self.config.validate_secrets:
                self._validate_secret(key, env_value)

            self._cache[cache_key] = env_value
            return env_value

        # Try external store if configured
        if self.config.use_external_store:
            try:
                external_value = self._get_from_external_store(key)
                if external_value:
                    if self.config.validate_secrets:
                        self._validate_secret(key, external_value)

                    self._cache[cache_key] = external_value
                    return external_value
            except Exception as e:
                _logger.error(
                    "Failed to retrieve secret from external store",
                    extra={
                        "key": key,
                        "error": str(e),
                        "store_type": self.config.store_type,
                    },
                )
                if required:
                    raise SecurityError(
                        f"Failed to retrieve required secret '{key}' from external store: {e}"
                    ) from e

        # Use default if provided
        if default is not None:
            return default

        # Check if required
        if required or self.config.require_all_secrets:
            raise SecurityError(
                f"Required secret '{key}' not found in environment or external store"
            )

        return None

    def get_api_token(self) -> str:
        """Get API token with validation.

        Returns:
            API token

        Raises:
            SecurityError: If token is missing or invalid
        """
        token = self.get_secret("API_TOKEN", required=True)
        if not token:
            raise SecurityError("API token is required but not configured")

        # Additional token validation
        if len(token) < 10:
            raise SecurityError("API token appears to be invalid (too short)")

        return token

    def get_oidc_credentials(self) -> Dict[str, str]:
        """Get OIDC credentials.

        Returns:
            Dictionary with OIDC configuration

        Raises:
            SecurityError: If required OIDC credentials are missing
        """
        issuer = self.get_secret("OIDC_ISSUER", required=True)
        if issuer is None:
            raise ValueError("OIDC_ISSUER is required but not found")
        client_id = self.get_secret("OIDC_CLIENT_ID", required=True)
        if client_id is None:
            raise ValueError("OIDC_CLIENT_ID is required but not found")
        client_secret = self.get_secret("OIDC_CLIENT_SECRET", required=True)
        if client_secret is None:
            raise ValueError("OIDC_CLIENT_SECRET is required but not found")
        scope = (
            self.get_secret("OIDC_SCOPE", default="openid profile") or "openid profile"
        )

        return {
            "issuer": issuer,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

    def get_mtls_paths(self) -> Dict[str, str]:
        """Get mTLS certificate paths.

        Returns:
            Dictionary with certificate paths

        Raises:
            SecurityError: If required certificate paths are missing
        """
        cert_path = self.get_secret("MTLS_CERT_PATH", required=True)
        if cert_path is None:
            raise ValueError("MTLS_CERT_PATH is required but not found")
        key_path = self.get_secret("MTLS_KEY_PATH", required=True)
        if key_path is None:
            raise ValueError("MTLS_KEY_PATH is required but not found")
        ca_path = self.get_secret("MTLS_CA_PATH")

        paths: Dict[str, str] = {
            "cert_path": cert_path,
            "key_path": key_path,
        }
        if ca_path is not None:
            paths["ca_path"] = ca_path

        # Validate paths exist
        for path_type, path in paths.items():
            if path and not Path(path).exists():
                raise SecurityError(f"mTLS {path_type} file not found: {path}")

        return paths

    def validate_configuration(self) -> bool:
        """Validate that all required secrets are available.

        Returns:
            True if all required secrets are available

        Raises:
            SecurityError: If validation fails
        """
        required_secrets = ["API_TOKEN"]
        missing_secrets = []

        for secret in required_secrets:
            if not self.get_secret(secret):
                missing_secrets.append(f"{self.config.env_prefix}{secret}")

        if missing_secrets:
            raise SecurityError(
                f"Missing required secrets: {', '.join(missing_secrets)}"
            )

        return True

    def _validate_secret(self, key: str, value: str) -> None:
        """Validate a secret value.

        Args:
            key: Secret key
            value: Secret value

        Raises:
            SecurityError: If validation fails
        """
        if not value or not value.strip():
            raise SecurityError(f"Secret '{key}' is empty or whitespace only")

        # Key-specific validation
        if "TOKEN" in key.upper():
            if len(value) < 10:
                raise SecurityError(f"Token '{key}' appears to be too short")

            # Check for placeholder values
            placeholder_patterns = ["your-", "test-", "example-", "placeholder"]
            if any(pattern in value.lower() for pattern in placeholder_patterns):
                raise SecurityError(f"Token '{key}' appears to be a placeholder value")

        if "URL" in key.upper():
            if not (value.startswith("http://") or value.startswith("https://")):
                raise SecurityError(f"URL '{key}' must start with http:// or https://")

    def _get_from_external_store(self, key: str) -> Optional[str]:
        """Get secret from external store.

        Args:
            key: Secret key

        Returns:
            Secret value or None
        """
        if not self.config.use_external_store:
            return None

        # This would be implemented based on the specific external store
        # For now, return None as external stores are not implemented
        _logger.debug(f"External store lookup for '{key}' not implemented")
        return None

    def clear_cache(self) -> None:
        """Clear the secrets cache."""
        self._cache.clear()
        _logger.debug("Secrets cache cleared")


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(config: Optional[SecretConfig] = None) -> SecretsManager:
    """Get the global secrets manager instance.

    Args:
        config: Secret management configuration

    Returns:
        SecretsManager instance
    """
    global _secrets_manager

    if _secrets_manager is None:
        _secrets_manager = SecretsManager(config)

    return _secrets_manager


def configure_secrets(config: SecretConfig) -> SecretsManager:
    """Configure the global secrets manager.

    Args:
        config: Secret management configuration

    Returns:
        Configured SecretsManager instance
    """
    global _secrets_manager
    _secrets_manager = SecretsManager(config)
    return _secrets_manager

# kei_agent/input_sanitizer.py
"""
Input sanitization and validation utilities for KEI-Agent SDK.

Provides comprehensive input sanitization for user-provided data,
CLI arguments, API endpoints, and configuration files with rate limiting
and size constraints for security.
"""

from __future__ import annotations

import re
import json
import urllib.parse

# Optional YAML support
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta

from .exceptions import ValidationError


class RateLimiter:
    """Simple rate limiter for input validation."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[datetime] = []

    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove old requests
        self.requests = [req for req in self.requests if req > cutoff]

        # Check limit
        if len(self.requests) >= self.max_requests:
            return False

        # Add current request
        self.requests.append(now)
        return True


class InputSanitizer:
    """Comprehensive input sanitization for KEI-Agent SDK."""

    # Maximum sizes for different input types
    MAX_STRING_LENGTH = 10000
    MAX_URL_LENGTH = 2000
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_JSON_DEPTH = 10
    MAX_ARRAY_LENGTH = 1000

    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        # Script injection
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"data:text/html",
        # SQL injection patterns
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r'(\b(OR|AND)\s+[\'"][^\'"]*[\'"])',
        # Command injection
        r"[;&|`$(){}[\]\\]",
        r"\b(rm|del|format|shutdown|reboot|kill)\b",
        # Path traversal
        r"\.\./|\.\.\\",
    ]

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """Initialize input sanitizer.

        Args:
            rate_limiter: Optional rate limiter instance
        """
        self.rate_limiter = rate_limiter or RateLimiter()
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS
        ]

    def check_rate_limit(self) -> None:
        """Check rate limit for input validation.

        Raises:
            ValidationError: If rate limit exceeded
        """
        if not self.rate_limiter.is_allowed():
            raise ValidationError("Rate limit exceeded for input validation")

    def sanitize_string(
        self, value: Any, max_length: Optional[int] = None, field_name: str = "input"
    ) -> str:
        """Sanitize string input with comprehensive validation.

        Args:
            value: Input value to sanitize
            max_length: Maximum allowed length
            field_name: Name of the field for error messages

        Returns:
            Sanitized string

        Raises:
            ValidationError: If validation fails
        """
        self.check_rate_limit()

        # Type validation
        if not isinstance(value, (str, int, float)):
            raise ValidationError(f"{field_name} must be a string, int, or float")

        # Convert to string
        str_value = str(value)

        # Length validation
        max_len = max_length or self.MAX_STRING_LENGTH
        if len(str_value) > max_len:
            raise ValidationError(f"{field_name} exceeds maximum length of {max_len}")

        # Remove null bytes and control characters (except common whitespace)
        sanitized = "".join(
            char for char in str_value if ord(char) >= 32 or char in "\t\n\r"
        )

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(sanitized):
                raise ValidationError(
                    f"{field_name} contains potentially dangerous content"
                )

        return sanitized.strip()

    def sanitize_url(self, value: Any, field_name: str = "URL") -> str:
        """Sanitize URL input with security validation.

        Args:
            value: URL value to sanitize
            field_name: Name of the field for error messages

        Returns:
            Sanitized URL

        Raises:
            ValidationError: If validation fails
        """
        sanitized = self.sanitize_string(value, self.MAX_URL_LENGTH, field_name)

        # Parse URL
        try:
            parsed = urllib.parse.urlparse(sanitized)
        except Exception as e:
            raise ValidationError(f"Invalid {field_name} format: {e}")

        # Validate scheme
        if parsed.scheme not in ["http", "https"]:
            raise ValidationError(f"{field_name} must use HTTP or HTTPS protocol")

        # Validate netloc
        if not parsed.netloc:
            raise ValidationError(f"{field_name} must have a valid domain")

        # Check for suspicious patterns in URL
        suspicious_patterns = ["..", "//", "\\", "<", ">", '"', "'", "`"]
        if any(pattern in sanitized for pattern in suspicious_patterns):
            raise ValidationError(f"{field_name} contains suspicious characters")

        return sanitized

    def sanitize_file_path(self, value: Any, field_name: str = "file path") -> str:
        """Sanitize file path input with security validation.

        Args:
            value: File path value to sanitize
            field_name: Name of the field for error messages

        Returns:
            Sanitized file path

        Raises:
            ValidationError: If validation fails
        """
        sanitized = self.sanitize_string(value, 500, field_name)

        # Check for path traversal
        if ".." in sanitized:
            path = Path(sanitized)
            if ".." in path.parts:
                raise ValidationError(f"{field_name} contains path traversal")

        # Validate file extension if present
        path = Path(sanitized)
        if path.suffix:
            dangerous_extensions = [
                ".exe",
                ".bat",
                ".cmd",
                ".sh",
                ".ps1",
                ".vbs",
                ".js",
            ]
            if path.suffix.lower() in dangerous_extensions:
                raise ValidationError(f"{field_name} has dangerous file extension")

        return sanitized

    def sanitize_json(self, value: Any, field_name: str = "JSON") -> Dict[str, Any]:
        """Sanitize JSON input with size and depth limits.

        Args:
            value: JSON value to sanitize (string or dict)
            field_name: Name of the field for error messages

        Returns:
            Sanitized JSON dictionary

        Raises:
            ValidationError: If validation fails
        """
        self.check_rate_limit()

        # Parse JSON if string
        if isinstance(value, str):
            sanitized_str = self.sanitize_string(value, self.MAX_FILE_SIZE, field_name)
            try:
                parsed = json.loads(sanitized_str)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid {field_name} format: {e}")
        elif isinstance(value, dict):
            parsed = value
        else:
            raise ValidationError(f"{field_name} must be a string or dictionary")

        # Validate depth and size
        self._validate_json_structure(parsed, field_name)

        return parsed

    def sanitize_yaml(self, value: Any, field_name: str = "YAML") -> Dict[str, Any]:
        """Sanitize YAML input with size and depth limits.

        Args:
            value: YAML value to sanitize (string or dict)
            field_name: Name of the field for error messages

        Returns:
            Sanitized YAML dictionary

        Raises:
            ValidationError: If validation fails
        """
        self.check_rate_limit()

        # Parse YAML if string
        if isinstance(value, str):
            sanitized_str = self.sanitize_string(value, self.MAX_FILE_SIZE, field_name)
            if not YAML_AVAILABLE:
                raise ValidationError(
                    "YAML parsing not available: pyyaml package not installed"
                )
            try:
                parsed = yaml.safe_load(sanitized_str)
            except yaml.YAMLError as e:
                raise ValidationError(f"Invalid {field_name} format: {e}")
        elif isinstance(value, dict):
            parsed = value
        else:
            raise ValidationError(f"{field_name} must be a string or dictionary")

        # Validate structure
        if parsed is not None:
            self._validate_json_structure(parsed, field_name)

        return parsed or {}

    def sanitize_cli_args(self, args: List[str]) -> List[str]:
        """Sanitize CLI arguments.

        Args:
            args: List of CLI arguments

        Returns:
            Sanitized arguments list

        Raises:
            ValidationError: If validation fails
        """
        if len(args) > 100:
            raise ValidationError("Too many CLI arguments")

        sanitized_args = []
        for i, arg in enumerate(args):
            sanitized = self.sanitize_string(arg, 1000, f"CLI argument {i}")
            sanitized_args.append(sanitized)

        return sanitized_args

    def _validate_json_structure(
        self, obj: Any, field_name: str, depth: int = 0
    ) -> None:
        """Validate JSON structure depth and size.

        Args:
            obj: Object to validate
            field_name: Field name for error messages
            depth: Current depth level

        Raises:
            ValidationError: If validation fails
        """
        if depth > self.MAX_JSON_DEPTH:
            raise ValidationError(
                f"{field_name} exceeds maximum depth of {self.MAX_JSON_DEPTH}"
            )

        if isinstance(obj, dict):
            if len(obj) > self.MAX_ARRAY_LENGTH:
                raise ValidationError(f"{field_name} dictionary too large")

            for key, value in obj.items():
                # Validate key
                if not isinstance(key, str):
                    raise ValidationError(f"{field_name} keys must be strings")
                if len(key) > 100:
                    raise ValidationError(f"{field_name} key too long: {key}")

                # Recursively validate value
                self._validate_json_structure(value, field_name, depth + 1)

        elif isinstance(obj, list):
            if len(obj) > self.MAX_ARRAY_LENGTH:
                raise ValidationError(f"{field_name} array too large")

            for item in obj:
                self._validate_json_structure(item, field_name, depth + 1)

        elif isinstance(obj, str):
            if len(obj) > self.MAX_STRING_LENGTH:
                raise ValidationError(f"{field_name} string value too long")


# Global sanitizer instance
_sanitizer: Optional[InputSanitizer] = None


def get_sanitizer() -> InputSanitizer:
    """Get the global input sanitizer instance."""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = InputSanitizer()
    return _sanitizer


def sanitize_input(value: Any, input_type: str = "string", **kwargs) -> Any:
    """Convenience function for input sanitization.

    Args:
        value: Value to sanitize
        input_type: Type of input ('string', 'url', 'file_path', 'json', 'yaml')
        **kwargs: Additional arguments for sanitization

    Returns:
        Sanitized value
    """
    sanitizer = get_sanitizer()

    if input_type == "string":
        return sanitizer.sanitize_string(value, **kwargs)
    elif input_type == "url":
        return sanitizer.sanitize_url(value, **kwargs)
    elif input_type == "file_path":
        return sanitizer.sanitize_file_path(value, **kwargs)
    elif input_type == "json":
        return sanitizer.sanitize_json(value, **kwargs)
    elif input_type == "yaml":
        return sanitizer.sanitize_yaml(value, **kwargs)
    else:
        raise ValidationError(f"Unknown input type: {input_type}")

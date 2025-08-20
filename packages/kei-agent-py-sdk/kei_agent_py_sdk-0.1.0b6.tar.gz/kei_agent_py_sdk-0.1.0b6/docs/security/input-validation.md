# Input Validation and Security

The KEI-Agent Python SDK implements comprehensive input validation and sanitization to protect against security vulnerabilities and ensure data integrity.

## Overview

The SDK provides multiple layers of input validation:

1. **Pydantic Models** - Schema validation for configuration objects
2. **Input Sanitization** - Content filtering and dangerous pattern detection
3. **Rate Limiting** - Protection against abuse
4. **Security Validation** - Credential and URL security checks

## Configuration Validation

### Security Configuration

```python
from kei_agent import SecurityConfig
from kei_agent.exceptions import ValidationError

# Valid configuration
config = SecurityConfig(
    auth_type="bearer",
    api_token=os.getenv("KEI_API_TOKEN"),  # From environment
    rbac_enabled=True,
    audit_enabled=True
)

# Validation is automatic
try:
    config.validate()
    print("Configuration is valid")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Agent Configuration

```python
from kei_agent import AgentClientConfig

config = AgentClientConfig(
    base_url="https://api.example.com",  # Must be HTTPS
    api_token=os.getenv("KEI_API_TOKEN"),
    agent_id="my-agent",  # No reserved names
    timeout=30.0,
    max_retries=3
)

# Automatic validation on creation
config.validate()
```

## Input Sanitization

### String Sanitization

```python
from kei_agent.input_sanitizer import get_sanitizer

sanitizer = get_sanitizer()

# Safe string sanitization
safe_input = sanitizer.sanitize_string(
    user_input,
    max_length=1000,
    field_name="user_message"
)

# Dangerous content is blocked
try:
    sanitizer.sanitize_string("<script>alert('xss')</script>")
except ValidationError:
    print("Dangerous content detected and blocked")
```

### URL Validation

```python
# URL sanitization with security checks
safe_url = sanitizer.sanitize_url(
    "https://api.example.com/endpoint",
    field_name="api_endpoint"
)

# HTTP URLs are only allowed for localhost
try:
    sanitizer.sanitize_url("http://external.com")  # Blocked
except ValidationError:
    print("Insecure URL blocked")
```

### File Path Validation

```python
# File path sanitization
safe_path = sanitizer.sanitize_file_path(
    "config/settings.json",
    field_name="config_file"
)

# Path traversal attempts are blocked
try:
    sanitizer.sanitize_file_path("../../../etc/passwd")
except ValidationError:
    print("Path traversal attempt blocked")
```

### JSON/YAML Validation

```python
# JSON sanitization with depth and size limits
config_data = sanitizer.sanitize_json(
    '{"api_url": "https://api.example.com", "timeout": 30}',
    field_name="configuration"
)

# YAML sanitization
yaml_data = sanitizer.sanitize_yaml(
    yaml_content,
    field_name="config_file"
)
```

## Rate Limiting

```python
from kei_agent.input_sanitizer import RateLimiter, InputSanitizer

# Custom rate limiter
rate_limiter = RateLimiter(max_requests=50, window_seconds=60)
sanitizer = InputSanitizer(rate_limiter)

# Rate limiting is automatically applied
try:
    for i in range(100):
        sanitizer.sanitize_string(f"input_{i}")
except ValidationError as e:
    print(f"Rate limit exceeded: {e}")
```

## Security Features

### Credential Validation

The SDK automatically validates credentials to prevent common security issues:

```python
# API token validation
config = SecurityConfig(
    auth_type="bearer",
    api_token="your-token-here"  # Placeholder detected!
)

try:
    config.validate()
except ValidationError:
    print("Placeholder token detected - use real credentials")
```

### Dangerous Pattern Detection

The input sanitizer detects and blocks:

- **Script injection**: `<script>`, `javascript:`, `vbscript:`
- **SQL injection**: `SELECT`, `UNION`, `OR 1=1`
- **Command injection**: `;`, `|`, `$()`
- **Path traversal**: `../`, `..\`

### Reserved Name Protection

```python
config = AgentClientConfig(
    base_url="https://api.example.com",
    api_token=os.getenv("KEI_API_TOKEN"),
    agent_id="admin"  # Reserved name!
)

try:
    config.validate()
except ValidationError:
    print("Reserved agent ID blocked")
```

## CLI Integration

The CLI automatically sanitizes all input:

```python
from kei_agent.cli import CLIContext

cli = CLIContext()

# Configuration files are sanitized
config = cli.load_config("config.json")  # Automatic sanitization

# Environment variables are sanitized
config = cli.load_config()  # From environment with sanitization
```

## Best Practices

### 1. Always Use Environment Variables

```python
# ✅ Good - Use environment variables
config = SecurityConfig(
    auth_type="bearer",
    api_token=os.getenv("KEI_API_TOKEN")
)

# ❌ Bad - Hardcoded credentials
config = SecurityConfig(
    auth_type="bearer",
    api_token="hardcoded-token-123"
)
```

### 2. Validate Early and Often

```python
# Validate configuration immediately
config = AgentClientConfig(...)
config.validate()  # Fail fast

# Sanitize user input
user_data = sanitizer.sanitize_string(user_input)
```

### 3. Use Specific Field Names

```python
# Provide descriptive field names for better error messages
sanitizer.sanitize_string(value, field_name="user_message")
sanitizer.sanitize_url(url, field_name="webhook_endpoint")
```

### 4. Handle Validation Errors Gracefully

```python
try:
    config.validate()
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    # Provide helpful error message to user
    return {"error": "Invalid configuration", "details": str(e)}
```

## Configuration Limits

The SDK enforces the following limits for security:

| Input Type | Maximum Size | Additional Limits |
|------------|--------------|-------------------|
| String | 10,000 chars | Control char removal |
| URL | 2,000 chars | HTTPS required |
| File Path | 500 chars | No path traversal |
| JSON | 10 MB | Max depth: 10 levels |
| Array | 1,000 items | Per array limit |
| Rate Limit | 100 req/min | Configurable |

## Error Handling

All validation errors inherit from `ValidationError`:

```python
from kei_agent.exceptions import ValidationError

try:
    # Validation operation
    config.validate()
except ValidationError as e:
    # Handle validation error
    print(f"Validation failed: {e}")
    # Log for security monitoring
    logger.warning(f"Input validation failed: {e}")
```

## Security Monitoring

Enable audit logging to monitor validation failures:

```python
config = SecurityConfig(
    auth_type="bearer",
    api_token=os.getenv("KEI_API_TOKEN"),
    audit_enabled=True  # Enable security audit logging
)
```

Validation failures are automatically logged for security monitoring and can be integrated with SIEM systems.

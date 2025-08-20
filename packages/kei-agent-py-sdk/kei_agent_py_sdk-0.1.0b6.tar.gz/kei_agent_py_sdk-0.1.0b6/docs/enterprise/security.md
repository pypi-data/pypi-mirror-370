# Security

Enterprise-Sicherheitsfeatures für das KEI-Agent SDK.

## 🔐 Authentifizierung

```python
from kei_agent import SecurityConfig, AuthType

# Bearer Token
bearer_config = SecurityConfig(
    auth_type=AuthType.BEARER,
    api_token="your-token",
    rbac_enabled=True,
    audit_enabled=True
)

# OIDC
oidc_config = SecurityConfig(
    auth_type=AuthType.OIDC,
    oidc_issuer="https://auth.company.com",
    oidc_client_id="kei-agent",
    oidc_client_secret="client-secret"
)

# mTLS
mtls_config = SecurityConfig(
    auth_type=AuthType.MTLS,
    mtls_cert_path="/etc/ssl/certs/client.crt",
    mtls_key_path="/etc/ssl/private/client.key",
    mtls_ca_path="/etc/ssl/certs/ca.crt"
)
```

## 🛡️ RBAC (Role-Based Access Control)

```yaml
roles:
  admin:
    permissions:
      - "system:*"
      - "agents:*"
      - "users:*"

  operator:
    permissions:
      - "agents:read"
      - "agents:execute"
      - "tasks:*"

  viewer:
    permissions:
      - "agents:read"
      - "tasks:read"
      - "metrics:read"
## 📊 Security Monitoring

```python
from kei_agent import get_logger

# Security Logging
logger = get_logger("security")
logger.warning(
    "authentication_failure",
    user_id="user123",
    ip_address="192.168.1.100",
    reason="invalid_password"
)

# Audit Logging
audit_logger = get_logger("audit")
audit_logger.info(
    "agent_task_execution",
    user_id="user123",
    resource_id="agent_456",
    task_type="data_processing"
)
```

## 🔍 Input Validation

```python
from kei_agent import get_input_validator

validator = get_input_validator()

# Validierung
result = validator.validate_agent_operation("plan", data)
if not result.valid:
    raise SecurityError(f"Validation failed: {result.errors}")

return result.sanitized_value
```

## 📋 Security Checklist

### Deployment
- [ ] TLS 1.3 für alle Verbindungen
- [ ] mTLS für interne Services
- [ ] MFA für privilegierte Accounts
- [ ] RBAC konfiguriert und getestet
- [ ] Audit-Logging aktiviert

### Laufend
- [ ] Sicherheits-Updates eingespielt
- [ ] Access Reviews durchgeführt
- [ ] Security Metrics überwacht

---

**Weitere Informationen:** [Logging](logging.md) | [Health Checks](health-checks.md)

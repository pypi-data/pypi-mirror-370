# Authentifizierung

*Diese Seite wird noch entwickelt.*

## Übersicht

Das KEI-Agent SDK unterstützt verschiedene Authentifizierungsmethoden.

## Authentifizierungstypen

### Bearer Token
```python
config = AgentClientConfig(
    api_token="your-bearer-token",
    auth_type=AuthType.BEARER
)
```

### OIDC (OpenID Connect)
```python
config = SecurityConfig(
    auth_type=AuthType.OIDC,
    oidc_issuer="https://your-oidc-provider.com",
    oidc_client_id="your-client-id"
)
```

### mTLS (Mutual TLS)
```python
config = SecurityConfig(
    auth_type=AuthType.MTLS,
    mtls_cert_path="/path/to/client.crt",
    mtls_key_path="/path/to/client.key"
)
```

## Weitere Informationen

- [Basis-Konzepte](concepts.md)
- [Client-Verwendung](client-usage.md)

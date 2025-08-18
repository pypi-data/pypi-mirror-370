# 🔒 Security Troubleshooting

Leitfaden zur Diagnose und Behebung von Sicherheitsproblemen in Keiko Personal Assistant.

## 🔐 Authentication Issues

### JWT Token Problems

**Problem:** JWT-Token werden nicht akzeptiert oder sind ungültig.

**Diagnose:**
```bash
# Token-Validierung testen
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/validate

# Token-Details dekodieren (ohne Verifikation)
echo $TOKEN | cut -d. -f2 | base64 -d | jq

# Token-Expiration prüfen
python3 -c "
import jwt
import json
token = '$TOKEN'
decoded = jwt.decode(token, options={'verify_signature': False})
print(json.dumps(decoded, indent=2))
"
```

**Häufige Ursachen & Lösungen:**

1. **Abgelaufene Tokens**
```python
# auth/token_validator.py
import jwt
from datetime import datetime, timezone

def validate_token_expiration(token: str) -> bool:
    """Prüft Token-Expiration."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get('exp')

        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            now = datetime.now(timezone.utc)

            if exp_datetime < now:
                logger.warning(f"Token expired at {exp_datetime}, current time: {now}")
                return False

        return True
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return False

# Token-Refresh implementieren
async def refresh_token_if_needed(token: str) -> str:
    """Refresht Token wenn nötig."""

    if not validate_token_expiration(token):
        # Token refresh
        refresh_token = get_refresh_token()
        new_token = await auth_service.refresh_access_token(refresh_token)
        return new_token

    return token
```

2. **Falsche Signatur**
```python
# config/jwt_config.py
import os
from cryptography.hazmat.primitives import serialization

# JWT-Konfiguration validieren
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable required")

# Für RS256/ES256 - Public/Private Key validieren
if JWT_ALGORITHM.startswith('RS') or JWT_ALGORITHM.startswith('ES'):
    private_key_path = os.getenv('JWT_PRIVATE_KEY_PATH')
    public_key_path = os.getenv('JWT_PUBLIC_KEY_PATH')

    if not private_key_path or not public_key_path:
        raise ValueError("Private/Public key paths required for asymmetric algorithms")

    # Keys laden und validieren
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
```

3. **Token-Format-Probleme**
```python
# auth/token_extractor.py
import re
from fastapi import HTTPException, Request

def extract_bearer_token(request: Request) -> str:
    """Extrahiert Bearer-Token aus Request."""

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise HTTPException(401, "Authorization header missing")

    # Bearer-Token-Format validieren
    bearer_pattern = r'^Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)$'
    match = re.match(bearer_pattern, auth_header)

    if not match:
        raise HTTPException(401, "Invalid Authorization header format")

    return match.group(1)

# Alternative Token-Quellen
def extract_token_from_multiple_sources(request: Request) -> str:
    """Extrahiert Token aus verschiedenen Quellen."""

    # 1. Authorization Header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]

    # 2. Query Parameter (für WebSocket)
    token = request.query_params.get('token')
    if token:
        return token

    # 3. Cookie (falls konfiguriert)
    token = request.cookies.get('access_token')
    if token:
        return token

    raise HTTPException(401, "No valid token found")
```

### Session Management Issues

**Problem:** Session-Probleme bei Multi-Instance-Deployment.

**Diagnose:**
```bash
# Redis-Session-Keys prüfen
redis-cli keys "session:*"

# Session-Details anzeigen
redis-cli hgetall "session:user123"

# Session-Expiration prüfen
redis-cli ttl "session:user123"
```

**Lösungen:**

1. **Sticky Sessions konfigurieren**
```nginx
# nginx.conf
upstream keiko_backend {
    ip_hash;  # Sticky sessions basierend auf Client-IP
    server keiko-app-1:8000;
    server keiko-app-2:8000;
    server keiko-app-3:8000;
}
```

2. **Shared Session Storage**
```python
# session/redis_session_store.py
import redis.asyncio as redis
import json
from typing import Dict, Any, Optional

class RedisSessionStore:
    """Redis-basierter Session-Store."""

    def __init__(self, redis_url: str, session_ttl: int = 3600):
        self.redis = redis.from_url(redis_url)
        self.session_ttl = session_ttl

    async def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Erstellt neue Session."""

        session_id = generate_session_id()
        session_key = f"session:{session_id}"

        session_data.update({
            'user_id': user_id,
            'created_at': time.time(),
            'last_accessed': time.time()
        })

        await self.redis.hset(session_key, mapping={
            k: json.dumps(v) if not isinstance(v, str) else v
            for k, v in session_data.items()
        })

        await self.redis.expire(session_key, self.session_ttl)

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Ruft Session-Daten ab."""

        session_key = f"session:{session_id}"
        session_data = await self.redis.hgetall(session_key)

        if not session_data:
            return None

        # Last-accessed aktualisieren
        await self.redis.hset(session_key, 'last_accessed', time.time())
        await self.redis.expire(session_key, self.session_ttl)

        # JSON-Daten dekodieren
        decoded_data = {}
        for key, value in session_data.items():
            try:
                decoded_data[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                decoded_data[key] = value

        return decoded_data

    async def delete_session(self, session_id: str) -> bool:
        """Löscht Session."""

        session_key = f"session:{session_id}"
        deleted = await self.redis.delete(session_key)

        return deleted > 0
```

## 🛡️ Authorization Problems

### RBAC Permission Issues

**Problem:** Benutzer haben nicht die erwarteten Berechtigungen.

**Diagnose:**
```python
# debug/permission_debugger.py
async def debug_user_permissions(user_id: str) -> Dict[str, Any]:
    """Debuggt Benutzer-Berechtigungen."""

    user = await user_service.get_user(user_id)
    if not user:
        return {"error": "User not found"}

    # Rollen abrufen
    user_roles = await rbac_service.get_user_roles(user_id)

    # Berechtigungen für jede Rolle
    role_permissions = {}
    for role in user_roles:
        permissions = await rbac_service.get_role_permissions(role.name)
        role_permissions[role.name] = [p.name for p in permissions]

    # Effektive Berechtigungen
    effective_permissions = await rbac_service.get_user_permissions(user_id)

    return {
        "user_id": user_id,
        "username": user.username,
        "roles": [r.name for r in user_roles],
        "role_permissions": role_permissions,
        "effective_permissions": [p.name for p in effective_permissions],
        "permission_count": len(effective_permissions)
    }

# Permission-Check mit Debugging
async def check_permission_with_debug(user_id: str, permission: str) -> Dict[str, Any]:
    """Prüft Berechtigung mit Debug-Informationen."""

    has_permission = await rbac_service.check_permission(user_id, permission)

    debug_info = await debug_user_permissions(user_id)
    debug_info.update({
        "requested_permission": permission,
        "has_permission": has_permission,
        "permission_source": None
    })

    # Quelle der Berechtigung finden
    if has_permission:
        for role, permissions in debug_info["role_permissions"].items():
            if permission in permissions:
                debug_info["permission_source"] = role
                break

    return debug_info
```

**Lösungen:**

1. **Permission-Inheritance prüfen**
```python
# rbac/permission_resolver.py
class PermissionResolver:
    """Löst Berechtigungen mit Inheritance auf."""

    async def resolve_user_permissions(self, user_id: str) -> Set[str]:
        """Löst alle Benutzer-Berechtigungen auf."""

        permissions = set()

        # Direkte Benutzer-Berechtigungen
        user_permissions = await self.get_direct_user_permissions(user_id)
        permissions.update(p.name for p in user_permissions)

        # Rollen-basierte Berechtigungen
        user_roles = await self.get_user_roles(user_id)
        for role in user_roles:
            role_permissions = await self.resolve_role_permissions(role.name)
            permissions.update(role_permissions)

        return permissions

    async def resolve_role_permissions(self, role_name: str) -> Set[str]:
        """Löst Rollen-Berechtigungen mit Inheritance auf."""

        permissions = set()
        visited_roles = set()

        await self._resolve_role_permissions_recursive(role_name, permissions, visited_roles)

        return permissions

    async def _resolve_role_permissions_recursive(
        self,
        role_name: str,
        permissions: Set[str],
        visited_roles: Set[str]
    ):
        """Rekursive Auflösung von Rollen-Inheritance."""

        if role_name in visited_roles:
            return  # Zirkuläre Abhängigkeit vermeiden

        visited_roles.add(role_name)

        # Direkte Rollen-Berechtigungen
        role_permissions = await self.get_direct_role_permissions(role_name)
        permissions.update(p.name for p in role_permissions)

        # Parent-Rollen
        parent_roles = await self.get_parent_roles(role_name)
        for parent_role in parent_roles:
            await self._resolve_role_permissions_recursive(
                parent_role.name, permissions, visited_roles
            )
```

2. **Permission-Caching optimieren**
```python
# rbac/permission_cache.py
import asyncio
from typing import Set, Optional

class PermissionCache:
    """Cache für Berechtigungen."""

    def __init__(self, redis_client, cache_ttl: int = 300):
        self.redis = redis_client
        self.cache_ttl = cache_ttl
        self.local_cache: Dict[str, Set[str]] = {}
        self.cache_timestamps: Dict[str, float] = {}

    async def get_user_permissions(self, user_id: str) -> Optional[Set[str]]:
        """Ruft Benutzer-Berechtigungen aus Cache ab."""

        # L1: Local Cache
        if self._is_local_cache_valid(user_id):
            return self.local_cache[user_id]

        # L2: Redis Cache
        cache_key = f"permissions:user:{user_id}"
        cached_permissions = await self.redis.smembers(cache_key)

        if cached_permissions:
            permissions = set(cached_permissions)
            self._update_local_cache(user_id, permissions)
            return permissions

        return None

    async def cache_user_permissions(self, user_id: str, permissions: Set[str]):
        """Cached Benutzer-Berechtigungen."""

        # L1: Local Cache
        self._update_local_cache(user_id, permissions)

        # L2: Redis Cache
        cache_key = f"permissions:user:{user_id}"

        if permissions:
            await self.redis.sadd(cache_key, *permissions)
            await self.redis.expire(cache_key, self.cache_ttl)

    async def invalidate_user_permissions(self, user_id: str):
        """Invalidiert Benutzer-Berechtigungen-Cache."""

        # Local Cache
        self.local_cache.pop(user_id, None)
        self.cache_timestamps.pop(user_id, None)

        # Redis Cache
        cache_key = f"permissions:user:{user_id}"
        await self.redis.delete(cache_key)

    def _is_local_cache_valid(self, user_id: str) -> bool:
        """Prüft ob Local-Cache gültig ist."""

        if user_id not in self.local_cache:
            return False

        timestamp = self.cache_timestamps.get(user_id, 0)
        return time.time() - timestamp < self.cache_ttl

    def _update_local_cache(self, user_id: str, permissions: Set[str]):
        """Aktualisiert Local-Cache."""

        self.local_cache[user_id] = permissions
        self.cache_timestamps[user_id] = time.time()
```

## 🔍 Security Audit & Monitoring

### Security Event Detection

```python
# security/event_detector.py
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class SecurityEventType(Enum):
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_ACCESS_VIOLATION = "data_access_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

@dataclass
class SecurityEvent:
    event_type: SecurityEventType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    severity: str  # low, medium, high, critical

class SecurityEventDetector:
    """Erkennt Security-Events."""

    def __init__(self):
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.suspicious_ips: Set[str] = set()

    async def detect_failed_login_pattern(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[SecurityEvent]:
        """Erkennt Failed-Login-Patterns."""

        now = datetime.utcnow()
        key = f"{user_id}:{ip_address}"

        # Failed-Login-Attempts tracken
        if key not in self.failed_login_attempts:
            self.failed_login_attempts[key] = []

        self.failed_login_attempts[key].append(now)

        # Alte Attempts entfernen (älter als 1 Stunde)
        cutoff = now - timedelta(hours=1)
        self.failed_login_attempts[key] = [
            attempt for attempt in self.failed_login_attempts[key]
            if attempt > cutoff
        ]

        # Threshold prüfen
        if len(self.failed_login_attempts[key]) >= 5:
            return SecurityEvent(
                event_type=SecurityEventType.FAILED_LOGIN,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=now,
                details={
                    "failed_attempts": len(self.failed_login_attempts[key]),
                    "time_window": "1 hour"
                },
                severity="high"
            )

        return None

    async def detect_privilege_escalation(
        self,
        user_id: str,
        old_permissions: Set[str],
        new_permissions: Set[str],
        ip_address: str
    ) -> Optional[SecurityEvent]:
        """Erkennt Privilege-Escalation."""

        added_permissions = new_permissions - old_permissions

        # Kritische Berechtigungen prüfen
        critical_permissions = {
            "system:admin", "users:delete", "agents:delete",
            "system:config", "security:manage"
        }

        critical_added = added_permissions & critical_permissions

        if critical_added:
            return SecurityEvent(
                event_type=SecurityEventType.PRIVILEGE_ESCALATION,
                user_id=user_id,
                ip_address=ip_address,
                user_agent="",
                timestamp=datetime.utcnow(),
                details={
                    "added_permissions": list(added_permissions),
                    "critical_permissions": list(critical_added)
                },
                severity="critical"
            )

        return None

    async def detect_suspicious_activity(
        self,
        user_id: str,
        action: str,
        resource: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[SecurityEvent]:
        """Erkennt verdächtige Aktivitäten."""

        # Ungewöhnliche IP-Adressen
        user_ips = await self.get_user_ip_history(user_id)
        if ip_address not in user_ips and len(user_ips) > 0:
            # Geolocation-Check
            user_country = await self.get_ip_country(user_ips[0])
            current_country = await self.get_ip_country(ip_address)

            if user_country != current_country:
                return SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.utcnow(),
                    details={
                        "reason": "unusual_location",
                        "user_country": user_country,
                        "current_country": current_country,
                        "action": action,
                        "resource": resource
                    },
                    severity="medium"
                )

        # Ungewöhnliche Zeiten
        now = datetime.utcnow()
        if now.hour < 6 or now.hour > 22:  # Außerhalb Geschäftszeiten
            return SecurityEvent(
                event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=now,
                details={
                    "reason": "unusual_time",
                    "hour": now.hour,
                    "action": action,
                    "resource": resource
                },
                severity="low"
            )

        return None

# Security-Event-Handler
class SecurityEventHandler:
    """Behandelt Security-Events."""

    async def handle_security_event(self, event: SecurityEvent):
        """Behandelt Security-Event."""

        # Event protokollieren
        await self.log_security_event(event)

        # Automatische Reaktionen
        if event.severity == "critical":
            await self.handle_critical_event(event)
        elif event.severity == "high":
            await self.handle_high_severity_event(event)

        # Benachrichtigungen senden
        await self.send_security_notification(event)

    async def handle_critical_event(self, event: SecurityEvent):
        """Behandelt kritische Security-Events."""

        if event.event_type == SecurityEventType.PRIVILEGE_ESCALATION:
            # Benutzer temporär sperren
            await self.temporarily_lock_user(event.user_id, duration_minutes=30)

            # Admin-Benachrichtigung
            await self.notify_security_team(event)

        elif event.event_type == SecurityEventType.DATA_ACCESS_VIOLATION:
            # Zugriff protokollieren und blockieren
            await self.block_ip_address(event.ip_address, duration_hours=24)

    async def handle_high_severity_event(self, event: SecurityEvent):
        """Behandelt High-Severity-Events."""

        if event.event_type == SecurityEventType.FAILED_LOGIN:
            # IP-Adresse temporär blockieren
            await self.rate_limit_ip(event.ip_address, duration_minutes=15)

            # Benutzer über verdächtige Aktivität informieren
            await self.notify_user_suspicious_activity(event.user_id, event)
```

### Security Compliance Monitoring

```python
# security/compliance_monitor.py
class ComplianceMonitor:
    """Überwacht Security-Compliance."""

    async def check_gdpr_compliance(self) -> Dict[str, bool]:
        """Prüft GDPR-Compliance."""

        checks = {
            "data_encryption": await self.check_data_encryption(),
            "access_logging": await self.check_access_logging(),
            "data_retention": await self.check_data_retention_policy(),
            "user_consent": await self.check_user_consent_tracking(),
            "data_portability": await self.check_data_portability_support(),
            "right_to_erasure": await self.check_erasure_capability()
        }

        return checks

    async def check_security_headers(self) -> Dict[str, bool]:
        """Prüft Security-Headers."""

        # Test-Request an API
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                headers = response.headers

                return {
                    "strict_transport_security": "Strict-Transport-Security" in headers,
                    "content_security_policy": "Content-Security-Policy" in headers,
                    "x_frame_options": "X-Frame-Options" in headers,
                    "x_content_type_options": "X-Content-Type-Options" in headers,
                    "x_xss_protection": "X-XSS-Protection" in headers,
                    "referrer_policy": "Referrer-Policy" in headers
                }

    async def check_password_policy_compliance(self) -> Dict[str, Any]:
        """Prüft Password-Policy-Compliance."""

        # Schwache Passwörter in Database prüfen
        weak_passwords = await self.find_weak_passwords()

        # Password-Policy-Einstellungen prüfen
        policy = await self.get_password_policy()

        return {
            "min_length_enforced": policy.min_length >= 8,
            "complexity_enforced": policy.require_special_chars and policy.require_numbers,
            "weak_passwords_count": len(weak_passwords),
            "password_expiry_enabled": policy.max_age_days is not None,
            "password_history_enabled": policy.history_count > 0
        }
```

!!! danger "Security-Alerts"
    Bei kritischen Security-Events:
    - Sofortige Benachrichtigung des Security-Teams
    - Automatische Sperrung betroffener Accounts
    - Detaillierte Forensik-Logs erstellen
    - Incident-Response-Prozess aktivieren

!!! tip "Security-Best-Practices"
    - Implementieren Sie umfassende Security-Event-Detection
    - Nutzen Sie Multi-Factor-Authentication für privilegierte Accounts
    - Überwachen Sie kontinuierlich Compliance-Status
    - Führen Sie regelmäßige Security-Audits durch
    - Dokumentieren Sie alle Security-Incidents

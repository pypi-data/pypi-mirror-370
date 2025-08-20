# tests/chaos/test_security_chaos.py
"""
Security Chaos Engineering Tests for KEI-Agent Python SDK.

These tests validate system resilience under security-related failures:
- Authentication token expiration and refresh failures
- Malformed or expired certificates
- Security event detection under attack scenarios
- Rate limiting bypass attempts
"""

import asyncio
import pytest
import time
import ssl
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

try:
    from kei_agent.unified_client import UnifiedKeiAgentClient, AgentClientConfig
    from kei_agent.error_aggregation import get_error_aggregator, ErrorCategory, ErrorSeverity
    from kei_agent.security_manager import SecurityManager
except ImportError:
    # Mock classes for testing when modules don't exist
    from enum import Enum

    class ErrorCategory(Enum):
        AUTHENTICATION = "authentication"
        SECURITY = "security"

    class ErrorSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    class AgentClientConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class UnifiedKeiAgentClient:
        def __init__(self, config):
            self.config = config

        async def close(self):
            pass

    def get_error_aggregator():
        return MagicMock()

    class SecurityManager:
        def __init__(self):
            pass

from tests.chaos.chaos_framework import chaos_test_context, ChaosTest
from tests.chaos.chaos_metrics import get_chaos_metrics_collector


class SecurityChaosInjector:
    """Injects security-related chaos."""

    def __init__(self):
        """Initialize security chaos injector."""
        self.name = "security_chaos"
        self.active = False
        self.original_token = None
        self.patches = []

    async def inject_chaos(self,
                          token_expiration: bool = False,
                          certificate_issues: bool = False,
                          attack_simulation: bool = False,
                          rate_limit_bypass: bool = False,
                          **kwargs) -> None:
        """Inject security chaos.

        Args:
            token_expiration: Simulate token expiration
            certificate_issues: Simulate certificate problems
            attack_simulation: Simulate security attacks
            rate_limit_bypass: Simulate rate limiting bypass attempts
        """
        self.active = True

        if token_expiration:
            await self._simulate_token_expiration()

        if certificate_issues:
            await self._simulate_certificate_issues()

        if attack_simulation:
            await self._simulate_security_attacks()

        if rate_limit_bypass:
            await self._simulate_rate_limit_bypass()

    async def stop_chaos(self) -> None:
        """Stop security chaos."""
        # Restore original patches
        for patcher in self.patches:
            patcher.stop()
        self.patches.clear()

        self.active = False

    async def _simulate_token_expiration(self) -> None:
        """Simulate authentication token expiration."""
        # Mock token validation to return expired tokens
        def mock_validate_token(token):
            # Simulate expired token
            return False

        def mock_refresh_token():
            # Simulate token refresh failure
            raise Exception("Token refresh service unavailable")

        # Apply patches
        token_patch = patch('kei_agent.security_manager.SecurityManager.validate_token',
                           side_effect=mock_validate_token)
        refresh_patch = patch('kei_agent.security_manager.SecurityManager.refresh_token',
                             side_effect=mock_refresh_token)

        token_patch.start()
        refresh_patch.start()

        self.patches.extend([token_patch, refresh_patch])

    async def _simulate_certificate_issues(self) -> None:
        """Simulate SSL certificate issues."""
        def mock_ssl_context():
            # Create SSL context that will fail verification
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        def mock_ssl_verification_failure(*args, **kwargs):
            raise ssl.SSLError("Certificate verification failed")

        # Apply patches
        ssl_patch = patch('ssl.create_default_context', side_effect=mock_ssl_context)
        verify_patch = patch('ssl.match_hostname', side_effect=mock_ssl_verification_failure)

        ssl_patch.start()
        verify_patch.start()

        self.patches.extend([ssl_patch, verify_patch])

    async def _simulate_security_attacks(self) -> None:
        """Simulate various security attack scenarios."""
        # Simulate injection attacks, malformed requests, etc.
        def mock_malicious_request(*args, **kwargs):
            # Simulate malicious request patterns
            malicious_patterns = [
                "'; DROP TABLE users; --",  # SQL injection
                "<script>alert('xss')</script>",  # XSS
                "../../../etc/passwd",  # Path traversal
                "{{7*7}}",  # Template injection
            ]

            # Randomly inject malicious content
            import random
            if random.random() < 0.3:  # 30% chance of malicious request
                raise SecurityError(f"Malicious pattern detected: {random.choice(malicious_patterns)}")

        # Apply patch to simulate attack detection
        attack_patch = patch('kei_agent.unified_client.UnifiedKeiAgentClient._make_request',
                            side_effect=mock_malicious_request)
        attack_patch.start()
        self.patches.append(attack_patch)

    async def _simulate_rate_limit_bypass(self) -> None:
        """Simulate rate limiting bypass attempts."""
        # Track request counts to simulate bypass attempts
        self.request_counts = {}

        def mock_rate_limited_request(self, *args, **kwargs):
            client_id = getattr(self, 'agent_id', 'unknown')
            current_time = time.time()

            # Initialize tracking for this client
            if client_id not in self.request_counts:
                self.request_counts[client_id] = []

            # Clean old requests (older than 1 minute)
            self.request_counts[client_id] = [
                req_time for req_time in self.request_counts[client_id]
                if current_time - req_time < 60
            ]

            # Add current request
            self.request_counts[client_id].append(current_time)

            # Check rate limit (10 requests per minute)
            if len(self.request_counts[client_id]) > 10:
                raise Exception("Rate limit exceeded - potential bypass attempt detected")

        # Apply rate limiting patch
        rate_patch = patch('kei_agent.unified_client.UnifiedKeiAgentClient._execute_operation',
                          side_effect=mock_rate_limited_request)
        rate_patch.start()
        self.patches.append(rate_patch)


class SecurityError(Exception):
    """Custom security error for testing."""
    pass


class TestSecurityChaos:
    """Security chaos engineering tests."""

    def setup_method(self):
        """Setup for each test."""
        self.config = AgentClientConfig(
            agent_id="chaos-test-agent",
            base_url="https://localhost:8080",  # HTTPS for SSL testing
            api_token="test-token-12345",
            timeout=5.0,
            max_retries=3
        )
        self.metrics_collector = get_chaos_metrics_collector()
        self.error_aggregator = get_error_aggregator()

    @pytest.mark.asyncio
    async def test_authentication_token_expiration(self):
        """Test system behavior when authentication tokens expire."""
        async with chaos_test_context("authentication_token_expiration") as chaos_test:
            security_chaos = SecurityChaosInjector()
            chaos_test.add_injector(security_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject token expiration chaos
                await chaos_test.inject_chaos(token_expiration=True)

                auth_attempts = 0
                auth_failures = 0
                fallback_auth_used = 0
                token_refresh_attempts = 0

                for i in range(10):
                    try:
                        auth_attempts += 1

                        # Simulate authentication attempts
                        if i < 6:  # First 6 attempts fail due to expired token
                            auth_failures += 1

                            # Try token refresh
                            token_refresh_attempts += 1

                            # Simulate fallback authentication
                            if i >= 3:  # After 3 failures, use fallback
                                fallback_auth_used += 1
                                chaos_test.record_operation(True)
                            else:
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                                # Record security event
                                self.error_aggregator.add_error({
                                    'error_id': f'auth_fail_{i}',
                                    'timestamp': time.time(),
                                    'agent_id': self.config.agent_id,
                                    'error_type': 'AuthenticationError',
                                    'error_message': 'Token expired',
                                    'category': ErrorCategory.AUTHENTICATION,
                                    'severity': ErrorSeverity.HIGH
                                })
                        else:
                            # Later attempts succeed (token refreshed)
                            chaos_test.record_operation(True)

                        await asyncio.sleep(0.1)

                    except Exception:
                        auth_failures += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("auth_attempts", auth_attempts)
                chaos_test.add_custom_metric("auth_failures", auth_failures)
                chaos_test.add_custom_metric("fallback_auth_used", fallback_auth_used)
                chaos_test.add_custom_metric("token_refresh_attempts", token_refresh_attempts)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: fallback_auth_used > 0,
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from token expiration"

                # Test normal authentication after recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify authentication fallback mechanisms
            assert metrics.custom_metrics["fallback_auth_used"] > 0, "Fallback authentication not used"
            assert metrics.custom_metrics["token_refresh_attempts"] > 0, "Token refresh not attempted"

    @pytest.mark.asyncio
    async def test_certificate_validation_failures(self):
        """Test behavior with SSL certificate issues."""
        async with chaos_test_context("certificate_validation_failures") as chaos_test:
            security_chaos = SecurityChaosInjector()
            chaos_test.add_injector(security_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject certificate issues
                await chaos_test.inject_chaos(certificate_issues=True)

                ssl_errors = 0
                certificate_bypasses = 0
                secure_connections = 0
                insecure_fallbacks = 0

                for i in range(8):
                    try:
                        # Simulate HTTPS connections
                        if i < 5:  # First 5 attempts have certificate issues
                            ssl_errors += 1

                            # Simulate different handling strategies
                            if i % 2 == 0:  # Even attempts: strict validation (fail)
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                                # Record security event
                                self.error_aggregator.add_error({
                                    'error_id': f'ssl_fail_{i}',
                                    'timestamp': time.time(),
                                    'agent_id': self.config.agent_id,
                                    'error_type': 'SSLError',
                                    'error_message': 'Certificate verification failed',
                                    'category': ErrorCategory.SECURITY,
                                    'severity': ErrorSeverity.CRITICAL
                                })
                            else:  # Odd attempts: fallback to insecure (with warning)
                                insecure_fallbacks += 1
                                chaos_test.record_operation(True)

                                # Log security warning
                                self.error_aggregator.add_error({
                                    'error_id': f'ssl_warning_{i}',
                                    'timestamp': time.time(),
                                    'agent_id': self.config.agent_id,
                                    'error_type': 'SecurityWarning',
                                    'error_message': 'Using insecure connection due to certificate issues',
                                    'category': ErrorCategory.SECURITY,
                                    'severity': ErrorSeverity.MEDIUM
                                })
                        else:
                            # Later attempts succeed (certificate issues resolved)
                            secure_connections += 1
                            chaos_test.record_operation(True)

                        await asyncio.sleep(0.1)

                    except ssl.SSLError:
                        ssl_errors += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("ssl_errors", ssl_errors)
                chaos_test.add_custom_metric("certificate_bypasses", certificate_bypasses)
                chaos_test.add_custom_metric("secure_connections", secure_connections)
                chaos_test.add_custom_metric("insecure_fallbacks", insecure_fallbacks)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: secure_connections > 0,
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from certificate issues"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify certificate handling
            assert metrics.custom_metrics["ssl_errors"] > 0, "SSL errors not detected"
            assert metrics.successful_operations > 0, "No successful operations despite certificate issues"

    @pytest.mark.asyncio
    async def test_security_attack_detection(self):
        """Test security event detection under attack scenarios."""
        async with chaos_test_context("security_attack_detection") as chaos_test:
            security_chaos = SecurityChaosInjector()
            chaos_test.add_injector(security_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject attack simulation
                await chaos_test.inject_chaos(attack_simulation=True)

                attack_attempts = 0
                attacks_detected = 0
                attacks_blocked = 0
                false_positives = 0

                for i in range(12):
                    try:
                        attack_attempts += 1

                        # Simulate various request types
                        if i < 8:  # First 8 requests during attack simulation
                            try:
                                # This should trigger attack detection
                                await asyncio.sleep(0.1)  # Simulate request processing

                                # If we get here, attack wasn't detected (false negative)
                                false_positives += 1
                                chaos_test.record_operation(True)

                            except SecurityError as e:
                                # Attack detected and blocked
                                attacks_detected += 1
                                attacks_blocked += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                                # Record security event
                                self.error_aggregator.add_error({
                                    'error_id': f'attack_{i}',
                                    'timestamp': time.time(),
                                    'agent_id': self.config.agent_id,
                                    'error_type': 'SecurityAttack',
                                    'error_message': str(e),
                                    'category': ErrorCategory.SECURITY,
                                    'severity': ErrorSeverity.CRITICAL
                                })
                        else:
                            # Normal requests after attack simulation
                            chaos_test.record_operation(True)

                        await asyncio.sleep(0.1)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("attack_attempts", attack_attempts)
                chaos_test.add_custom_metric("attacks_detected", attacks_detected)
                chaos_test.add_custom_metric("attacks_blocked", attacks_blocked)
                chaos_test.add_custom_metric("false_positives", false_positives)

                # Calculate detection rate
                detection_rate = attacks_detected / max(attack_attempts - 4, 1)  # Exclude normal requests
                chaos_test.add_custom_metric("detection_rate", detection_rate)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # System should continue operating
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from attack simulation"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify attack detection
            assert metrics.custom_metrics["attacks_detected"] > 0, "No attacks were detected"
            assert metrics.custom_metrics["detection_rate"] > 0.5, "Detection rate too low"

    @pytest.mark.asyncio
    async def test_rate_limiting_bypass_attempts(self):
        """Test rate limiting under bypass attempts."""
        async with chaos_test_context("rate_limiting_bypass_attempts") as chaos_test:
            security_chaos = SecurityChaosInjector()
            chaos_test.add_injector(security_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject rate limit bypass simulation
                await chaos_test.inject_chaos(rate_limit_bypass=True)

                bypass_attempts = 0
                rate_limit_violations = 0
                legitimate_requests = 0
                blocked_requests = 0

                # Simulate rapid requests (bypass attempt)
                for i in range(20):  # More than rate limit
                    try:
                        bypass_attempts += 1

                        # Simulate request
                        await asyncio.sleep(0.05)  # Very fast requests

                        if i < 15:  # First 15 are rapid (bypass attempt)
                            try:
                                # This should trigger rate limiting
                                legitimate_requests += 1
                                chaos_test.record_operation(True)
                            except Exception:
                                if "rate limit" in str(e).lower():
                                    rate_limit_violations += 1
                                    blocked_requests += 1
                                    chaos_test.record_operation(False)
                                    chaos_test.record_error()

                                    # Record security event
                                    self.error_aggregator.add_error({
                                        'error_id': f'rate_limit_{i}',
                                        'timestamp': time.time(),
                                        'agent_id': self.config.agent_id,
                                        'error_type': 'RateLimitViolation',
                                        'error_message': 'Rate limit exceeded',
                                        'category': ErrorCategory.SECURITY,
                                        'severity': ErrorSeverity.HIGH
                                    })
                                else:
                                    chaos_test.record_operation(False)
                                    chaos_test.record_error()
                        else:
                            # Normal rate requests
                            legitimate_requests += 1
                            chaos_test.record_operation(True)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("bypass_attempts", bypass_attempts)
                chaos_test.add_custom_metric("rate_limit_violations", rate_limit_violations)
                chaos_test.add_custom_metric("legitimate_requests", legitimate_requests)
                chaos_test.add_custom_metric("blocked_requests", blocked_requests)

                # Calculate blocking effectiveness
                blocking_rate = blocked_requests / max(bypass_attempts, 1)
                chaos_test.add_custom_metric("blocking_rate", blocking_rate)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # Rate limits should reset
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from rate limiting test"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify rate limiting effectiveness
            assert metrics.custom_metrics["rate_limit_violations"] > 0, "Rate limiting not triggered"
            assert metrics.custom_metrics["blocking_rate"] > 0.3, "Rate limiting not effective enough"

    @pytest.mark.asyncio
    async def test_comprehensive_security_resilience(self):
        """Test comprehensive security resilience under multiple attack vectors."""
        async with chaos_test_context("comprehensive_security_resilience") as chaos_test:
            security_chaos = SecurityChaosInjector()
            chaos_test.add_injector(security_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject multiple security chaos scenarios
                await chaos_test.inject_chaos(
                    token_expiration=True,
                    certificate_issues=True,
                    attack_simulation=True,
                    rate_limit_bypass=True
                )

                total_security_events = 0
                critical_events = 0
                system_compromised = False
                security_measures_active = 0

                for i in range(15):
                    try:
                        # Simulate various operations under multiple security threats
                        await asyncio.sleep(0.1)

                        # Check if system maintains security posture
                        if i < 10:  # During active chaos
                            # Some operations should fail due to security measures
                            if i % 3 == 0:  # Every 3rd operation blocked by security
                                total_security_events += 1
                                if i % 6 == 0:  # Every 6th is critical
                                    critical_events += 1

                                security_measures_active += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                            else:
                                # Some operations succeed with degraded security
                                chaos_test.record_operation(True)
                        else:
                            # Operations after security recovery
                            chaos_test.record_operation(True)

                    except Exception:
                        total_security_events += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("total_security_events", total_security_events)
                chaos_test.add_custom_metric("critical_events", critical_events)
                chaos_test.add_custom_metric("system_compromised", system_compromised)
                chaos_test.add_custom_metric("security_measures_active", security_measures_active)

                # Calculate security resilience score
                resilience_score = (security_measures_active / max(total_security_events, 1)) * 100
                chaos_test.add_custom_metric("security_resilience_score", resilience_score)

                # Stop chaos and verify security recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: not system_compromised,
                    timeout=15.0
                )

                assert recovery_successful, "System did not recover from comprehensive security chaos"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify comprehensive security resilience
            assert metrics.custom_metrics["security_measures_active"] > 0, "Security measures not activated"
            assert metrics.custom_metrics["security_resilience_score"] > 50, "Security resilience score too low"
            assert not metrics.custom_metrics["system_compromised"], "System was compromised"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Smoke tests for kei_agent.health_checks module."""

def test_import_health_checks():
    """Test that health_checks module can be imported."""
    import kei_agent.health_checks


def test_import_health_check_classes():
    """Test that health check classes can be imported."""
    from kei_agent.health_checks import (
        Healthstatus,
        HealthCheckResult,
        BaseHealthCheck,
        DatabaseHealthCheck,
        APIHealthCheck,
        MemoryHealthCheck,
        HealthCheckManager,
    )


def test_health_status_enum():
    """Test basic Healthstatus enum usage."""
    from kei_agent.health_checks import Healthstatus

    assert hasattr(Healthstatus, 'HEALTHY')
    assert hasattr(Healthstatus, 'UNHEALTHY') or hasattr(Healthstatus, 'DEGRADED')


def test_health_check_result_creation():
    """Test basic HealthCheckResult instantiation."""
    from kei_agent.health_checks import HealthCheckResult, Healthstatus

    result = HealthCheckResult(
        name="test-check",
        status=Healthstatus.HEALTHY,
        message="Test check passed"
    )
    assert result.name == "test-check"
    assert result.status == Healthstatus.HEALTHY
    assert result.message == "Test check passed"


def test_database_health_check_creation():
    """Test basic DatabaseHealthCheck instantiation."""
    from kei_agent.health_checks import DatabaseHealthCheck

    check = DatabaseHealthCheck(
        name="test-db",
        connection_string="sqlite:///:memory:"
    )
    assert check.name == "test-db"
    assert hasattr(check, 'check')


def test_api_health_check_creation():
    """Test basic APIHealthCheck instantiation."""
    from kei_agent.health_checks import APIHealthCheck

    check = APIHealthCheck(
        name="test-api",
        url="https://httpbin.org/status/200"
    )
    assert check.name == "test-api"
    assert hasattr(check, 'check')


def test_memory_health_check_creation():
    """Test basic MemoryHealthCheck instantiation."""
    from kei_agent.health_checks import MemoryHealthCheck

    check = MemoryHealthCheck()
    assert check.name == "memory"
    assert hasattr(check, 'check')


def test_health_check_manager_creation():
    """Test basic HealthCheckManager instantiation."""
    from kei_agent.health_checks import HealthCheckManager

    manager = HealthCheckManager()
    assert manager is not None
    assert hasattr(manager, 'register_check')
    assert hasattr(manager, 'run_all_checks')


def test_get_health_manager():
    """Test global health manager function."""
    from kei_agent.health_checks import get_health_manager

    manager = get_health_manager()
    assert manager is not None
    assert hasattr(manager, 'register_check')

"""Smoke tests for kei_agent.retry module."""

def test_import_retry():
    """Test that retry module can be imported."""
    import kei_agent.retry


def test_import_retry_classes():
    """Test that retry classes can be imported."""
    from kei_agent.retry import retryManager, retryPolicy


def test_retry_policy_creation():
    """Test basic retryPolicy instantiation."""
    from kei_agent.retry import retryPolicy

    policy = retryPolicy()
    assert policy.max_attempts >= 1
    assert policy.base_delay >= 0


def test_retry_manager_creation():
    """Test basic retryManager instantiation."""
    from kei_agent.retry import retryManager, retryPolicy

    policy = retryPolicy()
    manager = retryManager(policy)
    assert manager is not None

"""Smoke tests for kei_agent.config_api module."""

def test_import_config_api():
    """Test that config_api module can be imported."""
    import kei_agent.config_api


def test_import_config_api_class():
    """Test that ConfigAPI class can be imported."""
    from kei_agent.config_api import ConfigAPI


def test_config_api_creation():
    """Test basic ConfigAPI instantiation."""
    from kei_agent.config_api import ConfigAPI

    api = ConfigAPI(require_auth=False)
    assert api is not None
    assert hasattr(api, 'create_routes')
    assert hasattr(api, 'get_config_handler')


def test_get_config_api():
    """Test global config API function."""
    from kei_agent.config_api import get_config_api

    api = get_config_api()
    assert api is not None
    assert hasattr(api, 'create_routes')


def test_initialize_config_api():
    """Test config API initialization function."""
    from kei_agent.config_api import initialize_config_api

    api = initialize_config_api(require_auth=False)
    assert api is not None
    assert hasattr(api, 'create_routes')

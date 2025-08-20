"""Smoke tests for kei_agent.protocol_selector module."""

def test_import_protocol_selector():
    """Test that protocol_selector module can be imported."""
    import kei_agent.protocol_selector


def test_import_protocol_selector_classes():
    """Test that protocol selector classes can be imported."""
    from kei_agent.protocol_selector import ProtocolSelector
    from kei_agent.protocol_types import ProtocolConfig, Protocoltypee


def test_protocol_config_creation():
    """Test basic ProtocolConfig instantiation."""
    from kei_agent.protocol_types import ProtocolConfig, Protocoltypee

    config = ProtocolConfig(
        rpc_enabled=True,
        stream_enabled=True,
        bus_enabled=False
    )
    enabled = config.get_enabled_protocols()
    assert Protocoltypee.RPC in enabled
    assert Protocoltypee.STREAM in enabled


def test_protocol_selector_creation():
    """Test basic ProtocolSelector instantiation."""
    from kei_agent.protocol_selector import ProtocolSelector
    from kei_agent.protocol_types import ProtocolConfig, Protocoltypee

    config = ProtocolConfig(
        rpc_enabled=True,
        stream_enabled=True,
        bus_enabled=False
    )

    selector = ProtocolSelector(config)
    assert selector is not None
    assert selector.config == config
    assert hasattr(selector, 'select_protocol')
    assert hasattr(selector, '_operation_patterns')


def test_protocol_selector_methods():
    """Test that ProtocolSelector methods are callable."""
    from kei_agent.protocol_selector import ProtocolSelector
    from kei_agent.protocol_types import ProtocolConfig, Protocoltypee

    config = ProtocolConfig(
        rpc_enabled=True,
        stream_enabled=True,
        bus_enabled=False
    )

    selector = ProtocolSelector(config)

    # Test protocol selection
    selected = selector.select_protocol("test_operation")
    assert selected in [Protocoltypee.RPC, Protocoltypee.STREAM, Protocoltypee.BUS]

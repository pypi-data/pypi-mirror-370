"""Smoke tests for kei_agent.dashboard_generators module."""

def test_import_dashboard_generators():
    """Test that dashboard_generators module can be imported."""
    import kei_agent.dashboard_generators


def test_import_dashboard_functions():
    """Test that dashboard generator functions can be imported."""
    from kei_agent.dashboard_generators import (
        generate_security_dashboard_html,
        generate_business_dashboard_html,
    )


def test_generate_security_dashboard():
    """Test basic security dashboard generation."""
    from kei_agent.dashboard_generators import generate_security_dashboard_html

    html = generate_security_dashboard_html()
    assert isinstance(html, str)
    assert len(html) > 0
    assert "Security Dashboard" in html
    assert "<!DOCTYPE html>" in html


def test_generate_business_dashboard():
    """Test basic business dashboard generation."""
    from kei_agent.dashboard_generators import generate_business_dashboard_html

    html = generate_business_dashboard_html()
    assert isinstance(html, str)
    assert len(html) > 0
    assert "Business Metrics" in html
    assert "<!DOCTYPE html>" in html

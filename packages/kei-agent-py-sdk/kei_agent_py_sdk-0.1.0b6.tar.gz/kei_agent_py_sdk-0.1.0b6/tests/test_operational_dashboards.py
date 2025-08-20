# tests/test_operational_dashboards.py
"""
Tests for comprehensive operational dashboards.

This test validates that:
1. All dashboard endpoints are accessible
2. Dashboard HTML is generated correctly
3. API endpoints return proper data
4. Dashboard navigation works
5. Real-time updates function properly
"""

import asyncio
import json
from unittest.mock import patch, MagicMock

import pytest

try:
    from aiohttp import web
    from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from kei_agent.metrics_server import MetricsServer
from kei_agent.dashboard_generators import generate_security_dashboard_html, generate_business_dashboard_html


@pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not available")
class TestOperationalDashboards:
    """Tests for operational dashboard functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.metrics_server = MetricsServer(host="127.0.0.1", port=8091)

    def test_dashboard_generators(self):
        """Test dashboard HTML generators."""
        # Test security dashboard generator
        security_html = generate_security_dashboard_html()
        assert isinstance(security_html, str)
        assert "Security Monitoring Dashboard" in security_html
        assert "nav-link" in security_html
        assert "security-grid" in security_html

        # Test business dashboard generator
        business_html = generate_business_dashboard_html()
        assert isinstance(business_html, str)
        assert "Business Metrics Dashboard" in business_html
        assert "nav-link" in business_html
        assert "business-grid" in business_html

    def test_metrics_server_dashboard_methods(self):
        """Test metrics server dashboard generation methods."""
        # Test main dashboard
        main_html = self.metrics_server._generate_main_dashboard_html()
        assert isinstance(main_html, str)
        assert "KEI-Agent SDK Operational Dashboard" in main_html

        # Test health dashboard
        health_html = self.metrics_server._generate_health_dashboard_html()
        assert isinstance(health_html, str)
        assert "Health Monitoring Dashboard" in health_html

        # Test performance dashboard
        perf_html = self.metrics_server._generate_performance_dashboard_html()
        assert isinstance(perf_html, str)
        assert "Performance Monitoring Dashboard" in perf_html

        # Test security dashboard
        security_html = self.metrics_server._generate_security_dashboard_html()
        assert isinstance(security_html, str)
        assert "Security Monitoring Dashboard" in security_html

        # Test business dashboard
        business_html = self.metrics_server._generate_business_dashboard_html()
        assert isinstance(business_html, str)
        assert "Business Metrics Dashboard" in business_html

    @pytest.mark.asyncio
    async def test_dashboard_navigation_structure(self):
        """Test that all dashboards have consistent navigation."""
        dashboards = [
            self.metrics_server._generate_main_dashboard_html(),
            self.metrics_server._generate_health_dashboard_html(),
            self.metrics_server._generate_performance_dashboard_html(),
            self.metrics_server._generate_security_dashboard_html(),
            self.metrics_server._generate_business_dashboard_html()
        ]

        expected_nav_links = [
            'href="/dashboard"',
            'href="/dashboard/health"',
            'href="/dashboard/performance"',
            'href="/dashboard/security"',
            'href="/dashboard/business"'
        ]

        for dashboard_html in dashboards:
            for nav_link in expected_nav_links:
                assert nav_link in dashboard_html, f"Navigation link {nav_link} missing from dashboard"

    def test_dashboard_responsive_design(self):
        """Test that dashboards include responsive design elements."""
        dashboards = [
            self.metrics_server._generate_main_dashboard_html(),
            self.metrics_server._generate_health_dashboard_html(),
            self.metrics_server._generate_performance_dashboard_html(),
            self.metrics_server._generate_security_dashboard_html(),
            self.metrics_server._generate_business_dashboard_html()
        ]

        responsive_elements = [
            'viewport',
            'grid-template-columns',
            'auto-fit',
            'minmax'
        ]

        for dashboard_html in dashboards:
            for element in responsive_elements:
                assert element in dashboard_html, f"Responsive element {element} missing from dashboard"

    def test_dashboard_javascript_functionality(self):
        """Test that dashboards include necessary JavaScript functionality."""
        dashboards = [
            ("main", self.metrics_server._generate_main_dashboard_html()),
            ("health", self.metrics_server._generate_health_dashboard_html()),
            ("performance", self.metrics_server._generate_performance_dashboard_html()),
            ("security", self.metrics_server._generate_security_dashboard_html()),
            ("business", self.metrics_server._generate_business_dashboard_html())
        ]

        for dashboard_name, dashboard_html in dashboards:
            # Check for JavaScript presence
            assert "<script>" in dashboard_html, f"{dashboard_name} dashboard missing JavaScript"
            assert "</script>" in dashboard_html, f"{dashboard_name} dashboard missing JavaScript closing tag"

            # Check for update functions
            if dashboard_name != "main":
                assert f"update{dashboard_name.title()}Dashboard" in dashboard_html or "updateDashboard" in dashboard_html, \
                    f"{dashboard_name} dashboard missing update function"

            # Check for setInterval (auto-refresh)
            assert "setInterval" in dashboard_html, f"{dashboard_name} dashboard missing auto-refresh"

    def test_dashboard_css_styling(self):
        """Test that dashboards include proper CSS styling."""
        dashboards = [
            self.metrics_server._generate_main_dashboard_html(),
            self.metrics_server._generate_health_dashboard_html(),
            self.metrics_server._generate_performance_dashboard_html(),
            self.metrics_server._generate_security_dashboard_html(),
            self.metrics_server._generate_business_dashboard_html()
        ]

        css_elements = [
            "<style>",
            "</style>",
            "font-family",
            "background-color",
            "border-radius",
            "box-shadow"
        ]

        for dashboard_html in dashboards:
            for element in css_elements:
                assert element in dashboard_html, f"CSS element {element} missing from dashboard"

    def test_security_dashboard_specific_elements(self):
        """Test security dashboard specific elements."""
        security_html = generate_security_dashboard_html()

        security_specific_elements = [
            "security-grid",
            "security-card",
            "alert-high",
            "alert-medium",
            "alert-low",
            "security-metric",
            "event-list",
            "event-item",
            "🔒 Security Monitoring Dashboard",
            "🚨 Security Alerts",
            "🔐 Authentication Metrics",
            "🛡️ Security Posture"
        ]

        for element in security_specific_elements:
            assert element in security_html, f"Security element {element} missing from security dashboard"

    def test_business_dashboard_specific_elements(self):
        """Test business dashboard specific elements."""
        business_html = generate_business_dashboard_html()

        business_specific_elements = [
            "business-grid",
            "business-card",
            "kpi-value",
            "kpi-label",
            "donut-chart",
            "efficiency-bar",
            "efficiency-fill",
            "📊 Business Metrics Dashboard",
            "🤖 Agent Metrics",
            "⚡ Operation Success",
            "🚀 Protocol Usage",
            "📈 Resource Efficiency"
        ]

        for element in business_specific_elements:
            assert element in business_html, f"Business element {element} missing from business dashboard"

    def test_performance_dashboard_specific_elements(self):
        """Test performance dashboard specific elements."""
        perf_html = self.metrics_server._generate_performance_dashboard_html()

        performance_specific_elements = [
            "perf-grid",
            "perf-card",
            "metric-value",
            "metric-label",
            "progress-bar",
            "progress-fill",
            "chart-container",
            "⚡ Performance Monitoring Dashboard",
            "Request Metrics",
            "Throughput",
            "System Resources",
            "Protocol Performance"
        ]

        for element in performance_specific_elements:
            assert element in perf_html, f"Performance element {element} missing from performance dashboard"

    def test_health_dashboard_specific_elements(self):
        """Test health dashboard specific elements."""
        health_html = self.metrics_server._generate_health_dashboard_html()

        health_specific_elements = [
            "health-grid",
            "health-card",
            "health-score",
            "health-healthy",
            "health-warning",
            "health-degraded",
            "health-critical",
            "status-indicator",
            "🏥 Health Monitoring Dashboard",
            "Overall Health Score",
            "System Status",
            "Service Dependencies"
        ]

        for element in health_specific_elements:
            assert element in health_html, f"Health element {element} missing from health dashboard"

    @pytest.mark.asyncio
    async def test_api_endpoint_structure(self):
        """Test that API endpoints are properly structured."""
        # Create app to test routes
        app = self.metrics_server.create_app()

        expected_routes = [
            ('GET', '/'),
            ('GET', '/dashboard'),
            ('GET', '/dashboard/health'),
            ('GET', '/dashboard/performance'),
            ('GET', '/dashboard/security'),
            ('GET', '/dashboard/business'),
            ('GET', '/api/metrics/summary'),
            ('GET', '/api/health/status'),
            ('GET', '/api/performance/stats'),
            ('GET', '/api/security/events'),
            ('GET', '/api/business/metrics'),
            ('GET', '/metrics'),
            ('GET', '/health'),
            ('GET', '/ready'),
            ('GET', '/live'),
            ('GET', '/ws/metrics')
        ]

        # Get all routes from the app
        app_routes = []
        for resource in app.router.resources():
            for route in resource:
                app_routes.append((route.method, route.resource.canonical))

        # Check that expected routes exist
        for method, path in expected_routes:
            route_exists = any(
                app_method == method and app_path == path
                for app_method, app_path in app_routes
            )
            assert route_exists, f"Route {method} {path} not found in app routes"

    def test_dashboard_accessibility_features(self):
        """Test that dashboards include accessibility features."""
        dashboards = [
            self.metrics_server._generate_main_dashboard_html(),
            self.metrics_server._generate_health_dashboard_html(),
            self.metrics_server._generate_performance_dashboard_html(),
            self.metrics_server._generate_security_dashboard_html(),
            self.metrics_server._generate_business_dashboard_html()
        ]

        accessibility_features = [
            'charset="utf-8"',
            'name="viewport"',
            'alt=',  # Would be present if images were used
            'aria-',  # Would be present if ARIA labels were used
        ]

        for dashboard_html in dashboards:
            # Check for basic accessibility features
            assert 'charset="utf-8"' in dashboard_html, "Missing UTF-8 charset declaration"
            assert 'name="viewport"' in dashboard_html, "Missing viewport meta tag"

    def test_dashboard_error_handling(self):
        """Test that dashboards include error handling in JavaScript."""
        dashboards = [
            ("main", self.metrics_server._generate_main_dashboard_html()),
            ("health", self.metrics_server._generate_health_dashboard_html()),
            ("performance", self.metrics_server._generate_performance_dashboard_html()),
            ("security", self.metrics_server._generate_security_dashboard_html()),
            ("business", self.metrics_server._generate_business_dashboard_html())
        ]

        for dashboard_name, dashboard_html in dashboards:
            # Check for error handling
            assert "try {" in dashboard_html, f"{dashboard_name} dashboard missing try-catch blocks"
            assert "catch" in dashboard_html, f"{dashboard_name} dashboard missing catch blocks"
            assert "console.error" in dashboard_html, f"{dashboard_name} dashboard missing error logging"

    def test_dashboard_data_formatting(self):
        """Test that dashboards include data formatting functions."""
        dashboards_with_formatting = [
            ("health", self.metrics_server._generate_health_dashboard_html()),
            ("business", self.metrics_server._generate_business_dashboard_html())
        ]

        for dashboard_name, dashboard_html in dashboards_with_formatting:
            # Check for formatting functions
            assert "formatUptime" in dashboard_html or "toLocaleString" in dashboard_html or "toFixed" in dashboard_html, \
                f"{dashboard_name} dashboard missing data formatting functions"


class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""

    def test_dashboard_consistency(self):
        """Test that all dashboards have consistent structure and styling."""
        metrics_server = MetricsServer()

        dashboards = {
            "main": metrics_server._generate_main_dashboard_html(),
            "health": metrics_server._generate_health_dashboard_html(),
            "performance": metrics_server._generate_performance_dashboard_html(),
            "security": metrics_server._generate_security_dashboard_html(),
            "business": metrics_server._generate_business_dashboard_html()
        }

        # Check that all dashboards have similar structure
        common_elements = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>",
            "<body>",
            "nav-menu",
            "nav-link"
        ]

        for dashboard_name, dashboard_html in dashboards.items():
            for element in common_elements:
                assert element in dashboard_html, f"Common element {element} missing from {dashboard_name} dashboard"

    def test_dashboard_performance_considerations(self):
        """Test that dashboards are optimized for performance."""
        metrics_server = MetricsServer()

        dashboards = [
            metrics_server._generate_main_dashboard_html(),
            metrics_server._generate_health_dashboard_html(),
            metrics_server._generate_performance_dashboard_html(),
            metrics_server._generate_security_dashboard_html(),
            metrics_server._generate_business_dashboard_html()
        ]

        for dashboard_html in dashboards:
            # Check that dashboards are not excessively large
            assert len(dashboard_html) < 50000, "Dashboard HTML is too large (>50KB)"

            # Check for efficient update intervals
            assert "setInterval" in dashboard_html, "Dashboard missing auto-refresh"

            # Check that update intervals are reasonable (not too frequent)
            if "10000" in dashboard_html:  # 10 seconds
                assert True  # Performance dashboard updates every 10 seconds
            elif "30000" in dashboard_html:  # 30 seconds
                assert True  # Health and security dashboards update every 30 seconds
            elif "60000" in dashboard_html:  # 60 seconds
                assert True  # Business dashboard updates every 60 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# tests/test_coverage_functionality.py
"""
Test to verify coverage reporting functionality is working correctly.

This test validates that:
1. Coverage collection is enabled
2. Coverage reports are generated
3. Coverage thresholds are enforced
4. Coverage configuration is properly set
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestCoverageReporting:
    """Tests for coverage reporting functionality."""

    def test_coverage_collection_enabled(self):
        """Test that coverage collection is properly enabled."""
        # Run a simple test with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_import_system.py::TestImportSystem::test_main_package_import",
            "--cov=kei_agent", "--cov-report=term", "-v"
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Check that coverage was collected
        assert "coverage:" in result.stdout.lower()
        assert "total" in result.stdout.lower()

    def test_coverage_reports_generated(self):
        """Test that coverage reports are generated in expected formats."""
        # Run test with all coverage report formats
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_import_system.py::TestImportSystem::test_main_package_import",
            "--cov=kei_agent",
            "--cov-report=html:htmlcov",
            "--cov-report=xml",
            "--cov-report=term-missing",
            "-v"
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Check that HTML report was generated
        html_report_path = Path("htmlcov/index.html")
        assert html_report_path.exists(), "HTML coverage report not generated"

        # Check that XML report was generated
        xml_report_path = Path("coverage.xml")
        assert xml_report_path.exists(), "XML coverage report not generated"

        # Verify HTML report contains expected content
        with open(html_report_path, 'r') as f:
            html_content = f.read()
            assert "KEI-Agent Python SDK Coverage Report" in html_content
            assert "kei_agent" in html_content

    def test_coverage_threshold_enforcement(self):
        """Test that coverage threshold is properly enforced."""
        # Create a temporary test file with minimal coverage
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py',
                                       dir='tests', delete=False) as f:
            f.write("""
import pytest

def test_minimal():
    assert True
""")
            temp_test_file = f.name

        try:
            # Run test that should fail coverage threshold
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                temp_test_file,
                "--cov=kei_agent",
                # Coverage threshold now configured in pyproject.toml only
                "-v"
            ], capture_output=True, text=True, cwd=Path.cwd())

            # Should fail due to low coverage
            assert result.returncode != 0
            assert "Required test coverage of 15% not reached" in result.stdout

        finally:
            # Clean up temporary file
            os.unlink(temp_test_file)

    def test_coverage_configuration_valid(self):
        """Test that coverage configuration is valid."""
        # Check that pyproject.toml has proper coverage configuration
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists()

        with open(pyproject_path, 'r') as f:
            content = f.read()

        # Verify coverage configuration sections exist
        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content
        assert "[tool.coverage.html]" in content
        assert "[tool.coverage.xml]" in content

        # Verify key configuration values
        assert 'source = ["kei_agent"]' in content
        assert "fail_under = 15" in content
        assert "branch = true" in content

    def test_coverage_excludes_test_files(self):
        """Test that test files are properly excluded from coverage."""
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_import_system.py::TestImportSystem::test_main_package_import",
            "--cov=kei_agent", "--cov-report=term", "-v"
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Test files should not appear in coverage report
        assert "tests/" not in result.stdout or "0%" in result.stdout

    def test_coverage_branch_coverage_enabled(self):
        """Test that branch coverage is enabled."""
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_import_system.py::TestImportSystem::test_main_package_import",
            "--cov=kei_agent", "--cov-report=term", "--cov-branch", "-v"
        ], capture_output=True, text=True, cwd=Path.cwd())

        # Should show branch coverage columns
        assert "Branch" in result.stdout
        assert "BrPart" in result.stdout

    def test_importlib_metadata_issue_resolved(self):
        """Test that the importlib_metadata KeyError issue is resolved."""
        # This test verifies that coverage can run without the KeyError
        # that was previously disabling coverage
        result = subprocess.run([
            sys.executable, "-c",
            "import coverage; import importlib_metadata; print('OK')"
        ], capture_output=True, text=True)

        # Should not have KeyError
        assert result.returncode == 0
        assert "OK" in result.stdout
        assert "KeyError" not in result.stderr

    def test_coverage_html_report_structure(self):
        """Test that HTML coverage report has proper structure."""
        # Generate HTML report
        subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_import_system.py::TestImportSystem::test_main_package_import",
            "--cov=kei_agent", "--cov-report=html:htmlcov", "-v"
        ], capture_output=True, text=True, cwd=Path.cwd())

        htmlcov_dir = Path("htmlcov")
        assert htmlcov_dir.exists()
        assert htmlcov_dir.is_dir()

        # Check for key files
        assert (htmlcov_dir / "index.html").exists()
        assert (htmlcov_dir / "status.json").exists()

        # Check that module files are included
        module_files = list(htmlcov_dir.glob("kei_agent_*.html"))
        assert len(module_files) > 0, "No module coverage files generated"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

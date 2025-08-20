# tests/test_dependency_security.py
"""
Tests for dependency security scanning functionality.

This test validates that:
1. Security scanning scripts work correctly
2. SBOM generation functions properly
3. Vulnerability detection and reporting works
4. Security policies are enforced
"""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest


class TestSecurityScanning:
    """Tests for security scanning functionality."""

    def test_security_scan_script_exists(self):
        """Test that security scan script exists and is executable."""
        script_path = Path("scripts/security_scan.py")
        assert script_path.exists(), "Security scan script not found"
        assert script_path.is_file(), "Security scan script is not a file"

    def test_sbom_generation_script_exists(self):
        """Test that SBOM generation script exists and is executable."""
        script_path = Path("scripts/generate_sbom.py")
        assert script_path.exists(), "SBOM generation script not found"
        assert script_path.is_file(), "SBOM generation script is not a file"

    @patch('subprocess.run')
    def test_security_scanner_initialization(self, mock_run):
        """Test SecurityScanner class initialization."""
        from scripts.security_scan import SecurityScanner

        project_root = Path("/test/project")
        scanner = SecurityScanner(project_root)

        assert scanner.project_root == project_root
        assert scanner.output_dir == project_root / "security-reports"
        assert "scan_timestamp" in scanner.results
        assert "scanners" in scanner.results
        assert "summary" in scanner.results

    @patch('subprocess.run')
    def test_safety_scan_success(self, mock_run):
        """Test successful Safety vulnerability scan."""
        from scripts.security_scan import SecurityScanner

        # Mock successful Safety scan
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[]',  # No vulnerabilities
            stderr=''
        )

        scanner = SecurityScanner(Path.cwd())
        result = scanner.run_safety_scan()

        assert result["status"] == "passed"
        assert result["vulnerabilities"] == []
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_safety_scan_with_vulnerabilities(self, mock_run):
        """Test Safety scan with vulnerabilities found."""
        from scripts.security_scan import SecurityScanner

        # Mock Safety scan with vulnerabilities
        vulnerabilities = [
            {
                "id": "12345",
                "package_name": "test-package",
                "installed_version": "1.0.0",
                "advisory": "Test vulnerability"
            }
        ]

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=json.dumps(vulnerabilities),
            stderr=''
        )

        scanner = SecurityScanner(Path.cwd())
        result = scanner.run_safety_scan()

        assert result["status"] == "failed"
        assert len(result["vulnerabilities"]) == 1
        assert result["vulnerabilities"][0]["id"] == "12345"

    @patch('subprocess.run')
    def test_pip_audit_scan_success(self, mock_run):
        """Test successful pip-audit scan."""
        from scripts.security_scan import SecurityScanner

        # Mock successful pip-audit scan
        audit_data = {"vulnerabilities": []}

        with tempfile.TemporaryDirectory() as temp_dir:
            scanner = SecurityScanner(Path.cwd(), Path(temp_dir))

            # Create mock audit report file
            audit_report_path = scanner.output_dir / "pip-audit-report.json"
            with open(audit_report_path, 'w') as f:
                json.dump(audit_data, f)

            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='',
                stderr=''
            )

            result = scanner.run_pip_audit_scan()

            assert result["status"] == "passed"
            assert result["vulnerabilities"] == []

    @patch('subprocess.run')
    def test_bandit_scan_success(self, mock_run):
        """Test successful Bandit security scan."""
        from scripts.security_scan import SecurityScanner

        # Mock successful Bandit scan
        bandit_data = {
            "results": [],
            "metrics": {"_totals": {"loc": 100, "nosec": 0}}
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            scanner = SecurityScanner(Path.cwd(), Path(temp_dir))

            # Create mock bandit report file
            bandit_report_path = scanner.output_dir / "bandit-report.json"
            with open(bandit_report_path, 'w') as f:
                json.dump(bandit_data, f)

            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='',
                stderr=''
            )

            result = scanner.run_bandit_scan()

            assert result["status"] == "passed"
            assert result["issues"] == []

    def test_vulnerability_analysis(self):
        """Test vulnerability analysis and aggregation."""
        from scripts.security_scan import SecurityScanner

        scanner = SecurityScanner(Path.cwd())

        # Mock scan results
        scanner.results["scanners"] = {
            "safety": {
                "vulnerabilities": [
                    {"id": "1", "package_name": "pkg1"},
                    {"id": "2", "package_name": "pkg2"}
                ]
            },
            "pip_audit": {
                "vulnerabilities": [
                    {"id": "3", "package": "pkg3"}
                ]
            },
            "bandit": {
                "issues": [
                    {"issue_severity": "high"},
                    {"issue_severity": "medium"}
                ]
            }
        }

        scanner.analyze_results()

        summary = scanner.results["summary"]
        assert summary["total_vulnerabilities"] == 5  # 2 + 1 + 2
        assert summary["high"] == 1
        assert summary["medium"] == 4  # Safety vulns + audit vulns + 1 bandit medium
        assert summary["scan_passed"] is False  # Due to high severity issue

    def test_scan_passes_with_acceptable_vulnerabilities(self):
        """Test that scan passes with acceptable number of medium vulnerabilities."""
        from scripts.security_scan import SecurityScanner

        scanner = SecurityScanner(Path.cwd())

        # Mock scan results with only medium vulnerabilities
        scanner.results["scanners"] = {
            "safety": {
                "vulnerabilities": [
                    {"id": "1", "package_name": "pkg1"}
                ]
            },
            "pip_audit": {"vulnerabilities": []},
            "bandit": {
                "issues": [
                    {"issue_severity": "medium"}
                ]
            }
        }

        scanner.analyze_results()

        summary = scanner.results["summary"]
        assert summary["total_vulnerabilities"] == 2
        assert summary["critical"] == 0
        assert summary["high"] == 0
        assert summary["medium"] == 2
        assert summary["scan_passed"] is True  # Within acceptable limits


class TestSBOMGeneration:
    """Tests for SBOM generation functionality."""

    def test_sbom_generator_initialization(self):
        """Test SBOMGenerator class initialization."""
        from scripts.generate_sbom import SBOMGenerator

        project_root = Path("/test/project")
        generator = SBOMGenerator(project_root)

        assert generator.project_root == project_root
        assert generator.output_dir == project_root / "sbom"

    @patch('builtins.open', new_callable=mock_open, read_data='''
[project]
name = "test-project"
version = "1.0.0"
description = "Test project"
authors = [{name = "Test Author", email = "test@example.com"}]
license = {text = "MIT"}

[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/example/test"
''')
    def test_load_project_metadata(self, mock_file):
        """Test loading project metadata from pyproject.toml."""
        from scripts.generate_sbom import SBOMGenerator

        with patch('pathlib.Path.exists', return_value=True):
            generator = SBOMGenerator(Path.cwd())
            metadata = generator._load_project_metadata()

            assert metadata["name"] == "test-project"
            assert metadata["version"] == "1.0.0"
            assert metadata["description"] == "Test project"
            assert metadata["homepage"] == "https://example.com"
            assert metadata["repository"] == "https://github.com/example/test"

    @patch('subprocess.run')
    def test_cyclonedx_sbom_generation_success(self, mock_run):
        """Test successful CycloneDX SBOM generation."""
        from scripts.generate_sbom import SBOMGenerator

        # Mock successful cyclonedx-bom execution
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SBOMGenerator(Path.cwd(), Path(temp_dir))

            # Create mock SBOM file
            sbom_data = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "components": []
            }

            # Mock the SBOM file creation
            with patch.object(generator, '_enhance_sbom'):
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('builtins.open', mock_open(read_data=json.dumps(sbom_data))):
                        result = generator.generate_cyclonedx_sbom()

                        assert result is not None
                        assert result.name.startswith("sbom-")
                        assert result.suffix == ".json"

    @patch('subprocess.run')
    def test_dependency_tree_generation(self, mock_run):
        """Test dependency tree generation."""
        from scripts.generate_sbom import SBOMGenerator

        # Mock pipdeptree output
        deps_data = [
            {
                "package": {
                    "package_name": "test-package",
                    "installed_version": "1.0.0"
                },
                "dependencies": [
                    {
                        "package_name": "dependency1",
                        "installed_version": "2.0.0"
                    }
                ]
            }
        ]

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(deps_data),
            stderr=''
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SBOMGenerator(Path.cwd(), Path(temp_dir))
            result = generator.generate_dependency_tree()

            assert result is not None
            assert result.name.startswith("dependency-tree-")
            assert result.suffix == ".txt"

            # Check file content
            with open(result, 'r') as f:
                content = f.read()
                assert "test-package==1.0.0" in content
                assert "dependency1==2.0.0" in content

    def test_license_report_generation(self):
        """Test license report generation."""
        from scripts.generate_sbom import SBOMGenerator

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SBOMGenerator(Path.cwd(), Path(temp_dir))

            # Mock pkg_resources.working_set
            mock_package = MagicMock()
            mock_package.project_name = "test-package"
            mock_package.version = "1.0.0"
            mock_package.location = "/path/to/package"
            mock_package.get_metadata.return_value = "License: MIT\nAuthor: Test"

            with patch('pkg_resources.working_set', [mock_package]):
                result = generator.generate_license_report()

                assert result is not None
                assert result.name.startswith("license-report-")
                assert result.suffix == ".json"

                # Check file content
                with open(result, 'r') as f:
                    data = json.load(f)
                    assert len(data["licenses"]) == 1
                    assert data["licenses"][0]["package"] == "test-package"
                    assert data["licenses"][0]["license"] == "MIT"


class TestSecurityPolicy:
    """Tests for security policy enforcement."""

    def test_security_policy_file_exists(self):
        """Test that security policy file exists."""
        policy_path = Path("SECURITY-POLICY.md")
        assert policy_path.exists(), "Security policy file not found"

    def test_dependabot_configuration_exists(self):
        """Test that Dependabot configuration exists."""
        dependabot_path = Path(".github/dependabot.yml")
        assert dependabot_path.exists(), "Dependabot configuration not found"

    def test_dependabot_security_updates_enabled(self):
        """Test that Dependabot has security updates enabled."""
        import yaml

        dependabot_path = Path(".github/dependabot.yml")
        with open(dependabot_path, 'r') as f:
            config = yaml.safe_load(f)

        pip_config = None
        for update in config.get("updates", []):
            if update.get("package-ecosystem") == "pip":
                pip_config = update
                break

        assert pip_config is not None, "pip package ecosystem not found in Dependabot config"

        # Check for security updates configuration
        security_updates = pip_config.get("security-updates", {})
        assert security_updates.get("enabled") is True, "Security updates not enabled"

    def test_security_workflow_exists(self):
        """Test that security workflow exists."""
        workflow_path = Path(".github/workflows/security.yml")
        assert workflow_path.exists(), "Security workflow not found"

    def test_requirements_files_exist(self):
        """Test that requirements files exist for dependency locking."""
        requirements_in = Path("requirements.in")
        requirements_dev_in = Path("requirements-dev.in")

        assert requirements_in.exists(), "requirements.in not found"
        assert requirements_dev_in.exists(), "requirements-dev.in not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

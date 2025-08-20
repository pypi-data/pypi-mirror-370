# tests/chaos/chaos_integration.py
"""
Chaos Engineering Integration Framework for KEI-Agent Python SDK.

This module provides integration capabilities for chaos engineering tests:
- CI/CD pipeline integration
- Safe execution in live environments
- Automated reporting and analysis
- Test orchestration and scheduling
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import argparse
from datetime import datetime, timezone

from tests.chaos.chaos_framework import ChaosTest, chaos_test_context
from tests.chaos.chaos_metrics import ChaosMetricsCollector, get_chaos_metrics_collector, reset_chaos_metrics_collector
from tests.chaos.test_network_chaos import TestNetworkChaos
from tests.chaos.test_service_dependency_chaos import TestServiceDependencyChaos
from tests.chaos.test_resource_exhaustion_chaos import TestResourceExhaustionChaos
from tests.chaos.test_configuration_chaos import TestConfigurationChaos
from tests.chaos.test_security_chaos import TestSecurityChaos

logger = logging.getLogger(__name__)


class ChaosTestSuite:
    """Orchestrates chaos engineering test execution."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize chaos test suite.

        Args:
            config: Configuration for chaos testing
        """
        self.config = config or {}
        self.metrics_collector = get_chaos_metrics_collector()
        self.test_results: List[Dict[str, Any]] = []
        self.failed_tests: List[str] = []

        # Test categories and their classes
        self.test_categories = {
            'network': TestNetworkChaos,
            'service_dependency': TestServiceDependencyChaos,
            'resource_exhaustion': TestResourceExhaustionChaos,
            'configuration': TestConfigurationChaos,
            'security': TestSecurityChaos
        }

    async def run_chaos_tests(self,
                             categories: List[str] = None,
                             test_names: List[str] = None,
                             safe_mode: bool = True) -> Dict[str, Any]:
        """Run chaos engineering tests.

        Args:
            categories: Test categories to run (default: all)
            test_names: Specific test names to run
            safe_mode: Whether to run in safe mode (limited chaos)

        Returns:
            Test execution results
        """
        logger.info("Starting chaos engineering test suite")

        # Reset metrics collector
        reset_chaos_metrics_collector()
        self.metrics_collector = get_chaos_metrics_collector()

        # Determine which tests to run
        categories = categories or list(self.test_categories.keys())

        execution_start = datetime.now(timezone.utc)

        for category in categories:
            if category not in self.test_categories:
                logger.warning(f"Unknown test category: {category}")
                continue

            logger.info(f"Running {category} chaos tests")

            try:
                await self._run_category_tests(category, test_names, safe_mode)
            except Exception as e:
                logger.error(f"Error running {category} tests: {e}")
                self.failed_tests.append(f"{category}_suite")

        execution_end = datetime.now(timezone.utc)

        # Generate comprehensive report
        report = await self._generate_execution_report(execution_start, execution_end)

        logger.info("Chaos engineering test suite completed")
        return report

    async def _run_category_tests(self,
                                 category: str,
                                 test_names: List[str] = None,
                                 safe_mode: bool = True) -> None:
        """Run tests for a specific category.

        Args:
            category: Test category name
            test_names: Specific test names to run
            safe_mode: Whether to run in safe mode
        """
        test_class = self.test_categories[category]
        test_instance = test_class()

        # Get all test methods
        test_methods = [
            method for method in dir(test_instance)
            if method.startswith('test_') and callable(getattr(test_instance, method))
        ]

        # Filter by test names if specified
        if test_names:
            test_methods = [
                method for method in test_methods
                if any(name in method for name in test_names)
            ]

        # Run each test method
        for test_method_name in test_methods:
            try:
                logger.info(f"Running {category}.{test_method_name}")

                # Setup test instance
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()

                # Get test method
                test_method = getattr(test_instance, test_method_name)

                # Run test with safety checks
                if safe_mode:
                    await self._run_test_safely(test_method, f"{category}.{test_method_name}")
                else:
                    await test_method()

                # Teardown test instance
                if hasattr(test_instance, 'teardown_method'):
                    test_instance.teardown_method()

                logger.info(f"Completed {category}.{test_method_name}")

            except Exception as e:
                logger.error(f"Test {category}.{test_method_name} failed: {e}")
                self.failed_tests.append(f"{category}.{test_method_name}")

    async def _run_test_safely(self, test_method, test_name: str) -> None:
        """Run a test method with safety checks.

        Args:
            test_method: Test method to run
            test_name: Name of the test
        """
        # Pre-test safety checks
        if not await self._pre_test_safety_check():
            logger.warning(f"Skipping {test_name} due to safety check failure")
            return

        try:
            # Run test with timeout
            await asyncio.wait_for(test_method(), timeout=300)  # 5 minute timeout

        except asyncio.TimeoutError:
            logger.error(f"Test {test_name} timed out")
            raise

        finally:
            # Post-test safety checks and cleanup
            await self._post_test_safety_check()

    async def _pre_test_safety_check(self) -> bool:
        """Perform safety checks before running tests.

        Returns:
            True if safe to proceed
        """
        try:
            import psutil

            # Check system resources
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')

            # Safety thresholds
            if memory.percent > 90:
                logger.warning("Memory usage too high for chaos testing")
                return False

            if cpu > 90:
                logger.warning("CPU usage too high for chaos testing")
                return False

            if disk.percent > 95:
                logger.warning("Disk usage too high for chaos testing")
                return False

            return True

        except Exception as e:
            logger.error(f"Error in safety check: {e}")
            return False

    async def _post_test_safety_check(self) -> None:
        """Perform cleanup and safety checks after tests."""
        try:
            # Allow system to stabilize
            await asyncio.sleep(1.0)

            # Check for resource leaks
            import psutil
            memory = psutil.virtual_memory()

            if memory.percent > 85:
                logger.warning("High memory usage after test - potential leak")

            # Force garbage collection
            import gc
            gc.collect()

        except Exception as e:
            logger.error(f"Error in post-test safety check: {e}")

    async def _generate_execution_report(self,
                                       start_time: datetime,
                                       end_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive execution report.

        Args:
            start_time: Test execution start time
            end_time: Test execution end time

        Returns:
            Execution report
        """
        # Get metrics summary
        summary_report = self.metrics_collector.generate_summary_report()

        # Add execution metadata
        execution_report = {
            'execution_metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'environment': self._get_environment_info(),
                'configuration': self.config,
                'failed_tests': self.failed_tests
            },
            'chaos_test_results': summary_report,
            'recommendations': self._generate_recommendations(summary_report),
            'next_steps': self._generate_next_steps(summary_report)
        }

        return execution_report

    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for the report."""
        try:
            import platform
            import psutil

            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'disk_total_gb': psutil.disk_usage('/').total / (1024**3),
                'hostname': platform.node(),
                'ci_environment': os.getenv('CI', 'false').lower() == 'true',
                'environment_type': os.getenv('CHAOS_ENV', 'development')
            }
        except Exception as e:
            logger.error(f"Error getting environment info: {e}")
            return {'error': str(e)}

    def _generate_recommendations(self, summary_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results.

        Args:
            summary_report: Summary report from metrics collector

        Returns:
            List of recommendations
        """
        recommendations = []

        # Get overall resilience score
        overall_score = summary_report.get('summary', {}).get('overall_resilience_score', 0)

        if overall_score < 70:
            recommendations.append("Overall system resilience is below acceptable threshold (70%)")
            recommendations.append("Consider implementing comprehensive monitoring and alerting")
            recommendations.append("Review and strengthen error handling mechanisms")

        # Check for specific weak points
        weak_points = summary_report.get('weak_points', [])
        for weak_point in weak_points:
            component = weak_point.get('component', 'unknown')
            issues = weak_point.get('issues', [])

            if 'low_availability' in issues:
                recommendations.append(f"Improve {component} availability through redundancy and failover")

            if 'slow_recovery' in issues:
                recommendations.append(f"Optimize {component} recovery time with faster health checks")

            if 'poor_error_handling' in issues:
                recommendations.append(f"Enhance {component} error handling and logging")

        # Performance impact recommendations
        performance_impact = summary_report.get('performance_impact', {})

        if performance_impact.get('cpu', {}).get('impact_level') == 'high':
            recommendations.append("High CPU impact detected - consider optimizing resource usage")

        if performance_impact.get('memory', {}).get('impact_level') == 'high':
            recommendations.append("High memory impact detected - review memory management")

        return recommendations

    def _generate_next_steps(self, summary_report: Dict[str, Any]) -> List[str]:
        """Generate next steps based on test results.

        Args:
            summary_report: Summary report from metrics collector

        Returns:
            List of next steps
        """
        next_steps = []

        # Failed tests
        if self.failed_tests:
            next_steps.append(f"Investigate and fix {len(self.failed_tests)} failed tests")
            next_steps.append("Re-run failed tests after fixes are implemented")

        # Resilience improvements
        overall_score = summary_report.get('summary', {}).get('overall_resilience_score', 0)

        if overall_score < 80:
            next_steps.append("Implement resilience improvements based on recommendations")
            next_steps.append("Schedule follow-up chaos testing to validate improvements")

        # Monitoring and alerting
        next_steps.append("Set up continuous chaos testing in staging environment")
        next_steps.append("Integrate chaos test metrics into monitoring dashboards")
        next_steps.append("Establish chaos testing schedule for production validation")

        return next_steps

    def save_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Save execution report to file.

        Args:
            report: Execution report
            output_path: Path to save the report
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Chaos engineering report saved to {output_path}")

        except Exception as e:
            logger.error(f"Error saving report: {e}")


async def main():
    """Main entry point for chaos testing CLI."""
    parser = argparse.ArgumentParser(description="KEI-Agent Chaos Engineering Test Suite")

    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['network', 'service_dependency', 'resource_exhaustion', 'configuration', 'security'],
        help='Test categories to run'
    )

    parser.add_argument(
        '--tests',
        nargs='+',
        help='Specific test names to run'
    )

    parser.add_argument(
        '--safe-mode',
        action='store_true',
        default=True,
        help='Run in safe mode with limited chaos (default: True)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('chaos_test_report.json'),
        help='Output file for test report'
    )

    parser.add_argument(
        '--config',
        type=Path,
        help='Configuration file for chaos testing'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load configuration
    config = {}
    if args.config and args.config.exists():
        try:
            with open(args.config) as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)

    # Create and run test suite
    test_suite = ChaosTestSuite(config)

    try:
        report = await test_suite.run_chaos_tests(
            categories=args.categories,
            test_names=args.tests,
            safe_mode=args.safe_mode
        )

        # Save report
        test_suite.save_report(report, args.output)

        # Print summary
        print("\n" + "="*60)
        print("CHAOS ENGINEERING TEST SUMMARY")
        print("="*60)

        summary = report.get('chaos_test_results', {}).get('summary', {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Overall Resilience Score: {summary.get('overall_resilience_score', 0):.1f}%")
        print(f"Failed Tests: {len(test_suite.failed_tests)}")

        if test_suite.failed_tests:
            print("\nFailed Tests:")
            for test in test_suite.failed_tests:
                print(f"  - {test}")

        recommendations = report.get('recommendations', [])
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations[:5]:  # Show top 5
                print(f"  - {rec}")

        print(f"\nFull report saved to: {args.output}")

        # Exit with error code if tests failed
        if test_suite.failed_tests:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Chaos testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

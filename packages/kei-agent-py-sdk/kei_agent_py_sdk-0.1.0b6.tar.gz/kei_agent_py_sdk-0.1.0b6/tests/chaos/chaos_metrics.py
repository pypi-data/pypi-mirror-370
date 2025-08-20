# tests/chaos/chaos_metrics.py
"""
Chaos Engineering Metrics Collection and Analysis.

This module provides comprehensive metrics collection, analysis, and reporting
for chaos engineering tests to measure system resilience.
"""

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class ResilienceScore:
    """Calculated resilience score for a system component."""

    component: str
    availability_score: float  # 0-100
    recovery_score: float     # 0-100
    error_handling_score: float  # 0-100
    overall_score: float      # 0-100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ChaosMetricsCollector:
    """Collects and analyzes metrics from chaos engineering tests."""

    def __init__(self):
        """Initialize metrics collector."""
        self.test_results: List[Dict[str, Any]] = []
        self.baseline_metrics: Dict[str, Any] = {}

    def add_test_result(self, metrics: Dict[str, Any]) -> None:
        """Add test result metrics.

        Args:
            metrics: Test metrics dictionary
        """
        self.test_results.append({
            **metrics,
            'timestamp': time.time()
        })
        logger.info(f"Added test result for {metrics.get('test_name', 'unknown')}")

    def set_baseline_metrics(self, metrics: Dict[str, Any]) -> None:
        """Set baseline metrics for comparison.

        Args:
            metrics: Baseline metrics dictionary
        """
        self.baseline_metrics = metrics
        logger.info("Baseline metrics set")

    def calculate_resilience_scores(self) -> Dict[str, ResilienceScore]:
        """Calculate resilience scores for different components.

        Returns:
            Dictionary mapping component names to resilience scores
        """
        scores = {}

        # Group tests by component/category
        test_groups = self._group_tests_by_component()

        for component, tests in test_groups.items():
            availability_score = self._calculate_availability_score(tests)
            recovery_score = self._calculate_recovery_score(tests)
            error_handling_score = self._calculate_error_handling_score(tests)

            overall_score = (availability_score + recovery_score + error_handling_score) / 3

            scores[component] = ResilienceScore(
                component=component,
                availability_score=availability_score,
                recovery_score=recovery_score,
                error_handling_score=error_handling_score,
                overall_score=overall_score
            )

        return scores

    def _group_tests_by_component(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group test results by component."""
        groups = {}

        for test in self.test_results:
            test_name = test.get('test_name', '')

            # Extract component from test name
            if 'network' in test_name.lower():
                component = 'network'
            elif 'service' in test_name.lower() or 'dependency' in test_name.lower():
                component = 'service_dependencies'
            elif 'resource' in test_name.lower():
                component = 'resource_management'
            elif 'config' in test_name.lower():
                component = 'configuration'
            elif 'security' in test_name.lower():
                component = 'security'
            else:
                component = 'general'

            if component not in groups:
                groups[component] = []
            groups[component].append(test)

        return groups

    def _calculate_availability_score(self, tests: List[Dict[str, Any]]) -> float:
        """Calculate availability score based on success rates."""
        if not tests:
            return 0.0

        success_rates = []
        for test in tests:
            success_rate = test.get('success_rate', 0.0)
            success_rates.append(success_rate * 100)  # Convert to percentage

        return statistics.mean(success_rates) if success_rates else 0.0

    def _calculate_recovery_score(self, tests: List[Dict[str, Any]]) -> float:
        """Calculate recovery score based on recovery times."""
        if not tests:
            return 0.0

        recovery_scores = []
        for test in tests:
            recovery_time = test.get('time_to_recovery')
            if recovery_time is not None:
                # Score based on recovery time (faster = better)
                # 100 points for recovery under 1 second, decreasing linearly
                if recovery_time <= 1.0:
                    score = 100.0
                elif recovery_time <= 10.0:
                    score = 100.0 - ((recovery_time - 1.0) * 10.0)  # 90-100 points
                elif recovery_time <= 30.0:
                    score = 10.0 - ((recovery_time - 10.0) * 0.5)   # 0-10 points
                else:
                    score = 0.0

                recovery_scores.append(max(0.0, score))
            else:
                # No recovery detected
                recovery_scores.append(0.0)

        return statistics.mean(recovery_scores) if recovery_scores else 0.0

    def _calculate_error_handling_score(self, tests: List[Dict[str, Any]]) -> float:
        """Calculate error handling score based on error rates during chaos."""
        if not tests:
            return 0.0

        error_scores = []
        for test in tests:
            errors = test.get('errors_during_chaos', 0)
            total_ops = test.get('successful_operations', 0) + test.get('failed_operations', 0)

            if total_ops > 0:
                error_rate = errors / total_ops
                # Score inversely proportional to error rate
                score = max(0.0, 100.0 - (error_rate * 100.0))
                error_scores.append(score)
            else:
                error_scores.append(100.0)  # No operations = no errors

        return statistics.mean(error_scores) if error_scores else 0.0

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary report.

        Returns:
            Summary report dictionary
        """
        resilience_scores = self.calculate_resilience_scores()

        # Calculate overall system resilience
        overall_resilience = statistics.mean([
            score.overall_score for score in resilience_scores.values()
        ]) if resilience_scores else 0.0

        # Analyze test trends
        test_trends = self._analyze_test_trends()

        # Identify weak points
        weak_points = self._identify_weak_points(resilience_scores)

        # Performance impact analysis
        performance_impact = self._analyze_performance_impact()

        report = {
            'summary': {
                'total_tests': len(self.test_results),
                'overall_resilience_score': overall_resilience,
                'test_period': self._get_test_period(),
                'components_tested': list(resilience_scores.keys())
            },
            'resilience_scores': {
                name: score.to_dict() for name, score in resilience_scores.items()
            },
            'trends': test_trends,
            'weak_points': weak_points,
            'performance_impact': performance_impact,
            'recommendations': self._generate_recommendations(resilience_scores)
        }

        return report

    def _analyze_test_trends(self) -> Dict[str, Any]:
        """Analyze trends in test results over time."""
        if len(self.test_results) < 2:
            return {'trend': 'insufficient_data'}

        # Sort tests by timestamp
        sorted_tests = sorted(self.test_results, key=lambda x: x.get('timestamp', 0))

        # Calculate trend in success rates
        success_rates = [test.get('success_rate', 0.0) for test in sorted_tests]

        if len(success_rates) >= 2:
            trend_direction = 'improving' if success_rates[-1] > success_rates[0] else 'degrading'
            trend_magnitude = abs(success_rates[-1] - success_rates[0])
        else:
            trend_direction = 'stable'
            trend_magnitude = 0.0

        return {
            'trend': trend_direction,
            'magnitude': trend_magnitude,
            'success_rate_trend': success_rates,
            'recovery_time_trend': [test.get('time_to_recovery') for test in sorted_tests]
        }

    def _identify_weak_points(self, resilience_scores: Dict[str, ResilienceScore]) -> List[Dict[str, Any]]:
        """Identify system weak points based on resilience scores."""
        weak_points = []

        for component, score in resilience_scores.items():
            if score.overall_score < 70.0:  # Threshold for weak points
                weak_point = {
                    'component': component,
                    'overall_score': score.overall_score,
                    'issues': []
                }

                if score.availability_score < 70.0:
                    weak_point['issues'].append('low_availability')
                if score.recovery_score < 70.0:
                    weak_point['issues'].append('slow_recovery')
                if score.error_handling_score < 70.0:
                    weak_point['issues'].append('poor_error_handling')

                weak_points.append(weak_point)

        return weak_points

    def _analyze_performance_impact(self) -> Dict[str, Any]:
        """Analyze performance impact during chaos tests."""
        if not self.test_results:
            return {}

        # Analyze system metrics during tests
        cpu_impacts = []
        memory_impacts = []

        for test in self.test_results:
            system_metrics = test.get('system_metrics', {})

            if 'cpu_percent' in system_metrics:
                cpu_impacts.append(system_metrics['cpu_percent'])
            if 'memory_percent' in system_metrics:
                memory_impacts.append(system_metrics['memory_percent'])

        impact_analysis = {}

        if cpu_impacts:
            impact_analysis['cpu'] = {
                'max_usage': max(cpu_impacts),
                'avg_usage': statistics.mean(cpu_impacts),
                'impact_level': 'high' if max(cpu_impacts) > 80 else 'medium' if max(cpu_impacts) > 50 else 'low'
            }

        if memory_impacts:
            impact_analysis['memory'] = {
                'max_usage': max(memory_impacts),
                'avg_usage': statistics.mean(memory_impacts),
                'impact_level': 'high' if max(memory_impacts) > 80 else 'medium' if max(memory_impacts) > 50 else 'low'
            }

        return impact_analysis

    def _generate_recommendations(self, resilience_scores: Dict[str, ResilienceScore]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        for component, score in resilience_scores.items():
            if score.availability_score < 80.0:
                recommendations.append(f"Improve {component} availability through better error handling and fallback mechanisms")

            if score.recovery_score < 80.0:
                recommendations.append(f"Optimize {component} recovery time through faster health checks and circuit breakers")

            if score.error_handling_score < 80.0:
                recommendations.append(f"Enhance {component} error handling with better logging and graceful degradation")

        # General recommendations
        overall_score = statistics.mean([score.overall_score for score in resilience_scores.values()])

        if overall_score < 70.0:
            recommendations.append("Consider implementing comprehensive monitoring and alerting")
            recommendations.append("Add more robust retry mechanisms and circuit breakers")
            recommendations.append("Implement graceful degradation for critical components")

        return recommendations

    def _get_test_period(self) -> Dict[str, Any]:
        """Get the time period covered by tests."""
        if not self.test_results:
            return {}

        timestamps = [test.get('timestamp', 0) for test in self.test_results]

        return {
            'start_time': min(timestamps),
            'end_time': max(timestamps),
            'duration_hours': (max(timestamps) - min(timestamps)) / 3600
        }

    def save_report(self, report: Dict[str, Any], file_path: Path) -> None:
        """Save report to file.

        Args:
            report: Report dictionary
            file_path: Path to save the report
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Chaos engineering report saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    def export_metrics_csv(self, file_path: Path) -> None:
        """Export metrics to CSV format.

        Args:
            file_path: Path to save the CSV file
        """
        try:
            import csv

            with open(file_path, 'w', newline='') as csvfile:
                if not self.test_results:
                    return

                fieldnames = self.test_results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for test in self.test_results:
                    writer.writerow(test)

            logger.info(f"Metrics exported to CSV: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")


# Global metrics collector instance
_metrics_collector: Optional[ChaosMetricsCollector] = None


def get_chaos_metrics_collector() -> ChaosMetricsCollector:
    """Get the global chaos metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = ChaosMetricsCollector()
    return _metrics_collector


def reset_chaos_metrics_collector() -> None:
    """Reset the global chaos metrics collector."""
    global _metrics_collector
    _metrics_collector = ChaosMetricsCollector()

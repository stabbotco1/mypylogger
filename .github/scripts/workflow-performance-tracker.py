#!/usr/bin/env python3
"""Centralized Workflow Performance Tracking Script

This script provides centralized workflow performance monitoring,
metrics collection, and automated alerting for CI/CD workflows.

Requirements Addressed:
- 7.1: Implement workflow performance tracking and metrics collection
- 7.2: Add automated alerts for workflow performance degradation
- 7.3: Create periodic workflow health reports
- 7.4: Track workflow success rates and execution times
"""

import argparse
from datetime import datetime
import json
import os
import sys
from typing import Dict, List, Optional


class WorkflowPerformanceTracker:
    """Centralized workflow performance tracking and monitoring."""

    def __init__(self, github_token: Optional[str] = None):
        """Initialize the performance tracker."""
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPOSITORY", "unknown/unknown")
        self.run_id = os.getenv("GITHUB_RUN_ID", "unknown")

        # Performance thresholds
        self.thresholds = {
            "failure_rate_warning": 5.0,  # 5% failure rate warning
            "failure_rate_critical": 10.0,  # 10% failure rate critical
            "duration_warning": 300,  # 5 minutes warning
            "duration_critical": 600,  # 10 minutes critical
            "cache_hit_rate_warning": 80.0,  # 80% cache hit rate warning
        }

        # Workflow performance targets
        self.targets = {
            "quality_gate_duration": 300,  # 5 minutes target
            "security_scan_duration": 480,  # 8 minutes target
            "docs_build_duration": 300,  # 5 minutes target
            "publish_duration": 300,  # 5 minutes target
        }

    def collect_workflow_metrics(
        self, workflow_name: str, status: str, duration: int, cache_hit_rate: Optional[float] = None
    ) -> Dict:
        """Collect and analyze workflow performance metrics."""
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Determine performance status
        target_duration = self.targets.get(
            workflow_name.lower().replace(" ", "_").replace("-", "_") + "_duration",
            self.thresholds["duration_warning"],
        )

        performance_status = self._assess_performance(duration, target_duration, status)

        # Calculate performance score
        performance_score = self._calculate_performance_score(
            duration, target_duration, status, cache_hit_rate
        )

        metrics = {
            "timestamp": timestamp,
            "workflow_name": workflow_name,
            "run_id": self.run_id,
            "repository": self.repo,
            "status": status,
            "duration_seconds": duration,
            "duration_minutes": round(duration / 60, 2),
            "target_duration_seconds": target_duration,
            "performance_status": performance_status,
            "performance_score": performance_score,
            "cache_hit_rate": cache_hit_rate,
            "thresholds": self.thresholds.copy(),
            "analysis": self._generate_performance_analysis(
                workflow_name, duration, target_duration, status, cache_hit_rate
            ),
        }

        return metrics

    def _assess_performance(self, duration: int, target: int, status: str) -> str:
        """Assess workflow performance status."""
        if status != "success":
            return "failed"

        if duration <= target:
            return "excellent"
        if duration <= self.thresholds["duration_warning"]:
            return "good"
        if duration <= self.thresholds["duration_critical"]:
            return "acceptable"
        return "poor"

    def _calculate_performance_score(
        self, duration: int, target: int, status: str, cache_hit_rate: Optional[float]
    ) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100

        # Deduct points for failure
        if status != "success":
            score -= 50

        # Deduct points for duration overrun
        if duration > target:
            overrun_ratio = duration / target
            if overrun_ratio > 2.0:
                score -= 30
            elif overrun_ratio > 1.5:
                score -= 20
            elif overrun_ratio > 1.2:
                score -= 10
            else:
                score -= 5

        # Deduct points for poor cache performance
        if cache_hit_rate is not None:
            if cache_hit_rate < 70:
                score -= 15
            elif cache_hit_rate < 80:
                score -= 10
            elif cache_hit_rate < 90:
                score -= 5

        return max(0, score)

    def _generate_performance_analysis(
        self,
        workflow_name: str,
        duration: int,
        target: int,
        status: str,
        cache_hit_rate: Optional[float],
    ) -> Dict:
        """Generate detailed performance analysis."""
        analysis = {
            "status_assessment": self._analyze_status(status),
            "duration_assessment": self._analyze_duration(duration, target),
            "cache_assessment": self._analyze_cache_performance(cache_hit_rate),
            "recommendations": self._generate_recommendations(
                workflow_name, duration, target, status, cache_hit_rate
            ),
        }

        return analysis

    def _analyze_status(self, status: str) -> Dict:
        """Analyze workflow status."""
        if status == "success":
            return {
                "result": "positive",
                "message": "Workflow completed successfully",
                "impact": "none",
            }
        return {
            "result": "negative",
            "message": f"Workflow failed with status: {status}",
            "impact": "high",
        }

    def _analyze_duration(self, duration: int, target: int) -> Dict:
        """Analyze workflow duration performance."""
        if duration <= target:
            return {
                "result": "positive",
                "message": f"Duration within target ({duration}s ≤ {target}s)",
                "impact": "none",
                "efficiency": round((target - duration) / target * 100, 1),
            }
        overrun = duration - target
        overrun_percent = round(overrun / target * 100, 1)
        return {
            "result": "negative",
            "message": f"Duration exceeds target by {overrun}s ({overrun_percent}%)",
            "impact": "medium" if overrun_percent < 50 else "high",
            "efficiency": 0,
        }

    def _analyze_cache_performance(self, cache_hit_rate: Optional[float]) -> Dict:
        """Analyze cache performance."""
        if cache_hit_rate is None:
            return {
                "result": "unknown",
                "message": "Cache hit rate not available",
                "impact": "none",
            }

        if cache_hit_rate >= 90:
            return {
                "result": "excellent",
                "message": f"Excellent cache performance ({cache_hit_rate}%)",
                "impact": "positive",
            }
        if cache_hit_rate >= 80:
            return {
                "result": "good",
                "message": f"Good cache performance ({cache_hit_rate}%)",
                "impact": "low",
            }
        return {
            "result": "poor",
            "message": f"Poor cache performance ({cache_hit_rate}%)",
            "impact": "medium",
        }

    def _generate_recommendations(
        self,
        workflow_name: str,
        duration: int,
        target: int,
        status: str,
        cache_hit_rate: Optional[float],
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Status-based recommendations
        if status != "success":
            recommendations.extend(
                [
                    "Investigate workflow failure root cause",
                    "Review error logs and failure patterns",
                    "Implement failure recovery mechanisms",
                ]
            )

        # Duration-based recommendations
        if duration > target:
            overrun_percent = (duration - target) / target * 100
            if overrun_percent > 50:
                recommendations.extend(
                    [
                        "Critical performance issue - immediate optimization needed",
                        "Review workflow job dependencies and parallelization",
                        "Consider infrastructure upgrades or self-hosted runners",
                    ]
                )
            elif overrun_percent > 20:
                recommendations.extend(
                    [
                        "Optimize dependency installation and caching",
                        "Review test execution efficiency",
                        "Consider workflow job restructuring",
                    ]
                )
            else:
                recommendations.append("Minor optimization opportunities available")

        # Cache-based recommendations
        if cache_hit_rate is not None and cache_hit_rate < 80:
            recommendations.extend(
                [
                    "Improve caching strategy and cache key optimization",
                    "Review cache retention policies",
                    "Implement multi-level caching approach",
                ]
            )

        # Workflow-specific recommendations
        workflow_lower = workflow_name.lower()
        if "quality" in workflow_lower or "test" in workflow_lower:
            recommendations.extend(
                [
                    "Consider parallel test execution",
                    "Optimize test data and fixtures",
                    "Review test coverage requirements",
                ]
            )
        elif "security" in workflow_lower:
            recommendations.extend(
                [
                    "Implement incremental security scanning",
                    "Optimize CodeQL analysis configuration",
                    "Consider security scan result caching",
                ]
            )
        elif "docs" in workflow_lower or "documentation" in workflow_lower:
            recommendations.extend(
                [
                    "Implement incremental documentation building",
                    "Optimize Sphinx build configuration",
                    "Consider documentation artifact caching",
                ]
            )

        return recommendations

    def generate_performance_alert(self, metrics: Dict) -> Optional[Dict]:
        """Generate performance alert if thresholds are exceeded."""
        alert_conditions = []
        severity = "info"

        # Check failure
        if metrics["status"] != "success":
            alert_conditions.append(f"Workflow failed with status: {metrics['status']}")
            severity = "critical"

        # Check duration thresholds
        duration = metrics["duration_seconds"]
        if duration > self.thresholds["duration_critical"]:
            alert_conditions.append(
                f"Duration critically high: {duration}s > {self.thresholds['duration_critical']}s"
            )
            severity = "critical"
        elif duration > self.thresholds["duration_warning"]:
            alert_conditions.append(
                f"Duration warning: {duration}s > {self.thresholds['duration_warning']}s"
            )
            if severity == "info":
                severity = "warning"

        # Check cache performance
        cache_hit_rate = metrics.get("cache_hit_rate")
        if (
            cache_hit_rate is not None
            and cache_hit_rate < self.thresholds["cache_hit_rate_warning"]
        ):
            alert_conditions.append(
                f"Cache hit rate low: {cache_hit_rate}% < {self.thresholds['cache_hit_rate_warning']}%"
            )
            if severity == "info":
                severity = "warning"

        # Generate alert if conditions met
        if alert_conditions:
            return {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "workflow_name": metrics["workflow_name"],
                "run_id": metrics["run_id"],
                "severity": severity,
                "conditions": alert_conditions,
                "metrics": {
                    "duration": metrics["duration_seconds"],
                    "status": metrics["status"],
                    "performance_score": metrics["performance_score"],
                    "cache_hit_rate": cache_hit_rate,
                },
                "recommendations": metrics["analysis"]["recommendations"],
            }

        return None

    def save_metrics(self, metrics: Dict, output_dir: str = "monitoring-results") -> str:
        """Save performance metrics to file."""
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename with timestamp and workflow name
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        workflow_safe = metrics["workflow_name"].lower().replace(" ", "_").replace("-", "_")
        filename = f"performance_{workflow_safe}_{timestamp}_{self.run_id}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(metrics, f, indent=2)

        return filepath

    def save_alert(self, alert: Dict, output_dir: str = "monitoring-results") -> str:
        """Save performance alert to file."""
        os.makedirs(output_dir, exist_ok=True)

        # Generate alert filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        workflow_safe = alert["workflow_name"].lower().replace(" ", "_").replace("-", "_")
        filename = f"alert_{alert['severity']}_{workflow_safe}_{timestamp}_{self.run_id}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(alert, f, indent=2)

        return filepath


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Workflow Performance Tracking and Monitoring")
    parser.add_argument(
        "--workflow-name", required=True, help="Name of the workflow being monitored"
    )
    parser.add_argument(
        "--status", required=True, help="Workflow status (success, failure, cancelled)"
    )
    parser.add_argument("--duration", type=int, required=True, help="Workflow duration in seconds")
    parser.add_argument("--cache-hit-rate", type=float, help="Cache hit rate percentage (0-100)")
    parser.add_argument(
        "--output-dir", default="monitoring-results", help="Output directory for results"
    )
    parser.add_argument(
        "--generate-alert", action="store_true", help="Generate alert if thresholds exceeded"
    )

    args = parser.parse_args()

    try:
        # Initialize tracker
        tracker = WorkflowPerformanceTracker()

        # Collect metrics
        print("📊 Collecting workflow performance metrics...")
        metrics = tracker.collect_workflow_metrics(
            workflow_name=args.workflow_name,
            status=args.status,
            duration=args.duration,
            cache_hit_rate=args.cache_hit_rate,
        )

        # Save metrics
        metrics_file = tracker.save_metrics(metrics, args.output_dir)
        print(f"✅ Metrics saved to: {metrics_file}")

        # Display summary
        print("\n📈 Performance Summary:")
        print(f"- Workflow: {metrics['workflow_name']}")
        print(f"- Status: {metrics['status']}")
        print(f"- Duration: {metrics['duration_minutes']} minutes")
        print(f"- Performance Status: {metrics['performance_status']}")
        print(f"- Performance Score: {metrics['performance_score']}/100")

        if metrics.get("cache_hit_rate"):
            print(f"- Cache Hit Rate: {metrics['cache_hit_rate']}%")

        # Generate alert if requested and conditions met
        if args.generate_alert:
            alert = tracker.generate_performance_alert(metrics)
            if alert:
                alert_file = tracker.save_alert(alert, args.output_dir)
                print(f"\n🚨 Alert generated: {alert_file}")
                print(f"   Severity: {alert['severity']}")
                print(f"   Conditions: {len(alert['conditions'])}")
            else:
                print("\n✅ No alerts generated - performance within thresholds")

        # Display recommendations
        recommendations = metrics["analysis"]["recommendations"]
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"   {i}. {rec}")

        print("\n📊 Monitoring completed successfully")

    except Exception as e:
        print(f"❌ Error in workflow performance tracking: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

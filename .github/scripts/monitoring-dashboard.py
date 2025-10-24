#!/usr/bin/env python3
"""Centralized Workflow Monitoring Dashboard

This script generates comprehensive monitoring dashboards and health reports
for all CI/CD workflows, providing insights into performance trends and
system health.

Requirements Addressed:
- 7.1: Implement centralized workflow performance monitoring
- 7.3: Create periodic workflow health reports
- 7.4: Track workflow success rates and execution times
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import glob
import json
import os
import statistics
import sys
from typing import Dict, List, Tuple


class MonitoringDashboard:
    """Centralized monitoring dashboard and reporting system."""

    def __init__(self, monitoring_dir: str = "monitoring-results"):
        """Initialize the monitoring dashboard."""
        self.monitoring_dir = monitoring_dir
        self.repo = os.getenv("GITHUB_REPOSITORY", "unknown/unknown")

        # Health score thresholds
        self.health_thresholds = {"excellent": 90, "good": 75, "acceptable": 60, "poor": 0}

    def load_performance_data(self, days: int = 7) -> List[Dict]:
        """Load performance data from the last N days."""
        performance_files = glob.glob(os.path.join(self.monitoring_dir, "performance_*.json"))

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_data = []

        for file_path in performance_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by date
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_date:
                    recent_data.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue

        # Sort by timestamp
        recent_data.sort(key=lambda x: x["timestamp"])
        return recent_data

    def load_alert_data(self, days: int = 7) -> List[Dict]:
        """Load alert data from the last N days."""
        alert_files = glob.glob(os.path.join(self.monitoring_dir, "alert_*.json"))

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_alerts = []

        for file_path in alert_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by date
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_date:
                    recent_alerts.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse alert file {file_path}: {e}")
                continue

        # Sort by timestamp
        recent_alerts.sort(key=lambda x: x["timestamp"])
        return recent_alerts

    def calculate_workflow_statistics(self, performance_data: List[Dict]) -> Dict:
        """Calculate comprehensive workflow statistics."""
        if not performance_data:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "avg_duration": 0.0,
                "avg_performance_score": 0.0,
                "workflows": {},
            }

        # Overall statistics
        total_runs = len(performance_data)
        successful_runs = sum(1 for run in performance_data if run["status"] == "success")
        success_rate = (successful_runs / total_runs) * 100
        failure_rate = 100 - success_rate

        # Duration statistics
        durations = [run["duration_seconds"] for run in performance_data]
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)

        # Performance score statistics
        performance_scores = [run["performance_score"] for run in performance_data]
        avg_performance_score = statistics.mean(performance_scores)

        # Per-workflow statistics
        workflow_stats = defaultdict(
            lambda: {
                "runs": 0,
                "successes": 0,
                "failures": 0,
                "durations": [],
                "performance_scores": [],
            }
        )

        for run in performance_data:
            workflow = run["workflow_name"]
            workflow_stats[workflow]["runs"] += 1

            if run["status"] == "success":
                workflow_stats[workflow]["successes"] += 1
            else:
                workflow_stats[workflow]["failures"] += 1

            workflow_stats[workflow]["durations"].append(run["duration_seconds"])
            workflow_stats[workflow]["performance_scores"].append(run["performance_score"])

        # Calculate per-workflow metrics
        workflows = {}
        for workflow, stats in workflow_stats.items():
            workflows[workflow] = {
                "total_runs": stats["runs"],
                "success_rate": (stats["successes"] / stats["runs"]) * 100,
                "failure_rate": (stats["failures"] / stats["runs"]) * 100,
                "avg_duration": statistics.mean(stats["durations"]),
                "median_duration": statistics.median(stats["durations"]),
                "avg_performance_score": statistics.mean(stats["performance_scores"]),
                "min_duration": min(stats["durations"]),
                "max_duration": max(stats["durations"]),
            }

        return {
            "total_runs": total_runs,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "avg_duration": avg_duration,
            "median_duration": median_duration,
            "avg_performance_score": avg_performance_score,
            "min_duration": min(durations),
            "max_duration": max(durations),
            "workflows": workflows,
        }

    def calculate_system_health_score(self, stats: Dict, alerts: List[Dict]) -> Tuple[int, str]:
        """Calculate overall system health score."""
        health_score = 100

        # Deduct points for high failure rate
        failure_rate = stats["failure_rate"]
        if failure_rate > 15:
            health_score -= 40
        elif failure_rate > 10:
            health_score -= 25
        elif failure_rate > 5:
            health_score -= 15
        elif failure_rate > 2:
            health_score -= 5

        # Deduct points for poor performance
        avg_performance_score = stats["avg_performance_score"]
        if avg_performance_score < 60:
            health_score -= 30
        elif avg_performance_score < 75:
            health_score -= 20
        elif avg_performance_score < 85:
            health_score -= 10

        # Deduct points for recent alerts
        critical_alerts = sum(1 for alert in alerts if alert["severity"] == "critical")
        warning_alerts = sum(1 for alert in alerts if alert["severity"] == "warning")

        health_score -= critical_alerts * 15
        health_score -= warning_alerts * 5

        # Ensure score is within bounds
        health_score = max(0, min(100, health_score))

        # Determine health status
        if health_score >= self.health_thresholds["excellent"]:
            health_status = "excellent"
        elif health_score >= self.health_thresholds["good"]:
            health_status = "good"
        elif health_score >= self.health_thresholds["acceptable"]:
            health_status = "acceptable"
        else:
            health_status = "poor"

        return health_score, health_status

    def generate_performance_trends(self, performance_data: List[Dict]) -> Dict:
        """Generate performance trend analysis."""
        if len(performance_data) < 2:
            return {"trend_available": False, "message": "Insufficient data for trend analysis"}

        # Split data into two halves for comparison
        mid_point = len(performance_data) // 2
        first_half = performance_data[:mid_point]
        second_half = performance_data[mid_point:]

        # Calculate metrics for each half
        first_stats = self.calculate_workflow_statistics(first_half)
        second_stats = self.calculate_workflow_statistics(second_half)

        # Calculate trends
        success_rate_trend = second_stats["success_rate"] - first_stats["success_rate"]
        duration_trend = second_stats["avg_duration"] - first_stats["avg_duration"]
        performance_trend = (
            second_stats["avg_performance_score"] - first_stats["avg_performance_score"]
        )

        return {
            "trend_available": True,
            "success_rate_trend": {
                "change": success_rate_trend,
                "direction": "improving"
                if success_rate_trend > 0
                else "declining"
                if success_rate_trend < 0
                else "stable",
                "first_period": first_stats["success_rate"],
                "second_period": second_stats["success_rate"],
            },
            "duration_trend": {
                "change": duration_trend,
                "direction": "improving"
                if duration_trend < 0
                else "declining"
                if duration_trend > 0
                else "stable",
                "first_period": first_stats["avg_duration"],
                "second_period": second_stats["avg_duration"],
            },
            "performance_trend": {
                "change": performance_trend,
                "direction": "improving"
                if performance_trend > 0
                else "declining"
                if performance_trend < 0
                else "stable",
                "first_period": first_stats["avg_performance_score"],
                "second_period": second_stats["avg_performance_score"],
            },
        }

    def generate_dashboard_report(self, days: int = 7) -> Dict:
        """Generate comprehensive dashboard report."""
        print(f"📊 Generating monitoring dashboard for last {days} days...")

        # Load data
        performance_data = self.load_performance_data(days)
        alert_data = self.load_alert_data(days)

        print(f"   Loaded {len(performance_data)} performance records")
        print(f"   Loaded {len(alert_data)} alerts")

        # Calculate statistics
        stats = self.calculate_workflow_statistics(performance_data)
        health_score, health_status = self.calculate_system_health_score(stats, alert_data)
        trends = self.generate_performance_trends(performance_data)

        # Generate report
        report = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "repository": self.repo,
                "analysis_period_days": days,
                "data_points": len(performance_data),
                "alert_count": len(alert_data),
            },
            "system_health": {
                "score": health_score,
                "status": health_status,
                "assessment": self._get_health_assessment(health_status, health_score),
            },
            "performance_statistics": stats,
            "trends": trends,
            "alerts_summary": self._summarize_alerts(alert_data),
            "recommendations": self._generate_dashboard_recommendations(
                stats, health_status, trends, alert_data
            ),
        }

        return report

    def _get_health_assessment(self, status: str, score: int) -> str:
        """Get health assessment message."""
        assessments = {
            "excellent": f"System health is excellent ({score}/100). All workflows performing optimally.",
            "good": f"System health is good ({score}/100). Minor optimization opportunities available.",
            "acceptable": f"System health is acceptable ({score}/100). Some performance issues need attention.",
            "poor": f"System health is poor ({score}/100). Immediate action required to address performance issues.",
        }

        return assessments.get(status, f"System health status unknown ({score}/100).")

    def _summarize_alerts(self, alerts: List[Dict]) -> Dict:
        """Summarize alert data."""
        if not alerts:
            return {
                "total_alerts": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "info_alerts": 0,
                "most_common_issues": [],
            }

        # Count alerts by severity
        severity_counts = defaultdict(int)
        for alert in alerts:
            severity_counts[alert["severity"]] += 1

        # Find most common issues
        all_conditions = []
        for alert in alerts:
            all_conditions.extend(alert.get("conditions", []))

        condition_counts = defaultdict(int)
        for condition in all_conditions:
            condition_counts[condition] += 1

        most_common = sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_alerts": len(alerts),
            "critical_alerts": severity_counts["critical"],
            "warning_alerts": severity_counts["warning"],
            "info_alerts": severity_counts["info"],
            "most_common_issues": [
                {"issue": issue, "count": count} for issue, count in most_common
            ],
        }

    def _generate_dashboard_recommendations(
        self, stats: Dict, health_status: str, trends: Dict, alerts: List[Dict]
    ) -> List[str]:
        """Generate dashboard-level recommendations."""
        recommendations = []

        # Health-based recommendations
        if health_status == "poor":
            recommendations.extend(
                [
                    "🚨 CRITICAL: Immediate action required to address system health issues",
                    "Review and resolve all critical alerts",
                    "Implement emergency performance optimizations",
                    "Consider workflow architecture review",
                ]
            )
        elif health_status == "acceptable":
            recommendations.extend(
                [
                    "⚠️ Address performance degradation issues",
                    "Optimize workflows with high failure rates",
                    "Implement proactive monitoring measures",
                ]
            )

        # Failure rate recommendations
        if stats["failure_rate"] > 10:
            recommendations.append(
                f"🔧 High failure rate ({stats['failure_rate']:.1f}%) - investigate root causes"
            )

        # Performance recommendations
        if stats["avg_performance_score"] < 75:
            recommendations.append(
                f"⚡ Low performance score ({stats['avg_performance_score']:.1f}) - optimize execution times"
            )

        # Trend-based recommendations
        if trends.get("trend_available"):
            if trends["success_rate_trend"]["direction"] == "declining":
                recommendations.append("📉 Success rate declining - investigate recent changes")

            if trends["duration_trend"]["direction"] == "declining":
                recommendations.append(
                    "⏱️ Execution times increasing - review performance optimizations"
                )

        # Alert-based recommendations
        critical_alerts = sum(1 for alert in alerts if alert["severity"] == "critical")
        if critical_alerts > 0:
            recommendations.append(
                f"🚨 {critical_alerts} critical alerts require immediate attention"
            )

        # Workflow-specific recommendations
        for workflow, workflow_stats in stats["workflows"].items():
            if workflow_stats["failure_rate"] > 15:
                recommendations.append(
                    f"🔧 {workflow} has high failure rate ({workflow_stats['failure_rate']:.1f}%)"
                )

            if workflow_stats["avg_duration"] > 600:  # 10 minutes
                recommendations.append(
                    f"⚡ {workflow} has long execution time ({workflow_stats['avg_duration'] / 60:.1f}m)"
                )

        # Default recommendations if none generated
        if not recommendations:
            recommendations.extend(
                [
                    "✅ System performing well - continue monitoring",
                    "📈 Look for micro-optimization opportunities",
                    "🔍 Monitor for performance regressions",
                ]
            )

        return recommendations

    def print_dashboard(self, report: Dict):
        """Print formatted dashboard to console."""
        print("\n" + "=" * 80)
        print("📊 WORKFLOW MONITORING DASHBOARD")
        print("=" * 80)

        metadata = report["metadata"]
        print(f"Repository: {metadata['repository']}")
        print(f"Analysis Period: {metadata['analysis_period_days']} days")
        print(f"Generated: {metadata['generated_at']}")
        print(
            f"Data Points: {metadata['data_points']} performance records, {metadata['alert_count']} alerts"
        )

        # System Health
        health = report["system_health"]
        print(f"\n🏥 SYSTEM HEALTH: {health['status'].upper()} ({health['score']}/100)")
        print(f"   {health['assessment']}")

        # Performance Statistics
        stats = report["performance_statistics"]
        print("\n📈 PERFORMANCE STATISTICS")
        print(f"   Total Workflow Runs: {stats['total_runs']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Failure Rate: {stats['failure_rate']:.1f}%")
        print(f"   Average Duration: {stats['avg_duration'] / 60:.1f} minutes")
        print(f"   Average Performance Score: {stats['avg_performance_score']:.1f}/100")

        # Workflow Breakdown
        if stats["workflows"]:
            print("\n🔧 WORKFLOW BREAKDOWN")
            for workflow, workflow_stats in stats["workflows"].items():
                print(f"   {workflow}:")
                print(f"     Runs: {workflow_stats['total_runs']}")
                print(f"     Success Rate: {workflow_stats['success_rate']:.1f}%")
                print(f"     Avg Duration: {workflow_stats['avg_duration'] / 60:.1f}m")
                print(f"     Performance Score: {workflow_stats['avg_performance_score']:.1f}/100")

        # Trends
        trends = report["trends"]
        if trends.get("trend_available"):
            print("\n📊 PERFORMANCE TRENDS")

            success_trend = trends["success_rate_trend"]
            print(
                f"   Success Rate: {success_trend['direction']} ({success_trend['change']:+.1f}%)"
            )

            duration_trend = trends["duration_trend"]
            print(f"   Duration: {duration_trend['direction']} ({duration_trend['change']:+.1f}s)")

            perf_trend = trends["performance_trend"]
            print(f"   Performance Score: {perf_trend['direction']} ({perf_trend['change']:+.1f})")

        # Alerts Summary
        alerts = report["alerts_summary"]
        if alerts["total_alerts"] > 0:
            print("\n🚨 ALERTS SUMMARY")
            print(f"   Total Alerts: {alerts['total_alerts']}")
            print(f"   Critical: {alerts['critical_alerts']}")
            print(f"   Warning: {alerts['warning_alerts']}")
            print(f"   Info: {alerts['info_alerts']}")

            if alerts["most_common_issues"]:
                print("   Most Common Issues:")
                for issue in alerts["most_common_issues"][:3]:
                    print(f"     - {issue['issue']} ({issue['count']} times)")

        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print("\n💡 RECOMMENDATIONS")
            for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
                print(f"   {i}. {rec}")

        print("\n" + "=" * 80)

    def save_dashboard_report(self, report: Dict, output_file: str = None) -> str:
        """Save dashboard report to file."""
        if output_file is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"monitoring_dashboard_{timestamp}.json"

        output_path = os.path.join(self.monitoring_dir, output_file)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Generate Workflow Monitoring Dashboard")
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--monitoring-dir",
        default="monitoring-results",
        help="Directory containing monitoring data",
    )
    parser.add_argument("--output-file", help="Output file for dashboard report (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")

    args = parser.parse_args()

    try:
        # Initialize dashboard
        dashboard = MonitoringDashboard(args.monitoring_dir)

        # Generate report
        report = dashboard.generate_dashboard_report(args.days)

        # Print dashboard unless quiet mode
        if not args.quiet:
            dashboard.print_dashboard(report)

        # Save report if output file specified
        if args.output_file:
            output_path = dashboard.save_dashboard_report(report, args.output_file)
            print(f"\n✅ Dashboard report saved to: {output_path}")

        # Exit with appropriate code based on system health
        health_status = report["system_health"]["status"]
        if health_status == "poor":
            sys.exit(2)  # Critical issues
        elif health_status == "acceptable":
            sys.exit(1)  # Warning issues
        else:
            sys.exit(0)  # All good

    except Exception as e:
        print(f"❌ Error generating monitoring dashboard: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

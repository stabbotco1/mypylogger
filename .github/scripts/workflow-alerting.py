#!/usr/bin/env python3
"""Automated Workflow Alerting System

This script provides automated alerting for workflow performance degradation,
failure rate increases, and system health issues.

Requirements Addressed:
- 7.2: Add automated alerts for workflow performance degradation
- 7.3: Create periodic workflow health reports
- 7.4: Track workflow success rates and execution times
"""

import argparse
from datetime import datetime, timedelta
import glob
import json
import os
import statistics
import sys
from typing import Dict, List, Tuple


class WorkflowAlerting:
    """Automated workflow alerting and notification system."""

    def __init__(self, monitoring_dir: str = "monitoring-results"):
        """Initialize the alerting system."""
        self.monitoring_dir = monitoring_dir
        self.repo = os.getenv("GITHUB_REPOSITORY", "unknown/unknown")
        self.github_token = os.getenv("GITHUB_TOKEN")

        # Alert thresholds
        self.thresholds = {
            "failure_rate_warning": 5.0,  # 5% failure rate
            "failure_rate_critical": 10.0,  # 10% failure rate
            "duration_increase_warning": 20.0,  # 20% increase
            "duration_increase_critical": 50.0,  # 50% increase
            "performance_score_warning": 75,  # Performance score below 75
            "performance_score_critical": 50,  # Performance score below 50
            "consecutive_failures": 3,  # 3 consecutive failures
            "cache_hit_rate_warning": 80.0,  # Cache hit rate below 80%
        }

        # Alert cooldown periods (in hours)
        self.cooldown_periods = {
            "critical": 1,  # 1 hour for critical alerts
            "warning": 6,  # 6 hours for warning alerts
            "info": 24,  # 24 hours for info alerts
        }

    def load_recent_performance_data(self, hours: int = 24) -> List[Dict]:
        """Load performance data from the last N hours."""
        performance_files = glob.glob(os.path.join(self.monitoring_dir, "performance_*.json"))

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_data = []

        for file_path in performance_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by time
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_time:
                    recent_data.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue

        # Sort by timestamp
        recent_data.sort(key=lambda x: x["timestamp"])
        return recent_data

    def load_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Load recent alerts to check for cooldown periods."""
        alert_files = glob.glob(os.path.join(self.monitoring_dir, "alert_*.json"))

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_alerts = []

        for file_path in alert_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by time
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_time:
                    recent_alerts.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse alert file {file_path}: {e}")
                continue

        return recent_alerts

    def check_failure_rate_alerts(self, performance_data: List[Dict]) -> List[Dict]:
        """Check for failure rate alerts."""
        alerts = []

        if not performance_data:
            return alerts

        # Calculate overall failure rate
        total_runs = len(performance_data)
        failed_runs = sum(1 for run in performance_data if run["status"] != "success")
        failure_rate = (failed_runs / total_runs) * 100

        # Check thresholds
        if failure_rate >= self.thresholds["failure_rate_critical"]:
            alerts.append(
                {
                    "type": "failure_rate",
                    "severity": "critical",
                    "title": f"Critical Failure Rate Alert: {failure_rate:.1f}%",
                    "description": f"Workflow failure rate ({failure_rate:.1f}%) exceeds critical threshold ({self.thresholds['failure_rate_critical']}%)",
                    "metrics": {
                        "failure_rate": failure_rate,
                        "failed_runs": failed_runs,
                        "total_runs": total_runs,
                        "threshold": self.thresholds["failure_rate_critical"],
                    },
                    "recommendations": [
                        "Investigate root causes of recent failures",
                        "Review error logs and failure patterns",
                        "Implement immediate failure prevention measures",
                        "Consider rolling back recent changes",
                    ],
                }
            )
        elif failure_rate >= self.thresholds["failure_rate_warning"]:
            alerts.append(
                {
                    "type": "failure_rate",
                    "severity": "warning",
                    "title": f"Failure Rate Warning: {failure_rate:.1f}%",
                    "description": f"Workflow failure rate ({failure_rate:.1f}%) exceeds warning threshold ({self.thresholds['failure_rate_warning']}%)",
                    "metrics": {
                        "failure_rate": failure_rate,
                        "failed_runs": failed_runs,
                        "total_runs": total_runs,
                        "threshold": self.thresholds["failure_rate_warning"],
                    },
                    "recommendations": [
                        "Monitor failure trends closely",
                        "Review recent workflow changes",
                        "Implement proactive failure prevention",
                        "Enhance error handling and recovery",
                    ],
                }
            )

        # Check for consecutive failures
        consecutive_failures = 0
        max_consecutive = 0

        for run in reversed(performance_data):  # Check most recent first
            if run["status"] != "success":
                consecutive_failures += 1
                max_consecutive = max(max_consecutive, consecutive_failures)
            else:
                break

        if consecutive_failures >= self.thresholds["consecutive_failures"]:
            alerts.append(
                {
                    "type": "consecutive_failures",
                    "severity": "critical",
                    "title": f"Consecutive Failures Alert: {consecutive_failures} in a row",
                    "description": f"{consecutive_failures} consecutive workflow failures detected",
                    "metrics": {
                        "consecutive_failures": consecutive_failures,
                        "threshold": self.thresholds["consecutive_failures"],
                    },
                    "recommendations": [
                        "Immediate investigation required",
                        "Stop deployments until resolved",
                        "Review recent code changes",
                        "Check infrastructure status",
                    ],
                }
            )

        return alerts

    def check_performance_degradation_alerts(self, performance_data: List[Dict]) -> List[Dict]:
        """Check for performance degradation alerts."""
        alerts = []

        if len(performance_data) < 10:  # Need sufficient data for trend analysis
            return alerts

        # Split data into two periods for comparison
        mid_point = len(performance_data) // 2
        earlier_period = performance_data[:mid_point]
        recent_period = performance_data[mid_point:]

        # Calculate average durations for each period
        earlier_durations = [run["duration_seconds"] for run in earlier_period]
        recent_durations = [run["duration_seconds"] for run in recent_period]

        if not earlier_durations or not recent_durations:
            return alerts

        earlier_avg = statistics.mean(earlier_durations)
        recent_avg = statistics.mean(recent_durations)

        # Calculate percentage increase
        if earlier_avg > 0:
            duration_increase = ((recent_avg - earlier_avg) / earlier_avg) * 100

            if duration_increase >= self.thresholds["duration_increase_critical"]:
                alerts.append(
                    {
                        "type": "performance_degradation",
                        "severity": "critical",
                        "title": f"Critical Performance Degradation: +{duration_increase:.1f}%",
                        "description": f"Workflow execution time increased by {duration_increase:.1f}% (from {earlier_avg:.0f}s to {recent_avg:.0f}s)",
                        "metrics": {
                            "duration_increase_percent": duration_increase,
                            "earlier_avg_duration": earlier_avg,
                            "recent_avg_duration": recent_avg,
                            "threshold": self.thresholds["duration_increase_critical"],
                        },
                        "recommendations": [
                            "Investigate performance bottlenecks immediately",
                            "Review recent infrastructure changes",
                            "Check for resource constraints",
                            "Optimize critical workflow paths",
                        ],
                    }
                )
            elif duration_increase >= self.thresholds["duration_increase_warning"]:
                alerts.append(
                    {
                        "type": "performance_degradation",
                        "severity": "warning",
                        "title": f"Performance Degradation Warning: +{duration_increase:.1f}%",
                        "description": f"Workflow execution time increased by {duration_increase:.1f}% (from {earlier_avg:.0f}s to {recent_avg:.0f}s)",
                        "metrics": {
                            "duration_increase_percent": duration_increase,
                            "earlier_avg_duration": earlier_avg,
                            "recent_avg_duration": recent_avg,
                            "threshold": self.thresholds["duration_increase_warning"],
                        },
                        "recommendations": [
                            "Monitor performance trends",
                            "Review caching effectiveness",
                            "Consider workflow optimizations",
                            "Check for gradual resource degradation",
                        ],
                    }
                )

        # Check performance scores
        recent_scores = [
            run["performance_score"] for run in recent_period if "performance_score" in run
        ]
        if recent_scores:
            avg_score = statistics.mean(recent_scores)

            if avg_score < self.thresholds["performance_score_critical"]:
                alerts.append(
                    {
                        "type": "low_performance_score",
                        "severity": "critical",
                        "title": f"Critical Performance Score: {avg_score:.1f}/100",
                        "description": f"Average performance score ({avg_score:.1f}) is critically low",
                        "metrics": {
                            "avg_performance_score": avg_score,
                            "threshold": self.thresholds["performance_score_critical"],
                        },
                        "recommendations": [
                            "Immediate performance optimization required",
                            "Review all workflow components",
                            "Implement emergency performance fixes",
                            "Consider infrastructure upgrades",
                        ],
                    }
                )
            elif avg_score < self.thresholds["performance_score_warning"]:
                alerts.append(
                    {
                        "type": "low_performance_score",
                        "severity": "warning",
                        "title": f"Low Performance Score: {avg_score:.1f}/100",
                        "description": f"Average performance score ({avg_score:.1f}) is below optimal",
                        "metrics": {
                            "avg_performance_score": avg_score,
                            "threshold": self.thresholds["performance_score_warning"],
                        },
                        "recommendations": [
                            "Optimize workflow performance",
                            "Review caching strategies",
                            "Improve resource utilization",
                            "Monitor performance trends",
                        ],
                    }
                )

        return alerts

    def check_cache_performance_alerts(self, performance_data: List[Dict]) -> List[Dict]:
        """Check for cache performance alerts."""
        alerts = []

        # Get recent runs with cache hit rate data
        recent_cache_data = [
            run
            for run in performance_data[-10:]  # Last 10 runs
            if "cache_hit_rate" in run and run["cache_hit_rate"] is not None
        ]

        if not recent_cache_data:
            return alerts

        # Calculate average cache hit rate
        cache_rates = [run["cache_hit_rate"] for run in recent_cache_data]
        avg_cache_rate = statistics.mean(cache_rates)

        if avg_cache_rate < self.thresholds["cache_hit_rate_warning"]:
            alerts.append(
                {
                    "type": "low_cache_performance",
                    "severity": "warning",
                    "title": f"Low Cache Hit Rate: {avg_cache_rate:.1f}%",
                    "description": f"Average cache hit rate ({avg_cache_rate:.1f}%) is below optimal threshold",
                    "metrics": {
                        "avg_cache_hit_rate": avg_cache_rate,
                        "threshold": self.thresholds["cache_hit_rate_warning"],
                        "sample_size": len(recent_cache_data),
                    },
                    "recommendations": [
                        "Review cache key strategies",
                        "Optimize cache retention policies",
                        "Check for cache invalidation issues",
                        "Implement multi-level caching",
                    ],
                }
            )

        return alerts

    def check_alert_cooldown(self, alert: Dict, recent_alerts: List[Dict]) -> bool:
        """Check if alert is in cooldown period."""
        alert_type = alert["type"]
        severity = alert["severity"]
        cooldown_hours = self.cooldown_periods.get(severity, 24)

        cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)

        # Check for similar recent alerts
        for recent_alert in recent_alerts:
            if recent_alert.get("type") == alert_type and recent_alert.get("severity") == severity:
                alert_time = datetime.fromisoformat(
                    recent_alert["timestamp"].replace("Z", "+00:00")
                )

                if alert_time >= cutoff_time:
                    return True  # Still in cooldown

        return False  # Not in cooldown

    def generate_alerts(self, hours: int = 24) -> List[Dict]:
        """Generate all applicable alerts."""
        print(f"🔍 Checking for alerts in the last {hours} hours...")

        # Load data
        performance_data = self.load_recent_performance_data(hours)
        recent_alerts = self.load_recent_alerts(hours * 2)  # Check longer period for cooldown

        print(f"   Loaded {len(performance_data)} performance records")
        print(f"   Found {len(recent_alerts)} recent alerts")

        all_alerts = []

        # Check different alert types
        failure_alerts = self.check_failure_rate_alerts(performance_data)
        performance_alerts = self.check_performance_degradation_alerts(performance_data)
        cache_alerts = self.check_cache_performance_alerts(performance_data)

        # Combine all alerts
        all_alerts.extend(failure_alerts)
        all_alerts.extend(performance_alerts)
        all_alerts.extend(cache_alerts)

        # Filter out alerts in cooldown period
        active_alerts = []
        for alert in all_alerts:
            if not self.check_alert_cooldown(alert, recent_alerts):
                active_alerts.append(alert)
            else:
                print(f"   Skipping {alert['type']} alert (in cooldown period)")

        # Add metadata to alerts
        for alert in active_alerts:
            alert.update(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "repository": self.repo,
                    "analysis_period_hours": hours,
                    "data_points": len(performance_data),
                }
            )

        print(f"✅ Generated {len(active_alerts)} active alerts")
        return active_alerts

    def save_alerts(self, alerts: List[Dict]) -> List[str]:
        """Save alerts to files."""
        saved_files = []

        for alert in alerts:
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            alert_type = alert["type"].replace("_", "-")
            severity = alert["severity"]
            filename = f"alert_{severity}_{alert_type}_{timestamp}.json"
            filepath = os.path.join(self.monitoring_dir, filename)

            # Save alert
            os.makedirs(self.monitoring_dir, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(alert, f, indent=2)

            saved_files.append(filepath)

        return saved_files

    def format_alert_for_github_issue(self, alert: Dict) -> Tuple[str, str]:
        """Format alert for GitHub issue creation."""
        severity_emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}

        title = f"{severity_emoji.get(alert['severity'], '🔔')} {alert['title']}"

        body = f"""## {alert["title"]}

**Severity**: {alert["severity"].upper()}
**Type**: {alert["type"].replace("_", " ").title()}
**Timestamp**: {alert["timestamp"]}
**Repository**: {alert["repository"]}

### Description
{alert["description"]}

### Metrics
"""

        # Add metrics
        for key, value in alert.get("metrics", {}).items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, float):
                body += f"- **{formatted_key}**: {value:.2f}\n"
            else:
                body += f"- **{formatted_key}**: {value}\n"

        # Add recommendations
        recommendations = alert.get("recommendations", [])
        if recommendations:
            body += "\n### Recommended Actions\n"
            for i, rec in enumerate(recommendations, 1):
                body += f"{i}. {rec}\n"

        body += f"""
### Analysis Details
- **Analysis Period**: {alert["analysis_period_hours"]} hours
- **Data Points**: {alert["data_points"]} workflow runs

---
*This alert was automatically generated by the Workflow Monitoring System*
*Alert ID*: `{alert["type"]}_{alert["severity"]}_{alert["timestamp"]}`
"""

        return title, body


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Automated Workflow Alerting System")
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours of data to analyze (default: 24)"
    )
    parser.add_argument(
        "--monitoring-dir",
        default="monitoring-results",
        help="Directory containing monitoring data",
    )
    parser.add_argument("--save-alerts", action="store_true", help="Save generated alerts to files")
    parser.add_argument(
        "--create-github-issues",
        action="store_true",
        help="Create GitHub issues for critical alerts",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without taking action"
    )

    args = parser.parse_args()

    try:
        # Initialize alerting system
        alerting = WorkflowAlerting(args.monitoring_dir)

        # Generate alerts
        alerts = alerting.generate_alerts(args.hours)

        if not alerts:
            print("✅ No alerts generated - all systems operating normally")
            return

        # Display alerts
        print(f"\n🚨 GENERATED ALERTS ({len(alerts)})")
        print("=" * 60)

        for i, alert in enumerate(alerts, 1):
            print(f"\n{i}. {alert['title']}")
            print(f"   Severity: {alert['severity'].upper()}")
            print(f"   Type: {alert['type']}")
            print(f"   Description: {alert['description']}")

            if alert.get("recommendations"):
                print(f"   Recommendations: {len(alert['recommendations'])} actions")

        # Save alerts if requested
        if args.save_alerts and not args.dry_run:
            saved_files = alerting.save_alerts(alerts)
            print(f"\n💾 Saved {len(saved_files)} alert files:")
            for file_path in saved_files:
                print(f"   - {file_path}")

        # Create GitHub issues for critical alerts
        critical_alerts = [alert for alert in alerts if alert["severity"] == "critical"]
        if args.create_github_issues and critical_alerts and not args.dry_run:
            print(f"\n📝 Would create {len(critical_alerts)} GitHub issues for critical alerts")
            # Note: Actual GitHub issue creation would require GitHub API integration
            for alert in critical_alerts:
                title, body = alerting.format_alert_for_github_issue(alert)
                print(f"   Issue: {title}")

        if args.dry_run:
            print("\n🔍 DRY RUN - No actions taken")

        # Exit with appropriate code
        if any(alert["severity"] == "critical" for alert in alerts):
            sys.exit(2)  # Critical alerts
        elif any(alert["severity"] == "warning" for alert in alerts):
            sys.exit(1)  # Warning alerts
        else:
            sys.exit(0)  # Info alerts only

    except Exception as e:
        print(f"❌ Error in workflow alerting: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

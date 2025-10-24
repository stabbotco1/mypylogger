#!/usr/bin/env python3
"""Predictive Failure Detection System

This script implements predictive failure detection based on historical data,
workflow trend analysis, and proactive alerting for potential workflow issues.

Requirements Addressed:
- 7.5: Add predictive failure detection based on historical data
- 7.5: Implement workflow trend analysis and reporting
- 7.5: Add proactive alerting for potential workflow issues
- 7.5: Create workflow performance dashboards
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import glob
import json
import math
import os
import statistics
import sys
from typing import Dict, List


class PredictiveFailureDetection:
    """Predictive failure detection and trend analysis system."""

    def __init__(self, monitoring_dir: str = "monitoring-results"):
        """Initialize the predictive failure detection system."""
        self.monitoring_dir = monitoring_dir
        self.repo = os.getenv("GITHUB_REPOSITORY", "unknown/unknown")

        # Prediction thresholds and parameters
        self.prediction_config = {
            "min_data_points": 20,  # Minimum data points for reliable prediction
            "trend_window_days": 14,  # Days to analyze for trend detection
            "prediction_horizon_days": 7,  # Days to predict ahead
            "failure_rate_trend_threshold": 2.0,  # % increase that triggers alert
            "duration_trend_threshold": 10.0,  # % increase that triggers alert
            "performance_degradation_threshold": 5.0,  # Performance score decrease
            "confidence_threshold": 0.7,  # Minimum confidence for predictions
        }

        # Risk levels
        self.risk_levels = {
            "low": {"score": 0.3, "color": "🟢", "action": "monitor"},
            "medium": {"score": 0.6, "color": "🟡", "action": "investigate"},
            "high": {"score": 0.8, "color": "🟠", "action": "prepare"},
            "critical": {"score": 1.0, "color": "🔴", "action": "immediate"},
        }

    def load_historical_data(self, days: int = 30) -> List[Dict]:
        """Load historical performance data for analysis."""
        performance_files = glob.glob(os.path.join(self.monitoring_dir, "performance_*.json"))

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        historical_data = []

        for file_path in performance_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by date
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_date:
                    # Add parsed timestamp for easier processing
                    data["parsed_timestamp"] = timestamp
                    historical_data.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue

        # Sort by timestamp
        historical_data.sort(key=lambda x: x["parsed_timestamp"])
        return historical_data

    def calculate_trend_metrics(self, data: List[Dict], metric_key: str) -> Dict:
        """Calculate trend metrics for a specific data series."""
        if len(data) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0.0,
                "correlation": 0.0,
                "confidence": 0.0,
                "prediction": None,
            }

        # Extract time series data
        timestamps = [
            (d["parsed_timestamp"] - data[0]["parsed_timestamp"]).total_seconds() for d in data
        ]
        values = []

        for d in data:
            if metric_key in d:
                values.append(d[metric_key])
            elif metric_key == "failure_rate":
                # Calculate failure rate from status
                values.append(0.0 if d.get("status") == "success" else 100.0)
            else:
                values.append(0.0)

        if len(values) < 2:
            return {
                "trend": "insufficient_data",
                "slope": 0.0,
                "correlation": 0.0,
                "confidence": 0.0,
                "prediction": None,
            }

        # Calculate linear regression
        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        sum_y2 = sum(y * y for y in values)

        # Calculate slope and correlation
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0.0
            correlation = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator

            # Calculate correlation coefficient
            numerator = n * sum_xy - sum_x * sum_y
            denom_r = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
            correlation = numerator / denom_r if denom_r != 0 else 0.0

        # Determine trend direction
        if abs(slope) < 0.001:  # Very small slope
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        # Calculate confidence based on correlation strength and data points
        confidence = min(abs(correlation) * (min(n, 30) / 30), 1.0)

        # Make prediction for next period
        if confidence >= self.prediction_config["confidence_threshold"]:
            # Predict value for prediction horizon
            future_time = timestamps[-1] + (
                self.prediction_config["prediction_horizon_days"] * 24 * 3600
            )
            intercept = (sum_y - slope * sum_x) / n
            predicted_value = slope * future_time + intercept

            prediction = {
                "value": max(0, predicted_value),  # Ensure non-negative
                "confidence": confidence,
                "horizon_days": self.prediction_config["prediction_horizon_days"],
            }
        else:
            prediction = None

        return {
            "trend": trend,
            "slope": slope,
            "correlation": correlation,
            "confidence": confidence,
            "prediction": prediction,
            "current_value": values[-1] if values else 0,
            "data_points": n,
        }

    def analyze_failure_patterns(self, data: List[Dict]) -> Dict:
        """Analyze failure patterns and predict failure likelihood."""
        # Group data by time periods
        daily_data = defaultdict(list)
        for d in data:
            date_key = d["parsed_timestamp"].date()
            daily_data[date_key].append(d)

        # Calculate daily failure rates
        daily_failure_rates = []
        for date, day_data in daily_data.items():
            failures = sum(1 for d in day_data if d.get("status") != "success")
            total = len(day_data)
            failure_rate = (failures / total) * 100 if total > 0 else 0
            daily_failure_rates.append(
                {
                    "date": date,
                    "failure_rate": failure_rate,
                    "total_runs": total,
                    "failures": failures,
                    "parsed_timestamp": datetime.combine(date, datetime.min.time()),
                }
            )

        # Sort by date
        daily_failure_rates.sort(key=lambda x: x["date"])

        # Calculate trend for failure rates
        failure_trend = self.calculate_trend_metrics(daily_failure_rates, "failure_rate")

        # Analyze failure patterns
        failure_patterns = self._analyze_failure_patterns_detailed(data)

        # Calculate failure risk score
        risk_score = self._calculate_failure_risk_score(failure_trend, failure_patterns, data)

        return {
            "failure_trend": failure_trend,
            "failure_patterns": failure_patterns,
            "risk_assessment": self._assess_risk_level(risk_score),
            "daily_failure_rates": daily_failure_rates[-7:],  # Last 7 days
            "predictions": self._generate_failure_predictions(failure_trend, failure_patterns),
        }

    def analyze_performance_trends(self, data: List[Dict]) -> Dict:
        """Analyze performance trends and predict degradation."""
        # Analyze duration trends
        duration_trend = self.calculate_trend_metrics(data, "duration_seconds")

        # Analyze performance score trends
        performance_trend = self.calculate_trend_metrics(data, "performance_score")

        # Analyze cache performance trends
        cache_data = [d for d in data if "cache_hit_rate" in d and d["cache_hit_rate"] is not None]
        cache_trend = self.calculate_trend_metrics(cache_data, "cache_hit_rate")

        # Calculate performance risk
        performance_risk = self._calculate_performance_risk_score(
            duration_trend, performance_trend, cache_trend
        )

        return {
            "duration_trend": duration_trend,
            "performance_score_trend": performance_trend,
            "cache_performance_trend": cache_trend,
            "risk_assessment": self._assess_risk_level(performance_risk),
            "predictions": self._generate_performance_predictions(
                duration_trend, performance_trend, cache_trend
            ),
        }

    def _analyze_failure_patterns_detailed(self, data: List[Dict]) -> Dict:
        """Analyze detailed failure patterns."""
        failures = [d for d in data if d.get("status") != "success"]

        if not failures:
            return {
                "total_failures": 0,
                "failure_types": {},
                "time_patterns": {},
                "consecutive_failures": 0,
                "failure_clustering": "none",
            }

        # Analyze failure types (if available in data)
        failure_types = defaultdict(int)
        for failure in failures:
            failure_type = failure.get("failure_type", "unknown")
            failure_types[failure_type] += 1

        # Analyze time patterns
        hour_failures = defaultdict(int)
        day_failures = defaultdict(int)

        for failure in failures:
            hour = failure["parsed_timestamp"].hour
            day = failure["parsed_timestamp"].strftime("%A")
            hour_failures[hour] += 1
            day_failures[day] += 1

        # Check for consecutive failures
        consecutive_count = 0
        max_consecutive = 0

        for d in reversed(data):  # Check from most recent
            if d.get("status") != "success":
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                break

        # Analyze failure clustering
        failure_clustering = self._analyze_failure_clustering(failures)

        return {
            "total_failures": len(failures),
            "failure_types": dict(failure_types),
            "time_patterns": {"by_hour": dict(hour_failures), "by_day": dict(day_failures)},
            "consecutive_failures": consecutive_count,
            "max_consecutive_failures": max_consecutive,
            "failure_clustering": failure_clustering,
        }

    def _analyze_failure_clustering(self, failures: List[Dict]) -> str:
        """Analyze if failures are clustered in time."""
        if len(failures) < 3:
            return "insufficient_data"

        # Calculate time gaps between failures
        time_gaps = []
        for i in range(1, len(failures)):
            gap = (
                failures[i]["parsed_timestamp"] - failures[i - 1]["parsed_timestamp"]
            ).total_seconds()
            time_gaps.append(gap)

        if not time_gaps:
            return "none"

        # Analyze gap distribution
        avg_gap = statistics.mean(time_gaps)
        std_gap = statistics.stdev(time_gaps) if len(time_gaps) > 1 else 0

        # Check for clustering (many short gaps)
        short_gaps = sum(1 for gap in time_gaps if gap < avg_gap / 2)
        clustering_ratio = short_gaps / len(time_gaps)

        if clustering_ratio > 0.6:
            return "high_clustering"
        if clustering_ratio > 0.3:
            return "moderate_clustering"
        return "low_clustering"

    def _calculate_failure_risk_score(
        self, failure_trend: Dict, failure_patterns: Dict, data: List[Dict]
    ) -> float:
        """Calculate overall failure risk score."""
        risk_score = 0.0

        # Trend-based risk
        if failure_trend["trend"] == "increasing" and failure_trend["confidence"] > 0.5:
            risk_score += 0.3 * failure_trend["confidence"]

        # Pattern-based risk
        consecutive_failures = failure_patterns["consecutive_failures"]
        if consecutive_failures >= 3:
            risk_score += 0.4
        elif consecutive_failures >= 2:
            risk_score += 0.2

        # Clustering-based risk
        clustering = failure_patterns["failure_clustering"]
        if clustering == "high_clustering":
            risk_score += 0.2
        elif clustering == "moderate_clustering":
            risk_score += 0.1

        # Recent failure rate
        recent_data = data[-10:] if len(data) >= 10 else data
        recent_failures = sum(1 for d in recent_data if d.get("status") != "success")
        recent_failure_rate = recent_failures / len(recent_data) if recent_data else 0

        if recent_failure_rate > 0.2:  # 20% failure rate
            risk_score += 0.3
        elif recent_failure_rate > 0.1:  # 10% failure rate
            risk_score += 0.15

        return min(risk_score, 1.0)

    def _calculate_performance_risk_score(
        self, duration_trend: Dict, performance_trend: Dict, cache_trend: Dict
    ) -> float:
        """Calculate performance degradation risk score."""
        risk_score = 0.0

        # Duration trend risk
        if (
            duration_trend["trend"] == "increasing"
            and duration_trend["confidence"] > 0.5
            and duration_trend["slope"] > 0
        ):
            risk_score += 0.4 * duration_trend["confidence"]

        # Performance score trend risk
        if (
            performance_trend["trend"] == "decreasing"
            and performance_trend["confidence"] > 0.5
            and performance_trend["slope"] < 0
        ):
            risk_score += 0.3 * performance_trend["confidence"]

        # Cache performance risk
        if (
            cache_trend["trend"] == "decreasing"
            and cache_trend["confidence"] > 0.5
            and cache_trend["current_value"] < 80
        ):
            risk_score += 0.2 * cache_trend["confidence"]

        # Current performance level risk
        current_perf = performance_trend.get("current_value", 100)
        if current_perf < 60:
            risk_score += 0.3
        elif current_perf < 75:
            risk_score += 0.15

        return min(risk_score, 1.0)

    def _assess_risk_level(self, risk_score: float) -> Dict:
        """Assess risk level based on score."""
        for level, config in reversed(list(self.risk_levels.items())):
            if risk_score >= config["score"]:
                return {
                    "level": level,
                    "score": risk_score,
                    "color": config["color"],
                    "recommended_action": config["action"],
                    "description": self._get_risk_description(level, risk_score),
                }

        return {
            "level": "low",
            "score": risk_score,
            "color": "🟢",
            "recommended_action": "monitor",
            "description": "Low risk - continue normal monitoring",
        }

    def _get_risk_description(self, level: str, score: float) -> str:
        """Get risk level description."""
        descriptions = {
            "low": f"Low risk ({score:.2f}) - System operating normally",
            "medium": f"Medium risk ({score:.2f}) - Monitor trends closely",
            "high": f"High risk ({score:.2f}) - Proactive measures recommended",
            "critical": f"Critical risk ({score:.2f}) - Immediate attention required",
        }

        return descriptions.get(level, f"Unknown risk level ({score:.2f})")

    def _generate_failure_predictions(
        self, failure_trend: Dict, failure_patterns: Dict
    ) -> List[Dict]:
        """Generate failure predictions."""
        predictions = []

        # Trend-based prediction
        if failure_trend.get("prediction") and failure_trend["confidence"] > 0.6:
            predicted_rate = failure_trend["prediction"]["value"]

            predictions.append(
                {
                    "type": "failure_rate_trend",
                    "prediction": f"Failure rate may reach {predicted_rate:.1f}% in {failure_trend['prediction']['horizon_days']} days",
                    "confidence": failure_trend["confidence"],
                    "severity": "high"
                    if predicted_rate > 15
                    else "medium"
                    if predicted_rate > 10
                    else "low",
                    "recommendation": self._get_failure_prediction_recommendation(predicted_rate),
                }
            )

        # Pattern-based predictions
        consecutive = failure_patterns["consecutive_failures"]
        if consecutive >= 2:
            predictions.append(
                {
                    "type": "consecutive_failure_pattern",
                    "prediction": f"Risk of continued failures based on {consecutive} consecutive failures",
                    "confidence": 0.8,
                    "severity": "high" if consecutive >= 3 else "medium",
                    "recommendation": "Investigate root cause immediately to prevent failure cascade",
                }
            )

        return predictions

    def _generate_performance_predictions(
        self, duration_trend: Dict, performance_trend: Dict, cache_trend: Dict
    ) -> List[Dict]:
        """Generate performance predictions."""
        predictions = []

        # Duration trend prediction
        if duration_trend.get("prediction") and duration_trend["confidence"] > 0.6:
            predicted_duration = duration_trend["prediction"]["value"]
            current_duration = duration_trend.get("current_value", 0)

            if predicted_duration > current_duration * 1.2:  # 20% increase
                predictions.append(
                    {
                        "type": "duration_increase",
                        "prediction": f"Execution time may increase to {predicted_duration:.0f}s in {duration_trend['prediction']['horizon_days']} days",
                        "confidence": duration_trend["confidence"],
                        "severity": "high" if predicted_duration > 600 else "medium",
                        "recommendation": "Optimize workflow performance before degradation occurs",
                    }
                )

        # Performance score prediction
        if performance_trend.get("prediction") and performance_trend["confidence"] > 0.6:
            predicted_score = performance_trend["prediction"]["value"]

            if predicted_score < 70:
                predictions.append(
                    {
                        "type": "performance_degradation",
                        "prediction": f"Performance score may drop to {predicted_score:.1f} in {performance_trend['prediction']['horizon_days']} days",
                        "confidence": performance_trend["confidence"],
                        "severity": "high" if predicted_score < 50 else "medium",
                        "recommendation": "Implement performance optimizations proactively",
                    }
                )

        return predictions

    def _get_failure_prediction_recommendation(self, predicted_rate: float) -> str:
        """Get recommendation based on predicted failure rate."""
        if predicted_rate > 20:
            return "Critical: Implement immediate failure prevention measures"
        if predicted_rate > 15:
            return "High priority: Review and strengthen error handling"
        if predicted_rate > 10:
            return "Medium priority: Investigate trending failure causes"
        return "Low priority: Continue monitoring failure trends"

    def generate_predictive_analysis(self, days: int = 30) -> Dict:
        """Generate comprehensive predictive analysis."""
        print(f"🔮 Generating predictive analysis for last {days} days...")

        # Load historical data
        historical_data = self.load_historical_data(days)

        if len(historical_data) < self.prediction_config["min_data_points"]:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.prediction_config['min_data_points']} data points for reliable prediction",
                "data_points": len(historical_data),
                "recommendations": [
                    "Continue collecting monitoring data",
                    "Run workflows more frequently to gather data",
                    "Check monitoring system configuration",
                ],
            }

        print(f"   Analyzing {len(historical_data)} data points...")

        # Perform analyses
        failure_analysis = self.analyze_failure_patterns(historical_data)
        performance_analysis = self.analyze_performance_trends(historical_data)

        # Calculate overall system risk
        overall_risk_score = (
            failure_analysis["risk_assessment"]["score"] * 0.6
            + performance_analysis["risk_assessment"]["score"] * 0.4
        )
        overall_risk = self._assess_risk_level(overall_risk_score)

        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            failure_analysis, performance_analysis, overall_risk
        )

        # Create analysis report
        analysis_report = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "repository": self.repo,
                "analysis_period_days": days,
                "data_points": len(historical_data),
                "prediction_horizon_days": self.prediction_config["prediction_horizon_days"],
            },
            "overall_risk_assessment": overall_risk,
            "failure_analysis": failure_analysis,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "next_review_date": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
        }

        print("✅ Predictive analysis completed")
        print(f"   Overall Risk: {overall_risk['level'].upper()} ({overall_risk['score']:.2f})")

        return analysis_report

    def _generate_comprehensive_recommendations(
        self, failure_analysis: Dict, performance_analysis: Dict, overall_risk: Dict
    ) -> List[Dict]:
        """Generate comprehensive recommendations based on all analyses."""
        recommendations = []

        # Risk-based recommendations
        risk_level = overall_risk["level"]

        if risk_level == "critical":
            recommendations.extend(
                [
                    {
                        "priority": "critical",
                        "category": "immediate_action",
                        "title": "Immediate System Stabilization Required",
                        "description": "Critical risk detected - implement emergency measures",
                        "actions": [
                            "Stop non-essential deployments",
                            "Activate incident response team",
                            "Implement emergency rollback procedures",
                            "Increase monitoring frequency",
                        ],
                    }
                ]
            )
        elif risk_level == "high":
            recommendations.extend(
                [
                    {
                        "priority": "high",
                        "category": "proactive_measures",
                        "title": "Proactive Risk Mitigation",
                        "description": "High risk trends detected - take preventive action",
                        "actions": [
                            "Review recent changes for risk factors",
                            "Implement additional error handling",
                            "Prepare rollback procedures",
                            "Schedule performance optimization sprint",
                        ],
                    }
                ]
            )

        # Failure-specific recommendations
        failure_predictions = failure_analysis.get("predictions", [])
        for prediction in failure_predictions:
            if prediction["severity"] in ["high", "critical"]:
                recommendations.append(
                    {
                        "priority": prediction["severity"],
                        "category": "failure_prevention",
                        "title": f"Address {prediction['type'].replace('_', ' ').title()}",
                        "description": prediction["prediction"],
                        "actions": [prediction["recommendation"]],
                    }
                )

        # Performance-specific recommendations
        performance_predictions = performance_analysis.get("predictions", [])
        for prediction in performance_predictions:
            if prediction["severity"] in ["high", "critical"]:
                recommendations.append(
                    {
                        "priority": prediction["severity"],
                        "category": "performance_optimization",
                        "title": f"Optimize {prediction['type'].replace('_', ' ').title()}",
                        "description": prediction["prediction"],
                        "actions": [prediction["recommendation"]],
                    }
                )

        # General monitoring recommendations
        recommendations.append(
            {
                "priority": "medium",
                "category": "monitoring_enhancement",
                "title": "Enhance Predictive Monitoring",
                "description": "Improve prediction accuracy and coverage",
                "actions": [
                    "Increase data collection frequency",
                    "Add more performance metrics",
                    "Implement real-time trend analysis",
                    "Set up automated prediction alerts",
                ],
            }
        )

        return recommendations

    def save_analysis_report(self, report: Dict, output_file: str = None) -> str:
        """Save predictive analysis report to file."""
        if output_file is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"predictive_analysis_{timestamp}.json"

        output_path = os.path.join(self.monitoring_dir, output_file)
        os.makedirs(self.monitoring_dir, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Predictive Failure Detection System")
    parser.add_argument(
        "--days", type=int, default=30, help="Days of historical data to analyze (default: 30)"
    )
    parser.add_argument(
        "--monitoring-dir",
        default="monitoring-results",
        help="Directory containing monitoring data",
    )
    parser.add_argument("--output-file", help="Output file for analysis report (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")

    args = parser.parse_args()

    try:
        # Initialize predictive system
        predictor = PredictiveFailureDetection(args.monitoring_dir)

        # Generate analysis
        analysis = predictor.generate_predictive_analysis(args.days)

        # Display results unless quiet
        if not args.quiet:
            print("\n" + "=" * 80)
            print("🔮 PREDICTIVE FAILURE DETECTION ANALYSIS")
            print("=" * 80)

            if analysis.get("status") == "insufficient_data":
                print(f"❌ {analysis['message']}")
                print(f"   Current data points: {analysis['data_points']}")
                print(f"   Required data points: {predictor.prediction_config['min_data_points']}")
                return

            # Display overall risk
            risk = analysis["overall_risk_assessment"]
            print(f"\n{risk['color']} OVERALL RISK: {risk['level'].upper()}")
            print(f"   Score: {risk['score']:.2f}/1.0")
            print(f"   Action: {risk['recommended_action']}")
            print(f"   {risk['description']}")

            # Display failure analysis
            failure_analysis = analysis["failure_analysis"]
            print("\n🚨 FAILURE RISK ANALYSIS:")
            print(f"   Risk Level: {failure_analysis['risk_assessment']['level']}")
            print(
                f"   Consecutive Failures: {failure_analysis['failure_patterns']['consecutive_failures']}"
            )

            failure_predictions = failure_analysis.get("predictions", [])
            if failure_predictions:
                print(f"   Predictions: {len(failure_predictions)} identified")
                for pred in failure_predictions[:3]:  # Show top 3
                    print(f"     - {pred['prediction']} (confidence: {pred['confidence']:.1f})")

            # Display performance analysis
            perf_analysis = analysis["performance_analysis"]
            print("\n⚡ PERFORMANCE RISK ANALYSIS:")
            print(f"   Risk Level: {perf_analysis['risk_assessment']['level']}")

            perf_predictions = perf_analysis.get("predictions", [])
            if perf_predictions:
                print(f"   Predictions: {len(perf_predictions)} identified")
                for pred in perf_predictions[:3]:  # Show top 3
                    print(f"     - {pred['prediction']} (confidence: {pred['confidence']:.1f})")

            # Display top recommendations
            recommendations = analysis.get("recommendations", [])
            if recommendations:
                print("\n💡 TOP RECOMMENDATIONS:")
                high_priority = [
                    r for r in recommendations if r["priority"] in ["critical", "high"]
                ]
                for rec in high_priority[:5]:  # Show top 5 high priority
                    print(f"   {rec['priority'].upper()}: {rec['title']}")
                    print(f"     {rec['description']}")

        # Save report if requested
        if args.output_file:
            output_path = predictor.save_analysis_report(analysis, args.output_file)
            print(f"\n✅ Analysis report saved to: {output_path}")

        # Exit with appropriate code based on risk level
        risk_level = analysis.get("overall_risk_assessment", {}).get("level", "low")
        if risk_level == "critical":
            sys.exit(3)
        elif risk_level == "high":
            sys.exit(2)
        elif risk_level == "medium":
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"❌ Error in predictive failure detection: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()

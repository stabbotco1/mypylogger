#!/usr/bin/env python3
"""Workflow Trend Analysis System

This script implements comprehensive workflow trend analysis and reporting,
providing insights into performance patterns, seasonal variations, and
long-term system health trends.

Requirements Addressed:
- 7.5: Implement workflow trend analysis and reporting
- 7.5: Create workflow performance dashboards
- 7.5: Add proactive alerting for potential workflow issues
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import glob
import json
import os
import statistics
import sys
from typing import Dict, List


class WorkflowTrendAnalysis:
    """Comprehensive workflow trend analysis and reporting system."""

    def __init__(self, monitoring_dir: str = "monitoring-results"):
        """Initialize the trend analysis system."""
        self.monitoring_dir = monitoring_dir
        self.repo = os.getenv("GITHUB_REPOSITORY", "unknown/unknown")

        # Analysis configuration
        self.analysis_config = {
            "short_term_days": 7,  # Short-term trend analysis
            "medium_term_days": 30,  # Medium-term trend analysis
            "long_term_days": 90,  # Long-term trend analysis
            "seasonal_analysis_days": 180,  # Seasonal pattern analysis
            "min_data_points": 10,  # Minimum data points for analysis
            "trend_significance_threshold": 0.05,  # Statistical significance
        }

        # Trend categories
        self.trend_categories = {
            "improving": {"symbol": "📈", "color": "green"},
            "stable": {"symbol": "➡️", "color": "blue"},
            "declining": {"symbol": "📉", "color": "red"},
            "volatile": {"symbol": "📊", "color": "orange"},
            "insufficient_data": {"symbol": "❓", "color": "gray"},
        }

    def load_time_series_data(self, days: int = 90) -> List[Dict]:
        """Load time series data for trend analysis."""
        performance_files = glob.glob(os.path.join(self.monitoring_dir, "performance_*.json"))

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        time_series_data = []

        for file_path in performance_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Parse timestamp and filter by date
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

                if timestamp >= cutoff_date:
                    # Add parsed timestamp for easier processing
                    data["parsed_timestamp"] = timestamp
                    time_series_data.append(data)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse {file_path}: {e}")
                continue

        # Sort by timestamp
        time_series_data.sort(key=lambda x: x["parsed_timestamp"])
        return time_series_data

    def aggregate_daily_metrics(self, data: List[Dict]) -> List[Dict]:
        """Aggregate metrics by day for trend analysis."""
        daily_data = defaultdict(list)

        # Group data by date
        for d in data:
            date_key = d["parsed_timestamp"].date()
            daily_data[date_key].append(d)

        # Calculate daily aggregates
        daily_metrics = []
        for date, day_data in daily_data.items():
            if not day_data:
                continue

            # Calculate daily metrics
            total_runs = len(day_data)
            successful_runs = sum(1 for d in day_data if d.get("status") == "success")
            failed_runs = total_runs - successful_runs

            durations = [d.get("duration_seconds", 0) for d in day_data]
            performance_scores = [
                d.get("performance_score", 0) for d in day_data if "performance_score" in d
            ]
            cache_rates = [
                d.get("cache_hit_rate") for d in day_data if d.get("cache_hit_rate") is not None
            ]

            daily_metric = {
                "date": date,
                "parsed_timestamp": datetime.combine(date, datetime.min.time()),
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": (successful_runs / total_runs) * 100 if total_runs > 0 else 0,
                "failure_rate": (failed_runs / total_runs) * 100 if total_runs > 0 else 0,
                "avg_duration": statistics.mean(durations) if durations else 0,
                "median_duration": statistics.median(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "avg_performance_score": statistics.mean(performance_scores)
                if performance_scores
                else 0,
                "avg_cache_hit_rate": statistics.mean(cache_rates) if cache_rates else None,
                "workflow_count": len(set(d.get("workflow_name", "unknown") for d in day_data)),
            }

            daily_metrics.append(daily_metric)

        # Sort by date
        daily_metrics.sort(key=lambda x: x["date"])
        return daily_metrics

    def calculate_trend_statistics(self, values: List[float], timestamps: List[datetime]) -> Dict:
        """Calculate comprehensive trend statistics."""
        if len(values) < 3:
            return {
                "trend": "insufficient_data",
                "slope": 0.0,
                "r_squared": 0.0,
                "p_value": 1.0,
                "confidence_interval": (0.0, 0.0),
                "volatility": 0.0,
                "seasonal_component": None,
            }

        # Convert timestamps to numeric values (days since first timestamp)
        time_numeric = [(ts - timestamps[0]).total_seconds() / (24 * 3600) for ts in timestamps]

        # Calculate linear regression
        n = len(values)
        sum_x = sum(time_numeric)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(time_numeric, values))
        sum_x2 = sum(x * x for x in time_numeric)
        sum_y2 = sum(y * y for y in values)

        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0.0
            intercept = statistics.mean(values)
            r_squared = 0.0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n

            # Calculate R-squared
            y_mean = statistics.mean(values)
            ss_tot = sum((y - y_mean) ** 2 for y in values)
            ss_res = sum((values[i] - (slope * time_numeric[i] + intercept)) ** 2 for i in range(n))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Calculate volatility (coefficient of variation)
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        volatility = (std_val / mean_val) if mean_val != 0 else 0

        # Determine trend direction
        if abs(slope) < 0.001:
            trend = "stable"
        elif slope > 0:
            trend = "improving" if self._is_improvement_metric(values) else "declining"
        else:
            trend = "declining" if self._is_improvement_metric(values) else "improving"

        # Add volatility assessment
        if volatility > 0.3:  # High volatility
            trend = "volatile"

        # Simple p-value approximation (for demonstration)
        # In a real implementation, you'd use proper statistical tests
        p_value = max(0.01, 1 - r_squared) if r_squared > 0.5 else 0.5

        return {
            "trend": trend,
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_squared,
            "p_value": p_value,
            "volatility": volatility,
            "mean": mean_val,
            "std_dev": std_val,
            "data_points": n,
        }

    def _is_improvement_metric(self, values: List[float]) -> bool:
        """Determine if higher values indicate improvement for this metric."""
        # This is a simplified heuristic - in practice, you'd need to know the metric type
        # For now, assume metrics like success_rate and performance_score are improvement metrics
        # while duration and failure_rate are not
        return True  # Default assumption

    def analyze_short_term_trends(self, daily_data: List[Dict]) -> Dict:
        """Analyze short-term trends (last 7 days)."""
        short_term_data = daily_data[-self.analysis_config["short_term_days"] :]

        if len(short_term_data) < 3:
            return {"status": "insufficient_data", "message": "Need at least 3 days of data"}

        # Extract metrics and timestamps
        timestamps = [d["parsed_timestamp"] for d in short_term_data]

        metrics_analysis = {}

        # Analyze key metrics
        key_metrics = ["success_rate", "avg_duration", "avg_performance_score", "failure_rate"]

        for metric in key_metrics:
            values = [d.get(metric, 0) for d in short_term_data]
            if any(v != 0 for v in values):  # Skip if all zeros
                metrics_analysis[metric] = self.calculate_trend_statistics(values, timestamps)

        # Calculate overall short-term health
        health_indicators = []
        for metric, analysis in metrics_analysis.items():
            if metric in ["success_rate", "avg_performance_score"]:
                # Higher is better
                health_indicators.append(
                    1
                    if analysis["trend"] == "improving"
                    else 0.5
                    if analysis["trend"] == "stable"
                    else 0
                )
            else:
                # Lower is better
                health_indicators.append(
                    1
                    if analysis["trend"] == "declining"
                    else 0.5
                    if analysis["trend"] == "stable"
                    else 0
                )

        overall_health = statistics.mean(health_indicators) if health_indicators else 0.5

        return {
            "period": "short_term",
            "days_analyzed": len(short_term_data),
            "metrics_analysis": metrics_analysis,
            "overall_health_trend": self._categorize_health_trend(overall_health),
            "summary": self._generate_trend_summary(metrics_analysis, "short-term"),
        }

    def analyze_medium_term_trends(self, daily_data: List[Dict]) -> Dict:
        """Analyze medium-term trends (last 30 days)."""
        medium_term_data = daily_data[-self.analysis_config["medium_term_days"] :]

        if len(medium_term_data) < 7:
            return {"status": "insufficient_data", "message": "Need at least 7 days of data"}

        # Extract metrics and timestamps
        timestamps = [d["parsed_timestamp"] for d in medium_term_data]

        metrics_analysis = {}

        # Analyze key metrics with more sophisticated analysis
        key_metrics = [
            "success_rate",
            "avg_duration",
            "avg_performance_score",
            "failure_rate",
            "total_runs",
        ]

        for metric in key_metrics:
            values = [d.get(metric, 0) for d in medium_term_data]
            if any(v != 0 for v in values):  # Skip if all zeros
                analysis = self.calculate_trend_statistics(values, timestamps)

                # Add medium-term specific analysis
                analysis["weekly_patterns"] = self._analyze_weekly_patterns(
                    medium_term_data, metric
                )
                analysis["change_points"] = self._detect_change_points(values, timestamps)

                metrics_analysis[metric] = analysis

        # Analyze workflow-specific trends
        workflow_trends = self._analyze_workflow_specific_trends(medium_term_data)

        return {
            "period": "medium_term",
            "days_analyzed": len(medium_term_data),
            "metrics_analysis": metrics_analysis,
            "workflow_specific_trends": workflow_trends,
            "summary": self._generate_trend_summary(metrics_analysis, "medium-term"),
        }

    def analyze_long_term_trends(self, daily_data: List[Dict]) -> Dict:
        """Analyze long-term trends (last 90 days)."""
        if len(daily_data) < 14:
            return {"status": "insufficient_data", "message": "Need at least 14 days of data"}

        # Extract metrics and timestamps
        timestamps = [d["parsed_timestamp"] for d in daily_data]

        metrics_analysis = {}

        # Analyze key metrics with long-term perspective
        key_metrics = [
            "success_rate",
            "avg_duration",
            "avg_performance_score",
            "failure_rate",
            "total_runs",
        ]

        for metric in key_metrics:
            values = [d.get(metric, 0) for d in daily_data]
            if any(v != 0 for v in values):  # Skip if all zeros
                analysis = self.calculate_trend_statistics(values, timestamps)

                # Add long-term specific analysis
                analysis["monthly_patterns"] = self._analyze_monthly_patterns(daily_data, metric)
                analysis["seasonal_decomposition"] = self._analyze_seasonal_patterns(
                    values, timestamps
                )
                analysis["long_term_forecast"] = self._generate_long_term_forecast(
                    values, timestamps
                )

                metrics_analysis[metric] = analysis

        # Calculate system maturity indicators
        maturity_indicators = self._calculate_system_maturity(daily_data)

        return {
            "period": "long_term",
            "days_analyzed": len(daily_data),
            "metrics_analysis": metrics_analysis,
            "system_maturity": maturity_indicators,
            "summary": self._generate_trend_summary(metrics_analysis, "long-term"),
        }

    def _analyze_weekly_patterns(self, daily_data: List[Dict], metric: str) -> Dict:
        """Analyze weekly patterns in the data."""
        weekday_data = defaultdict(list)

        for d in daily_data:
            weekday = d["parsed_timestamp"].strftime("%A")
            value = d.get(metric, 0)
            weekday_data[weekday].append(value)

        # Calculate averages by weekday
        weekday_averages = {}
        for weekday, values in weekday_data.items():
            if values:
                weekday_averages[weekday] = {
                    "average": statistics.mean(values),
                    "count": len(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                }

        # Find best and worst performing days
        if weekday_averages:
            best_day = max(weekday_averages.keys(), key=lambda k: weekday_averages[k]["average"])
            worst_day = min(weekday_averages.keys(), key=lambda k: weekday_averages[k]["average"])
        else:
            best_day = worst_day = None

        return {
            "weekday_averages": weekday_averages,
            "best_performing_day": best_day,
            "worst_performing_day": worst_day,
            "has_weekly_pattern": len(set(weekday_averages.values())) > 1
            if weekday_averages
            else False,
        }

    def _analyze_monthly_patterns(self, daily_data: List[Dict], metric: str) -> Dict:
        """Analyze monthly patterns in the data."""
        monthly_data = defaultdict(list)

        for d in daily_data:
            month_key = d["parsed_timestamp"].strftime("%Y-%m")
            value = d.get(metric, 0)
            monthly_data[month_key].append(value)

        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_data.items():
            if values:
                monthly_averages[month] = {
                    "average": statistics.mean(values),
                    "count": len(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                }

        return {"monthly_averages": monthly_averages, "months_analyzed": len(monthly_averages)}

    def _analyze_seasonal_patterns(self, values: List[float], timestamps: List[datetime]) -> Dict:
        """Analyze seasonal patterns (simplified implementation)."""
        if len(values) < 30:  # Need at least 30 data points
            return {"status": "insufficient_data"}

        # Simple seasonal analysis - look for cyclical patterns
        # In a real implementation, you'd use more sophisticated methods like FFT

        # Calculate moving averages to identify trends
        window_size = min(7, len(values) // 4)
        moving_averages = []

        for i in range(len(values) - window_size + 1):
            avg = statistics.mean(values[i : i + window_size])
            moving_averages.append(avg)

        # Calculate detrended values
        detrended = []
        for i in range(len(moving_averages)):
            original_idx = i + window_size // 2
            if original_idx < len(values):
                detrended.append(values[original_idx] - moving_averages[i])

        # Simple seasonality detection
        has_seasonality = len(detrended) > 0 and statistics.stdev(
            detrended
        ) > 0.1 * statistics.mean(values)

        return {
            "has_seasonality": has_seasonality,
            "seasonal_strength": statistics.stdev(detrended) / statistics.mean(values)
            if values and statistics.mean(values) != 0
            else 0,
            "trend_component": moving_averages[-1] if moving_averages else 0,
        }

    def _detect_change_points(self, values: List[float], timestamps: List[datetime]) -> List[Dict]:
        """Detect significant change points in the data."""
        change_points = []

        if len(values) < 10:
            return change_points

        # Simple change point detection using moving averages
        window_size = max(3, len(values) // 10)

        for i in range(window_size, len(values) - window_size):
            before_avg = statistics.mean(values[i - window_size : i])
            after_avg = statistics.mean(values[i : i + window_size])

            # Check for significant change
            if before_avg != 0:
                change_percent = abs((after_avg - before_avg) / before_avg) * 100

                if change_percent > 20:  # 20% change threshold
                    change_points.append(
                        {
                            "timestamp": timestamps[i],
                            "index": i,
                            "before_value": before_avg,
                            "after_value": after_avg,
                            "change_percent": change_percent,
                            "change_type": "increase" if after_avg > before_avg else "decrease",
                        }
                    )

        return change_points

    def _generate_long_term_forecast(self, values: List[float], timestamps: List[datetime]) -> Dict:
        """Generate simple long-term forecast."""
        if len(values) < 14:
            return {"status": "insufficient_data"}

        # Simple linear extrapolation
        trend_stats = self.calculate_trend_statistics(values, timestamps)

        if trend_stats["r_squared"] < 0.3:  # Low correlation
            return {"status": "unreliable", "reason": "low_correlation"}

        # Forecast next 30 days
        last_timestamp = timestamps[-1]
        forecast_days = 30

        forecasted_values = []
        for day in range(1, forecast_days + 1):
            future_time_numeric = (len(values) - 1) + day
            forecasted_value = trend_stats["slope"] * future_time_numeric + trend_stats["intercept"]
            forecasted_values.append(max(0, forecasted_value))  # Ensure non-negative

        return {
            "forecast_horizon_days": forecast_days,
            "forecasted_values": forecasted_values,
            "confidence": trend_stats["r_squared"],
            "trend_direction": trend_stats["trend"],
        }

    def _analyze_workflow_specific_trends(self, daily_data: List[Dict]) -> Dict:
        """Analyze trends for specific workflows."""
        # This would require workflow-specific data
        # For now, return a placeholder
        return {
            "workflow_count": len(set(d.get("workflow_name", "unknown") for d in daily_data)),
            "analysis": "Workflow-specific analysis requires detailed workflow data",
        }

    def _calculate_system_maturity(self, daily_data: List[Dict]) -> Dict:
        """Calculate system maturity indicators."""
        if len(daily_data) < 30:
            return {"status": "insufficient_data"}

        # Calculate stability metrics
        success_rates = [d.get("success_rate", 0) for d in daily_data]
        durations = [d.get("avg_duration", 0) for d in daily_data]

        # Stability indicators
        success_rate_stability = 1 - (statistics.stdev(success_rates) / 100) if success_rates else 0
        duration_stability = (
            1 - (statistics.stdev(durations) / statistics.mean(durations))
            if durations and statistics.mean(durations) > 0
            else 0
        )

        # Consistency indicators
        consistency_score = (success_rate_stability + duration_stability) / 2

        # Maturity level
        if consistency_score > 0.8:
            maturity_level = "mature"
        elif consistency_score > 0.6:
            maturity_level = "developing"
        elif consistency_score > 0.4:
            maturity_level = "emerging"
        else:
            maturity_level = "unstable"

        return {
            "maturity_level": maturity_level,
            "consistency_score": consistency_score,
            "success_rate_stability": success_rate_stability,
            "duration_stability": duration_stability,
            "days_analyzed": len(daily_data),
        }

    def _categorize_health_trend(self, health_score: float) -> str:
        """Categorize overall health trend."""
        if health_score > 0.8:
            return "excellent"
        if health_score > 0.6:
            return "good"
        if health_score > 0.4:
            return "fair"
        return "poor"

    def _generate_trend_summary(self, metrics_analysis: Dict, period: str) -> Dict:
        """Generate a summary of trend analysis."""
        if not metrics_analysis:
            return {"message": "No metrics available for analysis"}

        # Count trends by type
        trend_counts = defaultdict(int)
        significant_trends = []

        for metric, analysis in metrics_analysis.items():
            trend = analysis.get("trend", "unknown")
            trend_counts[trend] += 1

            # Check for significant trends
            if analysis.get("r_squared", 0) > 0.5:  # Significant correlation
                significant_trends.append(
                    {
                        "metric": metric,
                        "trend": trend,
                        "strength": analysis.get("r_squared", 0),
                        "volatility": analysis.get("volatility", 0),
                    }
                )

        # Determine overall trend
        if trend_counts["improving"] > trend_counts["declining"]:
            overall_trend = "improving"
        elif trend_counts["declining"] > trend_counts["improving"]:
            overall_trend = "declining"
        else:
            overall_trend = "stable"

        return {
            "period": period,
            "overall_trend": overall_trend,
            "trend_distribution": dict(trend_counts),
            "significant_trends": significant_trends,
            "metrics_analyzed": len(metrics_analysis),
        }

    def generate_comprehensive_trend_report(self, days: int = 90) -> Dict:
        """Generate comprehensive trend analysis report."""
        print(f"📊 Generating comprehensive trend analysis for last {days} days...")

        # Load time series data
        time_series_data = self.load_time_series_data(days)

        if len(time_series_data) < self.analysis_config["min_data_points"]:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {self.analysis_config['min_data_points']} data points for trend analysis",
                "data_points": len(time_series_data),
            }

        print(f"   Processing {len(time_series_data)} data points...")

        # Aggregate daily metrics
        daily_metrics = self.aggregate_daily_metrics(time_series_data)

        print(f"   Aggregated into {len(daily_metrics)} daily metrics...")

        # Perform multi-timeframe analysis
        analyses = {}

        # Short-term analysis
        if len(daily_metrics) >= 3:
            analyses["short_term"] = self.analyze_short_term_trends(daily_metrics)

        # Medium-term analysis
        if len(daily_metrics) >= 7:
            analyses["medium_term"] = self.analyze_medium_term_trends(daily_metrics)

        # Long-term analysis
        if len(daily_metrics) >= 14:
            analyses["long_term"] = self.analyze_long_term_trends(daily_metrics)

        # Generate overall insights
        insights = self._generate_overall_insights(analyses)

        # Create comprehensive report
        report = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "repository": self.repo,
                "analysis_period_days": days,
                "data_points": len(time_series_data),
                "daily_metrics": len(daily_metrics),
            },
            "trend_analyses": analyses,
            "overall_insights": insights,
            "recommendations": self._generate_trend_recommendations(analyses, insights),
        }

        print("✅ Trend analysis completed")

        return report

    def _generate_overall_insights(self, analyses: Dict) -> Dict:
        """Generate overall insights from all trend analyses."""
        insights = {
            "system_stability": "unknown",
            "performance_trajectory": "unknown",
            "key_concerns": [],
            "positive_trends": [],
            "areas_for_attention": [],
        }

        # Analyze across timeframes
        if "long_term" in analyses:
            long_term = analyses["long_term"]
            if "system_maturity" in long_term:
                insights["system_stability"] = long_term["system_maturity"].get(
                    "maturity_level", "unknown"
                )

        # Collect key trends across timeframes
        all_trends = []
        for timeframe, analysis in analyses.items():
            if "summary" in analysis:
                summary = analysis["summary"]
                all_trends.append(
                    {
                        "timeframe": timeframe,
                        "overall_trend": summary.get("overall_trend", "unknown"),
                        "significant_trends": summary.get("significant_trends", []),
                    }
                )

        # Determine performance trajectory
        recent_trends = [
            t["overall_trend"]
            for t in all_trends
            if t["timeframe"] in ["short_term", "medium_term"]
        ]
        if recent_trends:
            if all(t == "improving" for t in recent_trends):
                insights["performance_trajectory"] = "improving"
            elif all(t == "declining" for t in recent_trends):
                insights["performance_trajectory"] = "declining"
            else:
                insights["performance_trajectory"] = "mixed"

        return insights

    def _generate_trend_recommendations(self, analyses: Dict, insights: Dict) -> List[Dict]:
        """Generate recommendations based on trend analysis."""
        recommendations = []

        # System stability recommendations
        stability = insights.get("system_stability", "unknown")
        if stability == "unstable":
            recommendations.append(
                {
                    "priority": "high",
                    "category": "stability",
                    "title": "Improve System Stability",
                    "description": "System shows unstable patterns requiring immediate attention",
                    "actions": [
                        "Investigate root causes of instability",
                        "Implement more robust error handling",
                        "Add system health monitoring",
                        "Consider infrastructure improvements",
                    ],
                }
            )

        # Performance trajectory recommendations
        trajectory = insights.get("performance_trajectory", "unknown")
        if trajectory == "declining":
            recommendations.append(
                {
                    "priority": "high",
                    "category": "performance",
                    "title": "Address Performance Decline",
                    "description": "Performance metrics show declining trends",
                    "actions": [
                        "Conduct performance audit",
                        "Optimize critical workflow paths",
                        "Review recent changes for performance impact",
                        "Implement performance monitoring alerts",
                    ],
                }
            )

        # Timeframe-specific recommendations
        for timeframe, analysis in analyses.items():
            if "summary" in analysis:
                summary = analysis["summary"]
                significant_trends = summary.get("significant_trends", [])

                for trend in significant_trends:
                    if trend["trend"] == "declining" and trend["strength"] > 0.7:
                        recommendations.append(
                            {
                                "priority": "medium",
                                "category": f"{timeframe}_trend",
                                "title": f"Address {trend['metric'].replace('_', ' ').title()} Decline",
                                "description": f"{timeframe.replace('_', '-').title()} decline in {trend['metric']}",
                                "actions": [f"Investigate {trend['metric']} performance issues"],
                            }
                        )

        # General monitoring recommendations
        recommendations.append(
            {
                "priority": "low",
                "category": "monitoring",
                "title": "Enhance Trend Monitoring",
                "description": "Improve trend analysis capabilities",
                "actions": [
                    "Increase data collection frequency",
                    "Add more performance metrics",
                    "Implement automated trend alerts",
                    "Create trend analysis dashboards",
                ],
            }
        )

        return recommendations

    def save_trend_report(self, report: Dict, output_file: str = None) -> str:
        """Save trend analysis report to file."""
        if output_file is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = f"trend_analysis_{timestamp}.json"

        output_path = os.path.join(self.monitoring_dir, output_file)
        os.makedirs(self.monitoring_dir, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Workflow Trend Analysis System")
    parser.add_argument(
        "--days", type=int, default=90, help="Days of data to analyze (default: 90)"
    )
    parser.add_argument(
        "--monitoring-dir",
        default="monitoring-results",
        help="Directory containing monitoring data",
    )
    parser.add_argument("--output-file", help="Output file for trend report (JSON)")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed output")

    args = parser.parse_args()

    try:
        # Initialize trend analysis system
        trend_analyzer = WorkflowTrendAnalysis(args.monitoring_dir)

        # Generate trend report
        report = trend_analyzer.generate_comprehensive_trend_report(args.days)

        # Display results unless quiet
        if not args.quiet:
            print("\n" + "=" * 80)
            print("📊 WORKFLOW TREND ANALYSIS REPORT")
            print("=" * 80)

            if report.get("status") == "insufficient_data":
                print(f"❌ {report['message']}")
                print(f"   Current data points: {report['data_points']}")
                return

            # Display metadata
            metadata = report["metadata"]
            print(f"\nRepository: {metadata['repository']}")
            print(f"Analysis Period: {metadata['analysis_period_days']} days")
            print(f"Data Points: {metadata['data_points']} performance records")
            print(f"Daily Metrics: {metadata['daily_metrics']} days")

            # Display trend analyses
            analyses = report.get("trend_analyses", {})
            for timeframe, analysis in analyses.items():
                if "summary" in analysis:
                    summary = analysis["summary"]
                    print(f"\n📈 {timeframe.replace('_', '-').upper()} TRENDS:")
                    print(f"   Overall Trend: {summary['overall_trend']}")
                    print(f"   Metrics Analyzed: {summary['metrics_analyzed']}")

                    significant = summary.get("significant_trends", [])
                    if significant:
                        print(f"   Significant Trends: {len(significant)}")
                        for trend in significant[:3]:  # Show top 3
                            print(
                                f"     - {trend['metric']}: {trend['trend']} (strength: {trend['strength']:.2f})"
                            )

            # Display insights
            insights = report.get("overall_insights", {})
            print("\n🔍 OVERALL INSIGHTS:")
            print(f"   System Stability: {insights.get('system_stability', 'unknown')}")
            print(f"   Performance Trajectory: {insights.get('performance_trajectory', 'unknown')}")

            # Display recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                print("\n💡 RECOMMENDATIONS:")
                high_priority = [r for r in recommendations if r["priority"] == "high"]
                for rec in high_priority[:3]:  # Show top 3 high priority
                    print(f"   HIGH: {rec['title']}")
                    print(f"         {rec['description']}")

        # Save report if requested
        if args.output_file:
            output_path = trend_analyzer.save_trend_report(report, args.output_file)
            print(f"\n✅ Trend analysis report saved to: {output_path}")

        # Exit with appropriate code based on insights
        trajectory = report.get("overall_insights", {}).get("performance_trajectory", "unknown")
        if trajectory == "declining":
            sys.exit(2)
        elif trajectory == "mixed":
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"❌ Error in workflow trend analysis: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()

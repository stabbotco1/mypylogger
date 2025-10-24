#!/usr/bin/env python3
"""Performance badge generation script for mypylogger v0.2.0.

This script generates performance badges from benchmark results for shields.io integration.
It also implements performance regression detection and failure conditions.

Requirements addressed:
- 9.4: Generate performance badges showing current benchmark results
- 9.5: Detect performance regressions and fail builds if performance degrades by more than 20%
- 15.2: Performance badge generation script using benchmark results
- 15.3: Performance regression detection and failure conditions
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

# Constants for magic values
WARNING_THRESHOLD = 5.0
MIN_ARGS_COUNT = 2
BASELINE_ARG_INDEX = 2
OUTPUT_DIR_ARG_INDEX = 3


class PerformanceBadgeGenerator:
    """Generates performance badges and detects regressions."""

    def __init__(self, benchmark_file: Path, baseline_file: Path | None = None) -> None:
        """Initialize badge generator.

        Args:
            benchmark_file: Path to current benchmark results JSON file
            baseline_file: Path to baseline benchmark results (optional)
        """
        self.benchmark_file = benchmark_file
        self.baseline_file = baseline_file
        self.current_results: dict[str, Any] = {}
        self.baseline_results: dict[str, Any] = {}
        self.regression_detected = False
        self.regression_details: list[str] = []

    def load_benchmark_results(self) -> bool:
        """Load current benchmark results.

        Returns:
            True if results loaded successfully, False otherwise
        """
        try:
            with self.benchmark_file.open() as f:
                self.current_results = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading benchmark results: {e}")
            return False

    def load_baseline_results(self) -> bool:
        """Load baseline benchmark results for regression detection.

        Returns:
            True if baseline loaded successfully, False otherwise
        """
        if not self.baseline_file or not self.baseline_file.exists():
            print("⚠️ No baseline file provided - skipping regression detection")
            return False

        try:
            with self.baseline_file.open() as f:
                self.baseline_results = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Error loading baseline results: {e}")
            return False

    def detect_performance_regression(self) -> bool:
        """Detect performance regressions against baseline.

        Returns:
            True if regression detected, False otherwise
        """
        if not self.baseline_results:
            return False

        print("🔍 Detecting Performance Regressions")
        print("=" * 38)

        current_benchmarks = self._extract_benchmarks(self.current_results)
        baseline_benchmarks = self._extract_benchmarks(self.baseline_results)

        regression_threshold = 20.0  # 20% degradation threshold

        for benchmark_name in current_benchmarks:
            if benchmark_name not in baseline_benchmarks:
                continue

            current_mean = current_benchmarks[benchmark_name]["mean"]
            baseline_mean = baseline_benchmarks[benchmark_name]["mean"]

            # Calculate percentage change
            percent_change = ((current_mean - baseline_mean) / baseline_mean) * 100

            print(f"📊 {benchmark_name}:")
            print(f"   Current: {current_mean * 1000:.3f}ms")
            print(f"   Baseline: {baseline_mean * 1000:.3f}ms")
            print(f"   Change: {percent_change:+.1f}%")

            if percent_change > regression_threshold:
                self.regression_detected = True
                regression_msg = (
                    f"Performance regression: {benchmark_name} degraded by "
                    f"{percent_change:.1f}% (threshold: {regression_threshold}%)"
                )
                self.regression_details.append(regression_msg)
                print("   ❌ REGRESSION DETECTED")
            elif percent_change > WARNING_THRESHOLD:  # Warning threshold
                print("   ⚠️ WARNING: Minor performance degradation")
            else:
                print("   ✅ STABLE: Performance within acceptable range")

            print()

        return self.regression_detected

    def generate_performance_badge(self) -> dict[str, Any]:
        """Generate performance badge data for shields.io.

        Returns:
            Dictionary containing badge data
        """
        print("🏷️ Generating Performance Badge")
        print("=" * 32)

        # Extract performance metrics
        benchmarks = self._extract_benchmarks(self.current_results)

        if not benchmarks:
            return self._create_fallback_badge("no data", "lightgrey")

        # Calculate key performance metrics
        init_times = []
        log_times = []

        for benchmark_name, stats in benchmarks.items():
            mean_time_ms = stats["mean"] * 1000

            if "initialization" in benchmark_name.lower():
                init_times.append(mean_time_ms)
            elif any(keyword in benchmark_name.lower() for keyword in ["log", "entry", "logging"]):
                log_times.append(mean_time_ms)

        # Calculate averages
        avg_init_time = sum(init_times) / len(init_times) if init_times else 0
        avg_log_time = sum(log_times) / len(log_times) if log_times else 0

        print(f"Average initialization time: {avg_init_time:.3f}ms")
        print(f"Average log entry time: {avg_log_time:.3f}ms")

        # Determine badge status and color
        init_threshold = 10.0  # 10ms
        log_threshold = 1.0  # 1ms

        init_pass = avg_init_time < init_threshold
        log_pass = avg_log_time < log_threshold

        if self.regression_detected:
            # Regression detected - red badge
            badge_color = "red"
            badge_message = "regression detected"
            status = "regression"
        elif init_pass and log_pass:
            # All thresholds met - green badge with metrics
            badge_color = "brightgreen"
            badge_message = f"init: {avg_init_time:.1f}ms | log: {avg_log_time:.1f}ms"
            status = "passing"
        elif init_pass or log_pass:
            # Some thresholds met - yellow badge
            badge_color = "yellow"
            badge_message = "partial pass"
            status = "warning"
        else:
            # No thresholds met - red badge
            badge_color = "red"
            badge_message = "failing"
            status = "failing"

        print(f"Badge status: {status}")
        print(f"Badge color: {badge_color}")
        print(f"Badge message: {badge_message}")

        return {
            "schemaVersion": 1,
            "label": "performance",
            "message": badge_message,
            "color": badge_color,
            "status": status,
            "init_time_ms": round(avg_init_time, 3),
            "log_time_ms": round(avg_log_time, 3),
            "regression_detected": self.regression_detected,
        }

    def generate_performance_summary(self) -> dict[str, Any]:
        """Generate detailed performance summary for reporting.

        Returns:
            Dictionary containing performance summary
        """
        benchmarks = self._extract_benchmarks(self.current_results)

        return {
            "timestamp": self._get_timestamp(),
            "total_benchmarks": len(benchmarks),
            "regression_detected": self.regression_detected,
            "regression_details": self.regression_details,
            "benchmark_results": {
                name: {
                    "mean_ms": round(stats["mean"] * 1000, 3),
                    "stddev_ms": round(stats.get("stddev", 0) * 1000, 3),
                    "min_ms": round(stats.get("min", 0) * 1000, 3),
                    "max_ms": round(stats.get("max", 0) * 1000, 3),
                }
                for name, stats in benchmarks.items()
            },
        }

    def save_badge_files(self, output_dir: Path) -> None:
        """Save badge files to output directory.

        Args:
            output_dir: Directory to save badge files
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate badge data
        badge_data = self.generate_performance_badge()
        summary_data = self.generate_performance_summary()

        # Save performance badge JSON
        badge_file = output_dir / "performance-badge.json"
        with badge_file.open("w") as f:
            json.dump(
                {
                    "schemaVersion": badge_data["schemaVersion"],
                    "label": badge_data["label"],
                    "message": badge_data["message"],
                    "color": badge_data["color"],
                },
                f,
                indent=2,
            )

        print(f"✅ Performance badge saved to: {badge_file}")

        # Save performance summary
        summary_file = output_dir / "performance-summary.json"
        with summary_file.open("w") as f:
            json.dump({**summary_data, "badge_data": badge_data}, f, indent=2)

        print(f"✅ Performance summary saved to: {summary_file}")

    def _extract_benchmarks(self, results: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract benchmark statistics from pytest-benchmark results.

        Args:
            results: Pytest-benchmark results dictionary

        Returns:
            Dictionary of benchmark names to their statistics
        """
        benchmarks = {}

        if "benchmarks" in results:
            for benchmark in results["benchmarks"]:
                name = benchmark.get("name", "")
                stats = benchmark.get("stats", {})
                if name and stats:
                    benchmarks[name] = stats

        return benchmarks

    def _create_fallback_badge(self, message: str, color: str) -> dict[str, Any]:
        """Create fallback badge data.

        Args:
            message: Badge message
            color: Badge color

        Returns:
            Badge data dictionary
        """
        return {
            "schemaVersion": 1,
            "label": "performance",
            "message": message,
            "color": color,
            "status": "unknown",
            "init_time_ms": 0,
            "log_time_ms": 0,
            "regression_detected": False,
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat() + "Z"


def main() -> None:
    """Main entry point for performance badge generation."""
    if len(sys.argv) < MIN_ARGS_COUNT:
        print(
            "Usage: python generate_performance_badge.py "
            "<benchmark_results.json> [baseline.json] [output_dir]"
        )
        sys.exit(1)

    benchmark_file = Path(sys.argv[1])
    baseline_file = (
        Path(sys.argv[BASELINE_ARG_INDEX])
        if len(sys.argv) > BASELINE_ARG_INDEX and sys.argv[BASELINE_ARG_INDEX] != "none"
        else None
    )
    output_dir = (
        Path(sys.argv[OUTPUT_DIR_ARG_INDEX])
        if len(sys.argv) > OUTPUT_DIR_ARG_INDEX
        else Path("badge-data")
    )

    if not benchmark_file.exists():
        print(f"❌ Benchmark results file not found: {benchmark_file}")
        sys.exit(1)

    print("🚀 Performance Badge Generation for mypylogger v0.2.0")
    print("=" * 55)
    print(f"Benchmark file: {benchmark_file}")
    if baseline_file:
        print(f"Baseline file: {baseline_file}")
    print(f"Output directory: {output_dir}")
    print()

    generator = PerformanceBadgeGenerator(benchmark_file, baseline_file)

    # Load benchmark results
    if not generator.load_benchmark_results():
        sys.exit(1)

    # Load baseline results (optional)
    generator.load_baseline_results()

    # Detect performance regressions
    regression_detected = generator.detect_performance_regression()

    # Generate and save badge files
    generator.save_badge_files(output_dir)

    # Print summary
    print("\n" + "=" * 55)
    print("📊 PERFORMANCE BADGE GENERATION SUMMARY")
    print("=" * 55)

    if regression_detected:
        print("❌ PERFORMANCE REGRESSION DETECTED")
        print("Regression details:")
        for detail in generator.regression_details:
            print(f"  • {detail}")
        print()
        print("🔧 Recommended Actions:")
        print("1. Review recent code changes for performance impact")
        print("2. Run local benchmarks to reproduce the regression")
        print("3. Optimize performance-critical code paths")
        print("4. Consider reverting changes that caused regression")
        print()
        print("❌ Build should FAIL due to performance regression")
        sys.exit(1)
    else:
        print("✅ Performance badge generated successfully")
        print("✅ No performance regressions detected")
        print()
        print("Badge files created and ready for deployment")
        sys.exit(0)


if __name__ == "__main__":
    main()

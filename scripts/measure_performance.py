#!/usr/bin/env python3
"""
Performance Measurement System for mypylogger

This script runs performance benchmarks and generates metrics for badge updates.
It measures actual latency, throughput, and memory usage to provide accurate
performance data for README badges.

Usage:
    python scripts/measure_performance.py [--format badge] [--os OS_NAME]

Options:
    --format badge    Output in badge-friendly format
    --os OS_NAME      Specify OS name for badge (ubuntu, macos, windows)
    --json           Output results as JSON
    --update-badges  Update README badges with measured performance
"""

import argparse
import json
import os
import platform
import re
import sys
import tempfile
import time
from pathlib import Path
from statistics import median
from typing import Any, Dict, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import psutil

    from mypylogger import get_logger
    from mypylogger.core import SingletonLogger
except ImportError as e:
    print(f"Error: Required dependencies not available: {e}")
    print("Please run: pip install -e '.[dev]'")
    sys.exit(1)


class PerformanceMeasurement:
    """Measures mypylogger performance metrics."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.temp_dir: Optional[str] = None

    def setup_test_environment(self) -> None:
        """Set up clean test environment."""
        # Create temporary directory for logs
        temp_dir: str = tempfile.mkdtemp(prefix="perf_test_")
        self.temp_dir = temp_dir

        # Reset singleton for clean testing
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Set environment for test
        os.environ["APP_NAME"] = "performance_measurement"

        if self.verbose:
            print(f"Test environment setup in: {self.temp_dir}")

    def cleanup_test_environment(self) -> None:
        """Clean up test environment."""
        if self.temp_dir:
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)
            if self.verbose:
                print("Test environment cleaned up")

    def measure_latency(self, num_samples: int = 100) -> Dict[str, float]:
        """Measure logging latency metrics."""
        logger = get_logger()

        # Warm up the logger
        for _ in range(10):
            logger.info("Warmup message")

        # Measure latency for multiple log entries
        latencies = []

        for i in range(num_samples):
            start_time = time.perf_counter()
            logger.info(f"Latency test message {i}")
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        return {
            "average_ms": sum(latencies) / len(latencies),
            "median_ms": median(latencies),
            "p95_ms": sorted(latencies)[int(0.95 * len(latencies))],
            "max_ms": max(latencies),
            "samples": num_samples,
        }

    def measure_throughput(self, num_messages: int = 15000) -> Dict[str, float]:
        """Measure logging throughput."""
        logger = get_logger()

        # Warm up
        for _ in range(100):
            logger.info("Warmup message")

        # Measure throughput
        start_time = time.perf_counter()

        for i in range(num_messages):
            logger.info(f"Throughput test message {i}")

        end_time = time.perf_counter()
        duration = end_time - start_time
        throughput = num_messages / duration

        return {
            "messages": num_messages,
            "duration_seconds": duration,
            "logs_per_second": throughput,
        }

    def measure_memory_usage(self, num_messages: int = 5000) -> Dict[str, float]:
        """Measure memory usage during logging."""
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        logger = get_logger()

        # Log messages and track memory
        for i in range(num_messages):
            logger.info(f"Memory test message {i} with additional data for realism")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        return {
            "baseline_mb": baseline_memory,
            "final_mb": final_memory,
            "increase_mb": memory_increase,
            "messages": num_messages,
        }

    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite."""
        self.setup_test_environment()

        try:
            if self.verbose:
                print("Running latency measurements...")
            latency_results = self.measure_latency()

            if self.verbose:
                print("Running throughput measurements...")
            throughput_results = self.measure_throughput()

            if self.verbose:
                print("Running memory usage measurements...")
            memory_results = self.measure_memory_usage()

            # Get system information
            system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count(),
                "timestamp": time.time(),
            }

            return {
                "latency": latency_results,
                "throughput": throughput_results,
                "memory": memory_results,
                "system": system_info,
            }

        finally:
            self.cleanup_test_environment()

    def format_for_badge(
        self, results: Dict[str, Any], os_name: Optional[str] = None
    ) -> str:
        """Format results for badge display."""
        if not os_name:
            os_name = platform.system().lower()
            if os_name == "darwin":
                os_name = "macos"

        latency = results["latency"]["average_ms"]
        throughput = results["throughput"]["logs_per_second"]

        # Format for badge display
        latency_str = f"{latency:.3f}ms" if latency >= 0.001 else f"{latency:.4f}ms"
        throughput_str = (
            f"{throughput/1000:.0f}K/sec"
            if throughput >= 1000
            else f"{throughput:.0f}/sec"
        )

        return f"{latency_str}, {throughput_str}"

    def generate_badge_url(
        self, results: Dict[str, Any], os_name: Optional[str] = None
    ) -> str:
        """Generate Shields.io badge URL with actual performance data."""
        if not os_name:
            os_name = platform.system().lower()
            if os_name == "darwin":
                os_name = "macos"

        performance_text = self.format_for_badge(results, os_name)

        # URL encode the performance text
        import urllib.parse

        encoded_text = urllib.parse.quote(performance_text)

        # Choose logo based on OS
        logo_map = {"ubuntu": "ubuntu", "macos": "apple", "windows": "windows"}
        logo = logo_map.get(os_name, "linux")

        return f"https://img.shields.io/badge/{os_name.title()}-{encoded_text}-brightgreen?logo={logo}"

    def update_readme_badges(self, results: Dict[str, Any]) -> None:
        """Update README.md with measured performance data."""
        readme_path = Path("README.md")

        if not readme_path.exists():
            print("Error: README.md not found")
            return

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Detect current OS and update appropriate badge
        current_os = platform.system().lower()
        if current_os == "darwin":
            current_os = "macos"

        performance_text = self.format_for_badge(results, current_os)

        # Update the badge for current OS
        if current_os == "macos":
            pattern = r"(\[!\[Performance macOS\]\(https://img\.shields\.io/badge/macOS-)[^-]+(-.+?\))"
            replacement = f'\\g<1>{performance_text.replace(",", "%2C")}\\g<2>'
        elif current_os == "linux" or current_os == "ubuntu":
            pattern = r"(\[!\[Performance Ubuntu\]\(https://img\.shields\.io/badge/Ubuntu-)[^-]+(-.+?\))"
            replacement = f'\\g<1>{performance_text.replace(",", "%2C")}\\g<2>'
        else:
            print(f"Warning: No badge pattern for OS: {current_os}")
            return

        updated_content = re.sub(pattern, replacement, content)

        if updated_content != content:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print(f"Updated {current_os} performance badge with: {performance_text}")
        else:
            print(f"No badge found to update for OS: {current_os}")


def main() -> None:
    """Main entry point for performance measurement."""
    parser = argparse.ArgumentParser(
        description="Measure mypylogger performance and generate badge data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/measure_performance.py
    python scripts/measure_performance.py --format badge --os macos
    python scripts/measure_performance.py --json
    python scripts/measure_performance.py --update-badges
        """,
    )

    parser.add_argument(
        "--format",
        choices=["badge", "json", "human"],
        default="human",
        help="Output format (default: human)",
    )

    parser.add_argument(
        "--os",
        choices=["ubuntu", "macos", "windows"],
        help="OS name for badge formatting",
    )

    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    parser.add_argument(
        "--update-badges",
        action="store_true",
        help="Update README badges with measured performance",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    # Override format if --json specified
    if args.json:
        args.format = "json"

    # Create measurement instance
    measurement = PerformanceMeasurement(verbose=args.verbose)

    try:
        # Run benchmarks
        results = measurement.run_full_benchmark()

        # Output results based on format
        if args.format == "json":
            print(json.dumps(results, indent=2))
        elif args.format == "badge":
            badge_text = measurement.format_for_badge(results, args.os)
            print(badge_text)
        else:  # human format
            print("Performance Measurement Results")
            print("=" * 40)
            print(f"OS: {results['system']['os']}")
            print(f"Python: {results['system']['python_version']}")
            print()

            print("Latency Metrics:")
            latency = results["latency"]
            print(f"  Average: {latency['average_ms']:.3f}ms")
            print(f"  Median:  {latency['median_ms']:.3f}ms")
            print(f"  95th %:  {latency['p95_ms']:.3f}ms")
            print(f"  Maximum: {latency['max_ms']:.3f}ms")
            print()

            print("Throughput Metrics:")
            throughput = results["throughput"]
            print(f"  Messages: {throughput['messages']}")
            print(f"  Duration: {throughput['duration_seconds']:.3f}s")
            print(f"  Throughput: {throughput['logs_per_second']:.0f} logs/second")
            print()

            print("Memory Usage:")
            memory = results["memory"]
            print(f"  Baseline: {memory['baseline_mb']:.1f}MB")
            print(f"  Final:    {memory['final_mb']:.1f}MB")
            print(f"  Increase: {memory['increase_mb']:.1f}MB")
            print()

            print("Badge Format:")
            badge_text = measurement.format_for_badge(results, args.os)
            print(f"  {badge_text}")

        # Update badges if requested
        if args.update_badges:
            measurement.update_readme_badges(results)

    except KeyboardInterrupt:
        print("\nMeasurement interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during measurement: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

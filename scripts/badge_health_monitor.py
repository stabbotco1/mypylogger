#!/usr/bin/env python3
"""
Badge Health Check System for CI/CD Integration

This script provides comprehensive badge monitoring for automated CI/CD pipelines.
It validates badge URLs, checks for failures, and provides detailed reporting
suitable for integration into GitHub Actions workflows.

Usage:
    python scripts/badge_health_monitor.py [--format FORMAT] [--fail-on-error]

Options:
    --format FORMAT     Output format: human, json, github-actions (default: human)
    --fail-on-error     Exit with code 1 if any badges fail validation
    --timeout SECONDS   HTTP request timeout (default: 10)
    --verbose          Show detailed output
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the existing badge validator
from validate_badges import BadgeValidator  # noqa: E402


class BadgeHealthMonitor:
    """Enhanced badge health monitoring for CI/CD integration."""

    def __init__(self, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.validator = BadgeValidator(timeout=timeout, verbose=verbose)

    def run_health_check(self, readme_path: str = "README.md") -> Dict[str, Any]:
        """Run comprehensive badge health check."""
        if self.verbose:
            print("🔍 Starting badge health check...")

        # Run validation using existing validator
        validation_results = self.validator.validate_all_badges(readme_path)

        if not validation_results["success"]:
            return validation_results

        # Enhanced health metrics
        health_metrics = self.calculate_health_metrics(validation_results)

        # Add health check metadata
        validation_results.update(
            {
                "health_check": {
                    "timestamp": time.time(),
                    "version": "1.0.0",
                    "metrics": health_metrics,
                }
            }
        )

        return validation_results

    def calculate_health_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional health metrics."""
        if not results.get("results"):
            return {}

        response_times = []
        tier_stats = {}

        for result in results["results"]:
            badge = result["badge"]

            # Collect response times
            if result.get("response_time"):
                response_times.append(result["response_time"])

            # Track by tier
            tier = badge.tier
            if tier not in tier_stats:
                tier_stats[tier] = {"total": 0, "passed": 0, "avg_response_time": 0}

            tier_stats[tier]["total"] += 1
            if not result["has_errors"]:
                tier_stats[tier]["passed"] += 1

        # Calculate tier response times
        for tier in tier_stats:
            tier_times = [
                r["response_time"]
                for r in results["results"]
                if r["badge"].tier == tier and r.get("response_time")
            ]
            if tier_times:
                tier_stats[tier]["avg_response_time"] = sum(tier_times) / len(
                    tier_times
                )

        return {
            "total_badges": len(results["results"]),
            "avg_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "max_response_time": max(response_times) if response_times else 0,
            "tier_statistics": tier_stats,
        }

    def format_github_actions_output(self, results: Dict[str, Any]) -> str:
        """Format output for GitHub Actions with proper annotations."""
        output_lines = []

        if results["success"]:
            output_lines.append(
                "::notice title=Badge Health Check::All badges passed validation"
            )

            # Add performance metrics
            if "health_check" in results:
                metrics = results["health_check"]["metrics"]
                avg_time = metrics.get("avg_response_time", 0)
                output_lines.append(
                    f"::notice title=Performance::Average response time: {avg_time:.3f}s"
                )
        else:
            output_lines.append(
                "::error title=Badge Health Check::Badge validation failed"
            )

            # Add specific errors
            for result in results.get("results", []):
                if result["has_errors"]:
                    badge = result["badge"]
                    for error in result["errors"] + result.get("alt_text_errors", []):
                        output_lines.append(
                            f"::error title=Badge Error::{badge.alt_text}: {error}"
                        )

        # Add summary
        passed = results.get("badges_passed", 0)
        total = results.get("badges_found", 0)
        output_lines.append(
            f"::notice title=Summary::{passed}/{total} badges passed validation"
        )

        return "\n".join(output_lines)

    def format_json_output(self, results: Dict[str, Any]) -> str:
        """Format output as JSON for programmatic consumption."""
        # Make results JSON serializable
        json_results: Dict[str, Any] = {}
        for key, value in results.items():
            if key == "results":
                # Convert Badge namedtuples to dicts
                json_results[key] = []
                for result in value:
                    json_result = dict(result)
                    if "badge" in json_result:
                        badge = json_result["badge"]
                        json_result["badge"] = {
                            "url": badge.url,
                            "link": badge.link,
                            "alt_text": badge.alt_text,
                            "tier": badge.tier,
                        }
                    json_results[key].append(json_result)
            else:
                json_results[key] = value

        return json.dumps(json_results, indent=2)

    def format_human_output(self, results: Dict[str, Any]) -> None:
        """Format output for human consumption."""
        self.validator.print_summary(results)


def main() -> None:
    """Main entry point for badge health monitoring."""
    parser = argparse.ArgumentParser(
        description="Badge health check system for CI/CD integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/badge_health_monitor.py
    python scripts/badge_health_monitor.py --format github-actions
    python scripts/badge_health_monitor.py --format json --fail-on-error
        """,
    )

    parser.add_argument(
        "--format",
        choices=["human", "json", "github-actions"],
        default="human",
        help="Output format (default: human)",
    )

    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit with code 1 if any badges fail validation",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to README.md file (default: README.md)",
    )

    args = parser.parse_args()

    # Create health monitor
    monitor = BadgeHealthMonitor(timeout=args.timeout, verbose=args.verbose)

    try:
        # Run health check
        results = monitor.run_health_check(args.readme)

        # Format output
        if args.format == "json":
            print(monitor.format_json_output(results))
        elif args.format == "github-actions":
            print(monitor.format_github_actions_output(results))
        else:  # human
            monitor.format_human_output(results)

        # Exit with appropriate code
        if args.fail_on_error and not results["success"]:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nHealth check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during health check: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

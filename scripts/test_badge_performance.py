#!/usr/bin/env python3
"""
Badge Performance and Fallback Testing Script

This script tests badge loading performance and fallback behavior to ensure:
- Badge loading times meet performance requirements (<200ms average)
- Fallback behavior works when badges are unavailable
- Alt text provides meaningful information when badges fail to load
- Badge accessibility compliance

Usage:
    python scripts/test_badge_performance.py [--iterations N] [--verbose]

Options:
    --iterations N   Number of test iterations (default: 5)
    --verbose       Show detailed performance metrics
"""

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, NamedTuple, Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class PerformanceResult(NamedTuple):
    """Performance test result for a single badge."""

    badge_url: str
    alt_text: str
    response_time: float
    status_code: int
    success: bool
    error: Optional[str] = None


class BadgePerformanceTester:
    """Tests badge loading performance and fallback behavior."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "mypylogger-badge-performance-tester/1.0"}
        )

    def extract_badge_urls_from_readme(
        self, readme_path: str = "README.md"
    ) -> List[Dict[str, str]]:
        """Extract badge URLs and alt text from README.md."""
        import re

        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {readme_path} not found")
            return []

        badges = []

        # Pattern to match markdown badges: [![alt](url)](link)
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"

        matches = re.findall(badge_pattern, content)
        for alt_text, badge_url, link_url in matches:
            badges.append({"url": badge_url, "alt_text": alt_text, "link": link_url})

        return badges

    def test_single_badge_performance(
        self, badge: Dict[str, str], timeout: int = 10
    ) -> PerformanceResult:
        """Test performance of a single badge."""
        try:
            start_time = time.time()
            response = self.session.get(badge["url"], timeout=timeout)
            response_time = time.time() - start_time

            return PerformanceResult(
                badge_url=badge["url"],
                alt_text=badge["alt_text"],
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code == 200,
            )

        except requests.exceptions.Timeout:
            return PerformanceResult(
                badge_url=badge["url"],
                alt_text=badge["alt_text"],
                response_time=timeout,
                status_code=0,
                success=False,
                error="Timeout",
            )
        except requests.exceptions.RequestException as e:
            return PerformanceResult(
                badge_url=badge["url"],
                alt_text=badge["alt_text"],
                response_time=0,
                status_code=0,
                success=False,
                error=str(e),
            )

    def test_concurrent_badge_loading(
        self, badges: List[Dict[str, str]], timeout: int = 10
    ) -> List[PerformanceResult]:
        """Test concurrent loading of all badges."""
        results = []

        with ThreadPoolExecutor(max_workers=len(badges)) as executor:
            # Submit all badge requests concurrently
            future_to_badge = {
                executor.submit(
                    self.test_single_badge_performance, badge, timeout
                ): badge
                for badge in badges
            }

            # Collect results as they complete
            for future in as_completed(future_to_badge):
                result = future.result()
                results.append(result)

        return results

    def test_fallback_behavior(self, badges: List[Dict[str, str]]) -> Dict[str, Any]:
        """Test fallback behavior when badges are unavailable."""
        alt_text_issues: List[Dict[str, str]] = []
        alt_text_coverage = 0
        meaningful_alt_text = 0

        for badge in badges:
            alt_text = badge["alt_text"].strip()

            # Check if alt text exists
            if alt_text:
                alt_text_coverage += 1

                # Check if alt text is meaningful
                if len(alt_text) >= 3 and alt_text.lower() not in [
                    "image",
                    "badge",
                    "icon",
                    "logo",
                ]:
                    meaningful_alt_text += 1
                else:
                    alt_text_issues.append(
                        {
                            "badge": badge["url"],
                            "alt_text": alt_text,
                            "issue": "Not meaningful or too short",
                        }
                    )
            else:
                alt_text_issues.append(
                    {
                        "badge": badge["url"],
                        "alt_text": alt_text,
                        "issue": "Missing alt text",
                    }
                )

        fallback_results: Dict[str, Any] = {
            "alt_text_coverage": alt_text_coverage,
            "meaningful_alt_text": meaningful_alt_text,
            "total_badges": len(badges),
            "alt_text_issues": alt_text_issues,
        }

        return fallback_results

    def run_performance_test(
        self, iterations: int = 5, readme_path: str = "README.md"
    ) -> Dict[str, Any]:
        """Run comprehensive performance test."""
        badges = self.extract_badge_urls_from_readme(readme_path)

        if not badges:
            return {
                "success": False,
                "error": "No badges found in README.md",
                "badges_found": 0,
            }

        print(
            f"🚀 Testing badge performance with {len(badges)} badges over {iterations} iterations..."
        )

        all_results = []
        iteration_times = []

        for i in range(iterations):
            if self.verbose:
                print(f"  Iteration {i+1}/{iterations}...")

            start_time = time.time()
            results = self.test_concurrent_badge_loading(badges)
            total_time = time.time() - start_time

            all_results.extend(results)
            iteration_times.append(total_time)

            if self.verbose:
                successful = sum(1 for r in results if r.success)
                avg_time = statistics.mean(
                    [r.response_time for r in results if r.success]
                )
                print(
                    f"    {successful}/{len(badges)} successful, avg: {avg_time:.3f}s, total: {total_time:.3f}s"
                )

        # Calculate performance statistics
        successful_results = [r for r in all_results if r.success]
        response_times = [r.response_time for r in successful_results]

        performance_stats = {}
        if response_times:
            performance_stats = {
                "average_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "std_dev_response_time": (
                    statistics.stdev(response_times) if len(response_times) > 1 else 0
                ),
            }

        # Test fallback behavior
        fallback_results = self.test_fallback_behavior(badges)

        # Calculate success rates
        total_tests = len(all_results)
        successful_tests = len(successful_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        return {
            "success": success_rate >= 95,  # 95% success rate threshold
            "badges_found": len(badges),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "performance_stats": performance_stats,
            "fallback_results": fallback_results,
            "iteration_stats": {
                "average_iteration_time": statistics.mean(iteration_times),
                "min_iteration_time": min(iteration_times),
                "max_iteration_time": max(iteration_times),
            },
            "failed_badges": [r for r in all_results if not r.success],
        }

    def print_performance_report(self, results: Dict[str, Any]) -> None:
        """Print formatted performance test report."""
        if not results.get("badges_found"):
            print("❌ No badges found to test")
            return

        print("\n📊 Badge Performance Test Report")
        print("=" * 60)

        # Overall results
        if results["success"]:
            print("✅ Badge performance meets requirements")
        else:
            print("❌ Badge performance issues detected")

        print(
            f"🎯 Success Rate: {results['success_rate']:.1f}% ({results['successful_tests']}/{results['total_tests']})"
        )

        # Performance metrics
        if results["performance_stats"]:
            stats = results["performance_stats"]
            print("\n⚡ Performance Metrics")
            print(f"Average response time: {stats['average_response_time']:.3f}s")
            print(f"Median response time: {stats['median_response_time']:.3f}s")
            print(f"Min response time: {stats['min_response_time']:.3f}s")
            print(f"Max response time: {stats['max_response_time']:.3f}s")
            print(f"Standard deviation: {stats['std_dev_response_time']:.3f}s")

            # Performance assessment
            avg_time = stats["average_response_time"]
            if avg_time < 0.2:
                print("✅ Excellent performance (<200ms average)")
            elif avg_time < 0.5:
                print("⚠️  Good performance (200-500ms average)")
            else:
                print("❌ Poor performance (>500ms average)")

        # Iteration statistics
        iter_stats = results["iteration_stats"]
        print("\n🔄 Iteration Statistics")
        print(f"Average total load time: {iter_stats['average_iteration_time']:.3f}s")
        print(f"Fastest iteration: {iter_stats['min_iteration_time']:.3f}s")
        print(f"Slowest iteration: {iter_stats['max_iteration_time']:.3f}s")

        # Fallback behavior
        fallback = results["fallback_results"]
        print("\n🛡️  Fallback Behavior Assessment")
        alt_coverage = (fallback["alt_text_coverage"] / fallback["total_badges"]) * 100
        meaningful_coverage = (
            fallback["meaningful_alt_text"] / fallback["total_badges"]
        ) * 100

        print(
            f"Alt text coverage: {alt_coverage:.1f}% ({fallback['alt_text_coverage']}/{fallback['total_badges']})"
        )
        print(
            f"Meaningful alt text: {meaningful_coverage:.1f}% ({fallback['meaningful_alt_text']}/{fallback['total_badges']})"
        )

        if alt_coverage >= 100 and meaningful_coverage >= 90:
            print("✅ Excellent accessibility compliance")
        elif alt_coverage >= 90:
            print("⚠️  Good accessibility (minor improvements needed)")
        else:
            print("❌ Poor accessibility (significant improvements needed)")

        # Failed badges
        if results["failed_badges"]:
            print("\n❌ Failed Badge Details")
            print("=" * 60)
            for badge in results["failed_badges"]:
                print(f"Badge: {badge.alt_text}")
                print(f"URL: {badge.badge_url}")
                print(f"Error: {badge.error or f'HTTP {badge.status_code}'}")
                print()

        # Alt text issues
        if fallback["alt_text_issues"]:
            print("\n⚠️  Alt Text Issues")
            print("=" * 60)
            for issue in fallback["alt_text_issues"]:
                print(f"Badge: {issue['badge']}")
                print(f"Alt text: '{issue['alt_text']}'")
                print(f"Issue: {issue['issue']}")
                print()

        # Recommendations
        print("\n💡 Recommendations")
        print("=" * 60)

        if results["performance_stats"]:
            avg_time = results["performance_stats"]["average_response_time"]
            if avg_time > 0.2:
                print("• Consider optimizing badge URLs or using cached versions")

            if results["success_rate"] < 95:
                print("• Investigate failed badge URLs and fix broken badges")

        if fallback["alt_text_issues"]:
            print("• Improve alt text for better accessibility compliance")
            print("• Ensure all badges have meaningful, descriptive alt text")

        if not results["success"]:
            print("• Run badge validation script to identify specific issues")
            print("• Consider implementing badge monitoring for production")


def main() -> None:
    """Main entry point for badge performance testing."""
    parser = argparse.ArgumentParser(
        description="Test badge loading performance and fallback behavior",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/test_badge_performance.py
    python scripts/test_badge_performance.py --iterations 10 --verbose
        """,
    )

    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=5,
        help="Number of test iterations (default: 5)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed performance metrics for each iteration",
    )

    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to README.md file (default: README.md)",
    )

    args = parser.parse_args()

    # Create tester and run performance test
    tester = BadgePerformanceTester(verbose=args.verbose)
    results = tester.run_performance_test(
        iterations=args.iterations, readme_path=args.readme
    )

    # Print results
    tester.print_performance_report(results)

    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()

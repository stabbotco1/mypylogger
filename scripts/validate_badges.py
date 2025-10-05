#!/usr/bin/env python3
"""
Badge Validation Script

This script validates all GitHub badges in the README.md file to ensure:
- Badge URLs return HTTP 200 status
- Badge links navigate to correct destinations
- Alt text provides meaningful accessibility information
- No broken or "unknown status" badges under normal conditions

Usage:
    python scripts/validate_badges.py [--verbose] [--timeout SECONDS]

Options:
    --verbose    Show detailed output for each badge check
    --timeout    HTTP request timeout in seconds (default: 10)
"""

import argparse
import re
import sys
import time
from typing import Any, Dict, List, NamedTuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class Badge(NamedTuple):
    """Represents a badge with its URL, link, and alt text."""

    url: str
    link: str
    alt_text: str
    tier: str


class BadgeValidator:
    """Validates GitHub badges for accessibility, functionality, and performance."""

    def __init__(self, timeout: int = 10, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "mypylogger-badge-validator/1.0"})

    def extract_badges_from_readme(self, readme_path: str = "README.md") -> List[Badge]:
        """Extract all badges from README.md file."""
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {readme_path} not found")
            return []

        badges = []
        current_tier = "Unknown"

        # Pattern to match markdown badges: [![alt](url)](link)
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"

        lines = content.split("\n")
        for line in lines:
            # Track current tier based on comments
            if "<!-- Core Status (Tier 1) -->" in line:
                current_tier = "Tier 1: Core Status"
            elif "<!-- Quality & Compatibility (Tier 2) -->" in line:
                current_tier = "Tier 2: Quality & Compatibility"
            elif "<!-- Performance & Community (Tier 3) -->" in line:
                current_tier = "Tier 3: Performance & Community"

            # Find badges in current line
            matches = re.findall(badge_pattern, line)
            for alt_text, badge_url, link_url in matches:
                badges.append(
                    Badge(
                        url=badge_url,
                        link=link_url,
                        alt_text=alt_text,
                        tier=current_tier,
                    )
                )

        return badges

    def validate_badge_url(self, badge: Badge) -> Dict[str, Any]:
        """Validate a single badge URL."""
        errors: List[str] = []
        result: Dict[str, Any] = {
            "badge": badge,
            "url_accessible": False,
            "link_accessible": False,
            "response_time": None,
            "status_code": None,
            "link_status_code": None,
            "errors": errors,
        }

        # Validate badge URL
        try:
            start_time = time.time()
            response = self.session.get(badge.url, timeout=self.timeout)
            result["response_time"] = time.time() - start_time
            result["status_code"] = response.status_code
            result["url_accessible"] = response.status_code == 200

            if response.status_code != 200:
                errors.append(f"Badge URL returned {response.status_code}")

        except requests.exceptions.Timeout:
            errors.append(f"Badge URL timeout after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            errors.append(f"Badge URL error: {str(e)}")

        # Validate link URL (with shorter timeout for performance)
        try:
            link_response = self.session.head(
                badge.link, timeout=5, allow_redirects=True
            )
            result["link_status_code"] = link_response.status_code
            result["link_accessible"] = link_response.status_code in [200, 301, 302]

            if not result["link_accessible"]:
                errors.append(f"Badge link returned {link_response.status_code}")

        except requests.exceptions.Timeout:
            errors.append("Badge link timeout")
        except requests.exceptions.RequestException as e:
            errors.append(f"Badge link error: {str(e)}")

        return result

    def validate_alt_text(self, badge: Badge) -> List[str]:
        """Validate badge alt text for accessibility."""
        errors = []

        if not badge.alt_text:
            errors.append("Missing alt text")
        elif len(badge.alt_text.strip()) < 3:
            errors.append("Alt text too short (less than 3 characters)")
        elif badge.alt_text.strip().lower() in ["image", "badge", "icon"]:
            errors.append("Alt text not descriptive (generic terms)")

        return errors

    def check_badge_performance(self, badges: List[Badge]) -> Dict[str, Any]:
        """Check overall badge loading performance."""
        if not badges:
            return {"total_time": 0, "average_time": 0, "slowest_badge": None}

        total_time = 0
        slowest_time = 0
        slowest_badge = None

        for badge in badges:
            result = self.validate_badge_url(badge)
            if result["response_time"]:
                total_time += result["response_time"]
                if result["response_time"] > slowest_time:
                    slowest_time = result["response_time"]
                    slowest_badge = badge

        return {
            "total_time": total_time,
            "average_time": total_time / len(badges) if badges else 0,
            "slowest_badge": slowest_badge,
            "slowest_time": slowest_time,
        }

    def validate_all_badges(self, readme_path: str = "README.md") -> Dict[str, Any]:
        """Validate all badges and return comprehensive results."""
        badges = self.extract_badges_from_readme(readme_path)

        if not badges:
            return {
                "success": False,
                "error": "No badges found in README.md",
                "badges_found": 0,
                "results": [],
            }

        results = []
        total_errors = 0

        print(f"🔍 Validating {len(badges)} badges...")
        if self.verbose:
            print()

        for i, badge in enumerate(badges, 1):
            if self.verbose:
                print(f"  [{i}/{len(badges)}] Checking {badge.alt_text}...")

            # Validate URL and link
            url_result = self.validate_badge_url(badge)

            # Validate alt text
            alt_errors = self.validate_alt_text(badge)

            # Combine results
            badge_result = {
                **url_result,
                "alt_text_errors": alt_errors,
                "has_errors": bool(url_result["errors"] or alt_errors),
            }

            if badge_result["has_errors"]:
                total_errors += 1

            results.append(badge_result)

            if self.verbose and badge_result["has_errors"]:
                for error in url_result["errors"] + alt_errors:
                    print(f"    ❌ {error}")
            elif self.verbose:
                print(f"    ✅ OK ({url_result['response_time']:.2f}s)")

        # Calculate performance metrics
        performance = self.check_badge_performance(badges)

        return {
            "success": total_errors == 0,
            "badges_found": len(badges),
            "badges_passed": len(badges) - total_errors,
            "badges_failed": total_errors,
            "results": results,
            "performance": performance,
        }

    def print_summary(self, validation_results: Dict[str, Any]) -> None:
        """Print a formatted summary of validation results."""
        if not validation_results.get("badges_found"):
            print("❌ No badges found to validate")
            return

        print("\n📊 Badge Validation Summary")
        print("=" * 50)

        # Overall status
        if validation_results["success"]:
            print("✅ All badges passed validation")
        else:
            print(f"❌ {validation_results['badges_failed']} badges failed validation")

        print(f"📈 Badges found: {validation_results['badges_found']}")
        print(f"✅ Badges passed: {validation_results['badges_passed']}")
        print(f"❌ Badges failed: {validation_results['badges_failed']}")

        # Performance metrics
        perf = validation_results["performance"]
        print("\n⚡ Performance Metrics")
        print(f"Average load time: {perf['average_time']:.2f}s")
        print(f"Total load time: {perf['total_time']:.2f}s")
        if perf["slowest_badge"]:
            print(
                f"Slowest badge: {perf['slowest_badge'].alt_text} ({perf['slowest_time']:.2f}s)"
            )

        # Detailed errors
        if not validation_results["success"]:
            print("\n🔍 Detailed Error Report")
            print("=" * 50)

            for result in validation_results["results"]:
                if result["has_errors"]:
                    badge = result["badge"]
                    print(f"\n❌ {badge.alt_text} ({badge.tier})")
                    print(f"   URL: {badge.url}")
                    print(f"   Link: {badge.link}")

                    all_errors = result["errors"] + result["alt_text_errors"]
                    for error in all_errors:
                        print(f"   • {error}")

        # Tier breakdown
        tier_stats = {}
        for result in validation_results["results"]:
            tier = result["badge"].tier
            if tier not in tier_stats:
                tier_stats[tier] = {"total": 0, "passed": 0}
            tier_stats[tier]["total"] += 1
            if not result["has_errors"]:
                tier_stats[tier]["passed"] += 1

        print("\n📋 Badges by Tier")
        print("=" * 50)
        for tier, stats in tier_stats.items():
            status = "✅" if stats["passed"] == stats["total"] else "❌"
            print(f"{status} {tier}: {stats['passed']}/{stats['total']} passed")


def main() -> None:
    """Main entry point for badge validation script."""
    parser = argparse.ArgumentParser(
        description="Validate GitHub badges in README.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/validate_badges.py
    python scripts/validate_badges.py --verbose
    python scripts/validate_badges.py --timeout 15 --verbose
        """,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each badge check",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )

    parser.add_argument(
        "--readme",
        default="README.md",
        help="Path to README.md file (default: README.md)",
    )

    args = parser.parse_args()

    # Create validator and run validation
    validator = BadgeValidator(timeout=args.timeout, verbose=args.verbose)
    results = validator.validate_all_badges(args.readme)

    # Print results
    validator.print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()

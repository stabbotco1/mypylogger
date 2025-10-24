#!/usr/bin/env python3
"""Documentation Quality Badge Generator for mypylogger v0.2.0.

This script generates shields.io compatible badges for documentation quality metrics
including docstring coverage, link validation status, and overall documentation health.

Requirements Addressed:
- 16.5: Documentation quality metrics and reporting
- Badge generation for documentation status display
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

# Constants for badge thresholds
EXCELLENT_THRESHOLD = 100
GOOD_THRESHOLD = 95
FAIR_THRESHOLD = 80
POOR_THRESHOLD = 60
QUALITY_EXCELLENT = 98
QUALITY_GOOD = 90


class DocumentationBadgeGenerator:
    """Generator for documentation quality badges."""

    def __init__(self, project_root: Path) -> None:
        """Initialize the badge generator.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.badge_data_dir = project_root / "badge-data"
        self.badge_data_dir.mkdir(exist_ok=True)

    def generate_docstring_coverage_badge(self, coverage_percent: float) -> dict[str, Any]:
        """Generate docstring coverage badge data.

        Args:
            coverage_percent: Docstring coverage percentage (0-100)

        Returns:
            Badge data dictionary for shields.io
        """
        # Determine badge color based on coverage
        if coverage_percent >= EXCELLENT_THRESHOLD:
            color = "brightgreen"
            status = "excellent"
        elif coverage_percent >= GOOD_THRESHOLD:
            color = "green"
            status = "good"
        elif coverage_percent >= FAIR_THRESHOLD:
            color = "yellow"
            status = "fair"
        elif coverage_percent >= POOR_THRESHOLD:
            color = "orange"
            status = "poor"
        else:
            color = "red"
            status = "critical"

        badge_data = {
            "schemaVersion": 1,
            "label": "docstring coverage",
            "message": f"{coverage_percent:.1f}%",
            "color": color,
        }

        # Save badge data
        badge_file = self.badge_data_dir / "docstring-coverage-badge.json"
        with badge_file.open("w") as f:
            json.dump(badge_data, f, indent=2)

        # Save detailed summary
        summary_data = {
            "coverage_percent": coverage_percent,
            "status": status,
            "badge_color": color,
            "threshold_met": coverage_percent >= EXCELLENT_THRESHOLD,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "badge_url": f"https://img.shields.io/badge/docstring%20coverage-{coverage_percent:.1f}%25-{color}",
        }

        summary_file = self.badge_data_dir / "docstring-coverage-summary.json"
        with summary_file.open("w") as f:
            json.dump(summary_data, f, indent=2)

        return badge_data

    def generate_link_validation_badge(
        self, validation_status: str, broken_count: int = 0
    ) -> dict[str, Any]:
        """Generate link validation badge data.

        Args:
            validation_status: Status of link validation ("pass", "fail", "error")
            broken_count: Number of broken links found

        Returns:
            Badge data dictionary for shields.io
        """
        if validation_status == "pass":
            color = "brightgreen"
            message = "all links valid"
        elif validation_status == "fail":
            color = "red"
            message = f"{broken_count} broken links" if broken_count > 0 else "links broken"
        else:  # error
            color = "lightgrey"
            message = "validation error"

        badge_data = {
            "schemaVersion": 1,
            "label": "links",
            "message": message,
            "color": color,
        }

        # Save badge data
        badge_file = self.badge_data_dir / "link-validation-badge.json"
        with badge_file.open("w") as f:
            json.dump(badge_data, f, indent=2)

        # Save detailed summary
        summary_data = {
            "validation_status": validation_status,
            "broken_count": broken_count,
            "badge_color": color,
            "message": message,
            "all_links_valid": validation_status == "pass",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "badge_url": (
                f"https://img.shields.io/badge/links-{message.replace(' ', '%20')}-{color}"
            ),
        }

        summary_file = self.badge_data_dir / "link-validation-summary.json"
        with summary_file.open("w") as f:
            json.dump(summary_data, f, indent=2)

        return badge_data

    def generate_spelling_badge(self, spelling_status: str, error_count: int = 0) -> dict[str, Any]:
        """Generate spelling and grammar badge data.

        Args:
            spelling_status: Status of spelling validation ("pass", "fail", "error")
            error_count: Number of spelling/grammar errors found

        Returns:
            Badge data dictionary for shields.io
        """
        if spelling_status == "pass":
            color = "brightgreen"
            message = "no errors"
        elif spelling_status == "fail":
            color = "red"
            message = f"{error_count} errors" if error_count > 0 else "errors found"
        else:  # error
            color = "lightgrey"
            message = "check failed"

        badge_data = {
            "schemaVersion": 1,
            "label": "spelling",
            "message": message,
            "color": color,
        }

        # Save badge data
        badge_file = self.badge_data_dir / "spelling-badge.json"
        with badge_file.open("w") as f:
            json.dump(badge_data, f, indent=2)

        # Save detailed summary
        summary_data = {
            "spelling_status": spelling_status,
            "error_count": error_count,
            "badge_color": color,
            "message": message,
            "no_errors": spelling_status == "pass",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "badge_url": (
                f"https://img.shields.io/badge/spelling-{message.replace(' ', '%20')}-{color}"
            ),
        }

        summary_file = self.badge_data_dir / "spelling-summary.json"
        with summary_file.open("w") as f:
            json.dump(summary_data, f, indent=2)

        return badge_data

    def generate_overall_docs_badge(
        self, overall_status: str, quality_score: float = 0.0
    ) -> dict[str, Any]:
        """Generate overall documentation quality badge.

        Args:
            overall_status: Overall documentation status ("pass", "fail", "error")
            quality_score: Overall quality score (0-100)

        Returns:
            Badge data dictionary for shields.io
        """
        if overall_status == "pass":
            if quality_score >= QUALITY_EXCELLENT:
                color = "brightgreen"
                message = "excellent"
            elif quality_score >= QUALITY_GOOD:
                color = "green"
                message = "good"
            else:
                color = "yellowgreen"
                message = "passing"
        elif overall_status == "fail":
            color = "red"
            message = "failing"
        else:  # error
            color = "lightgrey"
            message = "unknown"

        badge_data = {
            "schemaVersion": 1,
            "label": "docs",
            "message": message,
            "color": color,
        }

        # Save badge data
        badge_file = self.badge_data_dir / "docs-quality-badge.json"
        with badge_file.open("w") as f:
            json.dump(badge_data, f, indent=2)

        # Save detailed summary
        summary_data = {
            "overall_status": overall_status,
            "quality_score": quality_score,
            "badge_color": color,
            "message": message,
            "docs_passing": overall_status == "pass",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "badge_url": f"https://img.shields.io/badge/docs-{message}-{color}",
        }

        summary_file = self.badge_data_dir / "docs-quality-summary.json"
        with summary_file.open("w") as f:
            json.dump(summary_data, f, indent=2)

        return badge_data

    def generate_api_completeness_badge(
        self, completeness_status: str, missing_count: int = 0
    ) -> dict[str, Any]:
        """Generate API documentation completeness badge.

        Args:
            completeness_status: Status of API completeness ("pass", "fail", "error")
            missing_count: Number of APIs with missing documentation

        Returns:
            Badge data dictionary for shields.io
        """
        if completeness_status == "pass":
            color = "brightgreen"
            message = "complete"
        elif completeness_status == "fail":
            color = "red"
            message = f"{missing_count} missing" if missing_count > 0 else "incomplete"
        else:  # error
            color = "lightgrey"
            message = "check failed"

        badge_data = {
            "schemaVersion": 1,
            "label": "API docs",
            "message": message,
            "color": color,
        }

        # Save badge data
        badge_file = self.badge_data_dir / "api-completeness-badge.json"
        with badge_file.open("w") as f:
            json.dump(badge_data, f, indent=2)

        # Save detailed summary
        summary_data = {
            "completeness_status": completeness_status,
            "missing_count": missing_count,
            "badge_color": color,
            "message": message,
            "api_complete": completeness_status == "pass",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "badge_url": (
                f"https://img.shields.io/badge/API%20docs-{message.replace(' ', '%20')}-{color}"
            ),
        }

        summary_file = self.badge_data_dir / "api-completeness-summary.json"
        with summary_file.open("w") as f:
            json.dump(summary_data, f, indent=2)

        return badge_data

    def generate_all_badges_from_results(self, results_file: Path) -> dict[str, dict[str, Any]]:
        """Generate all documentation badges from validation results.

        Args:
            results_file: Path to validation results JSON file

        Returns:
            Dictionary of all generated badge data
        """
        try:
            with results_file.open() as f:
                results = json.load(f)
        except Exception as e:
            print(f"❌ Error reading results file {results_file}: {e}")
            return {}

        badges = {}

        # Generate docstring coverage badge
        docstring_data = results.get("docstring_coverage", {})
        coverage = docstring_data.get("coverage", 0.0)
        badges["docstring_coverage"] = self.generate_docstring_coverage_badge(coverage)

        # Generate link validation badge
        link_data = results.get("link_validation", {})
        link_status = link_data.get("status", "error")
        broken_count = len(link_data.get("broken_links", []))
        badges["link_validation"] = self.generate_link_validation_badge(link_status, broken_count)

        # Generate spelling badge
        spelling_data = results.get("spelling_grammar", {})
        spelling_status = spelling_data.get("status", "error")
        error_count = len(spelling_data.get("errors", []))
        badges["spelling"] = self.generate_spelling_badge(spelling_status, error_count)

        # Generate API completeness badge
        api_data = results.get("api_completeness", {})
        api_status = api_data.get("status", "error")
        missing_count = len(api_data.get("missing", []))
        badges["api_completeness"] = self.generate_api_completeness_badge(api_status, missing_count)

        # Calculate overall quality score
        quality_score = self.calculate_quality_score(results)
        overall_status = results.get("overall_status", "error")
        badges["overall"] = self.generate_overall_docs_badge(overall_status, quality_score)

        return badges

    def calculate_quality_score(self, results: dict[str, Any]) -> float:
        """Calculate overall documentation quality score.

        Args:
            results: Validation results dictionary

        Returns:
            Quality score from 0-100
        """
        # Weights for different quality aspects
        weights = {
            "docstring_coverage": 0.30,
            "link_validation": 0.20,
            "spelling_grammar": 0.20,
            "formatting_style": 0.15,
            "api_completeness": 0.15,
        }

        total_score = 0.0
        total_weight = 0.0

        for category, weight in weights.items():
            category_data = results.get(category, {})
            status = category_data.get("status", "error")

            if status == "pass":
                score = 100.0
            elif status == "fail":
                # Partial credit based on specific metrics
                if category == "docstring_coverage":
                    score = category_data.get("coverage", 0.0)
                elif category == "link_validation":
                    broken_count = len(category_data.get("broken_links", []))
                    # Assume 20 total links for scoring (adjust as needed)
                    score = max(0, 100 - (broken_count * 5))
                elif category == "spelling_grammar":
                    error_count = len(category_data.get("errors", []))
                    # Deduct 2 points per error
                    score = max(0, 100 - (error_count * 2))
                else:
                    score = 0.0  # Other categories are pass/fail
            else:  # error
                score = 0.0

            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def generate_badge_markdown(self) -> str:
        """Generate Markdown snippet for README badges.

        Returns:
            Markdown string with badge links
        """
        base_url = "https://img.shields.io"

        badges = [
            {
                "name": "Documentation",
                "file": "docs-quality-badge.json",
                "alt": "Documentation Quality",
            },
            {
                "name": "Docstring Coverage",
                "file": "docstring-coverage-badge.json",
                "alt": "Docstring Coverage",
            },
            {
                "name": "Links",
                "file": "link-validation-badge.json",
                "alt": "Link Validation",
            },
            {
                "name": "Spelling",
                "file": "spelling-badge.json",
                "alt": "Spelling Check",
            },
            {
                "name": "API Docs",
                "file": "api-completeness-badge.json",
                "alt": "API Documentation",
            },
        ]

        markdown_lines = ["## Documentation Quality Badges", ""]

        for badge in badges:
            badge_file = self.badge_data_dir / badge["file"]
            if badge_file.exists():
                try:
                    with badge_file.open() as f:
                        badge_data = json.load(f)

                    label = badge_data["label"].replace(" ", "%20")
                    message = badge_data["message"].replace(" ", "%20")
                    color = badge_data["color"]

                    badge_url = f"{base_url}/badge/{label}-{message}-{color}"
                    markdown_lines.append(f"![{badge['alt']}]({badge_url})")

                except Exception as e:
                    print(f"⚠️ Warning: Could not generate markdown for {badge['name']}: {e}")

        return "\n".join(markdown_lines)


def main() -> None:
    """Main entry point for badge generation."""
    parser = argparse.ArgumentParser(
        description="Generate documentation quality badges for mypylogger v0.2.0"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Path to project root directory"
    )
    parser.add_argument("--results-file", type=Path, help="Path to validation results JSON file")
    parser.add_argument(
        "--generate-markdown",
        action="store_true",
        help="Generate Markdown snippet for README badges",
    )
    parser.add_argument(
        "--docstring-coverage",
        type=float,
        help="Docstring coverage percentage (if not using results file)",
    )
    parser.add_argument(
        "--link-status",
        choices=["pass", "fail", "error"],
        help="Link validation status (if not using results file)",
    )
    parser.add_argument(
        "--spelling-status",
        choices=["pass", "fail", "error"],
        help="Spelling validation status (if not using results file)",
    )

    args = parser.parse_args()

    generator = DocumentationBadgeGenerator(args.project_root)

    if args.results_file and args.results_file.exists():
        # Generate badges from validation results
        print("📊 Generating documentation quality badges from validation results...")
        badges = generator.generate_all_badges_from_results(args.results_file)

        if badges:
            print("✅ Generated badges:")
            for badge_type, badge_data in badges.items():
                print(f"  - {badge_type}: {badge_data['message']} ({badge_data['color']})")
        else:
            print("❌ Failed to generate badges from results file")
            sys.exit(1)

    else:
        # Generate individual badges from command line arguments
        print("📊 Generating individual documentation quality badges...")

        if args.docstring_coverage is not None:
            badge = generator.generate_docstring_coverage_badge(args.docstring_coverage)
            print(f"✅ Docstring coverage badge: {badge['message']} ({badge['color']})")

        if args.link_status:
            badge = generator.generate_link_validation_badge(args.link_status)
            print(f"✅ Link validation badge: {badge['message']} ({badge['color']})")

        if args.spelling_status:
            badge = generator.generate_spelling_badge(args.spelling_status)
            print(f"✅ Spelling badge: {badge['message']} ({badge['color']})")

    if args.generate_markdown:
        print("\n📝 Generating Markdown snippet for README badges...")
        markdown = generator.generate_badge_markdown()

        markdown_file = args.project_root / "docs-badges.md"
        with markdown_file.open("w") as f:
            f.write(markdown)

        print(f"✅ Markdown snippet saved to: {markdown_file}")
        print("\nMarkdown content:")
        print("-" * 40)
        print(markdown)

    print(f"\n📁 Badge data saved to: {generator.badge_data_dir}")


if __name__ == "__main__":
    main()

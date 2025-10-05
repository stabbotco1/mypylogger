#!/usr/bin/env python3
"""
Documentation Date Validation Script

This script scans project documentation for potentially outdated dates and provides
warnings for dates that may need updating. It helps maintain accurate documentation
by identifying dates that are significantly in the past.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Match, Optional, Tuple


class DateValidationResult:
    """Result of date validation for a single file."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.outdated_dates: List[Tuple[int, str, str]] = (
            []
        )  # (line_num, date_str, context)
        self.suspicious_dates: List[Tuple[int, str, str]] = (
            []
        )  # (line_num, date_str, context)
        self.acceptable_dates: List[Tuple[int, str, str]] = (
            []
        )  # (line_num, date_str, context)

    def add_outdated(self, line_num: int, date_str: str, context: str) -> None:
        """Add an outdated date finding."""
        self.outdated_dates.append((line_num, date_str, context))

    def add_suspicious(self, line_num: int, date_str: str, context: str) -> None:
        """Add a suspicious date finding."""
        self.suspicious_dates.append((line_num, date_str, context))

    def add_acceptable(self, line_num: int, date_str: str, context: str) -> None:
        """Add an acceptable date finding."""
        self.acceptable_dates.append((line_num, date_str, context))

    @property
    def has_issues(self) -> bool:
        """Check if this file has any date issues."""
        return len(self.outdated_dates) > 0 or len(self.suspicious_dates) > 0


class DocumentationDateValidator:
    """Validates dates in documentation files."""

    def __init__(self) -> None:
        self.current_date = datetime.now()

        # Date patterns to search for
        self.date_patterns = [
            # ISO 8601 dates: 2024-01-15
            (r"\b(20\d{2})-(\d{2})-(\d{2})\b", "iso_date"),
            # Timestamps: 2024-01-15T10:30:45.123Z
            (
                r"\b(20\d{2})-(\d{2})-(\d{2})T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?\b",
                "iso_timestamp",
            ),
            # Month Year: January 2024, October 2025
            (
                r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b",
                "month_year",
            ),
            # Last Updated/Scan patterns
            (r"Last\s+(Updated|Scan|Modified):\s*([^\n]+)", "last_updated"),
            # Expires patterns
            (r'expires:\s*["\']?(20\d{2}-\d{2}-\d{2})["\']?', "expires"),
        ]

        # Files to exclude from validation
        self.excluded_files = {
            "CHANGELOG.md",  # Historical dates are expected
            "LICENSE",  # Copyright dates are expected
        }

        # Directories to exclude
        self.excluded_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            "venv",
            ".venv",
            "build",
            "dist",
            ".tox",
        }

        # Patterns that indicate acceptable historical dates
        self.acceptable_contexts = [
            r"test.*data",  # Test data
            r"example",  # Examples
            r"sample",  # Sample data
            r"mock",  # Mock data
            r"fixture",  # Test fixtures
            r"copyright",  # Copyright dates
            r"version.*history",  # Version history
            r"changelog",  # Changelog entries
            r"version.*2012-10-17",  # AWS policy version identifiers
            r'"Version":\s*"2012-10-17"',  # AWS IAM policy version
            r"aws.*policy",  # AWS policy documents
            r"python.*released",  # Historical Python release dates
            r"historical.*reference",  # Historical references
            r"eol.*\d{4}",  # End-of-life dates
        ]

    def is_acceptable_context(self, context: str, file_path: str) -> bool:
        """Check if a date appears in an acceptable context."""
        context_lower = context.lower()
        file_path_lower = file_path.lower()

        # Check if it's in a test file
        if "test" in file_path_lower:
            return True

        # Check for acceptable context patterns
        for pattern in self.acceptable_contexts:
            if re.search(pattern, context_lower) or re.search(pattern, file_path_lower):
                return True

        return False

    def parse_date_from_match(
        self, match: Match[str], pattern_type: str
    ) -> Optional[datetime]:
        """Parse a datetime from a regex match based on pattern type."""
        try:
            if pattern_type in ["iso_date", "iso_timestamp"]:
                year, month, day = (
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
                return datetime(year, month, day)
            elif pattern_type == "month_year":
                month_name = match.group(1)
                year = int(match.group(2))
                month_map = {
                    "January": 1,
                    "February": 2,
                    "March": 3,
                    "April": 4,
                    "May": 5,
                    "June": 6,
                    "July": 7,
                    "August": 8,
                    "September": 9,
                    "October": 10,
                    "November": 11,
                    "December": 12,
                }
                month = month_map.get(month_name, 1)
                return datetime(year, month, 1)
            elif pattern_type == "expires":
                date_str = match.group(1)
                year_str, month_str, day_str = date_str.split("-")
                return datetime(int(year_str), int(month_str), int(day_str))
            elif pattern_type == "last_updated":
                # Try to parse the date part
                date_part = match.group(2).strip()
                # Handle various formats
                if re.match(r"\d{4}-\d{2}-\d{2}", date_part):
                    year_str, month_str, day_str = date_part.split("-")[:3]
                    return datetime(int(year_str), int(month_str), int(day_str))
                elif "January" in date_part or "February" in date_part:  # etc.
                    # Handle "January 2024" format
                    month_match = re.search(
                        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})",
                        date_part,
                    )
                    if month_match:
                        return self.parse_date_from_match(month_match, "month_year")
        except (ValueError, AttributeError):
            pass

        return None

    def validate_file(self, file_path: str) -> DateValidationResult:
        """Validate dates in a single file."""
        result = DateValidationResult(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (UnicodeDecodeError, IOError):
            return result

        for line_num, line in enumerate(lines, 1):
            for pattern, pattern_type in self.date_patterns:
                for match in re.finditer(pattern, line):
                    date_str = match.group(0)
                    context = line.strip()

                    # Parse the date
                    parsed_date = self.parse_date_from_match(match, pattern_type)
                    if not parsed_date:
                        continue

                    # Calculate age
                    age_days = (self.current_date - parsed_date).days

                    # Categorize the date
                    if self.is_acceptable_context(context, file_path):
                        result.add_acceptable(line_num, date_str, context)
                    elif age_days > 365:  # More than 1 year old
                        result.add_outdated(line_num, date_str, context)
                    elif age_days > 90:  # More than 3 months old
                        result.add_suspicious(line_num, date_str, context)
                    else:
                        result.add_acceptable(line_num, date_str, context)

        return result

    def should_validate_file(self, file_path: Path) -> bool:
        """Check if a file should be validated."""
        # Skip if file is in excluded list
        if file_path.name in self.excluded_files:
            return False

        # Skip if any parent directory is excluded
        for part in file_path.parts:
            if part in self.excluded_dirs:
                return False

        # Only validate text files (markdown, text, etc.)
        if file_path.suffix.lower() in [".md", ".txt", ".rst", ".yml", ".yaml"]:
            return True

        return False

    def validate_project(
        self, project_root: str = "."
    ) -> Dict[str, DateValidationResult]:
        """Validate all documentation files in the project."""
        results = {}
        project_path = Path(project_root)

        for file_path in project_path.rglob("*"):
            if file_path.is_file() and self.should_validate_file(file_path):
                relative_path = str(file_path.relative_to(project_path))
                result = self.validate_file(str(file_path))
                if (
                    result.has_issues or result.acceptable_dates
                ):  # Include all results for completeness
                    results[relative_path] = result

        return results

    def generate_report(
        self, results: Dict[str, DateValidationResult], verbose: bool = False
    ) -> str:
        """Generate a human-readable report of validation results."""
        report_lines = []

        # Count issues
        total_outdated = sum(len(r.outdated_dates) for r in results.values())
        total_suspicious = sum(len(r.suspicious_dates) for r in results.values())
        total_acceptable = sum(len(r.acceptable_dates) for r in results.values())

        report_lines.append("Documentation Date Validation Report")
        report_lines.append("=" * 40)
        report_lines.append(
            f"Scan Date: {self.current_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")
        report_lines.append("Summary:")
        report_lines.append(f"  Outdated dates (>1 year): {total_outdated}")
        report_lines.append(f"  Suspicious dates (>3 months): {total_suspicious}")
        report_lines.append(f"  Acceptable dates: {total_acceptable}")
        report_lines.append("")

        if total_outdated == 0 and total_suspicious == 0:
            report_lines.append("✅ No outdated dates found!")
            return "\n".join(report_lines)

        # Report issues by severity
        if total_outdated > 0:
            report_lines.append("🚨 OUTDATED DATES (>1 year old):")
            report_lines.append("-" * 35)
            for file_path, result in results.items():
                if result.outdated_dates:
                    report_lines.append(f"\n📄 {file_path}:")
                    for line_num, date_str, context in result.outdated_dates:
                        report_lines.append(f"  Line {line_num}: {date_str}")
                        report_lines.append(f"    Context: {context[:80]}...")

        if total_suspicious > 0:
            report_lines.append("\n⚠️  SUSPICIOUS DATES (>3 months old):")
            report_lines.append("-" * 38)
            for file_path, result in results.items():
                if result.suspicious_dates:
                    report_lines.append(f"\n📄 {file_path}:")
                    for line_num, date_str, context in result.suspicious_dates:
                        report_lines.append(f"  Line {line_num}: {date_str}")
                        report_lines.append(f"    Context: {context[:80]}...")

        if verbose and total_acceptable > 0:
            report_lines.append("\n✅ ACCEPTABLE DATES:")
            report_lines.append("-" * 20)
            for file_path, result in results.items():
                if result.acceptable_dates:
                    report_lines.append(f"\n📄 {file_path}:")
                    for line_num, date_str, context in result.acceptable_dates:
                        report_lines.append(f"  Line {line_num}: {date_str}")
                        report_lines.append(f"    Context: {context[:80]}...")

        return "\n".join(report_lines)


def main() -> None:
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate dates in project documentation"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all dates including acceptable ones",
    )
    parser.add_argument(
        "--project-root",
        "-p",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--fail-on-outdated",
        action="store_true",
        help="Exit with error code if outdated dates are found",
    )

    args = parser.parse_args()

    validator = DocumentationDateValidator()
    results = validator.validate_project(args.project_root)

    report = validator.generate_report(results, verbose=args.verbose)
    print(report)

    # Exit with error if requested and issues found
    if args.fail_on_outdated:
        total_outdated = sum(len(r.outdated_dates) for r in results.values())
        if total_outdated > 0:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

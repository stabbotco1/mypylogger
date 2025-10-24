"""Badge system for mypylogger project.

This module provides functionality to generate and update project badges
in README.md using shields.io integration with atomic file operations.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from .config import BADGE_CONFIG, Badge, BadgeConfig, BadgeSection, get_badge_config
from .generator import (
    generate_code_style_badge,
    generate_downloads_badge,
    generate_license_badge,
    generate_pypi_version_badge,
    generate_python_versions_badge,
    generate_quality_gate_badge,
    generate_security_scan_badge,
    generate_type_check_badge,
)
from .security import (
    run_bandit_scan,
    run_safety_check,
    run_semgrep_analysis,
    simulate_codeql_checks,
)
from .status import (
    BadgeStatusCache,
    BadgeStatusError,
    get_all_badge_statuses,
    get_status_cache,
    validate_badge_status,
)
from .updater import atomic_write_readme, update_readme_with_badges


# Configure logging for badge system
logger = logging.getLogger(__name__)


class BadgeSystemError(Exception):
    """Raised when badge system operations fail."""


def generate_all_badges(detect_status: bool = True) -> list[Badge]:
    """Generate all project badges with current status.

    Args:
        detect_status: Whether to detect actual badge status or use defaults.

    Returns:
        List of Badge objects with generated URLs and status.

    Raises:
        BadgeSystemError: If badge generation fails.
    """
    try:
        logger.info("Generating all project badges")
        
        # Get badge statuses if requested
        statuses = {}
        if detect_status:
            try:
                statuses = get_all_badge_statuses()
                logger.info("Retrieved badge statuses from detection")
            except Exception as e:
                logger.warning(f"Failed to detect badge statuses: {e}")
                statuses = {}
        
        badges = []
        
        # Quality Gate badge
        try:
            quality_url = generate_quality_gate_badge()
            status_info = statuses.get("quality_gate", {"status": "unknown"})
            badges.append(Badge(
                name="quality_gate",
                url=quality_url,
                alt_text="Quality Gate",
                link_url=quality_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate quality gate badge: {e}")
        
        # Security Scan badge
        try:
            security_url = generate_security_scan_badge()
            status_info = statuses.get("security_scan", {"status": "unknown"})
            badges.append(Badge(
                name="security_scan",
                url=security_url,
                alt_text="Security Scan",
                link_url=security_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate security scan badge: {e}")
        
        # Code Style badge
        try:
            style_url = generate_code_style_badge()
            status_info = statuses.get("code_style", {"status": "passing"})
            badges.append(Badge(
                name="code_style",
                url=style_url,
                alt_text="Code Style: Ruff",
                link_url=style_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate code style badge: {e}")
        
        # Type Checking badge
        try:
            type_url = generate_type_check_badge()
            status_info = statuses.get("type_check", {"status": "passing"})
            badges.append(Badge(
                name="type_check",
                url=type_url,
                alt_text="Type Checked: mypy",
                link_url=type_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate type check badge: {e}")
        
        # Python Versions badge
        try:
            python_url = generate_python_versions_badge()
            status_info = statuses.get("python_versions", {"status": "passing"})
            badges.append(Badge(
                name="python_versions",
                url=python_url,
                alt_text="Python Versions",
                link_url=python_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate Python versions badge: {e}")
        
        # PyPI Version badge
        try:
            pypi_url = generate_pypi_version_badge()
            status_info = statuses.get("pypi_status", {"status": "development"})
            badges.append(Badge(
                name="pypi_version",
                url=pypi_url,
                alt_text="PyPI Version",
                link_url=pypi_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate PyPI version badge: {e}")
        
        # Downloads badge
        try:
            downloads_url = generate_downloads_badge()
            status_info = statuses.get("downloads", {"status": "development"})
            badges.append(Badge(
                name="downloads",
                url=downloads_url,
                alt_text="Downloads: Development",
                link_url=downloads_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate downloads badge: {e}")
        
        # License badge
        try:
            license_url = generate_license_badge()
            status_info = statuses.get("license", {"status": "passing"})
            badges.append(Badge(
                name="license",
                url=license_url,
                alt_text="License: MIT",
                link_url=license_url,
                status=status_info["status"]
            ))
        except Exception as e:
            logger.warning(f"Failed to generate license badge: {e}")
        
        logger.info(f"Generated {len(badges)} badges successfully")
        return badges
        
    except Exception as e:
        logger.error(f"Failed to generate badges: {e}")
        raise BadgeSystemError(f"Badge generation failed: {e}") from e


def create_badge_section(badges: list[Badge]) -> BadgeSection:
    """Create badge section with markdown formatting.

    Args:
        badges: List of Badge objects to include in section.

    Returns:
        BadgeSection with formatted markdown content.

    Raises:
        BadgeSystemError: If badge section creation fails.
    """
    try:
        logger.info("Creating badge section markdown")
        
        if not badges:
            logger.warning("No badges provided for section creation")
            return BadgeSection(
                title="Project Badges",
                badges=[],
                markdown=""
            )
        
        # Generate markdown for each badge
        badge_markdown_lines = []
        for badge in badges:
            if badge.link_url:
                markdown = f"[![{badge.alt_text}]({badge.url})]({badge.link_url})"
            else:
                markdown = f"![{badge.alt_text}]({badge.url})"
            badge_markdown_lines.append(markdown)
        
        # Combine all badges into single line with spaces
        combined_markdown = " ".join(badge_markdown_lines)
        
        section = BadgeSection(
            title="Project Badges",
            badges=badges,
            markdown=combined_markdown
        )
        
        logger.info(f"Created badge section with {len(badges)} badges")
        return section
        
    except Exception as e:
        logger.error(f"Failed to create badge section: {e}")
        raise BadgeSystemError(f"Badge section creation failed: {e}") from e


def update_project_badges(detect_status: bool = True) -> bool:
    """Main badge update workflow - generate badges and update README.

    Args:
        detect_status: Whether to detect actual badge status or use defaults.

    Returns:
        True if badge update was successful, False otherwise.

    Raises:
        BadgeSystemError: If badge update workflow fails.
    """
    try:
        logger.info("Starting badge update workflow")
        
        # Clear cache if we're detecting status
        if detect_status:
            cache = get_status_cache()
            if cache.is_expired():
                cache.clear()
                logger.info("Cleared expired badge status cache")
        
        # Generate all badges with status detection
        badges = generate_all_badges(detect_status=detect_status)
        
        if not badges:
            logger.warning("No badges generated, skipping README update")
            return False
        
        # Create badge section
        badge_section = create_badge_section(badges)
        
        # Update README with badges
        success = update_readme_with_badges([badge_section.markdown])
        
        if success:
            logger.info("Badge update workflow completed successfully")
        else:
            logger.error("Failed to update README with badges")
        
        return success
        
    except Exception as e:
        logger.error(f"Badge update workflow failed: {e}")
        raise BadgeSystemError(f"Badge update workflow failed: {e}") from e


def main() -> int:
    """Command-line interface for manual badge updates.

    Returns:
        Exit code: 0 for success, 1 for failure.
    """
    parser = argparse.ArgumentParser(
        description="Update project badges in README.md",
        prog="python -m badges"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Generate badges but don't update README"
    )
    
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check badge configuration and exit"
    )
    
    parser.add_argument(
        "--no-status-detection",
        action="store_true",
        help="Skip badge status detection and use defaults"
    )
    
    parser.add_argument(
        "--ci-mode",
        action="store_true",
        help="CI/CD mode: never fail pipeline, always return exit code 0"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        # Configuration check mode
        if args.config_check:
            logger.info("Checking badge configuration")
            config = get_badge_config()
            logger.info(f"Configuration valid: {config}")
            return 0
        
        # Dry run mode
        if args.dry_run:
            logger.info("Running in dry-run mode")
            detect_status = not args.no_status_detection
            badges = generate_all_badges(detect_status=detect_status)
            badge_section = create_badge_section(badges)
            logger.info(f"Generated badge section: {badge_section.markdown}")
            return 0
        
        # Normal badge update
        detect_status = not args.no_status_detection
        success = update_project_badges(detect_status=detect_status)
        
        if args.ci_mode:
            # In CI mode, always return 0 to not fail pipelines
            if success:
                logger.info("Badge update completed successfully in CI mode")
            else:
                logger.warning("Badge update failed in CI mode, but continuing pipeline")
            return 0
        else:
            return 0 if success else 1
        
    except BadgeSystemError as e:
        logger.error(f"Badge system error: {e}")
        if args.ci_mode:
            logger.info("Continuing CI/CD pipeline despite badge system error")
            return 0
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.ci_mode:
            logger.info("Continuing CI/CD pipeline despite unexpected error")
            return 0
        return 1


__all__ = [
    "BADGE_CONFIG",
    "Badge",
    "BadgeConfig",
    "BadgeSection",
    "BadgeStatusCache",
    "BadgeStatusError",
    "BadgeSystemError",
    "atomic_write_readme",
    "create_badge_section",
    "generate_all_badges",
    "generate_code_style_badge",
    "generate_downloads_badge",
    "generate_license_badge",
    "generate_pypi_version_badge",
    "generate_python_versions_badge",
    "generate_quality_gate_badge",
    "generate_security_scan_badge",
    "generate_type_check_badge",
    "get_all_badge_statuses",
    "get_status_cache",
    "main",
    "run_bandit_scan",
    "run_safety_check",
    "run_semgrep_analysis",
    "simulate_codeql_checks",
    "update_project_badges",
    "update_readme_with_badges",
    "validate_badge_status",
]


if __name__ == "__main__":
    sys.exit(main())

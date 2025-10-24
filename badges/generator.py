"""Badge generation module for shields.io integration.

This module provides functions to generate shields.io URLs for various
project badges including GitHub Actions status, code quality metrics,
and package information.
"""

from __future__ import annotations

import os

from badges.config import BADGE_CONFIG, get_badge_config
from badges.security import get_comprehensive_security_status


def generate_code_style_badge() -> str:
    """Generate Ruff code style compliance badge URL.

    Returns:
        Shields.io URL for Ruff code style badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["code_style"]

        return f"{config.shields_base_url}/{template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["code_style"]
        return f"{base_url}/{template}"


def generate_type_check_badge() -> str:
    """Generate mypy type checking badge URL.

    Returns:
        Shields.io URL for mypy type checking badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["type_checked"]

        return f"{config.shields_base_url}/{template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["type_checked"]
        return f"{base_url}/{template}"


def generate_python_versions_badge() -> str:
    """Generate Python compatibility badge URL.

    Returns:
        Shields.io URL for Python version compatibility badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["python_versions"]

        # Replace package placeholder with actual package name
        formatted_template = template.format(package=config.pypi_package)
        return f"{config.shields_base_url}/{formatted_template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["python_versions"]
        package = BADGE_CONFIG["pypi_package"]
        formatted_template = template.format(package=package)
        return f"{base_url}/{formatted_template}"


def generate_license_badge() -> str:
    """Generate MIT license badge URL.

    Returns:
        Shields.io URL for MIT license badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["license"]

        # Replace repo placeholder with actual repository
        formatted_template = template.format(repo=config.github_repo)
        return f"{config.shields_base_url}/{formatted_template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["license"]
        repo = BADGE_CONFIG["github_repo"]
        formatted_template = template.format(repo=repo)
        return f"{base_url}/{formatted_template}"


def generate_quality_gate_badge() -> str:
    """Generate overall quality gate badge that aggregates all quality checks.

    Returns:
        Shields.io URL for quality gate badge with appropriate status and color.
    """
    try:
        config = get_badge_config()

        # Get quality gate status (aggregated from all quality checks)
        from badges.status import get_quality_gate_status

        quality_status = get_quality_gate_status()
        status = quality_status["status"]

        # Determine badge color based on status
        color_map = {
            "passing": "brightgreen",
            "failing": "red",
            "pending": "yellow",
            "unknown": "lightgrey",
        }
        color = color_map.get(status, "lightgrey")

        # Create custom badge URL
        badge_text = f"quality%20gate-{status}-{color}"
        return f"{config.shields_base_url}/badge/{badge_text}?style=flat"

    except Exception:
        # Fallback to unknown status on error
        base_url = BADGE_CONFIG["shields_base_url"]
        return f"{base_url}/badge/quality%20gate-unknown-lightgrey?style=flat"


def generate_pypi_version_badge() -> str:
    """Generate PyPI version badge URL.

    Returns:
        Shields.io URL for PyPI version badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["pypi_version"]

        # Replace package placeholder with actual package name
        formatted_template = template.format(package=config.pypi_package)
        return f"{config.shields_base_url}/{formatted_template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["pypi_version"]
        package = BADGE_CONFIG["pypi_package"]
        formatted_template = template.format(package=package)
        return f"{base_url}/{formatted_template}"


def generate_downloads_badge() -> str:
    """Generate downloads status badge URL.

    Returns:
        Shields.io URL for downloads status badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["downloads"]

        return f"{config.shields_base_url}/{template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["downloads"]
        return f"{base_url}/{template}"


def generate_comprehensive_security_badge() -> str:
    """Generate comprehensive security badge combining local and GitHub CodeQL results.

    Returns:
        Shields.io URL for comprehensive security badge with appropriate status and color.
    """
    try:
        config = get_badge_config()

        # Get comprehensive security status
        security_status = get_comprehensive_security_status()
        status = security_status["status"]

        # Determine badge color based on status
        color_map = {
            "Verified": "brightgreen",
            "Issues Found": "red",
            "Scanning": "yellow",
            "Unknown": "lightgrey",
        }
        color = color_map.get(status, "lightgrey")

        # Create custom badge URL
        badge_text = f"security-{status.replace(' ', '%20')}-{color}"
        return f"{config.shields_base_url}/badge/{badge_text}?style=flat"

    except Exception:
        # Fallback to unknown status on error
        base_url = BADGE_CONFIG["shields_base_url"]
        return f"{base_url}/badge/security-Unknown-lightgrey?style=flat"


def get_comprehensive_security_badge_link() -> str:
    """Get the link URL for the comprehensive security badge.

    Returns:
        URL linking to GitHub CodeQL results or security tab.
    """
    try:
        security_status = get_comprehensive_security_status()
        return str(security_status["link_url"])
    except Exception:
        # Fallback to default repository security tab
        github_repo = os.getenv("GITHUB_REPOSITORY", "username/mypylogger")
        return f"https://github.com/{github_repo}/security"

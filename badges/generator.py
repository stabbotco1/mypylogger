"""Badge generation module for shields.io integration.

This module provides functions to generate shields.io URLs for various
project badges including GitHub Actions status, code quality metrics,
and package information.
"""

from __future__ import annotations

from badges.config import BADGE_CONFIG, get_badge_config


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
    """Generate GitHub Actions workflow status badge URL.

    Returns:
        Shields.io URL for quality-gate.yml workflow status badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["quality_gate"]

        # Replace repo placeholder with actual repository
        formatted_template = template.format(repo=config.github_repo)
        return f"{config.shields_base_url}/{formatted_template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["quality_gate"]
        repo = BADGE_CONFIG["github_repo"]
        formatted_template = template.format(repo=repo)
        return f"{base_url}/{formatted_template}"


def generate_security_scan_badge() -> str:
    """Generate security scan workflow status badge URL.

    Returns:
        Shields.io URL for security-scan.yml workflow status badge.
    """
    try:
        config = get_badge_config()
        template = BADGE_CONFIG["badge_templates"]["security_scan"]

        # Replace repo placeholder with actual repository
        formatted_template = template.format(repo=config.github_repo)
        return f"{config.shields_base_url}/{formatted_template}"
    except Exception:
        # Fallback to default configuration on error
        base_url = BADGE_CONFIG["shields_base_url"]
        template = BADGE_CONFIG["badge_templates"]["security_scan"]
        repo = BADGE_CONFIG["github_repo"]
        formatted_template = template.format(repo=repo)
        return f"{base_url}/{formatted_template}"


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

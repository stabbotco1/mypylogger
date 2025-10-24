"""Badge status detection and caching module.

This module provides functionality to determine badge status by running
tests or reading existing results, with caching to avoid unnecessary
API calls within a single run.
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from .config import get_badge_config


logger = logging.getLogger(__name__)


class BadgeStatusError(Exception):
    """Raised when badge status detection fails."""


class BadgeStatusCache:
    """Cache for badge status to avoid unnecessary API calls."""

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_timestamp = time.time()

    def get(self, badge_name: str) -> dict[str, Any] | None:
        """Get cached status for badge.

        Args:
            badge_name: Name of the badge to get status for.

        Returns:
            Cached status dict or None if not cached.
        """
        return self._cache.get(badge_name)

    def set(self, badge_name: str, status: dict[str, Any]) -> None:
        """Set cached status for badge.

        Args:
            badge_name: Name of the badge to cache status for.
            status: Status dictionary to cache.
        """
        self._cache[badge_name] = status
        logger.debug(f"Cached status for {badge_name}: {status}")

    def clear(self) -> None:
        """Clear all cached status."""
        self._cache.clear()
        self._cache_timestamp = time.time()
        logger.debug("Cleared badge status cache")

    def is_expired(self, max_age_seconds: int = 300) -> bool:
        """Check if cache is expired.

        Args:
            max_age_seconds: Maximum age in seconds before cache expires.

        Returns:
            True if cache is expired, False otherwise.
        """
        return (time.time() - self._cache_timestamp) > max_age_seconds


# Global cache instance
_status_cache = BadgeStatusCache()


def get_status_cache() -> BadgeStatusCache:
    """Get the global badge status cache.

    Returns:
        Global BadgeStatusCache instance.
    """
    return _status_cache


def detect_quality_gate_status() -> dict[str, Any]:
    """Detect quality gate badge status by running tests.

    Returns:
        Status dictionary with 'status' and 'message' keys.

    Raises:
        BadgeStatusError: If status detection fails.
    """
    cache = get_status_cache()
    cached = cache.get("quality_gate")
    if cached:
        logger.debug("Using cached quality gate status")
        return cached

    try:
        logger.info("Detecting quality gate status by running tests")
        
        # Check if run_tests.sh script exists
        test_script = Path("scripts/run_tests.sh")
        if test_script.exists():
            # Run the master test script
            result = subprocess.run(
                ["bash", str(test_script)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                status = {"status": "passing", "message": "All tests pass"}
            else:
                status = {"status": "failing", "message": "Tests failed"}
        else:
            # Fallback to pytest if no master script
            result = subprocess.run(
                ["uv", "run", "pytest", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                status = {"status": "passing", "message": "All tests pass"}
            else:
                status = {"status": "failing", "message": "Tests failed"}
        
        cache.set("quality_gate", status)
        logger.info(f"Quality gate status: {status['status']}")
        return status
        
    except subprocess.TimeoutExpired:
        status = {"status": "unknown", "message": "Test timeout"}
        cache.set("quality_gate", status)
        logger.warning("Quality gate status detection timed out")
        return status
    except Exception as e:
        status = {"status": "unknown", "message": f"Detection failed: {e}"}
        cache.set("quality_gate", status)
        logger.error(f"Failed to detect quality gate status: {e}")
        return status


def detect_security_scan_status() -> dict[str, Any]:
    """Detect security scan badge status by running security checks.

    Returns:
        Status dictionary with 'status' and 'message' keys.

    Raises:
        BadgeStatusError: If status detection fails.
    """
    cache = get_status_cache()
    cached = cache.get("security_scan")
    if cached:
        logger.debug("Using cached security scan status")
        return cached

    try:
        logger.info("Detecting security scan status by running security checks")
        
        # Import security functions
        from .security import (
            run_bandit_scan,
            run_safety_check,
            run_semgrep_analysis,
            simulate_codeql_checks,
        )
        
        # Run all security checks
        security_results = []
        
        try:
            bandit_result = run_bandit_scan()
            security_results.append(("bandit", bandit_result))
        except Exception as e:
            logger.warning(f"Bandit scan failed: {e}")
            security_results.append(("bandit", False))
        
        try:
            safety_result = run_safety_check()
            security_results.append(("safety", safety_result))
        except Exception as e:
            logger.warning(f"Safety check failed: {e}")
            security_results.append(("safety", False))
        
        try:
            semgrep_result = run_semgrep_analysis()
            security_results.append(("semgrep", semgrep_result))
        except Exception as e:
            logger.warning(f"Semgrep analysis failed: {e}")
            security_results.append(("semgrep", False))
        
        try:
            codeql_result = simulate_codeql_checks()
            security_results.append(("codeql", codeql_result))
        except Exception as e:
            logger.warning(f"CodeQL simulation failed: {e}")
            security_results.append(("codeql", False))
        
        # Determine overall status
        all_passed = all(result for _, result in security_results)
        any_failed = any(not result for _, result in security_results)
        
        if all_passed:
            status = {"status": "passing", "message": "All security checks pass"}
        elif any_failed:
            failed_checks = [name for name, result in security_results if not result]
            status = {
                "status": "failing",
                "message": f"Security checks failed: {', '.join(failed_checks)}"
            }
        else:
            status = {"status": "unknown", "message": "No security checks completed"}
        
        cache.set("security_scan", status)
        logger.info(f"Security scan status: {status['status']}")
        return status
        
    except Exception as e:
        status = {"status": "unknown", "message": f"Detection failed: {e}"}
        cache.set("security_scan", status)
        logger.error(f"Failed to detect security scan status: {e}")
        return status


def detect_code_style_status() -> dict[str, Any]:
    """Detect code style badge status by running Ruff checks.

    Returns:
        Status dictionary with 'status' and 'message' keys.
    """
    cache = get_status_cache()
    cached = cache.get("code_style")
    if cached:
        logger.debug("Using cached code style status")
        return cached

    try:
        logger.info("Detecting code style status by running Ruff")
        
        # Run Ruff format check
        format_result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "."],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Run Ruff linting check
        lint_result = subprocess.run(
            ["uv", "run", "ruff", "check", "."],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if format_result.returncode == 0 and lint_result.returncode == 0:
            status = {"status": "passing", "message": "Code style compliant"}
        else:
            status = {"status": "failing", "message": "Code style issues found"}
        
        cache.set("code_style", status)
        logger.info(f"Code style status: {status['status']}")
        return status
        
    except subprocess.TimeoutExpired:
        status = {"status": "unknown", "message": "Ruff check timeout"}
        cache.set("code_style", status)
        logger.warning("Code style status detection timed out")
        return status
    except Exception as e:
        status = {"status": "unknown", "message": f"Detection failed: {e}"}
        cache.set("code_style", status)
        logger.error(f"Failed to detect code style status: {e}")
        return status


def detect_type_check_status() -> dict[str, Any]:
    """Detect type checking badge status by running mypy.

    Returns:
        Status dictionary with 'status' and 'message' keys.
    """
    cache = get_status_cache()
    cached = cache.get("type_check")
    if cached:
        logger.debug("Using cached type check status")
        return cached

    try:
        logger.info("Detecting type check status by running mypy")
        
        # Run mypy type checking
        result = subprocess.run(
            ["uv", "run", "mypy", "src/", "badges/"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            status = {"status": "passing", "message": "Type checking passed"}
        else:
            status = {"status": "failing", "message": "Type checking failed"}
        
        cache.set("type_check", status)
        logger.info(f"Type check status: {status['status']}")
        return status
        
    except subprocess.TimeoutExpired:
        status = {"status": "unknown", "message": "mypy timeout"}
        cache.set("type_check", status)
        logger.warning("Type check status detection timed out")
        return status
    except Exception as e:
        status = {"status": "unknown", "message": f"Detection failed: {e}"}
        cache.set("type_check", status)
        logger.error(f"Failed to detect type check status: {e}")
        return status


def detect_pypi_status() -> dict[str, Any]:
    """Detect PyPI badge status by checking package information.

    Returns:
        Status dictionary with 'status' and 'message' keys.
    """
    cache = get_status_cache()
    cached = cache.get("pypi_status")
    if cached:
        logger.debug("Using cached PyPI status")
        return cached

    try:
        logger.info("Detecting PyPI status")
        
        # For now, assume development status since package may not be published yet
        status = {"status": "development", "message": "Package in development"}
        
        cache.set("pypi_status", status)
        logger.info(f"PyPI status: {status['status']}")
        return status
        
    except Exception as e:
        status = {"status": "unknown", "message": f"Detection failed: {e}"}
        cache.set("pypi_status", status)
        logger.error(f"Failed to detect PyPI status: {e}")
        return status


def validate_badge_status(badge_name: str, status: dict[str, Any]) -> bool:
    """Validate badge status dictionary format.

    Args:
        badge_name: Name of the badge being validated.
        status: Status dictionary to validate.

    Returns:
        True if status is valid, False otherwise.
    """
    try:
        # Check required keys
        if not isinstance(status, dict):
            logger.error(f"Invalid status for {badge_name}: not a dictionary")
            return False
        
        if "status" not in status:
            logger.error(f"Invalid status for {badge_name}: missing 'status' key")
            return False
        
        if "message" not in status:
            logger.error(f"Invalid status for {badge_name}: missing 'message' key")
            return False
        
        # Check status values
        valid_statuses = {"passing", "failing", "unknown", "development"}
        if status["status"] not in valid_statuses:
            logger.error(f"Invalid status for {badge_name}: invalid status value '{status['status']}'")
            return False
        
        # Check message is string
        if not isinstance(status["message"], str):
            logger.error(f"Invalid status for {badge_name}: message must be string")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to validate status for {badge_name}: {e}")
        return False


def get_all_badge_statuses() -> dict[str, dict[str, Any]]:
    """Get status for all badges with caching.

    Returns:
        Dictionary mapping badge names to their status dictionaries.
    """
    logger.info("Getting status for all badges")
    
    statuses = {}
    
    # Quality gate status
    try:
        statuses["quality_gate"] = detect_quality_gate_status()
    except Exception as e:
        logger.error(f"Failed to get quality gate status: {e}")
        statuses["quality_gate"] = {"status": "unknown", "message": "Status detection failed"}
    
    # Security scan status
    try:
        statuses["security_scan"] = detect_security_scan_status()
    except Exception as e:
        logger.error(f"Failed to get security scan status: {e}")
        statuses["security_scan"] = {"status": "unknown", "message": "Status detection failed"}
    
    # Code style status
    try:
        statuses["code_style"] = detect_code_style_status()
    except Exception as e:
        logger.error(f"Failed to get code style status: {e}")
        statuses["code_style"] = {"status": "unknown", "message": "Status detection failed"}
    
    # Type check status
    try:
        statuses["type_check"] = detect_type_check_status()
    except Exception as e:
        logger.error(f"Failed to get type check status: {e}")
        statuses["type_check"] = {"status": "unknown", "message": "Status detection failed"}
    
    # PyPI status
    try:
        statuses["pypi_status"] = detect_pypi_status()
    except Exception as e:
        logger.error(f"Failed to get PyPI status: {e}")
        statuses["pypi_status"] = {"status": "unknown", "message": "Status detection failed"}
    
    # Static badges always pass
    statuses["python_versions"] = {"status": "passing", "message": "Static badge"}
    statuses["downloads"] = {"status": "development", "message": "Development status"}
    statuses["license"] = {"status": "passing", "message": "MIT license"}
    
    logger.info(f"Retrieved status for {len(statuses)} badges")
    return statuses
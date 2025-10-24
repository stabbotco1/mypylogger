"""Unit tests for badge generator functionality."""

from __future__ import annotations

import os
from unittest.mock import patch

from badges.generator import (
    generate_code_style_badge,
    generate_downloads_badge,
    generate_license_badge,
    generate_pypi_version_badge,
    generate_python_versions_badge,
    generate_quality_gate_badge,
    generate_security_scan_badge,
    generate_type_check_badge,
)


class TestStaticBadgeGeneration:
    """Test static badge generation functions."""

    def test_generate_code_style_badge_with_defaults(self) -> None:
        """Test code style badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_code_style_badge()

            expected = "https://img.shields.io/badge/code%20style-ruff-000000?style=flat"
            assert url == expected

    def test_generate_code_style_badge_with_custom_config(self) -> None:
        """Test code style badge generation with custom configuration."""
        env_vars = {
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_code_style_badge()

            expected = "https://custom.shields.io/badge/code%20style-ruff-000000?style=flat"
            assert url == expected

    def test_generate_code_style_badge_with_config_error(self) -> None:
        """Test code style badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_code_style_badge()

            expected = "https://img.shields.io/badge/code%20style-ruff-000000?style=flat"
            assert url == expected

    def test_generate_type_check_badge_with_defaults(self) -> None:
        """Test type check badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_type_check_badge()

            expected = "https://img.shields.io/badge/type%20checked-mypy-blue?style=flat"
            assert url == expected

    def test_generate_type_check_badge_with_custom_config(self) -> None:
        """Test type check badge generation with custom configuration."""
        env_vars = {
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_type_check_badge()

            expected = "https://custom.shields.io/badge/type%20checked-mypy-blue?style=flat"
            assert url == expected

    def test_generate_type_check_badge_with_config_error(self) -> None:
        """Test type check badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_type_check_badge()

            expected = "https://img.shields.io/badge/type%20checked-mypy-blue?style=flat"
            assert url == expected

    def test_generate_python_versions_badge_with_defaults(self) -> None:
        """Test Python versions badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_python_versions_badge()

            expected = "https://img.shields.io/pypi/pyversions/mypylogger?style=flat"
            assert url == expected

    def test_generate_python_versions_badge_with_custom_package(self) -> None:
        """Test Python versions badge generation with custom package name."""
        env_vars = {
            "PYPI_PACKAGE": "custom-package",
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_python_versions_badge()

            expected = "https://custom.shields.io/pypi/pyversions/custom-package?style=flat"
            assert url == expected

    def test_generate_python_versions_badge_with_config_error(self) -> None:
        """Test Python versions badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_python_versions_badge()

            expected = "https://img.shields.io/pypi/pyversions/mypylogger?style=flat"
            assert url == expected

    def test_generate_license_badge_with_defaults(self) -> None:
        """Test license badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_license_badge()

            expected = "https://img.shields.io/github/license/username/mypylogger?style=flat"
            assert url == expected

    def test_generate_license_badge_with_custom_repo(self) -> None:
        """Test license badge generation with custom repository."""
        env_vars = {
            "GITHUB_REPOSITORY": "testuser/testrepo",
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_license_badge()

            expected = "https://custom.shields.io/github/license/testuser/testrepo?style=flat"
            assert url == expected

    def test_generate_license_badge_with_config_error(self) -> None:
        """Test license badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_license_badge()

            expected = "https://img.shields.io/github/license/username/mypylogger?style=flat"
            assert url == expected


class TestBadgeUrlFormat:
    """Test badge URL formatting and structure."""

    def test_all_static_badges_have_shields_base_url(self) -> None:
        """Test that all static badges use shields.io base URL."""
        with patch.dict(os.environ, {}, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
            ]

            for badge_url in badges:
                assert badge_url.startswith("https://img.shields.io/"), (
                    f"Badge URL does not start with shields.io base: {badge_url}"
                )

    def test_all_static_badges_have_style_parameter(self) -> None:
        """Test that all static badges include style=flat parameter."""
        with patch.dict(os.environ, {}, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
            ]

            for badge_url in badges:
                assert "style=flat" in badge_url, f"Badge URL missing style parameter: {badge_url}"

    def test_parametrized_badges_format_correctly(self) -> None:
        """Test that badges with parameters format placeholders correctly."""
        env_vars = {
            "GITHUB_REPOSITORY": "testuser/testrepo",
            "PYPI_PACKAGE": "testpackage",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            python_versions_url = generate_python_versions_badge()
            license_url = generate_license_badge()

            # Should not contain placeholder text
            assert "{package}" not in python_versions_url
            assert "{repo}" not in license_url

            # Should contain actual values
            assert "testpackage" in python_versions_url
            assert "testuser/testrepo" in license_url

    def test_badge_urls_are_valid_format(self) -> None:
        """Test that generated badge URLs have valid format."""
        with patch.dict(os.environ, {}, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
            ]

            for badge_url in badges:
                # Should be valid URL format
                assert badge_url.startswith("https://"), f"Invalid URL format: {badge_url}"

                # Should not have double slashes (except after protocol)
                url_path = badge_url.replace("https://", "")
                assert "//" not in url_path, f"Double slashes in URL path: {badge_url}"

                # Should not end with slash
                assert not badge_url.endswith("/"), f"URL ends with slash: {badge_url}"


class TestDynamicBadgeGeneration:
    """Test dynamic badge generation functions."""

    def test_generate_quality_gate_badge_with_defaults(self) -> None:
        """Test quality gate badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_quality_gate_badge()

            expected = (
                "https://img.shields.io/github/actions/workflow/status/"
                "username/mypylogger/quality-gate.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_quality_gate_badge_with_custom_repo(self) -> None:
        """Test quality gate badge generation with custom repository."""
        env_vars = {
            "GITHUB_REPOSITORY": "testuser/testrepo",
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_quality_gate_badge()

            expected = (
                "https://custom.shields.io/github/actions/workflow/status/"
                "testuser/testrepo/quality-gate.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_quality_gate_badge_with_config_error(self) -> None:
        """Test quality gate badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_quality_gate_badge()

            expected = (
                "https://img.shields.io/github/actions/workflow/status/"
                "username/mypylogger/quality-gate.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_security_scan_badge_with_defaults(self) -> None:
        """Test security scan badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_security_scan_badge()

            expected = (
                "https://img.shields.io/github/actions/workflow/status/"
                "username/mypylogger/security-scan.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_security_scan_badge_with_custom_repo(self) -> None:
        """Test security scan badge generation with custom repository."""
        env_vars = {
            "GITHUB_REPOSITORY": "testuser/testrepo",
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_security_scan_badge()

            expected = (
                "https://custom.shields.io/github/actions/workflow/status/"
                "testuser/testrepo/security-scan.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_security_scan_badge_with_config_error(self) -> None:
        """Test security scan badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_security_scan_badge()

            expected = (
                "https://img.shields.io/github/actions/workflow/status/"
                "username/mypylogger/security-scan.yml?branch=main&style=flat"
            )
            assert url == expected

    def test_generate_pypi_version_badge_with_defaults(self) -> None:
        """Test PyPI version badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_pypi_version_badge()

            expected = "https://img.shields.io/pypi/v/mypylogger?style=flat"
            assert url == expected

    def test_generate_pypi_version_badge_with_custom_package(self) -> None:
        """Test PyPI version badge generation with custom package name."""
        env_vars = {
            "PYPI_PACKAGE": "custom-package",
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_pypi_version_badge()

            expected = "https://custom.shields.io/pypi/v/custom-package?style=flat"
            assert url == expected

    def test_generate_pypi_version_badge_with_config_error(self) -> None:
        """Test PyPI version badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_pypi_version_badge()

            expected = "https://img.shields.io/pypi/v/mypylogger?style=flat"
            assert url == expected

    def test_generate_downloads_badge_with_defaults(self) -> None:
        """Test downloads badge generation with default configuration."""
        with patch.dict(os.environ, {}, clear=True):
            url = generate_downloads_badge()

            expected = "https://img.shields.io/badge/downloads-development-yellow?style=flat"
            assert url == expected

    def test_generate_downloads_badge_with_custom_config(self) -> None:
        """Test downloads badge generation with custom configuration."""
        env_vars = {
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_downloads_badge()

            expected = "https://custom.shields.io/badge/downloads-development-yellow?style=flat"
            assert url == expected

    def test_generate_downloads_badge_with_config_error(self) -> None:
        """Test downloads badge generation handles configuration errors."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            # Should fallback to default configuration
            url = generate_downloads_badge()

            expected = "https://img.shields.io/badge/downloads-development-yellow?style=flat"
            assert url == expected


class TestAllBadgeGeneration:
    """Test all badge generation functions together."""

    def test_all_badges_generate_valid_urls(self) -> None:
        """Test that all badge generation functions return valid URLs."""
        with patch.dict(os.environ, {}, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
                generate_quality_gate_badge(),
                generate_security_scan_badge(),
                generate_pypi_version_badge(),
                generate_downloads_badge(),
            ]

            for badge_url in badges:
                # Should be valid URL format
                assert badge_url.startswith("https://"), f"Invalid URL format: {badge_url}"

                # Should contain shields.io domain
                assert "shields.io" in badge_url, f"Not a shields.io URL: {badge_url}"

                # Should have style parameter
                assert "style=flat" in badge_url, f"Missing style parameter: {badge_url}"

    def test_all_badges_handle_config_errors_gracefully(self) -> None:
        """Test that all badge functions handle configuration errors gracefully."""
        env_vars = {
            "GITHUB_REPOSITORY": "invalid-format",  # This will cause config error
        }

        with patch.dict(os.environ, env_vars, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
                generate_quality_gate_badge(),
                generate_security_scan_badge(),
                generate_pypi_version_badge(),
                generate_downloads_badge(),
            ]

            # All should return valid URLs despite config error
            for badge_url in badges:
                assert badge_url.startswith("https://"), f"Invalid fallback URL: {badge_url}"
                assert len(badge_url) > 20, f"URL too short, likely empty: {badge_url}"

    def test_parametrized_badges_no_placeholders(self) -> None:
        """Test that parametrized badges don't contain placeholder text."""
        env_vars = {
            "GITHUB_REPOSITORY": "testuser/testrepo",
            "PYPI_PACKAGE": "testpackage",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            badges = [
                generate_python_versions_badge(),
                generate_license_badge(),
                generate_quality_gate_badge(),
                generate_security_scan_badge(),
                generate_pypi_version_badge(),
            ]

            for badge_url in badges:
                # Should not contain placeholder text
                assert "{package}" not in badge_url, f"Contains package placeholder: {badge_url}"
                assert "{repo}" not in badge_url, f"Contains repo placeholder: {badge_url}"

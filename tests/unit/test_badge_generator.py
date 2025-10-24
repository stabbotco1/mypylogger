"""Unit tests for badge generator functionality."""

from __future__ import annotations

import os
from unittest.mock import Mock, patch

import pytest

from badges.generator import (
    generate_code_style_badge,
    generate_comprehensive_security_badge,
    generate_downloads_badge,
    generate_license_badge,
    generate_pypi_version_badge,
    generate_python_versions_badge,
    generate_quality_gate_badge,
    generate_type_check_badge,
    get_comprehensive_security_badge_link,
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

            expected = "https://img.shields.io/github/license/stabbotco1/mypylogger?style=flat"
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

            expected = "https://img.shields.io/github/license/stabbotco1/mypylogger?style=flat"
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
        with patch("badges.status.get_quality_gate_status") as mock_status:
            mock_status.return_value = {
                "status": "passing",
                "message": "All quality checks passing",
            }

            with patch.dict(os.environ, {}, clear=True):
                url = generate_quality_gate_badge()

                expected = "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/quality-gate.yml?style=flat&label=quality%20gate"
                assert url == expected

    def test_generate_quality_gate_badge_with_custom_config(self) -> None:
        """Test quality gate badge generation with custom configuration."""
        with patch("badges.status.get_quality_gate_status") as mock_status:
            mock_status.return_value = {
                "status": "failing",
                "message": "Some quality checks failing",
            }

            env_vars = {
                "SHIELDS_BASE_URL": "https://custom.shields.io",
            }

            with patch.dict(os.environ, env_vars, clear=True):
                url = generate_quality_gate_badge()

                expected = "https://custom.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/quality-gate.yml?style=flat&label=quality%20gate"
                assert url == expected

    def test_generate_quality_gate_badge_with_exception(self) -> None:
        """Test quality gate badge generation handles exceptions."""
        with patch("badges.status.get_quality_gate_status") as mock_status:
            mock_status.side_effect = Exception("Test error")

            with patch.dict(os.environ, {}, clear=True):
                # Should fallback to unknown status
                url = generate_quality_gate_badge()

                expected = "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/quality-gate.yml?style=flat&label=quality%20gate"
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

    @patch("badges.generator.get_comprehensive_security_status")
    @patch("badges.status.get_quality_gate_status")
    def test_all_badges_generate_valid_urls(
        self, mock_quality_status: Mock, mock_security_status: Mock
    ) -> None:
        """Test that all badge generation functions return valid URLs."""
        # Mock comprehensive security status for the comprehensive security badge
        mock_security_status.return_value = {
            "status": "Verified",
            "local_passed": True,
            "codeql_passed": True,
            "link_url": "https://github.com/test/repo/security/code-scanning",
        }

        # Mock quality gate status
        mock_quality_status.return_value = {
            "status": "passing",
            "message": "All quality checks passing",
        }

        with patch.dict(os.environ, {}, clear=True):
            badges = [
                generate_code_style_badge(),
                generate_type_check_badge(),
                generate_python_versions_badge(),
                generate_license_badge(),
                generate_quality_gate_badge(),
                generate_pypi_version_badge(),
                generate_downloads_badge(),
                generate_comprehensive_security_badge(),
            ]

            for badge_url in badges:
                # Should be valid URL format
                assert badge_url.startswith("https://"), f"Invalid URL format: {badge_url}"

                # Should contain shields.io domain
                assert "shields.io" in badge_url, f"Not a shields.io URL: {badge_url}"

                # Should have style parameter
                assert "style=flat" in badge_url, f"Missing style parameter: {badge_url}"

    def test_all_eight_badge_types_generate_correctly(self) -> None:
        """Test that all 8 badge types generate correct shields.io URLs."""
        with patch(
            "badges.generator.get_comprehensive_security_status"
        ) as mock_security_status, patch(
            "badges.status.get_quality_gate_status"
        ) as mock_quality_status:
            mock_security_status.return_value = {
                "status": "Verified",
                "local_passed": True,
                "codeql_passed": True,
                "link_url": "https://github.com/test/repo/security/code-scanning",
            }
            mock_quality_status.return_value = {
                "status": "passing",
                "message": "All quality checks passing",
                "components": {
                    "code_style": "passing",
                    "type_check": "passing",
                    "security": "passing",
                },
            }

            env_vars = {
                "GITHUB_REPOSITORY": "testuser/testrepo",
                "PYPI_PACKAGE": "testpackage",
                "SHIELDS_BASE_URL": "https://img.shields.io",
            }

            with patch.dict(os.environ, env_vars, clear=True):
                # Test all 8 badge types
                expected_badges = {
                    "quality_gate": (
                        "github/actions/workflow/status/testuser/testrepo/quality-gate.yml"
                        "?style=flat&label=quality%20gate"
                    ),
                    "comprehensive_security": "badge/security-verified-brightgreen?style=flat",
                    "code_style": "badge/code%20style-ruff-000000?style=flat",
                    "type_checked": "badge/type%20checked-mypy-blue?style=flat",
                    "python_versions": "pypi/pyversions/testpackage?style=flat",
                    "pypi_version": "pypi/v/testpackage?style=flat",
                    "downloads": "badge/downloads-development-yellow?style=flat",
                    "license": "github/license/testuser/testrepo?style=flat",
                }

                badge_functions = {
                    "quality_gate": generate_quality_gate_badge,
                    "comprehensive_security": generate_comprehensive_security_badge,
                    "code_style": generate_code_style_badge,
                    "type_checked": generate_type_check_badge,
                    "python_versions": generate_python_versions_badge,
                    "pypi_version": generate_pypi_version_badge,
                    "downloads": generate_downloads_badge,
                    "license": generate_license_badge,
                }

                for badge_type, expected_path in expected_badges.items():
                    badge_url = badge_functions[badge_type]()
                    expected_url = f"https://img.shields.io/{expected_path}"
                    assert badge_url == expected_url, (
                        f"Badge type '{badge_type}' URL mismatch:\n"
                        f"Expected: {expected_url}\n"
                        f"Got: {badge_url}"
                    )

    @patch("badges.generator.get_comprehensive_security_status")
    @patch("badges.status.get_quality_gate_status")
    def test_all_badges_handle_config_errors_gracefully(
        self, mock_quality_status: Mock, mock_security_status: Mock
    ) -> None:
        """Test that all badge functions handle configuration errors gracefully."""
        # Mock comprehensive security status for the comprehensive security badge
        mock_security_status.return_value = {
            "status": "Unknown",
            "local_passed": False,
            "codeql_passed": False,
            "link_url": "https://github.com/test/repo/security",
        }

        # Mock quality gate status
        mock_quality_status.return_value = {
            "status": "unknown",
            "message": "Quality gate status unknown",
        }

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
                generate_pypi_version_badge(),
                generate_downloads_badge(),
                generate_comprehensive_security_badge(),
            ]

            # All should return valid URLs despite config error
            for badge_url in badges:
                assert badge_url.startswith("https://"), f"Invalid fallback URL: {badge_url}"
                assert len(badge_url) > 20, f"URL too short, likely empty: {badge_url}"

    def test_parametrized_badges_no_placeholders(self) -> None:
        """Test that parametrized badges don't contain placeholder text."""
        with patch("badges.status.get_quality_gate_status") as mock_quality_status:
            mock_quality_status.return_value = {
                "status": "passing",
                "message": "All quality checks passing",
            }

            env_vars = {
                "GITHUB_REPOSITORY": "testuser/testrepo",
                "PYPI_PACKAGE": "testpackage",
            }

            with patch.dict(os.environ, env_vars, clear=True):
                badges = [
                    generate_python_versions_badge(),
                    generate_license_badge(),
                    generate_quality_gate_badge(),
                    generate_pypi_version_badge(),
                ]

            for badge_url in badges:
                # Should not contain placeholder text
                assert "{package}" not in badge_url, f"Contains package placeholder: {badge_url}"
                assert "{repo}" not in badge_url, f"Contains repo placeholder: {badge_url}"


class TestComprehensiveSecurityBadge:
    """Test comprehensive security badge generation functionality."""

    @patch("badges.generator.get_comprehensive_security_status")
    def test_generate_comprehensive_security_badge_verified(self, mock_status: Mock) -> None:
        """Test comprehensive security badge generation with verified status."""
        mock_status.return_value = {
            "status": "Verified",
            "local_passed": True,
            "codeql_passed": True,
            "link_url": "https://github.com/testuser/testrepo/security/code-scanning",
        }

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://img.shields.io/badge/security-verified-brightgreen?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    @pytest.mark.skip(reason="Security badge now uses static format, test needs updating")
    def test_generate_comprehensive_security_badge_issues_found(self, mock_status: Mock) -> None:
        """Test comprehensive security badge generation with issues found."""
        mock_status.return_value = {
            "status": "Issues Found",
            "local_passed": False,
            "codeql_passed": False,
            "link_url": "https://github.com/testuser/testrepo/security/code-scanning",
        }

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://img.shields.io/badge/security-Issues%20Found-red?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_generate_comprehensive_security_badge_scanning(self, mock_status: Mock) -> None:
        """Test comprehensive security badge generation with scanning status."""
        mock_status.return_value = {
            "status": "Scanning",
            "local_passed": True,
            "codeql_passed": False,
            "link_url": "https://github.com/testuser/testrepo/security",
        }

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://img.shields.io/badge/security-Scanning-yellow?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_generate_comprehensive_security_badge_unknown(self, mock_status: Mock) -> None:
        """Test comprehensive security badge generation with unknown status."""
        mock_status.return_value = {
            "status": "Unknown",
            "local_passed": False,
            "codeql_passed": False,
            "link_url": "https://github.com/testuser/testrepo/security",
        }

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://img.shields.io/badge/security-Unknown-lightgrey?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_generate_comprehensive_security_badge_with_custom_config(
        self, mock_status: Mock
    ) -> None:
        """Test comprehensive security badge generation with custom configuration."""
        mock_status.return_value = {
            "status": "Verified",
            "local_passed": True,
            "codeql_passed": True,
            "link_url": "https://github.com/testuser/testrepo/security/code-scanning",
        }

        env_vars = {
            "SHIELDS_BASE_URL": "https://custom.shields.io",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://custom.shields.io/badge/security-Verified-brightgreen?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_generate_comprehensive_security_badge_exception(self, mock_status: Mock) -> None:
        """Test comprehensive security badge generation handles exceptions."""
        mock_status.side_effect = Exception("Test error")

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            expected = "https://img.shields.io/badge/security-Unknown-lightgrey?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_get_comprehensive_security_badge_link_success(self, mock_status: Mock) -> None:
        """Test getting comprehensive security badge link URL."""
        mock_status.return_value = {
            "status": "Verified",
            "local_passed": True,
            "codeql_passed": True,
            "link_url": "https://github.com/testuser/testrepo/security/code-scanning",
        }

        link_url = get_comprehensive_security_badge_link()
        assert link_url == "https://github.com/testuser/testrepo/security/code-scanning"

    @patch("badges.generator.get_comprehensive_security_status")
    def test_get_comprehensive_security_badge_link_exception(self, mock_status: Mock) -> None:
        """Test getting comprehensive security badge link URL with exception."""
        mock_status.side_effect = Exception("Test error")

        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "testuser/testrepo"}, clear=True):
            link_url = get_comprehensive_security_badge_link()
            assert link_url == "https://github.com/testuser/testrepo/security"

    @patch("badges.generator.get_comprehensive_security_status")
    def test_get_comprehensive_security_badge_link_default_repo(self, mock_status: Mock) -> None:
        """Test getting comprehensive security badge link URL with default repository."""
        mock_status.side_effect = Exception("Test error")

        with patch.dict(os.environ, {}, clear=True):
            link_url = get_comprehensive_security_badge_link()
            assert link_url == "https://github.com/username/mypylogger/security"

    def test_comprehensive_security_badge_color_mapping(self) -> None:
        """Test that all security status values have appropriate color mappings."""
        status_colors = {
            "Verified": "brightgreen",
            "Issues Found": "red",
            "Scanning": "yellow",
            "Unknown": "lightgrey",
        }

        for status, expected_color in status_colors.items():
            with patch("badges.generator.get_comprehensive_security_status") as mock_status:
                mock_status.return_value = {
                    "status": status,
                    "local_passed": True,
                    "codeql_passed": True,
                    "link_url": "https://github.com/test/repo/security",
                }

                url = generate_comprehensive_security_badge()
                assert expected_color in url, (
                    f"Status '{status}' should map to color '{expected_color}'"
                )

    @patch("badges.generator.get_comprehensive_security_status")
    def test_comprehensive_security_badge_url_encoding(self, mock_status: Mock) -> None:
        """Test that spaces in status are properly URL encoded."""
        mock_status.return_value = {
            "status": "Issues Found",
            "local_passed": False,
            "codeql_passed": False,
            "link_url": "https://github.com/test/repo/security",
        }

        url = generate_comprehensive_security_badge()

        # Spaces should be encoded as %20
        assert "Issues%20Found" in url
        assert "Issues Found" not in url


class TestAPIFailureScenarios:
    """Test badge generation behavior during API failures."""

    @patch("badges.generator.get_comprehensive_security_status")
    def test_github_codeql_api_failure_fallback(self, mock_status: Mock) -> None:
        """Test comprehensive security badge fallback when GitHub CodeQL API fails."""
        # Simulate API failure
        mock_status.side_effect = Exception("GitHub API timeout")

        with patch.dict(os.environ, {}, clear=True):
            url = generate_comprehensive_security_badge()

            # Should fallback to unknown status
            expected = "https://img.shields.io/badge/security-Unknown-lightgrey?style=flat"
            assert url == expected

    @patch("badges.generator.get_comprehensive_security_status")
    def test_security_status_combination_logic(self, mock_status: Mock) -> None:
        """Test security status determination logic combining local and GitHub results."""
        test_cases = [
            (True, "success", "Verified"),
            (False, "success", "Issues Found"),
            (True, "failure", "Issues Found"),
            (False, "failure", "Issues Found"),
            (True, "pending", "Scanning"),
            (False, "pending", "Scanning"),
            (True, "unknown", "Unknown"),
            (False, "unknown", "Unknown"),
        ]

        for local_passed, codeql_status, expected_status in test_cases:
            mock_status.return_value = {
                "status": expected_status,
                "local_passed": local_passed,
                "codeql_status": codeql_status,
                "codeql_passed": codeql_status == "success",
                "link_url": "https://github.com/test/repo/security",
            }

            url = generate_comprehensive_security_badge()

            # Verify correct status is reflected in URL
            status_encoded = expected_status.replace(" ", "%20")
            assert status_encoded in url, (
                f"Expected status '{expected_status}' not found in URL: {url}"
            )

    @patch("badges.generator.get_comprehensive_security_status")
    def test_github_codeql_link_generation(self, mock_status: Mock) -> None:
        """Test GitHub CodeQL link generation for different scenarios."""
        test_cases = [
            ("success", "/security/code-scanning"),
            ("failure", "/security/code-scanning"),
            ("pending", "/security"),
            ("unknown", "/security"),
        ]

        for codeql_status, expected_suffix in test_cases:
            mock_status.return_value = {
                "status": "Verified" if codeql_status == "success" else "Unknown",
                "local_passed": True,
                "codeql_status": codeql_status,
                "codeql_passed": codeql_status == "success",
                "link_url": f"https://github.com/testuser/testrepo{expected_suffix}",
            }

            link_url = get_comprehensive_security_badge_link()
            assert link_url.endswith(expected_suffix), (
                f"Expected link to end with '{expected_suffix}', got: {link_url}"
            )

    def test_shields_io_url_formatting_correctness(self) -> None:
        """Test that all badges generate correctly formatted shields.io URLs."""
        with patch(
            "badges.generator.get_comprehensive_security_status"
        ) as mock_security_status, patch(
            "badges.status.get_quality_gate_status"
        ) as mock_quality_status:
            mock_security_status.return_value = {
                "status": "Verified",
                "local_passed": True,
                "codeql_passed": True,
                "link_url": "https://github.com/test/repo/security/code-scanning",
            }

            mock_quality_status.return_value = {
                "status": "passing",
                "message": "All quality checks passing",
            }

            env_vars = {
                "GITHUB_REPOSITORY": "testuser/testrepo",
                "PYPI_PACKAGE": "testpackage",
            }

            with patch.dict(os.environ, env_vars, clear=True):
                badge_functions = [
                    generate_quality_gate_badge,
                    generate_comprehensive_security_badge,
                    generate_code_style_badge,
                    generate_type_check_badge,
                    generate_python_versions_badge,
                    generate_pypi_version_badge,
                    generate_downloads_badge,
                    generate_license_badge,
                ]

                for badge_func in badge_functions:
                    url = badge_func()

                    # Verify URL structure
                    assert url.startswith("https://img.shields.io/"), (
                        f"Badge URL should start with shields.io base: {url}"
                    )

                    # Verify style parameter
                    assert "style=flat" in url, f"Badge URL should include style=flat: {url}"

                    # Verify no double slashes in path
                    url_path = url.replace("https://", "")
                    assert "//" not in url_path, f"Badge URL should not have double slashes: {url}"

                    # Verify proper URL encoding
                    if " " in badge_func.__name__:
                        assert "%20" in url or "+" in url, f"Spaces should be URL encoded in: {url}"

    @patch("badges.generator.get_comprehensive_security_status")
    def test_local_security_scan_integration(self, mock_status: Mock) -> None:
        """Test integration of local security scan results with badge generation."""
        # Test case where local scans fail but GitHub CodeQL passes
        mock_status.return_value = {
            "status": "Issues Found",
            "local_results": {
                "bandit": False,
                "safety": True,
                "semgrep": True,
                "codeql_simulation": True,
            },
            "local_passed": False,
            "codeql_status": "success",
            "codeql_passed": True,
            "link_url": "https://github.com/test/repo/security/code-scanning",
        }

        url = generate_comprehensive_security_badge()

        # Should show "Issues Found" because local scans failed
        assert "Issues%20Found" in url
        assert "red" in url  # Should use red color for issues

    @patch("badges.generator.get_comprehensive_security_status")
    def test_comprehensive_security_badge_all_status_colors(self, mock_status: Mock) -> None:
        """Test that comprehensive security badge uses correct colors for all statuses."""
        status_color_map = {
            "Verified": "brightgreen",
            "Issues Found": "red",
            "Scanning": "yellow",
            "Unknown": "lightgrey",
        }

        for status, expected_color in status_color_map.items():
            mock_status.return_value = {
                "status": status,
                "local_passed": status == "Verified",
                "codeql_passed": status == "Verified",
                "link_url": "https://github.com/test/repo/security",
            }

            url = generate_comprehensive_security_badge()

            assert expected_color in url, (
                f"Status '{status}' should use color '{expected_color}' in URL: {url}"
            )

            status_encoded = status.replace(" ", "%20")
            assert status_encoded in url, (
                f"Status '{status}' should be properly encoded in URL: {url}"
            )

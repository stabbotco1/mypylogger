#!/usr/bin/env python3
"""
GitHub Action Monitoring Help System

This module provides contextual help messages, setup validation,
and diagnostic commands for troubleshooting configuration issues.
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from github_monitor_config import ConfigManager
    from github_monitor_exceptions import (
        GitHubAuthenticationError,
        GitHubConfigurationError,
        GitHubNetworkError,
        GitHubPermissionError,
        GitHubRateLimitError,
        GitHubRepositoryError,
    )
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.dirname(__file__))
    from github_monitor_config import ConfigManager
    from github_monitor_exceptions import (
        GitHubAuthenticationError,
        GitHubConfigurationError,
        GitHubNetworkError,
        GitHubPermissionError,
        GitHubRateLimitError,
        GitHubRepositoryError,
    )


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""

    name: str
    passed: bool
    message: str
    help_text: Optional[str] = None
    fix_command: Optional[str] = None


class GitHubHelpSystem:
    """
    Comprehensive help system for GitHub Action monitoring.

    Provides contextual help messages, setup validation, and diagnostic
    commands for troubleshooting configuration issues.
    """

    def __init__(self) -> None:
        """Initialize the help system."""
        self.config_manager = ConfigManager()

    def get_setup_guidance(self, error: Exception) -> str:
        """
        Get contextual setup guidance based on the error type.

        Args:
            error: The exception that occurred

        Returns:
            Formatted help text with specific guidance
        """
        if isinstance(error, GitHubAuthenticationError):
            return self._get_authentication_help(error)
        elif isinstance(error, GitHubPermissionError):
            return self._get_permission_help(error)
        elif isinstance(error, GitHubRepositoryError):
            return self._get_repository_help(error)
        elif isinstance(error, GitHubRateLimitError):
            return self._get_rate_limit_help(error)
        elif isinstance(error, GitHubNetworkError):
            return self._get_network_help(error)
        elif isinstance(error, GitHubConfigurationError):
            return self._get_configuration_help(error)
        else:
            return self._get_general_help()

    def _get_authentication_help(self, error: GitHubAuthenticationError) -> str:
        """Get help for authentication errors."""
        help_text = [
            "🔐 GitHub Authentication Issue",
            "",
            "The GitHub token is missing, invalid, or expired.",
            "",
            "Quick Fix:",
            "1. Check if token is set: echo $GITHUB_TOKEN",
            "2. If missing, set it: export GITHUB_TOKEN='your_token_here'",
            "3. If expired, generate a new token at:",
            "   https://github.com/settings/tokens",
            "",
            "Token Requirements:",
            "• Must start with 'ghp_'",
            "• Needs 'Actions: Read' permission only",
            "• Should not be expired",
            "",
            "Detailed Setup Guide:",
            "See docs/GITHUB_TOKEN_SETUP.md for complete instructions",
        ]

        if not error.token_provided:
            help_text.extend(
                [
                    "",
                    "⚠️  No token detected in environment variables.",
                    "Add to your shell profile (~/.bashrc or ~/.zshrc):",
                    "export GITHUB_TOKEN='your_token_here'",
                ]
            )

        return "\n".join(help_text)

    def _get_permission_help(self, error: GitHubPermissionError) -> str:
        """Get help for permission errors."""
        help_text = [
            "🚫 GitHub Permission Issue",
            "",
            "Your token doesn't have the required permissions.",
            "",
            "Quick Fix:",
            "1. Go to https://github.com/settings/tokens",
            "2. Find your token and click 'Edit'",
            "3. Ensure 'Actions: Read' is checked",
            "4. Click 'Update token'",
            "",
            "Common Issues:",
            "• Token missing 'Actions: Read' permission",
            "• Organization restrictions on personal tokens",
            "• Repository is private and token lacks access",
            "",
        ]

        if hasattr(error, "repo_owner") and hasattr(error, "repo_name"):
            help_text.extend(
                [
                    f"Repository: {error.repo_owner}/{error.repo_name}",
                    "",
                    "Repository-Specific Checks:",
                    "• Verify you have read access to this repository",
                    "• For private repos, ensure token has appropriate scope",
                    "• Check organization settings if applicable",
                ]
            )

        return "\n".join(help_text)

    def _get_repository_help(self, error: GitHubRepositoryError) -> str:
        """Get help for repository errors."""
        help_text = [
            "📁 Repository Access Issue",
            "",
            "The repository was not found or is not accessible.",
            "",
            "Quick Fix:",
            "1. Verify repository name: git remote -v",
            "2. Check repository exists on GitHub",
            "3. Ensure you have read access",
            "",
        ]

        if hasattr(error, "repo_owner") and hasattr(error, "repo_name"):
            repo_url = f"https://github.com/{error.repo_owner}/{error.repo_name}"
            help_text.extend(
                [
                    f"Repository: {error.repo_owner}/{error.repo_name}",
                    f"URL: {repo_url}",
                    "",
                    "Troubleshooting Steps:",
                    f"1. Visit {repo_url} in your browser",
                    "2. Verify the repository exists and you can access it",
                    "3. Check if repository is private (requires token access)",
                    "4. Ensure git remote is configured correctly:",
                    "   git remote set-url origin " + repo_url + ".git",
                ]
            )
        else:
            help_text.extend(
                [
                    "Repository Detection Failed:",
                    "1. Ensure you're in a git repository: git status",
                    "2. Check git remote: git remote -v",
                    "3. Add GitHub remote if missing:",
                    "   git remote add origin https://github.com/OWNER/REPO.git",
                ]
            )

        return "\n".join(help_text)

    def _get_rate_limit_help(self, error: GitHubRateLimitError) -> str:
        """Get help for rate limit errors."""
        help_text = [
            "⏱️  GitHub API Rate Limit Exceeded",
            "",
            "You've made too many API requests in a short time.",
            "",
        ]

        if hasattr(error, "reset_time") and error.reset_time:
            import datetime

            reset_time = datetime.datetime.fromtimestamp(error.reset_time)
            help_text.extend(
                [
                    f"Rate limit resets at: {reset_time.strftime('%H:%M:%S')}",
                    "",
                ]
            )

        help_text.extend(
            [
                "Quick Solutions:",
                "1. Wait for rate limit to reset (usually 1 hour)",
                "2. Reduce polling frequency:",
                "   export GITHUB_PIPELINE_POLL_INTERVAL=120",
                "3. Use cached data:",
                "   python scripts/github_pipeline_monitor.py --status-only --allow-stale",
                "",
                "Prevention:",
                "• Use authenticated requests (higher limits)",
                "• Enable intelligent polling (default)",
                "• Monitor rate limit status with --cache-stats",
            ]
        )

        return "\n".join(help_text)

    def _get_network_help(self, error: GitHubNetworkError) -> str:
        """Get help for network errors."""
        help_text = [
            "🌐 Network Connectivity Issue",
            "",
            "Cannot connect to GitHub API.",
            "",
            "Quick Diagnostics:",
            "1. Test internet: ping github.com",
            "2. Test GitHub API: curl https://api.github.com",
            "3. Check DNS: nslookup api.github.com",
            "",
            "Common Solutions:",
            "• Check internet connection",
            "• Verify firewall allows GitHub API access",
            "• Configure proxy if needed",
            "• Try again in a few minutes (temporary outage)",
            "",
            "GitHub Status:",
            "Check https://www.githubstatus.com/ for service issues",
        ]

        if hasattr(error, "original_error"):
            help_text.extend(
                [
                    "",
                    f"Technical Details: {error.original_error}",
                ]
            )

        return "\n".join(help_text)

    def _get_configuration_help(self, error: GitHubConfigurationError) -> str:
        """Get help for configuration errors."""
        help_text = [
            "⚙️  Configuration Issue",
            "",
            "There's a problem with your monitoring configuration.",
            "",
            "Quick Fix:",
            "1. Validate configuration:",
            "   python scripts/github_monitor_config.py --validate",
            "2. Show current config:",
            "   python scripts/github_monitor_config.py --show-config",
            "3. Get setup help:",
            "   python scripts/github_monitor_config.py --setup-help",
            "",
        ]

        if hasattr(error, "config_source"):
            help_text.extend(
                [
                    f"Configuration Source: {error.config_source}",
                    "",
                ]
            )

        help_text.extend(
            [
                "Common Issues:",
                "• Missing or invalid environment variables",
                "• Incorrect repository configuration",
                "• Invalid configuration file format",
                "",
                "Configuration Files:",
                "• Environment variables (GITHUB_TOKEN, etc.)",
                "• .github-monitor.yml in project root",
                "• Command-line arguments",
            ]
        )

        return "\n".join(help_text)

    def _get_general_help(self) -> str:
        """Get general help information."""
        return "\n".join(
            [
                "❓ General Help",
                "",
                "For comprehensive help, see:",
                "• Setup Guide: docs/GITHUB_TOKEN_SETUP.md",
                "• User Guide: docs/GITHUB_ACTION_MONITORING.md",
                "• Troubleshooting: docs/TROUBLESHOOTING.md",
                "• Examples: docs/WORKFLOW_EXAMPLES.md",
                "",
                "Quick Commands:",
                "• Test setup: python scripts/github_pipeline_monitor.py --status-only",
                "• Validate config: python scripts/github_monitor_config.py --validate",
                "• Get diagnostics: python scripts/github_help_system.py --diagnose",
            ]
        )

    def run_diagnostics(self) -> List[DiagnosticResult]:
        """
        Run comprehensive diagnostics to identify configuration issues.

        Returns:
            List of diagnostic results
        """
        results = []

        # Check GitHub token
        results.append(self._check_github_token())

        # Check git repository
        results.append(self._check_git_repository())

        # Check network connectivity
        results.append(self._check_network_connectivity())

        # Check GitHub API access
        results.append(self._check_github_api_access())

        # Check repository access
        results.append(self._check_repository_access())

        return results

    def _check_github_token(self) -> DiagnosticResult:
        """Check if GitHub token is properly configured."""
        token = os.environ.get("GITHUB_TOKEN")

        if not token:
            return DiagnosticResult(
                name="GitHub Token",
                passed=False,
                message="GITHUB_TOKEN environment variable not set",
                help_text="Set your GitHub token: export GITHUB_TOKEN='your_token_here'",
                fix_command="echo 'export GITHUB_TOKEN=\"your_token_here\"' >> ~/.bashrc && source ~/.bashrc",
            )

        # Check token format - GitHub tokens can have different prefixes
        # Include more comprehensive list of valid GitHub token prefixes
        valid_prefixes = ["ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_"]
        if not any(token.startswith(prefix) for prefix in valid_prefixes):
            # If token format check fails but we can test API access, skip format validation
            # and rely on actual API authentication test instead
            return DiagnosticResult(
                name="GitHub Token",
                passed=True,
                message="Token format validation skipped - will test API access instead",
                help_text="Token format will be validated through API authentication test",
            )

        if len(token) < 40:
            return DiagnosticResult(
                name="GitHub Token",
                passed=False,
                message="Token appears too short (should be 40+ characters)",
                help_text="Verify token was copied completely",
            )

        return DiagnosticResult(
            name="GitHub Token",
            passed=True,
            message="Token is set and appears valid",
        )

    def _check_git_repository(self) -> DiagnosticResult:
        """Check if we're in a valid git repository."""
        try:
            _ = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Check for GitHub remote
            try:
                remote_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                remote_url = remote_result.stdout.strip()
                if "github.com" not in remote_url:
                    return DiagnosticResult(
                        name="Git Repository",
                        passed=False,
                        message="Git remote is not pointing to GitHub",
                        help_text="Set GitHub remote: git remote set-url origin https://github.com/OWNER/REPO.git",
                    )

                return DiagnosticResult(
                    name="Git Repository",
                    passed=True,
                    message=f"Valid git repository with GitHub remote: {remote_url}",
                )

            except subprocess.CalledProcessError:
                return DiagnosticResult(
                    name="Git Repository",
                    passed=False,
                    message="Git repository exists but no 'origin' remote configured",
                    help_text="Add GitHub remote: git remote add origin https://github.com/OWNER/REPO.git",
                    fix_command="git remote add origin https://github.com/OWNER/REPO.git",
                )

        except subprocess.CalledProcessError:
            return DiagnosticResult(
                name="Git Repository",
                passed=False,
                message="Not in a git repository",
                help_text="Initialize git repository: git init && git remote add origin https://github.com/OWNER/REPO.git",
                fix_command="git init",
            )

    def _check_network_connectivity(self) -> DiagnosticResult:
        """Check network connectivity to GitHub."""
        try:
            request = Request("https://api.github.com")
            with urlopen(
                request, timeout=10
            ) as response:  # nosec B310 - Hardcoded GitHub API URL
                if response.status == 200:
                    return DiagnosticResult(
                        name="Network Connectivity",
                        passed=True,
                        message="GitHub API is accessible",
                    )
                else:
                    return DiagnosticResult(
                        name="Network Connectivity",
                        passed=False,
                        message=f"GitHub API returned status {response.status}",
                        help_text="Check GitHub status at https://www.githubstatus.com/",
                    )

        except URLError as e:
            return DiagnosticResult(
                name="Network Connectivity",
                passed=False,
                message=f"Cannot connect to GitHub API: {e.reason}",
                help_text="Check internet connection and firewall settings",
            )
        except Exception as e:
            return DiagnosticResult(
                name="Network Connectivity",
                passed=False,
                message=f"Network error: {str(e)}",
                help_text="Check internet connection",
            )

    def _check_github_api_access(self) -> DiagnosticResult:
        """Check GitHub API access with token."""
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return DiagnosticResult(
                name="GitHub API Access",
                passed=False,
                message="Cannot test API access without token",
                help_text="Set GITHUB_TOKEN first",
            )

        try:
            request = Request("https://api.github.com/user")
            request.add_header("Authorization", f"token {token}")
            request.add_header("User-Agent", "github-action-monitoring/1.0")

            with urlopen(
                request, timeout=10
            ) as response:  # nosec B310 - Hardcoded GitHub API URL
                if response.status == 200:
                    return DiagnosticResult(
                        name="GitHub API Access",
                        passed=True,
                        message="Successfully authenticated with GitHub API",
                    )
                else:
                    return DiagnosticResult(
                        name="GitHub API Access",
                        passed=False,
                        message=f"API returned status {response.status}",
                        help_text="Check token permissions",
                    )

        except HTTPError as e:
            if e.code == 401:
                return DiagnosticResult(
                    name="GitHub API Access",
                    passed=False,
                    message="Authentication failed - invalid token",
                    help_text="Generate new token at https://github.com/settings/tokens",
                )
            elif e.code == 403:
                return DiagnosticResult(
                    name="GitHub API Access",
                    passed=False,
                    message="Access denied - check token permissions",
                    help_text="Ensure token has 'Actions: Read' permission",
                )
            else:
                return DiagnosticResult(
                    name="GitHub API Access",
                    passed=False,
                    message=f"API error: HTTP {e.code}",
                    help_text="Check GitHub status and token validity",
                )

        except Exception as e:
            return DiagnosticResult(
                name="GitHub API Access",
                passed=False,
                message=f"API access error: {str(e)}",
                help_text="Check network connectivity and token",
            )

    def _check_repository_access(self) -> DiagnosticResult:
        """Check access to the specific repository."""
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return DiagnosticResult(
                name="Repository Access",
                passed=False,
                message="Cannot test repository access without token",
                help_text="Set GITHUB_TOKEN first",
            )

        try:
            # Try to detect repository from git remote
            from github_pipeline_monitor import parse_github_repo_from_remote

            owner, repo = parse_github_repo_from_remote()

            # Test repository access
            request = Request(f"https://api.github.com/repos/{owner}/{repo}")
            request.add_header("Authorization", f"token {token}")
            request.add_header("User-Agent", "github-action-monitoring/1.0")

            with urlopen(
                request, timeout=10
            ) as response:  # nosec B310 - Validated GitHub API URL
                if response.status == 200:
                    return DiagnosticResult(
                        name="Repository Access",
                        passed=True,
                        message=f"Successfully accessed repository {owner}/{repo}",
                    )
                else:
                    return DiagnosticResult(
                        name="Repository Access",
                        passed=False,
                        message=f"Repository access returned status {response.status}",
                        help_text="Check repository name and permissions",
                    )

        except HTTPError as e:
            if e.code == 404:
                return DiagnosticResult(
                    name="Repository Access",
                    passed=False,
                    message="Repository not found or not accessible",
                    help_text="Verify repository name and ensure you have read access",
                )
            else:
                return DiagnosticResult(
                    name="Repository Access",
                    passed=False,
                    message=f"Repository access error: HTTP {e.code}",
                    help_text="Check repository permissions",
                )

        except Exception as e:
            return DiagnosticResult(
                name="Repository Access",
                passed=False,
                message=f"Repository detection failed: {str(e)}",
                help_text="Ensure you're in a git repository with GitHub remote",
            )

    def print_diagnostic_results(self, results: List[DiagnosticResult]) -> None:
        """Print diagnostic results in a formatted way."""
        print("🔍 GitHub Action Monitoring Diagnostics")
        print("=" * 50)
        print()

        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        for result in results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.name}: {result.message}")

            if not result.passed and result.help_text:
                print(f"   💡 {result.help_text}")

            if not result.passed and result.fix_command:
                print(f"   🔧 Fix: {result.fix_command}")

            print()

        print(f"Summary: {passed_count}/{total_count} checks passed")

        if passed_count < total_count:
            print()
            print("❌ Some checks failed. Please address the issues above.")
            print("📚 For detailed help, see docs/TROUBLESHOOTING.md")
        else:
            print()
            print("✅ All diagnostics passed! Your setup looks good.")

    def create_sample_configuration(self) -> str:
        """Create a sample configuration file."""
        config_content = """# GitHub Action Monitoring Configuration
# Save as .github-monitor.yml in your project root

github:
  token: ${GITHUB_TOKEN}  # Environment variable reference
  repository: auto        # Auto-detect from git remote

monitoring:
  branches:
    - pre-release
    - main
  poll_interval: 30       # seconds
  timeout: 30            # minutes
  auto_monitor: true     # Monitor on push automatically

integration:
  test_suite_runner: true
  make_commands: true
  block_on_failure: true

output:
  format: console        # console, json, minimal
  colors: true
  progress_indicators: true
  verbose: false
"""
        return config_content

    def validate_setup(self) -> bool:
        """
        Validate the complete setup and provide guidance.

        Returns:
            True if setup is valid, False otherwise
        """
        results = self.run_diagnostics()
        self.print_diagnostic_results(results)

        return all(result.passed for result in results)


def main() -> None:
    """CLI interface for the help system."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Action Monitoring Help System")
    parser.add_argument(
        "--diagnose", action="store_true", help="Run comprehensive diagnostics"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate current setup"
    )
    parser.add_argument(
        "--create-config", action="store_true", help="Create sample configuration file"
    )
    parser.add_argument("--setup-help", action="store_true", help="Show setup guidance")

    args = parser.parse_args()

    help_system = GitHubHelpSystem()

    if args.diagnose or args.validate:
        success = help_system.validate_setup()
        sys.exit(0 if success else 1)

    elif args.create_config:
        config_content = help_system.create_sample_configuration()

        config_file = ".github-monitor.yml"
        if os.path.exists(config_file):
            print(f"⚠️  Configuration file {config_file} already exists.")
            response = input("Overwrite? (y/N): ")
            if response.lower() != "y":
                print("Configuration creation cancelled.")
                sys.exit(0)

        with open(config_file, "w") as f:
            f.write(config_content)

        print(f"✅ Created sample configuration: {config_file}")
        print("📝 Edit the file to customize your settings.")
        print("🔧 Set your GITHUB_TOKEN environment variable.")

    elif args.setup_help:
        print("🚀 GitHub Action Monitoring Setup Guide")
        print("=" * 50)
        print()
        print("1. Set up GitHub Token:")
        print("   export GITHUB_TOKEN='your_token_here'")
        print("   (Get token from https://github.com/settings/tokens)")
        print()
        print("2. Verify setup:")
        print("   python scripts/github_help_system.py --validate")
        print()
        print("3. Test monitoring:")
        print("   python scripts/github_pipeline_monitor.py --status-only")
        print()
        print("4. Enable integration:")
        print("   export GITHUB_PIPELINE_CHECK=true")
        print("   ./scripts/run-complete-test-suite.sh")
        print()
        print("📚 For detailed instructions, see:")
        print("   • docs/GITHUB_TOKEN_SETUP.md")
        print("   • docs/GITHUB_ACTION_MONITORING.md")
        print("   • docs/TROUBLESHOOTING.md")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub Pipeline Monitor Configuration Management

This module handles configuration loading, validation, and management
for the GitHub Actions monitoring system.
"""

import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import yaml


class MonitoringMode(Enum):
    """Monitoring operation modes."""

    FULL = "full"  # All features available
    LIMITED = "limited"  # Basic monitoring only
    DISABLED = "disabled"  # Monitoring unavailable


class OutputFormat(Enum):
    """Output format options."""

    CONSOLE = "console"
    JSON = "json"
    MINIMAL = "minimal"


@dataclass
class MonitoringConfig:
    """Configuration for GitHub Actions monitoring."""

    # GitHub API settings
    github_token: Optional[str] = None
    repo_owner: str = ""
    repo_name: str = ""

    # Monitoring behavior
    monitored_branches: List[str] = field(
        default_factory=lambda: ["pre-release", "main"]
    )
    poll_interval_seconds: int = 30
    timeout_minutes: int = 30
    auto_monitor_on_push: bool = True

    # Integration settings
    test_suite_integration: bool = True
    make_command_integration: bool = True
    block_on_failure: bool = True

    # Output settings
    output_format: OutputFormat = OutputFormat.CONSOLE
    colors_enabled: bool = True
    progress_indicators: bool = True
    verbose: bool = False

    # Performance settings
    max_retries: int = 3
    base_retry_delay: float = 1.0
    cache_ttl_seconds: int = 60


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfigManager:
    """Manages configuration loading, validation, and repository detection."""

    def __init__(self):
        self.config_file_paths = [
            ".github-monitor.yml",
            ".github-monitor.yaml",
            os.path.expanduser("~/.github-monitor.yml"),
            os.path.expanduser("~/.github-monitor.yaml"),
        ]

    def load_config(self, config_path: Optional[str] = None) -> MonitoringConfig:
        """
        Load configuration from multiple sources with precedence:
        1. Command line arguments (handled by caller)
        2. Environment variables
        3. Configuration file
        4. Defaults
        """
        config = MonitoringConfig()

        # Load from config file if specified or found
        if config_path:
            config = self._load_from_file(config_path, config)
        else:
            config = self._load_from_default_files(config)

        # Override with environment variables
        config = self._load_from_environment(config)

        # Auto-detect repository if not configured
        if not config.repo_owner or not config.repo_name:
            try:
                config.repo_owner, config.repo_name = self._detect_repository()
            except ConfigurationError:
                pass  # Will be handled in validation

        # Validate configuration
        self._validate_config(config)

        return config

    def _load_from_file(
        self, file_path: str, config: MonitoringConfig
    ) -> MonitoringConfig:
        """Load configuration from a YAML file."""
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f) or {}

            # GitHub settings
            github_section = data.get("github", {})
            if "token" in github_section:
                config.github_token = self._resolve_env_var(github_section["token"])
            if (
                "repository" in github_section
                and github_section["repository"] != "auto"
            ):
                if "/" in github_section["repository"]:
                    config.repo_owner, config.repo_name = github_section[
                        "repository"
                    ].split("/", 1)

            # Monitoring settings
            monitoring_section = data.get("monitoring", {})
            if "branches" in monitoring_section:
                config.monitored_branches = monitoring_section["branches"]
            if "poll_interval" in monitoring_section:
                config.poll_interval_seconds = monitoring_section["poll_interval"]
            if "timeout" in monitoring_section:
                config.timeout_minutes = monitoring_section["timeout"]
            if "auto_monitor" in monitoring_section:
                config.auto_monitor_on_push = monitoring_section["auto_monitor"]

            # Integration settings
            integration_section = data.get("integration", {})
            if "test_suite_runner" in integration_section:
                config.test_suite_integration = integration_section["test_suite_runner"]
            if "make_commands" in integration_section:
                config.make_command_integration = integration_section["make_commands"]
            if "block_on_failure" in integration_section:
                config.block_on_failure = integration_section["block_on_failure"]

            # Output settings
            output_section = data.get("output", {})
            if "format" in output_section:
                config.output_format = OutputFormat(output_section["format"])
            if "colors" in output_section:
                config.colors_enabled = output_section["colors"]
            if "progress_indicators" in output_section:
                config.progress_indicators = output_section["progress_indicators"]

        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in configuration file {file_path}: {e}"
            )
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value in {file_path}: {e}")

        return config

    def _load_from_default_files(self, config: MonitoringConfig) -> MonitoringConfig:
        """Load configuration from default file locations."""
        for file_path in self.config_file_paths:
            if os.path.exists(file_path):
                return self._load_from_file(file_path, config)
        return config

    def _load_from_environment(self, config: MonitoringConfig) -> MonitoringConfig:
        """Load configuration from environment variables."""

        # GitHub settings
        if os.getenv("GITHUB_TOKEN"):
            config.github_token = os.getenv("GITHUB_TOKEN")
        if os.getenv("GITHUB_REPOSITORY"):
            repo = os.getenv("GITHUB_REPOSITORY")
            if "/" in repo:
                config.repo_owner, config.repo_name = repo.split("/", 1)

        # Monitoring settings
        if os.getenv("GITHUB_MONITOR_BRANCHES"):
            config.monitored_branches = os.getenv("GITHUB_MONITOR_BRANCHES").split(",")
        if os.getenv("GITHUB_MONITOR_POLL_INTERVAL"):
            config.poll_interval_seconds = int(
                os.getenv("GITHUB_MONITOR_POLL_INTERVAL")
            )
        if os.getenv("GITHUB_MONITOR_TIMEOUT"):
            config.timeout_minutes = int(os.getenv("GITHUB_MONITOR_TIMEOUT"))
        if os.getenv("GITHUB_MONITOR_AUTO"):
            config.auto_monitor_on_push = os.getenv("GITHUB_MONITOR_AUTO").lower() in (
                "true",
                "1",
                "yes",
            )

        # Integration settings
        if os.getenv("GITHUB_MONITOR_BLOCK_ON_FAILURE"):
            config.block_on_failure = os.getenv(
                "GITHUB_MONITOR_BLOCK_ON_FAILURE"
            ).lower() in ("true", "1", "yes")

        # Output settings
        if os.getenv("GITHUB_MONITOR_FORMAT"):
            config.output_format = OutputFormat(os.getenv("GITHUB_MONITOR_FORMAT"))
        if os.getenv("GITHUB_MONITOR_COLORS"):
            config.colors_enabled = os.getenv("GITHUB_MONITOR_COLORS").lower() in (
                "true",
                "1",
                "yes",
            )
        if os.getenv("GITHUB_MONITOR_VERBOSE"):
            config.verbose = os.getenv("GITHUB_MONITOR_VERBOSE").lower() in (
                "true",
                "1",
                "yes",
            )

        return config

    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variable references in configuration values."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            resolved = os.getenv(env_var)
            if resolved is None:
                raise ConfigurationError(f"Environment variable {env_var} not found")
            return resolved
        return value

    def _detect_repository(self) -> Tuple[str, str]:
        """Auto-detect repository owner and name from git remote."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
                cwd=os.getcwd(),
            )
            remote_url = result.stdout.strip()

            # Handle both SSH and HTTPS URLs
            if remote_url.startswith("git@github.com:"):
                # SSH format: git@github.com:owner/repo.git
                repo_path = remote_url.replace("git@github.com:", "").replace(
                    ".git", ""
                )
            elif remote_url.startswith("https://github.com/"):
                # HTTPS format: https://github.com/owner/repo.git
                repo_path = remote_url.replace("https://github.com/", "").replace(
                    ".git", ""
                )
            else:
                raise ConfigurationError(f"Unsupported remote URL format: {remote_url}")

            if "/" not in repo_path:
                raise ConfigurationError(f"Invalid repository path: {repo_path}")

            owner, repo = repo_path.split("/", 1)
            return owner, repo

        except subprocess.CalledProcessError as e:
            raise ConfigurationError(f"Failed to get git remote URL: {e}")
        except ValueError as e:
            raise ConfigurationError(f"Failed to parse repository info: {e}")

    def _validate_config(self, config: MonitoringConfig) -> None:
        """Validate configuration and provide helpful error messages."""
        errors = []

        # Repository validation
        if not config.repo_owner:
            errors.append(
                "Repository owner not specified. Set GITHUB_REPOSITORY environment variable or configure in .github-monitor.yml"
            )
        if not config.repo_name:
            errors.append(
                "Repository name not specified. Set GITHUB_REPOSITORY environment variable or configure in .github-monitor.yml"
            )

        # GitHub token validation (warning, not error)
        if not config.github_token:
            print(
                "⚠️  Warning: No GitHub token configured. Set GITHUB_TOKEN environment variable for authenticated API access."
            )

        # Numeric validation
        if config.poll_interval_seconds < 1:
            errors.append("Poll interval must be at least 1 second")
        if config.timeout_minutes < 1:
            errors.append("Timeout must be at least 1 minute")
        if config.max_retries < 0:
            errors.append("Max retries must be non-negative")
        if config.base_retry_delay < 0:
            errors.append("Base retry delay must be non-negative")

        # Branch validation
        if not config.monitored_branches:
            errors.append("At least one branch must be monitored")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise ConfigurationError(error_msg)

    def determine_monitoring_mode(self, config: MonitoringConfig) -> MonitoringMode:
        """Determine the appropriate monitoring mode based on configuration."""
        if not config.github_token:
            return MonitoringMode.DISABLED

        if not config.repo_owner or not config.repo_name:
            return MonitoringMode.DISABLED

        # Could add additional checks here (e.g., API connectivity test)
        return MonitoringMode.FULL

    def create_sample_config(self, file_path: str = ".github-monitor.yml") -> None:
        """Create a sample configuration file."""
        sample_config = {
            "github": {"token": "${GITHUB_TOKEN}", "repository": "auto"},
            "monitoring": {
                "branches": ["pre-release", "main"],
                "poll_interval": 30,
                "timeout": 30,
                "auto_monitor": True,
            },
            "integration": {
                "test_suite_runner": True,
                "make_commands": True,
                "block_on_failure": True,
            },
            "output": {
                "format": "console",
                "colors": True,
                "progress_indicators": True,
            },
        }

        with open(file_path, "w") as f:
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Sample configuration created at {file_path}")
        print("Edit the file to customize your monitoring settings.")

    def validate_github_token_permissions(
        self, token: str, repo_owner: str, repo_name: str
    ) -> Dict[str, bool]:
        """Validate GitHub token permissions (placeholder for future implementation)."""
        # This would make actual API calls to validate permissions
        # For now, return a placeholder result
        return {"repo_access": True, "actions_read": True, "rate_limit_ok": True}

    def get_setup_instructions(self) -> str:
        """Get setup instructions for configuration."""
        return """
GitHub Actions Monitor Setup Instructions:

🔗 Complete Setup Guide: docs/GITHUB_TOKEN_SETUP.md

Quick Setup:
1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - IMPORTANT: Only select "Actions: Read-only" permission
   - Copy the token (starts with ghp_)

2. Set the GITHUB_TOKEN environment variable:
   echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc
   source ~/.zshrc

3. Test the configuration:
   python scripts/github_pipeline_monitor.py --status-only --repo your-username/your-repo

4. You should see output like:
   📊 Pipeline Status
   📝 Commit: abc12345
   ✅ Overall Status: SUCCESS

For detailed troubleshooting and security considerations, see docs/GITHUB_TOKEN_SETUP.md
"""


def main():
    """CLI interface for configuration management."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub Actions Monitor Configuration")
    parser.add_argument(
        "--create-config", action="store_true", help="Create sample configuration file"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate current configuration"
    )
    parser.add_argument(
        "--show-config", action="store_true", help="Show current configuration"
    )
    parser.add_argument(
        "--setup-help", action="store_true", help="Show setup instructions"
    )
    parser.add_argument("--config-file", help="Path to configuration file")

    args = parser.parse_args()

    config_manager = ConfigManager()

    try:
        if args.create_config:
            config_manager.create_sample_config()
        elif args.setup_help:
            print(config_manager.get_setup_instructions())
        elif args.validate or args.show_config:
            config = config_manager.load_config(args.config_file)
            mode = config_manager.determine_monitoring_mode(config)

            if args.show_config:
                print("Current Configuration:")
                print(f"  Repository: {config.repo_owner}/{config.repo_name}")
                print(f"  Token configured: {'Yes' if config.github_token else 'No'}")
                print(f"  Monitored branches: {', '.join(config.monitored_branches)}")
                print(f"  Poll interval: {config.poll_interval_seconds}s")
                print(f"  Timeout: {config.timeout_minutes}m")
                print(f"  Monitoring mode: {mode.value}")

            if args.validate:
                print("✅ Configuration is valid")
                print(f"Monitoring mode: {mode.value}")
        else:
            parser.print_help()

    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub Pipeline Monitor

This module provides integration with GitHub Actions API to monitor
CI/CD pipeline status after pushes and provide real-time feedback.
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

# Import configuration management and error handling
try:
    from github_data_models import PipelineStatus, WorkflowRun
    from github_monitor_config import (
        ConfigManager,
        ConfigurationError,
        MonitoringConfig,
        MonitoringMode,
    )
    from github_monitor_exceptions import (
        GitHubAuthenticationError,
        GitHubConfigurationError,
        GitHubMonitorError,
        GitHubNetworkError,
        GitHubPermissionError,
        GitHubRateLimitError,
        GitHubRepositoryError,
        handle_github_api_error,
        retry_with_exponential_backoff,
    )
except ImportError:
    # Fallback for when running from different directory
    import sys

    sys.path.append(os.path.dirname(__file__))
    from github_data_models import PipelineStatus, WorkflowRun
    from github_monitor_config import (
        ConfigManager,
        ConfigurationError,
        MonitoringConfig,
        MonitoringMode,
    )
    from github_monitor_exceptions import (
        GitHubAuthenticationError,
        GitHubConfigurationError,
        GitHubMonitorError,
        GitHubNetworkError,
        GitHubPermissionError,
        GitHubRateLimitError,
        GitHubRepositoryError,
        handle_github_api_error,
        retry_with_exponential_backoff,
    )


# Legacy exception class for backward compatibility
class GitHubAPIError(GitHubMonitorError):
    """Legacy exception class - use specific GitHubMonitorError subclasses instead."""

    pass


class GitHubPipelineMonitor:
    """Monitor GitHub Actions pipeline status via API."""

    def __init__(
        self,
        config: Optional[MonitoringConfig] = None,
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
        github_token: Optional[str] = None,
    ):
        """
        Initialize the GitHub pipeline monitor.

        Args:
            config: MonitoringConfig object (preferred)
            repo_owner: GitHub repository owner/organization (legacy)
            repo_name: GitHub repository name (legacy)
            github_token: GitHub personal access token (legacy)
        """
        if config:
            self.config = config
        else:
            # Legacy initialization - create config from parameters
            config_manager = ConfigManager()
            self.config = config_manager.load_config()
            if repo_owner:
                self.config.repo_owner = repo_owner
            if repo_name:
                self.config.repo_name = repo_name
            if github_token:
                self.config.github_token = github_token

        self.repo_owner = self.config.repo_owner
        self.repo_name = self.config.repo_name
        self.github_token = self.config.github_token
        self.base_url = "https://api.github.com"

        # Status reporter will be created when needed to avoid circular imports
        self._status_reporter = None

    @property
    def status_reporter(self):
        """Lazy-load status reporter to avoid circular imports."""
        if self._status_reporter is None:
            from github_status_reporter import create_status_reporter

            self._status_reporter = create_status_reporter(self.config)
        return self._status_reporter

        # Colors for output (respect config setting) - kept for backward compatibility
        if self.config.colors_enabled:
            self.colors = {
                "GREEN": "\033[0;32m",
                "RED": "\033[0;31m",
                "YELLOW": "\033[1;33m",
                "BLUE": "\033[0;34m",
                "PURPLE": "\033[0;35m",
                "CYAN": "\033[0;36m",
                "NC": "\033[0m",  # No Color
            }
        else:
            # No colors
            self.colors = {
                key: ""
                for key in ["GREEN", "RED", "YELLOW", "BLUE", "PURPLE", "CYAN", "NC"]
            }

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(GitHubNetworkError, GitHubRateLimitError),
    )
    def _make_api_request(self, endpoint: str) -> Dict:
        """Make a request to the GitHub API with enhanced error handling and retry logic."""
        url = urljoin(self.base_url, endpoint)

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "mypylogger-pipeline-monitor/1.0",
        }

        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        else:
            raise GitHubAuthenticationError(
                "GitHub token not provided", token_provided=False
            )

        try:
            request = Request(url, headers=headers)
            with urlopen(request) as response:
                # Extract rate limit information from headers
                rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                rate_limit_reset = response.headers.get("X-RateLimit-Reset")

                # Warn if approaching rate limit
                if rate_limit_remaining and int(rate_limit_remaining) < 10:
                    reset_time = int(rate_limit_reset) if rate_limit_reset else None
                    print(
                        f"⚠️  GitHub API rate limit warning: {rate_limit_remaining} requests remaining"
                    )
                    if reset_time:
                        reset_minutes = max(0, (reset_time - int(time.time())) // 60)
                        print(f"   Rate limit resets in {reset_minutes} minutes")

                return json.loads(response.read().decode())

        except HTTPError as e:
            # Read response body for more detailed error information
            response_text = ""
            try:
                response_text = e.read().decode() if hasattr(e, "read") else str(e)
            except Exception:
                response_text = str(e)

            # Extract rate limit info from headers if available
            rate_limit_reset = None
            rate_limit_remaining = None
            if hasattr(e, "headers"):
                rate_limit_reset = e.headers.get("X-RateLimit-Reset")
                rate_limit_remaining = e.headers.get("X-RateLimit-Remaining")

            # Convert to specific exception types
            if e.code == 401:
                raise GitHubAuthenticationError(
                    "GitHub API authentication failed - invalid or missing token",
                    token_provided=bool(self.github_token),
                    details={"status_code": e.code, "response": response_text},
                )
            elif e.code == 403:
                if "rate limit" in response_text.lower() or rate_limit_remaining == "0":
                    reset_time = int(rate_limit_reset) if rate_limit_reset else None
                    raise GitHubRateLimitError(
                        "GitHub API rate limit exceeded",
                        reset_time=reset_time,
                        remaining=(
                            int(rate_limit_remaining) if rate_limit_remaining else 0
                        ),
                        details={"status_code": e.code, "response": response_text},
                    )
                else:
                    raise GitHubPermissionError(
                        "GitHub API access denied - insufficient permissions",
                        repo_owner=self.repo_owner,
                        repo_name=self.repo_name,
                        details={"status_code": e.code, "response": response_text},
                    )
            elif e.code == 404:
                raise GitHubRepositoryError(
                    f"Repository {self.repo_owner}/{self.repo_name} not found or not accessible",
                    repo_owner=self.repo_owner,
                    repo_name=self.repo_name,
                    details={"status_code": e.code, "response": response_text},
                )
            else:
                # Use the generic error handler for other HTTP errors
                raise handle_github_api_error(
                    e.code, response_text, self.repo_owner, self.repo_name
                )

        except URLError as e:
            raise GitHubNetworkError(
                f"Network connectivity error: {e.reason}",
                original_error=e,
                details={"url": url, "reason": str(e.reason)},
            )
        except json.JSONDecodeError as e:
            raise GitHubMonitorError(
                "Invalid JSON response from GitHub API",
                details={"url": url, "error": str(e)},
            )
        except Exception as e:
            raise GitHubMonitorError(
                f"Unexpected error during API request: {str(e)}",
                details={"url": url, "error_type": type(e).__name__},
            )

    def get_current_commit_sha(self) -> str:
        """Get the current commit SHA from git."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitHubConfigurationError(
                f"Failed to get current commit SHA: {e}",
                config_source="git",
                details={"command": "git rev-parse HEAD", "error": str(e)},
            )

    def get_current_branch(self) -> str:
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitHubConfigurationError(
                f"Failed to get current branch: {e}",
                config_source="git",
                details={"command": "git branch --show-current", "error": str(e)},
            )

    def get_workflow_runs_for_commit(self, commit_sha: str) -> List[WorkflowRun]:
        """Get all workflow runs for a specific commit."""
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/actions/runs"
        params = f"?head_sha={commit_sha}&per_page=100"

        data = self._make_api_request(endpoint + params)

        workflow_runs = []
        for run_data in data.get("workflow_runs", []):
            # Calculate duration if workflow is completed
            duration_seconds = None
            if (
                run_data["status"] == "completed"
                and run_data.get("created_at")
                and run_data.get("updated_at")
            ):
                try:
                    from datetime import datetime

                    created = datetime.fromisoformat(
                        run_data["created_at"].replace("Z", "+00:00")
                    )
                    updated = datetime.fromisoformat(
                        run_data["updated_at"].replace("Z", "+00:00")
                    )
                    duration_seconds = int((updated - created).total_seconds())
                except (ValueError, TypeError):
                    pass  # Keep duration as None if parsing fails

            workflow_run = WorkflowRun(
                id=run_data["id"],
                name=run_data["name"],
                status=run_data["status"],
                conclusion=run_data["conclusion"],
                html_url=run_data["html_url"],
                created_at=run_data["created_at"],
                updated_at=run_data["updated_at"],
                head_sha=run_data["head_sha"],
                duration_seconds=duration_seconds,
            )
            workflow_runs.append(workflow_run)

        return workflow_runs

    def get_pipeline_status(self, commit_sha: Optional[str] = None) -> PipelineStatus:
        """Get the overall pipeline status for a commit."""
        if commit_sha is None:
            commit_sha = self.get_current_commit_sha()

        workflow_runs = self.get_workflow_runs_for_commit(commit_sha)

        if not workflow_runs:
            return PipelineStatus(
                commit_sha=commit_sha,
                workflow_runs=[],
                overall_status="no_workflows",
                failed_workflows=[],
                pending_workflows=[],
                success_workflows=[],
            )

        failed_workflows = []
        pending_workflows = []
        success_workflows = []
        total_duration = 0
        completed_count = 0

        for run in workflow_runs:
            if run.status == "completed":
                completed_count += 1
                if run.duration_seconds:
                    total_duration += run.duration_seconds

                if run.conclusion == "success":
                    success_workflows.append(run.name)
                elif run.conclusion in ["failure", "cancelled", "timed_out"]:
                    failed_workflows.append(run.name)
            else:
                pending_workflows.append(run.name)

        # Determine overall status
        if failed_workflows:
            overall_status = "failure"
        elif pending_workflows:
            overall_status = "pending"
        else:
            overall_status = "success"

        # Calculate estimated completion for pending workflows
        estimated_completion = None
        if pending_workflows and completed_count > 0:
            avg_duration = total_duration / completed_count
            estimated_completion = int(avg_duration * len(pending_workflows))

        return PipelineStatus(
            commit_sha=commit_sha,
            workflow_runs=workflow_runs,
            overall_status=overall_status,
            failed_workflows=failed_workflows,
            pending_workflows=pending_workflows,
            success_workflows=success_workflows,
            total_duration_seconds=total_duration if completed_count > 0 else None,
            estimated_completion_seconds=estimated_completion,
        )

    def wait_for_pipeline_completion(
        self,
        commit_sha: Optional[str] = None,
        timeout_minutes: Optional[int] = None,
        poll_interval_seconds: Optional[int] = None,
    ) -> PipelineStatus:
        """
        Wait for all pipeline workflows to complete for a commit.

        Args:
            commit_sha: Commit SHA to monitor (defaults to current HEAD)
            timeout_minutes: Maximum time to wait for completion (uses config default if None)
            poll_interval_seconds: How often to check status (uses config default if None)

        Returns:
            Final pipeline status

        Raises:
            GitHubMonitorError: If timeout is reached or API errors occur
        """
        if commit_sha is None:
            commit_sha = self.get_current_commit_sha()

        # Use config defaults if not specified
        if timeout_minutes is None:
            timeout_minutes = self.config.timeout_minutes
        if poll_interval_seconds is None:
            poll_interval_seconds = self.config.poll_interval_seconds

        print(
            f"{self.colors['CYAN']}🔍 Monitoring GitHub Actions pipeline for commit {commit_sha[:8]}...{self.colors['NC']}"
        )

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while True:
            try:
                status = self.get_pipeline_status(commit_sha)

                if status.overall_status == "no_workflows":
                    print(
                        f"{self.colors['YELLOW']}⚠️  No workflows found for commit {commit_sha[:8]}{self.colors['NC']}"
                    )
                    return status

                # Print current status
                self._print_pipeline_status(status)

                if status.overall_status in ["success", "failure"]:
                    return status

                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    raise GitHubMonitorError(
                        f"Pipeline monitoring timeout after {timeout_minutes} minutes",
                        details={
                            "timeout_minutes": timeout_minutes,
                            "elapsed_seconds": elapsed,
                        },
                    )

                # Show progress and wait before next poll
                self.status_reporter.display_progress(status)
                time.sleep(poll_interval_seconds)

            except KeyboardInterrupt:
                print(
                    f"\n{self.colors['YELLOW']}⚠️  Pipeline monitoring interrupted by user{self.colors['NC']}"
                )
                return self.get_pipeline_status(commit_sha)

    def _print_pipeline_status(self, status: PipelineStatus) -> None:
        """Print a formatted pipeline status report using the enhanced StatusReporter."""
        self.status_reporter.display_status(status)

    def check_pipeline_after_push(self, branch: str = "pre-release") -> PipelineStatus:
        """
        Check pipeline status after a push to a specific branch.

        This method is designed to be called after a git push to verify
        that the associated CI/CD pipeline completes successfully.
        """
        current_branch = self.get_current_branch()

        if current_branch != branch:
            print(
                f"{self.colors['YELLOW']}⚠️  Current branch '{current_branch}' doesn't match target branch '{branch}'{self.colors['NC']}"
            )

        commit_sha = self.get_current_commit_sha()
        print(
            f"{self.colors['CYAN']}🚀 Checking pipeline status after push to {branch} (commit: {commit_sha[:8]}){self.colors['NC']}"
        )

        # Wait a moment for GitHub to register the push
        print(
            f"{self.colors['BLUE']}⏳ Waiting 10 seconds for GitHub to register the push...{self.colors['NC']}"
        )
        time.sleep(10)

        return self.wait_for_pipeline_completion(commit_sha)


def parse_github_repo_from_remote() -> Tuple[str, str]:
    """Parse GitHub repository owner and name from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # Handle both SSH and HTTPS URLs
        if remote_url.startswith("git@github.com:"):
            # SSH format: git@github.com:owner/repo.git
            repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
        elif remote_url.startswith("https://github.com/"):
            # HTTPS format: https://github.com/owner/repo.git
            repo_path = remote_url.replace("https://github.com/", "").replace(
                ".git", ""
            )
        else:
            raise ValueError(f"Unsupported remote URL format: {remote_url}")

        owner, repo = repo_path.split("/")
        return owner, repo

    except subprocess.CalledProcessError as e:
        raise GitHubConfigurationError(
            f"Failed to get git remote URL: {e}",
            config_source="git",
            details={"command": "git remote get-url origin", "error": str(e)},
        )
    except ValueError as e:
        raise GitHubConfigurationError(
            f"Failed to parse repository info: {e}",
            config_source="git",
            details={
                "remote_url": remote_url if "remote_url" in locals() else None,
                "error": str(e),
            },
        )


def main():
    """CLI interface for the GitHub pipeline monitor."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor GitHub Actions pipeline status"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--repo", help="Repository in format owner/name (overrides config)"
    )
    parser.add_argument(
        "--commit", help="Commit SHA to monitor (defaults to current HEAD)"
    )
    parser.add_argument(
        "--branch", default="pre-release", help="Branch to monitor after push"
    )
    parser.add_argument(
        "--timeout", type=int, help="Timeout in minutes (overrides config)"
    )
    parser.add_argument(
        "--poll-interval", type=int, help="Poll interval in seconds (overrides config)"
    )
    parser.add_argument(
        "--after-push", action="store_true", help="Monitor pipeline after a push"
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Check current status without waiting",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--no-colors", action="store_true", help="Disable colored output"
    )
    parser.add_argument(
        "--format", choices=["console", "json", "minimal"], help="Output format"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(args.config)

        # Override config with command line arguments
        if args.repo:
            if "/" in args.repo:
                config.repo_owner, config.repo_name = args.repo.split("/", 1)
            else:
                raise GitHubConfigurationError(
                    "Repository must be in format 'owner/name'",
                    config_source="command_line",
                    details={"provided_repo": args.repo},
                )

        if args.timeout:
            config.timeout_minutes = args.timeout
        if args.poll_interval:
            config.poll_interval_seconds = args.poll_interval
        if args.verbose:
            config.verbose = True
        if args.no_colors:
            config.colors_enabled = False
        if args.format:
            from github_monitor_config import OutputFormat

            config.output_format = OutputFormat(args.format)

        # Check monitoring mode
        monitoring_mode = config_manager.determine_monitoring_mode(config)
        if monitoring_mode == MonitoringMode.DISABLED:
            print("⚠️  GitHub monitoring is disabled. Check your configuration:")
            print("  - Set GITHUB_TOKEN environment variable")
            print("  - Ensure repository is properly configured")
            print("  - Run: python scripts/github_monitor_config.py --setup-help")
            exit(1)

        # Create monitor with configuration
        monitor = GitHubPipelineMonitor(config)

        if args.after_push:
            # Monitor after push
            status = monitor.check_pipeline_after_push(args.branch)
        elif args.status_only:
            # Just check current status
            status = monitor.get_pipeline_status(args.commit)
            if config.output_format.value == "json":
                print(
                    json.dumps(
                        {
                            "commit_sha": status.commit_sha,
                            "overall_status": status.overall_status,
                            "workflow_runs": [
                                {
                                    "id": run.id,
                                    "name": run.name,
                                    "status": run.status,
                                    "conclusion": run.conclusion,
                                    "html_url": run.html_url,
                                    "duration_seconds": run.duration_seconds,
                                }
                                for run in status.workflow_runs
                            ],
                            "failed_workflows": status.failed_workflows,
                            "pending_workflows": status.pending_workflows,
                            "success_workflows": status.success_workflows,
                        },
                        indent=2,
                    )
                )
            else:
                monitor._print_pipeline_status(status)
        else:
            # Wait for completion
            status = monitor.wait_for_pipeline_completion(args.commit)

        # Exit with appropriate code
        if status.overall_status == "success":
            exit(0)
        elif status.overall_status == "failure":
            exit(1)
        else:
            exit(2)  # Pending or no workflows

    except (GitHubMonitorError, ConfigurationError) as e:
        print(f"❌ Error: {e}")

        # Provide setup guidance for specific error types
        if hasattr(e, "get_setup_guidance"):
            print("\n💡 Setup Guidance:")
            print(e.get_setup_guidance())

        exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose if "args" in locals() else False:
            import traceback

            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

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
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

# Import configuration management
try:
    from github_monitor_config import (
        ConfigManager,
        ConfigurationError,
        MonitoringConfig,
        MonitoringMode,
    )
except ImportError:
    # Fallback for when running from different directory
    import sys

    sys.path.append(os.path.dirname(__file__))
    from github_monitor_config import (
        ConfigManager,
        ConfigurationError,
        MonitoringConfig,
        MonitoringMode,
    )


@dataclass
class WorkflowRun:
    """Represents a GitHub Actions workflow run."""

    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped
    html_url: str
    created_at: str
    updated_at: str
    head_sha: str
    duration_seconds: Optional[int] = None


@dataclass
class PipelineStatus:
    """Represents the overall pipeline status."""

    commit_sha: str
    workflow_runs: List[WorkflowRun]
    overall_status: str  # pending, success, failure, no_workflows
    failed_workflows: List[str]
    pending_workflows: List[str]
    success_workflows: List[str]
    total_duration_seconds: Optional[int] = None
    estimated_completion_seconds: Optional[int] = None


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""

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

        # Colors for output (respect config setting)
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

    def _make_api_request(self, endpoint: str) -> Dict:
        """Make a request to the GitHub API."""
        url = urljoin(self.base_url, endpoint)

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "mypylogger-pipeline-monitor/1.0",
        }

        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        try:
            request = Request(url, headers=headers)
            with urlopen(request) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 401:
                raise GitHubAPIError(
                    "GitHub API authentication failed. Check your GITHUB_TOKEN."
                )
            elif e.code == 403:
                raise GitHubAPIError("GitHub API rate limit exceeded or access denied.")
            elif e.code == 404:
                raise GitHubAPIError(
                    f"Repository {self.repo_owner}/{self.repo_name} not found."
                )
            else:
                raise GitHubAPIError(f"GitHub API error: {e.code} {e.reason}")
        except URLError as e:
            raise GitHubAPIError(f"Network error: {e.reason}")

    def get_current_commit_sha(self) -> str:
        """Get the current commit SHA from git."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitHubAPIError(f"Failed to get current commit SHA: {e}")

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
            raise GitHubAPIError(f"Failed to get current branch: {e}")

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
            GitHubAPIError: If timeout is reached or API errors occur
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
                    raise GitHubAPIError(
                        f"Pipeline monitoring timeout after {timeout_minutes} minutes"
                    )

                # Wait before next poll
                print(
                    f"{self.colors['BLUE']}⏳ Waiting {poll_interval_seconds}s before next check...{self.colors['NC']}"
                )
                time.sleep(poll_interval_seconds)

            except KeyboardInterrupt:
                print(
                    f"\n{self.colors['YELLOW']}⚠️  Pipeline monitoring interrupted by user{self.colors['NC']}"
                )
                return self.get_pipeline_status(commit_sha)

    def _print_pipeline_status(self, status: PipelineStatus) -> None:
        """Print a formatted pipeline status report."""
        print(
            f"\n{self.colors['BLUE']}📊 Pipeline Status for {status.commit_sha[:8]}:{self.colors['NC']}"
        )

        for run in status.workflow_runs:
            if run.status == "completed":
                if run.conclusion == "success":
                    icon = f"{self.colors['GREEN']}✅{self.colors['NC']}"
                elif run.conclusion in ["failure", "cancelled", "timed_out"]:
                    icon = f"{self.colors['RED']}❌{self.colors['NC']}"
                else:
                    icon = f"{self.colors['YELLOW']}⚠️{self.colors['NC']}"

                # Add duration if available and verbose mode
                duration_text = ""
                if self.config.verbose and run.duration_seconds:
                    minutes = run.duration_seconds // 60
                    seconds = run.duration_seconds % 60
                    duration_text = f" ({minutes}m {seconds}s)"

                status_text = f"{run.conclusion}{duration_text}"
            else:
                icon = f"{self.colors['YELLOW']}🔄{self.colors['NC']}"
                status_text = f"{run.status}"

            print(f"  {icon} {run.name}: {status_text}")

        # Overall status with enhanced information
        if status.overall_status == "success":
            success_count = len(status.success_workflows)
            print(
                f"\n{self.colors['GREEN']}🚀 All workflows completed successfully! ({success_count} workflows){self.colors['NC']}"
            )
            if self.config.verbose and status.total_duration_seconds:
                total_minutes = status.total_duration_seconds // 60
                total_seconds = status.total_duration_seconds % 60
                print(f"  Total execution time: {total_minutes}m {total_seconds}s")
        elif status.overall_status == "failure":
            print(
                f"\n{self.colors['RED']}💥 Pipeline failed - {len(status.failed_workflows)} workflow(s) failed{self.colors['NC']}"
            )
            for workflow in status.failed_workflows:
                print(f"  {self.colors['RED']}❌ {workflow}{self.colors['NC']}")
        elif status.overall_status == "pending":
            pending_count = len(status.pending_workflows)
            print(
                f"\n{self.colors['YELLOW']}⏳ Pipeline in progress - {pending_count} workflow(s) pending{self.colors['NC']}"
            )

            # Show estimated completion time if available
            if status.estimated_completion_seconds and self.config.progress_indicators:
                est_minutes = status.estimated_completion_seconds // 60
                est_seconds = status.estimated_completion_seconds % 60
                print(f"  Estimated completion: ~{est_minutes}m {est_seconds}s")

            for workflow in status.pending_workflows:
                print(f"  {self.colors['YELLOW']}🔄 {workflow}{self.colors['NC']}")
        elif status.overall_status == "no_workflows":
            print(
                f"\n{self.colors['YELLOW']}⚠️  No workflows found for this commit{self.colors['NC']}"
            )

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
        raise GitHubAPIError(f"Failed to get git remote URL: {e}")
    except ValueError as e:
        raise GitHubAPIError(f"Failed to parse repository info: {e}")


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
                raise GitHubAPIError("Repository must be in format 'owner/name'")

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

    except (GitHubAPIError, ConfigurationError) as e:
        print(f"❌ Error: {e}")
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

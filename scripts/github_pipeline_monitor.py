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
from typing import Any, Dict, List, Optional, Tuple

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
        GitHubConfigurationError,
        GitHubMonitorError,
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


# Legacy exception class for backward compatibility
class GitHubAPIError(GitHubMonitorError):
    """Legacy exception class - use specific GitHubMonitorError subclasses instead."""

    pass


class GitHubPipelineMonitor:
    """
    Monitor GitHub Actions pipeline status with intelligent polling and caching.

    This class focuses on monitoring logic and delegates API interactions
    to the dedicated GitHubAPIClient.
    """

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

        # Create API client for GitHub interactions
        from github_api_client import create_api_client

        self._api_client = create_api_client(self.config)

        # Status reporter will be created when needed to avoid circular imports
        self._status_reporter = None

        # Intelligent polling manager for optimized API usage
        self._polling_manager = None

        # Cache manager for response caching and rate limiting
        self._cache_manager = None

    @property
    def status_reporter(self):
        """Lazy-load status reporter to avoid circular imports."""
        if self._status_reporter is None:
            from github_status_reporter import create_status_reporter

            self._status_reporter = create_status_reporter(self.config)
        return self._status_reporter

    @property
    def polling_manager(self):
        """Lazy-load intelligent polling manager."""
        if self._polling_manager is None:
            from github_intelligent_polling import (
                PollingStrategy,
                create_intelligent_polling_manager,
            )

            # Create polling strategy from config
            strategy = PollingStrategy(
                queued_interval=max(60, self.config.poll_interval_seconds * 2),
                starting_interval=self.config.poll_interval_seconds,
                active_interval=max(10, self.config.poll_interval_seconds // 2),
                completing_interval=max(5, self.config.poll_interval_seconds // 3),
                max_interval=min(300, self.config.poll_interval_seconds * 10),
            )

            self._polling_manager = create_intelligent_polling_manager(strategy)
        return self._polling_manager

    @property
    def cache_manager(self):
        """Lazy-load cache manager."""
        if self._cache_manager is None:
            from github_cache_manager import CacheConfig, create_cache_manager

            # Create cache config based on monitoring config
            cache_config = CacheConfig(
                workflow_runs_ttl=max(15, self.config.poll_interval_seconds // 2),
                allow_stale_responses=True,  # Allow stale responses for better availability
                rate_limit_threshold=20,  # Conservative threshold
            )

            self._cache_manager = create_cache_manager(cache_config)

            # Inject cache manager into API client
            self._api_client.set_cache_manager(self._cache_manager)

        return self._cache_manager

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
        """
        Get all workflow runs for a specific commit.

        Args:
            commit_sha: Commit SHA to get workflow runs for

        Returns:
            List of workflow runs for the commit
        """
        # Ensure cache manager is initialized (which also injects it into API client)
        _ = self.cache_manager

        # Delegate to API client
        return self._api_client.get_workflow_runs_for_commit(commit_sha)

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

        # Calculate estimated completion using intelligent polling manager
        estimated_completion = None
        if pending_workflows:
            # Try to get intelligent estimates for each pending workflow
            estimates = []
            for run in workflow_runs:
                if run.status != "completed":
                    estimate = self.polling_manager.estimate_completion_time(run)
                    if estimate is not None:
                        estimates.append(estimate)

            if estimates:
                # Use the maximum estimate (longest running workflow)
                estimated_completion = max(estimates)
            elif completed_count > 0:
                # Fallback to simple average-based estimation
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
        Wait for all pipeline workflows to complete for a commit using intelligent polling.

        Args:
            commit_sha: Commit SHA to monitor (defaults to current HEAD)
            timeout_minutes: Maximum time to wait for completion (uses config default if None)
            poll_interval_seconds: Base poll interval (adaptive polling will adjust this)

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

        print(
            f"{self.colors['CYAN']}🔍 Monitoring GitHub Actions pipeline for commit {commit_sha[:8]} (intelligent polling)...{self.colors['NC']}"
        )

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_status_display = 0

        while True:
            try:
                status = self.get_pipeline_status(commit_sha)

                if status.overall_status == "no_workflows":
                    print(
                        f"{self.colors['YELLOW']}⚠️  No workflows found for commit {commit_sha[:8]}{self.colors['NC']}"
                    )
                    return status

                # Update polling manager with current workflow states
                for workflow_run in status.workflow_runs:
                    self.polling_manager.update_workflow_history(workflow_run)

                # Display status periodically (not on every poll)
                current_time = time.time()
                if (
                    current_time - last_status_display > 30
                ):  # Show status every 30 seconds
                    self._print_pipeline_status(status)
                    last_status_display = current_time

                if status.overall_status in ["success", "failure"]:
                    # Final status display
                    self._print_pipeline_status(status)
                    self.polling_manager.cleanup_completed_workflows()
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

                # Show progress
                self.status_reporter.display_progress(status)

                # Use intelligent polling to determine next poll interval
                workflows_to_poll = self.polling_manager.get_workflows_to_poll(
                    status.workflow_runs
                )

                if workflows_to_poll:
                    # Calculate adaptive poll interval based on active workflows
                    intervals = []
                    for workflow in workflows_to_poll:
                        interval = self.polling_manager.get_next_poll_interval(workflow)
                        intervals.append(interval)
                        self.polling_manager.record_poll_time(workflow.id)

                    # Use the minimum interval of active workflows
                    next_poll_interval = (
                        min(intervals)
                        if intervals
                        else poll_interval_seconds or self.config.poll_interval_seconds
                    )
                else:
                    # No workflows need immediate polling, use longer interval
                    next_poll_interval = 30

                # Display polling and cache statistics in verbose mode
                if self.config.verbose:
                    polling_stats = self.polling_manager.get_polling_statistics()
                    cache_stats = self.cache_manager.get_request_statistics()
                    print(
                        f"   Polling: {polling_stats['active_workflows']} active, next poll in {next_poll_interval}s"
                    )
                    print(
                        f"   Cache: {cache_stats['cache']['total_entries']} entries, {cache_stats['cache']['hit_ratio']:.1%} hit rate"
                    )
                    if cache_stats["rate_limit"]:
                        remaining = cache_stats["rate_limit"]["remaining"]
                        print(f"   Rate limit: {remaining} requests remaining")

                time.sleep(next_poll_interval)

            except KeyboardInterrupt:
                print(
                    f"\n{self.colors['YELLOW']}⚠️  Pipeline monitoring interrupted by user{self.colors['NC']}"
                )
                return self.get_pipeline_status(commit_sha)

    def _print_pipeline_status(self, status: PipelineStatus) -> None:
        """Print a formatted pipeline status report using the enhanced StatusReporter."""
        self.status_reporter.display_status(status)

    def invalidate_workflow_cache(self, commit_sha: Optional[str] = None) -> int:
        """
        Invalidate cached workflow data to force fresh API requests.

        Args:
            commit_sha: Specific commit to invalidate, or None for all workflows

        Returns:
            Number of cache entries invalidated
        """
        from github_cache_manager import CacheEntryType

        if commit_sha:
            # Invalidate specific commit's workflow runs
            pattern = f"actions/runs.*head_sha={commit_sha}"
            return self.cache_manager.invalidate_cache(endpoint_pattern=pattern)
        else:
            # Invalidate all workflow run caches
            return self.cache_manager.invalidate_cache(
                entry_type=CacheEntryType.WORKFLOW_RUNS
            )

    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about API caching and rate limiting.

        Returns:
            Dictionary with cache and rate limit statistics
        """
        return self.cache_manager.get_request_statistics()

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
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache and rate limit statistics",
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

        # Show cache statistics if requested
        if args.cache_stats:
            stats = monitor.get_cache_statistics()
            print("📊 Cache and Rate Limit Statistics:")
            print(f"  Cache entries: {stats['cache']['total_entries']}")
            print(f"  Cache hit ratio: {stats['cache']['hit_ratio']:.1%}")
            print(
                f"  Recent requests (10min): {stats['requests']['recent_requests_10min']}"
            )
            if stats["rate_limit"]:
                print(
                    f"  Rate limit remaining: {stats['rate_limit']['remaining']}/{stats['rate_limit']['limit']}"
                )
                print(
                    f"  Rate limit resets in: {stats['rate_limit']['time_until_reset_seconds']:.0f}s"
                )
            return

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
        else:
            # Fallback help for configuration errors
            print("\n💡 For help with setup and configuration:")
            print("   python scripts/github_help_system.py --setup-help")
            print("   python scripts/github_help_system.py --diagnose")

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

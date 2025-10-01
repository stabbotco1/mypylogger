#!/usr/bin/env python3
"""
GitHub API Client

This module provides a clean, focused API client for GitHub Actions
with comprehensive error handling, input validation, and caching support.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from github_data_models import WorkflowRun
from github_monitor_config import MonitoringConfig
from github_monitor_exceptions import (
    GitHubAuthenticationError,
    GitHubMonitorError,
    GitHubNetworkError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubRepositoryError,
    handle_github_api_error,
    retry_with_exponential_backoff,
)


class GitHubAPIClient:
    """
    Clean, focused GitHub API client for Actions monitoring.

    This class handles all direct GitHub API interactions with comprehensive
    error handling, input validation, and caching support.
    """

    def __init__(self, config: MonitoringConfig):
        """
        Initialize the GitHub API client.

        Args:
            config: Monitoring configuration with API credentials and settings
        """
        self.config = config
        self.base_url = "https://api.github.com"

        # Validate configuration
        self._validate_config()

        # Cache manager will be injected by the monitoring system
        self._cache_manager = None

    def set_cache_manager(self, cache_manager):
        """
        Set the cache manager for this API client.

        Args:
            cache_manager: Cache manager instance
        """
        self._cache_manager = cache_manager

    def _validate_config(self) -> None:
        """Validate the configuration for API client usage."""
        if not self.config.github_token:
            raise GitHubAuthenticationError(
                "GitHub token not provided", token_provided=False
            )

        if not self.config.repo_owner:
            raise GitHubMonitorError("Repository owner not specified")

        if not self.config.repo_name:
            raise GitHubMonitorError("Repository name not specified")

        # Validate repository name format
        if not self._is_valid_repo_name(self.config.repo_owner):
            raise GitHubMonitorError(
                f"Invalid repository owner format: {self.config.repo_owner}"
            )

        if not self._is_valid_repo_name(self.config.repo_name):
            raise GitHubMonitorError(
                f"Invalid repository name format: {self.config.repo_name}"
            )

    def _is_valid_repo_name(self, name: str) -> bool:
        """
        Validate repository name format.

        Args:
            name: Repository name to validate

        Returns:
            True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False

        # GitHub repository names can contain alphanumeric characters, hyphens, underscores, and periods
        # They cannot start or end with special characters
        pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$"
        return bool(re.match(pattern, name)) and len(name) <= 100

    def _validate_commit_sha(self, commit_sha: str) -> None:
        """
        Validate commit SHA format.

        Args:
            commit_sha: Commit SHA to validate

        Raises:
            GitHubMonitorError: If commit SHA is invalid
        """
        if not commit_sha or not isinstance(commit_sha, str):
            raise GitHubMonitorError("Commit SHA must be a non-empty string")

        # Git commit SHAs are 40-character hexadecimal strings (or shorter for abbreviated SHAs)
        if not re.match(r"^[a-fA-F0-9]{7,40}$", commit_sha):
            raise GitHubMonitorError(f"Invalid commit SHA format: {commit_sha}")

    def _validate_workflow_run_id(self, run_id: int) -> None:
        """
        Validate workflow run ID.

        Args:
            run_id: Workflow run ID to validate

        Raises:
            GitHubMonitorError: If run ID is invalid
        """
        if not isinstance(run_id, int) or run_id <= 0:
            raise GitHubMonitorError(f"Invalid workflow run ID: {run_id}")

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize API parameters to prevent injection attacks.

        Args:
            params: Parameters to sanitize

        Returns:
            Sanitized parameters
        """
        sanitized = {}

        for key, value in params.items():
            # Validate parameter keys
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                raise GitHubMonitorError(f"Invalid parameter key: {key}")

            # Sanitize parameter values
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized_value = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', "", value)
                sanitized[key] = sanitized_value
            elif isinstance(value, (int, bool)):
                sanitized[key] = value
            else:
                # Convert other types to string and sanitize
                sanitized[key] = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', "", str(value))

        return sanitized

    @retry_with_exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        retryable_exceptions=(GitHubNetworkError, GitHubRateLimitError),
    )
    def _make_api_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Make a request to the GitHub API with comprehensive error handling.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            Various GitHubMonitorError subclasses based on error type
        """
        # Validate and sanitize inputs
        if not endpoint or not isinstance(endpoint, str):
            raise GitHubMonitorError("API endpoint must be a non-empty string")

        if params:
            params = self._sanitize_params(params)

        # Check cache first if cache manager is available
        if self._cache_manager:
            cached_response = self._cache_manager.get_cached_response(endpoint, params)
            if cached_response is not None:
                return cached_response

        # Check rate limiting if cache manager is available
        if self._cache_manager and self._cache_manager.should_throttle_request():
            throttle_delay = self._cache_manager.get_throttle_delay()
            if throttle_delay > 0:
                time.sleep(throttle_delay)

        # Build URL with parameters
        url = urljoin(self.base_url, endpoint)
        if params:
            from urllib.parse import urlencode

            url += "?" + urlencode(params)

        # Prepare headers
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-action-monitoring/1.0",
            "Authorization": f"token {self.config.github_token}",
        }

        try:
            request = Request(url, headers=headers)
            with urlopen(request) as response:
                response_headers = dict(response.headers)

                # Update rate limit information if cache manager is available
                if self._cache_manager:
                    self._cache_manager.update_rate_limit_info(response_headers)
                    self._cache_manager.record_request(endpoint)

                # Parse response
                response_data = json.loads(response.read().decode())

                # Cache the response if cache manager is available
                if self._cache_manager:
                    self._cache_manager.cache_response(
                        endpoint, params, response_data, response_headers
                    )

                return response_data

        except HTTPError as e:
            # Read response body for detailed error information
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
                    token_provided=bool(self.config.github_token),
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
                        repo_owner=self.config.repo_owner,
                        repo_name=self.config.repo_name,
                        details={"status_code": e.code, "response": response_text},
                    )
            elif e.code == 404:
                raise GitHubRepositoryError(
                    f"Repository {self.config.repo_owner}/{self.config.repo_name} not found or not accessible",
                    repo_owner=self.config.repo_owner,
                    repo_name=self.config.repo_name,
                    details={"status_code": e.code, "response": response_text},
                )
            else:
                # Use the generic error handler for other HTTP errors
                raise handle_github_api_error(
                    e.code, response_text, self.config.repo_owner, self.config.repo_name
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

    def get_workflow_runs_for_commit(self, commit_sha: str) -> List[WorkflowRun]:
        """
        Get all workflow runs for a specific commit.

        Args:
            commit_sha: Commit SHA to get workflow runs for

        Returns:
            List of workflow runs for the commit

        Raises:
            GitHubMonitorError: If commit SHA is invalid or API request fails
        """
        # Validate input
        self._validate_commit_sha(commit_sha)

        endpoint = (
            f"/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/runs"
        )
        params = {"head_sha": commit_sha, "per_page": 100}

        data = self._make_api_request(endpoint, params)

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

    def get_workflow_run_details(self, run_id: int) -> WorkflowRun:
        """
        Get detailed information about a specific workflow run.

        Args:
            run_id: Workflow run ID

        Returns:
            Detailed workflow run information

        Raises:
            GitHubMonitorError: If run ID is invalid or API request fails
        """
        # Validate input
        self._validate_workflow_run_id(run_id)

        endpoint = f"/repos/{self.config.repo_owner}/{self.config.repo_name}/actions/runs/{run_id}"

        run_data = self._make_api_request(endpoint)

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

        return WorkflowRun(
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

    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get repository information.

        Returns:
            Repository information from GitHub API

        Raises:
            GitHubMonitorError: If API request fails
        """
        endpoint = f"/repos/{self.config.repo_owner}/{self.config.repo_name}"
        return self._make_api_request(endpoint)

    def check_api_rate_limit(self) -> Dict[str, int]:
        """
        Check current API rate limit status.

        Returns:
            Rate limit information

        Raises:
            GitHubMonitorError: If API request fails
        """
        endpoint = "/rate_limit"
        return self._make_api_request(endpoint)


def create_api_client(config: MonitoringConfig) -> GitHubAPIClient:
    """
    Factory function to create a GitHub API client.

    Args:
        config: Monitoring configuration

    Returns:
        Configured GitHubAPIClient instance
    """
    return GitHubAPIClient(config)

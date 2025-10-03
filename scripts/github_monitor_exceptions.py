#!/usr/bin/env python3
"""
GitHub Pipeline Monitor Exception Classes

This module defines specific exception classes for different types of errors
that can occur during GitHub Actions monitoring, enabling precise error handling
and recovery strategies.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar

T = TypeVar("T")


class GitHubMonitorError(Exception):
    """Base exception for all GitHub monitoring errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message

    def get_setup_guidance(self) -> str:
        """
        Get contextual setup guidance for this error.

        Returns:
            Formatted help text with specific guidance
        """
        try:
            from github_help_system import GitHubHelpSystem

            help_system = GitHubHelpSystem()
            return help_system.get_setup_guidance(self)
        except ImportError:
            return (
                "For setup help, run: python scripts/github_help_system.py --setup-help"
            )


class GitHubAuthenticationError(GitHubMonitorError):
    """Raised when GitHub API authentication fails."""

    def __init__(
        self,
        message: str = "GitHub API authentication failed",
        token_provided: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.token_provided = token_provided

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for resolving authentication issues."""
        if not self.token_provided:
            return """
GitHub token not provided. To fix this:

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: 'repo' (for private repos) or 'public_repo' (for public repos)
   - Copy the token

2. Set the GITHUB_TOKEN environment variable:
   export GITHUB_TOKEN=your_token_here

3. Or add it to your .github-monitor.yml config file:
   github:
     token: ${GITHUB_TOKEN}
"""
        else:
            return """
GitHub token authentication failed. To fix this:

1. Verify your token is valid:
   - Check if the token has expired
   - Ensure the token has the correct permissions

2. Required token scopes:
   - 'repo' scope for private repositories
   - 'public_repo' scope for public repositories
   - 'actions:read' scope for workflow access

3. Test your token:
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
"""


class GitHubPermissionError(GitHubMonitorError):
    """Raised when GitHub API access is denied due to insufficient permissions."""

    def __init__(
        self,
        message: str = "GitHub API access denied",
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for resolving permission issues."""
        repo_info = (
            f"{self.repo_owner}/{self.repo_name}"
            if self.repo_owner and self.repo_name
            else "the repository"
        )
        return f"""
Access denied to {repo_info}. To fix this:

1. Verify repository access:
   - Ensure you have read access to the repository
   - Check if the repository name is correct

2. Update token permissions:
   - For private repos: token needs 'repo' scope
   - For public repos: token needs 'public_repo' scope
   - For workflow access: token needs 'actions:read' scope

3. Organization settings:
   - Check if the organization has restricted token access
   - Ensure your token is authorized for the organization
"""


class GitHubRateLimitError(GitHubMonitorError):
    """Raised when GitHub API rate limits are exceeded."""

    def __init__(
        self,
        message: str = "GitHub API rate limit exceeded",
        reset_time: Optional[int] = None,
        remaining: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.reset_time = reset_time
        self.remaining = remaining

    def get_wait_time(self) -> int:
        """Get the recommended wait time in seconds before retrying."""
        if self.reset_time:
            current_time = int(time.time())
            wait_time = max(0, self.reset_time - current_time)
            return wait_time + 10  # Add 10 seconds buffer
        return 60  # Default 1 minute wait

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for handling rate limits."""
        wait_time = self.get_wait_time()
        return f"""
GitHub API rate limit exceeded. To handle this:

1. Wait for rate limit reset:
   - Wait approximately {wait_time} seconds before retrying
   - Rate limits reset every hour

2. Optimize API usage:
   - Increase polling intervals in configuration
   - Use authenticated requests (higher rate limits)
   - Consider caching workflow status

3. Check current rate limit status:
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
"""


class GitHubNetworkError(GitHubMonitorError):
    """Raised when network connectivity issues occur."""

    def __init__(
        self,
        message: str = "Network connectivity error",
        original_error: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.original_error = original_error

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for resolving network issues."""
        return """
Network connectivity error occurred. To resolve this:

1. Check internet connection:
   - Verify you can access github.com
   - Test with: ping github.com

2. Check proxy/firewall settings:
   - Ensure GitHub API (api.github.com) is accessible
   - Check corporate firewall rules

3. Retry the operation:
   - Network issues are often temporary
   - The system will automatically retry with exponential backoff
"""


class GitHubRepositoryError(GitHubMonitorError):
    """Raised when repository-related errors occur."""

    def __init__(
        self,
        message: str = "Repository error",
        repo_owner: Optional[str] = None,
        repo_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for resolving repository issues."""
        repo_info = (
            f"{self.repo_owner}/{self.repo_name}"
            if self.repo_owner and self.repo_name
            else "the repository"
        )
        return f"""
Repository error for {repo_info}. To resolve this:

1. Verify repository information:
   - Check repository owner and name are correct
   - Ensure repository exists and is accessible

2. Check repository settings:
   - Verify Actions are enabled for the repository
   - Check if repository is private/public as expected

3. Auto-detection issues:
   - Run: git remote get-url origin
   - Ensure git remote points to correct GitHub repository
"""


class GitHubConfigurationError(GitHubMonitorError):
    """Raised when configuration-related errors occur."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.config_source = config_source

    def get_setup_guidance(self) -> str:
        """Get actionable guidance for resolving configuration issues."""
        return """
Configuration error occurred. To resolve this:

1. Check configuration sources:
   - Environment variables (GITHUB_TOKEN, GITHUB_REPOSITORY, etc.)
   - Configuration file (.github-monitor.yml)
   - Command-line arguments

2. Validate configuration:
   python scripts/github_monitor_config.py --validate

3. Create sample configuration:
   python scripts/github_monitor_config.py --create-config

4. Get setup help:
   python scripts/github_monitor_config.py --setup-help
"""


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        GitHubNetworkError,
        GitHubRateLimitError,
    ),
) -> Callable[..., Callable[..., T]]:
    """
    Decorator that implements retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which delay increases each retry
        retryable_exceptions: Tuple of exception types that should trigger retries

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt failed, raise the last exception
                        raise e

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor**attempt), max_delay)

                    # Special handling for rate limit errors
                    if isinstance(e, GitHubRateLimitError):
                        delay = max(delay, e.get_wait_time())

                    error_msg = getattr(e, "message", str(e))
                    print(f"⚠️  Attempt {attempt + 1} failed: {error_msg}")
                    print(f"🔄 Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    raise e

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

            # Fallback return (should never be reached)
            raise RuntimeError("Unexpected state in retry logic")

        return wrapper

    return decorator


def handle_github_api_error(
    response_code: int,
    response_text: str,
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
) -> GitHubMonitorError:
    """
    Convert HTTP response codes to appropriate GitHub monitoring exceptions.

    Args:
        response_code: HTTP response status code
        response_text: Response body text
        repo_owner: Repository owner (optional)
        repo_name: Repository name (optional)

    Returns:
        Appropriate GitHubMonitorError subclass
    """
    details = {
        "status_code": response_code,
        "response": (
            response_text[:500] if response_text else None
        ),  # Limit response text
    }

    if response_code == 401:
        return GitHubAuthenticationError(
            "GitHub API authentication failed - invalid or missing token",
            token_provided=True,
            details=details,
        )
    elif response_code == 403:
        if "rate limit" in response_text.lower():
            # Try to extract rate limit info from headers (would need to be passed in)
            return GitHubRateLimitError(
                "GitHub API rate limit exceeded", details=details
            )
        else:
            return GitHubPermissionError(
                "GitHub API access denied - insufficient permissions",
                repo_owner=repo_owner,
                repo_name=repo_name,
                details=details,
            )
    elif response_code == 404:
        return GitHubRepositoryError(
            (
                f"Repository not found or not accessible: {repo_owner}/{repo_name}"
                if repo_owner and repo_name
                else "Repository not found"
            ),
            repo_owner=repo_owner,
            repo_name=repo_name,
            details=details,
        )
    elif response_code >= 500:
        return GitHubNetworkError(
            f"GitHub API server error (HTTP {response_code})", details=details
        )
    else:
        return GitHubMonitorError(
            f"GitHub API error (HTTP {response_code}): {response_text}", details=details
        )


def graceful_degradation_handler(
    func: Callable[..., T],
    fallback_value: T,
    error_message: str = "Operation failed, using fallback",
) -> Callable[..., T]:
    """
    Wrapper that provides graceful degradation by returning a fallback value on error.

    Args:
        func: Function to wrap
        fallback_value: Value to return if function fails
        error_message: Message to display when falling back

    Returns:
        Function result or fallback value
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except GitHubMonitorError as e:
            print(f"⚠️  {error_message}: {e.message}")
            if hasattr(e, "get_setup_guidance"):
                print("💡 Guidance:")
                print(e.get_setup_guidance())
            return fallback_value
        except Exception as e:
            print(f"⚠️  {error_message}: {str(e)}")
            return fallback_value

    return wrapper

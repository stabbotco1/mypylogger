"""Unit tests for publishing failure notifications."""

from __future__ import annotations

from pathlib import Path

# Import the modules we're testing
import sys
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from notify_publishing_failure import PublishingFailureNotifier


class TestPublishingFailureNotifier:
    """Test PublishingFailureNotifier class."""

    def test_notifier_initialization(self) -> None:
        """Test notifier initialization."""
        notifier = PublishingFailureNotifier()

        assert notifier.github_token is None
        assert notifier.repository == "unknown/unknown"

    def test_notifier_initialization_with_token(self) -> None:
        """Test notifier initialization with GitHub token."""
        notifier = PublishingFailureNotifier("test-token")

        assert notifier.github_token == "test-token"

    @patch.dict("os.environ", {"GITHUB_TOKEN": "env-token", "GITHUB_REPOSITORY": "user/repo"})
    def test_notifier_initialization_from_env(self) -> None:
        """Test notifier initialization from environment variables."""
        notifier = PublishingFailureNotifier()

        assert notifier.github_token == "env-token"
        assert notifier.repository == "user/repo"

    def test_format_error_for_github_success(self) -> None:
        """Test formatting error report for GitHub when no errors."""
        notifier = PublishingFailureNotifier()

        error_report = {"status": "success"}
        formatted = notifier.format_error_for_github(error_report)

        assert "No errors to report" in formatted
        assert "publishing succeeded" in formatted

    def test_format_error_for_github_with_errors(self) -> None:
        """Test formatting error report for GitHub with errors."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 2,
            "most_severe": "critical",
            "summary": "Authentication failed",
            "errors": [
                {
                    "category": "authentication",
                    "severity": "critical",
                    "message": "Invalid API token",
                    "details": "401 Unauthorized",
                    "command": "twine upload",
                    "stderr": "Authentication failed",
                    "is_retryable": False,
                    "retry_count": 0,
                },
                {
                    "category": "network",
                    "severity": "medium",
                    "message": "Connection timeout",
                    "details": "Network unreachable",
                    "command": "twine upload",
                    "stderr": "Timeout after 30 seconds",
                    "is_retryable": True,
                    "retry_count": 2,
                },
            ],
        }

        formatted = notifier.format_error_for_github(error_report)

        # Check that key information is included
        assert "PyPI Publishing Failure Report" in formatted
        assert "Total Errors: 2" in formatted
        assert "Most Severe: CRITICAL" in formatted
        assert "Authentication failed" in formatted
        assert "AUTHENTICATION Errors" in formatted
        assert "NETWORK Errors" in formatted
        assert "Invalid API token" in formatted
        assert "Connection timeout" in formatted
        assert "Troubleshooting Steps" in formatted
        assert "twine upload" in formatted

    def test_format_error_for_github_truncates_long_stderr(self) -> None:
        """Test that long stderr output is truncated in GitHub formatting."""
        notifier = PublishingFailureNotifier()

        long_stderr = "A" * 600  # Longer than 500 character limit

        error_report = {
            "status": "error",
            "total_errors": 1,
            "most_severe": "high",
            "summary": "Build failed",
            "errors": [
                {
                    "category": "build",
                    "severity": "high",
                    "message": "Build error",
                    "stderr": long_stderr,
                    "is_retryable": False,
                    "retry_count": 0,
                },
            ],
        }

        formatted = notifier.format_error_for_github(error_report)

        # Check that stderr is truncated
        assert "A" * 500 in formatted
        assert "..." in formatted
        assert len(long_stderr) > 500  # Verify our test data is actually long

    @patch("requests.post")
    def test_create_github_issue_success(self, mock_post: Mock) -> None:
        """Test successful GitHub issue creation."""
        notifier = PublishingFailureNotifier("test-token")

        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "html_url": "https://github.com/user/repo/issues/123",
            "number": 123,
        }
        mock_post.return_value = mock_response

        result = notifier.create_github_issue(
            "Test Issue",
            "Test body content",
            ["bug", "test"],
        )

        assert result is True
        mock_post.assert_called_once()

        # Verify API call parameters
        call_args = mock_post.call_args
        assert "repos/unknown/unknown/issues" in call_args[1]["url"]
        assert call_args[1]["headers"]["Authorization"] == "token test-token"
        assert call_args[1]["json"]["title"] == "Test Issue"
        assert call_args[1]["json"]["body"] == "Test body content"
        assert call_args[1]["json"]["labels"] == ["bug", "test"]

    def test_create_github_issue_no_token(self) -> None:
        """Test GitHub issue creation without token."""
        notifier = PublishingFailureNotifier()

        result = notifier.create_github_issue("Test Issue", "Test body")

        assert result is False

    @patch("requests.post")
    def test_create_github_issue_api_error(self, mock_post: Mock) -> None:
        """Test GitHub issue creation with API error."""
        notifier = PublishingFailureNotifier("test-token")

        # Mock API error
        mock_post.side_effect = Exception("API Error")

        result = notifier.create_github_issue("Test Issue", "Test body")

        assert result is False

    @patch("requests.post")
    def test_create_github_issue_http_error(self, mock_post: Mock) -> None:
        """Test GitHub issue creation with HTTP error."""
        notifier = PublishingFailureNotifier("test-token")

        # Mock HTTP error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_post.return_value = mock_response

        result = notifier.create_github_issue("Test Issue", "Test body")

        assert result is False

    def test_create_github_issue_no_requests_library(self) -> None:
        """Test GitHub issue creation when requests library is not available."""
        notifier = PublishingFailureNotifier("test-token")

        with patch("builtins.__import__", side_effect=ImportError("No module named 'requests'")):
            result = notifier.create_github_issue("Test Issue", "Test body")

            assert result is False

    def test_send_console_notification_success(self, capsys: any) -> None:
        """Test console notification for successful publishing."""
        notifier = PublishingFailureNotifier()

        error_report = {"status": "success"}
        notifier.send_console_notification(error_report)

        captured = capsys.readouterr()
        assert "Publishing succeeded" in captured.out
        assert "no notification needed" in captured.out

    def test_send_console_notification_with_errors(self, capsys: any) -> None:
        """Test console notification with errors."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 2,
            "most_severe": "critical",
            "summary": "Authentication failed",
            "errors": [
                {
                    "category": "authentication",
                    "severity": "critical",
                    "message": "Invalid API token",
                },
                {
                    "category": "network",
                    "severity": "medium",
                    "message": "Connection timeout",
                },
            ],
        }

        notifier.send_console_notification(error_report)

        captured = capsys.readouterr()
        assert "PYPI PUBLISHING FAILURE NOTIFICATION" in captured.out
        assert "Total Errors: 2" in captured.out
        assert "Most Severe: CRITICAL" in captured.out
        assert "Authentication failed" in captured.out
        assert "Invalid API token" in captured.out
        assert "Connection timeout" in captured.out

    def test_send_console_notification_sorts_by_severity(self, capsys: any) -> None:
        """Test that console notification sorts errors by severity."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 3,
            "most_severe": "critical",
            "summary": "Multiple errors",
            "errors": [
                {
                    "category": "network",
                    "severity": "low",
                    "message": "Minor network issue",
                },
                {
                    "category": "authentication",
                    "severity": "critical",
                    "message": "Auth failure",
                },
                {
                    "category": "build",
                    "severity": "high",
                    "message": "Build error",
                },
            ],
        }

        notifier.send_console_notification(error_report)

        captured = capsys.readouterr()
        output_lines = captured.out.split("\n")

        # Find the error lines
        error_lines = [line for line in output_lines if line.strip().startswith(("1.", "2.", "3."))]

        # Critical should be first, then high, then low
        assert "CRITICAL" in error_lines[0]
        assert "HIGH" in error_lines[1]
        assert "LOW" in error_lines[2]

    def test_notify_failure_success_no_issue(self, capsys: any) -> None:
        """Test notify_failure for successful publishing without issue creation."""
        notifier = PublishingFailureNotifier()

        error_report = {"status": "success"}
        result = notifier.notify_failure(error_report, create_issue=False)

        assert result is True
        captured = capsys.readouterr()
        assert "Publishing succeeded" in captured.out

    def test_notify_failure_with_errors_no_issue(self, capsys: any) -> None:
        """Test notify_failure with errors but no issue creation."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 1,
            "most_severe": "high",
            "summary": "Build failed",
            "errors": [
                {
                    "category": "build",
                    "severity": "high",
                    "message": "Build error",
                },
            ],
        }

        result = notifier.notify_failure(error_report, create_issue=False)

        assert result is True
        captured = capsys.readouterr()
        assert "PYPI PUBLISHING FAILURE NOTIFICATION" in captured.out

    @patch.object(PublishingFailureNotifier, "create_github_issue")
    def test_notify_failure_with_issue_creation(self, mock_create_issue: Mock) -> None:
        """Test notify_failure with GitHub issue creation."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 1,
            "most_severe": "critical",
            "summary": "Auth failed",
            "errors": [
                {
                    "category": "authentication",
                    "severity": "critical",
                    "message": "Invalid token",
                },
            ],
        }

        mock_create_issue.return_value = True

        result = notifier.notify_failure(error_report, create_issue=True)

        assert result is True
        mock_create_issue.assert_called_once()

        # Check that issue title includes severity and timestamp
        call_args = mock_create_issue.call_args[0]
        issue_title = call_args[0]
        assert "CRITICAL" in issue_title
        assert "PyPI Publishing Failure" in issue_title

    @patch.object(PublishingFailureNotifier, "create_github_issue")
    def test_notify_failure_with_custom_issue_title(self, mock_create_issue: Mock) -> None:
        """Test notify_failure with custom issue title."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 1,
            "most_severe": "high",
            "summary": "Build failed",
            "errors": [],
        }

        mock_create_issue.return_value = True

        result = notifier.notify_failure(
            error_report,
            create_issue=True,
            issue_title="Custom Issue Title",
        )

        assert result is True
        mock_create_issue.assert_called_once()

        # Check that custom title was used
        call_args = mock_create_issue.call_args[0]
        issue_title = call_args[0]
        assert issue_title == "Custom Issue Title"

    @patch.object(PublishingFailureNotifier, "create_github_issue")
    def test_notify_failure_issue_creation_fails(
        self, mock_create_issue: Mock
    ) -> None:
        """Test notify_failure when GitHub issue creation fails."""
        notifier = PublishingFailureNotifier()

        error_report = {
            "status": "error",
            "total_errors": 1,
            "most_severe": "high",
            "summary": "Build failed",
            "errors": [],
        }

        mock_create_issue.return_value = False

        result = notifier.notify_failure(error_report, create_issue=True)

        assert result is False
        mock_create_issue.assert_called_once()

    def test_notify_failure_success_with_issue_request(self, capsys: any) -> None:
        """Test notify_failure for success case with issue creation requested."""
        notifier = PublishingFailureNotifier()

        error_report = {"status": "success"}
        result = notifier.notify_failure(error_report, create_issue=True)

        # Should succeed and not create issue for successful publishing
        assert result is True
        captured = capsys.readouterr()
        assert "Publishing succeeded" in captured.out

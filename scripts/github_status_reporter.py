#!/usr/bin/env python3
"""
GitHub Pipeline Status Reporter

This module provides comprehensive status reporting and user feedback for
GitHub Actions monitoring, with support for multiple output formats,
real-time progress indicators, and enhanced user experience.
"""

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, TextIO

# Import configuration and data models
try:
    from github_data_models import PipelineStatus, WorkflowRun
    from github_monitor_config import MonitoringConfig, OutputFormat
except ImportError:
    # Fallback for when running from different directory
    import os

    sys.path.append(os.path.dirname(__file__))
    from github_data_models import PipelineStatus, WorkflowRun
    from github_monitor_config import MonitoringConfig, OutputFormat


class VerbosityLevel(Enum):
    """Verbosity levels for status reporting."""

    QUIET = "quiet"  # Minimal output, errors only
    NORMAL = "normal"  # Standard output with key information
    VERBOSE = "verbose"  # Detailed output with all information
    DEBUG = "debug"  # Maximum detail for troubleshooting


@dataclass
class StatusDisplayConfig:
    """Configuration for status display formatting."""

    output_format: OutputFormat = OutputFormat.CONSOLE
    verbosity: VerbosityLevel = VerbosityLevel.NORMAL
    colors_enabled: bool = True
    progress_indicators: bool = True
    show_timestamps: bool = False
    show_duration: bool = True
    show_links: bool = True
    compact_mode: bool = False


class StatusReporter:
    """
    Comprehensive status reporter for GitHub Actions monitoring.

    Provides multiple output formats, real-time progress indicators,
    and enhanced user feedback with color coding and detailed information.
    """

    def __init__(self, config: MonitoringConfig, output_stream: TextIO = sys.stdout):
        """
        Initialize the status reporter.

        Args:
            config: Monitoring configuration
            output_stream: Output stream for status messages
        """
        self.config = config
        self.output_stream = output_stream

        # Create display configuration from monitoring config
        self.display_config = StatusDisplayConfig(
            output_format=config.output_format,
            verbosity=(
                VerbosityLevel.VERBOSE if config.verbose else VerbosityLevel.NORMAL
            ),
            colors_enabled=config.colors_enabled,
            progress_indicators=config.progress_indicators,
            show_timestamps=config.verbose,
            show_duration=True,
            show_links=True,
            compact_mode=False,
        )

        # Color codes for terminal output
        if self.display_config.colors_enabled:
            self.colors = {
                "GREEN": "\033[0;32m",
                "RED": "\033[0;31m",
                "YELLOW": "\033[1;33m",
                "BLUE": "\033[0;34m",
                "PURPLE": "\033[0;35m",
                "CYAN": "\033[0;36m",
                "WHITE": "\033[1;37m",
                "GRAY": "\033[0;37m",
                "BOLD": "\033[1m",
                "DIM": "\033[2m",
                "NC": "\033[0m",  # No Color
            }
        else:
            # No colors - all empty strings
            self.colors = {
                key: ""
                for key in [
                    "GREEN",
                    "RED",
                    "YELLOW",
                    "BLUE",
                    "PURPLE",
                    "CYAN",
                    "WHITE",
                    "GRAY",
                    "BOLD",
                    "DIM",
                    "NC",
                ]
            }

        # Status icons
        self.icons = {
            "success": "✅",
            "failure": "❌",
            "pending": "🔄",
            "queued": "⏳",
            "cancelled": "⚠️",
            "skipped": "⏭️",
            "warning": "⚠️",
            "info": "ℹ️",
            "rocket": "🚀",
            "clock": "⏰",
            "link": "🔗",
            "branch": "🌿",
            "commit": "📝",
        }

    def display_status(self, status: PipelineStatus) -> None:
        """
        Display comprehensive pipeline status information.

        Args:
            status: Pipeline status to display
        """
        if self.display_config.output_format == OutputFormat.JSON:
            self._display_json_status(status)
        elif self.display_config.output_format == OutputFormat.MINIMAL:
            self._display_minimal_status(status)
        else:
            self._display_console_status(status)

    def display_progress(self, status: PipelineStatus) -> None:
        """
        Display real-time progress indicators for ongoing workflows.

        Args:
            status: Current pipeline status
        """
        if not self.display_config.progress_indicators:
            return

        if self.display_config.output_format == OutputFormat.JSON:
            # For JSON format, output progress as structured data
            progress_data = self._create_progress_data(status)
            self._write_json(progress_data)
        else:
            self._display_console_progress(status)

    def display_completion(self, status: PipelineStatus) -> None:
        """
        Display final completion status with summary information.

        Args:
            status: Final pipeline status
        """
        if self.display_config.output_format == OutputFormat.JSON:
            completion_data = self._create_completion_data(status)
            self._write_json(completion_data)
        elif self.display_config.output_format == OutputFormat.MINIMAL:
            self._display_minimal_completion(status)
        else:
            self._display_console_completion(status)

    def display_error(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Display error information with appropriate formatting.

        Args:
            error: Exception that occurred
            context: Optional context information
        """
        if self.display_config.output_format == OutputFormat.JSON:
            error_data = {
                "type": "error",
                "error_type": type(error).__name__,
                "message": str(error),
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._write_json(error_data)
        else:
            error_icon = self.icons["failure"]
            error_color = self.colors["RED"]
            reset_color = self.colors["NC"]

            self._write_line(
                f"{error_color}{error_icon} Error: {str(error)}{reset_color}"
            )

            if context and self.display_config.verbosity != VerbosityLevel.QUIET:
                self._write_line(f"   Context: {context}")

    def display_warning(self, message: str, context: Optional[str] = None) -> None:
        """
        Display warning message with appropriate formatting.

        Args:
            message: Warning message
            context: Optional context information
        """
        if self.display_config.verbosity == VerbosityLevel.QUIET:
            return

        if self.display_config.output_format == OutputFormat.JSON:
            warning_data = {
                "type": "warning",
                "message": message,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._write_json(warning_data)
        else:
            warning_icon = self.icons["warning"]
            warning_color = self.colors["YELLOW"]
            reset_color = self.colors["NC"]

            self._write_line(
                f"{warning_color}{warning_icon} Warning: {message}{reset_color}"
            )

            if context and self.display_config.verbosity == VerbosityLevel.VERBOSE:
                self._write_line(f"   Context: {context}")

    def display_info(self, message: str, context: Optional[str] = None) -> None:
        """
        Display informational message.

        Args:
            message: Information message
            context: Optional context information
        """
        if self.display_config.verbosity == VerbosityLevel.QUIET:
            return

        if self.display_config.output_format == OutputFormat.JSON:
            info_data = {
                "type": "info",
                "message": message,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self._write_json(info_data)
        else:
            info_icon = self.icons["info"]
            info_color = self.colors["BLUE"]
            reset_color = self.colors["NC"]

            self._write_line(f"{info_color}{info_icon} {message}{reset_color}")

            if context and self.display_config.verbosity == VerbosityLevel.VERBOSE:
                self._write_line(f"   Context: {context}")

    def _display_console_status(self, status: PipelineStatus) -> None:
        """Display status in console format with colors and formatting."""
        # Header with commit information
        commit_icon = self.icons["commit"]
        header_color = self.colors["CYAN"]
        bold_color = self.colors["BOLD"]
        reset_color = self.colors["NC"]

        self._write_line(f"\n{header_color}{bold_color}📊 Pipeline Status{reset_color}")
        self._write_line(f"{commit_icon} Commit: {status.commit_sha[:8]}")

        if self.display_config.show_timestamps:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            self._write_line(f"⏰ Checked: {timestamp}")

        # Overall status
        overall_icon, overall_color = self._get_status_icon_color(status.overall_status)
        self._write_line(
            f"\n{overall_color}{overall_icon} Overall Status: {status.overall_status.upper()}{reset_color}"
        )

        # Workflow details
        if status.workflow_runs:
            self._write_line(f"\n{bold_color}Workflows:{reset_color}")

            for run in status.workflow_runs:
                self._display_workflow_run(run)
        else:
            self._write_line(
                f"\n{self.colors['YELLOW']}No workflows found for this commit{reset_color}"
            )

        # Summary information
        if (
            status.workflow_runs
            and self.display_config.verbosity != VerbosityLevel.QUIET
        ):
            self._display_status_summary(status)

    def _display_workflow_run(self, run: WorkflowRun) -> None:
        """Display individual workflow run information."""
        # Get status icon and color
        if run.status == "completed":
            if run.conclusion == "success":
                icon, color = self.icons["success"], self.colors["GREEN"]
            elif run.conclusion in ["failure", "cancelled", "timed_out"]:
                icon, color = self.icons["failure"], self.colors["RED"]
            elif run.conclusion == "skipped":
                icon, color = self.icons["skipped"], self.colors["GRAY"]
            else:
                icon, color = self.icons["warning"], self.colors["YELLOW"]
        else:
            if run.status == "queued":
                icon, color = self.icons["queued"], self.colors["YELLOW"]
            else:  # in_progress
                icon, color = self.icons["pending"], self.colors["BLUE"]

        # Format workflow name and status
        status_text = run.conclusion if run.status == "completed" else run.status
        workflow_line = f"  {icon} {color}{run.name}{self.colors['NC']}: {status_text}"

        # Add duration if available and enabled
        if self.display_config.show_duration and run.duration_seconds:
            duration = self._format_duration(run.duration_seconds)
            workflow_line += f" ({duration})"

        self._write_line(workflow_line)

        # Add workflow URL if enabled and verbose
        if (
            self.display_config.show_links
            and self.display_config.verbosity == VerbosityLevel.VERBOSE
        ):
            link_color = self.colors["DIM"]
            self._write_line(
                f"    {self.icons['link']} {link_color}{run.html_url}{self.colors['NC']}"
            )

    def _display_status_summary(self, status: PipelineStatus) -> None:
        """Display summary information about the pipeline status."""
        summary_lines = []

        # Count workflows by status
        total_workflows = len(status.workflow_runs)
        success_count = len(status.success_workflows)
        failed_count = len(status.failed_workflows)
        pending_count = len(status.pending_workflows)

        summary_lines.append(f"Total workflows: {total_workflows}")

        if success_count > 0:
            summary_lines.append(
                f"{self.colors['GREEN']}✓ {success_count} successful{self.colors['NC']}"
            )

        if failed_count > 0:
            summary_lines.append(
                f"{self.colors['RED']}✗ {failed_count} failed{self.colors['NC']}"
            )

        if pending_count > 0:
            summary_lines.append(
                f"{self.colors['YELLOW']}⧖ {pending_count} pending{self.colors['NC']}"
            )

        # Total duration
        if status.total_duration_seconds and self.display_config.show_duration:
            total_duration = self._format_duration(status.total_duration_seconds)
            summary_lines.append(f"Total time: {total_duration}")

        # Estimated completion
        if status.estimated_completion_seconds and pending_count > 0:
            est_duration = self._format_duration(status.estimated_completion_seconds)
            summary_lines.append(f"Est. completion: ~{est_duration}")

        if summary_lines:
            self._write_line(f"\n{self.colors['BOLD']}Summary:{self.colors['NC']}")
            for line in summary_lines:
                self._write_line(f"  {line}")

    def _display_console_progress(self, status: PipelineStatus) -> None:
        """Display real-time progress indicators."""
        if not status.pending_workflows:
            return

        progress_color = self.colors["BLUE"]
        reset_color = self.colors["NC"]

        # Show spinning indicator for pending workflows
        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_idx = int(time.time() * 2) % len(spinner_chars)
        spinner = spinner_chars[spinner_idx]

        pending_count = len(status.pending_workflows)
        self._write_line(
            f"{progress_color}{spinner} Monitoring {pending_count} workflow(s)...{reset_color}"
        )

        # Show estimated completion if available
        if status.estimated_completion_seconds:
            est_duration = self._format_duration(status.estimated_completion_seconds)
            self._write_line(f"   Estimated completion: ~{est_duration}")

    def _display_console_completion(self, status: PipelineStatus) -> None:
        """Display final completion status with celebration or failure indication."""
        if status.overall_status == "success":
            success_color = self.colors["GREEN"]
            rocket_icon = self.icons["rocket"]
            self._write_line(
                f"\n{success_color}{rocket_icon} All workflows completed successfully!{self.colors['NC']}"
            )

            if status.total_duration_seconds and self.display_config.show_duration:
                total_duration = self._format_duration(status.total_duration_seconds)
                self._write_line(f"   Total execution time: {total_duration}")

        elif status.overall_status == "failure":
            failure_color = self.colors["RED"]
            failure_icon = self.icons["failure"]
            failed_count = len(status.failed_workflows)

            self._write_line(
                f"\n{failure_color}{failure_icon} Pipeline failed - {failed_count} workflow(s) failed{self.colors['NC']}"
            )

            # List failed workflows
            for workflow_name in status.failed_workflows:
                self._write_line(
                    f"   {failure_color}✗ {workflow_name}{self.colors['NC']}"
                )

        elif status.overall_status == "no_workflows":
            warning_color = self.colors["YELLOW"]
            warning_icon = self.icons["warning"]
            self._write_line(
                f"\n{warning_color}{warning_icon} No workflows found for this commit{self.colors['NC']}"
            )

    def _display_json_status(self, status: PipelineStatus) -> None:
        """Display status in JSON format."""
        status_data = {
            "type": "status",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit_sha": status.commit_sha,
            "overall_status": status.overall_status,
            "workflow_runs": [
                {
                    "id": run.id,
                    "name": run.name,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "html_url": run.html_url,
                    "created_at": run.created_at,
                    "updated_at": run.updated_at,
                    "duration_seconds": run.duration_seconds,
                }
                for run in status.workflow_runs
            ],
            "summary": {
                "total_workflows": len(status.workflow_runs),
                "successful_workflows": len(status.success_workflows),
                "failed_workflows": len(status.failed_workflows),
                "pending_workflows": len(status.pending_workflows),
                "total_duration_seconds": status.total_duration_seconds,
                "estimated_completion_seconds": status.estimated_completion_seconds,
            },
        }

        self._write_json(status_data)

    def _display_minimal_status(self, status: PipelineStatus) -> None:
        """Display status in minimal format."""
        status_char = self._get_minimal_status_char(status.overall_status)
        self._write_line(f"{status_char} {status.overall_status}")

        if status.failed_workflows:
            for workflow in status.failed_workflows:
                self._write_line(f"  ✗ {workflow}")

    def _display_minimal_completion(self, status: PipelineStatus) -> None:
        """Display completion in minimal format."""
        if status.overall_status == "success":
            self._write_line("✓ SUCCESS")
        elif status.overall_status == "failure":
            self._write_line(f"✗ FAILED ({len(status.failed_workflows)} workflows)")
        else:
            self._write_line(f"? {status.overall_status.upper()}")

    def _create_progress_data(self, status: PipelineStatus) -> Dict[str, Any]:
        """Create structured progress data for JSON output."""
        return {
            "type": "progress",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit_sha": status.commit_sha,
            "pending_workflows": status.pending_workflows,
            "estimated_completion_seconds": status.estimated_completion_seconds,
            "progress_percentage": self._calculate_progress_percentage(status),
        }

    def _create_completion_data(self, status: PipelineStatus) -> Dict[str, Any]:
        """Create structured completion data for JSON output."""
        return {
            "type": "completion",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit_sha": status.commit_sha,
            "overall_status": status.overall_status,
            "summary": {
                "total_workflows": len(status.workflow_runs),
                "successful_workflows": len(status.success_workflows),
                "failed_workflows": len(status.failed_workflows),
                "total_duration_seconds": status.total_duration_seconds,
            },
            "failed_workflows": status.failed_workflows,
        }

    def _get_status_icon_color(self, status: str) -> tuple:
        """Get appropriate icon and color for a status."""
        status_mapping = {
            "success": (self.icons["success"], self.colors["GREEN"]),
            "failure": (self.icons["failure"], self.colors["RED"]),
            "pending": (self.icons["pending"], self.colors["YELLOW"]),
            "no_workflows": (self.icons["warning"], self.colors["YELLOW"]),
        }
        return status_mapping.get(status, (self.icons["info"], self.colors["BLUE"]))

    def _get_minimal_status_char(self, status: str) -> str:
        """Get single character representation for minimal output."""
        status_chars = {
            "success": "✓",
            "failure": "✗",
            "pending": "⧖",
            "no_workflows": "?",
        }
        return status_chars.get(status, "?")

    def _format_duration(self, seconds: int) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m"

    def _calculate_progress_percentage(self, status: PipelineStatus) -> Optional[float]:
        """Calculate progress percentage based on completed workflows."""
        if not status.workflow_runs:
            return None

        completed_count = len(
            [run for run in status.workflow_runs if run.status == "completed"]
        )
        total_count = len(status.workflow_runs)

        return (completed_count / total_count) * 100.0

    def _write_line(self, text: str) -> None:
        """Write a line to the output stream."""
        print(text, file=self.output_stream)
        self.output_stream.flush()

    def _write_json(self, data: Dict[str, Any]) -> None:
        """Write JSON data to the output stream."""
        json_str = json.dumps(
            data,
            indent=(
                2 if self.display_config.verbosity == VerbosityLevel.VERBOSE else None
            ),
        )
        self._write_line(json_str)


def create_status_reporter(
    config: MonitoringConfig, output_stream: TextIO = sys.stdout
) -> StatusReporter:
    """
    Factory function to create a status reporter with the given configuration.

    Args:
        config: Monitoring configuration
        output_stream: Output stream for status messages

    Returns:
        Configured StatusReporter instance
    """
    return StatusReporter(config, output_stream)

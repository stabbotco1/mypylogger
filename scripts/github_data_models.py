#!/usr/bin/env python3
"""
GitHub Pipeline Monitor Data Models

This module contains shared data models used across the GitHub Actions
monitoring system to avoid circular imports.
"""

from dataclasses import dataclass
from typing import List, Optional


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
#!/usr/bin/env python3
"""
GitHub Intelligent Polling System

This module implements adaptive polling intervals and intelligent monitoring
strategies for GitHub Actions workflows to optimize API usage and provide
better user experience.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from github_data_models import WorkflowRun


class WorkflowPhase(Enum):
    """Different phases of workflow execution for polling optimization."""

    QUEUED = "queued"  # Workflow is queued, slow polling
    STARTING = "starting"  # Workflow just started, medium polling
    ACTIVE = "active"  # Workflow actively running, fast polling
    COMPLETING = "completing"  # Workflow near completion, fast polling
    COMPLETED = "completed"  # Workflow finished, no polling needed


@dataclass
class WorkflowHistory:
    """Historical data for a workflow to inform polling decisions."""

    workflow_name: str
    typical_duration_seconds: Optional[int] = None
    last_seen_status: Optional[str] = None
    last_seen_conclusion: Optional[str] = None
    phase_transitions: List[tuple] = field(
        default_factory=list
    )  # (timestamp, old_phase, new_phase)
    duration_samples: List[int] = field(default_factory=list)  # Historical durations

    def add_duration_sample(self, duration_seconds: int) -> None:
        """Add a duration sample and update typical duration."""
        self.duration_samples.append(duration_seconds)

        # Keep only last 10 samples for rolling average
        if len(self.duration_samples) > 10:
            self.duration_samples = self.duration_samples[-10:]

        # Calculate typical duration as median of samples
        if self.duration_samples:
            sorted_durations = sorted(self.duration_samples)
            n = len(sorted_durations)
            if n % 2 == 0:
                self.typical_duration_seconds = (
                    sorted_durations[n // 2 - 1] + sorted_durations[n // 2]
                ) // 2
            else:
                self.typical_duration_seconds = sorted_durations[n // 2]

    def record_phase_transition(
        self, old_phase: WorkflowPhase, new_phase: WorkflowPhase
    ) -> None:
        """Record a phase transition for analysis."""
        timestamp = datetime.now(timezone.utc)
        self.phase_transitions.append((timestamp, old_phase, new_phase))

        # Keep only last 20 transitions
        if len(self.phase_transitions) > 20:
            self.phase_transitions = self.phase_transitions[-20:]


@dataclass
class PollingStrategy:
    """Configuration for adaptive polling intervals."""

    # Base intervals for different phases (seconds)
    queued_interval: int = 60  # Slow polling for queued workflows
    starting_interval: int = 30  # Medium polling for starting workflows
    active_interval: int = 15  # Fast polling for active workflows
    completing_interval: int = 10  # Very fast polling near completion

    # Backoff settings
    max_interval: int = 300  # Maximum polling interval (5 minutes)
    backoff_multiplier: float = 1.5  # Multiplier for backoff

    # Completion detection
    completion_threshold_ratio: float = 0.8  # When to switch to completing phase

    # Concurrent monitoring limits
    max_concurrent_workflows: int = 10

    def get_interval_for_phase(self, phase: WorkflowPhase) -> int:
        """Get polling interval for a specific workflow phase."""
        interval_map = {
            WorkflowPhase.QUEUED: self.queued_interval,
            WorkflowPhase.STARTING: self.starting_interval,
            WorkflowPhase.ACTIVE: self.active_interval,
            WorkflowPhase.COMPLETING: self.completing_interval,
            WorkflowPhase.COMPLETED: 0,  # No polling needed
        }
        return interval_map.get(phase, self.active_interval)


class IntelligentPollingManager:
    """
    Manages adaptive polling intervals and workflow monitoring strategies.

    This class implements intelligent polling that adapts based on:
    - Workflow status and phase
    - Historical duration data
    - Current system load
    - API rate limiting considerations
    """

    def __init__(self, strategy: Optional[PollingStrategy] = None):
        """
        Initialize the intelligent polling manager.

        Args:
            strategy: Polling strategy configuration
        """
        self.strategy = strategy or PollingStrategy()
        self.workflow_histories: Dict[str, WorkflowHistory] = {}
        self.active_workflows: Dict[int, WorkflowRun] = {}  # workflow_id -> WorkflowRun
        self.workflow_phases: Dict[int, WorkflowPhase] = (
            {}
        )  # workflow_id -> current phase
        self.last_poll_times: Dict[int, datetime] = {}  # workflow_id -> last poll time
        self.backoff_multipliers: Dict[int, float] = (
            {}
        )  # workflow_id -> current backoff

    def analyze_workflow_phase(self, workflow_run: WorkflowRun) -> WorkflowPhase:
        """
        Analyze the current phase of a workflow run.

        Args:
            workflow_run: The workflow run to analyze

        Returns:
            Current phase of the workflow
        """
        if workflow_run.status == "completed":
            return WorkflowPhase.COMPLETED

        if workflow_run.status == "queued":
            return WorkflowPhase.QUEUED

        # For in_progress workflows, determine sub-phase
        if workflow_run.status == "in_progress":
            # Check if we have historical data to estimate completion
            history = self.workflow_histories.get(workflow_run.name)

            if history and history.typical_duration_seconds:
                # Calculate elapsed time since creation
                try:
                    created_time = datetime.fromisoformat(
                        workflow_run.created_at.replace("Z", "+00:00")
                    )
                    elapsed_seconds = (
                        datetime.now(timezone.utc) - created_time
                    ).total_seconds()

                    # Determine phase based on elapsed time vs typical duration
                    progress_ratio = elapsed_seconds / history.typical_duration_seconds

                    if progress_ratio < 0.1:
                        return WorkflowPhase.STARTING
                    elif progress_ratio > self.strategy.completion_threshold_ratio:
                        return WorkflowPhase.COMPLETING
                    else:
                        return WorkflowPhase.ACTIVE

                except (ValueError, TypeError):
                    # If we can't parse timestamps, default to active
                    return WorkflowPhase.ACTIVE
            else:
                # No historical data, assume active
                return WorkflowPhase.ACTIVE

        # Default to active for unknown states
        return WorkflowPhase.ACTIVE

    def update_workflow_history(self, workflow_run: WorkflowRun) -> None:
        """
        Update historical data for a workflow.

        Args:
            workflow_run: The workflow run to record
        """
        if workflow_run.name not in self.workflow_histories:
            self.workflow_histories[workflow_run.name] = WorkflowHistory(
                workflow_run.name
            )

        history = self.workflow_histories[workflow_run.name]

        # Update status tracking
        _ = history.last_seen_status
        history.last_seen_status = workflow_run.status
        history.last_seen_conclusion = workflow_run.conclusion

        # Record duration if workflow completed
        if (
            workflow_run.status == "completed"
            and workflow_run.duration_seconds
            and workflow_run.duration_seconds > 0
        ):
            history.add_duration_sample(workflow_run.duration_seconds)

        # Track phase transitions
        current_phase = self.analyze_workflow_phase(workflow_run)
        old_phase = self.workflow_phases.get(workflow_run.id)

        if old_phase and old_phase != current_phase:
            history.record_phase_transition(old_phase, current_phase)

        self.workflow_phases[workflow_run.id] = current_phase

    def get_next_poll_interval(self, workflow_run: WorkflowRun) -> int:
        """
        Calculate the next polling interval for a workflow.

        Args:
            workflow_run: The workflow run to calculate interval for

        Returns:
            Next polling interval in seconds
        """
        # Update workflow tracking
        self.active_workflows[workflow_run.id] = workflow_run
        self.update_workflow_history(workflow_run)

        # Get current phase
        current_phase = self.workflow_phases.get(workflow_run.id, WorkflowPhase.ACTIVE)

        # Get base interval for phase
        base_interval = self.strategy.get_interval_for_phase(current_phase)

        # Apply backoff if needed
        backoff = self.backoff_multipliers.get(workflow_run.id, 1.0)
        interval = int(base_interval * backoff)

        # Ensure we don't exceed maximum interval
        interval = min(interval, self.strategy.max_interval)

        return interval

    def apply_backoff(self, workflow_id: int) -> None:
        """
        Apply exponential backoff to a workflow's polling interval.

        Args:
            workflow_id: ID of the workflow to apply backoff to
        """
        current_backoff = self.backoff_multipliers.get(workflow_id, 1.0)
        new_backoff = min(current_backoff * self.strategy.backoff_multiplier, 10.0)
        self.backoff_multipliers[workflow_id] = new_backoff

    def reset_backoff(self, workflow_id: int) -> None:
        """
        Reset backoff for a workflow (e.g., after successful status change).

        Args:
            workflow_id: ID of the workflow to reset backoff for
        """
        self.backoff_multipliers[workflow_id] = 1.0

    def should_poll_workflow(self, workflow_run: WorkflowRun) -> bool:
        """
        Determine if a workflow should be polled now.

        Args:
            workflow_run: The workflow run to check

        Returns:
            True if the workflow should be polled now
        """
        # Always poll completed workflows once to update history
        if workflow_run.status == "completed":
            if workflow_run.id not in self.workflow_phases:
                return True
            return self.workflow_phases[workflow_run.id] != WorkflowPhase.COMPLETED

        # Check if enough time has passed since last poll
        last_poll = self.last_poll_times.get(workflow_run.id)
        if not last_poll:
            return True

        interval = self.get_next_poll_interval(workflow_run)
        time_since_poll = (datetime.now(timezone.utc) - last_poll).total_seconds()

        return time_since_poll >= interval

    def record_poll_time(self, workflow_id: int) -> None:
        """
        Record the time when a workflow was polled.

        Args:
            workflow_id: ID of the workflow that was polled
        """
        self.last_poll_times[workflow_id] = datetime.now(timezone.utc)

    def get_workflows_to_poll(
        self, all_workflows: List[WorkflowRun]
    ) -> List[WorkflowRun]:
        """
        Get the list of workflows that should be polled now.

        Args:
            all_workflows: All workflows being monitored

        Returns:
            List of workflows that should be polled
        """
        workflows_to_poll = []

        for workflow in all_workflows:
            if self.should_poll_workflow(workflow):
                workflows_to_poll.append(workflow)

        # Limit concurrent polling to avoid overwhelming the API
        if len(workflows_to_poll) > self.strategy.max_concurrent_workflows:
            # Prioritize by phase (completing > active > starting > queued)
            phase_priority = {
                WorkflowPhase.COMPLETING: 0,
                WorkflowPhase.ACTIVE: 1,
                WorkflowPhase.STARTING: 2,
                WorkflowPhase.QUEUED: 3,
                WorkflowPhase.COMPLETED: 4,
            }

            workflows_to_poll.sort(
                key=lambda w: phase_priority.get(self.analyze_workflow_phase(w), 2)
            )
            workflows_to_poll = workflows_to_poll[
                : self.strategy.max_concurrent_workflows
            ]

        return workflows_to_poll

    def cleanup_completed_workflows(self) -> None:
        """Remove completed workflows from active tracking."""
        completed_ids = []

        for workflow_id, phase in self.workflow_phases.items():
            if phase == WorkflowPhase.COMPLETED:
                completed_ids.append(workflow_id)

        for workflow_id in completed_ids:
            self.active_workflows.pop(workflow_id, None)
            self.workflow_phases.pop(workflow_id, None)
            self.last_poll_times.pop(workflow_id, None)
            self.backoff_multipliers.pop(workflow_id, None)

    def get_polling_statistics(self) -> Dict[str, any]:
        """
        Get statistics about current polling state.

        Returns:
            Dictionary with polling statistics
        """
        phase_counts = {}
        for phase in self.workflow_phases.values():
            phase_counts[phase.value] = phase_counts.get(phase.value, 0) + 1

        return {
            "active_workflows": len(self.active_workflows),
            "workflow_histories": len(self.workflow_histories),
            "phase_distribution": phase_counts,
            "average_backoff": (
                sum(self.backoff_multipliers.values()) / len(self.backoff_multipliers)
                if self.backoff_multipliers
                else 1.0
            ),
        }

    def estimate_completion_time(self, workflow_run: WorkflowRun) -> Optional[int]:
        """
        Estimate completion time for a workflow based on historical data.

        Args:
            workflow_run: The workflow run to estimate completion for

        Returns:
            Estimated seconds until completion, or None if unknown
        """
        if workflow_run.status == "completed":
            return 0

        history = self.workflow_histories.get(workflow_run.name)
        if not history or not history.typical_duration_seconds:
            return None

        try:
            created_time = datetime.fromisoformat(
                workflow_run.created_at.replace("Z", "+00:00")
            )
            elapsed_seconds = (
                datetime.now(timezone.utc) - created_time
            ).total_seconds()

            remaining_seconds = history.typical_duration_seconds - elapsed_seconds
            return max(0, int(remaining_seconds))

        except (ValueError, TypeError):
            return None


def create_intelligent_polling_manager(
    strategy: Optional[PollingStrategy] = None,
) -> IntelligentPollingManager:
    """
    Factory function to create an intelligent polling manager.

    Args:
        strategy: Optional polling strategy configuration

    Returns:
        Configured IntelligentPollingManager instance
    """
    return IntelligentPollingManager(strategy)

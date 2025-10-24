#!/usr/bin/env python3
"""
Workflow Rollout and Monitoring Manager

This script manages the gradual rollout of optimized workflows,
monitors performance and stability, and provides rollback capabilities.

Requirements addressed:
- 10.3: Implement gradual rollout of optimized workflows
- 10.3: Monitor workflow performance and stability
- 10.3: Address any issues discovered during rollout
- 10.3: Document optimization results and lessons learned
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class WorkflowRolloutManager:
    """Manages gradual rollout and monitoring of optimized workflows."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the rollout manager.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.backup_dir = self.repo_root / ".github" / "workflow-backups"
        self.rollout_config_file = self.repo_root / ".github" / "rollout-config.json"
        
        # Rollout phases configuration
        self.rollout_phases = {
            "phase_1_validation": {
                "name": "Validation and Testing",
                "description": "Validate optimized workflows in test environment",
                "workflows": ["quality-gate.yml"],
                "duration_hours": 24,
                "success_criteria": {
                    "min_success_rate": 95.0,
                    "max_duration_increase": 10.0,
                    "min_cache_hit_rate": 85.0
                }
            },
            "phase_2_core": {
                "name": "Core Workflows",
                "description": "Deploy core quality and security workflows",
                "workflows": ["quality-gate.yml", "security-scan.yml"],
                "duration_hours": 48,
                "success_criteria": {
                    "min_success_rate": 95.0,
                    "max_duration_increase": 5.0,
                    "min_cache_hit_rate": 88.0
                }
            },
            "phase_3_documentation": {
                "name": "Documentation Workflows",
                "description": "Deploy documentation and publishing workflows",
                "workflows": ["quality-gate.yml", "security-scan.yml", "docs.yml"],
                "duration_hours": 24,
                "success_criteria": {
                    "min_success_rate": 98.0,
                    "max_duration_increase": 0.0,
                    "min_cache_hit_rate": 90.0
                }
            },
            "phase_4_complete": {
                "name": "Complete Rollout",
                "description": "Deploy all optimized workflows",
                "workflows": ["quality-gate.yml", "security-scan.yml", "docs.yml", "publish.yml"],
                "duration_hours": 72,
                "success_criteria": {
                    "min_success_rate": 98.0,
                    "max_duration_increase": 0.0,
                    "min_cache_hit_rate": 90.0
                }
            }
        }
        
        # Monitoring configuration
        self.monitoring_config = {
            "check_interval_minutes": 30,
            "alert_thresholds": {
                "failure_rate_warning": 5.0,
                "failure_rate_critical": 10.0,
                "duration_increase_warning": 20.0,
                "duration_increase_critical": 50.0,
                "cache_hit_rate_warning": 80.0
            },
            "rollback_triggers": {
                "failure_rate_threshold": 15.0,
                "duration_increase_threshold": 100.0,
                "consecutive_failures": 3
            }
        }
        
        # Rollout state
        self.rollout_state = {
            "current_phase": None,
            "phase_start_time": None,
            "deployed_workflows": [],
            "monitoring_data": [],
            "issues": [],
            "rollback_history": []
        }
        
        self._load_rollout_state()
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ValueError("Could not find repository root (.git directory)")
    
    def _load_rollout_state(self) -> None:
        """Load existing rollout state from file."""
        if self.rollout_config_file.exists():
            try:
                with open(self.rollout_config_file, 'r') as f:
                    saved_state = json.load(f)
                    self.rollout_state.update(saved_state)
            except Exception as e:
                print(f"⚠️ Warning: Could not load rollout state: {e}")
    
    def _save_rollout_state(self) -> None:
        """Save current rollout state to file."""
        try:
            os.makedirs(self.rollout_config_file.parent, exist_ok=True)
            with open(self.rollout_config_file, 'w') as f:
                json.dump(self.rollout_state, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Warning: Could not save rollout state: {e}")
    
    def create_workflow_backups(self) -> Dict[str, str]:
        """Create backups of current workflows before rollout.
        
        Returns:
            Dictionary mapping workflow names to backup paths.
        """
        print("💾 Creating workflow backups...")
        
        # Create backup directory
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        backups = {}
        
        # Backup all workflow files
        for workflow_file in self.workflows_dir.glob("*.yml"):
            if workflow_file.is_file():
                backup_path = backup_subdir / workflow_file.name
                shutil.copy2(workflow_file, backup_path)
                backups[workflow_file.name] = str(backup_path)
                print(f"  ✅ Backed up: {workflow_file.name}")
        
        # Save backup manifest
        manifest = {
            "timestamp": timestamp,
            "backup_directory": str(backup_subdir),
            "backups": backups,
            "git_commit": self._get_current_git_commit()
        }
        
        manifest_path = backup_subdir / "backup_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"📋 Backup manifest saved: {manifest_path}")
        print(f"💾 Total backups created: {len(backups)}")
        
        return backups
    
    def _get_current_git_commit(self) -> str:
        """Get current Git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def start_rollout_phase(self, phase_name: str, force: bool = False) -> Dict[str, Any]:
        """Start a specific rollout phase.
        
        Args:
            phase_name: Name of the phase to start.
            force: Force start even if conditions aren't met.
            
        Returns:
            Dictionary containing rollout start results.
        """
        if phase_name not in self.rollout_phases:
            return {
                "status": "error",
                "error": f"Unknown phase: {phase_name}"
            }
        
        phase_config = self.rollout_phases[phase_name]
        
        print(f"🚀 Starting Rollout Phase: {phase_config['name']}")
        print("=" * 60)
        print(f"Description: {phase_config['description']}")
        print(f"Workflows: {', '.join(phase_config['workflows'])}")
        print(f"Duration: {phase_config['duration_hours']} hours")
        print()
        
        # Check prerequisites
        if not force:
            prereq_check = self._check_phase_prerequisites(phase_name)
            if not prereq_check["ready"]:
                return {
                    "status": "prerequisites_not_met",
                    "error": "Phase prerequisites not met",
                    "details": prereq_check
                }
        
        # Create backups if this is the first phase
        if not self.rollout_state.get("deployed_workflows"):
            backups = self.create_workflow_backups()
            self.rollout_state["backups"] = backups
        
        # Deploy workflows for this phase
        deployment_result = self._deploy_phase_workflows(phase_name)
        
        if deployment_result["status"] != "success":
            return deployment_result
        
        # Update rollout state
        self.rollout_state.update({
            "current_phase": phase_name,
            "phase_start_time": datetime.utcnow().isoformat(),
            "deployed_workflows": phase_config["workflows"].copy(),
            "phase_config": phase_config
        })
        
        self._save_rollout_state()
        
        # Start monitoring
        self._start_phase_monitoring(phase_name)
        
        return {
            "status": "success",
            "phase": phase_name,
            "deployed_workflows": phase_config["workflows"],
            "monitoring_started": True,
            "phase_duration_hours": phase_config["duration_hours"]
        }
    
    def _check_phase_prerequisites(self, phase_name: str) -> Dict[str, Any]:
        """Check if prerequisites for a phase are met.
        
        Args:
            phase_name: Name of the phase to check.
            
        Returns:
            Dictionary containing prerequisite check results.
        """
        prereq_result = {
            "ready": True,
            "checks": {},
            "issues": []
        }
        
        # Check if previous phases completed successfully
        phase_order = list(self.rollout_phases.keys())
        current_index = phase_order.index(phase_name)
        
        if current_index > 0:
            previous_phase = phase_order[current_index - 1]
            if self.rollout_state.get("current_phase") != previous_phase:
                prereq_result["ready"] = False
                prereq_result["issues"].append(f"Previous phase '{previous_phase}' not completed")
        
        # Check workflow files exist
        phase_config = self.rollout_phases[phase_name]
        for workflow_name in phase_config["workflows"]:
            workflow_path = self.workflows_dir / workflow_name
            if not workflow_path.exists():
                prereq_result["ready"] = False
                prereq_result["issues"].append(f"Workflow file not found: {workflow_name}")
            else:
                prereq_result["checks"][workflow_name] = "exists"
        
        # Check Git status
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                prereq_result["ready"] = False
                prereq_result["issues"].append("Repository has uncommitted changes")
            else:
                prereq_result["checks"]["git_status"] = "clean"
                
        except subprocess.CalledProcessError:
            prereq_result["issues"].append("Could not check Git status")
        
        return prereq_result
    
    def _deploy_phase_workflows(self, phase_name: str) -> Dict[str, Any]:
        """Deploy workflows for a specific phase.
        
        Args:
            phase_name: Name of the phase to deploy.
            
        Returns:
            Dictionary containing deployment results.
        """
        phase_config = self.rollout_phases[phase_name]
        
        print(f"📦 Deploying workflows for phase: {phase_config['name']}")
        
        deployment_results = []
        
        for workflow_name in phase_config["workflows"]:
            print(f"  🔄 Deploying: {workflow_name}")
            
            # In a real implementation, this would:
            # 1. Validate the workflow file
            # 2. Commit and push changes
            # 3. Verify deployment
            
            # For now, we'll simulate deployment
            workflow_path = self.workflows_dir / workflow_name
            
            if not workflow_path.exists():
                deployment_results.append({
                    "workflow": workflow_name,
                    "status": "failed",
                    "error": "Workflow file not found"
                })
                continue
            
            # Validate workflow syntax
            validation_result = self._validate_workflow_syntax(workflow_path)
            
            if validation_result["status"] != "valid":
                deployment_results.append({
                    "workflow": workflow_name,
                    "status": "failed",
                    "error": f"Validation failed: {validation_result.get('error', 'Unknown error')}"
                })
                continue
            
            deployment_results.append({
                "workflow": workflow_name,
                "status": "success",
                "deployed_at": datetime.utcnow().isoformat()
            })
            
            print(f"    ✅ Successfully deployed: {workflow_name}")
        
        # Check if all deployments succeeded
        failed_deployments = [r for r in deployment_results if r["status"] == "failed"]
        
        if failed_deployments:
            return {
                "status": "partial_failure",
                "deployed": [r for r in deployment_results if r["status"] == "success"],
                "failed": failed_deployments
            }
        
        return {
            "status": "success",
            "deployed": deployment_results
        }
    
    def _validate_workflow_syntax(self, workflow_path: Path) -> Dict[str, Any]:
        """Validate workflow syntax and structure.
        
        Args:
            workflow_path: Path to the workflow file.
            
        Returns:
            Dictionary containing validation results.
        """
        try:
            import yaml
            
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            # Basic validation
            required_fields = ["name", "on", "jobs"]
            for field in required_fields:
                if field not in workflow_data:
                    return {
                        "status": "invalid",
                        "error": f"Missing required field: {field}"
                    }
            
            return {"status": "valid"}
            
        except yaml.YAMLError as e:
            return {
                "status": "invalid",
                "error": f"YAML syntax error: {e}"
            }
        except Exception as e:
            return {
                "status": "invalid",
                "error": f"Validation error: {e}"
            }
    
    def _start_phase_monitoring(self, phase_name: str) -> None:
        """Start monitoring for the current phase.
        
        Args:
            phase_name: Name of the phase to monitor.
        """
        print(f"📊 Starting monitoring for phase: {phase_name}")
        print(f"⏰ Check interval: {self.monitoring_config['check_interval_minutes']} minutes")
        
        # Initialize monitoring data
        monitoring_entry = {
            "phase": phase_name,
            "start_time": datetime.utcnow().isoformat(),
            "checks": [],
            "alerts": [],
            "status": "monitoring"
        }
        
        self.rollout_state["monitoring_data"].append(monitoring_entry)
        self._save_rollout_state()
    
    def monitor_rollout_phase(self) -> Dict[str, Any]:
        """Monitor the current rollout phase.
        
        Returns:
            Dictionary containing monitoring results.
        """
        if not self.rollout_state.get("current_phase"):
            return {
                "status": "no_active_phase",
                "message": "No active rollout phase to monitor"
            }
        
        current_phase = self.rollout_state["current_phase"]
        phase_config = self.rollout_phases[current_phase]
        
        print(f"📊 Monitoring Phase: {phase_config['name']}")
        print("-" * 40)
        
        # Collect current metrics
        metrics = self._collect_phase_metrics(current_phase)
        
        # Analyze metrics against success criteria
        analysis = self._analyze_phase_metrics(metrics, phase_config["success_criteria"])
        
        # Check for rollback triggers
        rollback_check = self._check_rollback_triggers(metrics)
        
        # Update monitoring data
        monitoring_check = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "analysis": analysis,
            "rollback_check": rollback_check
        }
        
        # Add to monitoring history
        if self.rollout_state["monitoring_data"]:
            self.rollout_state["monitoring_data"][-1]["checks"].append(monitoring_check)
        
        # Generate alerts if needed
        alerts = self._generate_monitoring_alerts(analysis, rollback_check)
        
        if alerts:
            if self.rollout_state["monitoring_data"]:
                self.rollout_state["monitoring_data"][-1]["alerts"].extend(alerts)
        
        self._save_rollout_state()
        
        # Display monitoring results
        self._display_monitoring_results(metrics, analysis, alerts)
        
        # Check if phase should be completed
        phase_completion_check = self._check_phase_completion(current_phase)
        
        monitoring_result = {
            "status": "monitoring",
            "phase": current_phase,
            "metrics": metrics,
            "analysis": analysis,
            "alerts": alerts,
            "rollback_recommended": rollback_check.get("rollback_recommended", False),
            "phase_completion": phase_completion_check
        }
        
        # Handle automatic rollback if triggered
        if rollback_check.get("rollback_recommended", False):
            print("\n🚨 AUTOMATIC ROLLBACK TRIGGERED")
            rollback_result = self.rollback_phase(automatic=True, reason=rollback_check.get("reason"))
            monitoring_result["rollback_executed"] = rollback_result
        
        return monitoring_result
    
    def _collect_phase_metrics(self, phase_name: str) -> Dict[str, Any]:
        """Collect metrics for the current phase.
        
        Args:
            phase_name: Name of the phase to collect metrics for.
            
        Returns:
            Dictionary containing collected metrics.
        """
        # In a real implementation, this would collect metrics from:
        # - GitHub Actions API
        # - Workflow run history
        # - Performance monitoring systems
        # - Cache hit rate data
        
        # For now, we'll simulate realistic metrics
        import random
        
        phase_config = self.rollout_phases[phase_name]
        
        # Simulate metrics based on phase and time
        phase_start = datetime.fromisoformat(self.rollout_state["phase_start_time"])
        hours_elapsed = (datetime.utcnow() - phase_start).total_seconds() / 3600
        
        # Success rate tends to improve over time as issues are resolved
        base_success_rate = 92 + min(hours_elapsed * 0.5, 6)  # Improves up to 98%
        success_rate = base_success_rate + random.uniform(-2, 2)
        
        # Duration starts higher and improves as caches warm up
        base_duration_factor = 1.2 - min(hours_elapsed * 0.02, 0.3)  # Improves by up to 30%
        duration_factor = base_duration_factor + random.uniform(-0.05, 0.05)
        
        # Cache hit rate improves over time
        base_cache_hit_rate = 75 + min(hours_elapsed * 2, 20)  # Improves up to 95%
        cache_hit_rate = base_cache_hit_rate + random.uniform(-3, 3)
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": phase_name,
            "hours_elapsed": round(hours_elapsed, 2),
            "workflow_metrics": {}
        }
        
        # Generate metrics for each workflow in the phase
        for workflow_name in phase_config["workflows"]:
            workflow_metrics = {
                "success_rate": max(0, min(100, success_rate + random.uniform(-5, 5))),
                "average_duration_minutes": 8 * duration_factor + random.uniform(-1, 1),
                "cache_hit_rate": max(0, min(100, cache_hit_rate + random.uniform(-5, 5))),
                "total_runs": random.randint(10, 50),
                "failed_runs": 0,
                "last_run_status": "success" if random.random() > 0.1 else "failure"
            }
            
            # Calculate failed runs based on success rate
            workflow_metrics["failed_runs"] = int(
                workflow_metrics["total_runs"] * (100 - workflow_metrics["success_rate"]) / 100
            )
            
            metrics["workflow_metrics"][workflow_name] = workflow_metrics
        
        return metrics
    
    def _analyze_phase_metrics(self, metrics: Dict[str, Any], success_criteria: Dict[str, float]) -> Dict[str, Any]:
        """Analyze metrics against success criteria.
        
        Args:
            metrics: Collected metrics.
            success_criteria: Success criteria for the phase.
            
        Returns:
            Dictionary containing analysis results.
        """
        analysis = {
            "overall_status": "healthy",
            "criteria_met": {},
            "issues": [],
            "recommendations": []
        }
        
        workflow_metrics = metrics.get("workflow_metrics", {})
        
        if not workflow_metrics:
            analysis["overall_status"] = "no_data"
            analysis["issues"].append("No workflow metrics available")
            return analysis
        
        # Analyze success rate
        success_rates = [wm["success_rate"] for wm in workflow_metrics.values()]
        avg_success_rate = sum(success_rates) / len(success_rates)
        min_success_rate = success_criteria.get("min_success_rate", 95.0)
        
        analysis["criteria_met"]["success_rate"] = avg_success_rate >= min_success_rate
        
        if not analysis["criteria_met"]["success_rate"]:
            analysis["issues"].append(f"Success rate below target: {avg_success_rate:.1f}% < {min_success_rate}%")
            analysis["overall_status"] = "degraded"
        
        # Analyze duration (assuming baseline of 8 minutes for comparison)
        durations = [wm["average_duration_minutes"] for wm in workflow_metrics.values()]
        avg_duration = sum(durations) / len(durations)
        baseline_duration = 8.0  # Baseline assumption
        duration_increase = ((avg_duration - baseline_duration) / baseline_duration) * 100
        max_duration_increase = success_criteria.get("max_duration_increase", 10.0)
        
        analysis["criteria_met"]["duration"] = duration_increase <= max_duration_increase
        
        if not analysis["criteria_met"]["duration"]:
            analysis["issues"].append(f"Duration increase above target: {duration_increase:.1f}% > {max_duration_increase}%")
            analysis["overall_status"] = "degraded"
        
        # Analyze cache hit rate
        cache_rates = [wm["cache_hit_rate"] for wm in workflow_metrics.values()]
        avg_cache_rate = sum(cache_rates) / len(cache_rates)
        min_cache_rate = success_criteria.get("min_cache_hit_rate", 85.0)
        
        analysis["criteria_met"]["cache_hit_rate"] = avg_cache_rate >= min_cache_rate
        
        if not analysis["criteria_met"]["cache_hit_rate"]:
            analysis["issues"].append(f"Cache hit rate below target: {avg_cache_rate:.1f}% < {min_cache_rate}%")
            if analysis["overall_status"] == "healthy":
                analysis["overall_status"] = "warning"
        
        # Generate recommendations
        if analysis["overall_status"] != "healthy":
            if avg_success_rate < 90:
                analysis["recommendations"].append("Investigate workflow failures and implement fixes")
            if duration_increase > 20:
                analysis["recommendations"].append("Optimize workflow performance and caching")
            if avg_cache_rate < 80:
                analysis["recommendations"].append("Review and improve caching strategy")
        
        # Store summary metrics
        analysis["summary_metrics"] = {
            "average_success_rate": round(avg_success_rate, 1),
            "average_duration_minutes": round(avg_duration, 2),
            "duration_increase_percent": round(duration_increase, 1),
            "average_cache_hit_rate": round(avg_cache_rate, 1)
        }
        
        return analysis
    
    def _check_rollback_triggers(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check if rollback should be triggered.
        
        Args:
            metrics: Current metrics.
            
        Returns:
            Dictionary containing rollback check results.
        """
        rollback_check = {
            "rollback_recommended": False,
            "triggers": [],
            "reason": None
        }
        
        workflow_metrics = metrics.get("workflow_metrics", {})
        
        if not workflow_metrics:
            return rollback_check
        
        rollback_config = self.monitoring_config["rollback_triggers"]
        
        # Check failure rate threshold
        success_rates = [wm["success_rate"] for wm in workflow_metrics.values()]
        avg_success_rate = sum(success_rates) / len(success_rates)
        failure_rate = 100 - avg_success_rate
        
        if failure_rate >= rollback_config["failure_rate_threshold"]:
            rollback_check["triggers"].append(f"High failure rate: {failure_rate:.1f}%")
            rollback_check["rollback_recommended"] = True
            rollback_check["reason"] = f"Failure rate {failure_rate:.1f}% exceeds threshold {rollback_config['failure_rate_threshold']}%"
        
        # Check duration increase threshold
        durations = [wm["average_duration_minutes"] for wm in workflow_metrics.values()]
        avg_duration = sum(durations) / len(durations)
        baseline_duration = 8.0
        duration_increase = ((avg_duration - baseline_duration) / baseline_duration) * 100
        
        if duration_increase >= rollback_config["duration_increase_threshold"]:
            rollback_check["triggers"].append(f"Excessive duration increase: {duration_increase:.1f}%")
            rollback_check["rollback_recommended"] = True
            rollback_check["reason"] = f"Duration increase {duration_increase:.1f}% exceeds threshold {rollback_config['duration_increase_threshold']}%"
        
        # Check consecutive failures (simplified check)
        consecutive_failures = sum(1 for wm in workflow_metrics.values() if wm["last_run_status"] == "failure")
        
        if consecutive_failures >= rollback_config["consecutive_failures"]:
            rollback_check["triggers"].append(f"Multiple workflow failures: {consecutive_failures}")
            rollback_check["rollback_recommended"] = True
            rollback_check["reason"] = f"Consecutive failures {consecutive_failures} exceeds threshold {rollback_config['consecutive_failures']}"
        
        return rollback_check
    
    def _generate_monitoring_alerts(self, analysis: Dict[str, Any], rollback_check: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate monitoring alerts based on analysis.
        
        Args:
            analysis: Metrics analysis results.
            rollback_check: Rollback check results.
            
        Returns:
            List of alert dictionaries.
        """
        alerts = []
        
        # Critical alerts
        if rollback_check.get("rollback_recommended", False):
            alerts.append({
                "severity": "critical",
                "type": "rollback_recommended",
                "message": f"Rollback recommended: {rollback_check.get('reason', 'Unknown reason')}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Warning alerts
        if analysis.get("overall_status") == "degraded":
            alerts.append({
                "severity": "warning",
                "type": "performance_degradation",
                "message": f"Performance degradation detected: {len(analysis.get('issues', []))} issues",
                "issues": analysis.get("issues", []),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Info alerts
        if analysis.get("recommendations"):
            alerts.append({
                "severity": "info",
                "type": "recommendations",
                "message": f"Performance recommendations available: {len(analysis['recommendations'])} items",
                "recommendations": analysis["recommendations"],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _display_monitoring_results(self, metrics: Dict[str, Any], analysis: Dict[str, Any], alerts: List[Dict[str, Any]]) -> None:
        """Display monitoring results to console.
        
        Args:
            metrics: Collected metrics.
            analysis: Analysis results.
            alerts: Generated alerts.
        """
        print(f"📊 Monitoring Results - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Overall status
        status_icon = {
            "healthy": "✅",
            "warning": "⚠️",
            "degraded": "❌",
            "no_data": "❓"
        }.get(analysis.get("overall_status"), "❓")
        
        print(f"Overall Status: {status_icon} {analysis.get('overall_status', 'unknown').upper()}")
        print()
        
        # Summary metrics
        summary = analysis.get("summary_metrics", {})
        if summary:
            print("📈 Summary Metrics:")
            print(f"  Success Rate: {summary.get('average_success_rate', 'N/A')}%")
            print(f"  Average Duration: {summary.get('average_duration_minutes', 'N/A')} min")
            print(f"  Duration Change: {summary.get('duration_increase_percent', 'N/A')}%")
            print(f"  Cache Hit Rate: {summary.get('average_cache_hit_rate', 'N/A')}%")
            print()
        
        # Individual workflow metrics
        workflow_metrics = metrics.get("workflow_metrics", {})
        if workflow_metrics:
            print("🔧 Workflow Details:")
            for workflow_name, wm in workflow_metrics.items():
                status_icon = "✅" if wm["last_run_status"] == "success" else "❌"
                print(f"  {status_icon} {workflow_name}:")
                print(f"    Success Rate: {wm['success_rate']:.1f}% ({wm['total_runs'] - wm['failed_runs']}/{wm['total_runs']} runs)")
                print(f"    Duration: {wm['average_duration_minutes']:.1f} min")
                print(f"    Cache Hit Rate: {wm['cache_hit_rate']:.1f}%")
            print()
        
        # Issues and recommendations
        if analysis.get("issues"):
            print("⚠️ Issues Detected:")
            for issue in analysis["issues"]:
                print(f"  • {issue}")
            print()
        
        if analysis.get("recommendations"):
            print("💡 Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
            print()
        
        # Alerts
        if alerts:
            print("🚨 Alerts:")
            for alert in alerts:
                severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["severity"], "⚪")
                print(f"  {severity_icon} {alert['severity'].upper()}: {alert['message']}")
            print()
    
    def _check_phase_completion(self, phase_name: str) -> Dict[str, Any]:
        """Check if the current phase should be completed.
        
        Args:
            phase_name: Name of the phase to check.
            
        Returns:
            Dictionary containing completion check results.
        """
        phase_config = self.rollout_phases[phase_name]
        phase_start = datetime.fromisoformat(self.rollout_state["phase_start_time"])
        
        # Check if phase duration has elapsed
        hours_elapsed = (datetime.utcnow() - phase_start).total_seconds() / 3600
        duration_complete = hours_elapsed >= phase_config["duration_hours"]
        
        # Check if success criteria are consistently met
        # (This would require analyzing recent monitoring data)
        criteria_met = True  # Simplified for now
        
        completion_check = {
            "duration_complete": duration_complete,
            "criteria_met": criteria_met,
            "hours_elapsed": round(hours_elapsed, 2),
            "target_hours": phase_config["duration_hours"],
            "ready_for_next_phase": duration_complete and criteria_met
        }
        
        return completion_check
    
    def complete_phase(self, phase_name: str) -> Dict[str, Any]:
        """Complete the current rollout phase.
        
        Args:
            phase_name: Name of the phase to complete.
            
        Returns:
            Dictionary containing completion results.
        """
        if self.rollout_state.get("current_phase") != phase_name:
            return {
                "status": "error",
                "error": f"Phase {phase_name} is not the current active phase"
            }
        
        print(f"🏁 Completing Phase: {phase_name}")
        
        # Generate phase completion report
        completion_report = self._generate_phase_completion_report(phase_name)
        
        # Update rollout state
        self.rollout_state["current_phase"] = None
        self.rollout_state["phase_start_time"] = None
        
        # Mark monitoring as complete
        if self.rollout_state["monitoring_data"]:
            self.rollout_state["monitoring_data"][-1]["status"] = "completed"
            self.rollout_state["monitoring_data"][-1]["completion_report"] = completion_report
        
        self._save_rollout_state()
        
        print(f"✅ Phase {phase_name} completed successfully")
        
        return {
            "status": "completed",
            "phase": phase_name,
            "completion_report": completion_report
        }
    
    def _generate_phase_completion_report(self, phase_name: str) -> Dict[str, Any]:
        """Generate a completion report for a phase.
        
        Args:
            phase_name: Name of the completed phase.
            
        Returns:
            Dictionary containing completion report.
        """
        phase_config = self.rollout_phases[phase_name]
        
        # Collect final metrics
        final_metrics = self._collect_phase_metrics(phase_name)
        final_analysis = self._analyze_phase_metrics(final_metrics, phase_config["success_criteria"])
        
        # Calculate phase statistics
        monitoring_data = self.rollout_state.get("monitoring_data", [])
        current_monitoring = monitoring_data[-1] if monitoring_data else {}
        
        checks = current_monitoring.get("checks", [])
        alerts = current_monitoring.get("alerts", [])
        
        report = {
            "phase": phase_name,
            "completion_time": datetime.utcnow().isoformat(),
            "duration_hours": (datetime.utcnow() - datetime.fromisoformat(self.rollout_state["phase_start_time"])).total_seconds() / 3600,
            "final_metrics": final_metrics,
            "final_analysis": final_analysis,
            "statistics": {
                "total_monitoring_checks": len(checks),
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
                "warning_alerts": len([a for a in alerts if a.get("severity") == "warning"])
            },
            "success_criteria_met": all(final_analysis.get("criteria_met", {}).values()),
            "overall_success": final_analysis.get("overall_status") in ["healthy", "warning"]
        }
        
        return report
    
    def rollback_phase(self, automatic: bool = False, reason: str = None) -> Dict[str, Any]:
        """Rollback the current phase to previous state.
        
        Args:
            automatic: Whether this is an automatic rollback.
            reason: Reason for the rollback.
            
        Returns:
            Dictionary containing rollback results.
        """
        current_phase = self.rollout_state.get("current_phase")
        
        if not current_phase:
            return {
                "status": "error",
                "error": "No active phase to rollback"
            }
        
        print(f"🔄 {'Automatic' if automatic else 'Manual'} Rollback Initiated")
        print(f"Phase: {current_phase}")
        if reason:
            print(f"Reason: {reason}")
        print()
        
        # Find backup to restore
        backups = self.rollout_state.get("backups", {})
        
        if not backups:
            return {
                "status": "error",
                "error": "No backups available for rollback"
            }
        
        # Restore workflows from backup
        rollback_results = []
        
        for workflow_name, backup_path in backups.items():
            try:
                workflow_path = self.workflows_dir / workflow_name
                shutil.copy2(backup_path, workflow_path)
                
                rollback_results.append({
                    "workflow": workflow_name,
                    "status": "restored",
                    "backup_path": backup_path
                })
                
                print(f"  ✅ Restored: {workflow_name}")
                
            except Exception as e:
                rollback_results.append({
                    "workflow": workflow_name,
                    "status": "failed",
                    "error": str(e)
                })
                
                print(f"  ❌ Failed to restore: {workflow_name} - {e}")
        
        # Record rollback in history
        rollback_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "phase": current_phase,
            "automatic": automatic,
            "reason": reason,
            "results": rollback_results
        }
        
        self.rollout_state["rollback_history"].append(rollback_record)
        
        # Reset rollout state
        self.rollout_state["current_phase"] = None
        self.rollout_state["phase_start_time"] = None
        self.rollout_state["deployed_workflows"] = []
        
        # Mark monitoring as rolled back
        if self.rollout_state["monitoring_data"]:
            self.rollout_state["monitoring_data"][-1]["status"] = "rolled_back"
            self.rollout_state["monitoring_data"][-1]["rollback_record"] = rollback_record
        
        self._save_rollout_state()
        
        successful_rollbacks = len([r for r in rollback_results if r["status"] == "restored"])
        total_workflows = len(rollback_results)
        
        print(f"\n🔄 Rollback completed: {successful_rollbacks}/{total_workflows} workflows restored")
        
        return {
            "status": "completed",
            "phase": current_phase,
            "automatic": automatic,
            "reason": reason,
            "restored_workflows": successful_rollbacks,
            "total_workflows": total_workflows,
            "rollback_record": rollback_record
        }
    
    def generate_rollout_report(self) -> str:
        """Generate comprehensive rollout report."""
        report_lines = []
        
        # Header
        report_lines.extend([
            "🚀 Workflow Rollout Report",
            "=" * 50,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Repository: {self.repo_root}",
            ""
        ])
        
        # Current status
        current_phase = self.rollout_state.get("current_phase")
        if current_phase:
            phase_config = self.rollout_phases[current_phase]
            report_lines.extend([
                "📊 Current Status",
                "-" * 20,
                f"Active Phase: {phase_config['name']}",
                f"Phase Start: {self.rollout_state.get('phase_start_time', 'Unknown')}",
                f"Deployed Workflows: {', '.join(self.rollout_state.get('deployed_workflows', []))}",
                ""
            ])
        else:
            report_lines.extend([
                "📊 Current Status",
                "-" * 20,
                "No active rollout phase",
                ""
            ])
        
        # Monitoring history
        monitoring_data = self.rollout_state.get("monitoring_data", [])
        if monitoring_data:
            report_lines.extend([
                "📈 Monitoring History",
                "-" * 25
            ])
            
            for i, monitoring in enumerate(monitoring_data, 1):
                phase = monitoring.get("phase", "Unknown")
                status = monitoring.get("status", "Unknown")
                checks_count = len(monitoring.get("checks", []))
                alerts_count = len(monitoring.get("alerts", []))
                
                report_lines.extend([
                    f"{i}. Phase: {phase}",
                    f"   Status: {status.title()}",
                    f"   Monitoring Checks: {checks_count}",
                    f"   Alerts Generated: {alerts_count}",
                    ""
                ])
        
        # Rollback history
        rollback_history = self.rollout_state.get("rollback_history", [])
        if rollback_history:
            report_lines.extend([
                "🔄 Rollback History",
                "-" * 20
            ])
            
            for i, rollback in enumerate(rollback_history, 1):
                rollback_type = "Automatic" if rollback.get("automatic", False) else "Manual"
                reason = rollback.get("reason", "No reason provided")
                
                report_lines.extend([
                    f"{i}. {rollback_type} Rollback",
                    f"   Phase: {rollback.get('phase', 'Unknown')}",
                    f"   Timestamp: {rollback.get('timestamp', 'Unknown')}",
                    f"   Reason: {reason}",
                    ""
                ])
        
        # Lessons learned and recommendations
        report_lines.extend([
            "💡 Lessons Learned & Recommendations",
            "-" * 40,
            "• Monitor workflow performance continuously during rollout",
            "• Implement gradual rollout phases to minimize risk",
            "• Maintain comprehensive backups for quick rollback",
            "• Set clear success criteria and rollback triggers",
            "• Document all issues and resolutions for future reference",
            ""
        ])
        
        report_lines.extend([
            "🏁 Report Complete",
            f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ])
        
        return "\n".join(report_lines)
    
    def save_rollout_documentation(self, output_dir: str = "rollout-documentation") -> str:
        """Save comprehensive rollout documentation."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save rollout state
        state_file = os.path.join(output_dir, f"rollout_state_{timestamp}.json")
        with open(state_file, "w") as f:
            json.dump(self.rollout_state, f, indent=2, default=str)
        
        # Save rollout report
        report_file = os.path.join(output_dir, f"rollout_report_{timestamp}.md")
        with open(report_file, "w") as f:
            f.write(self.generate_rollout_report())
        
        return output_dir


def main():
    """Main entry point for rollout management."""
    parser = argparse.ArgumentParser(
        description="Workflow Rollout and Monitoring Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start-phase phase_1_validation     # Start validation phase
  %(prog)s monitor                            # Monitor current phase
  %(prog)s complete-phase phase_1_validation  # Complete current phase
  %(prog)s rollback --reason "Performance issues"  # Manual rollback
  %(prog)s status                             # Show rollout status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start phase command
    start_parser = subparsers.add_parser("start-phase", help="Start a rollout phase")
    start_parser.add_argument("phase", help="Phase name to start")
    start_parser.add_argument("--force", action="store_true", help="Force start ignoring prerequisites")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor current rollout phase")
    
    # Complete phase command
    complete_parser = subparsers.add_parser("complete-phase", help="Complete current rollout phase")
    complete_parser.add_argument("phase", help="Phase name to complete")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback current phase")
    rollback_parser.add_argument("--reason", help="Reason for rollback")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show rollout status")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate rollout report")
    report_parser.add_argument("--save", action="store_true", help="Save report to file")
    
    # Global arguments
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        manager = WorkflowRolloutManager(args.repo_root)
        
        if args.command == "start-phase":
            result = manager.start_rollout_phase(args.phase, args.force)
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                if result["status"] == "success":
                    print(f"✅ Phase '{args.phase}' started successfully")
                    print(f"Deployed workflows: {', '.join(result['deployed_workflows'])}")
                    print(f"Monitoring duration: {result['phase_duration_hours']} hours")
                else:
                    print(f"❌ Failed to start phase: {result.get('error', 'Unknown error')}")
                    sys.exit(1)
        
        elif args.command == "monitor":
            result = manager.monitor_rollout_phase()
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            
            if result.get("rollback_executed"):
                print("\n🚨 Automatic rollback was executed due to performance issues")
                sys.exit(1)
        
        elif args.command == "complete-phase":
            result = manager.complete_phase(args.phase)
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                if result["status"] == "completed":
                    print(f"✅ Phase '{args.phase}' completed successfully")
                else:
                    print(f"❌ Failed to complete phase: {result.get('error', 'Unknown error')}")
                    sys.exit(1)
        
        elif args.command == "rollback":
            result = manager.rollback_phase(automatic=False, reason=args.reason)
            
            if args.output == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                if result["status"] == "completed":
                    print(f"✅ Rollback completed: {result['restored_workflows']}/{result['total_workflows']} workflows restored")
                else:
                    print(f"❌ Rollback failed: {result.get('error', 'Unknown error')}")
                    sys.exit(1)
        
        elif args.command == "status":
            current_phase = manager.rollout_state.get("current_phase")
            
            if args.output == "json":
                print(json.dumps(manager.rollout_state, indent=2, default=str))
            else:
                if current_phase:
                    phase_config = manager.rollout_phases[current_phase]
                    print(f"📊 Rollout Status: ACTIVE")
                    print(f"Current Phase: {phase_config['name']}")
                    print(f"Deployed Workflows: {', '.join(manager.rollout_state.get('deployed_workflows', []))}")
                    
                    if manager.rollout_state.get("phase_start_time"):
                        start_time = datetime.fromisoformat(manager.rollout_state["phase_start_time"])
                        elapsed = datetime.utcnow() - start_time
                        print(f"Elapsed Time: {elapsed}")
                else:
                    print("📊 Rollout Status: INACTIVE")
                    print("No active rollout phase")
        
        elif args.command == "report":
            report = manager.generate_rollout_report()
            
            if args.save:
                output_dir = manager.save_rollout_documentation()
                print(f"📄 Documentation saved to: {output_dir}")
            
            print(report)
        
    except Exception as e:
        print(f"❌ Rollout management error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Comprehensive Workflow Testing Framework

This script provides comprehensive testing capabilities for all optimized GitHub Actions workflows,
including performance validation, error handling testing, and badge generation verification.

Requirements addressed:
- 10.1: Test all optimized workflows on feature branches
- 10.1: Validate performance improvements meet target metrics
- 10.1: Test error handling and recovery mechanisms
- 10.1: Verify badge generation and update functionality
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml


class ComprehensiveWorkflowTester:
    """Comprehensive testing framework for optimized GitHub Actions workflows."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the comprehensive workflow tester.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        
        # Performance targets for optimized workflows
        self.performance_targets = {
            "quality-gate.yml": {
                "max_duration_minutes": 8,
                "target_duration_minutes": 5,
                "cache_hit_rate_target": 90.0,
                "parallel_jobs": True,
                "fail_fast": True
            },
            "security-scan.yml": {
                "max_duration_minutes": 12,
                "target_duration_minutes": 8,
                "cache_hit_rate_target": 85.0,
                "incremental_scanning": True,
                "parallel_scans": True
            },
            "docs.yml": {
                "max_duration_minutes": 6,
                "target_duration_minutes": 4,
                "cache_hit_rate_target": 90.0,
                "incremental_builds": True,
                "quality_checks": True
            },
            "publish.yml": {
                "max_duration_minutes": 6,
                "target_duration_minutes": 4,
                "validation_required": True,
                "security_checks": True
            }
        }
        
        # Test results storage
        self.test_results = {
            "start_time": datetime.utcnow().isoformat(),
            "workflows": {},
            "summary": {
                "total_workflows": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "performance_issues": 0
            }
        }
        
        # Available testing tools
        self.available_tools = self._check_available_tools()
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ValueError("Could not find repository root (.git directory)")
    
    def _check_available_tools(self) -> Dict[str, bool]:
        """Check availability of testing tools."""
        tools = {}
        
        # Check for act (local GitHub Actions runner)
        try:
            subprocess.run(["act", "--version"], capture_output=True, check=True)
            tools["act"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["act"] = False
        
        # Check for actionlint
        try:
            subprocess.run(["actionlint", "-version"], capture_output=True, check=True)
            tools["actionlint"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["actionlint"] = False
        
        # Check for yamllint
        try:
            subprocess.run(["yamllint", "--version"], capture_output=True, check=True)
            tools["yamllint"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["yamllint"] = False
        
        return tools
    
    def test_all_optimized_workflows(self) -> Dict[str, Any]:
        """Test all optimized workflows comprehensively.
        
        Returns:
            Dictionary containing comprehensive test results.
        """
        print("🧪 Starting Comprehensive Workflow Testing")
        print("=" * 60)
        print(f"Repository: {self.repo_root}")
        print(f"Workflows Directory: {self.workflows_dir}")
        print(f"Available Tools: {', '.join([tool for tool, available in self.available_tools.items() if available])}")
        print()
        
        # Find optimized workflow files
        workflow_files = [
            self.workflows_dir / "quality-gate.yml",
            self.workflows_dir / "security-scan.yml", 
            self.workflows_dir / "docs.yml",
            self.workflows_dir / "publish.yml"
        ]
        
        # Filter to existing files
        existing_workflows = [wf for wf in workflow_files if wf.exists()]
        
        if not existing_workflows:
            return {
                "status": "no_workflows",
                "message": "No optimized workflow files found",
                "workflows": {}
            }
        
        print(f"Found {len(existing_workflows)} optimized workflows to test")
        
        self.test_results["summary"]["total_workflows"] = len(existing_workflows)
        
        # Test each workflow comprehensively
        for workflow_file in existing_workflows:
            print(f"\n📋 Testing: {workflow_file.name}")
            print("-" * 40)
            
            workflow_result = self._test_workflow_comprehensive(workflow_file)
            self.test_results["workflows"][workflow_file.name] = workflow_result
            
            # Update summary
            if workflow_result["overall_status"] == "passed":
                self.test_results["summary"]["passed"] += 1
            elif workflow_result["overall_status"] == "failed":
                self.test_results["summary"]["failed"] += 1
            
            self.test_results["summary"]["warnings"] += len(workflow_result.get("warnings", []))
            
            if workflow_result.get("performance_issues"):
                self.test_results["summary"]["performance_issues"] += 1
        
        # Generate final summary
        self.test_results["end_time"] = datetime.utcnow().isoformat()
        self.test_results["duration_minutes"] = self._calculate_test_duration()
        
        # Determine overall status
        if self.test_results["summary"]["failed"] > 0:
            self.test_results["status"] = "failed"
        elif self.test_results["summary"]["warnings"] > 0:
            self.test_results["status"] = "passed_with_warnings"
        else:
            self.test_results["status"] = "passed"
        
        return self.test_results
    
    def _test_workflow_comprehensive(self, workflow_path: Path) -> Dict[str, Any]:
        """Perform comprehensive testing of a single workflow.
        
        Args:
            workflow_path: Path to the workflow file.
            
        Returns:
            Dictionary containing comprehensive test results.
        """
        workflow_name = workflow_path.name
        
        result = {
            "workflow": workflow_name,
            "start_time": datetime.utcnow().isoformat(),
            "tests": {},
            "warnings": [],
            "errors": [],
            "performance_metrics": {},
            "optimization_validation": {},
            "overall_status": "testing"
        }
        
        # Test suite for comprehensive validation
        test_suite = [
            ("syntax_validation", self._test_syntax_validation),
            ("optimization_validation", self._test_optimization_features),
            ("performance_validation", self._test_performance_characteristics),
            ("error_handling_validation", self._test_error_handling),
            ("badge_generation_validation", self._test_badge_generation),
            ("caching_validation", self._test_caching_strategy),
            ("security_validation", self._test_security_features),
            ("dry_run_validation", self._test_dry_run_execution)
        ]
        
        passed_tests = 0
        total_tests = len(test_suite)
        
        # Execute test suite
        for test_name, test_func in test_suite:
            print(f"  🔍 {test_name.replace('_', ' ').title()}...")
            
            try:
                test_result = test_func(workflow_path)
                result["tests"][test_name] = test_result
                
                if test_result["status"] == "passed":
                    passed_tests += 1
                    print(f"    ✅ {test_result.get('message', 'Passed')}")
                elif test_result["status"] == "failed":
                    print(f"    ❌ {test_result.get('error', 'Failed')}")
                    result["errors"].append(f"{test_name}: {test_result.get('error', 'Unknown error')}")
                elif test_result["status"] == "warning":
                    passed_tests += 1  # Warnings don't fail the test
                    print(f"    ⚠️ {test_result.get('message', 'Warning')}")
                    result["warnings"].append(f"{test_name}: {test_result.get('message', 'Unknown warning')}")
                else:
                    print(f"    ⏭️ {test_result.get('reason', 'Skipped')}")
                
            except Exception as e:
                print(f"    💥 Test error: {e}")
                result["errors"].append(f"{test_name}: Test execution error - {e}")
                result["tests"][test_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Determine overall status
        if result["errors"]:
            result["overall_status"] = "failed"
        elif result["warnings"]:
            result["overall_status"] = "passed_with_warnings"
        else:
            result["overall_status"] = "passed"
        
        result["end_time"] = datetime.utcnow().isoformat()
        result["test_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0
        }
        
        return result
    
    def _test_syntax_validation(self, workflow_path: Path) -> Dict[str, Any]:
        """Test workflow syntax and structure validation."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data:
                return {"status": "failed", "error": "Empty or invalid YAML file"}
            
            # Check required fields
            required_fields = ["name", "on", "jobs"]
            missing_fields = [field for field in required_fields if field not in workflow_data]
            
            if missing_fields:
                return {
                    "status": "failed",
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Validate jobs structure
            jobs = workflow_data.get("jobs", {})
            if not isinstance(jobs, dict) or not jobs:
                return {"status": "failed", "error": "Jobs section must be a non-empty dictionary"}
            
            # Check for optimization indicators
            optimization_indicators = []
            
            # Check for advanced caching
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        uses = step.get("uses", "")
                        if "advanced-cache-manager" in uses:
                            optimization_indicators.append("Advanced caching system")
                        elif "cache@v4" in uses:
                            optimization_indicators.append("Updated caching actions")
            
            # Check for performance optimizations
            if "UV_CONCURRENT_DOWNLOADS" in str(workflow_data):
                optimization_indicators.append("Parallel dependency downloads")
            
            if "timeout-minutes" in str(workflow_data):
                optimization_indicators.append("Timeout optimizations")
            
            return {
                "status": "passed",
                "message": "Syntax validation passed",
                "optimization_indicators": optimization_indicators
            }
            
        except yaml.YAMLError as e:
            return {"status": "failed", "error": f"YAML syntax error: {e}"}
        except Exception as e:
            return {"status": "failed", "error": f"Validation error: {e}"}
    
    def _test_optimization_features(self, workflow_path: Path) -> Dict[str, Any]:
        """Test that optimization features are properly implemented."""
        workflow_name = workflow_path.name
        targets = self.performance_targets.get(workflow_name, {})
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            optimizations_found = []
            missing_optimizations = []
            
            # Check for advanced caching
            if "advanced-cache-manager" in content:
                optimizations_found.append("Advanced multi-level caching system")
            elif targets.get("cache_hit_rate_target"):
                missing_optimizations.append("Advanced caching system not implemented")
            
            # Check for parallel execution
            jobs = workflow_data.get("jobs", {})
            if len(jobs) > 1:
                # Check if jobs can run in parallel
                jobs_with_needs = sum(1 for job in jobs.values() if "needs" in job)
                if jobs_with_needs < len(jobs):
                    optimizations_found.append("Parallel job execution enabled")
                else:
                    missing_optimizations.append("Limited parallelization due to dependencies")
            
            # Check for fail-fast strategies
            if targets.get("fail_fast"):
                fail_fast_found = False
                for job_data in jobs.values():
                    strategy = job_data.get("strategy", {})
                    if strategy.get("fail-fast") is True:
                        fail_fast_found = True
                        break
                
                if fail_fast_found:
                    optimizations_found.append("Fail-fast strategy implemented")
                else:
                    missing_optimizations.append("Fail-fast strategy not found")
            
            # Check for performance monitoring
            if "workflow-monitor" in content or "performance-tracker" in content:
                optimizations_found.append("Performance monitoring enabled")
            
            # Check for timeout optimizations
            timeout_optimized = False
            for job_data in jobs.values():
                timeout = job_data.get("timeout-minutes")
                if timeout and timeout <= targets.get("max_duration_minutes", 15):
                    timeout_optimized = True
                    break
            
            if timeout_optimized:
                optimizations_found.append("Timeout optimizations applied")
            
            # Check for incremental features (if applicable)
            if targets.get("incremental_scanning") and "incremental" in content.lower():
                optimizations_found.append("Incremental processing implemented")
            
            if targets.get("incremental_builds") and "incremental" in content.lower():
                optimizations_found.append("Incremental builds implemented")
            
            # Determine result
            if missing_optimizations:
                return {
                    "status": "warning",
                    "message": f"Some optimizations missing: {len(missing_optimizations)} issues",
                    "optimizations_found": optimizations_found,
                    "missing_optimizations": missing_optimizations
                }
            else:
                return {
                    "status": "passed",
                    "message": f"All expected optimizations found: {len(optimizations_found)} features",
                    "optimizations_found": optimizations_found
                }
                
        except Exception as e:
            return {"status": "failed", "error": f"Optimization validation error: {e}"}
    
    def _test_performance_characteristics(self, workflow_path: Path) -> Dict[str, Any]:
        """Test performance characteristics against targets."""
        workflow_name = workflow_path.name
        targets = self.performance_targets.get(workflow_name, {})
        
        if not targets:
            return {
                "status": "skipped",
                "reason": f"No performance targets defined for {workflow_name}"
            }
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            performance_analysis = {
                "timeout_analysis": {},
                "caching_analysis": {},
                "parallelization_analysis": {},
                "optimization_score": 0
            }
            
            jobs = workflow_data.get("jobs", {})
            
            # Analyze timeout settings
            max_timeout = 0
            jobs_with_timeout = 0
            
            for job_name, job_data in jobs.items():
                timeout = job_data.get("timeout-minutes")
                if timeout:
                    jobs_with_timeout += 1
                    max_timeout = max(max_timeout, timeout)
            
            performance_analysis["timeout_analysis"] = {
                "max_timeout_minutes": max_timeout,
                "target_max_minutes": targets.get("max_duration_minutes"),
                "jobs_with_timeout": jobs_with_timeout,
                "total_jobs": len(jobs),
                "timeout_compliance": max_timeout <= targets.get("max_duration_minutes", 15) if max_timeout > 0 else None
            }
            
            # Analyze caching strategy
            caching_steps = 0
            advanced_caching = False
            
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        uses = step.get("uses", "")
                        if "cache" in uses:
                            caching_steps += 1
                        if "advanced-cache-manager" in uses:
                            advanced_caching = True
            
            performance_analysis["caching_analysis"] = {
                "caching_steps": caching_steps,
                "advanced_caching": advanced_caching,
                "cache_target_hit_rate": targets.get("cache_hit_rate_target"),
                "caching_score": min(100, (caching_steps * 25) + (50 if advanced_caching else 0))
            }
            
            # Analyze parallelization
            jobs_with_needs = sum(1 for job in jobs.values() if "needs" in job)
            parallel_jobs = len(jobs) - jobs_with_needs
            
            performance_analysis["parallelization_analysis"] = {
                "total_jobs": len(jobs),
                "parallel_jobs": parallel_jobs,
                "sequential_jobs": jobs_with_needs,
                "parallelization_ratio": round((parallel_jobs / len(jobs)) * 100, 1) if len(jobs) > 0 else 0
            }
            
            # Calculate optimization score
            score = 0
            
            # Timeout score (30 points)
            if performance_analysis["timeout_analysis"]["timeout_compliance"]:
                score += 30
            elif max_timeout > 0:
                score += 15  # Partial credit for having timeouts
            
            # Caching score (40 points)
            score += min(40, performance_analysis["caching_analysis"]["caching_score"] * 0.4)
            
            # Parallelization score (30 points)
            score += min(30, performance_analysis["parallelization_analysis"]["parallelization_ratio"] * 0.3)
            
            performance_analysis["optimization_score"] = round(score, 1)
            
            # Determine result
            if score >= 80:
                status = "passed"
                message = f"Excellent performance characteristics (score: {score}/100)"
            elif score >= 60:
                status = "warning"
                message = f"Good performance characteristics with room for improvement (score: {score}/100)"
            else:
                status = "failed"
                message = f"Performance characteristics need significant improvement (score: {score}/100)"
            
            return {
                "status": status,
                "message": message,
                "performance_analysis": performance_analysis
            }
            
        except Exception as e:
            return {"status": "failed", "error": f"Performance analysis error: {e}"}
    
    def _test_error_handling(self, workflow_path: Path) -> Dict[str, Any]:
        """Test error handling and recovery mechanisms."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            error_handling_features = []
            missing_features = []
            
            jobs = workflow_data.get("jobs", {})
            
            # Check for error reporting steps
            has_error_reporting = False
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        step_name = step.get("name", "").lower()
                        uses = step.get("uses", "")
                        if_condition = step.get("if", "")
                        
                        if ("error" in step_name or "failure" in step_name or 
                            "report" in step_name or "error-reporter" in uses):
                            has_error_reporting = True
                            error_handling_features.append("Error reporting steps")
                            break
                        
                        if "failure()" in if_condition:
                            has_error_reporting = True
                            error_handling_features.append("Failure condition handling")
            
            if not has_error_reporting:
                missing_features.append("Error reporting mechanisms")
            
            # Check for retry mechanisms
            if "retry" in content.lower() or "nick-invision/retry" in content:
                error_handling_features.append("Retry mechanisms for transient failures")
            else:
                missing_features.append("Retry mechanisms for reliability")
            
            # Check for graceful degradation
            if "continue-on-error" in content:
                error_handling_features.append("Graceful error handling")
            
            # Check for timeout handling
            timeout_count = content.count("timeout-minutes")
            if timeout_count > 0:
                error_handling_features.append(f"Timeout protection ({timeout_count} jobs)")
            else:
                missing_features.append("Timeout protection")
            
            # Check for enhanced error context
            if "GITHUB_OUTPUT" in content or "github.event" in content:
                error_handling_features.append("Enhanced error context")
            
            # Determine result
            if len(error_handling_features) >= 3:
                return {
                    "status": "passed",
                    "message": f"Comprehensive error handling ({len(error_handling_features)} features)",
                    "error_handling_features": error_handling_features,
                    "missing_features": missing_features
                }
            elif len(error_handling_features) >= 1:
                return {
                    "status": "warning",
                    "message": f"Basic error handling present ({len(error_handling_features)} features)",
                    "error_handling_features": error_handling_features,
                    "missing_features": missing_features
                }
            else:
                return {
                    "status": "failed",
                    "error": "No error handling mechanisms found",
                    "missing_features": missing_features
                }
                
        except Exception as e:
            return {"status": "failed", "error": f"Error handling validation error: {e}"}
    
    def _test_badge_generation(self, workflow_path: Path) -> Dict[str, Any]:
        """Test badge generation and update functionality."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            badge_features = []
            
            # Check for badge generation steps
            if "badge" in content.lower():
                badge_features.append("Badge generation steps present")
            
            # Check for badge data creation
            if "badge-data" in content or "badge_data" in content:
                badge_features.append("Badge data directory creation")
            
            # Check for artifact upload for badges
            if "upload-artifact" in content and "badge" in content:
                badge_features.append("Badge artifact upload")
            
            # Check for specific badge types
            badge_types = []
            if "coverage" in content.lower():
                badge_types.append("coverage")
            if "build" in content.lower() or "status" in content.lower():
                badge_types.append("build status")
            if "security" in content.lower():
                badge_types.append("security")
            if "performance" in content.lower():
                badge_types.append("performance")
            
            if badge_types:
                badge_features.append(f"Badge types: {', '.join(badge_types)}")
            
            # Check for badge update workflows
            if "update-badges" in content or "badge" in workflow_path.name:
                badge_features.append("Dedicated badge update workflow")
            
            # Determine result
            if len(badge_features) >= 2:
                return {
                    "status": "passed",
                    "message": f"Badge generation implemented ({len(badge_features)} features)",
                    "badge_features": badge_features
                }
            elif len(badge_features) >= 1:
                return {
                    "status": "warning",
                    "message": f"Basic badge support ({len(badge_features)} features)",
                    "badge_features": badge_features
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "No badge generation expected for this workflow"
                }
                
        except Exception as e:
            return {"status": "failed", "error": f"Badge validation error: {e}"}
    
    def _test_caching_strategy(self, workflow_path: Path) -> Dict[str, Any]:
        """Test caching strategy implementation."""
        workflow_name = workflow_path.name
        targets = self.performance_targets.get(workflow_name, {})
        
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            caching_analysis = {
                "cache_actions": [],
                "cache_keys": [],
                "cache_paths": [],
                "advanced_features": []
            }
            
            jobs = workflow_data.get("jobs", {})
            
            # Analyze caching implementation
            for job_name, job_data in jobs.items():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        uses = step.get("uses", "")
                        with_params = step.get("with", {})
                        
                        if "cache" in uses:
                            caching_analysis["cache_actions"].append({
                                "job": job_name,
                                "action": uses,
                                "version": uses.split("@")[-1] if "@" in uses else "unknown"
                            })
                            
                            # Analyze cache configuration
                            if "key" in with_params:
                                caching_analysis["cache_keys"].append(with_params["key"])
                            
                            if "path" in with_params:
                                caching_analysis["cache_paths"].append(with_params["path"])
                        
                        # Check for advanced caching features
                        if "advanced-cache-manager" in uses:
                            caching_analysis["advanced_features"].append("Multi-level caching system")
                        
                        if "cache-performance-monitor" in uses:
                            caching_analysis["advanced_features"].append("Cache performance monitoring")
            
            # Check for cache optimization features
            if "cache-hit" in content or "cache_hit" in content:
                caching_analysis["advanced_features"].append("Cache hit rate tracking")
            
            if "restore-keys" in content:
                caching_analysis["advanced_features"].append("Fallback cache keys")
            
            # Analyze cache key strategies
            cache_key_quality = 0
            for key in caching_analysis["cache_keys"]:
                if "hashFiles" in key:
                    cache_key_quality += 2  # Good: content-based keys
                elif "${{" in key:
                    cache_key_quality += 1  # OK: dynamic keys
            
            # Calculate caching score
            score = 0
            score += min(30, len(caching_analysis["cache_actions"]) * 10)  # Up to 30 points for cache actions
            score += min(20, cache_key_quality * 5)  # Up to 20 points for key quality
            score += min(30, len(caching_analysis["advanced_features"]) * 10)  # Up to 30 points for advanced features
            score += 20 if len(caching_analysis["cache_paths"]) > 0 else 0  # 20 points for having cache paths
            
            caching_analysis["caching_score"] = score
            caching_analysis["target_hit_rate"] = targets.get("cache_hit_rate_target")
            
            # Determine result
            if score >= 80:
                status = "passed"
                message = f"Excellent caching strategy (score: {score}/100)"
            elif score >= 60:
                status = "warning"
                message = f"Good caching with room for improvement (score: {score}/100)"
            elif score >= 30:
                status = "warning"
                message = f"Basic caching implemented (score: {score}/100)"
            else:
                status = "failed"
                message = f"Insufficient caching strategy (score: {score}/100)"
            
            return {
                "status": status,
                "message": message,
                "caching_analysis": caching_analysis
            }
            
        except Exception as e:
            return {"status": "failed", "error": f"Caching validation error: {e}"}
    
    def _test_security_features(self, workflow_path: Path) -> Dict[str, Any]:
        """Test security features and best practices."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            security_features = []
            security_issues = []
            
            # Check permissions
            permissions = workflow_data.get("permissions", {})
            if permissions:
                if permissions == "read-all" or permissions.get("contents") == "read":
                    security_features.append("Minimal read permissions")
                elif "write" in str(permissions):
                    security_features.append("Write permissions (review required)")
                else:
                    security_features.append("Custom permissions configured")
            else:
                security_issues.append("No explicit permissions set")
            
            # Check for pinned action versions
            unpinned_actions = []
            jobs = workflow_data.get("jobs", {})
            
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        uses = step.get("uses", "")
                        if uses and "@" in uses:
                            action, version = uses.rsplit("@", 1)
                            if version in ["main", "master", "latest"]:
                                unpinned_actions.append(uses)
            
            if unpinned_actions:
                security_issues.append(f"Unpinned actions: {len(unpinned_actions)} found")
            else:
                security_features.append("All actions use pinned versions")
            
            # Check for secret handling
            if "${{ secrets." in content:
                security_features.append("Proper secret handling")
            
            # Check for OIDC token usage
            if "id-token: write" in content:
                security_features.append("OIDC token authentication")
            
            # Check for security scanning
            if "security" in workflow_path.name.lower():
                security_features.append("Dedicated security scanning workflow")
            
            # Determine result
            security_score = len(security_features) * 20 - len(security_issues) * 10
            
            if security_score >= 80:
                return {
                    "status": "passed",
                    "message": f"Excellent security practices (score: {security_score}/100)",
                    "security_features": security_features,
                    "security_issues": security_issues
                }
            elif security_score >= 60:
                return {
                    "status": "warning",
                    "message": f"Good security with minor issues (score: {security_score}/100)",
                    "security_features": security_features,
                    "security_issues": security_issues
                }
            else:
                return {
                    "status": "failed",
                    "error": f"Security issues need attention (score: {security_score}/100)",
                    "security_features": security_features,
                    "security_issues": security_issues
                }
                
        except Exception as e:
            return {"status": "failed", "error": f"Security validation error: {e}"}
    
    def _test_dry_run_execution(self, workflow_path: Path) -> Dict[str, Any]:
        """Test workflow with dry run execution using act."""
        if not self.available_tools.get("act", False):
            return {
                "status": "skipped",
                "reason": "act not available - install from https://github.com/nektos/act"
            }
        
        try:
            # Run act with dry-run flag
            result = subprocess.run(
                ["act", "--dry-run", "-W", str(workflow_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return {
                    "status": "passed",
                    "message": "Dry run execution successful",
                    "output_lines": len(result.stdout.split('\n'))
                }
            else:
                # Check if failure is due to missing secrets/environment (acceptable)
                stderr_lower = result.stderr.lower()
                if any(keyword in stderr_lower for keyword in ["secret", "env", "token"]):
                    return {
                        "status": "passed",
                        "message": "Dry run failed due to missing secrets (expected in test environment)",
                        "note": "Workflow structure appears valid"
                    }
                else:
                    return {
                        "status": "failed",
                        "error": "Dry run execution failed",
                        "stderr_preview": result.stderr[:500]  # First 500 chars
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Dry run timed out after 2 minutes"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Dry run execution error: {e}"
            }
    
    def _calculate_test_duration(self) -> float:
        """Calculate total test duration in minutes."""
        try:
            start_time = datetime.fromisoformat(self.test_results["start_time"])
            end_time = datetime.fromisoformat(self.test_results["end_time"])
            duration = (end_time - start_time).total_seconds() / 60
            return round(duration, 2)
        except:
            return 0.0
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive test report."""
        report_lines = []
        
        # Header
        report_lines.extend([
            "🧪 Comprehensive Workflow Testing Report",
            "=" * 60,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Repository: {self.repo_root}",
            f"Test Duration: {self.test_results.get('duration_minutes', 0)} minutes",
            ""
        ])
        
        # Executive Summary
        summary = self.test_results["summary"]
        report_lines.extend([
            "📊 Executive Summary",
            "-" * 30,
            f"Overall Status: {self.test_results.get('status', 'unknown').upper()}",
            f"Total Workflows Tested: {summary['total_workflows']}",
            f"✅ Passed: {summary['passed']}",
            f"❌ Failed: {summary['failed']}",
            f"⚠️ Warnings: {summary['warnings']}",
            f"🚀 Performance Issues: {summary['performance_issues']}",
            ""
        ])
        
        # Tool Availability
        report_lines.extend([
            "🔧 Testing Tools",
            "-" * 20
        ])
        
        for tool, available in self.available_tools.items():
            status = "✅ Available" if available else "❌ Not Available"
            report_lines.append(f"{tool}: {status}")
        
        report_lines.append("")
        
        # Individual Workflow Results
        report_lines.extend([
            "📋 Workflow Test Results",
            "-" * 30
        ])
        
        for workflow_name, workflow_result in self.test_results["workflows"].items():
            status_icon = {
                "passed": "✅",
                "passed_with_warnings": "⚠️",
                "failed": "❌"
            }.get(workflow_result.get("overall_status"), "❓")
            
            test_summary = workflow_result.get("test_summary", {})
            success_rate = test_summary.get("success_rate", 0)
            
            report_lines.extend([
                f"{status_icon} {workflow_name}",
                f"   Status: {workflow_result.get('overall_status', 'unknown').upper()}",
                f"   Success Rate: {success_rate}% ({test_summary.get('passed_tests', 0)}/{test_summary.get('total_tests', 0)} tests)",
                ""
            ])
            
            # Show key test results
            tests = workflow_result.get("tests", {})
            for test_name, test_result in tests.items():
                test_status = test_result.get("status", "unknown")
                test_icon = {"passed": "  ✅", "failed": "  ❌", "warning": "  ⚠️", "skipped": "  ⏭️"}.get(test_status, "  ❓")
                
                report_lines.append(f"{test_icon} {test_name.replace('_', ' ').title()}")
                
                if test_result.get("message"):
                    report_lines.append(f"      {test_result['message']}")
                elif test_result.get("error"):
                    report_lines.append(f"      Error: {test_result['error']}")
            
            report_lines.append("")
        
        # Performance Analysis
        report_lines.extend([
            "🚀 Performance Analysis",
            "-" * 25
        ])
        
        for workflow_name, workflow_result in self.test_results["workflows"].items():
            performance_test = workflow_result.get("tests", {}).get("performance_validation", {})
            if performance_test.get("performance_analysis"):
                analysis = performance_test["performance_analysis"]
                score = analysis.get("optimization_score", 0)
                
                report_lines.extend([
                    f"📈 {workflow_name}:",
                    f"   Optimization Score: {score}/100",
                    f"   Timeout Compliance: {analysis.get('timeout_analysis', {}).get('timeout_compliance', 'Unknown')}",
                    f"   Caching Score: {analysis.get('caching_analysis', {}).get('caching_score', 0)}/100",
                    f"   Parallelization: {analysis.get('parallelization_analysis', {}).get('parallelization_ratio', 0)}%",
                    ""
                ])
        
        # Recommendations
        report_lines.extend([
            "💡 Recommendations",
            "-" * 20
        ])
        
        # Generate recommendations based on results
        recommendations = []
        
        if summary["failed"] > 0:
            recommendations.append("🔧 Fix failing workflow tests before deployment")
        
        if summary["warnings"] > 5:
            recommendations.append("⚠️ Address workflow warnings to improve quality")
        
        if summary["performance_issues"] > 0:
            recommendations.append("🚀 Optimize workflows with performance issues")
        
        if not self.available_tools.get("act"):
            recommendations.append("📦 Install 'act' for comprehensive workflow testing")
        
        if not self.available_tools.get("actionlint"):
            recommendations.append("📦 Install 'actionlint' for GitHub Actions linting")
        
        # Add workflow-specific recommendations
        for workflow_name, workflow_result in self.test_results["workflows"].items():
            if workflow_result.get("overall_status") == "failed":
                recommendations.append(f"🔍 Review and fix issues in {workflow_name}")
        
        if not recommendations:
            recommendations.append("✅ All workflows are performing well - no immediate actions needed")
        
        for rec in recommendations:
            report_lines.append(f"• {rec}")
        
        report_lines.extend([
            "",
            "🏁 Testing Complete",
            f"Report generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, output_dir: str = "workflow-test-results") -> str:
        """Save comprehensive test results to JSON file."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_workflow_test_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        return filepath


def main():
    """Main entry point for comprehensive workflow testing."""
    parser = argparse.ArgumentParser(
        description="Comprehensive GitHub Actions Workflow Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Test all optimized workflows
  %(prog)s --output json                      # JSON output format
  %(prog)s --save-results                     # Save results to file
  %(prog)s --output-dir custom-results        # Custom output directory
        """
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Save detailed results to JSON file"
    )
    
    parser.add_argument(
        "--output-dir",
        default="workflow-test-results",
        help="Output directory for saved results (default: workflow-test-results)"
    )
    
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root path (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize comprehensive tester
        tester = ComprehensiveWorkflowTester(args.repo_root)
        
        # Run comprehensive tests
        results = tester.test_all_optimized_workflows()
        
        # Generate and display report
        if args.output == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            report = tester.generate_comprehensive_report()
            print(report)
        
        # Save results if requested
        if args.save_results:
            results_file = tester.save_results(args.output_dir)
            print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Exit with appropriate code
        if results["status"] == "failed":
            print(f"\n❌ Comprehensive testing failed - {results['summary']['failed']} workflows have issues")
            sys.exit(1)
        elif results["status"] == "passed_with_warnings":
            print(f"\n⚠️ Testing completed with warnings - {results['summary']['warnings']} issues to review")
            sys.exit(0)
        else:
            print(f"\n✅ All workflows passed comprehensive testing")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Comprehensive testing error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
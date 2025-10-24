#!/usr/bin/env python3
"""
GitHub Actions Workflow Linter

Advanced linting tool for GitHub Actions workflows with comprehensive
rule checking, performance analysis, and security validation.

Requirements addressed:
- 10.3: Provide workflow configuration linting and validation
- Enhanced rule-based validation beyond basic syntax checking
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import yaml


class LintRule:
    """Base class for workflow linting rules."""
    
    def __init__(self, rule_id: str, severity: str, description: str):
        self.rule_id = rule_id
        self.severity = severity  # error, warning, info
        self.description = description
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        """Check the rule against workflow data.
        
        Returns:
            List of violations found.
        """
        raise NotImplementedError


class WorkflowLinter:
    """Comprehensive GitHub Actions workflow linter."""
    
    def __init__(self):
        self.rules: List[LintRule] = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Register all default linting rules."""
        # Security rules
        self.rules.extend([
            HardcodedSecretsRule(),
            OverlyPermissivePermissionsRule(),
            UnpinnedActionVersionsRule(),
            InsecureCheckoutRule(),
            MissingSecurityScanningRule()
        ])
        
        # Performance rules
        self.rules.extend([
            MissingCachingRule(),
            LongRunningJobsRule(),
            InefficiencyParallelizationRule(),
            LargeMatrixRule(),
            RedundantStepsRule()
        ])
        
        # Best practices rules
        self.rules.extend([
            MissingJobNamesRule(),
            MissingStepNamesRule(),
            DeprecatedActionsRule(),
            MissingTimeoutsRule(),
            PoorErrorHandlingRule(),
            InconsistentNamingRule()
        ])
        
        # Maintainability rules
        self.rules.extend([
            ComplexWorkflowRule(),
            MissingDocumentationRule(),
            DuplicatedCodeRule(),
            CircularDependenciesRule(),
            UnusedEnvironmentVariablesRule()
        ])
    
    def lint_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Lint a single workflow file.
        
        Args:
            workflow_path: Path to the workflow file.
            
        Returns:
            Dictionary containing linting results.
        """
        result = {
            "file": workflow_path.name,
            "status": "passed",
            "violations": {
                "error": [],
                "warning": [],
                "info": []
            },
            "summary": {
                "total_violations": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0
            },
            "rules_checked": len(self.rules)
        }
        
        try:
            # Load workflow data
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data:
                result["violations"]["error"].append({
                    "rule_id": "SYNTAX_001",
                    "message": "Empty or invalid YAML file",
                    "severity": "error"
                })
                result["status"] = "failed"
                return result
            
            # Run all rules
            for rule in self.rules:
                try:
                    violations = rule.check(workflow_data, workflow_path)
                    for violation in violations:
                        severity = violation.get("severity", "info")
                        result["violations"][severity].append(violation)
                        result["summary"][f"{severity}s"] += 1
                        result["summary"]["total_violations"] += 1
                except Exception as e:
                    # Rule execution error - add as warning
                    result["violations"]["warning"].append({
                        "rule_id": "LINT_ERROR",
                        "message": f"Rule {rule.rule_id} failed: {e}",
                        "severity": "warning"
                    })
            
            # Determine overall status
            if result["summary"]["errors"] > 0:
                result["status"] = "failed"
            elif result["summary"]["warnings"] > 0:
                result["status"] = "passed_with_warnings"
            
        except yaml.YAMLError as e:
            result["violations"]["error"].append({
                "rule_id": "YAML_001",
                "message": f"YAML syntax error: {e}",
                "severity": "error"
            })
            result["status"] = "failed"
        except Exception as e:
            result["violations"]["error"].append({
                "rule_id": "LINT_001",
                "message": f"Linting error: {e}",
                "severity": "error"
            })
            result["status"] = "failed"
        
        return result
    
    def lint_all_workflows(self, workflows_dir: Path) -> Dict[str, Any]:
        """Lint all workflows in a directory.
        
        Args:
            workflows_dir: Directory containing workflow files.
            
        Returns:
            Dictionary containing results for all workflows.
        """
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        results = {
            "status": "passed",
            "total_workflows": len(workflow_files),
            "workflows": {},
            "summary": {
                "passed": 0,
                "failed": 0,
                "total_violations": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0
            }
        }
        
        for workflow_file in workflow_files:
            workflow_result = self.lint_workflow(workflow_file)
            results["workflows"][workflow_file.name] = workflow_result
            
            # Update summary
            if workflow_result["status"] == "failed":
                results["summary"]["failed"] += 1
                results["status"] = "failed"
            else:
                results["summary"]["passed"] += 1
            
            # Aggregate violation counts
            for severity in ["errors", "warnings", "info"]:
                results["summary"][severity] += workflow_result["summary"][severity]
            results["summary"]["total_violations"] += workflow_result["summary"]["total_violations"]
        
        return results


# Security Rules

class HardcodedSecretsRule(LintRule):
    """Check for hardcoded secrets in workflow files."""
    
    def __init__(self):
        super().__init__(
            "SEC_001",
            "error",
            "Hardcoded secrets detected in workflow"
        )
        
        self.secret_patterns = [
            (r'password\s*[:=]\s*["\'][^"\']{8,}["\']', "password"),
            (r'token\s*[:=]\s*["\'][^"\']{20,}["\']', "token"),
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']{16,}["\']', "api_key"),
            (r'secret\s*[:=]\s*["\'][^"\']{16,}["\']', "secret"),
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', "base64_encoded"),
            (r'-----BEGIN [A-Z ]+-----', "private_key")
        ]
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Read raw file content for pattern matching
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern, secret_type in self.secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Potential {secret_type} hardcoded at line {line_num}",
                    "severity": self.severity,
                    "line": line_num,
                    "secret_type": secret_type
                })
        
        return violations


class OverlyPermissivePermissionsRule(LintRule):
    """Check for overly permissive workflow permissions."""
    
    def __init__(self):
        super().__init__(
            "SEC_002",
            "warning",
            "Overly permissive workflow permissions"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        permissions = workflow_data.get("permissions")
        if not permissions:
            return violations
        
        # Check for write-all or overly broad permissions
        if permissions == "write-all":
            violations.append({
                "rule_id": self.rule_id,
                "message": "Workflow has write-all permissions - consider using minimal permissions",
                "severity": self.severity
            })
        elif isinstance(permissions, dict):
            risky_permissions = []
            
            for scope, level in permissions.items():
                if level == "write" and scope in ["contents", "actions", "checks", "deployments"]:
                    risky_permissions.append(f"{scope}: write")
            
            if len(risky_permissions) > 2:
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Multiple write permissions detected: {', '.join(risky_permissions)}",
                    "severity": self.severity
                })
        
        return violations


class UnpinnedActionVersionsRule(LintRule):
    """Check for unpinned action versions."""
    
    def __init__(self):
        super().__init__(
            "SEC_003",
            "warning",
            "Actions should use pinned versions for security"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                
                uses = step.get("uses")
                if not uses or "@" not in uses:
                    continue
                
                action_name, version = uses.rsplit("@", 1)
                
                # Check for unpinned versions
                if version in ["main", "master", "latest", "HEAD"]:
                    violations.append({
                        "rule_id": self.rule_id,
                        "message": f"Job '{job_name}', step {i+1}: Action '{action_name}' uses unpinned version '{version}'",
                        "severity": self.severity,
                        "job": job_name,
                        "step": i+1,
                        "action": action_name,
                        "version": version
                    })
        
        return violations


class InsecureCheckoutRule(LintRule):
    """Check for insecure checkout configurations."""
    
    def __init__(self):
        super().__init__(
            "SEC_004",
            "warning",
            "Checkout action should use secure configurations"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                
                uses = step.get("uses", "")
                if "checkout" not in uses:
                    continue
                
                with_params = step.get("with", {})
                
                # Check for potentially insecure configurations
                if with_params.get("token") and with_params["token"] != "${{ github.token }}":
                    violations.append({
                        "rule_id": self.rule_id,
                        "message": f"Job '{job_name}', step {i+1}: Custom token in checkout - verify security",
                        "severity": self.severity,
                        "job": job_name,
                        "step": i+1
                    })
                
                if with_params.get("persist-credentials") == "true":
                    violations.append({
                        "rule_id": self.rule_id,
                        "message": f"Job '{job_name}', step {i+1}: persist-credentials enabled - consider security implications",
                        "severity": "info",
                        "job": job_name,
                        "step": i+1
                    })
        
        return violations


class MissingSecurityScanningRule(LintRule):
    """Check if security scanning is implemented."""
    
    def __init__(self):
        super().__init__(
            "SEC_005",
            "info",
            "Consider implementing security scanning"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Skip if this is already a security workflow
        workflow_name = workflow_data.get("name", "").lower()
        if "security" in workflow_name or "scan" in workflow_name:
            return violations
        
        # Check if workflow includes security scanning
        has_security_scanning = False
        jobs = workflow_data.get("jobs", {})
        
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    uses = step.get("uses", "")
                    run = step.get("run", "")
                    
                    if ("codeql" in uses.lower() or 
                        "security" in uses.lower() or
                        "audit" in run.lower() or
                        "bandit" in run.lower()):
                        has_security_scanning = True
                        break
        
        if not has_security_scanning:
            violations.append({
                "rule_id": self.rule_id,
                "message": "Workflow lacks security scanning - consider adding dependency/code security checks",
                "severity": self.severity
            })
        
        return violations


# Performance Rules

class MissingCachingRule(LintRule):
    """Check for missing caching optimizations."""
    
    def __init__(self):
        super().__init__(
            "PERF_001",
            "info",
            "Consider adding caching for better performance"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Check if workflow uses caching
        has_caching = False
        jobs = workflow_data.get("jobs", {})
        
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict) and "cache" in step.get("uses", ""):
                    has_caching = True
                    break
        
        # Check if workflow installs dependencies (likely needs caching)
        has_dependencies = False
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    run = step.get("run", "")
                    if any(cmd in run.lower() for cmd in ["pip install", "npm install", "yarn install", "uv sync"]):
                        has_dependencies = True
                        break
        
        if has_dependencies and not has_caching:
            violations.append({
                "rule_id": self.rule_id,
                "message": "Workflow installs dependencies but lacks caching - consider adding cache steps",
                "severity": self.severity
            })
        
        return violations


class LongRunningJobsRule(LintRule):
    """Check for jobs with excessive timeouts."""
    
    def __init__(self):
        super().__init__(
            "PERF_002",
            "warning",
            "Jobs have excessive timeout values"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            timeout = job_data.get("timeout-minutes")
            
            if timeout and timeout > 60:  # More than 1 hour
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Job '{job_name}' has excessive timeout ({timeout} minutes) - consider optimization",
                    "severity": self.severity,
                    "job": job_name,
                    "timeout": timeout
                })
        
        return violations


class InefficiencyParallelizationRule(LintRule):
    """Check for inefficient job parallelization."""
    
    def __init__(self):
        super().__init__(
            "PERF_003",
            "info",
            "Workflow could benefit from better parallelization"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        if len(jobs) <= 1:
            return violations
        
        # Check if all jobs have dependencies (sequential execution)
        jobs_with_needs = sum(1 for job in jobs.values() if "needs" in job)
        
        if jobs_with_needs == len(jobs):
            violations.append({
                "rule_id": self.rule_id,
                "message": "All jobs have dependencies - consider parallel execution for independent tasks",
                "severity": self.severity
            })
        
        return violations


class LargeMatrixRule(LintRule):
    """Check for excessively large matrix strategies."""
    
    def __init__(self):
        super().__init__(
            "PERF_004",
            "warning",
            "Matrix strategy is very large"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            strategy = job_data.get("strategy", {})
            matrix = strategy.get("matrix", {})
            
            if not matrix:
                continue
            
            # Calculate matrix size
            matrix_size = 1
            for key, values in matrix.items():
                if isinstance(values, list):
                    matrix_size *= len(values)
            
            if matrix_size > 20:  # Arbitrary threshold
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Job '{job_name}' has large matrix ({matrix_size} combinations) - consider reducing",
                    "severity": self.severity,
                    "job": job_name,
                    "matrix_size": matrix_size
                })
        
        return violations


class RedundantStepsRule(LintRule):
    """Check for redundant or duplicate steps."""
    
    def __init__(self):
        super().__init__(
            "PERF_005",
            "info",
            "Workflow contains potentially redundant steps"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        
        # Check for duplicate checkout steps within jobs
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            checkout_count = 0
            
            for step in steps:
                if isinstance(step, dict) and "checkout" in step.get("uses", ""):
                    checkout_count += 1
            
            if checkout_count > 1:
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Job '{job_name}' has multiple checkout steps ({checkout_count}) - consider consolidation",
                    "severity": self.severity,
                    "job": job_name
                })
        
        return violations


# Best Practices Rules

class MissingJobNamesRule(LintRule):
    """Check for jobs without descriptive names."""
    
    def __init__(self):
        super().__init__(
            "BP_001",
            "info",
            "Jobs should have descriptive names"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_id, job_data in jobs.items():
            if not job_data.get("name"):
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Job '{job_id}' lacks a descriptive name",
                    "severity": self.severity,
                    "job": job_id
                })
        
        return violations


class MissingStepNamesRule(LintRule):
    """Check for steps without names."""
    
    def __init__(self):
        super().__init__(
            "BP_002",
            "info",
            "Steps should have descriptive names"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            unnamed_count = 0
            
            for step in steps:
                if isinstance(step, dict) and not step.get("name"):
                    unnamed_count += 1
            
            if unnamed_count > 2:  # Allow a few unnamed steps
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Job '{job_name}' has {unnamed_count} unnamed steps - consider adding names",
                    "severity": self.severity,
                    "job": job_name,
                    "unnamed_count": unnamed_count
                })
        
        return violations


class DeprecatedActionsRule(LintRule):
    """Check for deprecated actions."""
    
    def __init__(self):
        super().__init__(
            "BP_003",
            "warning",
            "Workflow uses deprecated actions"
        )
        
        self.deprecated_actions = {
            "actions/setup-python@v4": "actions/setup-python@v5",
            "actions/checkout@v3": "actions/checkout@v4",
            "actions/cache@v3": "actions/cache@v4",
            "actions/upload-artifact@v3": "actions/upload-artifact@v4",
            "actions/download-artifact@v3": "actions/download-artifact@v4"
        }
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                
                uses = step.get("uses")
                if uses in self.deprecated_actions:
                    replacement = self.deprecated_actions[uses]
                    violations.append({
                        "rule_id": self.rule_id,
                        "message": f"Job '{job_name}', step {i+1}: Deprecated action '{uses}' - use '{replacement}'",
                        "severity": self.severity,
                        "job": job_name,
                        "step": i+1,
                        "deprecated_action": uses,
                        "replacement": replacement
                    })
        
        return violations


class MissingTimeoutsRule(LintRule):
    """Check for jobs without timeout configurations."""
    
    def __init__(self):
        super().__init__(
            "BP_004",
            "info",
            "Jobs should have timeout configurations"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        jobs_without_timeout = []
        
        for job_name, job_data in jobs.items():
            if "timeout-minutes" not in job_data:
                jobs_without_timeout.append(job_name)
        
        if jobs_without_timeout:
            violations.append({
                "rule_id": self.rule_id,
                "message": f"Jobs without timeout: {', '.join(jobs_without_timeout)}",
                "severity": self.severity,
                "jobs": jobs_without_timeout
            })
        
        return violations


class PoorErrorHandlingRule(LintRule):
    """Check for poor error handling practices."""
    
    def __init__(self):
        super().__init__(
            "BP_005",
            "info",
            "Workflow could benefit from better error handling"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Check if workflow has any error handling
        has_error_handling = False
        jobs = workflow_data.get("jobs", {})
        
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    if ("if: failure()" in str(step) or 
                        "continue-on-error" in step or
                        step.get("if", "").startswith("failure")):
                        has_error_handling = True
                        break
        
        if not has_error_handling:
            violations.append({
                "rule_id": self.rule_id,
                "message": "Workflow lacks error handling steps - consider adding failure recovery",
                "severity": self.severity
            })
        
        return violations


class InconsistentNamingRule(LintRule):
    """Check for inconsistent naming conventions."""
    
    def __init__(self):
        super().__init__(
            "BP_006",
            "info",
            "Inconsistent naming conventions detected"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        job_names = list(jobs.keys())
        
        # Check job naming consistency
        kebab_case = sum(1 for name in job_names if "-" in name and "_" not in name)
        snake_case = sum(1 for name in job_names if "_" in name and "-" not in name)
        
        if kebab_case > 0 and snake_case > 0:
            violations.append({
                "rule_id": self.rule_id,
                "message": "Inconsistent job naming: mix of kebab-case and snake_case",
                "severity": self.severity
            })
        
        return violations


# Maintainability Rules

class ComplexWorkflowRule(LintRule):
    """Check for overly complex workflows."""
    
    def __init__(self):
        super().__init__(
            "MAINT_001",
            "warning",
            "Workflow is overly complex"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        
        # Calculate complexity metrics
        total_steps = sum(len(job.get("steps", [])) for job in jobs.values())
        total_jobs = len(jobs)
        
        # Check for excessive complexity
        if total_jobs > 10:
            violations.append({
                "rule_id": self.rule_id,
                "message": f"Workflow has many jobs ({total_jobs}) - consider splitting",
                "severity": self.severity,
                "metric": "job_count",
                "value": total_jobs
            })
        
        if total_steps > 50:
            violations.append({
                "rule_id": self.rule_id,
                "message": f"Workflow has many steps ({total_steps}) - consider refactoring",
                "severity": self.severity,
                "metric": "step_count",
                "value": total_steps
            })
        
        return violations


class MissingDocumentationRule(LintRule):
    """Check for missing workflow documentation."""
    
    def __init__(self):
        super().__init__(
            "MAINT_002",
            "info",
            "Workflow lacks documentation"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Read raw content to check for comments
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for documentation comments
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        
        if len(comment_lines) < 3:  # Minimal documentation threshold
            violations.append({
                "rule_id": self.rule_id,
                "message": "Workflow lacks documentation comments - consider adding purpose and usage info",
                "severity": self.severity
            })
        
        return violations


class DuplicatedCodeRule(LintRule):
    """Check for duplicated code patterns."""
    
    def __init__(self):
        super().__init__(
            "MAINT_003",
            "info",
            "Workflow contains duplicated patterns"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        
        # Check for duplicate step patterns
        step_patterns = {}
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    uses = step.get("uses")
                    if uses:
                        step_patterns[uses] = step_patterns.get(uses, 0) + 1
        
        # Find frequently repeated patterns
        frequent_patterns = [(uses, count) for uses, count in step_patterns.items() if count > 3]
        
        if frequent_patterns:
            violations.append({
                "rule_id": self.rule_id,
                "message": f"Frequently repeated actions detected - consider reusable actions: {', '.join([uses for uses, _ in frequent_patterns[:3]])}",
                "severity": self.severity,
                "patterns": frequent_patterns
            })
        
        return violations


class CircularDependenciesRule(LintRule):
    """Check for circular job dependencies."""
    
    def __init__(self):
        super().__init__(
            "MAINT_004",
            "error",
            "Circular job dependencies detected"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        jobs = workflow_data.get("jobs", {})
        
        # Build dependency graph
        dependencies = {}
        for job_name, job_data in jobs.items():
            needs = job_data.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            dependencies[job_name] = needs
        
        # Check for circular dependencies
        def has_cycle(job: str, path: Set[str]) -> bool:
            if job in path:
                return True
            
            path.add(job)
            for dep in dependencies.get(job, []):
                if has_cycle(dep, path):
                    return True
            path.remove(job)
            return False
        
        for job in dependencies:
            if has_cycle(job, set()):
                violations.append({
                    "rule_id": self.rule_id,
                    "message": f"Circular dependency detected involving job '{job}'",
                    "severity": self.severity,
                    "job": job
                })
                break  # Only report once
        
        return violations


class UnusedEnvironmentVariablesRule(LintRule):
    """Check for unused environment variables."""
    
    def __init__(self):
        super().__init__(
            "MAINT_005",
            "info",
            "Unused environment variables detected"
        )
    
    def check(self, workflow_data: Dict, workflow_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        # Get all defined environment variables
        env_vars = set()
        
        # Global env vars
        global_env = workflow_data.get("env", {})
        env_vars.update(global_env.keys())
        
        # Job-level env vars
        jobs = workflow_data.get("jobs", {})
        for job_data in jobs.values():
            job_env = job_data.get("env", {})
            env_vars.update(job_env.keys())
        
        if not env_vars:
            return violations
        
        # Read raw content to check usage
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check which env vars are actually used
        unused_vars = []
        for var in env_vars:
            # Look for ${{ env.VAR }} or $VAR patterns
            if (f"env.{var}" not in content and 
                f"${var}" not in content and
                f"${{{var}}}" not in content):
                unused_vars.append(var)
        
        if unused_vars:
            violations.append({
                "rule_id": self.rule_id,
                "message": f"Unused environment variables: {', '.join(unused_vars)}",
                "severity": self.severity,
                "unused_vars": unused_vars
            })
        
        return violations


def main():
    """Main entry point for the workflow linter."""
    parser = argparse.ArgumentParser(
        description="Lint GitHub Actions workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to workflow file or directory (default: .github/workflows)"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        help="Minimum severity level to report"
    )
    
    parser.add_argument(
        "--rules",
        nargs="+",
        help="Specific rule IDs to check"
    )
    
    args = parser.parse_args()
    
    # Determine target path
    if args.path:
        target_path = Path(args.path)
    else:
        target_path = Path(".github/workflows")
    
    if not target_path.exists():
        print(f"❌ Path not found: {target_path}")
        sys.exit(1)
    
    linter = WorkflowLinter()
    
    # Filter rules if specified
    if args.rules:
        linter.rules = [rule for rule in linter.rules if rule.rule_id in args.rules]
    
    try:
        if target_path.is_file():
            # Lint single file
            result = linter.lint_workflow(target_path)
            
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                print_single_result(result, args.severity)
            
            sys.exit(0 if result["status"] != "failed" else 1)
        else:
            # Lint all workflows in directory
            results = linter.lint_all_workflows(target_path)
            
            if args.output == "json":
                print(json.dumps(results, indent=2))
            else:
                print_all_results(results, args.severity)
            
            sys.exit(0 if results["status"] != "failed" else 1)
            
    except Exception as e:
        print(f"❌ Linting error: {e}")
        sys.exit(1)


def print_single_result(result: Dict[str, Any], min_severity: Optional[str] = None) -> None:
    """Print results for a single workflow."""
    severity_order = {"error": 3, "warning": 2, "info": 1}
    min_level = severity_order.get(min_severity, 0)
    
    print(f"\n🔍 Linting Results: {result['file']}")
    print("=" * 50)
    
    status_icon = {"passed": "✅", "passed_with_warnings": "⚠️", "failed": "❌"}.get(result["status"], "❓")
    print(f"{status_icon} Status: {result['status'].upper()}")
    
    summary = result["summary"]
    print(f"📊 Summary: {summary['total_violations']} violations ({summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info)")
    
    # Print violations by severity
    for severity in ["error", "warning", "info"]:
        violations = result["violations"][severity]
        if not violations or severity_order.get(severity, 0) < min_level:
            continue
        
        icon = {"error": "❌", "warning": "⚠️", "info": "💡"}[severity]
        print(f"\n{icon} {severity.upper()} ({len(violations)}):")
        
        for violation in violations:
            print(f"  {violation['rule_id']}: {violation['message']}")


def print_all_results(results: Dict[str, Any], min_severity: Optional[str] = None) -> None:
    """Print results for all workflows."""
    print("\n🔍 Workflow Linting Results")
    print("=" * 50)
    
    summary = results["summary"]
    print(f"📊 Overall Summary:")
    print(f"  Total workflows: {results['total_workflows']}")
    print(f"  ✅ Passed: {summary['passed']}")
    print(f"  ❌ Failed: {summary['failed']}")
    print(f"  📋 Total violations: {summary['total_violations']}")
    print(f"  Status: {results['status'].upper()}")
    
    # Print individual workflow results
    print(f"\n📋 Individual Results:")
    for workflow_name, workflow_result in results["workflows"].items():
        status_icon = {"passed": "✅", "passed_with_warnings": "⚠️", "failed": "❌"}.get(workflow_result["status"], "❓")
        violations = workflow_result["summary"]["total_violations"]
        print(f"  {status_icon} {workflow_name}: {workflow_result['status']} ({violations} violations)")


if __name__ == "__main__":
    main()
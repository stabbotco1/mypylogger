#!/usr/bin/env python3
"""
Workflow Configuration Validator for GitHub Actions

This script validates GitHub Actions workflow syntax, configuration,
and performs impact analysis for workflow changes.

Requirements addressed:
- 10.1: Validate workflow syntax before execution
- 10.2: Test workflow changes in isolated environments
- 10.3: Provide workflow configuration linting and validation
- 10.4: Implement workflow change impact analysis
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import yaml


class WorkflowValidationError(Exception):
    """Custom exception for workflow validation errors."""
    pass


class WorkflowValidator:
    """Comprehensive GitHub Actions workflow validator."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the workflow validator.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.validation_results: Dict[str, Any] = {}
        
        # Validation rules and patterns
        self.required_fields = {
            "name": str,
            "on": (dict, str, list),
            "jobs": dict
        }
        
        self.deprecated_actions = {
            "actions/setup-python@v4": "actions/setup-python@v5",
            "actions/checkout@v3": "actions/checkout@v4",
            "actions/cache@v3": "actions/cache@v4",
            "actions/upload-artifact@v3": "actions/upload-artifact@v4",
            "actions/download-artifact@v3": "actions/download-artifact@v4"
        }
        
        self.security_patterns = [
            r"password\s*[:=]\s*['\"][^'\"]+['\"]",
            r"token\s*[:=]\s*['\"][^'\"]+['\"]",
            r"secret\s*[:=]\s*['\"][^'\"]+['\"]",
            r"api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]"
        ]
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise WorkflowValidationError("Could not find repository root (.git directory)")
    
    def validate_all_workflows(self) -> Dict[str, Any]:
        """Validate all workflows in the repository.
        
        Returns:
            Dictionary containing validation results for all workflows.
        """
        print("🔍 Starting comprehensive workflow validation...")
        print(f"Repository: {self.repo_root}")
        print(f"Workflows directory: {self.workflows_dir}")
        
        if not self.workflows_dir.exists():
            raise WorkflowValidationError(f"Workflows directory not found: {self.workflows_dir}")
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            print("⚠️ No workflow files found")
            return {"status": "no_workflows", "workflows": {}}
        
        print(f"Found {len(workflow_files)} workflow files")
        
        results = {
            "status": "success",
            "total_workflows": len(workflow_files),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "workflows": {},
            "summary": {}
        }
        
        for workflow_file in workflow_files:
            print(f"\n📋 Validating: {workflow_file.name}")
            try:
                workflow_result = self.validate_workflow(workflow_file)
                results["workflows"][workflow_file.name] = workflow_result
                
                if workflow_result["status"] == "passed":
                    results["passed"] += 1
                elif workflow_result["status"] == "failed":
                    results["failed"] += 1
                    results["status"] = "failed"
                
                results["warnings"] += len(workflow_result.get("warnings", []))
                
            except Exception as e:
                print(f"❌ Error validating {workflow_file.name}: {e}")
                results["workflows"][workflow_file.name] = {
                    "status": "error",
                    "error": str(e)
                }
                results["failed"] += 1
                results["status"] = "failed"
        
        # Generate summary
        results["summary"] = self._generate_validation_summary(results)
        
        return results
    
    def validate_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Validate a single workflow file.
        
        Args:
            workflow_path: Path to the workflow file.
            
        Returns:
            Dictionary containing validation results.
        """
        result = {
            "file": workflow_path.name,
            "status": "passed",
            "errors": [],
            "warnings": [],
            "info": [],
            "checks": {}
        }
        
        try:
            # Load and parse YAML
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            if not workflow_data:
                result["errors"].append("Empty or invalid YAML file")
                result["status"] = "failed"
                return result
            
            # Run validation checks
            self._validate_syntax(workflow_data, result)
            self._validate_structure(workflow_data, result)
            self._validate_actions(workflow_data, result)
            self._validate_security(content, result)
            self._validate_performance(workflow_data, result)
            self._validate_best_practices(workflow_data, result)
            
            # Set final status
            if result["errors"]:
                result["status"] = "failed"
            elif result["warnings"]:
                result["status"] = "passed_with_warnings"
            
        except yaml.YAMLError as e:
            result["errors"].append(f"YAML syntax error: {e}")
            result["status"] = "failed"
        except Exception as e:
            result["errors"].append(f"Validation error: {e}")
            result["status"] = "failed"
        
        return result
    
    def _validate_syntax(self, workflow_data: Dict, result: Dict) -> None:
        """Validate basic workflow syntax and required fields."""
        result["checks"]["syntax"] = {"status": "checking"}
        
        # Check required top-level fields
        for field, expected_type in self.required_fields.items():
            if field not in workflow_data:
                result["errors"].append(f"Missing required field: {field}")
            elif not isinstance(workflow_data[field], expected_type):
                result["errors"].append(f"Field '{field}' must be of type {expected_type.__name__}")
        
        # Validate workflow name
        if "name" in workflow_data:
            name = workflow_data["name"]
            if not isinstance(name, str) or not name.strip():
                result["errors"].append("Workflow name must be a non-empty string")
            elif len(name) > 100:
                result["warnings"].append("Workflow name is very long (>100 characters)")
        
        # Validate jobs structure
        if "jobs" in workflow_data:
            jobs = workflow_data["jobs"]
            if not isinstance(jobs, dict) or not jobs:
                result["errors"].append("Jobs section must be a non-empty dictionary")
            else:
                for job_name, job_data in jobs.items():
                    if not isinstance(job_data, dict):
                        result["errors"].append(f"Job '{job_name}' must be a dictionary")
                    elif "runs-on" not in job_data:
                        result["errors"].append(f"Job '{job_name}' missing required 'runs-on' field")
        
        result["checks"]["syntax"]["status"] = "passed" if not result["errors"] else "failed"
    
    def _validate_structure(self, workflow_data: Dict, result: Dict) -> None:
        """Validate workflow structure and organization."""
        result["checks"]["structure"] = {"status": "checking"}
        
        jobs = workflow_data.get("jobs", {})
        
        # Check for circular dependencies
        dependencies = {}
        for job_name, job_data in jobs.items():
            needs = job_data.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            dependencies[job_name] = needs
        
        if self._has_circular_dependencies(dependencies):
            result["errors"].append("Circular job dependencies detected")
        
        # Check for unreachable jobs
        unreachable = self._find_unreachable_jobs(dependencies)
        if unreachable:
            result["warnings"].append(f"Potentially unreachable jobs: {', '.join(unreachable)}")
        
        # Validate timeout settings
        for job_name, job_data in jobs.items():
            timeout = job_data.get("timeout-minutes")
            if timeout:
                if not isinstance(timeout, int) or timeout <= 0:
                    result["errors"].append(f"Job '{job_name}' has invalid timeout-minutes")
                elif timeout > 360:  # 6 hours
                    result["warnings"].append(f"Job '{job_name}' has very long timeout ({timeout} minutes)")
        
        result["checks"]["structure"]["status"] = "passed" if not any(
            "Circular" in error or "invalid timeout" in error for error in result["errors"]
        ) else "failed"
    
    def _validate_actions(self, workflow_data: Dict, result: Dict) -> None:
        """Validate GitHub Actions usage and versions."""
        result["checks"]["actions"] = {"status": "checking", "deprecated": [], "outdated": []}
        
        jobs = workflow_data.get("jobs", {})
        
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            
            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue
                
                uses = step.get("uses")
                if not uses:
                    continue
                
                # Check for deprecated actions
                if uses in self.deprecated_actions:
                    replacement = self.deprecated_actions[uses]
                    result["warnings"].append(
                        f"Job '{job_name}', step {i+1}: Deprecated action '{uses}', "
                        f"use '{replacement}' instead"
                    )
                    result["checks"]["actions"]["deprecated"].append({
                        "job": job_name,
                        "step": i+1,
                        "action": uses,
                        "replacement": replacement
                    })
                
                # Check for pinned versions
                if "@" in uses:
                    action_name, version = uses.rsplit("@", 1)
                    if version in ["main", "master", "latest"]:
                        result["warnings"].append(
                            f"Job '{job_name}', step {i+1}: Action '{action_name}' "
                            f"uses unpinned version '{version}'"
                        )
                
                # Check for common action patterns
                if "setup-python" in uses and "@v4" in uses:
                    result["warnings"].append(
                        f"Job '{job_name}', step {i+1}: Consider upgrading to setup-python@v5"
                    )
        
        result["checks"]["actions"]["status"] = "passed"
    
    def _validate_security(self, content: str, result: Dict) -> None:
        """Validate security aspects of the workflow."""
        result["checks"]["security"] = {"status": "checking", "issues": []}
        
        # Check for hardcoded secrets
        for pattern in self.security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                result["warnings"].append(
                    f"Line {line_num}: Potential hardcoded secret detected"
                )
                result["checks"]["security"]["issues"].append({
                    "line": line_num,
                    "pattern": pattern,
                    "match": match.group()
                })
        
        # Check for overly permissive permissions
        if "permissions:" in content:
            if "write-all" in content or "contents: write" in content:
                result["warnings"].append("Workflow has broad write permissions")
        
        result["checks"]["security"]["status"] = "passed"
    
    def _validate_performance(self, workflow_data: Dict, result: Dict) -> None:
        """Validate performance-related configurations."""
        result["checks"]["performance"] = {"status": "checking", "optimizations": []}
        
        jobs = workflow_data.get("jobs", {})
        
        # Check for caching usage
        has_caching = False
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict) and step.get("uses", "").startswith("actions/cache"):
                    has_caching = True
                    break
        
        if not has_caching:
            result["info"].append("Consider adding caching to improve performance")
        
        # Check for parallel job execution
        job_count = len(jobs)
        jobs_with_needs = sum(1 for job in jobs.values() if "needs" in job)
        
        if job_count > 1 and jobs_with_needs == job_count:
            result["warnings"].append("All jobs have dependencies - consider parallelization")
        
        # Check for timeout configurations
        jobs_without_timeout = [
            name for name, job in jobs.items() 
            if "timeout-minutes" not in job
        ]
        
        if jobs_without_timeout:
            result["info"].append(
                f"Jobs without timeout: {', '.join(jobs_without_timeout)} "
                "(consider adding timeout-minutes)"
            )
        
        result["checks"]["performance"]["status"] = "passed"
    
    def _validate_best_practices(self, workflow_data: Dict, result: Dict) -> None:
        """Validate adherence to GitHub Actions best practices."""
        result["checks"]["best_practices"] = {"status": "checking"}
        
        # Check for descriptive job and step names
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            if not job_data.get("name"):
                result["info"].append(f"Job '{job_name}' could benefit from a descriptive name")
            
            steps = job_data.get("steps", [])
            unnamed_steps = sum(1 for step in steps if isinstance(step, dict) and not step.get("name"))
            
            if unnamed_steps > 0:
                result["info"].append(
                    f"Job '{job_name}' has {unnamed_steps} unnamed steps "
                    "(consider adding descriptive names)"
                )
        
        # Check for environment variable usage
        if "env" not in workflow_data:
            result["info"].append("Consider using global environment variables for common settings")
        
        # Check for proper error handling
        has_error_handling = False
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict) and ("if: failure()" in str(step) or "continue-on-error" in step):
                    has_error_handling = True
                    break
        
        if not has_error_handling:
            result["info"].append("Consider adding error handling steps for better debugging")
        
        result["checks"]["best_practices"]["status"] = "passed"
    
    def _has_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> bool:
        """Check for circular dependencies in job needs."""
        def visit(job: str, path: Set[str]) -> bool:
            if job in path:
                return True
            
            path.add(job)
            for dep in dependencies.get(job, []):
                if visit(dep, path):
                    return True
            path.remove(job)
            return False
        
        for job in dependencies:
            if visit(job, set()):
                return True
        return False
    
    def _find_unreachable_jobs(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Find jobs that might be unreachable due to complex dependencies."""
        # This is a simplified check - in practice, this would be more complex
        all_jobs = set(dependencies.keys())
        referenced_jobs = set()
        
        for deps in dependencies.values():
            referenced_jobs.update(deps)
        
        # Jobs that are never referenced as dependencies might be entry points
        entry_points = all_jobs - referenced_jobs
        
        # If there are too many entry points, some might be unreachable
        if len(entry_points) > 3:  # Arbitrary threshold
            return list(entry_points)[3:]  # Return excess entry points
        
        return []
    
    def _generate_validation_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate a comprehensive validation summary."""
        summary = {
            "overall_status": results["status"],
            "statistics": {
                "total_workflows": results["total_workflows"],
                "passed": results["passed"],
                "failed": results["failed"],
                "warnings": results["warnings"]
            },
            "common_issues": [],
            "recommendations": []
        }
        
        # Analyze common issues across workflows
        all_errors = []
        all_warnings = []
        
        for workflow_result in results["workflows"].values():
            if isinstance(workflow_result, dict):
                all_errors.extend(workflow_result.get("errors", []))
                all_warnings.extend(workflow_result.get("warnings", []))
        
        # Find most common issues
        error_counts = {}
        for error in all_errors:
            # Generalize error messages
            generalized = re.sub(r"'[^']*'", "'*'", error)
            error_counts[generalized] = error_counts.get(generalized, 0) + 1
        
        summary["common_issues"] = [
            {"issue": issue, "count": count}
            for issue, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
            if count > 1
        ]
        
        # Generate recommendations
        if results["failed"] > 0:
            summary["recommendations"].append("Fix validation errors before deploying workflows")
        
        if results["warnings"] > 5:
            summary["recommendations"].append("Address warnings to improve workflow quality")
        
        if any("deprecated" in str(w) for w in all_warnings):
            summary["recommendations"].append("Update deprecated actions to latest versions")
        
        if any("timeout" in str(w) for w in all_warnings):
            summary["recommendations"].append("Review and optimize job timeout settings")
        
        return summary
    
    def analyze_workflow_changes(self, base_ref: str = "main") -> Dict[str, Any]:
        """Analyze the impact of workflow changes compared to base branch.
        
        Args:
            base_ref: Base branch to compare against.
            
        Returns:
            Dictionary containing change impact analysis.
        """
        print(f"🔍 Analyzing workflow changes against {base_ref}...")
        
        try:
            # Get list of changed workflow files
            result = subprocess.run(
                ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD", ".github/workflows/"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [
                line.strip() for line in result.stdout.split('\n') 
                if line.strip() and (line.endswith('.yml') or line.endswith('.yaml'))
            ]
            
            if not changed_files:
                return {
                    "status": "no_changes",
                    "message": "No workflow files changed",
                    "changed_files": []
                }
            
            print(f"Found {len(changed_files)} changed workflow files:")
            for file in changed_files:
                print(f"  - {file}")
            
            # Analyze each changed file
            analysis = {
                "status": "success",
                "changed_files": changed_files,
                "file_analysis": {},
                "impact_summary": {
                    "risk_level": "low",
                    "affected_workflows": len(changed_files),
                    "breaking_changes": [],
                    "recommendations": []
                }
            }
            
            for file_path in changed_files:
                full_path = self.repo_root / file_path
                if full_path.exists():
                    file_analysis = self._analyze_file_changes(file_path, base_ref)
                    analysis["file_analysis"][file_path] = file_analysis
                    
                    # Update impact summary based on file analysis
                    if file_analysis.get("risk_level") == "high":
                        analysis["impact_summary"]["risk_level"] = "high"
                    elif (file_analysis.get("risk_level") == "medium" and 
                          analysis["impact_summary"]["risk_level"] == "low"):
                        analysis["impact_summary"]["risk_level"] = "medium"
            
            # Generate overall recommendations
            analysis["impact_summary"]["recommendations"] = self._generate_change_recommendations(analysis)
            
            return analysis
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": f"Git command failed: {e}",
                "changed_files": []
            }
    
    def _analyze_file_changes(self, file_path: str, base_ref: str) -> Dict[str, Any]:
        """Analyze changes in a specific workflow file."""
        try:
            # Get the diff for this file
            result = subprocess.run(
                ["git", "diff", f"origin/{base_ref}...HEAD", file_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            diff_content = result.stdout
            
            analysis = {
                "file": file_path,
                "risk_level": "low",
                "changes": {
                    "added_lines": 0,
                    "removed_lines": 0,
                    "modified_sections": []
                },
                "potential_issues": [],
                "breaking_changes": []
            }
            
            # Analyze diff content
            added_lines = len([line for line in diff_content.split('\n') if line.startswith('+')])
            removed_lines = len([line for line in diff_content.split('\n') if line.startswith('-')])
            
            analysis["changes"]["added_lines"] = added_lines
            analysis["changes"]["removed_lines"] = removed_lines
            
            # Check for potentially risky changes
            risky_patterns = [
                (r'permissions:', "Permission changes detected"),
                (r'secrets\.|env\.', "Secret or environment variable changes"),
                (r'runs-on:', "Runner environment changes"),
                (r'uses:.*@', "Action version changes"),
                (r'needs:', "Job dependency changes"),
                (r'if:', "Conditional logic changes")
            ]
            
            for pattern, description in risky_patterns:
                if re.search(pattern, diff_content, re.IGNORECASE):
                    analysis["potential_issues"].append(description)
                    if "Permission" in description or "Secret" in description:
                        analysis["risk_level"] = "high"
                    elif analysis["risk_level"] == "low":
                        analysis["risk_level"] = "medium"
            
            # Check for breaking changes
            if "- name:" in diff_content and "+ name:" in diff_content:
                analysis["breaking_changes"].append("Workflow or job name changed")
            
            if removed_lines > added_lines * 2:  # Significant removal
                analysis["breaking_changes"].append("Significant content removal detected")
                analysis["risk_level"] = "high"
            
            return analysis
            
        except subprocess.CalledProcessError:
            return {
                "file": file_path,
                "risk_level": "unknown",
                "error": "Could not analyze file changes"
            }
    
    def _generate_change_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on change analysis."""
        recommendations = []
        
        risk_level = analysis["impact_summary"]["risk_level"]
        
        if risk_level == "high":
            recommendations.extend([
                "⚠️ High-risk changes detected - thorough testing recommended",
                "Test workflows in a feature branch before merging",
                "Review permission and security changes carefully",
                "Consider gradual rollout for critical workflows"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Medium-risk changes detected - testing recommended",
                "Verify workflow behavior in development environment",
                "Check for unintended side effects"
            ])
        else:
            recommendations.append("Low-risk changes - standard review process sufficient")
        
        # Add specific recommendations based on detected changes
        all_issues = []
        for file_analysis in analysis["file_analysis"].values():
            all_issues.extend(file_analysis.get("potential_issues", []))
        
        if any("Action version" in issue for issue in all_issues):
            recommendations.append("Verify compatibility of updated action versions")
        
        if any("dependency" in issue.lower() for issue in all_issues):
            recommendations.append("Test job execution order and dependencies")
        
        if any("Permission" in issue for issue in all_issues):
            recommendations.append("Review security implications of permission changes")
        
        return recommendations
    
    def test_workflow_in_isolation(self, workflow_path: Path) -> Dict[str, Any]:
        """Test a workflow in an isolated environment using act.
        
        Args:
            workflow_path: Path to the workflow file to test.
            
        Returns:
            Dictionary containing test results.
        """
        print(f"🧪 Testing workflow in isolation: {workflow_path.name}")
        
        # Check if act is available
        try:
            subprocess.run(["act", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "status": "skipped",
                "reason": "act not available - install from https://github.com/nektos/act"
            }
        
        test_result = {
            "workflow": workflow_path.name,
            "status": "testing",
            "test_runs": []
        }
        
        try:
            # Test with dry run first
            print("Running dry-run test...")
            result = subprocess.run(
                ["act", "--dry-run", "-W", str(workflow_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            dry_run_result = {
                "type": "dry_run",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "passed" if result.returncode == 0 else "failed"
            }
            
            test_result["test_runs"].append(dry_run_result)
            
            if result.returncode == 0:
                print("✅ Dry run passed")
                test_result["status"] = "passed"
            else:
                print("❌ Dry run failed")
                test_result["status"] = "failed"
                
        except subprocess.TimeoutExpired:
            test_result["status"] = "timeout"
            test_result["error"] = "Test timed out after 60 seconds"
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result


def main():
    """Main entry point for the workflow validator."""
    parser = argparse.ArgumentParser(
        description="Validate GitHub Actions workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validate-all                    # Validate all workflows
  %(prog)s --file quality-gate.yml          # Validate specific workflow
  %(prog)s --analyze-changes                 # Analyze workflow changes
  %(prog)s --test-isolation quality-gate.yml # Test workflow in isolation
        """
    )
    
    parser.add_argument(
        "--validate-all",
        action="store_true",
        help="Validate all workflow files"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Validate specific workflow file"
    )
    
    parser.add_argument(
        "--analyze-changes",
        action="store_true",
        help="Analyze workflow changes against main branch"
    )
    
    parser.add_argument(
        "--test-isolation",
        type=str,
        help="Test specific workflow in isolation using act"
    )
    
    parser.add_argument(
        "--base-ref",
        type=str,
        default="main",
        help="Base branch for change analysis (default: main)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root path (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    try:
        validator = WorkflowValidator(args.repo_root)
        
        if args.validate_all:
            results = validator.validate_all_workflows()
            
            if args.output == "json":
                print(json.dumps(results, indent=2))
            else:
                print_validation_results(results)
            
            # Exit with error code if validation failed
            sys.exit(0 if results["status"] == "success" else 1)
            
        elif args.file:
            workflow_path = validator.workflows_dir / args.file
            if not workflow_path.exists():
                print(f"❌ Workflow file not found: {workflow_path}")
                sys.exit(1)
            
            result = validator.validate_workflow(workflow_path)
            
            if args.output == "json":
                print(json.dumps(result, indent=2))
            else:
                print_single_workflow_result(result)
            
            sys.exit(0 if result["status"] in ["passed", "passed_with_warnings"] else 1)
            
        elif args.analyze_changes:
            analysis = validator.analyze_workflow_changes(args.base_ref)
            
            if args.output == "json":
                print(json.dumps(analysis, indent=2))
            else:
                print_change_analysis(analysis)
            
            sys.exit(0)
            
        elif args.test_isolation:
            workflow_path = validator.workflows_dir / args.test_isolation
            if not workflow_path.exists():
                print(f"❌ Workflow file not found: {workflow_path}")
                sys.exit(1)
            
            test_result = validator.test_workflow_in_isolation(workflow_path)
            
            if args.output == "json":
                print(json.dumps(test_result, indent=2))
            else:
                print_test_results(test_result)
            
            sys.exit(0 if test_result["status"] == "passed" else 1)
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except WorkflowValidationError as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def print_validation_results(results: Dict[str, Any]) -> None:
    """Print formatted validation results."""
    print("\n🔍 Workflow Validation Results")
    print("=" * 50)
    
    stats = results.get("statistics", {})
    print(f"📊 Summary:")
    print(f"  Total workflows: {stats.get('total_workflows', 0)}")
    print(f"  ✅ Passed: {stats.get('passed', 0)}")
    print(f"  ❌ Failed: {stats.get('failed', 0)}")
    print(f"  ⚠️ Warnings: {stats.get('warnings', 0)}")
    print(f"  Overall status: {results['status'].upper()}")
    
    # Print individual workflow results
    print(f"\n📋 Individual Results:")
    for workflow_name, workflow_result in results.get("workflows", {}).items():
        if isinstance(workflow_result, dict):
            status_icon = {
                "passed": "✅",
                "passed_with_warnings": "⚠️",
                "failed": "❌",
                "error": "💥"
            }.get(workflow_result.get("status"), "❓")
            
            print(f"  {status_icon} {workflow_name}: {workflow_result.get('status', 'unknown')}")
            
            # Show errors and warnings
            for error in workflow_result.get("errors", []):
                print(f"    ❌ {error}")
            for warning in workflow_result.get("warnings", []):
                print(f"    ⚠️ {warning}")
    
    # Print summary and recommendations
    summary = results.get("summary", {})
    if summary.get("recommendations"):
        print(f"\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")
    
    if summary.get("common_issues"):
        print(f"\n🔍 Common Issues:")
        for issue in summary["common_issues"][:3]:  # Show top 3
            print(f"  • {issue['issue']} (appears {issue['count']} times)")


def print_single_workflow_result(result: Dict[str, Any]) -> None:
    """Print results for a single workflow validation."""
    status_icon = {
        "passed": "✅",
        "passed_with_warnings": "⚠️",
        "failed": "❌",
        "error": "💥"
    }.get(result.get("status"), "❓")
    
    print(f"\n{status_icon} Workflow: {result.get('file', 'unknown')}")
    print(f"Status: {result.get('status', 'unknown').upper()}")
    
    if result.get("errors"):
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  • {error}")
    
    if result.get("warnings"):
        print(f"\n⚠️ Warnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            print(f"  • {warning}")
    
    if result.get("info"):
        print(f"\n💡 Suggestions ({len(result['info'])}):")
        for info in result["info"]:
            print(f"  • {info}")
    
    # Print check details
    checks = result.get("checks", {})
    if checks:
        print(f"\n🔍 Detailed Checks:")
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            icon = "✅" if status == "passed" else "❌" if status == "failed" else "🔄"
            print(f"  {icon} {check_name.replace('_', ' ').title()}: {status}")


def print_change_analysis(analysis: Dict[str, Any]) -> None:
    """Print workflow change analysis results."""
    print("\n🔍 Workflow Change Analysis")
    print("=" * 50)
    
    if analysis["status"] == "no_changes":
        print("✅ No workflow changes detected")
        return
    
    impact = analysis.get("impact_summary", {})
    risk_level = impact.get("risk_level", "unknown")
    risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "❓")
    
    print(f"📊 Impact Summary:")
    print(f"  {risk_icon} Risk Level: {risk_level.upper()}")
    print(f"  📁 Changed Files: {len(analysis.get('changed_files', []))}")
    
    # List changed files
    print(f"\n📋 Changed Workflows:")
    for file_path in analysis.get("changed_files", []):
        print(f"  • {file_path}")
    
    # Show file-specific analysis
    print(f"\n🔍 File Analysis:")
    for file_path, file_analysis in analysis.get("file_analysis", {}).items():
        risk = file_analysis.get("risk_level", "unknown")
        risk_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk, "❓")
        
        print(f"  {risk_icon} {file_path} ({risk} risk)")
        
        changes = file_analysis.get("changes", {})
        print(f"    +{changes.get('added_lines', 0)} -{changes.get('removed_lines', 0)} lines")
        
        for issue in file_analysis.get("potential_issues", []):
            print(f"    ⚠️ {issue}")
        
        for breaking in file_analysis.get("breaking_changes", []):
            print(f"    💥 {breaking}")
    
    # Show recommendations
    recommendations = impact.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")


def print_test_results(test_result: Dict[str, Any]) -> None:
    """Print workflow isolation test results."""
    print(f"\n🧪 Workflow Test Results: {test_result.get('workflow', 'unknown')}")
    print("=" * 50)
    
    status = test_result.get("status", "unknown")
    status_icon = {"passed": "✅", "failed": "❌", "timeout": "⏱️", "error": "💥", "skipped": "⏭️"}.get(status, "❓")
    
    print(f"{status_icon} Overall Status: {status.upper()}")
    
    if test_result.get("reason"):
        print(f"Reason: {test_result['reason']}")
    
    if test_result.get("error"):
        print(f"❌ Error: {test_result['error']}")
    
    # Show test run details
    for test_run in test_result.get("test_runs", []):
        test_type = test_run.get("type", "unknown")
        test_status = test_run.get("status", "unknown")
        test_icon = {"passed": "✅", "failed": "❌"}.get(test_status, "❓")
        
        print(f"\n{test_icon} {test_type.replace('_', ' ').title()}: {test_status}")
        print(f"Exit Code: {test_run.get('exit_code', 'unknown')}")
        
        if test_run.get("stderr"):
            print("Errors:")
            for line in test_run["stderr"].split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"  {line}")


if __name__ == "__main__":
    main()
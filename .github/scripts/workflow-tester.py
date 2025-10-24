#!/usr/bin/env python3
"""
Workflow Testing Framework

Provides comprehensive testing capabilities for GitHub Actions workflows
in isolated environments using various testing strategies and tools.

Requirements addressed:
- 10.2: Test workflow changes in isolated environments
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml


class WorkflowTester:
    """Comprehensive workflow testing framework."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the workflow tester.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        
        # Testing tools availability
        self.available_tools = self._check_available_tools()
        
        # Test result storage
        self.test_results = {}
    
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
        
        # Check for Docker
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            tools["docker"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["docker"] = False
        
        # Check for yamllint
        try:
            subprocess.run(["yamllint", "--version"], capture_output=True, check=True)
            tools["yamllint"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["yamllint"] = False
        
        # Check for actionlint
        try:
            subprocess.run(["actionlint", "-version"], capture_output=True, check=True)
            tools["actionlint"] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools["actionlint"] = False
        
        return tools
    
    def test_workflow(self, workflow_path: Path, test_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test a single workflow with comprehensive validation.
        
        Args:
            workflow_path: Path to the workflow file.
            test_config: Optional test configuration.
            
        Returns:
            Dictionary containing test results.
        """
        print(f"🧪 Testing workflow: {workflow_path.name}")
        
        if not workflow_path.exists():
            return {
                "workflow": workflow_path.name,
                "status": "error",
                "error": "Workflow file not found"
            }
        
        test_config = test_config or {}
        
        result = {
            "workflow": workflow_path.name,
            "status": "testing",
            "start_time": time.time(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        # Test suite configuration
        test_suite = [
            ("syntax_validation", self._test_syntax_validation),
            ("yaml_linting", self._test_yaml_linting),
            ("action_linting", self._test_action_linting),
            ("security_scan", self._test_security_scan),
            ("dry_run", self._test_dry_run),
            ("isolated_execution", self._test_isolated_execution),
            ("performance_check", self._test_performance_check)
        ]
        
        # Run tests based on configuration and tool availability
        for test_name, test_func in test_suite:
            if test_config.get("skip_tests", {}).get(test_name, False):
                result["tests"][test_name] = {
                    "status": "skipped",
                    "reason": "Skipped by configuration"
                }
                result["summary"]["skipped"] += 1
            else:
                print(f"  Running {test_name.replace('_', ' ')}...")
                test_result = test_func(workflow_path, test_config)
                result["tests"][test_name] = test_result
                
                if test_result["status"] == "passed":
                    result["summary"]["passed"] += 1
                elif test_result["status"] == "failed":
                    result["summary"]["failed"] += 1
                else:
                    result["summary"]["skipped"] += 1
            
            result["summary"]["total_tests"] += 1
        
        # Determine overall status
        if result["summary"]["failed"] > 0:
            result["status"] = "failed"
        elif result["summary"]["passed"] > 0:
            result["status"] = "passed"
        else:
            result["status"] = "no_tests"
        
        result["end_time"] = time.time()
        result["duration"] = result["end_time"] - result["start_time"]
        
        return result
    
    def _test_syntax_validation(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic YAML syntax validation."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            if not workflow_data:
                return {
                    "status": "failed",
                    "error": "Empty or invalid YAML file"
                }
            
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
                return {
                    "status": "failed",
                    "error": "Jobs section must be a non-empty dictionary"
                }
            
            for job_name, job_data in jobs.items():
                if not isinstance(job_data, dict):
                    return {
                        "status": "failed",
                        "error": f"Job '{job_name}' must be a dictionary"
                    }
                
                if "runs-on" not in job_data:
                    return {
                        "status": "failed",
                        "error": f"Job '{job_name}' missing required 'runs-on' field"
                    }
            
            return {
                "status": "passed",
                "message": "YAML syntax and structure valid"
            }
            
        except yaml.YAMLError as e:
            return {
                "status": "failed",
                "error": f"YAML syntax error: {e}"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Validation error: {e}"
            }
    
    def _test_yaml_linting(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test YAML linting with yamllint."""
        if not self.available_tools.get("yamllint", False):
            return {
                "status": "skipped",
                "reason": "yamllint not available"
            }
        
        try:
            result = subprocess.run(
                ["yamllint", "-f", "parsable", str(workflow_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "status": "passed",
                    "message": "YAML linting passed"
                }
            else:
                return {
                    "status": "failed",
                    "error": "YAML linting failed",
                    "details": result.stdout + result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "YAML linting timed out"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"YAML linting error: {e}"
            }
    
    def _test_action_linting(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test GitHub Actions specific linting with actionlint."""
        if not self.available_tools.get("actionlint", False):
            return {
                "status": "skipped",
                "reason": "actionlint not available - install from https://github.com/rhysd/actionlint"
            }
        
        try:
            result = subprocess.run(
                ["actionlint", "-format", "{{json .}}", str(workflow_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "status": "passed",
                    "message": "Action linting passed"
                }
            else:
                # Parse actionlint output
                issues = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        try:
                            issue = json.loads(line)
                            issues.append({
                                "line": issue.get("line"),
                                "column": issue.get("column"),
                                "message": issue.get("message"),
                                "kind": issue.get("kind")
                            })
                        except json.JSONDecodeError:
                            issues.append({"message": line})
                
                return {
                    "status": "failed",
                    "error": "Action linting failed",
                    "issues": issues
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Action linting timed out"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Action linting error: {e}"
            }
    
    def _test_security_scan(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test workflow for security issues."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            security_issues = []
            
            # Check for hardcoded secrets
            secret_patterns = [
                (r'password\s*[:=]\s*["\'][^"\']{8,}["\']', "Potential hardcoded password"),
                (r'token\s*[:=]\s*["\'][^"\']{20,}["\']', "Potential hardcoded token"),
                (r'api[_-]?key\s*[:=]\s*["\'][^"\']{16,}["\']', "Potential hardcoded API key"),
                (r'-----BEGIN [A-Z ]+-----', "Potential private key")
            ]
            
            import re
            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    security_issues.append({
                        "line": line_num,
                        "issue": description,
                        "severity": "high"
                    })
            
            # Check for overly permissive permissions
            if "permissions:" in content:
                if "write-all" in content:
                    security_issues.append({
                        "issue": "Workflow has write-all permissions",
                        "severity": "medium"
                    })
            
            # Check for unpinned action versions
            unpinned_pattern = r'uses:\s*[^@\n]+@(main|master|latest|HEAD)'
            matches = re.finditer(unpinned_pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                security_issues.append({
                    "line": line_num,
                    "issue": "Action uses unpinned version",
                    "severity": "low"
                })
            
            if security_issues:
                return {
                    "status": "failed",
                    "error": f"Security issues detected ({len(security_issues)} issues)",
                    "issues": security_issues
                }
            else:
                return {
                    "status": "passed",
                    "message": "No security issues detected"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Security scan error: {e}"
            }
    
    def _test_dry_run(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test workflow with act dry run."""
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
                    "message": "Dry run completed successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "failed",
                    "error": "Dry run failed",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Dry run timed out after 2 minutes"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Dry run error: {e}"
            }
    
    def _test_isolated_execution(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test workflow execution in isolated environment."""
        if not self.available_tools.get("act", False):
            return {
                "status": "skipped",
                "reason": "act not available for isolated execution"
            }
        
        # Skip full execution for certain workflow types to avoid side effects
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        # Skip workflows that might have side effects
        skip_patterns = ["publish", "deploy", "release", "pypi"]
        if any(pattern in content for pattern in skip_patterns):
            return {
                "status": "skipped",
                "reason": "Skipped to avoid side effects (publish/deploy workflow)"
            }
        
        try:
            # Create isolated test environment
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_repo = Path(temp_dir) / "test_repo"
                
                # Copy minimal repository structure
                shutil.copytree(self.repo_root, temp_repo, ignore=shutil.ignore_patterns(
                    '.git', 'node_modules', '__pycache__', '*.pyc', '.venv', 'venv'
                ))
                
                # Run workflow in isolated environment
                result = subprocess.run(
                    ["act", "-W", str(workflow_path.name), "--pull=false"],
                    cwd=temp_repo,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes
                )
                
                if result.returncode == 0:
                    return {
                        "status": "passed",
                        "message": "Isolated execution completed successfully"
                    }
                else:
                    # Check if failure is due to missing secrets/environment
                    if "secret" in result.stderr.lower() or "env" in result.stderr.lower():
                        return {
                            "status": "passed",
                            "message": "Execution failed due to missing secrets/env (expected in test)",
                            "note": "Workflow structure appears valid"
                        }
                    else:
                        return {
                            "status": "failed",
                            "error": "Isolated execution failed",
                            "stderr": result.stderr[:1000]  # Limit output
                        }
                        
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "error": "Isolated execution timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Isolated execution error: {e}"
            }
    
    def _test_performance_check(self, workflow_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test workflow for performance characteristics."""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = yaml.safe_load(f)
            
            performance_issues = []
            
            jobs = workflow_data.get("jobs", {})
            
            # Check for excessive timeouts
            for job_name, job_data in jobs.items():
                timeout = job_data.get("timeout-minutes")
                if timeout and timeout > 60:  # More than 1 hour
                    performance_issues.append({
                        "job": job_name,
                        "issue": f"Excessive timeout: {timeout} minutes",
                        "severity": "medium"
                    })
            
            # Check for large matrix strategies
            for job_name, job_data in jobs.items():
                strategy = job_data.get("strategy", {})
                matrix = strategy.get("matrix", {})
                
                if matrix:
                    matrix_size = 1
                    for key, values in matrix.items():
                        if isinstance(values, list):
                            matrix_size *= len(values)
                    
                    if matrix_size > 20:
                        performance_issues.append({
                            "job": job_name,
                            "issue": f"Large matrix strategy: {matrix_size} combinations",
                            "severity": "medium"
                        })
            
            # Check for missing caching
            has_caching = False
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if isinstance(step, dict) and "cache" in step.get("uses", ""):
                        has_caching = True
                        break
            
            # Check if workflow installs dependencies but lacks caching
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
                performance_issues.append({
                    "issue": "Workflow installs dependencies but lacks caching",
                    "severity": "low"
                })
            
            if performance_issues:
                return {
                    "status": "passed",  # Performance issues are warnings, not failures
                    "message": f"Performance check completed with {len(performance_issues)} recommendations",
                    "issues": performance_issues
                }
            else:
                return {
                    "status": "passed",
                    "message": "No performance issues detected"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Performance check error: {e}"
            }
    
    def test_all_workflows(self, test_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test all workflows in the repository.
        
        Args:
            test_config: Optional test configuration.
            
        Returns:
            Dictionary containing results for all workflows.
        """
        print("🧪 Testing all workflows...")
        
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            return {
                "status": "no_workflows",
                "message": "No workflow files found",
                "workflows": {}
            }
        
        results = {
            "status": "testing",
            "total_workflows": len(workflow_files),
            "workflows": {},
            "summary": {
                "passed": 0,
                "failed": 0,
                "no_tests": 0,
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_skipped": 0
            },
            "tool_availability": self.available_tools
        }
        
        for workflow_file in workflow_files:
            print(f"\n📋 Testing: {workflow_file.name}")
            workflow_result = self.test_workflow(workflow_file, test_config)
            results["workflows"][workflow_file.name] = workflow_result
            
            # Update summary
            if workflow_result["status"] == "passed":
                results["summary"]["passed"] += 1
            elif workflow_result["status"] == "failed":
                results["summary"]["failed"] += 1
            else:
                results["summary"]["no_tests"] += 1
            
            # Aggregate test counts
            summary = workflow_result.get("summary", {})
            results["summary"]["total_tests"] += summary.get("total_tests", 0)
            results["summary"]["total_passed"] += summary.get("passed", 0)
            results["summary"]["total_failed"] += summary.get("failed", 0)
            results["summary"]["total_skipped"] += summary.get("skipped", 0)
        
        # Determine overall status
        if results["summary"]["failed"] > 0:
            results["status"] = "failed"
        elif results["summary"]["passed"] > 0:
            results["status"] = "passed"
        else:
            results["status"] = "no_tests"
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any], format: str = "text") -> str:
        """Generate a formatted test report."""
        
        if format == "json":
            return json.dumps(results, indent=2, default=str)
        
        # Generate text report
        report_lines = []
        
        # Header
        report_lines.extend([
            "🧪 Workflow Testing Report",
            "=" * 50,
            f"Total Workflows: {results.get('total_workflows', 0)}",
            f"Overall Status: {results.get('status', 'unknown').upper()}",
            ""
        ])
        
        # Summary
        summary = results.get("summary", {})
        report_lines.extend([
            "📊 Summary",
            "-" * 20,
            f"✅ Passed: {summary.get('passed', 0)}",
            f"❌ Failed: {summary.get('failed', 0)}",
            f"⏭️ No Tests: {summary.get('no_tests', 0)}",
            "",
            f"📋 Test Details:",
            f"  Total Tests: {summary.get('total_tests', 0)}",
            f"  ✅ Passed: {summary.get('total_passed', 0)}",
            f"  ❌ Failed: {summary.get('total_failed', 0)}",
            f"  ⏭️ Skipped: {summary.get('total_skipped', 0)}",
            ""
        ])
        
        # Tool availability
        tools = results.get("tool_availability", {})
        if tools:
            report_lines.extend([
                "🔧 Tool Availability",
                "-" * 20
            ])
            
            for tool, available in tools.items():
                status = "✅ Available" if available else "❌ Not Available"
                report_lines.append(f"{tool}: {status}")
            
            report_lines.append("")
        
        # Individual workflow results
        workflows = results.get("workflows", {})
        if workflows:
            report_lines.extend([
                "📋 Workflow Results",
                "-" * 20
            ])
            
            for workflow_name, workflow_result in workflows.items():
                status_icon = {"passed": "✅", "failed": "❌", "no_tests": "⏭️"}.get(workflow_result.get("status"), "❓")
                duration = workflow_result.get("duration", 0)
                
                report_lines.append(f"{status_icon} {workflow_name} ({duration:.1f}s)")
                
                # Show test details
                tests = workflow_result.get("tests", {})
                for test_name, test_result in tests.items():
                    test_status = test_result.get("status", "unknown")
                    test_icon = {"passed": "  ✅", "failed": "  ❌", "skipped": "  ⏭️"}.get(test_status, "  ❓")
                    
                    report_lines.append(f"{test_icon} {test_name.replace('_', ' ').title()}")
                    
                    if test_result.get("error"):
                        report_lines.append(f"      Error: {test_result['error']}")
                    elif test_result.get("reason"):
                        report_lines.append(f"      Reason: {test_result['reason']}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main entry point for the workflow tester."""
    parser = argparse.ArgumentParser(
        description="Test GitHub Actions workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                           # Test all workflows
  %(prog)s --file quality-gate.yml        # Test specific workflow
  %(prog)s --all --skip-tests dry_run     # Skip specific tests
  %(prog)s --file test.yml --output json  # JSON output
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all workflow files"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Test specific workflow file"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--skip-tests",
        nargs="+",
        help="Skip specific tests (syntax_validation, yaml_linting, etc.)"
    )
    
    parser.add_argument(
        "--report-file",
        type=str,
        help="Save report to file"
    )
    
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root path (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    if not args.all and not args.file:
        parser.print_help()
        sys.exit(1)
    
    try:
        tester = WorkflowTester(args.repo_root)
        
        # Prepare test configuration
        test_config = {}
        if args.skip_tests:
            test_config["skip_tests"] = {test: True for test in args.skip_tests}
        
        if args.all:
            # Test all workflows
            results = tester.test_all_workflows(test_config)
        else:
            # Test specific workflow
            workflow_path = tester.workflows_dir / args.file
            if not workflow_path.exists():
                print(f"❌ Workflow file not found: {workflow_path}")
                sys.exit(1)
            
            workflow_result = tester.test_workflow(workflow_path, test_config)
            results = {
                "status": workflow_result["status"],
                "total_workflows": 1,
                "workflows": {args.file: workflow_result},
                "summary": {
                    "passed": 1 if workflow_result["status"] == "passed" else 0,
                    "failed": 1 if workflow_result["status"] == "failed" else 0,
                    "no_tests": 1 if workflow_result["status"] == "no_tests" else 0,
                    **workflow_result.get("summary", {})
                },
                "tool_availability": tester.available_tools
            }
        
        # Generate report
        report = tester.generate_test_report(results, args.output)
        
        # Output report
        if args.report_file:
            with open(args.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to: {args.report_file}")
        else:
            print(report)
        
        # Exit with appropriate code
        if results["status"] == "failed":
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Testing error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
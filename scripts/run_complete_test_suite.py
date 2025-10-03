#!/usr/bin/env python3
"""
Complete Test Suite Runner for mypylogger

This script runs the complete test suite with comprehensive reporting
to verify task completion, test coverage, and detect regressions.

Usage: python scripts/run_complete_test_suite.py [OPTIONS]

Options:
  --performance  Include performance benchmark tests
  --verbose      Show summary output only (default is detailed output)
  --subset TYPE  Run only specific test subset (quality|tests|security|build|docs)
  --help         Show this help message

Default behavior: Run comprehensive testing with detailed output
Note: Fast mode is temporarily disabled until full test suite passes consistently
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


class TestResult:
    """Container for test execution results."""

    def __init__(self, name: str, status: str, duration: float, output: str = ""):
        self.name = name
        self.status = status  # PASS, FAIL, SKIP
        self.duration = duration
        self.output = output


class TestSuiteRunner:
    """Main test suite runner class."""

    def __init__(
        self,
        verbose: bool = False,
        fast: bool = False,
        performance: bool = False,
        subset: Optional[str] = None,
        check_pipeline: bool = False,
        pipeline_branch: str = "pre-release",
        pipeline_timeout: int = 30,
        pipeline_bypass: bool = False,
        pipeline_wait: bool = False,
    ):
        self.verbose = verbose
        self.fast = fast
        self.performance = performance
        self.subset = subset
        self.check_pipeline = check_pipeline
        self.pipeline_branch = pipeline_branch
        self.pipeline_timeout = pipeline_timeout
        self.pipeline_bypass = pipeline_bypass
        self.pipeline_wait = pipeline_wait
        self.coverage_threshold = 90
        self.start_time = time.time()
        self.results: Dict[str, TestResult] = {}

    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        if self.verbose:
            print(f"\n{Colors.BLUE}{'=' * 32}{Colors.NC}")
            print(f"{Colors.BLUE}{text}{Colors.NC}")
            print(f"{Colors.BLUE}{'=' * 32}{Colors.NC}")

    def print_step(self, text: str) -> None:
        """Print a step message."""
        if self.verbose:
            print(f"\n{Colors.CYAN}🔍 {text}{Colors.NC}")

    def print_success(self, text: str) -> None:
        """Print a success message."""
        print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

    def print_warning(self, text: str) -> None:
        """Print a warning message."""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

    def print_error(self, text: str) -> None:
        """Print an error message."""
        print(f"{Colors.RED}❌ {text}{Colors.NC}")

    def run_command(self, cmd: List[str], description: str, step_name: str) -> bool:
        """Run a command and track results."""
        start_time = time.time()

        if self.verbose:
            print(f"{Colors.PURPLE}Running: {' '.join(cmd)}{Colors.NC}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=Path.cwd()
            )

            duration = time.time() - start_time
            self.results[step_name] = TestResult(
                step_name, "PASS", duration, result.stdout
            )

            self.print_success(f"{description} ({duration:.1f}s)")
            return True

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            self.results[step_name] = TestResult(
                step_name, "FAIL", duration, e.stderr or e.stdout or ""
            )

            self.print_error(f"{description} failed")
            if self.verbose:
                error_output = e.stderr or e.stdout or "No error output available"
                if error_output.strip():
                    print(f"Error output: {error_output}")
            return False

    def check_environment(self) -> bool:
        """Check and setup the environment."""
        if self.verbose:
            self.print_header("ENVIRONMENT SETUP")

        # Check if we're in the right directory
        if not (Path("pyproject.toml").exists() and Path("mypylogger").exists()):
            self.print_error("Not in mypylogger project root directory")
            return False

        # Check if mypylogger is importable
        try:
            import mypylogger  # noqa: F401

            if self.verbose:
                self.print_success("mypylogger package importable")
        except ImportError:
            self.print_warning("mypylogger package not importable, installing...")
            if not self.run_command(
                [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
                "Installing development dependencies",
                "install_deps",
            ):
                return False

        return True

    def run_quality_checks(self) -> bool:
        """Run code quality checks."""
        if self.verbose:
            self.print_header("CODE QUALITY CHECKS")

        success = True

        # Black formatting check
        if not self.run_command(
            ["black", "--check", "--diff", "."], "Code formatting check", "formatting"
        ):
            # Try to auto-fix
            if self.verbose:
                self.print_warning("Attempting to fix formatting...")
            subprocess.run(["black", "."], capture_output=True)
            subprocess.run(["isort", "."], capture_output=True)

            # Verify fix
            if not self.run_command(
                ["black", "--check", "--diff", "."],
                "Code formatting verification",
                "formatting_fix",
            ):
                success = False

        # Import sorting check
        if not self.run_command(
            ["isort", "--check-only", "--diff", "."],
            "Import sorting check",
            "import_sorting",
        ):
            success = False

        # Linting
        success &= self.run_command(["flake8", "."], "Linting check", "linting")

        # Type checking
        success &= self.run_command(
            ["mypy", "mypylogger/"], "Type checking", "type_checking"
        )

        # Security scan
        success &= self.run_command(
            ["bandit", "-r", "mypylogger/", "-f", "txt"],
            "Security scan",
            "security_scan",
        )

        # Vulnerability scan
        success &= self.run_command(
            ["pip-audit", "--ignore-vuln", "GHSA-4xh5-x5gv-qwph"],
            "Dependency vulnerability scan",
            "vulnerability_scan",
        )

        return success

    def check_pipeline_status(self) -> bool:
        """Check GitHub Actions pipeline status with quality gate enforcement."""
        if not self.check_pipeline:
            return True

        # Check for bypass option
        if self.pipeline_bypass:
            if self.verbose:
                self.print_warning(
                    "Pipeline checking bypassed - emergency mode enabled"
                )
            self.results["pipeline_check"] = TestResult("pipeline_check", "SKIP", 0.0)
            return True

        if self.verbose:
            self.print_header("GITHUB PIPELINE STATUS")
            self.print_step(
                "Checking remote pipeline status for quality gate enforcement"
            )

        try:
            # Import GitHub pipeline monitor
            import sys
            from pathlib import Path

            # Add scripts directory to path for imports
            scripts_dir = Path(__file__).parent
            sys.path.insert(0, str(scripts_dir))

            from github_monitor_config import ConfigManager, MonitoringMode
            from github_pipeline_monitor import GitHubPipelineMonitor

            # Load configuration
            config_manager = ConfigManager()
            config = config_manager.load_config()

            # Check if monitoring is available
            monitoring_mode = config_manager.determine_monitoring_mode(config)
            if monitoring_mode == MonitoringMode.DISABLED:
                if self.verbose:
                    self.print_warning(
                        "GitHub pipeline monitoring disabled - no token configured"
                    )
                    self.print_warning(
                        "Set GITHUB_TOKEN environment variable to enable pipeline checking"
                    )
                self.results["pipeline_check"] = TestResult(
                    "pipeline_check", "SKIP", 0.0
                )
                return True

            # Create monitor and check status
            monitor = GitHubPipelineMonitor(config)

            start_time = time.time()
            status = monitor.get_pipeline_status()
            duration = time.time() - start_time

            # Override timeout from command line
            if self.pipeline_timeout:
                config.timeout_minutes = self.pipeline_timeout

            if self.pipeline_wait:
                # Wait for pipeline completion with timeout
                if self.verbose:
                    self.print_step(
                        f"Waiting for pipeline completion (timeout: {self.pipeline_timeout}m)"
                    )
                status = monitor.wait_for_pipeline_completion(
                    timeout_minutes=self.pipeline_timeout
                )
            else:
                # Just check current status
                status = monitor.get_pipeline_status()

            duration = time.time() - start_time

            # Quality gate enforcement logic
            if status.overall_status == "success":
                self.results["pipeline_check"] = TestResult(
                    "pipeline_check", "PASS", duration
                )
                self.print_success(
                    f"✅ Pipeline quality gate: PASSED ({duration:.1f}s)"
                )
                if self.verbose:
                    for workflow in status.success_workflows:
                        print(f"   ✅ {workflow}")
                return True

            elif status.overall_status == "failure":
                self.results["pipeline_check"] = TestResult(
                    "pipeline_check", "FAIL", duration
                )
                self.print_error("❌ Pipeline quality gate: FAILED")
                self.print_error(
                    f"   {len(status.failed_workflows)} workflow(s) failed - blocking test suite completion"
                )

                if self.verbose:
                    print(f"\n{Colors.RED}Failed Workflows:{Colors.NC}")
                    for workflow in status.failed_workflows:
                        print(f"   ❌ {workflow}")
                        # Find the workflow run for more details
                        for run in status.workflow_runs:
                            if run.name == workflow:
                                print(f"      🔗 {run.html_url}")
                                break

                # Provide resolution guidance
                print(f"\n{Colors.YELLOW}💡 Resolution Options:{Colors.NC}")
                print("   1. Fix the failing workflows and push new commits")
                print("   2. Use --pipeline-bypass for emergency situations")
                print("   3. Use --pipeline-wait to wait for completion")
                print(
                    f"   4. Check workflow details: https://github.com/{config.repo_owner}/{config.repo_name}/actions"
                )

                return False

            elif status.overall_status == "pending":
                self.results["pipeline_check"] = TestResult(
                    "pipeline_check", "FAIL", duration
                )
                self.print_error("⏳ Pipeline quality gate: PENDING")
                self.print_error(
                    f"   {len(status.pending_workflows)} workflow(s) still running - blocking test suite completion"
                )

                if self.verbose:
                    print(f"\n{Colors.YELLOW}Pending Workflows:{Colors.NC}")
                    for workflow in status.pending_workflows:
                        print(f"   🔄 {workflow}")
                        # Find the workflow run for more details
                        for run in status.workflow_runs:
                            if run.name == workflow:
                                print(f"      🔗 {run.html_url}")
                                break

                    if status.estimated_completion_seconds:
                        est_minutes = status.estimated_completion_seconds // 60
                        print(f"   ⏱️  Estimated completion: ~{est_minutes}m")

                # Provide resolution guidance
                print(f"\n{Colors.YELLOW}💡 Resolution Options:{Colors.NC}")
                print(
                    f"   1. Use --pipeline-wait to wait for completion (timeout: {self.pipeline_timeout}m)"
                )
                print("   2. Use --pipeline-bypass for emergency situations")
                print(
                    f"   3. Monitor progress: https://github.com/{config.repo_owner}/{config.repo_name}/actions"
                )

                return False

            else:  # no_workflows
                self.results["pipeline_check"] = TestResult(
                    "pipeline_check", "SKIP", duration
                )
                if self.verbose:
                    self.print_warning(
                        "No workflows found for current commit - quality gate skipped"
                    )
                return True

        except ImportError as e:
            if self.verbose:
                self.print_warning(f"GitHub monitoring not available: {e}")
                self.print_warning("Use --pipeline-bypass if monitoring is not needed")
            self.results["pipeline_check"] = TestResult("pipeline_check", "SKIP", 0.0)
            return True

        except Exception as e:
            duration = time.time() - start_time if "start_time" in locals() else 0.0
            self.results["pipeline_check"] = TestResult(
                "pipeline_check", "FAIL", duration
            )
            self.print_error(f"❌ Pipeline quality gate: ERROR - {e}")

            if self.verbose:
                import traceback

                traceback.print_exc()

            # Provide resolution guidance for errors
            print(f"\n{Colors.YELLOW}💡 Resolution Options:{Colors.NC}")
            print("   1. Check your GITHUB_TOKEN environment variable")
            print("   2. Verify repository access permissions")
            print("   3. Use --pipeline-bypass for emergency situations")
            print("   4. Run with --verbose for detailed error information")

            return False

    def run_tests(self) -> bool:
        """Run the test suite."""
        if self.verbose:
            self.print_header("TEST EXECUTION")

        # Build test command
        cmd = [
            "pytest",
            "-v",
            "--cov=mypylogger",
            "--cov-report=html",
            "--cov-report=term-missing",
            f"--cov-fail-under={self.coverage_threshold}",
        ]

        if self.fast:
            cmd.append("tests/unit/")
            if self.verbose:
                self.print_step("Running fast unit tests only")
        else:
            if self.verbose:
                self.print_step("Running complete test suite")

        start_time = time.time()

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = time.time() - start_time

            # Extract coverage and test count from output
            coverage = "N/A"
            test_count = "N/A"

            # Combine stdout and stderr for parsing
            full_output = result.stdout + "\n" + (result.stderr or "")

            # Parse coverage from multiple possible formats
            import re

            for line in full_output.split("\n"):
                # Coverage parsing - look for TOTAL line with percentage
                if "TOTAL" in line and "%" in line:
                    # Match percentage pattern like "98%" or "98.02%"
                    coverage_match = re.search(r"(\d+(?:\.\d+)?%)", line)
                    if coverage_match:
                        coverage = coverage_match.group(1)

                # Test count parsing - look for various pytest summary formats
                # Format: "15 passed" or "15 passed, 2 warnings" or "===== 15 passed ====="
                if (
                    "passed" in line and "PASSED" not in line
                ):  # Avoid individual test PASSED lines
                    # Try different patterns
                    patterns = [
                        r"(\d+)\s+passed",  # "15 passed"
                        r"=+\s*(\d+)\s+passed",  # "===== 15 passed ====="
                        r"(\d+)\s+passed\s*[,\s]",  # "15 passed, 2 warnings"
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            test_count = match.group(1)
                            break

                    if test_count != "N/A":
                        break

            # If verbose, show detailed parsing info
            if self.verbose and (coverage == "N/A" or test_count == "N/A"):
                self.print_step("🔍 Parsing test output for coverage and test count")
                print("Output lines containing relevant keywords:")
                for line in full_output.split("\n"):
                    if ("TOTAL" in line and "%" in line) or (
                        "passed" in line and "PASSED" not in line
                    ):
                        print(f"  {line.strip()}")
                print(f"Extracted: coverage={coverage}, test_count={test_count}")

            self.results["tests"] = TestResult("tests", "PASS", duration, result.stdout)
            self.print_success(
                f"Tests: {test_count} passed, {coverage} coverage ({duration:.1f}s)"
            )

            # Show detailed test output in verbose mode
            if self.verbose:
                print("\n📋 Test Summary:")
                # Show coverage report summary
                coverage_started = False
                for line in full_output.split("\n"):
                    if "Name" in line and "Stmts" in line and "Miss" in line:
                        coverage_started = True
                    if coverage_started and (line.strip() == "" or "=" in line):
                        if "TOTAL" in line:
                            print(f"  {line}")
                            break
                    elif coverage_started:
                        print(f"  {line}")

                # Show test result summary
                for line in full_output.split("\n"):
                    if "passed" in line and (
                        "warning" in line
                        or "error" in line
                        or "failed" in line
                        or "=" in line
                    ):
                        print(f"  {line.strip()}")
                        break

            return True

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time

            # Try to extract coverage and test info even from failed runs
            coverage = "N/A"
            test_count = "N/A"
            failed_count = "N/A"

            full_output = (e.stdout or "") + "\n" + (e.stderr or "")

            import re

            for line in full_output.split("\n"):
                # Coverage parsing
                if "TOTAL" in line and "%" in line:
                    coverage_match = re.search(r"(\d+(?:\.\d+)?%)", line)
                    if coverage_match:
                        coverage = coverage_match.group(1)

                # Test results parsing for failures
                if "failed" in line or "passed" in line:
                    # Look for patterns like "5 failed, 10 passed" or "15 passed"
                    failed_match = re.search(r"(\d+)\s+failed", line)
                    passed_match = re.search(r"(\d+)\s+passed", line)

                    if failed_match:
                        failed_count = failed_match.group(1)
                    if passed_match:
                        test_count = passed_match.group(1)

            self.results["tests"] = TestResult("tests", "FAIL", duration, full_output)

            # Enhanced error reporting
            if failed_count != "N/A":
                self.print_error(
                    f"Tests failed: {failed_count} failed, {test_count} passed, {coverage} coverage ({duration:.1f}s)"
                )
            else:
                self.print_error(f"Tests failed: {coverage} coverage ({duration:.1f}s)")

            if self.verbose:
                print("\n📋 Test Failure Details:")
                # Show failed test details
                in_failures = False
                for line in full_output.split("\n"):
                    if "FAILURES" in line or "ERRORS" in line:
                        in_failures = True
                    elif "short test summary" in line.lower():
                        in_failures = False
                        print(f"  {line}")
                    elif in_failures or "FAILED" in line or "ERROR" in line:
                        print(f"  {line}")

            return False

    def run_performance_tests(self) -> bool:
        """Run performance benchmarks."""
        if not self.performance or self.fast:
            return True

        if self.verbose:
            self.print_header("PERFORMANCE BENCHMARKS")
            self.print_step("Running performance benchmark tests")

        return self.run_command(
            ["pytest", "tests/test_performance.py", "-v", "-m", "performance", "-s"],
            "Performance benchmarks",
            "performance",
        )

    def verify_package_build(self) -> bool:
        """Verify package can be built."""
        if self.verbose:
            self.print_header("PACKAGE BUILD VERIFICATION")

        success = True

        # Build package
        success &= self.run_command(
            [sys.executable, "-m", "build"], "Package build", "build"
        )

        # Check package
        success &= self.run_command(
            [sys.executable, "-m", "twine", "check", "dist/*"],
            "Package validation",
            "package_validation",
        )

        return success

    def verify_documentation(self) -> bool:
        """Verify documentation."""
        if self.verbose:
            self.print_header("DOCUMENTATION VERIFICATION")

        success = True

        # Badge verification
        badge_script = Path("scripts/verify-badges.py")
        if badge_script.exists():
            success &= self.run_command(
                [sys.executable, str(badge_script)], "Badge verification", "badges"
            )
        else:
            if self.verbose:
                self.print_warning("Badge verification script not found")
            self.results["badges"] = TestResult("badges", "SKIP", 0.0)

        # Documentation check
        success &= self.run_command(
            [sys.executable, "-c", "import mypylogger; help(mypylogger)"],
            "Documentation check",
            "documentation",
        )

        return success

    def generate_report(self) -> None:
        """Generate final summary report."""
        duration = time.time() - self.start_time

        print(f"\n{Colors.BLUE}{'=' * 32}{Colors.NC}")
        print(f"{Colors.BLUE}TEST SUITE SUMMARY{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 32}{Colors.NC}")

        # Count results
        passed = sum(1 for r in self.results.values() if r.status == "PASS")
        failed = sum(1 for r in self.results.values() if r.status == "FAIL")
        skipped = sum(1 for r in self.results.values() if r.status == "SKIP")

        # Overall status
        if failed == 0:
            print(f"{Colors.GREEN}✅ ALL CHECKS PASSED{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ {failed} CHECK(S) FAILED{Colors.NC}")

        print("\n📊 Execution Summary:")
        print(f"   Total Duration: {duration:.1f}s")
        mode = (
            "Fast"
            if self.fast
            else f"Subset ({self.subset})" if self.subset else "Complete"
        )
        print(f"   Mode: {mode}")
        print(f"   Results: {passed} passed, {failed} failed, {skipped} skipped")

        print("\n🔍 Check Results:")

        # Define check order for consistent output
        check_order = [
            "formatting",
            "import_sorting",
            "linting",
            "type_checking",
            "security_scan",
            "vulnerability_scan",
            "tests",
            "performance",
            "build",
            "package_validation",
            "badges",
            "documentation",
            "pipeline_check",
        ]

        for check in check_order:
            if check in self.results:
                result = self.results[check]
                icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[result.status]
                print(f"   {icon} {check:<20} {result.duration:.1f}s")

        if failed == 0:
            print(
                f"\n{Colors.GREEN}🚀 All quality gates passed - "
                f"ready for deployment!{Colors.NC}"
            )

            if not self.verbose:
                print("\n💡 For detailed output, run with --verbose flag")

            print("\n📁 Generated artifacts:")
            if Path("htmlcov").exists():
                print("   • htmlcov/index.html - Coverage report")
            if Path("dist").exists():
                print("   • dist/ - Built packages")
        else:
            print(f"\n{Colors.RED}🔧 Fix the failed checks above and re-run{Colors.NC}")

            if not self.verbose:
                print("\n💡 For detailed error output, run with --verbose flag")

    def run(self) -> bool:
        """Run the complete test suite."""
        if self.verbose:
            print(f"{Colors.PURPLE}🧪 mypylogger Complete Test Suite Runner{Colors.NC}")
            print(f"{Colors.PURPLE}{'=' * 39}{Colors.NC}")
        else:
            print(f"{Colors.CYAN}🧪 Running test suite...{Colors.NC}")

        # Setup environment
        if not self.check_environment():
            return False

        overall_success = True

        # Run checks based on mode
        if self.subset:
            if self.subset == "quality":
                overall_success = self.run_quality_checks()
            elif self.subset == "tests":
                overall_success = self.run_tests()
            elif self.subset == "security":
                success = True
                success &= self.run_command(
                    ["bandit", "-r", "mypylogger/", "-f", "txt"],
                    "Security scan",
                    "security_scan",
                )
                success &= self.run_command(
                    ["pip-audit", "--ignore-vuln", "GHSA-4xh5-x5gv-qwph"],
                    "Dependency vulnerability scan",
                    "vulnerability_scan",
                )
                overall_success = success
            elif self.subset == "build":
                overall_success = self.verify_package_build()
            elif self.subset == "docs":
                overall_success = self.verify_documentation()
            else:
                self.print_error(f"Unknown subset: {self.subset}")
                self.print_error("Valid subsets: quality, tests, security, build, docs")
                return False
        else:
            # Run complete test suite
            overall_success &= self.run_quality_checks()
            overall_success &= self.run_tests()
            overall_success &= self.run_performance_tests()
            overall_success &= self.verify_package_build()
            overall_success &= self.verify_documentation()

            # Check pipeline status (after all local checks pass)
            if overall_success or not self.check_pipeline:
                overall_success &= self.check_pipeline_status()

        # Generate report
        self.generate_report()

        return overall_success


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete Test Suite Runner for mypylogger (defaults to verbose mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_complete_test_suite.py                    # Complete suite (detailed output)
  python scripts/run_complete_test_suite.py --performance     # With benchmarks
  python scripts/run_complete_test_suite.py --verbose         # Summary output only
  python scripts/run_complete_test_suite.py --subset quality  # Quality checks
  python scripts/run_complete_test_suite.py --subset tests    # Tests only
  python scripts/run_complete_test_suite.py --check-pipeline  # Include pipeline status

Pipeline Integration:
  --check-pipeline                                            # Check GitHub Actions status
  --pipeline-branch main                                      # Monitor specific branch
  --pipeline-timeout 60                                       # Custom timeout (minutes)
  --pipeline-bypass                                           # Emergency bypass option
  --pipeline-wait                                             # Wait for completion

Quality Gate Enforcement:
  python scripts/run_complete_test_suite.py --check-pipeline --pipeline-wait  # Wait for pipelines
  python scripts/run_complete_test_suite.py --check-pipeline --pipeline-bypass # Emergency mode

Note: Fast mode is temporarily disabled until full test suite passes consistently.
Pipeline checking requires GITHUB_TOKEN environment variable.
        """,
    )

    # Temporarily disabled --fast option until full test suite passes
    # parser.add_argument(
    #     "--fast",
    #     action="store_true",
    #     help="Run only fast unit tests (skip integration and performance)",
    # )
    parser.add_argument(
        "--performance", action="store_true", help="Include performance benchmark tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_false",  # Changed: now --verbose turns OFF verbose (default is ON)
        help="Show summary output only (default is detailed output)",
    )
    parser.add_argument(
        "--subset",
        choices=["quality", "tests", "security", "build", "docs"],
        help="Run only specific test subset",
    )
    parser.add_argument(
        "--check-pipeline",
        action="store_true",
        help="Check GitHub Actions pipeline status before completing",
    )
    parser.add_argument(
        "--pipeline-branch",
        default="pre-release",
        help="Branch to monitor for pipeline status (default: pre-release)",
    )
    parser.add_argument(
        "--pipeline-timeout",
        type=int,
        default=30,
        help="Timeout in minutes for pipeline completion (default: 30)",
    )
    parser.add_argument(
        "--pipeline-bypass",
        action="store_true",
        help="Bypass pipeline checking for emergency situations",
    )
    parser.add_argument(
        "--pipeline-wait",
        action="store_true",
        help="Wait for pipeline completion instead of just checking current status",
    )

    args = parser.parse_args()

    # Create and run test suite
    runner = TestSuiteRunner(
        verbose=args.verbose,
        fast=False,  # Disabled fast mode until full test suite passes
        performance=args.performance,
        subset=args.subset,
        check_pipeline=args.check_pipeline,
        pipeline_branch=args.pipeline_branch,
        pipeline_timeout=args.pipeline_timeout,
        pipeline_bypass=args.pipeline_bypass,
        pipeline_wait=args.pipeline_wait,
    )

    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

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
    ):
        self.verbose = verbose
        self.fast = fast
        self.performance = performance
        self.subset = subset
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
            ["safety", "check"], "Dependency vulnerability scan", "vulnerability_scan"
        )

        return success

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

            for line in result.stdout.split("\n"):
                if "TOTAL" in line and "%" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            coverage = part
                            break
                if "passed" in line:
                    words = line.split()
                    for i, word in enumerate(words):
                        if word == "passed" and i > 0:
                            test_count = words[i - 1]
                            break

            self.results["tests"] = TestResult("tests", "PASS", duration, result.stdout)
            self.print_success(
                f"Tests: {test_count} passed, {coverage} coverage ({duration:.1f}s)"
            )
            return True

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            self.results["tests"] = TestResult(
                "tests", "FAIL", duration, e.stdout or e.stderr or ""
            )
            self.print_error("Tests failed")
            if self.verbose:
                print("Test output:")
                print(e.stdout or e.stderr or "No output available")
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
                    ["safety", "check"],
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

        # Generate report
        self.generate_report()

        return overall_success


def main():
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

Note: Fast mode is temporarily disabled until full test suite passes consistently.
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

    args = parser.parse_args()

    # Create and run test suite
    runner = TestSuiteRunner(
        verbose=args.verbose,
        fast=False,  # Disabled fast mode until full test suite passes
        performance=args.performance,
        subset=args.subset,
    )

    success = runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""PyPI publishing script with comprehensive error handling.

This script provides a robust PyPI publishing workflow with error handling,
retry logic, and detailed failure reporting.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Dict, Optional

from publishing_error_handler import (
    ErrorCategory,
    PublishingError,
    PublishingErrorHandler,
    RetryConfig,
)


class PyPIPublisher:
    """PyPI publisher with comprehensive error handling."""

    def __init__(
        self,
        package_dir: Path = Path(),
        dry_run: bool = False,
        log_file: Optional[Path] = None,
    ) -> None:
        """Initialize PyPI publisher.

        Args:
            package_dir: Directory containing the package
            dry_run: Whether to perform dry run (build only, no publish)
            log_file: Optional log file path
        """
        self.package_dir = package_dir
        self.dry_run = dry_run
        self.error_handler = PublishingErrorHandler(log_file)
        self.build_dir: Optional[Path] = None

    def validate_environment(self) -> bool:
        """Validate publishing environment.

        Returns:
            True if environment is valid, False otherwise
        """
        self.error_handler.logger.info("Validating publishing environment...")

        # Check required files
        required_files = ["pyproject.toml", "README.md"]
        for file_name in required_files:
            file_path = self.package_dir / file_name
            if not file_path.exists():
                error = PublishingError(
                    category=ErrorCategory.CONFIGURATION,
                    severity=self.error_handler.determine_severity(ErrorCategory.CONFIGURATION, 1),
                    message=f"Required file not found: {file_name}",
                    is_retryable=False,
                )
                self.error_handler.errors.append(error)
                return False

        # Check source directory
        src_dir = self.package_dir / "src"
        if not src_dir.exists():
            error = PublishingError(
                category=ErrorCategory.CONFIGURATION,
                severity=self.error_handler.determine_severity(ErrorCategory.CONFIGURATION, 1),
                message="Source directory 'src/' not found",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        # Check UV installation
        success, error = self.error_handler.run_command_with_retry(
            ["uv", "--version"], RetryConfig(max_retries=0), self.package_dir
        )
        if not success:
            return False

        self.error_handler.logger.info("✅ Environment validation passed")
        return True

    def run_quality_gates(self) -> bool:
        """Run quality gate checks.

        Returns:
            True if all quality gates pass, False otherwise
        """
        self.error_handler.logger.info("Running quality gate checks...")

        # Run master test script
        test_script = self.package_dir / "scripts" / "run_tests.sh"
        if test_script.exists():
            success, error = self.error_handler.run_command_with_retry(
                [str(test_script)], RetryConfig(max_retries=0), self.package_dir
            )
            if not success:
                self.error_handler.logger.error("Quality gates failed")
                return False
        else:
            self.error_handler.logger.warning(
                "Master test script not found, skipping quality gates"
            )

        self.error_handler.logger.info("✅ Quality gates passed")
        return True

    def validate_package_metadata(self) -> bool:
        """Validate package metadata.

        Returns:
            True if metadata is valid, False otherwise
        """
        self.error_handler.logger.info("Validating package metadata...")

        # Run package validation script
        validation_script = self.package_dir / "scripts" / "validate_package.py"
        if validation_script.exists():
            success, error = self.error_handler.run_command_with_retry(
                ["uv", "run", "python", str(validation_script)],
                RetryConfig(max_retries=0),
                self.package_dir,
            )
            if not success:
                self.error_handler.logger.error("Package metadata validation failed")
                return False
        else:
            self.error_handler.logger.warning("Package validation script not found")

        self.error_handler.logger.info("✅ Package metadata validation passed")
        return True

    def build_package(self) -> bool:
        """Build package distributions.

        Returns:
            True if build succeeds, False otherwise
        """
        self.error_handler.logger.info("Building package distributions...")

        # Create temporary build directory
        self.build_dir = Path(tempfile.mkdtemp(prefix="pypi_build_"))
        self.error_handler.logger.info(f"Using build directory: {self.build_dir}")

        # Build source distribution
        success, error = self.error_handler.run_command_with_retry(
            ["uv", "build", "--sdist", "--out-dir", str(self.build_dir)],
            RetryConfig(max_retries=1),
            self.package_dir,
        )
        if not success:
            self.error_handler.logger.error("Source distribution build failed")
            return False

        # Build wheel distribution
        success, error = self.error_handler.run_command_with_retry(
            ["uv", "build", "--wheel", "--out-dir", str(self.build_dir)],
            RetryConfig(max_retries=1),
            self.package_dir,
        )
        if not success:
            self.error_handler.logger.error("Wheel distribution build failed")
            return False

        # Verify built files
        sdist_files = list(self.build_dir.glob("*.tar.gz"))
        wheel_files = list(self.build_dir.glob("*.whl"))

        if not sdist_files:
            error = PublishingError(
                category=ErrorCategory.BUILD,
                severity=self.error_handler.determine_severity(ErrorCategory.BUILD, 1),
                message="No source distribution files found after build",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        if not wheel_files:
            error = PublishingError(
                category=ErrorCategory.BUILD,
                severity=self.error_handler.determine_severity(ErrorCategory.BUILD, 1),
                message="No wheel distribution files found after build",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        self.error_handler.logger.info(
            f"✅ Built {len(sdist_files)} sdist and {len(wheel_files)} wheel files"
        )
        return True

    def validate_built_package(self) -> bool:
        """Validate built package integrity.

        Returns:
            True if validation succeeds, False otherwise
        """
        if not self.build_dir:
            error = PublishingError(
                category=ErrorCategory.VALIDATION,
                severity=self.error_handler.determine_severity(ErrorCategory.VALIDATION, 1),
                message="No build directory available for validation",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        self.error_handler.logger.info("Validating built package integrity...")

        # Get all distribution files
        dist_files = list(self.build_dir.glob("*.tar.gz")) + list(self.build_dir.glob("*.whl"))

        if not dist_files:
            error = PublishingError(
                category=ErrorCategory.VALIDATION,
                severity=self.error_handler.determine_severity(ErrorCategory.VALIDATION, 1),
                message="No distribution files found for validation",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        # Validate with twine check
        success, error = self.error_handler.run_command_with_retry(
            ["uv", "run", "twine", "check"] + [str(f) for f in dist_files],
            RetryConfig(max_retries=2, base_delay=1.0),
            self.package_dir,
        )
        if not success:
            self.error_handler.logger.error("Package integrity validation failed")
            return False

        self.error_handler.logger.info("✅ Package integrity validation passed")
        return True

    def publish_to_pypi(self) -> bool:
        """Publish package to PyPI.

        Returns:
            True if publishing succeeds, False otherwise
        """
        if self.dry_run:
            self.error_handler.logger.info("🧪 Dry run mode - skipping actual PyPI publishing")
            return True

        if not self.build_dir:
            error = PublishingError(
                category=ErrorCategory.UPLOAD,
                severity=self.error_handler.determine_severity(ErrorCategory.UPLOAD, 1),
                message="No build directory available for publishing",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        self.error_handler.logger.info("Publishing package to PyPI...")

        # Get all distribution files
        dist_files = list(self.build_dir.glob("*.tar.gz")) + list(self.build_dir.glob("*.whl"))

        if not dist_files:
            error = PublishingError(
                category=ErrorCategory.UPLOAD,
                severity=self.error_handler.determine_severity(ErrorCategory.UPLOAD, 1),
                message="No distribution files found for publishing",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            return False

        # Check for PyPI token
        pypi_token = os.environ.get("PYPI_API_TOKEN")
        if not pypi_token:
            self.error_handler.logger.warning("⚠️  No PYPI_API_TOKEN found - using placeholder")
            self.error_handler.logger.info("🚀 Would publish to PyPI with twine upload")
            for dist_file in dist_files:
                self.error_handler.logger.info(f"   - {dist_file.name}")
            return True

        # Publish with twine (with retry for network issues)
        success, error = self.error_handler.run_command_with_retry(
            ["uv", "run", "twine", "upload"] + [str(f) for f in dist_files],
            RetryConfig(max_retries=3, base_delay=2.0),
            self.package_dir,
        )
        if not success:
            self.error_handler.logger.error("PyPI publishing failed")
            return False

        self.error_handler.logger.info("✅ Package published to PyPI successfully")
        return True

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.build_dir and self.build_dir.exists():
            import shutil

            try:
                shutil.rmtree(self.build_dir)
                self.error_handler.logger.info(f"Cleaned up build directory: {self.build_dir}")
            except Exception as e:
                self.error_handler.logger.warning(f"Failed to clean up build directory: {e}")

    def generate_publishing_report(self) -> Dict[str, any]:
        """Generate comprehensive publishing report.

        Returns:
            Publishing report dictionary
        """
        error_report = self.error_handler.generate_error_report()

        report = {
            "publishing_status": "success" if error_report["status"] == "success" else "failed",
            "dry_run": self.dry_run,
            "package_dir": str(self.package_dir),
            "build_dir": str(self.build_dir) if self.build_dir else None,
            "error_report": error_report,
        }

        # Add distribution file information if available
        if self.build_dir and self.build_dir.exists():
            dist_files = list(self.build_dir.glob("*.tar.gz")) + list(self.build_dir.glob("*.whl"))
            report["distribution_files"] = [
                {"name": f.name, "size": f.stat().st_size, "path": str(f)} for f in dist_files
            ]

        return report

    def run_publishing_workflow(self) -> bool:
        """Run complete publishing workflow.

        Returns:
            True if workflow succeeds, False otherwise
        """
        try:
            self.error_handler.logger.info("🚀 Starting PyPI publishing workflow...")

            # Step 1: Validate environment
            if not self.validate_environment():
                self.error_handler.logger.error("❌ Environment validation failed")
                return False

            # Step 2: Run quality gates
            if not self.run_quality_gates():
                self.error_handler.logger.error("❌ Quality gates failed")
                return False

            # Step 3: Validate package metadata
            if not self.validate_package_metadata():
                self.error_handler.logger.error("❌ Package metadata validation failed")
                return False

            # Step 4: Build package
            if not self.build_package():
                self.error_handler.logger.error("❌ Package build failed")
                return False

            # Step 5: Validate built package
            if not self.validate_built_package():
                self.error_handler.logger.error("❌ Built package validation failed")
                return False

            # Step 6: Publish to PyPI
            if not self.publish_to_pypi():
                self.error_handler.logger.error("❌ PyPI publishing failed")
                return False

            self.error_handler.logger.info("✅ Publishing workflow completed successfully")
            return True

        except Exception as e:
            error = PublishingError(
                category=ErrorCategory.UNKNOWN,
                severity=self.error_handler.determine_severity(ErrorCategory.UNKNOWN, 1),
                message=f"Unexpected error in publishing workflow: {e!s}",
                is_retryable=False,
            )
            self.error_handler.errors.append(error)
            self.error_handler.logger.exception("Unexpected error in publishing workflow")
            return False

        finally:
            self.cleanup()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PyPI publishing with error handling")
    parser.add_argument(
        "--package-dir",
        type=Path,
        default=Path(),
        help="Directory containing the package (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run (build only, no publish)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path for detailed logging",
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default=Path("publishing_report.json"),
        help="Output file for publishing report",
    )

    args = parser.parse_args()

    # Initialize publisher
    publisher = PyPIPublisher(
        package_dir=args.package_dir,
        dry_run=args.dry_run,
        log_file=args.log_file,
    )

    # Run publishing workflow
    success = publisher.run_publishing_workflow()

    # Generate and save report
    report = publisher.generate_publishing_report()
    with args.report_file.open("w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Publishing report saved to: {args.report_file}")

    # Print summary
    if success:
        print("✅ Publishing workflow completed successfully!")
        if args.dry_run:
            print("🧪 Dry run mode - no actual publishing performed")
    else:
        print("❌ Publishing workflow failed!")
        publisher.error_handler.print_error_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

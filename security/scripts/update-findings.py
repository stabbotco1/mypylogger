#!/usr/bin/env python3
"""Core automation engine for security findings management.

This script provides complete automation workflow for processing security scanner
outputs, synchronizing remediation plans, and generating findings documents.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

# Add security module to path for imports
security_dir = Path(__file__).parent.parent
sys.path.insert(0, str(security_dir))
sys.path.insert(0, str(security_dir.parent))  # Add project root for security module

from security.generator import FindingsDocumentGenerator
from security.history import HistoricalDataManager, get_default_historical_manager
from security.parsers import ScannerParseError, extract_all_findings
from security.remediation import RemediationDatastore, get_default_datastore
from security.synchronizer import RemediationSynchronizer


class AutomationEngine:
    """Core automation engine for security findings management."""

    def __init__(
        self,
        reports_dir: Path | None = None,
        findings_file: Path | None = None,
        datastore: RemediationDatastore | None = None,
        historical_manager: HistoricalDataManager | None = None,
        verbose: bool = False,
    ) -> None:
        """Initialize the automation engine.

        Args:
            reports_dir: Directory containing security scan reports
            findings_file: Output file for findings document
            datastore: Remediation datastore instance
            historical_manager: Historical data manager instance
            verbose: Enable verbose logging
        """
        self.reports_dir = reports_dir or Path("security/reports/latest")
        self.findings_file = findings_file or Path("security/findings/SECURITY_FINDINGS.md")
        self.datastore = datastore or get_default_datastore()
        self.historical_manager = historical_manager or get_default_historical_manager()
        self.verbose = verbose

        # Initialize components
        self.synchronizer = RemediationSynchronizer(
            self.datastore, self.reports_dir, self.historical_manager
        )
        self.generator = FindingsDocumentGenerator(
            self.datastore, self.reports_dir, self.findings_file
        )

    def run_complete_workflow(self) -> dict[str, any]:
        """Run the complete automation workflow.

        Returns:
            Dictionary with workflow execution results and statistics

        Raises:
            RuntimeError: If workflow execution fails
        """
        try:
            self._log("Starting security findings automation workflow...")

            workflow_results = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reports_processed": 0,
                "findings_extracted": 0,
                "synchronization_stats": {},
                "document_generated": False,
                "archive_created": False,
                "errors": [],
                "warnings": [],
            }

            # Step 1: Process scanner outputs
            self._log("Step 1: Processing scanner outputs...")
            findings_result = self._process_scanner_outputs()
            workflow_results.update(findings_result)

            # Step 2: Synchronize remediation plans
            self._log("Step 2: Synchronizing remediation plans...")
            sync_result = self._synchronize_remediation_plans()
            workflow_results["synchronization_stats"] = sync_result

            # Step 3: Generate findings document
            self._log("Step 3: Generating findings document...")
            doc_result = self._generate_findings_document()
            workflow_results["document_generated"] = doc_result

            # Step 4: Archive scan results
            self._log("Step 4: Archiving scan results...")
            archive_result = self._archive_scan_results()
            workflow_results["archive_created"] = archive_result

            # Step 5: Validate results
            self._log("Step 5: Validating results...")
            validation_result = self._validate_workflow_results()
            workflow_results["validation_errors"] = validation_result

            self._log("Automation workflow completed successfully!")
            return workflow_results

        except Exception as e:
            error_msg = f"Automation workflow failed: {e}"
            self._log(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg) from e

    def _process_scanner_outputs(self) -> dict[str, any]:
        """Process security scanner outputs and extract findings.

        Returns:
            Dictionary with processing results
        """
        try:
            if not self.reports_dir.exists():
                self._log(f"WARNING: Reports directory not found: {self.reports_dir}")
                return {
                    "reports_processed": 0,
                    "findings_extracted": 0,
                    "warnings": [f"Reports directory not found: {self.reports_dir}"],
                }

            # Check for expected scanner output files
            expected_files = {
                "pip-audit.json": "pip-audit",
                "bandit.json": "bandit",
                "secrets-scan.json": "secrets",
            }

            reports_found = []
            for filename, scanner_type in expected_files.items():
                file_path = self.reports_dir / filename
                if file_path.exists():
                    reports_found.append((file_path, scanner_type))
                    self._log(f"Found {scanner_type} report: {file_path}")

            if not reports_found:
                self._log("WARNING: No scanner output files found")
                return {
                    "reports_processed": 0,
                    "findings_extracted": 0,
                    "warnings": ["No scanner output files found"],
                }

            # Extract findings from all available reports
            try:
                all_findings = extract_all_findings(self.reports_dir)
                self._log(
                    f"Extracted {len(all_findings)} findings from {len(reports_found)} reports"
                )

                return {
                    "reports_processed": len(reports_found),
                    "findings_extracted": len(all_findings),
                    "scanner_types": [scanner_type for _, scanner_type in reports_found],
                }

            except ScannerParseError as e:
                error_msg = f"Failed to parse scanner outputs: {e}"
                self._log(f"ERROR: {error_msg}")
                return {
                    "reports_processed": 0,
                    "findings_extracted": 0,
                    "errors": [error_msg],
                }

        except Exception as e:
            error_msg = f"Failed to process scanner outputs: {e}"
            self._log(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg) from e

    def _synchronize_remediation_plans(self) -> dict[str, any]:
        """Synchronize remediation plans with current findings.

        Returns:
            Dictionary with synchronization statistics
        """
        try:
            # Get synchronization status before changes
            status_before = self.synchronizer.get_synchronization_status()
            self._log(
                f"Before sync: {status_before['total_findings']} findings, "
                f"{status_before['total_plans']} plans, "
                f"{status_before['sync_percentage']:.1f}% in sync"
            )

            # Perform synchronization
            sync_stats = self.synchronizer.synchronize_findings(preserve_manual_edits=True)

            # Get status after synchronization
            status_after = self.synchronizer.get_synchronization_status()
            self._log(
                f"After sync: {status_after['total_findings']} findings, "
                f"{status_after['total_plans']} plans, "
                f"{status_after['sync_percentage']:.1f}% in sync"
            )

            # Validate synchronization
            validation_errors = self.synchronizer.validate_synchronization()
            if validation_errors:
                self._log(
                    f"WARNING: Synchronization validation found {len(validation_errors)} issues"
                )
                for error in validation_errors:
                    self._log(f"  - {error}")

            return {
                "before": status_before,
                "after": status_after,
                "changes": sync_stats,
                "validation_errors": validation_errors,
            }

        except Exception as e:
            error_msg = f"Failed to synchronize remediation plans: {e}"
            self._log(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg) from e

    def _generate_findings_document(self) -> bool:
        """Generate the findings document.

        Returns:
            True if document was generated successfully
        """
        try:
            # Ensure output directory exists
            self.findings_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate document
            self.generator.generate_document()

            # Verify document was created
            if self.findings_file.exists():
                file_size = self.findings_file.stat().st_size
                self._log(f"Generated findings document: {self.findings_file} ({file_size} bytes)")
                return True
            self._log("ERROR: Findings document was not created")
            return False

        except Exception as e:
            error_msg = f"Failed to generate findings document: {e}"
            self._log(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg) from e

    def _archive_scan_results(self) -> bool:
        """Archive current scan results for historical tracking.

        Returns:
            True if archival was successful
        """
        try:
            if not self.reports_dir.exists():
                self._log("WARNING: No reports directory to archive")
                return False

            # Archive scan results
            archive_dir = self.historical_manager.archive_scan_results()
            self._log(f"Archived scan results to: {archive_dir}")
            return True

        except Exception as e:
            error_msg = f"Failed to archive scan results: {e}"
            self._log(f"ERROR: {error_msg}")
            return False

    def _validate_workflow_results(self) -> list[str]:
        """Validate the results of the workflow execution.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Validate findings document exists and is readable
            if not self.findings_file.exists():
                errors.append(f"Findings document not found: {self.findings_file}")
            else:
                try:
                    content = self.findings_file.read_text(encoding="utf-8")
                    if len(content) < 100:  # Minimum expected content
                        errors.append("Findings document appears to be empty or too short")
                except Exception as e:
                    errors.append(f"Cannot read findings document: {e}")

            # Validate remediation registry
            registry_errors = self.datastore.validate_registry_structure()
            errors.extend(registry_errors)

            # Validate synchronization state
            sync_errors = self.synchronizer.validate_synchronization()
            errors.extend(sync_errors)

        except Exception as e:
            errors.append(f"Validation failed: {e}")

        return errors

    def _log(self, message: str) -> None:
        """Log a message with timestamp.

        Args:
            message: Message to log
        """
        if self.verbose:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"[{timestamp}] {message}")


def main() -> int:
    """Main entry point for the automation engine."""
    parser = argparse.ArgumentParser(
        description="Security findings automation engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Run with default settings
  %(prog)s --verbose                          # Run with verbose logging
  %(prog)s --reports-dir /path/to/reports     # Use custom reports directory
  %(prog)s --output /path/to/findings.md      # Use custom output file
  %(prog)s --dry-run                          # Show what would be done without making changes
        """,
    )

    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("security/reports/latest"),
        help="Directory containing security scan reports (default: security/reports/latest)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("security/findings/SECURITY_FINDINGS.md"),
        help="Output file for findings document (default: security/findings/SECURITY_FINDINGS.md)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    try:
        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")
            print(f"Reports directory: {args.reports_dir}")
            print(f"Output file: {args.output}")

            # Check what files would be processed
            if args.reports_dir.exists():
                scanner_files = ["pip-audit.json", "bandit.json", "secrets-scan.json"]
                found_files = [f for f in scanner_files if (args.reports_dir / f).exists()]
                print(f"Scanner files found: {found_files}")
            else:
                print("Reports directory does not exist")

            return 0

        # Initialize and run automation engine
        engine = AutomationEngine(
            reports_dir=args.reports_dir,
            findings_file=args.output,
            verbose=args.verbose,
        )

        results = engine.run_complete_workflow()

        # Output results
        if args.json_output:
            print(json.dumps(results, indent=2, default=str))
        else:
            # Human-readable output
            print("Security Findings Automation Results:")
            print(f"  Reports processed: {results.get('reports_processed', 0)}")
            print(f"  Findings extracted: {results.get('findings_extracted', 0)}")

            sync_stats = results.get("synchronization_stats", {}).get("changes", {})
            print(f"  Remediation plans added: {sync_stats.get('added', 0)}")
            print(f"  Remediation plans removed: {sync_stats.get('removed', 0)}")
            print(f"  Remediation plans preserved: {sync_stats.get('preserved', 0)}")

            print(f"  Document generated: {results.get('document_generated', False)}")

            validation_errors = results.get("validation_errors", [])
            if validation_errors:
                print(f"  Validation errors: {len(validation_errors)}")
                for error in validation_errors:
                    print(f"    - {error}")
            else:
                print("  Validation: PASSED")

        # Return appropriate exit code
        validation_errors = results.get("validation_errors", [])
        errors = results.get("errors", [])

        if validation_errors or errors:
            return 1
        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

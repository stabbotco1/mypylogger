#!/usr/bin/env python3
"""
Production mode example for mypylogger.

This example demonstrates mypylogger configured for production:
- Warning level logging (reduced verbosity)
- No stdout logging (file only)
- Log file persistence
- Structured JSON output for log analysis
"""

import json
import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import mypylogger
sys.path.insert(0, str(Path(__file__).parent.parent))

import mypylogger


def simulate_production_workflow():
    """Simulate a typical production workflow with logging."""
    logger = mypylogger.get_logger()

    # Simulate application startup (only important events logged)
    logger.info("Production service started")

    # Simulate normal operations (debug messages won't appear)
    for i in range(5):
        # This debug message won't be logged in production mode
        logger.debug(f"Processing request {i + 1}")  # Won't appear

        if i == 2:
            # Warning and above will be logged
            logger.warning(
                "High memory usage detected",
                extra={
                    "memory_usage_mb": 512,
                    "threshold_mb": 400,
                    "service": "api-server",
                },
            )

        if i == 4:
            # Error conditions are always logged
            logger.error(
                "External service timeout",
                extra={
                    "service": "payment-gateway",
                    "timeout_seconds": 30,
                    "request_id": f"req-{i + 1}",
                },
            )

    # Critical issues are always logged
    logger.critical(
        "Service health check failed",
        extra={
            "health_score": 0.2,
            "failed_checks": ["database", "cache"],
            "timestamp": time.time(),
        },
    )

    logger.info("Production service shutdown initiated")


def analyze_log_output():
    """Analyze the JSON log output to demonstrate structured logging benefits."""
    log_file_path = Path("logs") / f"prod_service_{time.strftime('%Y_%m_%d')}.log"

    if not log_file_path.exists():
        print(f"No log file found for analysis at: {log_file_path.absolute()}")
        return

    print("\n=== Log Analysis ===")

    log_entries = []
    with open(log_file_path, "r") as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                log_entries.append(log_entry)
            except json.JSONDecodeError:
                continue

    print(f"Total log entries: {len(log_entries)}")

    # Analyze by level
    level_counts = {}
    for entry in log_entries:
        level = entry.get("levelname", "UNKNOWN")
        level_counts[level] = level_counts.get(level, 0) + 1

    print("Log entries by level:")
    for level, count in sorted(level_counts.items()):
        print(f"  {level}: {count}")

    # Show structured data examples
    print("\nStructured data examples:")
    for entry in log_entries:
        if "memory_usage_mb" in entry:
            print(
                f"  Memory alert: {entry['memory_usage_mb']}MB (threshold: {entry['threshold_mb']}MB)"
            )
        elif "service" in entry and entry.get("levelname") == "ERROR":
            print(f"  Service error: {entry['service']} - {entry['message']}")
        elif "health_score" in entry:
            print(
                f"  Health check: score={entry['health_score']}, failed={entry['failed_checks']}"
            )


def main():
    """Demonstrate production mode configuration."""
    print("=== Production Mode Example ===\n")

    # Configure for production
    os.environ["APP_NAME"] = "prod_service"
    os.environ["LOG_LEVEL"] = "WARNING"  # Only warnings and above
    os.environ["PARALLEL_STDOUT_LOGGING"] = "false"  # No console output
    os.environ["EMPTY_LOG_FILE_ON_RUN"] = "false"  # Preserve existing logs

    print("Production configuration:")
    print("  - Warning level logging (reduced verbosity)")
    print("  - File-only logging (no console output)")
    print("  - Log file persistence")
    print("  - Structured JSON for analysis")
    print()

    # Get logger and show configuration
    logger = mypylogger.get_logger()
    print(f"Logger configured: {logger.name} (level: {logger.level})")
    print(f"Effective level: {mypylogger.get_effective_level()}")
    print()

    print("Running production workflow simulation...")
    print("(Logs will only go to file, not console)")
    print()

    # Run the simulation
    simulate_production_workflow()

    # Show log file information
    log_file_path = Path("logs") / f"prod_service_{time.strftime('%Y_%m_%d')}.log"
    print(f"Production logs saved to: {log_file_path.absolute()}")

    if log_file_path.exists():
        print(f"Log file size: {log_file_path.stat().st_size} bytes")

        # Show sample log entries
        print("\nSample log entries (JSON format):")
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:3], 1):
                try:
                    log_data = json.loads(line.strip())
                    print(f"  {i}: {log_data['levelname']} - {log_data['message']}")
                except json.JSONDecodeError:
                    print(f"  {i}: {line.strip()}")

    # Analyze the structured log output
    analyze_log_output()

    print("\n=== Production mode example completed ===")


if __name__ == "__main__":
    main()

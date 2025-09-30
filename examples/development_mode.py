#!/usr/bin/env python3
"""
Development mode example for mypylogger.

This example demonstrates mypylogger configured for development:
- Debug level logging
- Stdout logging enabled
- Log file truncation on startup
- Real-time log visibility
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import mypylogger
sys.path.insert(0, str(Path(__file__).parent.parent))

import mypylogger


def simulate_development_workflow():
    """Simulate a typical development workflow with logging."""
    logger = mypylogger.get_logger()

    # Simulate application startup
    logger.info("Starting development server")
    logger.debug("Loading configuration from environment")
    logger.debug("Initializing database connection")

    # Simulate some processing
    for i in range(3):
        logger.info(f"Processing request {i + 1}")
        logger.debug(f"Request details: method=GET, path=/api/users/{i + 1}")

        # Simulate some work
        time.sleep(0.1)

        if i == 1:
            logger.warning(
                "Slow query detected", extra={"query_time_ms": 250, "table": "users"}
            )

        logger.debug(f"Request {i + 1} completed successfully")

    # Simulate an error condition
    logger.error(
        "Database connection timeout", extra={"timeout_seconds": 30, "retry_count": 3}
    )

    # Simulate recovery
    logger.info("Reconnected to database")
    logger.info("Development server ready")


def main():
    """Demonstrate development mode configuration."""
    print("=== Development Mode Example ===\n")

    # Configure for development
    os.environ["APP_NAME"] = "dev_server"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["PARALLEL_STDOUT_LOGGING"] = "DEBUG"  # Show all logs in console
    os.environ["EMPTY_LOG_FILE_ON_RUN"] = "true"  # Fresh log file each run

    print("Development configuration:")
    print("  - Debug level logging enabled")
    print("  - All logs mirrored to stdout")
    print("  - Log file truncated on startup")
    print("  - Real-time log visibility")
    print()

    # Get logger and show configuration
    logger = mypylogger.get_logger()
    print(f"Logger configured: {logger.name} (level: {logger.level})")
    print(f"Handlers: {len(logger.handlers)}")
    print()

    print("Starting development workflow simulation...")
    print("(Watch for real-time logs in console and file)")
    print()

    # Run the simulation
    simulate_development_workflow()

    # Show log file information
    log_file_path = Path("logs") / f"dev_server_{time.strftime('%Y_%m_%d')}.log"
    print(f"\nDevelopment logs saved to: {log_file_path.absolute()}")

    if log_file_path.exists():
        print(f"Log entries: {len(open(log_file_path).readlines())}")
        print("\nTail of log file (last 3 lines):")
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(f"  {line.strip()}")

    print("\n=== Development mode example completed ===")


if __name__ == "__main__":
    main()

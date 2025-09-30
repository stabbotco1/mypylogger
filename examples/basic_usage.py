#!/usr/bin/env python3
"""
Basic usage example for mypylogger.

This example demonstrates the core functionality of mypylogger including:
- Getting a logger instance
- Logging at different levels
- JSON formatted output
- File and stdout logging
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import mypylogger
sys.path.insert(0, str(Path(__file__).parent.parent))

import mypylogger


def main():
    """Demonstrate basic mypylogger usage."""
    print("=== Basic mypylogger Usage Example ===\n")

    # Set up environment for this example
    os.environ["APP_NAME"] = "basic_example"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["PARALLEL_STDOUT_LOGGING"] = "INFO"
    os.environ["EMPTY_LOG_FILE_ON_RUN"] = "true"

    print("Environment configuration:")
    print(f"  APP_NAME: {os.environ['APP_NAME']}")
    print(f"  LOG_LEVEL: {os.environ['LOG_LEVEL']}")
    print(f"  PARALLEL_STDOUT_LOGGING: {os.environ['PARALLEL_STDOUT_LOGGING']}")
    print(f"  EMPTY_LOG_FILE_ON_RUN: {os.environ['EMPTY_LOG_FILE_ON_RUN']}")
    print()

    # Get logger instance
    logger = mypylogger.get_logger()

    print(f"Logger name: {logger.name}")
    print(f"Logger level: {logger.level} ({mypylogger.get_effective_level()})")
    print(f"Number of handlers: {len(logger.handlers)}")
    print()

    # Demonstrate logging at different levels
    print("Logging messages at different levels:")
    print("(Messages will appear in both console and log file)")
    print()

    logger.debug("This is a debug message with detailed information")
    logger.info("Application started successfully")
    logger.warning("This is a warning message about potential issues")
    logger.error("An error occurred during processing")
    logger.critical("Critical system failure detected")

    # Demonstrate logging with extra context
    print("\nLogging with extra context:")
    logger.info(
        "User action completed",
        extra={"user_id": 12345, "action": "login", "duration_ms": 150},
    )

    # Demonstrate exception logging
    print("\nLogging exceptions:")
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=True)

    # Show log file location
    log_file_path = (
        Path("logs") / f"{os.environ['APP_NAME']}_{time.strftime('%Y_%m_%d')}.log"
    )
    print(f"\nLog file created at: {log_file_path.absolute()}")

    if log_file_path.exists():
        print(f"Log file size: {log_file_path.stat().st_size} bytes")
        print("\nFirst few lines of log file:")
        with open(log_file_path, "r") as f:
            lines = f.readlines()[:5]
            for i, line in enumerate(lines, 1):
                print(f"  {i}: {line.strip()}")

    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()

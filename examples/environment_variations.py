#!/usr/bin/env python3
"""
Environment variations example for mypylogger.

This example demonstrates how mypylogger behaves with different
environment variable combinations and configurations.
"""

import json
import os
import sys
import time
from pathlib import Path

import mypylogger

# Add the parent directory to the path so we can import mypylogger
sys.path.insert(0, str(Path(__file__).parent.parent))


def reset_environment() -> None:
    """Reset environment variables to clean state."""
    env_vars = [
        "APP_NAME",
        "LOG_LEVEL",
        "EMPTY_LOG_FILE_ON_RUN",
        "PARALLEL_STDOUT_LOGGING",
    ]
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    # Reset singleton state
    if hasattr(mypylogger.SingletonLogger, "_instance"):
        mypylogger.SingletonLogger._instance = None
        mypylogger.SingletonLogger._logger = None
        mypylogger.SingletonLogger._config = None


def test_configuration(name: str, env_config: dict, description: str) -> None:
    """Test a specific environment configuration."""
    print(f"\n=== {name} ===")
    print(f"Description: {description}")

    # Reset and apply configuration
    reset_environment()
    for key, value in env_config.items():
        os.environ[key] = value

    print("Environment variables:")
    for key, value in env_config.items():
        print(f"  {key}={value}")

    # Get logger and show configuration
    logger = mypylogger.get_logger()
    config = mypylogger.LogConfig.from_environment()

    print(f"Logger: {logger.name} (level: {logger.level})")
    print(f"Handlers: {len(logger.handlers)}")
    print(f"Config: app_name={config.app_name}, log_level={config.log_level}")
    print(
        f"        empty_on_run={config.empty_log_file_on_run}, stdout={config.parallel_stdout_logging}"
    )

    # Test logging
    logger.debug("Debug message for testing")
    logger.info("Info message for testing")
    logger.warning("Warning message for testing")
    logger.error("Error message for testing")

    # Check log file
    log_file_path = Path("logs") / f"{config.app_name}_{time.strftime('%Y_%m_%d')}.log"
    if log_file_path.exists():
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            print(f"Log entries written: {len(lines)}")
            if lines:
                try:
                    last_entry = json.loads(lines[-1].strip())
                    print(f"Last entry level: {last_entry['levelname']}")
                except json.JSONDecodeError:
                    print("Last entry: (not JSON)")


def main() -> None:
    """Test various environment configurations."""
    print("=== Environment Variations Example ===")
    print("Testing mypylogger with different environment configurations")

    # Test configurations
    configurations = [
        (
            "Default Configuration",
            {},
            "No environment variables set - should use all defaults",
        ),
        (
            "Custom App Name",
            {"APP_NAME": "custom_app"},
            "Custom application name with other defaults",
        ),
        (
            "Debug Level",
            {"APP_NAME": "debug_app", "LOG_LEVEL": "DEBUG"},
            "Debug level logging - should show all messages",
        ),
        (
            "Error Level Only",
            {"APP_NAME": "error_app", "LOG_LEVEL": "ERROR"},
            "Error level logging - should only show errors and critical",
        ),
        (
            "Stdout Enabled",
            {
                "APP_NAME": "stdout_app",
                "LOG_LEVEL": "INFO",
                "PARALLEL_STDOUT_LOGGING": "INFO",
            },
            "Stdout logging enabled at INFO level",
        ),
        (
            "Stdout Debug Level",
            {
                "APP_NAME": "stdout_debug",
                "LOG_LEVEL": "DEBUG",
                "PARALLEL_STDOUT_LOGGING": "DEBUG",
            },
            "Stdout logging enabled at DEBUG level",
        ),
        (
            "File Truncation Enabled",
            {
                "APP_NAME": "truncate_app",
                "LOG_LEVEL": "INFO",
                "EMPTY_LOG_FILE_ON_RUN": "true",
            },
            "Log file truncated on startup",
        ),
        (
            "Production-like",
            {
                "APP_NAME": "prod_app",
                "LOG_LEVEL": "WARNING",
                "EMPTY_LOG_FILE_ON_RUN": "false",
                "PARALLEL_STDOUT_LOGGING": "false",
            },
            "Production configuration - warnings only, file only",
        ),
        (
            "Development-like",
            {
                "APP_NAME": "dev_app",
                "LOG_LEVEL": "DEBUG",
                "EMPTY_LOG_FILE_ON_RUN": "true",
                "PARALLEL_STDOUT_LOGGING": "DEBUG",
            },
            "Development configuration - debug level, stdout enabled, fresh file",
        ),
        (
            "Invalid Values",
            {
                "APP_NAME": "",
                "LOG_LEVEL": "INVALID_LEVEL",
                "EMPTY_LOG_FILE_ON_RUN": "maybe",
                "PARALLEL_STDOUT_LOGGING": "sometimes",
            },
            "Invalid environment values - should use defaults gracefully",
        ),
    ]

    # Test each configuration
    for name, env_config, description in configurations:
        test_configuration(name, env_config, description)

    # Summary
    print("\n=== Summary ===")
    print("All environment configurations tested successfully!")
    print("Check the logs/ directory for generated log files.")

    # Show all log files created
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"\nLog files created: {len(log_files)}")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"  {log_file.name}: {size} bytes")

    print("\n=== Environment variations example completed ===")


if __name__ == "__main__":
    main()

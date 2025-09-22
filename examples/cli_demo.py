#!/usr/bin/env python3
"""
CLI demo for mypylogger.

This is a command-line interface that demonstrates all mypylogger functionality
and allows interactive testing of different configurations.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import mypylogger
sys.path.insert(0, str(Path(__file__).parent.parent))

import mypylogger


def reset_logger():
    """Reset the singleton logger for fresh configuration."""
    if hasattr(mypylogger.SingletonLogger, '_instance'):
        mypylogger.SingletonLogger._instance = None
        mypylogger.SingletonLogger._logger = None
        mypylogger.SingletonLogger._config = None


def setup_environment(args):
    """Set up environment variables based on CLI arguments."""
    if args.app_name:
        os.environ['APP_NAME'] = args.app_name
    if args.log_level:
        os.environ['LOG_LEVEL'] = args.log_level.upper()
    if args.empty_log_file is not None:
        os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true' if args.empty_log_file else 'false'
    if args.stdout_logging is not None:
        if args.stdout_logging:
            os.environ['PARALLEL_STDOUT_LOGGING'] = args.log_level.upper() if args.log_level else 'INFO'
        else:
            os.environ['PARALLEL_STDOUT_LOGGING'] = 'false'


def show_configuration():
    """Display current configuration."""
    config = mypylogger.LogConfig.from_environment()
    logger = mypylogger.get_logger()
    
    print("Current Configuration:")
    print(f"  App Name: {config.app_name}")
    print(f"  Log Level: {config.log_level} (numeric: {config.get_log_level_int()})")
    print(f"  Empty Log File on Run: {config.empty_log_file_on_run}")
    print(f"  Parallel Stdout Logging: {config.parallel_stdout_logging}")
    print(f"  Logger Name: {logger.name}")
    print(f"  Logger Level: {logger.level}")
    print(f"  Number of Handlers: {len(logger.handlers)}")
    
    # Show handler details
    for i, handler in enumerate(logger.handlers):
        handler_type = type(handler).__name__
        print(f"    Handler {i + 1}: {handler_type}")


def test_all_log_levels():
    """Test logging at all levels."""
    logger = mypylogger.get_logger()
    
    print("\nTesting all log levels:")
    
    test_messages = [
        (mypylogger.DEBUG, "This is a DEBUG message with detailed information"),
        (mypylogger.INFO, "This is an INFO message about normal operation"),
        (mypylogger.WARNING, "This is a WARNING message about potential issues"),
        (mypylogger.ERROR, "This is an ERROR message about a problem"),
        (mypylogger.CRITICAL, "This is a CRITICAL message about system failure")
    ]
    
    for level, message in test_messages:
        level_name = {
            mypylogger.DEBUG: "DEBUG",
            mypylogger.INFO: "INFO",
            mypylogger.WARNING: "WARNING",
            mypylogger.ERROR: "ERROR",
            mypylogger.CRITICAL: "CRITICAL"
        }[level]
        
        print(f"  Logging {level_name}: {message}")
        logger.log(level, message)


def test_structured_logging():
    """Test structured logging with extra fields."""
    logger = mypylogger.get_logger()
    
    print("\nTesting structured logging:")
    
    # User action with context
    logger.info("User login successful", extra={
        'user_id': 12345,
        'username': 'john_doe',
        'ip_address': '192.168.1.100',
        'duration_ms': 150
    })
    
    # API request with metrics
    logger.info("API request processed", extra={
        'method': 'POST',
        'endpoint': '/api/users',
        'status_code': 201,
        'response_time_ms': 45,
        'request_id': 'req-abc123'
    })
    
    # Error with context
    logger.error("Database query failed", extra={
        'query': 'SELECT * FROM users WHERE active = ?',
        'error_code': 'TIMEOUT',
        'retry_count': 3,
        'table': 'users'
    })
    
    print("  Structured log entries created with extra context")


def test_exception_logging():
    """Test exception logging."""
    logger = mypylogger.get_logger()
    
    print("\nTesting exception logging:")
    
    try:
        # Simulate a division by zero error
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=True)
        print("  Exception logged with stack trace")
    
    try:
        # Simulate a file not found error
        with open('nonexistent_file.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError as e:
        logger.warning("File not found", extra={
            'file_path': 'nonexistent_file.txt',
            'operation': 'read'
        }, exc_info=True)
        print("  File error logged with context")


def analyze_log_file():
    """Analyze the generated log file."""
    config = mypylogger.LogConfig.from_environment()
    log_file_path = Path("logs") / f"{config.app_name}_{time.strftime('%Y_%m_%d')}.log"
    
    if not log_file_path.exists():
        print(f"\nNo log file found at: {log_file_path}")
        return
    
    print(f"\nAnalyzing log file: {log_file_path}")
    
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
    
    print(f"Total log entries: {len(lines)}")
    print(f"File size: {log_file_path.stat().st_size} bytes")
    
    # Parse JSON entries and analyze
    json_entries = []
    for line in lines:
        try:
            entry = json.loads(line.strip())
            json_entries.append(entry)
        except json.JSONDecodeError:
            continue
    
    if json_entries:
        print(f"Valid JSON entries: {len(json_entries)}")
        
        # Count by level
        level_counts = {}
        for entry in json_entries:
            level = entry.get('levelname', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("Entries by level:")
        for level, count in sorted(level_counts.items()):
            print(f"  {level}: {count}")
        
        # Show sample entries
        print("\nSample log entries:")
        for i, entry in enumerate(json_entries[:3], 1):
            print(f"  {i}. {entry['levelname']}: {entry['message']}")
            if 'time' in entry:
                print(f"     Time: {entry['time']}")
            if any(key not in ['time', 'levelname', 'message', 'filename', 'lineno', 'funcName'] 
                   for key in entry.keys()):
                extra_fields = {k: v for k, v in entry.items() 
                              if k not in ['time', 'levelname', 'message', 'filename', 'lineno', 'funcName']}
                if extra_fields:
                    print(f"     Extra: {extra_fields}")


def run_performance_test(num_messages=1000):
    """Run a performance test with many log messages."""
    logger = mypylogger.get_logger()
    
    print(f"\nRunning performance test with {num_messages} messages...")
    
    start_time = time.time()
    
    for i in range(num_messages):
        if i % 4 == 0:
            logger.debug(f"Debug message {i}")
        elif i % 4 == 1:
            logger.info(f"Info message {i}")
        elif i % 4 == 2:
            logger.warning(f"Warning message {i}")
        else:
            logger.error(f"Error message {i}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Performance test completed:")
    print(f"  Messages: {num_messages}")
    print(f"  Duration: {duration:.3f} seconds")
    print(f"  Rate: {num_messages / duration:.1f} messages/second")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="CLI demo for mypylogger - test all functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --app-name myapp --log-level debug --stdout-logging
  %(prog)s --app-name prod --log-level warning --no-stdout-logging
  %(prog)s --performance-test 5000
  %(prog)s --show-config-only
        """
    )
    
    parser.add_argument('--app-name', help='Application name for logging')
    parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                       help='Logging level')
    parser.add_argument('--empty-log-file', action='store_true',
                       help='Empty log file on startup')
    parser.add_argument('--no-empty-log-file', dest='empty_log_file', action='store_false',
                       help='Do not empty log file on startup')
    parser.add_argument('--stdout-logging', action='store_true',
                       help='Enable stdout logging')
    parser.add_argument('--no-stdout-logging', dest='stdout_logging', action='store_false',
                       help='Disable stdout logging')
    parser.add_argument('--show-config-only', action='store_true',
                       help='Only show configuration, do not run tests')
    parser.add_argument('--performance-test', type=int, metavar='N',
                       help='Run performance test with N messages')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only analyze existing log file')
    
    args = parser.parse_args()
    
    print("=== mypylogger CLI Demo ===\n")
    
    # Set up environment
    reset_logger()
    setup_environment(args)
    
    # Show configuration
    show_configuration()
    
    if args.show_config_only:
        return
    
    if args.analyze_only:
        analyze_log_file()
        return
    
    if args.performance_test:
        run_performance_test(args.performance_test)
        analyze_log_file()
        return
    
    # Run all tests
    test_all_log_levels()
    test_structured_logging()
    test_exception_logging()
    
    # Analyze results
    analyze_log_file()
    
    print("\n=== CLI demo completed ===")
    print("Check the logs/ directory for generated log files.")


if __name__ == "__main__":
    main()
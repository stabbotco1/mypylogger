# mypylogger Examples

This directory contains example scripts demonstrating various features and usage patterns of mypylogger.

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the core functionality of mypylogger:
- Getting a logger instance
- Logging at different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- JSON formatted output
- File and stdout logging
- Structured logging with extra context
- Exception logging

**Usage:**
```bash
python examples/basic_usage.py
```

**Configuration:**
- APP_NAME: basic_example
- LOG_LEVEL: DEBUG
- PARALLEL_STDOUT_LOGGING: INFO
- EMPTY_LOG_FILE_ON_RUN: true

### 2. Development Mode (`development_mode.py`)

Shows mypylogger configured for development environments:
- Debug level logging for detailed information
- Real-time stdout logging for immediate feedback
- Log file truncation on startup for fresh logs
- Simulated development workflow with request processing

**Usage:**
```bash
python examples/development_mode.py
```

**Configuration:**
- APP_NAME: dev_server
- LOG_LEVEL: DEBUG
- PARALLEL_STDOUT_LOGGING: DEBUG
- EMPTY_LOG_FILE_ON_RUN: true

### 3. Production Mode (`production_mode.py`)

Demonstrates mypylogger configured for production environments:
- Warning level logging for reduced verbosity
- File-only logging (no console output)
- Log file persistence across runs
- Structured JSON output for log analysis
- Log analysis functionality

**Usage:**
```bash
python examples/production_mode.py
```

**Configuration:**
- APP_NAME: prod_service
- LOG_LEVEL: WARNING
- PARALLEL_STDOUT_LOGGING: false
- EMPTY_LOG_FILE_ON_RUN: false

### 4. Environment Variations (`environment_variations.py`)

Tests mypylogger with different environment variable combinations:
- Default configuration (no env vars)
- Custom app names and log levels
- Various stdout logging configurations
- File truncation settings
- Invalid environment values (graceful handling)

**Usage:**
```bash
python examples/environment_variations.py
```

**Features:**
- Tests 10 different configuration scenarios
- Demonstrates graceful degradation with invalid values
- Shows configuration flexibility

### 5. CLI Demo (`cli_demo.py`)

Interactive command-line interface for testing all mypylogger functionality:
- Configurable via command-line arguments
- Performance testing capabilities
- Log file analysis
- Complete workflow testing

**Usage:**
```bash
# Show help
python examples/cli_demo.py --help

# Basic usage with custom configuration
python examples/cli_demo.py --app-name myapp --log-level debug --stdout-logging

# Production-like configuration
python examples/cli_demo.py --app-name prod --log-level warning --no-stdout-logging

# Performance test
python examples/cli_demo.py --performance-test 5000

# Show configuration only
python examples/cli_demo.py --show-config-only

# Analyze existing log file
python examples/cli_demo.py --analyze-only
```

**Features:**
- All log level testing
- Structured logging examples
- Exception logging demonstrations
- Performance benchmarking
- JSON log analysis

## Common Patterns

### Environment Configuration

All examples use environment variables for configuration:

```bash
export APP_NAME="my_application"
export LOG_LEVEL="INFO"
export PARALLEL_STDOUT_LOGGING="INFO"
export EMPTY_LOG_FILE_ON_RUN="false"
```

### Basic Logger Usage

```python
import mypylogger

# Get logger instance
logger = mypylogger.get_logger()

# Basic logging
logger.info("Application started")
logger.error("An error occurred")

# Structured logging
logger.info("User action", extra={
    'user_id': 12345,
    'action': 'login',
    'duration_ms': 150
})

# Exception logging
try:
    risky_operation()
except Exception:
    logger.error("Operation failed", exc_info=True)
```

### Configuration Patterns

#### Development Configuration
```python
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['PARALLEL_STDOUT_LOGGING'] = 'DEBUG'
os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true'
```

#### Production Configuration
```python
os.environ['LOG_LEVEL'] = 'WARNING'
os.environ['PARALLEL_STDOUT_LOGGING'] = 'false'
os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'false'
```

## Log File Locations

All examples create log files in the `logs/` directory with the format:
```
logs/{APP_NAME}_{YYYY_MM_DD}.log
```

For example:
- `logs/basic_example_2025_09_22.log`
- `logs/dev_server_2025_09_22.log`
- `logs/prod_service_2025_09_22.log`

## JSON Output Format

All log entries are formatted as JSON with a consistent schema:

```json
{
  "time": "2025-09-22T16:58:18.643Z",
  "levelname": "INFO",
  "message": "User login successful",
  "filename": "example.py",
  "lineno": "42",
  "funcName": "main",
  "user_id": 12345,
  "action": "login"
}
```

### Field Descriptions

- `time`: UTC timestamp in ISO8601 format with milliseconds
- `levelname`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message`: The log message
- `filename`: Source file name (basename only)
- `lineno`: Line number as string
- `funcName`: Function name where log was called
- Additional fields from `extra` parameter are included

## Running All Examples

To run all examples in sequence:

```bash
# Run basic examples
python examples/basic_usage.py
python examples/development_mode.py
python examples/production_mode.py
python examples/environment_variations.py

# Run CLI demo with different configurations
python examples/cli_demo.py --app-name demo1 --log-level info --stdout-logging
python examples/cli_demo.py --performance-test 1000
```

## Performance Characteristics

Based on the CLI demo performance tests:
- **Throughput**: ~100,000+ messages/second
- **File I/O**: Immediate flush for real-time visibility
- **Memory**: Minimal overhead with singleton pattern
- **Thread Safety**: Full concurrent access support

## Troubleshooting

### Log Files Not Created
- Check that the application has write permissions to the current directory
- Verify the `logs/` directory can be created
- Check for file system space issues

### Missing Log Entries
- Verify the log level configuration allows the message level
- Check that handlers are properly configured
- Ensure immediate flush is working for real-time visibility

### Configuration Issues
- Invalid environment values fall back to defaults gracefully
- Empty or missing environment variables use sensible defaults
- Check the configuration output in examples for current settings

## Integration with Applications

These examples can be adapted for use in your applications:

1. **Web Applications**: Use production mode configuration
2. **Development Tools**: Use development mode configuration
3. **CLI Tools**: Use the CLI demo pattern for argument parsing
4. **Services**: Use structured logging for monitoring and analysis
5. **Testing**: Use environment variations pattern for test configurations

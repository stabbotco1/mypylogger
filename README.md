# mypylogger

[![Build Status](https://github.com/stabbotco1/mypylogger/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/stabbotco1/mypylogger/actions)
[![Coverage](https://codecov.io/gh/stabbotco1/mypylogger/branch/main/graph/badge.svg)](https://codecov.io/gh/stabbotco1/mypylogger)
[![Security Scanning](https://github.com/stabbotco1/mypylogger/workflows/Security%20Scanning/badge.svg)](https://github.com/stabbotco1/mypylogger/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mypylogger.svg)](https://badge.fury.io/py/mypylogger)
[![Python versions](https://img.shields.io/pypi/pyversions/mypylogger.svg)](https://pypi.org/project/mypylogger/)
[![Downloads](https://pepy.tech/badge/mypylogger)](https://pepy.tech/project/mypylogger)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/stabbotco1/mypylogger/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/stabbotco1/mypylogger.svg)](https://github.com/stabbotco1/mypylogger/issues)
[![GitHub stars](https://img.shields.io/github/stars/stabbotco1/mypylogger.svg)](https://github.com/stabbotco1/mypylogger/stargazers)

A production-quality Python logging library that provides structured JSON logging with real-time development support and environment-driven configuration.

## Project Status

🚀 **Production Ready** - Comprehensive CI/CD pipeline with automated testing, security scanning, and quality gates  
🔒 **Security First** - Multi-tool security scanning with CodeQL, Trivy, and dependency vulnerability checks  
📊 **High Quality** - 94%+ test coverage with performance benchmarks and automated quality assurance  
⚡ **High Performance** - <1ms latency, >10,000 logs/second throughput, minimal memory footprint  
🛡️ **Enterprise Grade** - OIDC authentication, zero-credential deployments, bank-grade security practices  

## Features

- **Structured JSON Logging**: Consistent JSON format with fixed field order for easy parsing
- **Environment-Driven Configuration**: Configure via environment variables for different deployment environments
- **Real-Time Development Support**: Immediate log flushing for real-time debugging
- **Singleton Pattern**: Consistent logger configuration across your entire application
- **Thread-Safe**: Safe for use in multi-threaded applications
- **Graceful Error Handling**: Continues operation even when log directories can't be created

## Quick Start

### Installation

```bash
pip install mypylogger
```

### Basic Usage

```python
import mypylogger

# Get the configured logger
logger = mypylogger.get_logger()

# Log some messages
logger.info("Application started")
logger.debug("Processing user request")
logger.warning("Low disk space")
logger.error("Failed to connect to database")
```

### JSON Output

Log entries are written as JSON to `logs/{APP_NAME}_{YYYY_MM_DD}.log`:

```json
{"time": "2024-01-15T10:30:45.123Z", "levelname": "INFO", "message": "Application started", "filename": "main.py", "lineno": "42", "funcName": "main"}
{"time": "2024-01-15T10:30:45.456Z", "levelname": "ERROR", "message": "Failed to connect to database", "filename": "main.py", "lineno": "45", "funcName": "connect"}
```

## Configuration

Configure the logger using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name (used for logger name and log file prefix) | `"default_app"` |
| `LOG_LEVEL` | Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `"INFO"` |
| `EMPTY_LOG_FILE_ON_RUN` | Truncate log file on startup (true/false) | `false` |
| `PARALLEL_STDOUT_LOGGING` | Enable stdout logging with minimum level, or "false" to disable | `"false"` |

### Configuration Examples

#### Development Environment
```bash
export APP_NAME="my_app"
export LOG_LEVEL="DEBUG"
export PARALLEL_STDOUT_LOGGING="INFO"
export EMPTY_LOG_FILE_ON_RUN="true"
```

#### Production Environment
```bash
export APP_NAME="my_app_prod"
export LOG_LEVEL="WARNING"
export PARALLEL_STDOUT_LOGGING="false"
export EMPTY_LOG_FILE_ON_RUN="false"
```

## Advanced Usage

### Using the Singleton Directly

```python
from mypylogger import SingletonLogger

# Get logger instance
logger = SingletonLogger.get_logger()

# Check current log level
current_level = SingletonLogger.get_effective_level()
if current_level <= SingletonLogger.DEBUG:
    logger.debug("Debug logging is enabled")
```

### Custom Configuration

```python
from mypylogger.config import LogConfig

# Create custom configuration
config = LogConfig(
    app_name="custom_app",
    log_level="DEBUG",
    empty_log_file_on_run=True,
    parallel_stdout_logging="WARNING"
)

# Configuration is automatically loaded from environment
# when using get_logger()
```

### Working with Log Files

Log files are automatically created in the `logs/` directory with the format:
```
logs/{APP_NAME}_{YYYY_MM_DD}.log
```

Examples:
- `logs/my_app_2024_01_15.log`
- `logs/production_service_2024_01_15.log`

## Development Features

### Real-Time Log Visibility

The `ImmediateFlushFileHandler` ensures log entries are immediately written to disk:

```python
logger.info("This message appears in the log file immediately")
# No need to wait for buffer flush or program exit
```

### Parallel Stdout Logging

Enable console output alongside file logging for development:

```bash
export PARALLEL_STDOUT_LOGGING="DEBUG"
```

```python
logger.info("This appears in both the log file (JSON) and console (text)")
```

### Log File Management

Control log file behavior:

```bash
# Truncate log file on each run (useful for development)
export EMPTY_LOG_FILE_ON_RUN="true"

# Append to existing log file (useful for production)
export EMPTY_LOG_FILE_ON_RUN="false"
```

## Thread Safety

The logger is fully thread-safe and uses the singleton pattern:

```python
import threading
import mypylogger

def worker_function(worker_id):
    logger = mypylogger.get_logger()  # Same instance across all threads
    logger.info(f"Worker {worker_id} started")

# Create multiple threads - they all share the same logger instance
threads = []
for i in range(10):
    thread = threading.Thread(target=worker_function, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Error Handling

The library gracefully handles various error conditions:

- **Missing log directory**: Automatically creates the `logs/` directory
- **Permission errors**: Continues operation without file logging if directory can't be created
- **Invalid configuration**: Uses sensible defaults for invalid environment variable values
- **Handler failures**: Continues with available handlers if some fail to initialize

## JSON Schema

Log entries follow this JSON schema:

```json
{
  "time": "2024-01-15T10:30:45.123Z",     // UTC timestamp with milliseconds
  "levelname": "INFO",                     // Log level name
  "message": "Application started",        // Log message
  "filename": "main.py",                   // Source filename
  "lineno": "42",                         // Line number (as string)
  "funcName": "main"                      // Function name
}
```

## API Reference

### Main Functions

- `mypylogger.get_logger()` → `logging.Logger`: Get the configured logger instance
- `mypylogger.get_effective_level()` → `int`: Get the current logging level

### Classes

- `SingletonLogger`: Core singleton logger class
- `LogConfig`: Configuration management class
- `CustomJsonFormatter`: JSON formatter with fixed field order
- `ImmediateFlushFileHandler`: File handler with immediate flushing
- `ParallelStdoutHandler`: Stdout handler with level filtering

### Constants

- `mypylogger.DEBUG` (10)
- `mypylogger.INFO` (20)
- `mypylogger.WARNING` (30)
- `mypylogger.ERROR` (40)
- `mypylogger.CRITICAL` (50)

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py`: Simple logging setup
- `development_mode.py`: Development configuration with stdout logging
- `production_mode.py`: Production configuration
- `environment_variations.py`: Different environment setups
- `cli_demo.py`: Command-line application example

## Requirements

- Python 3.7+
- `python-json-logger`

## Project Health & Quality Indicators

The badges at the top of this README provide real-time project health information:

- **Build Status**: All tests pass across Python 3.8-3.12 on Ubuntu, macOS, and Windows
- **Coverage**: Maintains >90% test coverage with comprehensive test suite  
- **Security Scanning**: Clean security scans with no known vulnerabilities
- **License**: MIT License for maximum compatibility and commercial use
- **PyPI Version**: Latest version available for `pip install mypylogger`
- **Python Support**: Compatible with Python 3.8+ 
- **Downloads**: Community adoption and usage statistics
- **Code Style**: Consistent formatting with Black code formatter
- **Maintenance**: Actively maintained with regular updates
- **Issues**: Current open issues and community support
- **Stars**: Community appreciation and project popularity

All badges update automatically based on the latest CI/CD pipeline results and community activity.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## GitHub Actions Monitoring

This project includes advanced GitHub Actions pipeline monitoring for local development:

```bash
# Monitor current commit's pipeline status
python scripts/github_pipeline_monitor.py --status-only --repo stabbotco1/mypylogger

# Example output:
# 📊 Pipeline Status
# 📝 Commit: 2f40aaa5
# ✅ Overall Status: SUCCESS
# Workflows:
#   ✅ CI/CD Pipeline: success (1m 23s)
#   ✅ Security Scanning: success (45s)
```

**Setup Required**: You need a GitHub Personal Access Token to use pipeline monitoring.

📖 **[Complete GitHub Token Setup Guide](docs/GITHUB_TOKEN_SETUP.md)** - Step-by-step instructions for secure token configuration

### Quick Setup
1. Create token at https://github.com/settings/tokens with **Actions: Read-only** permission
2. Set environment variable: `export GITHUB_TOKEN=your_token_here`
3. Test: `python scripts/github_pipeline_monitor.py --status-only --repo your-username/your-repo`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Submit a pull request

## Github Repository

<https://github.com/stabbotco1/mypylogger>


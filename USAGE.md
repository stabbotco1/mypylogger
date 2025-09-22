# mypylogger Usage Guide

This guide provides detailed examples and patterns for using mypylogger in various scenarios.

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Environment Configuration](#environment-configuration)
3. [Development Workflows](#development-workflows)
4. [Production Deployment](#production-deployment)
5. [Advanced Patterns](#advanced-patterns)
6. [Troubleshooting](#troubleshooting)

## Basic Setup

### Minimal Example

```python
import mypylogger

# Get logger with default configuration
logger = mypylogger.get_logger()

# Start logging
logger.info("Application started")
logger.debug("This won't appear with default INFO level")
logger.warning("Something might be wrong")
logger.error("Something is definitely wrong")
```

This creates a log file at `logs/default_app_2024_01_15.log` (using current date).

### Checking Configuration

```python
import mypylogger

# Check current log level
level = mypylogger.get_effective_level()
print(f"Current log level: {level}")

# Use constants for comparison
if level <= mypylogger.DEBUG:
    print("Debug logging is enabled")
elif level <= mypylogger.INFO:
    print("Info logging is enabled")
```

## Environment Configuration

### Development Environment

Create a `.env` file or set environment variables:

```bash
# .env file for development
APP_NAME=my_development_app
LOG_LEVEL=DEBUG
EMPTY_LOG_FILE_ON_RUN=true
PARALLEL_STDOUT_LOGGING=DEBUG
```

```python
# Load environment variables (if using python-dotenv)
from dotenv import load_dotenv
load_dotenv()

import mypylogger

logger = mypylogger.get_logger()
logger.debug("Debug message visible in both file and console")
logger.info("Info message")
```

### Production Environment

```bash
# Production environment variables
export APP_NAME="my_production_app"
export LOG_LEVEL="WARNING"
export EMPTY_LOG_FILE_ON_RUN="false"
export PARALLEL_STDOUT_LOGGING="false"
```

```python
import mypylogger

logger = mypylogger.get_logger()
logger.info("This won't appear (below WARNING level)")
logger.warning("This will appear in log file only")
logger.error("Critical error occurred")
```

### Staging Environment

```bash
# Staging environment - balance between dev and prod
export APP_NAME="my_staging_app"
export LOG_LEVEL="INFO"
export EMPTY_LOG_FILE_ON_RUN="false"
export PARALLEL_STDOUT_LOGGING="ERROR"  # Only errors to console
```

## Development Workflows

### Real-Time Log Monitoring

The immediate flush feature allows real-time log monitoring:

```python
import mypylogger
import time

logger = mypylogger.get_logger()

for i in range(10):
    logger.info(f"Processing item {i}")
    time.sleep(1)  # Each log entry appears immediately in the file
```

Monitor in another terminal:
```bash
tail -f logs/default_app_2024_01_15.log
```

### Debug Session Setup

```python
import os
import mypylogger

# Set up debug environment
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['PARALLEL_STDOUT_LOGGING'] = 'DEBUG'
os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true'

logger = mypylogger.get_logger()

def debug_function():
    logger.debug("Entering debug_function")
    
    # Your code here
    data = {"key": "value"}
    logger.debug(f"Processing data: {data}")
    
    try:
        # Some operation
        result = process_data(data)
        logger.debug(f"Operation successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
    finally:
        logger.debug("Exiting debug_function")

def process_data(data):
    # Simulate some processing
    return data["key"].upper()

# Run debug session
debug_function()
```

### Testing with Different Log Levels

```python
import os
import mypylogger

def test_with_log_level(level):
    """Test function with specific log level."""
    os.environ['LOG_LEVEL'] = level
    os.environ['APP_NAME'] = f'test_{level.lower()}'
    
    # Force re-initialization by clearing singleton
    mypylogger.SingletonLogger._instance = None
    mypylogger.SingletonLogger._logger = None
    
    logger = mypylogger.get_logger()
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

# Test different levels
for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    print(f"\nTesting with {level} level:")
    test_with_log_level(level)
```

## Production Deployment

### Docker Container Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set production environment
ENV APP_NAME=my_production_service
ENV LOG_LEVEL=INFO
ENV EMPTY_LOG_FILE_ON_RUN=false
ENV PARALLEL_STDOUT_LOGGING=false

# Create logs directory
RUN mkdir -p logs

CMD ["python", "main.py"]
```

```python
# main.py
import mypylogger
import signal
import sys

logger = mypylogger.get_logger()

def signal_handler(sig, frame):
    logger.info("Received shutdown signal, cleaning up...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    logger.info("Service starting up")
    
    try:
        # Your application logic here
        while True:
            # Service loop
            logger.debug("Service heartbeat")
            time.sleep(60)
            
    except Exception as e:
        logger.critical(f"Service crashed: {e}")
        raise

if __name__ == "__main__":
    main()
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        env:
        - name: APP_NAME
          value: "my-k8s-app"
        - name: LOG_LEVEL
          value: "INFO"
        - name: EMPTY_LOG_FILE_ON_RUN
          value: "false"
        - name: PARALLEL_STDOUT_LOGGING
          value: "false"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

### Log Aggregation Setup

```python
# For log aggregation systems like ELK stack
import mypylogger
import json

logger = mypylogger.get_logger()

# Add structured data to logs
def log_with_context(level, message, **context):
    """Log with additional context for aggregation."""
    # The JSON formatter will include all extra fields
    getattr(logger, level.lower())(message, extra=context)

# Usage
log_with_context('info', 'User login', 
                user_id=12345, 
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0...')

log_with_context('error', 'Database connection failed',
                database='users',
                connection_pool='primary',
                retry_count=3)
```

## Advanced Patterns

### Multi-Module Applications

```python
# main.py
import mypylogger
from modules import user_service, data_processor

logger = mypylogger.get_logger()

def main():
    logger.info("Application starting")
    
    # All modules will use the same logger configuration
    user_service.process_users()
    data_processor.process_data()
    
    logger.info("Application finished")

if __name__ == "__main__":
    main()
```

```python
# modules/user_service.py
import mypylogger

# Same logger instance as main.py
logger = mypylogger.get_logger()

def process_users():
    logger.info("Starting user processing")
    # Processing logic here
    logger.info("User processing completed")
```

```python
# modules/data_processor.py
import mypylogger

logger = mypylogger.get_logger()

def process_data():
    logger.info("Starting data processing")
    # Processing logic here
    logger.info("Data processing completed")
```

### Error Handling with Context

```python
import mypylogger
import traceback

logger = mypylogger.get_logger()

def process_file(filename):
    logger.info(f"Processing file: {filename}")
    
    try:
        with open(filename, 'r') as f:
            data = f.read()
            # Process data
            logger.info(f"Successfully processed {len(data)} characters")
            
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise
    except PermissionError:
        logger.error(f"Permission denied: {filename}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {filename}: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        raise

# Usage
try:
    process_file("data.txt")
except Exception:
    logger.critical("File processing failed, shutting down")
```

### Performance Monitoring

```python
import mypylogger
import time
from functools import wraps

logger = mypylogger.get_logger()

def log_performance(func):
    """Decorator to log function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper

@log_performance
def slow_operation():
    time.sleep(2)
    return "completed"

# Usage
result = slow_operation()
```

### Configuration Validation

```python
import mypylogger
from mypylogger.config import LogConfig

def validate_configuration():
    """Validate current logging configuration."""
    config = LogConfig.from_environment()
    logger = mypylogger.get_logger()
    
    logger.info("Validating logging configuration")
    logger.info(f"App name: {config.app_name}")
    logger.info(f"Log level: {config.log_level}")
    logger.info(f"Empty log file on run: {config.empty_log_file_on_run}")
    logger.info(f"Parallel stdout logging: {config.parallel_stdout_logging}")
    
    # Test all log levels
    logger.debug("Debug level test")
    logger.info("Info level test")
    logger.warning("Warning level test")
    logger.error("Error level test")
    logger.critical("Critical level test")
    
    logger.info("Configuration validation completed")

if __name__ == "__main__":
    validate_configuration()
```

## Troubleshooting

### Common Issues

#### 1. No Log File Created

**Problem**: Logger works but no log file is created.

**Solution**: Check permissions and directory creation:

```python
import os
import mypylogger

# Check if logs directory exists and is writable
logs_dir = "logs"
if not os.path.exists(logs_dir):
    print(f"Logs directory doesn't exist: {logs_dir}")
    try:
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    except PermissionError:
        print(f"Permission denied creating: {logs_dir}")

# Test logging
logger = mypylogger.get_logger()
logger.info("Test message")
```

#### 2. Logs Not Appearing in Real-Time

**Problem**: Log entries don't appear immediately in the file.

**Solution**: The library uses immediate flush by default. If logs still don't appear:

```python
import mypylogger
import time

logger = mypylogger.get_logger()
logger.info("Test message 1")

# Force a small delay to ensure file system sync
time.sleep(0.1)

# Check if file exists
import os
from datetime import datetime
log_file = f"logs/default_app_{datetime.now().strftime('%Y_%m_%d')}.log"
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        print("Log file contents:")
        print(f.read())
else:
    print(f"Log file not found: {log_file}")
```

#### 3. Environment Variables Not Working

**Problem**: Environment variables are set but not being used.

**Solution**: Verify environment variable loading:

```python
import os
import mypylogger
from mypylogger.config import LogConfig

# Check environment variables
print("Environment variables:")
for var in ['APP_NAME', 'LOG_LEVEL', 'EMPTY_LOG_FILE_ON_RUN', 'PARALLEL_STDOUT_LOGGING']:
    value = os.environ.get(var, 'NOT SET')
    print(f"  {var}: {value}")

# Check parsed configuration
config = LogConfig.from_environment()
print(f"\nParsed configuration:")
print(f"  app_name: {config.app_name}")
print(f"  log_level: {config.log_level}")
print(f"  empty_log_file_on_run: {config.empty_log_file_on_run}")
print(f"  parallel_stdout_logging: {config.parallel_stdout_logging}")

# Test logger
logger = mypylogger.get_logger()
logger.info("Configuration test message")
```

#### 4. Multiple Logger Instances

**Problem**: Getting different logger instances instead of singleton.

**Solution**: The singleton pattern should prevent this, but if you're seeing issues:

```python
import mypylogger

# Get multiple logger instances
logger1 = mypylogger.get_logger()
logger2 = mypylogger.get_logger()

# They should be the same object
print(f"Logger 1 ID: {id(logger1)}")
print(f"Logger 2 ID: {id(logger2)}")
print(f"Same instance: {logger1 is logger2}")

# If they're different, there might be an import issue
# Make sure you're importing from the same module
```

### Debug Mode

Enable debug mode to see internal logging operations:

```python
import logging
import mypylogger

# Enable debug logging for the logging module itself
logging.basicConfig(level=logging.DEBUG)

# Now get your logger
logger = mypylogger.get_logger()
logger.info("Test message")
```

### Log File Analysis

Analyze log files with Python:

```python
import json
from datetime import datetime

def analyze_log_file(filename):
    """Analyze a mypylogger JSON log file."""
    with open(filename, 'r') as f:
        entries = []
        for line in f:
            try:
                entry = json.loads(line.strip())
                entries.append(entry)
            except json.JSONDecodeError:
                print(f"Invalid JSON line: {line.strip()}")
    
    print(f"Total log entries: {len(entries)}")
    
    # Count by level
    levels = {}
    for entry in entries:
        level = entry.get('levelname', 'UNKNOWN')
        levels[level] = levels.get(level, 0) + 1
    
    print("Log levels:")
    for level, count in sorted(levels.items()):
        print(f"  {level}: {count}")
    
    # Show time range
    if entries:
        first_time = entries[0].get('time', 'Unknown')
        last_time = entries[-1].get('time', 'Unknown')
        print(f"Time range: {first_time} to {last_time}")

# Usage
analyze_log_file("logs/my_app_2024_01_15.log")
```

This usage guide covers the most common scenarios and patterns for using mypylogger effectively in different environments and use cases.
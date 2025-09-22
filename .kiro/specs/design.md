# Logging Library Design

## Overview

This document outlines the design for mypylogger, a Python logging library that provides structured JSON logging with environment-driven configuration and real-time development support.

## Architecture

### Core Components

```
mypylogger/
├── __init__.py          # Public API exports
├── core.py              # SingletonLogger class
├── formatters.py        # CustomJsonFormatter
├── handlers.py          # ImmediateFlushFileHandler, ParallelStdoutHandler
└── config.py            # Environment variable handling
```

### Design Decisions

#### Singleton Pattern
- **Decision:** Use singleton pattern for logger management
- **Rationale:** Ensures consistent configuration across application modules and prevents duplicate handlers
- **Implementation:** Static method `get_logger()` returns single instance

#### JSON Formatting
- **Decision:** Fixed field order with custom formatter
- **Rationale:** Predictable log structure for parsing and analysis
- **Implementation:** Extend `pythonjsonlogger.JsonFormatter` with custom field processing, ensuring timestamp is always first field

#### Immediate Flush
- **Decision:** Custom file handler with immediate flush
- **Rationale:** Real-time log visibility for development debugging
- **Implementation:** Override `emit()` method to call `flush()` after each write

## Components and Interfaces

### SingletonLogger Class

```python
class SingletonLogger:
    @staticmethod
    def get_logger() -> logging.Logger
    
    @staticmethod
    def get_effective_level() -> int
    
    # Expose logging constants
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
```

### CustomJsonFormatter Class

```python
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def parse(self) -> List[str]
    def process_log_record(self, log_record: dict) -> dict
```

**Field Processing:**
- Add UTC timestamp with milliseconds
- Convert line numbers to strings
- Normalize null values
- Remove unwanted fields

### Handler Classes

```python
class ImmediateFlushFileHandler(logging.FileHandler):
    def emit(self, record: logging.LogRecord) -> None

class ParallelStdoutHandler(logging.StreamHandler):
    def __init__(self, stdout_level: int)
    def emit(self, record: logging.LogRecord) -> None
```

## Data Models

### Log Record Schema

```json
{
  "time": "2024-01-15T10:30:45.123Z",
  "levelname": "INFO",
  "message": "Application started",
  "filename": "main.py",
  "lineno": "42",
  "funcName": "main"
}
```

### Configuration Model

```python
@dataclass
class LogConfig:
    app_name: str = "default_app"
    log_level: str = "INFO"
    empty_log_file_on_run: bool = False
    parallel_stdout_logging: str = "false"
```

## Error Handling

### File System Errors
- **Strategy:** Graceful degradation
- **Implementation:** If logs directory cannot be created, log error and continue
- **Fallback:** Use temporary directory or current working directory

### Configuration Errors
- **Strategy:** Use defaults with warnings
- **Implementation:** Invalid log levels default to INFO with warning message
- **Validation:** Environment variable parsing with type checking

### Handler Errors
- **Strategy:** Continue operation without failed handlers
- **Implementation:** Catch exceptions during handler setup
- **Logging:** Log handler failures to stderr

## Testing Strategy

### Unit Tests
- Test singleton behavior (single instance, thread safety)
- Test JSON formatter output and field processing
- Test handler flush behavior and stdout filtering
- Test configuration parsing and defaults

### Integration Tests
- Test complete logger setup with various configurations
- Test file creation and writing
- Test environment variable override behavior
- Test error conditions and graceful degradation

### Test Structure
```
tests/
├── unit/
│   ├── test_singleton.py
│   ├── test_formatters.py
│   ├── test_handlers.py
│   └── test_config.py
└── integration/
    ├── test_logger_setup.py
    └── test_file_operations.py
```
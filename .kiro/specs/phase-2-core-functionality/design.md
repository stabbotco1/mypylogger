# Design Document

## Overview

Phase 2 implements the core mypylogger functionality, providing a simple `get_logger()` API that returns JSON-configured loggers with comprehensive source location tracking, environment-based configuration, and graceful error handling. The design emphasizes reliability, simplicity, and compatibility with existing Python logging infrastructure.

## Architecture

### Core Components Architecture

```
mypylogger/
├── __init__.py           # Public API (get_logger function)
├── core.py              # Core logger creation and configuration logic
├── config.py            # Environment variable handling and defaults
├── formatters.py        # JSON formatter with source location tracking
├── handlers.py          # File and console handler setup with fallbacks
└── exceptions.py        # Custom exceptions for error handling
```

### Data Flow Architecture

```
User Code
    ↓
get_logger(name?) 
    ↓
Config Resolution (env vars + defaults)
    ↓
Logger Creation & Configuration
    ↓
Handler Setup (stdout + optional file)
    ↓
JSON Formatter with Source Location
    ↓
Log Output (JSON to stdout/file)
```

### Error Handling Architecture

```
Primary Operation → Fallback Operation → Final Fallback
File Logging     → Stdout Only      → Stderr Warning
JSON Formatting  → Plain Text       → Basic Format
Directory Create → Temp Directory   → Stdout Only
Config Parsing   → Safe Defaults    → Minimal Config
```

## Components and Interfaces

### Public API (\_\_init\_\_.py)

```python
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with JSON formatting and source location tracking.
    
    Args:
        name: Logger name. If None, uses APP_NAME env var, then calling module's __name__,
              then "mypylogger" as final fallback.
              
    Returns:
        Configured Logger instance with JSON formatting and appropriate handlers.
    """
```

### Core Logger Management (core.py)

```python
class LoggerManager:
    """Manages logger creation and configuration."""
    
    def __init__(self):
        self._configured_loggers: Set[str] = set()
        self._handler_cache: Dict[str, logging.Handler] = {}
    
    def get_or_create_logger(self, name: str) -> logging.Logger:
        """Get existing logger or create new one with full configuration."""
        
    def configure_logger(self, logger: logging.Logger, config: LogConfig) -> None:
        """Apply handlers, formatters, and level configuration to logger.
        
        Prevents handler accumulation by checking if logger is already configured.
        """
        
    def _resolve_logger_name(self, name: Optional[str]) -> str:
        """Resolve logger name using fallback chain: name → APP_NAME → __name__ → "mypylogger"."""
        
    def _is_logger_configured(self, logger_name: str) -> bool:
        """Check if logger has already been configured by mypylogger."""
```

### Configuration Management (config.py)

```python
@dataclass
class LogConfig:
    """Configuration container for logger setup."""
    app_name: str
    log_level: str
    log_to_file: bool
    log_file_dir: Path
    
class ConfigResolver:
    """Resolves configuration from environment variables with safe defaults."""
    
    def resolve_config(self) -> LogConfig:
        """Get configuration from environment with fallback to safe defaults."""
        
    def _get_safe_log_level(self, level_str: str) -> str:
        """Validate and return safe log level."""
        
    def _get_safe_file_dir(self, dir_path: str) -> Path:
        """Validate and return safe file directory path."""
```

### JSON Formatting (formatters.py)

```python
class SourceLocationJSONFormatter(logging.Formatter):
    """JSON formatter with automatic source location tracking."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with source location fields."""
        
    def _extract_source_location(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract module, filename, function_name, and line from call stack."""
        
    def _build_json_record(self, record: logging.LogRecord, location: Dict[str, Any]) -> Dict[str, Any]:
        """Build ordered JSON record with consistent field ordering."""
        
    def _handle_custom_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract and merge custom fields from extra and custom parameters."""
```

### Handler Management (handlers.py)

```python
class HandlerFactory:
    """Creates and configures log handlers with fallback logic."""
    
    def create_console_handler(self) -> logging.StreamHandler:
        """Create stdout handler with JSON formatter."""
        
    def create_file_handler(self, config: LogConfig) -> Optional[logging.FileHandler]:
        """Create file handler with graceful fallback on failure."""
        
    def _generate_log_filename(self, config: LogConfig) -> str:
        """Generate log filename using pattern {APP_NAME}_{date}_{hour}.log."""
        
    def _ensure_log_directory(self, log_dir: Path) -> bool:
        """Create log directory with fallback handling."""
```

## Data Models

### JSON Log Record Structure

```json
{
  "timestamp": "2025-01-21T10:30:45.123456Z",
  "level": "INFO",
  "message": "User authentication successful",
  "module": "myapp.services.auth",
  "filename": "services/auth.py", 
  "function_name": "authenticate_user",
  "line": 42,
  "user_id": 12345,
  "session_id": "abc123"
}
```

**Field Specifications:**
- **timestamp**: ISO 8601 with microsecond precision, always first field
- **level**: Standard Python logging level names
- **message**: The actual log message
- **module**: Full module path (e.g., "myapp.services.auth")
- **filename**: Relative file path (e.g., "services/auth.py")
- **function_name**: Function where logging call originated
- **line**: Line number of logging call
- **Custom fields**: Any additional fields from `extra` or `custom` parameters

### Configuration Data Model

```python
@dataclass
class LogConfig:
    app_name: str = "mypylogger"
    log_level: str = "INFO"
    log_to_file: bool = False
    log_file_dir: Path = Path("/tmp")
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        "APP_NAME": "app_name",
        "LOG_LEVEL": "log_level", 
        "LOG_TO_FILE": "log_to_file",
        "LOG_FILE_DIR": "log_file_dir"
    }
```

### Source Location Data Model

```python
@dataclass
class SourceLocation:
    module: str
    filename: str
    function_name: str
    line: int
    
    @classmethod
    def extract_from_stack(cls, skip_frames: int = 3) -> 'SourceLocation':
        """Extract source location from call stack."""
```

## Error Handling

### Graceful Degradation Strategy

**File Logging Failures:**
```python
try:
    file_handler = create_file_handler(config)
    logger.addHandler(file_handler)
except (OSError, PermissionError) as e:
    # Fall back to stdout only
    # Log library errors to stderr using a separate stderr handler
    _log_library_error(f"File logging failed, using stdout only: {e}")
    # Continue with console handler only
```

**JSON Formatting Failures:**
```python
try:
    json_output = json.dumps(log_record, ensure_ascii=False)
    return json_output
except (TypeError, ValueError, RecursionError) as e:
    # Fall back to plain text - NEVER raise exceptions
    _log_library_error(f"JSON formatting failed, using plain text: {e}")
    return f"{record.levelname}: {record.getMessage()}"
except Exception as e:
    # Catch-all for any unexpected errors
    return f"{record.levelname}: {record.getMessage()}"
```

**Directory Creation Failures:**
```python
try:
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
except OSError as e:
    _log_library_error(f"Failed to create log directory {log_dir}: {e}")
    # Try temp directory
    try:
        temp_dir = Path("/tmp/mypylogger")
        temp_dir.mkdir(exist_ok=True)
        _log_library_error(f"Using temporary directory: {temp_dir}")
        return temp_dir
    except OSError as e2:
        _log_library_error(f"Failed to create temp directory: {e2}")
        # Final fallback to stdout only - never raise
        return None
```

### Exception Hierarchy

```python
class MypyloggerError(Exception):
    """Base exception for mypylogger errors."""
    
class ConfigurationError(MypyloggerError):
    """Configuration-related errors."""
    
class FormattingError(MypyloggerError):
    """JSON formatting errors."""
    
class HandlerError(MypyloggerError):
    """Handler setup errors."""
```

### Library Error Logging

```python
def _log_library_error(message: str) -> None:
    """Log mypylogger internal errors to stderr without affecting user logging."""
    # Use a dedicated stderr handler for library errors
    # This ensures library errors are visible but don't interfere with user logs
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter('mypylogger: %(message)s'))
    
    # Create temporary logger for library errors
    lib_logger = logging.getLogger('mypylogger._internal')
    lib_logger.addHandler(stderr_handler)
    lib_logger.setLevel(logging.WARNING)
    lib_logger.warning(message)
    
    # Clean up to avoid handler accumulation
    lib_logger.removeHandler(stderr_handler)
```

## Testing Strategy

### Unit Testing Strategy

**Core Function Testing:**
- `get_logger()` name resolution logic
- Configuration parsing and validation
- JSON formatting with various input types
- Source location extraction accuracy
- Custom field handling and merging

**Error Handling Testing:**
- File system permission errors
- Invalid JSON serialization scenarios
- Invalid configuration values
- Missing environment variables

**Mocking Strategy:**
- Mock file system operations for handler testing
- Mock environment variables for configuration testing
- Mock call stack for source location testing

### Integration Testing Strategy

**End-to-End Workflows:**
- Complete logging workflow from `get_logger()` to file output
- Environment variable configuration integration
- File and console output verification
- Custom field integration testing

**Real File System Testing:**
- Actual file creation and writing
- Directory creation and permissions
- Log file rotation and naming
- Cleanup and resource management

### Performance Testing

**Benchmarks:**
- Logger initialization time (<10ms target)
- Single log entry time (<1ms target)
- Memory usage with multiple loggers
- File I/O performance with immediate flush

### Quality Gate Integration

**Master Test Script Integration:**
- All unit tests must pass (95%+ coverage)
- All integration tests must pass
- Linting compliance (Ruff)
- Type checking compliance (mypy)
- Code formatting compliance (Ruff format)

## Antipattern Prevention

### Critical Logging Library Antipatterns to Avoid

**1. Exception Propagation:**
- ✅ Never raise exceptions from logging operations
- ✅ Always catch and handle errors gracefully with fallbacks
- ✅ Use try-catch blocks around all I/O operations

**2. Blocking Operations:**
- ✅ Use immediate flush but with timeout protection
- ✅ Implement fallback handlers when primary handlers fail
- ✅ Never perform network I/O synchronously

**3. Global State Modification:**
- ✅ Never call `logging.basicConfig()` or modify root logger
- ✅ Only configure loggers we create, not existing ones
- ✅ Respect existing logging configuration

**4. Handler Accumulation:**
- ✅ Check for existing handlers before adding new ones
- ✅ Use handler caching to prevent duplicates
- ✅ Clean up handlers properly when needed

**5. Resource Leaks:**
- ✅ Properly close file handles and resources
- ✅ Use context managers for file operations
- ✅ Implement proper cleanup in error scenarios

**6. Performance Impact:**
- ✅ Lazy initialization of expensive operations
- ✅ Efficient source location extraction
- ✅ Minimal overhead for disabled log levels

## Implementation Considerations

### Python Logging Integration

**Standard Library Compatibility:**
- Use `logging.getLogger()` internally for logger creation
- Leverage existing `logging.Handler` and `logging.Formatter` base classes
- Maintain compatibility with existing logging configuration

**Logger Hierarchy:**
- Support standard Python logger hierarchy (parent.child)
- Respect logger propagation settings
- Allow integration with existing logging setups
- **Never modify existing loggers or global logging state**

**Handler Management:**
- Check for existing handlers before adding new ones
- Implement handler deduplication to prevent accumulation
- Use handler caching for performance and consistency

### Performance Optimizations

**Lazy Initialization:**
- Create handlers only when first log message is emitted
- Cache configuration resolution results
- Reuse existing loggers when possible

**Efficient Source Location:**
- Minimize call stack inspection overhead
- Cache source location for repeated calls from same location
- Use efficient string operations for path manipulation

### Thread Safety

**Concurrent Access:**
- Use thread-safe logger creation patterns
- Ensure handler setup is atomic
- Protect shared configuration state

This design provides a robust, maintainable foundation for the mypylogger core functionality while maintaining simplicity and reliability.
# Logging Standards and Conventions

## Purpose
This document defines coding standards, naming conventions, and implementation guidelines for the mypylogger library to ensure consistency, maintainability, and adherence to Python best practices.

## Code Style and Formatting

### Python Standards
- **PEP 8**: Follow Python Enhancement Proposal 8 for code style
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Use isort for consistent import ordering
- **Type Hints**: All public functions and methods must include type hints
- **Docstrings**: Use Google-style docstrings for all public APIs

### Formatting Tools
- **Black**: Automatic code formatting
- **isort**: Import statement organization
- **flake8**: Linting and style checking
- **mypy**: Static type checking

## Naming Conventions

### Modules and Packages
- **Package**: `mypylogger` (snake_case)
- **Modules**: `config.py`, `formatters.py`, `handlers.py`, `core.py`
- **Private modules**: Prefix with underscore if internal-only

### Classes
- **Public Classes**: `PascalCase` (e.g., `SingletonLogger`, `CustomJsonFormatter`)
- **Private Classes**: `_PascalCase` (e.g., `_InternalConfig`)
- **Exception Classes**: Suffix with `Error` (e.g., `LoggingConfigError`)

### Functions and Methods
- **Public Functions**: `snake_case` (e.g., `get_logger`, `get_effective_level`)
- **Private Functions**: `_snake_case` (e.g., `_setup_logger`, `_validate_config`)
- **Magic Methods**: Standard Python conventions (`__init__`, `__str__`)

### Variables and Constants
- **Variables**: `snake_case` (e.g., `log_level`, `file_handler`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_LOG_LEVEL`, `MAX_FILE_SIZE`)
- **Environment Variables**: `UPPER_SNAKE_CASE` with descriptive prefixes

### Configuration Variables
- **Environment Variables**: Use `LOG_` prefix for library-specific settings
  - `APP_NAME`: Application identifier
  - `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `LOG_TO_FILE`: Enable file logging (true/false)
  - `LOG_FILE_DIR`: Directory for log files
  - `EMPTY_LOG_FILE_ON_RUN`: Truncate log file on startup
  - `PARALLEL_STDOUT_LOGGING`: Enable stdout mirroring

## JSON Logging Standards

### Field Naming
- **Field Names**: Use `snake_case` for consistency with Python conventions
- **Required Fields**: `time`, `levelname`, `message`, `filename`, `lineno`, `funcName`
- **Field Order**: Fixed order with `time` as first field for parsing efficiency

### Timestamp Format
- **Standard**: ISO 8601 with milliseconds and UTC timezone
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ`
- **Example**: `2024-01-15T10:30:45.123Z`
- **Implementation**: Use `datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'`

### Value Normalization
- **Null Values**: Convert Python `None` to JSON string `"null"`
- **Line Numbers**: Convert integers to strings for consistency
- **Missing Values**: Use `"unknown"` for missing function names
- **Field Removal**: Remove unwanted fields like `taskName`

## Error Handling Standards

### Exception Hierarchy
```python
class LoggingError(Exception):
    """Base exception for logging library errors."""
    pass

class ConfigurationError(LoggingError):
    """Raised when configuration is invalid."""
    pass

class FileSystemError(LoggingError):
    """Raised when file operations fail."""
    pass
```

### Error Handling Patterns
- **Graceful Degradation**: Continue operation when non-critical errors occur
- **Logging Errors**: Log errors to stderr, not to the main log file
- **Configuration Errors**: Use defaults with warning messages
- **File System Errors**: Fall back to alternative locations or stdout

### Error Messages
- **Format**: Clear, actionable error messages with context
- **Example**: `"Failed to create log directory '/logs': Permission denied. Using '/tmp' as fallback."`
- **Logging**: Use standard library logging for internal errors

## File and Directory Structure

### Package Layout
```
mypylogger/
├── __init__.py              # Public API exports
├── core.py                  # SingletonLogger implementation
├── config.py                # Configuration handling
├── formatters.py            # JSON formatter classes
├── handlers.py              # Custom handler classes
├── exceptions.py            # Custom exception classes
└── py.typed                 # Type hint marker file
```

### File Organization
- **One class per file**: Unless classes are tightly coupled
- **Logical grouping**: Related functionality in same module
- **Clear separation**: Public API separate from implementation details

## Logging Behavior Standards

### Singleton Implementation
- **Thread Safety**: Use threading.Lock for singleton creation
- **Instance Management**: Store instance as class variable
- **Initialization**: Lazy initialization on first access
- **Prevention**: Raise exception if direct instantiation attempted

### Handler Configuration
- **File Handler**: Always use immediate flush for development visibility
- **Stdout Handler**: Optional, configurable by level
- **Handler Reuse**: Prevent duplicate handlers on same logger
- **Error Recovery**: Continue with available handlers if some fail

### Performance Considerations
- **Immediate Flush**: Accept performance trade-off for real-time visibility
- **Memory Usage**: Minimize memory footprint of log records
- **Thread Safety**: Use Python logging's built-in thread safety
- **Lazy Loading**: Load configuration only when needed

## Testing Standards

### Test Organization
```
tests/
├── unit/
│   ├── test_core.py
│   ├── test_config.py
│   ├── test_formatters.py
│   └── test_handlers.py
├── integration/
│   ├── test_logger_setup.py
│   └── test_file_operations.py
└── conftest.py              # Shared test fixtures
```

### Test Naming
- **Test Files**: `test_<module_name>.py`
- **Test Classes**: `Test<ClassName>`
- **Test Methods**: `test_<behavior>_<expected_result>`
- **Example**: `test_singleton_returns_same_instance`

### Test Coverage
- **Minimum Coverage**: 90% line coverage
- **Critical Paths**: 100% coverage for error handling and configuration
- **Edge Cases**: Test boundary conditions and error scenarios
- **Integration**: Test complete workflows end-to-end

## Documentation Standards

### Docstring Format
```python
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a configured logger instance.

    Args:
        name: Optional logger name. If None, uses APP_NAME from environment.

    Returns:
        Configured logger instance with JSON formatting and appropriate handlers.

    Raises:
        ConfigurationError: If configuration is invalid.

    Example:
        >>> logger = get_logger()
        >>> logger.info("Application started")
    """
```

### API Documentation
- **Public Functions**: Complete docstrings with examples
- **Parameters**: Document all parameters with types and defaults
- **Return Values**: Document return types and possible values
- **Exceptions**: Document all exceptions that may be raised

## Security and Privacy Standards

### Log Content Security
- **Sensitive Data**: Never log passwords, tokens, or personal information
- **Data Sanitization**: Provide hooks for sanitizing log content
- **File Permissions**: Create log files with appropriate permissions (644)
- **Directory Security**: Ensure log directory is not world-writable

### Configuration Security
- **Environment Variables**: Validate all environment variable inputs
- **Path Validation**: Validate file paths to prevent directory traversal
- **Default Security**: Use secure defaults for all configuration options

## Compatibility Standards

### Python Version Support
- **Minimum Version**: Python 3.8+
- **Type Hints**: Use modern type hint syntax
- **Dependencies**: Minimize external dependencies
- **Standard Library**: Prefer standard library over third-party when possible

### Dependency Management
- **Core Dependencies**: `python-json-logger` for JSON formatting
- **Development Dependencies**: `pytest`, `black`, `isort`, `flake8`, `mypy`
- **Version Pinning**: Use compatible version ranges, not exact pins
- **Security**: Regularly update dependencies for security patches

# Requirements Document

## Introduction

This document defines the requirements for Phase 2 of mypylogger v0.2.7 development, focusing on implementing the core JSON logging functionality with environment-based configuration, graceful error handling, and comprehensive source location tracking.

## Glossary

- **get_logger**: Main API function that returns a configured logger instance
- **JSON Formatter**: Custom formatter that outputs structured JSON with consistent field ordering
- **Source Location**: Module, filename, function name, and line number where logging call originated
- **Graceful Degradation**: Fallback behavior when preferred operations fail (file → stdout, JSON → plain text)
- **Environment Configuration**: Configuration via environment variables with safe defaults
- **Custom Fields**: Additional metadata added via `extra` or `custom` parameters
- **Handler**: Python logging component that determines where log messages are sent (file, stdout, stderr)

## Requirements

### Requirement 1

**User Story:** As a developer, I want a simple `get_logger()` function, so that I can quickly get a configured JSON logger for my module.

#### Acceptance Criteria

1. THE mypylogger package SHALL provide a `get_logger()` function with optional name parameter
2. WHEN `get_logger()` is called without arguments, THE system SHALL use APP_NAME environment variable if available
3. WHEN APP_NAME is not set, THE system SHALL fall back to the calling module's `__name__`
4. WHEN both APP_NAME and `__name__` are unavailable, THE system SHALL use "mypylogger" as final fallback
5. THE `get_logger()` function SHALL return a standard Python logging.Logger instance

### Requirement 2

**User Story:** As a developer, I want consistent JSON log output, so that my logs can be easily parsed by log aggregation services.

#### Acceptance Criteria

1. THE JSON formatter SHALL output logs with consistent field ordering starting with timestamp
2. THE JSON output SHALL include timestamp, level, message, module, filename, function_name, and line fields
3. THE timestamp field SHALL use ISO 8601 format with microsecond precision
4. THE level field SHALL use standard Python logging level names (DEBUG, INFO, WARNING, ERROR, CRITICAL)
5. THE source location fields SHALL be automatically extracted from the call stack

### Requirement 3

**User Story:** As a developer, I want environment-based configuration, so that I can control logging behavior without code changes.

#### Acceptance Criteria

1. THE system SHALL support APP_NAME environment variable for default logger naming
2. THE system SHALL support LOG_LEVEL environment variable (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. THE system SHALL support LOG_TO_FILE environment variable (true/false) for file output control
4. THE system SHALL support LOG_FILE_DIR environment variable for log file directory location
5. THE system SHALL provide safe defaults when environment variables are not set

### Requirement 4

**User Story:** As a developer, I want both file and console logging, so that I can see logs during development and persist them for analysis.

#### Acceptance Criteria

1. THE system SHALL output logs to stdout by default
2. WHEN LOG_TO_FILE is true, THE system SHALL also write logs to files in LOG_FILE_DIR
3. THE log files SHALL be named using pattern {APP_NAME}_{date}_{hour}.log
4. THE system SHALL create log directories if they do not exist
5. THE system SHALL use immediate flush for real-time log visibility

### Requirement 5

**User Story:** As a developer, I want graceful error handling, so that logging failures never crash my application.

#### Acceptance Criteria

1. IF file logging fails, THEN THE system SHALL fall back to stdout only
2. IF JSON formatting fails, THEN THE system SHALL fall back to plain text output
3. IF log directory creation fails, THEN THE system SHALL fall back to stdout and stderr
4. IF configuration is invalid, THEN THE system SHALL use safe defaults
5. THE system SHALL log its own errors using a dedicated internal logger to stderr without causing application failure

### Requirement 6

**User Story:** As a developer, I want to add custom metadata to logs, so that I can include context-specific information.

#### Acceptance Criteria

1. THE system SHALL support custom fields via the standard `extra` parameter
2. THE system SHALL support custom fields via a `custom` parameter for convenience
3. THE custom fields SHALL be merged into the JSON output alongside standard fields
4. THE custom fields SHALL not override standard fields (timestamp, level, message, etc.)
5. THE system SHALL handle custom field serialization errors gracefully

### Requirement 7

**User Story:** As a developer, I want flexible log level configuration, so that I can control verbosity globally and per-logger.

#### Acceptance Criteria

1. THE system SHALL respect LOG_LEVEL environment variable as global default
2. THE system SHALL allow per-logger level configuration via setLevel() method
3. THE per-logger configuration SHALL override the global LOG_LEVEL setting
4. THE system SHALL support all standard Python logging levels
5. THE system SHALL default to INFO level when no configuration is provided

### Requirement 8

**User Story:** As a developer, I want comprehensive source location tracking, so that I can quickly identify where log messages originated.

#### Acceptance Criteria

1. THE system SHALL automatically extract module name from the call stack
2. THE system SHALL automatically extract relative filename from the call stack
3. THE system SHALL automatically extract function name from the call stack
4. THE system SHALL automatically extract line number from the call stack
5. THE source location extraction SHALL work correctly with nested function calls
# Development Workflow

## Purpose

This document defines the specific development workflow patterns for mypylogger v0.2.4, emphasizing TDD methodology and UV-based environment management.

## Core Development Principles

### 1. Test-Driven Development (TDD)
**MANDATORY:** All code must follow strict TDD cycle

#### TDD Cycle
1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass  
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Continue with next requirement

#### TDD Standards
- **Test first**: No production code without a failing test
- **Minimal implementation**: Write just enough code to pass the test
- **Refactor safely**: Tests provide safety net for improvements
- **Fast feedback**: Unit tests should run in <1 second

### 2. Environment Management with UV
**CRITICAL:** All Python commands must use UV

#### UV Command Pattern
```bash
# CORRECT - Always use uv run prefix
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src/
uv run python -m build

# WRONG - Never use bare commands
pytest                    # NO - environment might not be active
python -m pytest        # NO - might use wrong Python
source .venv/bin/activate && pytest  # NO - unnecessary
```

#### UV Project Setup
```bash
# Initial setup (once)
uv init mypylogger
cd mypylogger

# Add dependencies
uv add python-json-logger

# Add development dependencies  
uv add --dev pytest pytest-cov ruff mypy

# Install dependencies
uv sync

# Verify setup
uv run pytest --version
uv run ruff --version
```

### 3. Code Quality Gates
**Before ANY commit, ALL must pass:**

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run mypy src/

# Run tests with coverage
uv run pytest --cov=mypylogger --cov-fail-under=95

# Master test script (when available)
./scripts/run_tests.sh
```

## Task Execution Workflow

### Before Starting Any Task
1. Read requirements, design, and task details completely
2. Understand dependencies and prerequisites  
3. Write failing tests first (TDD approach)
4. Implement minimal solution to pass tests

### During Task Execution
- Focus on single task objective only
- Reference specific requirements mentioned in task
- Maintain code quality standards from steering documents
- Use `uv run` for all Python commands
- Document any deviations or discoveries

### After Task Completion
- Verify all tests pass: `uv run pytest`
- Check code can be imported/executed
- Run quality gates (format, lint, type check)
- Update documentation if needed
- **STOP** and wait for user review before proceeding

## Testing Standards

### Test Categories

#### Unit Tests (Fast - <1s total)
- Test individual functions and classes in isolation
- Mock external dependencies
- 100% coverage of core logic
- Run on every change

```python
def test_get_logger_returns_configured_logger():
    """Test that get_logger returns properly configured logger."""
    logger = get_logger("test_app")
    assert logger.name == "test_app"
    assert len(logger.handlers) > 0
    # Verify JSON formatting is configured
```

#### Integration Tests (Medium - <30s total)  
- Test component interactions
- Use real dependencies (filesystem, etc.)
- Cover critical user workflows
- Run before commits

```python
def test_file_logging_workflow(tmp_path):
    """Test complete file logging workflow."""
    os.environ["LOG_TO_FILE"] = "true"
    os.environ["LOG_FILE_DIR"] = str(tmp_path)
    
    logger = get_logger("integration_test")
    logger.info("Test message")
    
    log_file = tmp_path / "integration_test.log"
    assert log_file.exists()
    
    content = log_file.read_text()
    log_entry = json.loads(content.strip())
    assert log_entry["message"] == "Test message"
```

### Test Organization
```
tests/
├── unit/
│   ├── test_core.py           # get_logger() tests
│   ├── test_config.py         # Configuration tests  
│   ├── test_formatters.py     # JSON formatter tests
│   └── test_exceptions.py     # Exception tests
├── integration/
│   ├── test_end_to_end.py     # Complete workflows
│   └── test_file_operations.py # File logging scenarios
└── conftest.py                # Shared fixtures
```

### Running Tests
```bash
# All tests with coverage
uv run pytest --cov=mypylogger --cov-report=term-missing --cov-fail-under=95

# Unit tests only (fast feedback)
uv run pytest tests/unit/ -v

# Specific test file
uv run pytest tests/unit/test_core.py -v

# Specific test function
uv run pytest tests/unit/test_core.py::test_get_logger_with_name -v
```

## Code Quality Standards

### Formatting and Linting
```bash
# Auto-format code
uv run ruff format .

# Check and auto-fix linting issues
uv run ruff check --fix .

# Verify formatting compliance
uv run ruff format --check .

# Check remaining linting issues
uv run ruff check .
```

### Type Checking
```bash
# Run type checker
uv run mypy src/

# Type hints required for all public functions
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger with type hints."""
    pass
```

### Documentation Standards
```python
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with JSON formatting.
    
    Args:
        name: Logger name. If None, uses APP_NAME from environment
              or falls back to calling module's __name__.
              
    Returns:
        Logger instance configured with JSON formatting and
        appropriate handlers.
        
    Raises:
        ConfigurationError: If configuration is invalid.
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        {"time":"2025-01-21T10:30:45.123456Z","levelname":"INFO",...}
    """
```

## Error Handling Philosophy

### Graceful Degradation
- Log operations should never crash the application
- Fall back to safe defaults when operations fail
- Provide clear error messages with actionable information
- Use stderr for library's own error messages

```python
# Example: File logging fallback
try:
    log_file = Path("/logs/app.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    # Fall back to /tmp
    try:
        log_file = Path("/tmp/app.log")
    except (OSError, PermissionError):
        # Fall back to stdout only
        log_file = None
        print("WARNING: Could not create log file, using stdout only",
              file=sys.stderr)
```

## Git Workflow

### Commit Standards
Use conventional commit format:
```
type(scope): description

Examples:
feat(core): add get_logger function
fix(formatter): handle None values in JSON
docs(readme): add installation instructions
test(config): add validation tests
refactor(handlers): simplify file handler setup
```

### Commit Frequency
- Commit after each completed TDD cycle (Red → Green → Refactor)
- Ensure all tests pass before committing
- Keep commits focused and atomic
- Each commit should leave codebase in working state

## Performance Expectations

### "Fast Enough" Targets
- Logger initialization: <10ms
- Single log entry: <1ms (with immediate flush)
- Module import: <100ms
- Test suite: <5 seconds (unit tests)

### Not Performance Critical
We do NOT optimize for:
- High-frequency logging (>10k/sec)
- Minimal memory footprint
- Fastest possible throughput

If users need extreme performance, they should use specialized solutions.

## Agent-Specific Guidelines

### What Agents Should Do
- Follow TDD strictly (test first, then code)
- Use `uv run` for all Python commands
- Focus on one task at a time
- Stop and wait for review after each task
- Reference specific requirements from specs

### What Agents Should Avoid
- Implementing features not in specs
- Skipping tests to "save time"
- Adding "helpful" features without asking
- Breaking working code to add enhancements
- Using bare Python commands (always use `uv run`)

### Success Pattern for Agents
1. Read ALL steering docs and relevant specs
2. Understand complete task before starting
3. Write failing test first
4. Implement minimal code to pass test
5. Verify code works: `uv run pytest`
6. Run quality gates
7. **STOP** and wait for user review
8. Only proceed after explicit approval

This workflow ensures consistent, high-quality development while maintaining the project's focus and simplicity.
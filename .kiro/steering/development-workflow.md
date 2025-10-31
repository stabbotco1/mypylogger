---
inclusion: always
---

# Development Workflow

This document defines the specific development workflow patterns for mypylogger v0.2.7, emphasizing TDD methodology and UV-based environment management.

## Core Development Principles

### Test-Driven Development (TDD) - MANDATORY
All code must follow strict TDD cycle:

1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass  
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Continue with next requirement

**TDD Requirements:**
- No production code without a failing test first
- Write minimal implementation to pass tests
- Unit tests must run in <1 second
- 95% test coverage minimum

### UV Environment Management - CRITICAL
**Always use `uv run` prefix for all Python commands**

```bash
# CORRECT
uv run pytest
uv run ruff check .
uv run mypy src/

# WRONG - Never use bare commands
pytest                    # NO
python -m pytest        # NO
```

**Essential UV Commands:**
```bash
uv sync                  # Install dependencies
uv add <package>         # Add dependency
uv run <command>         # Run in project environment
```

### Quality Gates - MANDATORY Before Commits
**ALL must pass before any commit:**

```bash
uv run ruff format .                              # Format code
uv run ruff check .                               # Check linting
uv run mypy src/                                  # Type checking
uv run pytest --cov=mypylogger --cov-fail-under=95  # Tests + coverage
./scripts/run_tests.sh                            # Master validation
```

## Task Execution Workflow

### AI Agent Task Protocol
1. **Before Starting:** Read ALL requirements, design, and task details
2. **TDD First:** Write failing tests before any implementation
3. **Minimal Implementation:** Write just enough code to pass tests
4. **Quality Gates:** Run all validation before marking complete
5. **STOP:** Wait for user review after each task completion

**Critical Rules:**
- Use `uv run` for all Python commands
- Focus on single task objective only
- Reference specific requirements from specs
- Never skip tests to "save time"
- No task complete without passing `./scripts/run_tests.sh`

## Testing Standards

### Test Categories
- **Unit Tests:** <1s total, mock external dependencies, 100% core logic coverage
- **Integration Tests:** <30s total, real dependencies, critical workflows

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
└── conftest.py     # Shared fixtures
```

### Essential Test Commands
```bash
# All tests with coverage (primary)
uv run pytest --cov=mypylogger --cov-fail-under=95

# Fast unit tests only
uv run pytest tests/unit/ -v

# Specific test
uv run pytest tests/unit/test_core.py::test_function -v
```

## Code Quality Standards

### Required Order for Quality Checks
```bash
uv run ruff format .           # 1. Auto-format first
uv run ruff check --fix .      # 2. Auto-fix linting
uv run ruff format --check .   # 3. Verify formatting
uv run ruff check .            # 4. Check remaining issues
uv run mypy src/               # 5. Type checking
```

### Code Requirements
- **Type hints:** Required for all public functions
- **Docstrings:** Google-style format for all public APIs
- **Error handling:** All code must include try-catch blocks
- **Line length:** 100 chars target, 120 chars hard limit

### Documentation Pattern
```python
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with JSON formatting.
    
    Args:
        name: Logger name. If None, uses APP_NAME from environment.
              
    Returns:
        Logger instance configured with JSON formatting.
        
    Raises:
        ConfigurationError: If configuration is invalid.
    """
```

## Error Handling Philosophy

### Graceful Degradation Pattern
- **Never crash:** Log operations must never crash the application
- **Safe defaults:** Fall back to safe defaults when operations fail
- **Clear messages:** Provide actionable error information
- **Use stderr:** For library's own error messages

```python
# Example: Graceful fallback pattern
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    fallback_operation()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    safe_default()
```

## Git Workflow

### Conventional Commits (Required)
```
type(scope): description

Examples:
feat(core): add get_logger function
fix(formatter): handle None values in JSON
test(config): add validation tests
```

### Commit Rules
- Commit after each TDD cycle completion
- All tests must pass before committing
- Use `git --no-pager` commands to prevent terminal lockup
- Keep commits atomic and focused

## Performance Expectations

### "Fast Enough" Philosophy
- Logger initialization: <10ms
- Single log entry: <1ms (with immediate flush)
- Test suite: <5 seconds (unit tests)

**Not optimized for:** High-frequency logging (>10k/sec) or extreme performance scenarios.

## AI Agent Guidelines

### MANDATORY Agent Protocol
1. **Read ALL:** Steering docs and relevant specs before starting
2. **TDD First:** Write failing test before any implementation
3. **UV Only:** Use `uv run` for all Python commands
4. **One Task:** Focus on single task objective only
5. **Quality Gates:** Run all validation before marking complete
6. **STOP:** Wait for user review after each task

### Agent Restrictions
- **No features** not explicitly in specs
- **No skipping tests** to "save time"
- **No "helpful" additions** without asking
- **No bare Python commands** (always `uv run`)

### Task Completion Checklist
- [ ] All tests pass: `uv run pytest`
- [ ] Code quality passes: `uv run ruff check .`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Master script passes: `./scripts/run_tests.sh`
- [ ] Changes committed with conventional commit message
- [ ] **STOP** and wait for user review

**Success Pattern:** Read → Test → Code → Validate → Stop → Wait for approval
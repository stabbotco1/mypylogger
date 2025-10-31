---
inclusion: always
---

# Code Style Guidelines

## Line Length Standards

- **Target**: 100 characters (optimal for readability)
- **Hard limit**: 120 characters (CI enforcement)
- Use parentheses for line continuation in Python
- Configure IDE rulers at 100 and 120 character positions

## Auto-Formatting Workflow

**CRITICAL**: Always auto-format before manual corrections

### Required Order
1. `uv run ruff format .` - Auto-format all files
2. `uv run ruff check --fix` - Auto-fix linting issues  
3. `uv run ruff format --check .` - Verify formatting
4. `uv run ruff check .` - Check remaining issues
5. `uv run mypy .` - Type checking
6. Manual corrections only for unfixable issues

### Quality Gates
- No lines exceed 120 characters
- All Ruff checks must pass
- All mypy checks must pass
- Zero tolerance for style/linting errors

## Core Principles

- **Concise over verbose**: Minimize lines without sacrificing clarity
- **Consistency**: Follow established patterns within codebase
- **Self-documenting**: Code should be readable without excessive comments
- **PEP 8 compliance**: Strict adherence to Python standards

## Error Handling

- **Mandatory**: All code must include try-catch blocks
- **Graceful degradation**: Fall back to safe defaults
- **Meaningful messages**: Provide actionable error information
- **Logging**: Use appropriate log levels for errors

## Python Standards

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase` 
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_private_var`
- **Modules**: lowercase with underscores

### Import Organization
```python
# Standard library
import os
from typing import Optional

# Third-party  
import requests

# Local
from mypackage import mymodule
```

### Type Hints (Required)
- All function parameters and return values must have type hints
- Use `Optional[Type]` for nullable values
- Import from `typing` module as needed

### Docstrings (Required)
- Google-style format for all public functions/classes
- Include Args, Returns, Raises sections
- Brief description on first line

### String Formatting
- **Preferred**: f-strings (`f"Hello {name}"`)
- **Avoid**: % formatting

### Exception Handling Pattern
```python
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    handle_error(e)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
finally:
    cleanup_resources()
```

## Quality Standards

### Zero Tolerance Policy
- No linting errors allowed for task completion
- All mypy type checking must pass
- All public APIs require comprehensive docstrings
- Strict PEP 8 compliance required

### Ruff Configuration
- Primary tool for linting and formatting
- Line length: 100 characters (target), 120 (hard limit)
- Automatic import sorting and quote consistency
- VSCode integration via official Ruff extension

### Essential Commands
```bash
# Format and fix
uv run ruff format .
uv run ruff check --fix .

# Verify compliance  
uv run ruff format --check .
uv run ruff check .
uv run mypy .
```

### Task Completion Requirements
- All Ruff checks pass
- All mypy checks pass  
- 95%+ test coverage
- Master test script passes: `./scripts/run_tests.sh`
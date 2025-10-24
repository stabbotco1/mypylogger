# Code Style Guidelines

## Line Length Standards

### Target Line Length

- **Target**: 100 characters per line (optimal for modern editors)
- **Hard limit**: 120 characters per line (testing/CI enforcement)

### Implementation Guidelines

- Aim for 100 characters as the preferred line length
- 120 characters is the absolute maximum (hard limit for CI/testing)
- Break long lines using appropriate language-specific conventions
- Prioritize readability over strict adherence to line length limits
- Modern editors and Python naming conventions work well with 100-char target

### Language-Specific Formatting

- **Python**: Follow PEP 8 guidelines with the adjusted line length limits
- Use parentheses for line continuation when appropriate
- Break long function calls and definitions across multiple lines
- Use consistent indentation for wrapped lines

### Tool Configuration

- Configure linters and formatters to use these line length limits
- Set up IDE/editor rulers at 100 and 120 character positions
- Ensure automated formatting tools respect these constraints

## Auto-Formatting Workflow

### CRITICAL: Auto-Format First Policy

**ALWAYS use automated formatting tools before making manual corrections**

### Required Workflow Order

1. **First**: Run auto-formatting tools
   ```bash
   uv run ruff format .     # Auto-format all Python files with Ruff
   uv run ruff check --fix  # Auto-fix linting issues
   ```

2. **Second**: Check for remaining issues
   ```bash
   uv run ruff format --check . # Verify Ruff formatting compliance
   uv run ruff check .      # Check for remaining linting issues
   uv run mypy .           # Type checking
   ```

3. **Last**: Manual corrections only for issues that cannot be auto-fixed

### Auto-Formatting Benefits

- **Consistency**: Ensures uniform code style across the entire codebase
- **Efficiency**: Eliminates manual formatting work and reduces review time
- **Error Prevention**: Catches common style issues automatically
- **Team Alignment**: Removes subjective formatting decisions

### Manual Correction Guidelines

- **Only after auto-formatting**: Never manually format what tools can handle
- **Document exceptions**: If manual formatting is needed, document why
- **Focus on logic**: Manual corrections should address logic, not style
- **Preserve auto-format**: Don't override auto-formatter decisions manually

### Integration Requirements

- **Pre-commit hooks**: Set up auto-formatting in pre-commit hooks when available
- **IDE integration**: Configure IDE to run formatters on save
- **CI/CD validation**: Ensure formatting checks pass in automated pipelines

### Quality Gates

- Code must pass linting with these line length requirements
- No lines should exceed 120 characters
- Prefer shorter, more readable lines when possible

## General Style Principles

- **Concise over verbose**: Fewer lines of code without sacrificing functionality is always better
- **Consistency**: Use consistent patterns across similar file types
- **Readability**: Code should be self-documenting and easy to understand
- **Language standards**: Follow Python PEP 8 guidelines with project-specific adjustments

## Error Handling Requirements

- **Complete error handling**: All code must be wrapped in try-catch blocks
- Handle exceptions appropriately for the context
- Provide meaningful error messages
- Log errors when appropriate

## Python PEP 8 Style Guide

### Indentation and Whitespace

- **Indentation**: Use 4 spaces per indentation level (never tabs)
- **Blank lines**: 
  - Two blank lines around top-level function and class definitions
  - One blank line around method definitions inside classes
  - Use blank lines sparingly inside functions to indicate logical sections
- **Whitespace in expressions**:
  - No spaces around `=` in keyword arguments: `func(arg=value)`
  - Spaces around operators: `x = y + z`
  - No trailing whitespace

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes**: Leading underscore `_private_var`
- **Protected attributes**: Single leading underscore `_protected_var`
- **Name mangling**: Double leading underscore `__private_var`
- **Module names**: Short, lowercase, underscores if needed

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import requests
import numpy as np

# Local application imports
from mypackage import mymodule
from . import sibling_module
from .subpackage import cousin_module
```

### String Formatting

- **Preferred**: f-strings for Python 3.6+
  ```python
  name = "world"
  message = f"Hello, {name}!"
  ```
- **Alternative**: `.format()` method for complex formatting
- **Avoid**: `%` formatting (legacy)

### Function and Class Definitions

```python
def function_name(param1: str, param2: int = 0) -> Optional[str]:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2 with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    try:
        result = process_data(param1, param2)
        return result
    except ProcessingError as e:
        logger.error(f"Failed to process data: {e}")
        return None


class MyClass:
    """Brief description of class."""
    
    def __init__(self, value: str) -> None:
        """Initialize MyClass with value."""
        self._value = value
    
    def public_method(self) -> str:
        """Public method description."""
        return self._value
    
    def _private_method(self) -> None:
        """Private method description."""
        pass
```

### Type Hints

- **Required**: Use type hints for all function parameters and return values
- **Import types**: From `typing` module when needed
- **Optional values**: Use `Optional[Type]` or `Type | None` (Python 3.10+)
- **Collections**: Use generic types `List[str]`, `Dict[str, int]`

### Documentation Strings

- **Required**: All public functions, classes, and modules must have docstrings
- **Format**: Use Google-style docstrings
- **Content**: Brief description, Args, Returns, Raises sections
- **Line length**: Follow same 100/120 character limits

### Comments

- **Inline comments**: Use sparingly, explain "why" not "what"
- **Block comments**: Use for complex logic explanation
- **TODO comments**: Format as `# TODO: Description of what needs to be done`

### Exception Handling

```python
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}")
    handle_specific_error(e)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise  # Re-raise if cannot handle
finally:
    cleanup_resources()
```

### Boolean Expressions

- **Explicit comparisons**: `if value is None:` not `if not value:`
- **Boolean values**: `if flag:` not `if flag is True:`
- **Empty sequences**: `if not sequence:` not `if len(sequence) == 0:`

## Code Quality Standards

- **Zero tolerance policy**: No linting or style errors allowed for task completion
- All code must pass mypy type checking
- **Ruff is used for both linting and formatting**: Fast, comprehensive Python tooling
- Follow established patterns within the codebase
- **PEP 8 compliance**: All Python code must strictly adhere to PEP 8 standards
- **Docstring coverage**: All public APIs must have comprehensive docstrings

## Ruff Code Formatter and Linter

### Ruff Configuration
- **Line length**: Configure Ruff to use 100 characters (project standard)
- **String quotes**: Consistent quote style enforcement
- **Import sorting**: Automatic import organization
- **Trailing commas**: Consistent trailing comma usage

### Ruff Benefits
- **Fast**: Extremely fast linting and formatting
- **Comprehensive**: Combines multiple tools (flake8, isort, etc.)
- **Configurable**: Highly customizable rules and formatting
- **Modern**: Built with Rust for performance

### Ruff Integration
- **Auto-formatting**: Use `uv run ruff format .` to format all Python files
- **Check mode**: Use `uv run ruff format --check .` to verify formatting without changes
- **Linting**: Use `uv run ruff check .` to run linting checks
- **Auto-fix**: Use `uv run ruff check --fix .` to automatically fix issues
- **VSCode integration**: Use the official Ruff extension for real-time feedback
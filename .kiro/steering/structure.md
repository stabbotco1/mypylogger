---
inclusion: always
---

# Project Structure

This document outlines the organizational patterns and folder structure conventions for this project.

## Root Level Organization

```
mypylogger/
├── .git/                   # Git version control
├── .gitignore             # Git ignore patterns
├── .kiro/                 # Kiro AI assistant configuration
│   ├── steering/          # AI guidance documents
│   └── specs/             # Project specifications and tasks
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # UV lock file for reproducible builds
├── README.md             # Project overview
├── src/                  # Source code
│   └── mypylogger/       # Main package directory
├── tests/                # Test files
│   ├── unit/             # Fast, isolated unit tests
│   └── integration/      # Component interaction tests
├── scripts/              # Build and test scripts
│   └── run_tests.sh      # Master test runner script (MANDATORY)
├── docs/                 # Documentation
├── badges/               # Project badges and status
├── security/             # Security monitoring and validation
├── infrastructure/       # Deployment and infrastructure code
└── metrics/              # Performance and workflow metrics
```

## Development Methodology: TDD First

**CRITICAL**: This project follows Test-Driven Development (TDD) as the primary methodology.

### Task Completion Criteria

A task or sub-task is ONLY considered complete when ALL conditions are met:
- **100% test passing**: All tests in the full test suite must pass
- **No warnings**: Zero test warnings allowed
- **No skipped tests**: All tests must be executed
- **95%+ test coverage**: Minimum test coverage threshold
- **Complete error handling**: All code must be wrapped in try-catch blocks
- **Zero linting errors**: Code must pass all linting rules (`uv run ruff check .`)
- **Zero style errors**: Code must conform to style guidelines (`uv run ruff format --check .`)
- **Type checking passes**: All mypy checks must pass (`uv run mypy .`)
- **Master test script passes**: `./scripts/run_tests.sh` must complete successfully

### MANDATORY Agent Requirements

**CRITICAL**: All AI agents working on this project MUST follow this testing protocol:

#### Required Testing Workflow
1. **Development phase**: Use `uv run pytest`, `uv run ruff check`, etc. for iterative development
2. **MANDATORY final validation**: Execute `./scripts/run_tests.sh` before marking ANY task complete
3. **Dual verification required**: Both individual commands AND master script must pass
4. **No exceptions**: Cannot skip master test script under any circumstances

#### Agent Compliance Rules
- **Cannot mark tasks complete**: Without successful `./scripts/run_tests.sh` execution
- **Must verify all requirements**: 95% coverage, zero errors, all tests passing
- **Must show script output**: Display master test script execution results
- **Use UV commands**: Always prefix with `uv run` for Python commands

### Master Test Script Requirements

**CRITICAL**: The `./scripts/run_tests.sh` script is the definitive quality gate

#### Script Must Include:
- **All tests**: Run complete test suite with coverage reporting (`uv run pytest --cov`)
- **All linting**: Execute all linting rules (`uv run ruff check .`)
- **All style checks**: Verify code formatting (`uv run ruff format --check .`)
- **Type checking**: Run mypy validation (`uv run mypy .`)
- **Exit codes**: Return non-zero exit code on any failure

#### Script Execution Requirements:
- **Comprehensive validation**: Must validate every aspect of code quality
- **No exceptions**: ALL checks must pass - no partial success allowed
- **Clear reporting**: Provide detailed failure information when checks fail
- **Success summary**: Show clear success message when all checks pass
- **Fast execution**: Complete validation in under 30 seconds

### Test Verification Process

1. **Development testing**: Use `uv run pytest`, `uv run ruff check` during development
2. **MANDATORY final verification**: Run `./scripts/run_tests.sh` before task completion
3. **Zero tolerance**: Master test script must pass completely without any failures
4. **No task completion**: Tasks cannot be marked complete until master script passes
5. **Git integration**: Only commit code that passes all quality gates

## Source Code Organization

### Core Package Structure
```
src/mypylogger/
├── __init__.py          # Public API exports
├── core.py              # Main logger functionality  
├── config.py            # Environment-driven configuration
├── formatters.py        # JSON formatting logic
└── exceptions.py        # Custom exception classes
```

### Organization Principles
- Keep source code in dedicated `src/` directory
- Organize by feature/domain rather than file type
- Use clear, descriptive folder and file names
- Separate concerns: core logic, configuration, formatting, exceptions
- **All code must include comprehensive error handling**

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Test files**: `test_*.py` (preferred) or `*_test.py`
- **Configuration files**: Standard naming (`pyproject.toml`, `uv.lock`)
- **Documentation**: Markdown files with descriptive names
- **Scripts**: Executable scripts in `scripts/` directory
- **Consistency**: Use consistent casing and descriptive names

## Import Structure

### Import Organization
```python
# Standard library
import os
from typing import Optional

# Third-party (minimal - only python-json-logger allowed)
from pythonjsonlogger import jsonlogger

# Local imports
from mypylogger.config import get_config
from mypylogger.exceptions import ConfigurationError
```

### Import Rules
- Use absolute imports from package root
- Organize modules by functionality
- Keep `__init__.py` files minimal with clear public API exports
- Group imports: stdlib, third-party, local

## Configuration Management

### Configuration Strategy
- **Environment variables only**: No configuration files
- **Root level files**: `pyproject.toml`, `uv.lock` at project root
- **Environment-driven**: All configuration via environment variables
- **Sensible defaults**: Works out-of-box without configuration

### Key Configuration Files
- `pyproject.toml`: Project metadata, dependencies, tool configuration
- `uv.lock`: Dependency lock file (committed to version control)
- `.gitignore`: Version control exclusions

## Documentation Structure

### Documentation Organization
- **README.md**: Project overview, quick start, installation
- **docs/**: Comprehensive documentation
- **.kiro/steering/**: AI assistant guidance documents
- **.kiro/specs/**: Project specifications and task definitions
- **badges/**: Project status badges and CI workflow documentation

## Best Practices

### Development Practices
- **TDD First**: Write failing tests before implementation code
- **UV commands**: Always use `uv run` prefix for Python commands
- **Quality gates**: All checks must pass before commits
- **Atomic commits**: Each commit represents a single logical change

### Structure Practices
- Maintain flat directory structure when possible
- Avoid deeply nested folders (max 3-4 levels)
- Use consistent patterns across similar file types
- Keep related files close together in directory tree
- **Never commit code without 100% passing tests**

## Documentation Consistency

### Steering Document Requirements
- **Internal consistency**: All `.kiro/steering/` documents must align
- **Cross-references**: Ensure steering files reference each other correctly
- **Update together**: Change related documents when making updates
- **Coherent methodology**: Maintain consistent development approach across all guidance

## Version Control with Git

**CRITICAL**: This project uses Git for comprehensive version management

### Git Workflow
- **Primary branch**: `main` - all development occurs on main branch
- **Commit strategy**: Direct commits to main (no feature branches)
- **Commit frequency**: Commit after each completed TDD cycle

### Required Git Practices
- **Conventional commits**: Use standardized commit message format
  - `feat: add new logging feature`
  - `fix: resolve memory leak in logger`
  - `docs: update API documentation`
  - `test: add unit tests for formatter`
  - `refactor: simplify configuration parsing`
- **Atomic commits**: Each commit represents a single logical change
- **Quality gates**: Only commit code that passes all tests and quality checks
- **CRITICAL**: Always use `--no-pager` flag to prevent terminal lockup

### Essential Git Commands
```bash
# Check status and stage changes (ALWAYS use --no-pager)
git --no-pager status
git add .

# Commit with conventional message
git commit -m "feat: implement new logging formatter"

# Push to main branch
git push origin main

# View recent history (no pager)
git --no-pager log --oneline -10

# View changes (no pager)
git --no-pager diff
```

### Files to Commit
- **Source code**: All Python files in `src/`
- **Tests**: All test files in `tests/`
- **Configuration**: `pyproject.toml`, `uv.lock`
- **Documentation**: README.md, docs/, steering files
- **Scripts**: Build and validation scripts

### Files to Ignore (via .gitignore)
- **Build artifacts**: `build/`, `dist/`, `*.egg-info/`
- **Cache files**: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **Virtual environments**: `.venv/`, `venv/`
- **IDE files**: `.vscode/`, `.idea/`
- **Temporary files**: `*.log`, `temp/`, `.DS_Store`
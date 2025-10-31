---
inclusion: always
---

# Technology Stack & Development Standards

## Core Technology Stack

### Language & Runtime
- **Python 3.8+** - Primary programming language
- **uv** - Package management and dependency resolution
- **pyproject.toml** - Project configuration and dependencies
- **uv.lock** - Lock file for reproducible builds (committed to version control)

### Development Tools
- **pytest** - Testing framework with coverage reporting
- **ruff** - Fast Python linter and formatter (primary code quality tool)
- **mypy** - Static type checker
- **Git** - Version control with conventional commits

## Dependency Policy

**CRITICAL**: Minimal dependency approach for mypylogger v0.2.7

### Approved Dependencies
- **python-json-logger** - ONLY external dependency allowed
  - Provides reliable JSON formatting
  - Mature, stable library with no transitive dependencies

### Dependency Approval Process
Before adding ANY dependency, it must meet ALL criteria:
1. Cannot be implemented with stdlib in <100 lines
2. Mature and actively maintained
3. No (or minimal) transitive dependencies
4. Adds clear value to >50% of users
5. **Explicit approval required**

## Code Quality Standards

### Quality Philosophy
- **Concise over verbose** - Minimize lines without sacrificing clarity
- **Zero tolerance** - No linting, style, or type errors allowed
- **Stdlib first** - Prefer standard library over external dependencies
- **Error handling** - All code must include try-catch blocks

### Master Test Script (MANDATORY)
The `./scripts/run_tests.sh` script is the definitive quality gate:

#### Required Validations
- **All tests pass** with 95%+ coverage
- **Zero linting errors** (`uv run ruff check .`)
- **Zero style errors** (`uv run ruff format --check .`)
- **Zero type errors** (`uv run mypy .`)
- **No warnings or skipped tests**

#### Script Requirements
- Return non-zero exit code on ANY failure
- ALL checks must pass - no partial success
- Provide detailed failure information
- Complete validation in <30 seconds

## Essential Commands

### Package Management
```bash
uv sync                    # Install dependencies from lock file
uv add <package>          # Add new dependency
uv run <command>          # Run command in project environment
```

### Development Workflow
```bash
# Master test runner (REQUIRED before task completion)
./scripts/run_tests.sh

# Individual quality checks (for development)
uv run pytest --cov=mypylogger --cov-fail-under=95
uv run ruff format .
uv run ruff check .
uv run mypy src/
```

### Git Workflow (CRITICAL: Use --no-pager)
```bash
git --no-pager status     # Check repository status
git add .                 # Stage all changes
git commit -m "feat: description"  # Conventional commit
git push origin main      # Push to main branch
git --no-pager log --oneline -10   # View recent history
```

## AI Agent Protocol (MANDATORY)

### Required Agent Workflow
1. **Development phase**: Use individual commands for iterative development
2. **Validation phase**: Execute `./scripts/run_tests.sh` as final verification
3. **Completion phase**: Only mark tasks complete after master script passes

### Agent Requirements
- **MUST use `uv run`** for all Python commands
- **MUST execute master script** before marking any task complete
- **MUST use `--no-pager`** for all git commands
- **CANNOT skip validation** - no exceptions allowed
- **MUST commit with conventional messages**

### Task Completion Checklist
- [ ] All tests pass: `uv run pytest --cov=mypylogger --cov-fail-under=95`
- [ ] Code quality passes: `uv run ruff check .` and `uv run ruff format --check .`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] **Master script passes**: `./scripts/run_tests.sh`
- [ ] Changes committed with conventional message
- [ ] **STOP and wait for user approval**

### Git Integration Requirements
- Always use `git --no-pager` commands to prevent terminal lockup
- Check status before starting work
- Commit after each logical unit completion
- Use conventional commit format: `type(scope): description`

## Code Style Requirements

### Formatting Standards
- **Line length**: 100 chars target, 120 chars hard limit
- **Auto-formatting order**: 
  1. `uv run ruff format .`
  2. `uv run ruff check --fix .`
  3. Verify with `uv run ruff format --check .`

### Python Standards
- **Type hints**: Required for all public functions
- **Docstrings**: Google-style format for public APIs
- **Error handling**: All code wrapped in try-catch blocks
- **Import organization**: stdlib, third-party, local

### Quality Gates
- Zero linting errors (ruff check)
- Zero style errors (ruff format --check)
- Zero type errors (mypy)
- 95%+ test coverage
- All tests passing with no warnings

## Project Architecture

### Source Organization
```
src/mypylogger/
├── __init__.py          # Public API exports
├── core.py              # Main logger functionality  
├── config.py            # Environment-driven configuration
├── formatters.py        # JSON formatting logic
└── exceptions.py        # Custom exception classes
```

### Testing Structure
```
tests/
├── unit/               # Fast, isolated tests (<1s total)
├── integration/        # Component interaction tests
└── conftest.py         # Shared fixtures
```

## Success Metrics

- **Installation**: Works in <1 minute with `pip install mypylogger`
- **Zero config**: Sensible defaults, environment-driven configuration
- **JSON output**: Valid JSON, timestamp-first, one line per entry
- **Reliability**: Logs never lost due to crashes/termination
- **Size**: Core library <500 lines of code
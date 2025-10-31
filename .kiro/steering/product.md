---
inclusion: always
---

# mypylogger v0.2.7 Product Guide

## Core Mission
Zero-dependency JSON logging library with sensible defaults. Does ONE thing exceptionally well: structured JSON logs that work everywhere—from local development to AWS Lambda to Kubernetes.

## Value Proposition
1. **Minimal Dependencies** - Only `python-json-logger`, works in restricted environments
2. **Predictable JSON Output** - Flat structure, timestamp-first, machine-parseable
3. **Zero Configuration** - Works out-of-box, environment-driven config
4. **Standard Python Patterns** - Uses `logging.getLogger(__name__)`, not a singleton

## Design Principles

### Simplicity Over Features
- One clear purpose: JSON logging only
- Minimal API: `get_logger(__name__)` + standard logging methods
- No magic: Explicit configuration, obvious defaults
- <500 lines total codebase

### Reliability Over Performance
- Immediate flush by default (reliability > speed)
- Graceful degradation with safe fallbacks
- Never crash the application
- Predictable behavior across environments

### Maintainability Over Completeness
- Stdlib-based architecture
- Clear boundaries: external tools handle rotation/filtering/analysis
- Comprehensive error handling with try-catch blocks
- Self-documenting code patterns

## Architecture Constraints

### Dependencies
- **ONLY** `python-json-logger` allowed as external dependency
- Must justify any new dependency against 5 strict criteria
- Prefer stdlib solutions over external libraries
- Zero transitive dependencies preferred

### Code Organization
```
src/mypylogger/
├── __init__.py          # Public API exports
├── core.py              # Main logger functionality  
├── config.py            # Environment-driven configuration
├── formatters.py        # JSON formatting logic
└── exceptions.py        # Custom exception classes
```

### API Design
- Primary entry point: `get_logger(name: Optional[str] = None)`
- Standard logging methods: `.info()`, `.error()`, `.debug()`, etc.
- Configuration via environment variables only
- No configuration files, no complex initialization

## Quality Gates (MANDATORY)

### Test Requirements
- 95% minimum test coverage
- All tests must pass (zero tolerance)
- No warnings or skipped tests
- TDD methodology required

### Code Quality
- Zero linting errors (`uv run ruff check .`)
- Zero style errors (`uv run ruff format --check .`)
- Zero type errors (`uv run mypy .`)
- All code wrapped in try-catch blocks

### Master Validation
- `./scripts/run_tests.sh` must pass completely
- Required before ANY task/sub-task completion
- No exceptions or partial success allowed

## Development Workflow

### TDD Cycle (MANDATORY)
1. **Red**: Write failing test first
2. **Green**: Minimal code to pass test
3. **Refactor**: Improve while keeping tests green
4. **Validate**: Run master test script

### UV Environment (REQUIRED)
- Always use `uv run` prefix for Python commands
- `uv run pytest --cov=mypylogger --cov-fail-under=95`
- `uv run ruff check .` and `uv run ruff format .`
- `uv run mypy src/`

### Git Workflow
- Conventional commits on main branch
- Commit after each TDD cycle completion
- Use `git --no-pager` commands to prevent lockup
- All quality gates must pass before commit

## Success Metrics
1. **Installation**: `pip install mypylogger` → working logger in <1 minute
2. **Zero Config**: Works immediately with sensible defaults
3. **JSON Output**: Valid JSON, timestamp-first, one line per entry
4. **Reliability**: Logs never lost due to crashes/termination
5. **Size**: Core library <500 lines of code

## AI Agent Guidelines

### MANDATORY Protocol
1. Read ALL steering docs before starting any task
2. Follow TDD: write failing test before implementation
3. Use `uv run` for all Python commands
4. Focus on single task objective only
5. Run `./scripts/run_tests.sh` before marking complete
6. STOP and wait for user review after completion

### Restrictions
- No features not explicitly in specifications
- No "helpful" additions without asking
- No skipping tests to save time
- No bare Python commands (always `uv run`)
- Default answer is NO to new features

### Task Completion Checklist
- [ ] Tests pass: `uv run pytest --cov=mypylogger --cov-fail-under=95`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Formatting passes: `uv run ruff format --check .`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Master script passes: `./scripts/run_tests.sh`
- [ ] Changes committed with conventional message
- [ ] STOP and wait for user approval
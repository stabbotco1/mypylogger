# Technology Stack

## Language & Runtime

- **Python 3.8+** - Primary programming language (check with `python --version`)
- **uv** - Fast Python package installer and resolver

## Build System & Package Management

- **uv** - Package management and dependency resolution
- **pyproject.toml** - Project configuration and dependencies
- **uv.lock** - Lock file for reproducible builds (committed to version control)

## Development Tools

- **pytest** - Testing framework
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **coverage.py** - Code coverage measurement
- **Git** - Version control and project management
- **VSCode extensions** - Ruff extension for integrated linting and formatting

## Dependencies

**CRITICAL**: Minimal dependency policy for mypylogger v0.2.0

### Approved Dependencies
- **python-json-logger** - ONLY external dependency allowed
  - Provides reliable JSON formatting
  - Mature, stable library
  - No transitive dependencies

### Dependency Approval Process
**Before adding ANY dependency:**
1. Cannot be implemented with stdlib in reasonable LOC (<100 lines)
2. Dependency is mature and actively maintained
3. Dependency has no transitive dependencies (or very few)
4. Adds clear value to >50% of users
5. **Explicit approval required** - Must be approved before adding

### Frameworks & Libraries Policy
- **Prefer stdlib**: Use Python standard library whenever possible
- **Zero tolerance**: No additional dependencies without explicit approval
- **Justification required**: Each dependency must solve a real problem
- **Consider maintenance**: Every dependency has a permanent maintenance cost

## Code Quality Philosophy

- **Concise over verbose** - Fewer lines of code without sacrificing functionality is always better
- **Language-specific standards** - Use popular, accepted linters and style automation
- **Zero tolerance policy** - No linting or style errors allowed for task completion
- **Ask when uncertain** - Request guidance on tooling choices if unsure

## Testing Infrastructure

**CRITICAL**: Master test runner script is required at `./scripts/run_tests.sh`

### Master Test Script Requirements

The `./scripts/run_tests.sh` script is the definitive quality gate and must include:

#### Comprehensive Test Execution
- **All tests**: Run complete test suite with pytest
- **Coverage reporting**: Validate 95%+ test coverage requirement
- **No warnings**: Ensure zero test warnings
- **No skipped tests**: All tests must execute

#### Complete Code Quality Validation
- **Linting**: Run `uv run ruff check .` - must pass completely
- **Style formatting**: Run `uv run ruff format --check .` - must pass completely  
- **Type checking**: Run `uv run mypy .` - must pass completely
- **Import sorting**: Validate import organization

#### Script Behavior Requirements
- **Exit codes**: Return non-zero exit code on ANY failure
- **No partial success**: ALL checks must pass - no exceptions
- **Detailed reporting**: Show specific failure information for debugging
- **Success summary**: Clear success message when all checks pass
- **Fail fast**: Stop on first critical failure to save time

#### Integration Requirements
- **Task completion gate**: No task or sub-task complete until script passes
- **CI/CD ready**: Script must be suitable for automated pipeline execution
- **Reproducible**: Must work consistently across different environments

## Common Commands

```bash
# Master test runner (REQUIRED)
./scripts/run_tests.sh

# Package Management
uv sync                    # Install dependencies from lock file
uv add <package>          # Add new dependency
uv remove <package>       # Remove dependency
uv lock                   # Update lock file

# Development
uv run python <script>    # Run Python script in project environment
uv run <command>          # Run any command in project environment

# Testing
uv run pytest            # Run tests (primary)
uv run pytest --cov      # Run tests with coverage
uv run pytest --cov --cov-report=html  # Generate HTML coverage report

# Code Quality
uv run ruff check         # Lint code
uv run ruff format        # Format code with Ruff
uv run ruff format --check # Check formatting without changes
uv run mypy .            # Type checking

# Project Setup
uv init                   # Initialize new project
uv python install 3.x    # Install specific Python version

# Version Control
git --no-pager status     # Check repository status (no pager)
git add .                 # Stage all changes
git commit -m "message"   # Commit with conventional message
git push origin main      # Push to main branch
git --no-pager log --oneline -10  # View recent commit history (no pager)
git --no-pager diff       # View changes (no pager)
git --no-pager show       # Show commit details (no pager)
```

## Quality Gates

**CRITICAL**: All code must pass these quality gates before ANY task or sub-task completion:

### Master Test Script Validation
- **`./scripts/run_tests.sh` must pass completely**: This is the definitive quality gate
- **No exceptions**: ALL checks in the script must pass without any failures
- **Mandatory for every task**: Both main tasks and sub-tasks require script validation

### Individual Quality Requirements
- **Test Coverage**: Minimum 95% coverage required
- **Linting**: Zero linting errors allowed (validated by ruff check)
- **Style**: Zero style errors allowed (validated by ruff format --check)
- **Type Checking**: Zero type errors allowed (validated by mypy)
- **Error Handling**: All code wrapped in try-catch blocks
- **Test Status**: 100% passing, no warnings, no skipped tests

### Task Completion Policy
- **No partial completion**: Tasks cannot be marked complete with any failing checks
- **Sub-task validation**: Even individual sub-tasks must pass the master test script
- **Zero tolerance**: No exceptions or workarounds allowed

## MANDATORY Agent Testing Protocol

**CRITICAL**: All AI agents working on this project MUST follow this exact testing protocol:

### Required Agent Workflow
1. **Development phase**: Use typical commands (`uv run pytest`, `uv run ruff check`, `uv run ruff format`, `uv run mypy .`) for iterative development and debugging
2. **Validation phase**: Execute `./scripts/run_tests.sh` as the final verification step
3. **Completion phase**: Only mark tasks/sub-tasks complete after BOTH typical commands AND master script pass

### Agent Compliance Requirements
- **MUST execute master script**: `./scripts/run_tests.sh` before marking any task or sub-task complete
- **MUST verify all criteria**: 95% coverage, zero linting errors, zero style errors, all tests passing
- **MUST show script output**: Display the results of the master test script execution
- **CANNOT skip validation**: No exceptions, shortcuts, or workarounds allowed
- **CANNOT mark incomplete**: Tasks/sub-tasks cannot be marked complete with any failing checks

### Agent Verification Checklist
Before marking any task or sub-task complete, agents must confirm:
- [ ] Typical test commands pass (`uv run pytest --cov`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Style formatting passes (`uv run ruff format --check .`)
- [ ] Type checking passes (`uv run mypy .`)
- [ ] **Master script passes** (`./scripts/run_tests.sh`)
- [ ] All output shows 95%+ coverage, zero errors, zero warnings
- [ ] Changes are committed to Git with conventional commit messages

## Git Integration for Agents

**CRITICAL**: All AI agents must integrate Git version control into their workflow:

### Pager Prevention (MANDATORY)
**CRITICAL**: Always use `--no-pager` flag to prevent terminal lockup:
- `git --no-pager status` instead of `git status`
- `git --no-pager log --oneline -10` instead of `git log --oneline -10`
- `git --no-pager diff` instead of `git diff`
- `git --no-pager show` instead of `git show`
- **Never use bare git commands** that might trigger pager mode

### Agent Git Requirements
- **Check Git status**: Use `git --no-pager status` to understand current repository state
- **Stage changes**: Use `git add .` to stage all modified files
- **Commit with quality**: Only commit after all quality gates pass
- **Conventional commits**: Use proper commit message format
- **Push changes**: Use `git push origin main` to update remote repository
- **CRITICAL**: Always use `--no-pager` flag for git commands that might trigger pager mode

### Git Workflow for Agents
1. **Before starting work**: Check `git status` to understand current state
2. **During development**: Make incremental commits as logical units complete
3. **Before task completion**: Ensure all changes are committed with proper messages
4. **After quality validation**: Final commit and push to main branch

### Commit Message Standards for Agents
- **feat**: New features or functionality
- **fix**: Bug fixes and corrections
- **test**: Adding or modifying tests
- **docs**: Documentation updates
- **refactor**: Code restructuring without functionality changes
- **style**: Code formatting and style improvements

## Environment Setup

- **Python 3.8+** required
- **uv** installation required (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Document any required environment variables in `.env` file
- Use `uv sync` to set up development environment
- Configure test coverage reporting tools (coverage.py)

## VSCode Integration

### Required Extensions
- **Ruff** - Official Ruff extension for VSCode
  - Provides integrated linting and formatting
  - Auto-formats on save when configured
  - Shows linting errors inline

### VSCode Configuration
- Configure Ruff as the default Python formatter
- Enable format on save for automatic code formatting
- Set up Ruff to run linting checks in real-time
- Configure rulers at 100 and 120 character positions

## Project Structure

- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Dependency lock file (commit to version control)
- `src/` - Source code directory
- `tests/` - Test files
- `scripts/run_tests.sh` - Master test runner script
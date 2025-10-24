# Project Structure

This document outlines the organizational patterns and folder structure conventions for this project.

## Root Level Organization

```
mypylogger/
├── .git/                   # Git version control
├── .gitignore             # Git ignore patterns
├── .kiro/                 # Kiro AI assistant configuration
│   └── steering/          # AI guidance documents
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # UV lock file for reproducible builds
├── README.md             # Project overview
├── src/                  # Source code
│   └── mypylogger/       # Main package directory
├── tests/                # Test files
├── scripts/              # Build and test scripts
│   └── run_tests.sh      # Master test runner script 
├── docs/                 # Documentation
├── config/               # Configuration files
└── examples/             # Usage examples
```

## Development Methodology: TDD First

**CRITICAL**: This project follows Test-Driven Development (TDD) as the primary methodology.

### Task Completion Criteria

A task or sub-task is ONLY considered complete when ALL of the following conditions are met:
- **100% test passing**: All tests in the full test suite must pass
- **No warnings**: Zero test warnings allowed
- **No skipped tests**: All tests must be executed
- **95%+ test coverage**: Minimum test coverage threshold
- **Complete error handling**: All code must be wrapped in try-catch blocks
- **Zero linting errors**: Code must pass all linting rules
- **Zero style errors**: Code must conform to style guidelines
- **Master test script passes**: `./scripts/run_tests.sh` must complete successfully

### MANDATORY Agent Requirements

**CRITICAL**: All AI agents working on this project MUST follow this testing protocol:

#### Required Testing Workflow
1. **Use typical commands during development**: Run `uv run pytest`, `uv run ruff check`, etc. for iterative development
2. **MANDATORY final validation**: Execute `./scripts/run_tests.sh` before marking ANY task or sub-task complete
3. **Dual verification required**: Both typical commands AND the master script must pass
4. **No exceptions**: Agents cannot skip the master test script under any circumstances

#### Agent Compliance Rules
- **Cannot mark tasks complete**: Without successful `./scripts/run_tests.sh` execution
- **Cannot mark sub-tasks complete**: Without successful `./scripts/run_tests.sh` execution
- **Must verify all requirements**: 95% coverage, zero linting errors, zero style errors, all tests passing
- **Must report script results**: Show the output of the master test script execution

### Master Test Script Requirements

**CRITICAL**: The `./scripts/run_tests.sh` script is the definitive quality gate

#### Script Must Include:
- **All tests**: Run complete test suite with coverage reporting
- **All linting**: Execute all linting rules and checks
- **All style checks**: Verify code formatting and style compliance
- **Type checking**: Run mypy or equivalent type validation
- **Exit codes**: Return non-zero exit code on any failure

#### Script Execution Requirements:
- **Comprehensive validation**: Must validate every aspect of code quality
- **No exceptions**: ALL checks must pass - no partial success allowed
- **Clear reporting**: Provide detailed failure information when checks fail
- **Success summary**: Show clear success message when all checks pass

### Test Verification Process

1. **Primary testing**: Use language-specific test runners during development
2. **MANDATORY final verification**: Run `./scripts/run_tests.sh` before task completion
3. **Zero tolerance**: The master test script must pass completely without any failures
4. **No task completion**: Tasks cannot be marked complete until master script passes
5. **Sub-task validation**: Even individual sub-tasks must pass the master test script

## Source Code Organization

- Keep source code in a dedicated `src/` directory
- Organize by feature or domain rather than file type when possible
- Use clear, descriptive folder and file names
- Separate concerns: business logic, UI components, utilities, etc.
- **All code must include comprehensive error handling**

## File Naming Conventions

- Python files: `snake_case.py`
- Test files: `test_*.py` or `*_test.py`
- Configuration files: Follow standard naming (pyproject.toml, etc.)
- Documentation: Markdown files with descriptive names
- Use consistent casing and make file names descriptive and specific

## Import Structure

- Use absolute imports from the package root
- Organize modules by functionality
- Keep __init__.py files minimal with clear public API exports

## Configuration Files

- Keep configuration files at the root level or in a `config/` directory
- Use environment-specific config files when needed
- Document all configuration options and their purposes

## Documentation Structure

- README.md at root with project overview and quick start
- API documentation in `docs/api/`
- Architecture decisions in `docs/architecture/`
- User guides in `docs/guides/`

## Best Practices

- **TDD First**: Write tests before implementation code
- Maintain a flat directory structure when possible
- Avoid deeply nested folders (max 3-4 levels recommended)
- Use consistent patterns across similar file types
- Keep related files close together in the directory tree
- **Never commit code without 100% passing tests**

## Documentation Consistency

- **Logical consistency required** - All .kiro documentation must be internally consistent
- Cross-reference steering files to ensure alignment
- Update related documents when making changes
- Maintain coherent development methodology across all guidance

## Version Control with Git

**CRITICAL**: This project uses Git for comprehensive version management

### Git Workflow
- **Primary branch**: `main` - all development occurs on main branch
- **Commit strategy**: Direct commits to main (no feature branches for now)
- **Commit frequency**: Commit early and often with meaningful messages

### Required Git Practices
- **Conventional commits**: Use conventional commit message format
  - `feat: add new logging feature`
  - `fix: resolve memory leak in logger`
  - `docs: update API documentation`
  - `test: add unit tests for formatter`
  - `refactor: simplify configuration parsing`
- **Atomic commits**: Each commit should represent a single logical change
- **Commit all quality gates**: Only commit code that passes all tests and quality checks
- **CRITICAL**: Always use `--no-pager` flag for git commands to prevent terminal lockup

### Files to Commit
- **Source code**: All Python files in `src/`
- **Tests**: All test files in `tests/`
- **Configuration**: `pyproject.toml`, `uv.lock` (for reproducible builds)
- **Documentation**: README.md, docs/, steering files
- **Scripts**: `scripts/run_tests.sh` and other build scripts

### Files to Ignore
- **Build artifacts**: `build/`, `dist/`, `*.egg-info/`
- **Cache files**: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **Virtual environments**: `.venv/`, `venv/`
- **IDE files**: `.vscode/`, `.idea/`
- **Temporary files**: `*.log`, `temp/`, `.DS_Store`

### Git Commands for Development
```bash
# Check status and stage changes (no pager)
git --no-pager status
git add .

# Commit with conventional message
git commit -m "feat: implement new logging formatter"

# Push to main branch
git push origin main

# View commit history (no pager)
git --no-pager log --oneline -10

# View changes (no pager)
git --no-pager diff

# Show commit details (no pager)
git --no-pager show
```
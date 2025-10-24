# CI-Only Badge Update Workflow

This document describes how to implement badge updates exclusively in CI/CD environments.

## Overview

The badge system is designed to update badges only after successful CI test execution, ensuring badges always reflect the actual state of the main branch code.

## Local Development Workflow

Local development focuses exclusively on code quality:

```bash
# Run all quality checks locally
./scripts/run_tests.sh

# This script runs:
# - Code formatting (ruff format --check)
# - Linting (ruff check)  
# - Type checking (mypy)
# - Test execution with 95% coverage
# - Security scanning (bandit, safety, semgrep, codeql simulation)
# - Package import verification

# NO badge updates happen locally
```

## CI/CD Workflow Integration

### GitHub Actions Example

Add this step to your GitHub Actions workflow AFTER successful test execution:

```yaml
name: Quality Gate

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
        
      - name: Install dependencies
        run: uv sync
        
      - name: Run quality gates
        run: ./scripts/run_tests.sh
        
      # Badge update step - ONLY runs on main branch after successful tests
      - name: Update badges
        if: github.ref == 'refs/heads/main' && success()
        run: |
          uv run python -m badges --ci-mode
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Key Points

1. **Badge updates only on main branch**: `if: github.ref == 'refs/heads/main'`
2. **Only after successful tests**: `&& success()`
3. **CI mode prevents pipeline failures**: `--ci-mode` flag
4. **Automatic git configuration**: CI environment is detected automatically
5. **Skip CI loops**: Commits use `[skip ci]` message

## Badge Update Process

When running in CI:

1. **Environment Detection**: Automatically detects CI environment via environment variables
2. **Git Configuration**: Sets up git user for commits (`action@github.com`)
3. **Badge Generation**: Generates badges based on actual CI test results
4. **README Update**: Updates README.md with new badge URLs
5. **Git Commit**: Commits changes with `docs: update badges [skip ci]`
6. **Push**: Pushes updated README back to main branch

## Manual CI Badge Update

For testing or manual updates in CI environment:

```bash
# In CI environment only
uv run python -m badges

# Force local update (not recommended)
uv run python -m badges --allow-local

# Dry run (generate badges without updating README)
uv run python -m badges --dry-run
```

## Benefits

- **Single Source of Truth**: Badges always reflect actual CI test results
- **No Local Inconsistencies**: Local development can't create badge mismatches
- **Automatic Updates**: Badges update automatically after successful CI runs
- **Clean Development**: Local workflow focuses purely on code quality
- **No Chicken-and-Egg**: CI determines badge status, not local environment

## Troubleshooting

### Badge Updates Not Working

1. Check CI environment variables are set
2. Verify GitHub token permissions
3. Check git configuration in CI
4. Review CI logs for badge update step

### Local Badge Update Errors

This is expected behavior! Badge updates should only happen in CI:

```
Badge updates are only allowed in CI/CD environments
```

Use `--allow-local` flag only for testing purposes.

### Infinite CI Loops

The `[skip ci]` commit message prevents infinite loops. If loops occur:

1. Check commit message format
2. Verify GitHub Actions trigger configuration
3. Review branch protection rules
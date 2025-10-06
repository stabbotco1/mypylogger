# Project Standards

**Purpose**: Python, Git, and CI/CD standards for mypylogger

## Python Standards

### Code Quality Tools
- black: Code formatting (line length 88)
- isort: Import sorting
- flake8: Linting
- mypy: Type checking
- bandit: Security scanning
- pip-audit: Dependency vulnerabilities

### Testing Requirements
- Minimum 90% code coverage (currently 96.48%)
- All tests must pass before merge
- Performance tests required for core functionality
- Use pytest with coverage plugin

### Type Hints
- All public functions must have type hints
- Use Optional[T] for nullable types (Python 3.8 compatibility)
- Avoid union syntax (|) - use Union[T1, T2] instead

### Documentation
- Docstrings required for all public functions/classes
- Follow Google docstring format
- Keep README.md updated with accurate badges

## Git Workflow

### Branch Strategy
- main: Production-ready code
- feature branches: task-N-description format
- No direct commits to main (use PRs for collaborative work)

### Commit Messages
Format: type: description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code change that neither fixes bug nor adds feature
- test: Adding or updating tests
- chore: Maintenance tasks
- task N: Completing kiro task N

Examples:
- "feat: add JSON formatting support"
- "fix: correct macOS sed syntax for badge updates"
- "task 9: add performance regression tracking"

### Pre-Commit Checklist
1. Run formatters: black . && isort .
2. Run linters: flake8 .
3. Run type checker: mypy mypylogger/
4. Run security scan: bandit -r mypylogger/
5. Run tests: pytest -v --cov
6. Check coverage: Must be >= 90%

Or use: ./scripts/pre-release-check.sh

## CI/CD Standards

### Quality Gates (All Must Pass)
1. Code formatting check (black)
2. Import sorting check (isort)
3. Linting (flake8)
4. Type checking (mypy)
5. Security scanning (bandit)
6. Dependency vulnerabilities (pip-audit)
7. Test execution (pytest)
8. Coverage threshold (90%+)
9. Package build verification
10. Documentation validation

### Performance Requirements
- Latency: < 0.1ms average
- Throughput: > 10,000 logs/second
- Memory: Minimal footprint

### GitHub Actions Workflows
- ci.yml: Main quality gate pipeline
- performance-badge-update.yml: Benchmark and badge updates
- security.yml: CodeQL and Trivy scanning
- manual-release.yml: PyPI deployment

### Release Process
1. Ensure all CI checks pass
2. Run pre-flight check: ./scripts/pre-release-check.sh
3. Trigger manual release via GitHub Actions
4. Verify PyPI publication
5. Update CURRENT_TASKS.md if releasing after task completion

## Virtual Environment

### Setup
- Use venv (not conda/virtualenv)
- Python 3.8+ required
- Always activate before work: source venv/bin/activate

### Dependencies
- Install with: pip install -e ".[dev]"
- Keep pyproject.toml up to date
- Run pip-audit regularly for vulnerabilities

## File Organization

### Package Structure
mypylogger/          # No src/ directory
  __init__.py        # Contains __version__
  config.py
  core.py
  formatters.py
  handlers.py

### Critical Files
- pyproject.toml: Package metadata, dependencies, tool configs
- README.md: User-facing documentation with badges
- CHANGELOG.md: Auto-generated release notes
- .kiro/: Project management (NOT in package)

## Security Standards

### No Secrets in Code
- Use environment variables
- Use GitHub OIDC for PyPI (no tokens)
- Never commit credentials

### Dependency Management
- Pin major versions in pyproject.toml
- Allow minor/patch updates
- Run pip-audit before releases
- Review security alerts promptly

## Performance Standards

### Benchmarking
- Run scripts/measure_performance.py for metrics
- Update badges on every push to main
- Investigate regressions immediately
- Document optimization decisions

### Optimization Rules
- Profile before optimizing
- Measure, don't guess
- Document trade-offs
- Keep benchmarks in version control

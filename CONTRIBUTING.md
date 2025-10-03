# Contributing to mypylogger

Thank you for your interest in contributing to mypylogger! This document provides guidelines and information for contributors.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/stabbotco1/mypylogger.git
   cd mypylogger
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Verify setup**
   ```bash
   python -c "import mypylogger; print('Setup successful!')"
   pytest
   ```

## Git Workflow

We use a GitFlow-inspired workflow with the following branches:

### Branch Structure
- **`main`**: Production-ready code, protected branch
- **`pre-release`**: Release candidate testing, protected branch
- **`feature/feature-name`**: New features, branched from pre-release
- **`bugfix/issue-description`**: Bug fixes, branched from pre-release
- **`hotfix/critical-issue`**: Emergency fixes, branched from main

### Development Process

1. **Create feature branch**
   ```bash
   git checkout pre-release
   git pull origin pre-release
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following TDD**
   - Write failing tests first
   - Implement minimal code to pass tests
   - Refactor while keeping tests green
   - Ensure all tests pass: `pytest`

3. **Commit with conventional messages**
   ```bash
   git add .
   git commit -m "feat(scope): add new feature description"
   ```

4. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create PR targeting `pre-release` branch
   - Fill out the PR template completely
   - Wait for review and CI checks

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `style`: Code style changes
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(logging): add structured JSON output
fix(handlers): resolve file handler flush issue
docs(readme): update installation instructions
test(core): add singleton pattern tests
```

## Code Standards

### Code Quality Requirements
- **Test Coverage**: Minimum 90% line coverage
- **Linting**: All code must pass flake8, black, isort
- **Type Checking**: All public APIs must have type hints
- **Documentation**: All public functions must have docstrings

### Style Guidelines
- **Formatting**: Use Black with 88 character line length
- **Import Organization**: Use isort for consistent import ordering
- **Type Hints**: All public functions and methods must include type hints
- **Docstrings**: Use Google-style docstrings for all public APIs

### Testing Requirements
- **Test-Driven Development**: Write tests before implementation
- **Test Categories**:
  - Unit tests: Fast (<1s), isolated, mocked dependencies
  - Integration tests: Medium (<30s), real dependencies
  - End-to-end tests: Slow (<5min), complete workflows
- **Coverage**: Maintain ≥90% test coverage
- **Performance**: Include performance regression tests

## Quality Checks

### Local Development
Run these commands before committing:

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run tests with coverage
pytest --cov=mypylogger --cov-report=html --cov-fail-under=90

# Security scan
bandit -r mypylogger/
safety check
```

### Pre-commit Hooks
The following checks run automatically on commit:
- Code formatting (Black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- Test execution (fast unit tests)

## Pull Request Process

### Before Submitting
- [ ] All tests pass locally
- [ ] Code coverage ≥ 90%
- [ ] No linting violations
- [ ] Security scans pass
- [ ] Documentation updated if needed
- [ ] Conventional commit messages used

### Review Process
1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one approving review required
3. **Testing**: Verify changes work in realistic scenarios
4. **Documentation**: Ensure docs are updated for user-facing changes
5. **Security**: Review for security implications

### Merge Requirements
- All automated tests pass
- Code coverage maintained or improved
- Security scans show no new vulnerabilities
- At least one approving review
- Branch is up to date with target branch

## Issue Reporting

### Bug Reports
When reporting bugs, please include:
- Python version and operating system
- mypylogger version
- Minimal code example that reproduces the issue
- Expected vs actual behavior
- Full error traceback if applicable

### Feature Requests
For new features, please provide:
- Clear description of the proposed feature
- Use case and motivation
- Proposed API or interface design
- Consideration of backward compatibility

## Security

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security concerns to: [security contact]
- Include detailed description and reproduction steps
- Allow time for coordinated disclosure

### Security Guidelines
- Never commit secrets, tokens, or credentials
- Validate all external inputs
- Follow secure coding practices
- Keep dependencies updated
- Use security scanning tools

## Documentation

### Documentation Standards
- **API Documentation**: Auto-generated from docstrings
- **Usage Examples**: Include practical, runnable examples
- **Architecture**: Document design decisions and rationales
- **Troubleshooting**: Common issues and solutions

### Documentation Updates
- Update docstrings for API changes
- Add examples for new features
- Update README for significant changes
- Maintain CHANGELOG.md for releases

## Release Process

### Version Management
- Follow [Semantic Versioning](https://semver.org/)
- Use pre-release versions for testing (e.g., 0.1.0a1, 0.1.0b1)
- Tag releases from main branch
- Update CHANGELOG.md for each release

### Release Checklist
- [ ] All tests pass on all supported Python versions
- [ ] Security scans clean
- [ ] Documentation updated
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] Git tag created
- [ ] PyPI package published

## Getting Help

### Resources
- **Documentation**: [GitHub README](https://github.com/stabbotco1/mypylogger#readme)
- **Issues**: [GitHub Issues](https://github.com/stabbotco1/mypylogger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/stabbotco1/mypylogger/discussions)

### Community Guidelines
- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Provide constructive feedback
- Follow the code of conduct

## Recognition

Contributors who make significant contributions will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to mypylogger! 🚀

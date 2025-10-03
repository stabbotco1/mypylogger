---
inclusion: always
---

# Development Standards

## Purpose
This document defines local development standards, real-time testing feedback, and developer productivity optimization patterns.

## Local Development Environment

### Required Tools
- **Python 3.8+**: Minimum supported version
- **Virtual Environment**: Isolated dependency management
- **Pre-commit**: Automated quality checks
- **pytest**: Test execution and coverage
- **Black**: Code formatting
- **isort**: Import organization
- **flake8**: Linting
- **mypy**: Type checking

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify setup
make test-fast
```

## Real-Time Testing Feedback

### Continuous Testing Loop
**Vision**: Save file → Immediate test feedback → Instant coverage update

#### Implementation Strategy
```bash
# File watcher with immediate feedback
pytest-watch --clear --onpass --onfail --runner "pytest --tb=short"

# Coverage monitoring
pytest --cov=mypylogger --cov-report=term-missing --cov-fail-under=90

# Real-time coverage display
coverage html && open htmlcov/index.html
```

#### Feedback Mechanisms
- **Terminal notifications**: Pass/fail status on save
- **Coverage percentage**: Real-time coverage display
- **Performance indicators**: Test execution time
- **Quality metrics**: Linting and type check status

### Fast Feedback Requirements
- **Unit tests**: Complete in <1 second
- **Coverage calculation**: <2 seconds total
- **Linting**: <500ms
- **Type checking**: <1 second
- **Total feedback loop**: <5 seconds

## Test-Driven Development (TDD)

### TDD Cycle
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green
4. **Repeat**: Continue with next requirement

### TDD Standards
- **Test first**: No production code without failing test
- **Minimal implementation**: Just enough to pass tests
- **Refactor safely**: Tests provide safety net
- **Fast feedback**: Immediate test execution

### Test Categories

#### Unit Tests (Fast)
```python
# Example: Fast unit test
def test_logger_singleton_returns_same_instance():
    logger1 = SingletonLogger.get_logger()
    logger2 = SingletonLogger.get_logger()
    assert logger1 is logger2
```

#### Integration Tests (Medium)
```python
# Example: Integration test
def test_complete_logging_workflow():
    logger = SingletonLogger.get_logger()
    logger.info("Test message")
    # Verify file creation, JSON format, etc.
```

#### End-to-End Tests (Slow)
```python
# Example: E2E test
def test_production_logging_scenario():
    # Test complete real-world usage
    pass
```

## Code Quality Standards

### Formatting Standards
- **Black**: Automatic code formatting (88 char line length)
- **isort**: Import statement organization
- **Consistent style**: No manual formatting decisions

### Linting Standards
- **flake8**: PEP 8 compliance
- **No warnings**: Zero tolerance for linting warnings
- **Custom rules**: Project-specific linting configuration

### Type Checking Standards
- **mypy**: Static type analysis
- **Type hints**: All public APIs must have type hints
- **Type coverage**: ≥95% type hint coverage
- **Strict mode**: Gradual adoption of strict type checking

### Documentation Standards
- **Docstrings**: Google-style docstrings for all public APIs
- **Type information**: Include parameter and return types
- **Examples**: Include usage examples in docstrings
- **API documentation**: Auto-generated from docstrings

## Performance Standards

### Local Performance Requirements
- **Test execution**: Unit tests <1s, integration <30s
- **Build time**: Package build <10s
- **Import time**: Module import <100ms
- **Memory usage**: <50MB baseline

### Performance Monitoring
```python
# Example: Performance test
def test_logging_performance():
    import time
    logger = SingletonLogger.get_logger()

    start = time.perf_counter()
    for _ in range(1000):
        logger.info("Performance test message")
    duration = time.perf_counter() - start

    assert duration < 1.0  # <1ms per log entry
```

## Development Workflow

### Daily Development Cycle
1. **Pull latest**: `git pull origin pre-release`
2. **Create branch**: `git checkout -b feature/new-feature`
3. **Write tests**: Start with failing tests
4. **Implement**: Write minimal code to pass
5. **Refactor**: Improve while maintaining green tests
6. **Commit**: Use conventional commit messages
7. **Push**: Trigger automated validation
8. **Create PR**: With clear description and context

### Quality Gates (Local)
Before every commit:
- [ ] All tests pass locally
- [ ] Coverage ≥ 90%
- [ ] No linting violations
- [ ] Type checking passes
- [ ] Documentation updated if needed

### Productivity Tools

#### Makefile Commands
```makefile
# Fast development commands
test-fast:
	pytest tests/unit/ -v

test-coverage:
	pytest --cov=mypylogger --cov-report=html --cov-fail-under=90

test-watch:
	pytest-watch --clear --onpass --onfail

lint:
	black . && isort . && flake8 . && mypy .

clean:
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/
```

#### IDE Integration
- **VS Code**: Python extension with pytest, black, mypy
- **PyCharm**: Built-in testing and quality tools
- **Vim/Neovim**: Language server protocol (LSP) integration
- **Emacs**: Python development environment

## Continuous Learning and Improvement

### Code Review Standards
- **Self-review**: Review your own code before PR
- **Constructive feedback**: Focus on code, not person
- **Learning opportunity**: Share knowledge and best practices
- **Quality focus**: Maintain high standards consistently

### Knowledge Sharing
- **Documentation**: Keep development docs updated
- **Comments**: Explain complex logic and decisions
- **Examples**: Provide clear usage examples
- **Patterns**: Document reusable patterns and solutions

### Metrics and Improvement
- **Track metrics**: Test coverage, build times, bug rates
- **Identify bottlenecks**: Slow tests, complex code areas
- **Continuous improvement**: Regular retrospectives and adjustments
- **Tool evaluation**: Regularly assess and upgrade development tools

## Error Handling and Debugging

### Error Handling Standards
- **Graceful degradation**: Continue operation when possible
- **Clear error messages**: Actionable error information
- **Logging errors**: Use appropriate log levels
- **Exception hierarchy**: Well-defined custom exceptions

### Debugging Tools
- **pytest**: Test debugging with `-s` and `--pdb`
- **Python debugger**: `pdb` and `ipdb` for interactive debugging
- **Logging**: Strategic debug logging for troubleshooting
- **Profiling**: `cProfile` and `line_profiler` for performance analysis

### Debugging Workflow
1. **Reproduce**: Create minimal test case
2. **Isolate**: Narrow down to specific component
3. **Debug**: Use appropriate debugging tools
4. **Fix**: Implement minimal fix
5. **Test**: Verify fix with comprehensive tests
6. **Document**: Update docs if needed

## Security in Development

### Secure Coding Practices
- **Input validation**: Validate all external inputs
- **Dependency management**: Keep dependencies updated
- **Secret management**: Never commit secrets to code
- **Code scanning**: Regular security scans

### Security Tools Integration
- **bandit**: Security linting during development
- **safety**: Dependency vulnerability checking
- **pre-commit**: Automated security checks
- **IDE plugins**: Real-time security feedback

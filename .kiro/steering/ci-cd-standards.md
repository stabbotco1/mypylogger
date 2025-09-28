---
inclusion: always
---

# CI/CD Standards

## Purpose
This document defines continuous integration and deployment standards, including automated testing, security scanning, and quality assurance pipelines.

## Pipeline Architecture

### Multi-Stage Pipeline
```
Code Push → Quality Gates → Security Scan → Test Matrix → Deploy
     ↓           ↓              ↓            ↓         ↓
   Lint      Unit Tests    Vulnerability   Integration  PyPI
   Format    Type Check    Scan           E2E Tests    Docs
   Style     Coverage      Malware        Performance  Release
```

## Quality Gates

### Stage 1: Code Quality
**Triggers**: Every push, every PR
**Tools**: 
- **Black**: Code formatting enforcement
- **isort**: Import statement organization
- **flake8**: PEP 8 compliance and linting
- **mypy**: Static type checking
- **bandit**: Basic security linting

**Requirements**:
- [ ] All formatting checks pass
- [ ] No linting violations
- [ ] Type hints coverage ≥ 95%
- [ ] No security warnings from bandit

### Stage 2: Testing
**Triggers**: After code quality passes
**Tools**:
- **pytest**: Test execution
- **pytest-cov**: Coverage measurement
- **pytest-xdist**: Parallel test execution
- **tox**: Multi-environment testing

**Requirements**:
- [ ] All tests pass (100%)
- [ ] Coverage ≥ 90%
- [ ] No test failures or errors
- [ ] Performance within acceptable limits

### Stage 3: Security Scanning
**Triggers**: On PR to protected branches
**Tools**:
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Comprehensive vulnerability scanner
- **CodeQL**: Semantic code analysis
- **Semgrep**: Static analysis security testing

**Requirements**:
- [ ] No high or critical vulnerabilities
- [ ] All dependencies scanned clean
- [ ] No malicious code patterns detected
- [ ] Security policy compliance verified

### Stage 4: Integration Testing
**Triggers**: On merge to pre-release/main
**Tools**:
- **Docker**: Containerized testing
- **pytest**: End-to-end test suite
- **Performance tests**: Load and stress testing
- **Compatibility tests**: Multi-version testing

**Requirements**:
- [ ] All integration tests pass
- [ ] Performance benchmarks met
- [ ] Multi-environment compatibility verified
- [ ] Documentation builds successfully

## Badge Integration

### Required Badges
Display in README.md header:

```markdown
[![Build Status](https://github.com/username/mypylogger/workflows/CI/badge.svg)](https://github.com/username/mypylogger/actions)
[![Coverage](https://codecov.io/gh/username/mypylogger/branch/main/graph/badge.svg)](https://codecov.io/gh/username/mypylogger)
[![Security](https://github.com/username/mypylogger/workflows/Security/badge.svg)](https://github.com/username/mypylogger/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/mypylogger.svg)](https://badge.fury.io/py/mypylogger)
[![Python versions](https://img.shields.io/pypi/pyversions/mypylogger.svg)](https://pypi.org/project/mypylogger/)
[![Downloads](https://pepy.tech/badge/mypylogger)](https://pepy.tech/project/mypylogger)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

### Badge Services
- **GitHub Actions**: Build and test status
- **Codecov**: Test coverage reporting
- **PyPI**: Version and download statistics
- **Shields.io**: Custom badges and metrics
- **Snyk**: Security vulnerability status

## Automated Testing Strategy

### Test Categories

#### Unit Tests (Fast - <1s total)
- **Scope**: Individual functions and classes
- **Isolation**: Mocked dependencies
- **Coverage**: 100% of core logic
- **Execution**: On every commit

#### Integration Tests (Medium - <30s total)
- **Scope**: Component interactions
- **Environment**: Real dependencies
- **Coverage**: Critical user workflows
- **Execution**: On PR creation

#### End-to-End Tests (Slow - <5min total)
- **Scope**: Complete user scenarios
- **Environment**: Production-like setup
- **Coverage**: Major use cases
- **Execution**: On merge to protected branches

### Test Matrix

#### Python Versions
- Python 3.8 (minimum supported)
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12 (latest)

#### Operating Systems
- Ubuntu Latest (primary)
- macOS Latest (compatibility)
- Windows Latest (compatibility)

#### Dependencies
- Minimum versions (compatibility)
- Latest versions (current)
- Pre-release versions (future compatibility)

## Security Automation

### Vulnerability Scanning

#### Dependency Scanning
```yaml
# Daily automated scan
- name: Safety Check
  run: safety check --json
  
- name: Trivy Scan
  run: trivy fs --security-checks vuln .
```

#### Code Analysis
```yaml
# On every PR
- name: CodeQL Analysis
  uses: github/codeql-action/analyze
  
- name: Semgrep Scan
  run: semgrep --config=auto .
```

#### Container Scanning
```yaml
# If using containers
- name: Container Scan
  run: trivy image mypylogger:latest
```

### Security Reporting
- **Automated alerts**: Slack/email on vulnerabilities
- **Security dashboard**: Centralized vulnerability tracking
- **Compliance reports**: Regular security posture reports
- **Incident response**: Automated security incident workflows

## Performance Monitoring

### Performance Tests
- **Benchmark tests**: Core functionality performance
- **Load tests**: High-volume logging scenarios
- **Memory tests**: Memory usage and leak detection
- **Regression tests**: Performance trend monitoring

### Performance Gates
- **Latency**: <1ms per log entry (95th percentile)
- **Throughput**: >10,000 logs/second
- **Memory**: <50MB baseline memory usage
- **CPU**: <5% CPU usage under normal load

## Deployment Automation

### PyPI Publication
```yaml
# On git tag creation
- name: Build Package
  run: python -m build
  
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
```

### Documentation Deployment
```yaml
# On merge to main
- name: Build Docs
  run: mkdocs build
  
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
```

## Monitoring and Alerting

### Build Monitoring
- **Failure alerts**: Immediate notification on build failures
- **Performance alerts**: Notification on performance degradation
- **Security alerts**: Immediate notification on vulnerabilities
- **Dependency alerts**: Notification on outdated dependencies

### Quality Metrics
- **Test coverage trends**: Track coverage over time
- **Build time trends**: Monitor CI/CD performance
- **Security posture**: Track vulnerability remediation
- **Code quality metrics**: Track technical debt

## Local Development Integration

### Pre-commit Integration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Local Testing Commands
```bash
# Fast feedback loop
make test-fast      # Unit tests only (<1s)
make test-coverage  # With coverage report
make test-security  # Security scans
make test-all      # Full test suite
```

### Real-time Feedback
- **File watcher**: Automatic test execution on save
- **Coverage display**: Real-time coverage percentage
- **Quality indicators**: Immediate feedback on code quality
- **Performance monitoring**: Local performance regression detection
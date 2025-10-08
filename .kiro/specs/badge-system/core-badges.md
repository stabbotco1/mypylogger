# Core Badges Specification (Tier 1)

**Purpose**: Document Tier 1 badges - critical quality indicators that must always pass for production readiness.

## Tier 1 Overview

**Tier Definition**: Core Status badges that indicate blocking failures

**Badge Count**: 4 badges

**Failure Impact**: Project is not production-ready if any Tier 1 badge fails

**Update Frequency**: Real-time (within 5 minutes of source change)

**Badges**:
1. Build Status
2. Coverage
3. Security
4. License

---

## Badge 1: Build Status

**Status**: ✅ Working  
**Tier**: 1 (Core Status)  
**Update Mechanism**: Workflow-Driven (GitHub Actions)

### Purpose
Indicates whether the CI/CD pipeline is passing. This badge shows that:
- All tests pass across Python 3.8-3.12
- Code quality checks pass (black, isort, flake8, mypy)
- Security scans complete successfully
- Package builds without errors

### Data Source
- **Workflow**: `.github/workflows/ci.yml`
- **Workflow Name**: `CI/CD Pipeline`
- **Shields.io Endpoint**: `github/actions/workflow/status`

### Current Implementation

```markdown
[![Build Status](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/ci.yml?branch=main&label=build&logo=github)](https://github.com/stabbotco1/mypylogger/actions/workflows/ci.yml)
```

**Badge URL Components**:
- Base: `https://img.shields.io/github/actions/workflow/status/`
- Owner: `stabbotco1`
- Repo: `mypylogger`
- Workflow: `ci.yml`
- Branch: `?branch=main`
- Label: `&label=build`
- Logo: `&logo=github`

**Link Target**: `https://github.com/stabbotco1/mypylogger/actions/workflows/ci.yml`

**Alt Text**: `Build Status`

### Update Process

1. **Trigger**: Developer pushes to main or pre-release branch
2. **Workflow Execution**: 
   - Quality gates (formatting, linting, type checking)
   - Test matrix (Python 3.8-3.12, Ubuntu/macOS)
   - Coverage validation (≥90%)
   - Package build and validation
3. **Status Update**: Workflow status written to GitHub API
4. **Badge Update**: Shields.io polls GitHub API (5-minute cache)
5. **Display**: Badge shows success (green) or failure (red)

### Verification

**Method 1: Visual Inspection**
```
Action: View README.md on GitHub
Expected: Green "build | passing" badge
Location: First badge in Tier 1 row
```

**Method 2: HTTP 200 Check**
```bash
# Automated by validate_badges.py
curl -I "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/ci.yml?branch=main"
# Expected: HTTP 200 OK
```

**Method 3: Link Target Validation**
```bash
# Verify link navigates to correct workflow
curl -I "https://github.com/stabbotco1/mypylogger/actions/workflows/ci.yml"
# Expected: HTTP 200 OK
```

### Acceptance Criteria

**Working Correctly Means**:
- ✅ Badge URL returns HTTP 200
- ✅ Badge displays current workflow status (not "unknown")
- ✅ Badge updates within 5 minutes of workflow completion
- ✅ Badge link navigates to ci.yml workflow page
- ✅ Badge color matches status (green=passing, red=failing, yellow=pending)

### Known Issues

**Issue 1: Workflow Name Mismatch**
- **Symptom**: Badge shows "unknown" despite passing workflow
- **Cause**: Workflow name doesn't match badge URL expectation
- **Resolution**: Workflow file name (ci.yml) used instead of display name
- **Status**: Fixed - using file name reference

**Issue 2: Shields.io Cache Delay**
- **Symptom**: Badge shows old status for up to 5 minutes
- **Cause**: Shields.io caching mechanism
- **Resolution**: Accept as normal behavior (improves performance)
- **Status**: Expected behavior, not a bug

### Dependencies

**Workflow File**: `.github/workflows/ci.yml`
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, pre-release ]
  pull_request:
    branches: [ main, pre-release ]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    # ... quality checks ...
  
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    # ... test execution ...
```

**External Services**:
- GitHub Actions (workflow execution)
- Shields.io (badge generation)
- GitHub API (status polling)

**Environment Variables**: None required

---

## Badge 2: Coverage

**Status**: ✅ Working  
**Tier**: 1 (Core Status)  
**Update Mechanism**: Static (Manual - currently showing 96.48%)

### Purpose
Displays test coverage percentage to demonstrate code quality and test thoroughness. Indicates:
- Percentage of code exercised by tests
- Quality of test suite
- Areas of code that are untested

### Data Source
- **Current**: Static value in badge URL (96.48%)
- **Source**: Pytest coverage reports from CI/CD pipeline
- **Future Option**: Could integrate with Codecov API for dynamic updates

### Current Implementation

```markdown
[![Coverage](https://img.shields.io/badge/coverage-96.48%25-brightgreen?logo=codecov)](https://codecov.io/gh/stabbotco1/mypylogger)
```

**Badge URL Components**:
- Base: `https://img.shields.io/badge/`
- Label: `coverage`
- Message: `96.48%25` (URL-encoded: %25 = %)
- Color: `brightgreen`
- Logo: `?logo=codecov`

**Link Target**: `https://codecov.io/gh/stabbotco1/mypylogger`

**Alt Text**: `Coverage`

### Update Process

**Current (Manual)**:
1. CI/CD runs pytest with coverage
2. Coverage report generated (currently 96.48%)
3. Developer manually updates badge URL in README.md when coverage changes significantly
4. Commit and push updated README.md

**Future (Automated via Codecov)**:
```markdown
[![Coverage](https://img.shields.io/codecov/c/github/stabbotco1/mypylogger?logo=codecov)](https://codecov.io/gh/stabbotco1/mypylogger)
```
- Codecov receives coverage data from CI/CD
- Shields.io queries Codecov API
- Badge updates automatically

### Verification

**Method 1: Visual Inspection**
```
Action: View README.md on GitHub
Expected: Green badge showing "coverage | >=%"
Location: Second badge in Tier 1 row
```

**Method 2: HTTP 200 Check**
```bash
curl -I "https://img.shields.io/badge/coverage-96.48%25-brightgreen?logo=codecov"
# Expected: HTTP 200 OK
```

**Method 3: Link Target Validation**
```bash
curl -I "https://codecov.io/gh/stabbotco1/mypylogger"
# Expected: HTTP 200 OK
```

**Method 4: Actual Coverage Verification**
```bash
# Run tests locally with coverage
pytest --cov=mypylogger --cov-report=term-missing

# Verify coverage matches badge (±0.5%)
# Current coverage: 96.48%
```

### Acceptance Criteria

**Working Correctly Means**:
- ✅ Badge URL returns HTTP 200
- ✅ Badge displays accurate coverage percentage (within 0.5% of actual)
- ✅ Badge updates when coverage changes significantly (>1% change)
- ✅ Badge link navigates to Codecov dashboard
- ✅ Badge color reflects coverage quality:
  - Green: ≥90%
  - Yellow: 80-89%
  - Red: <80%

### Known Issues

**Issue 1: Manual Update Burden**
- **Symptom**: Badge may show slightly outdated coverage
- **Cause**: Manual update process
- **Resolution**: Consider automating with Codecov integration
- **Status**: Acceptable - coverage changes infrequently

**Issue 2: URL Encoding**
- **Symptom**: Percent sign requires encoding (%25)
- **Cause**: URL encoding rules
- **Resolution**: Always use %25 for percent sign in badge URLs
- **Status**: Working as designed

### Dependencies

**CI/CD Workflow**: `.github/workflows/ci.yml`
```yaml
test-matrix:
  steps:
    - name: Run tests with coverage
      run: |
        pytest --cov=mypylogger --cov-report=xml --cov-report=term-missing --cov-fail-under=90
```

**External Services**:
- Shields.io (badge generation)
- Codecov.io (coverage link target)
- Pytest (coverage measurement)

**Configuration**: `pyproject.toml`
```toml
[tool.pytest.ini_options]
addopts = "--cov=mypylogger --cov-report=html --cov-report=term-missing --cov-fail-under=90"
```

---

## Badge 3: Security

**Status**: ✅ Working  
**Tier**: 1 (Core Status)  
**Update Mechanism**: Workflow-Driven (GitHub Actions)

### Purpose
Indicates security scan status from multiple tools:
- CodeQL semantic analysis
- Trivy vulnerability scanning
- Bandit Python security linting
- Safety dependency scanning

Shows that the codebase has been scanned for known vulnerabilities and security issues.

### Data Source
- **Workflow**: `.github/workflows/security.yml`
- **Workflow Name**: `Security Scanning`
- **Shields.io Endpoint**: `github/actions/workflow/status`

### Current Implementation

```markdown
[![Security](https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/security.yml?branch=main&label=security&logo=github)](https://github.com/stabbotco1/mypylogger/actions/workflows/security.yml)
```

**Badge URL Components**:
- Base: `https://img.shields.io/github/actions/workflow/status/`
- Owner: `stabbotco1`
- Repo: `mypylogger`
- Workflow: `security.yml`
- Branch: `?branch=main`
- Label: `&label=security`
- Logo: `&logo=github`

**Link Target**: `https://github.com/stabbotco1/mypylogger/actions/workflows/security.yml`

**Alt Text**: `Security`

### Update Process

1. **Trigger**: 
   - Push to main/pre-release branches
   - Daily scheduled scan (2 AM UTC)
   - Pull requests
2. **Workflow Execution**:
   - Bandit security scan (Python-specific)
   - Safety dependency scan (vulnerabilities)
   - CodeQL analysis (semantic code analysis)
   - Trivy vulnerability scanner
3. **Status Update**: Workflow status written to GitHub API
4. **Badge Update**: Shields.io polls GitHub API (5-minute cache)
5. **Display**: Badge shows security scan status

### Verification

**Method 1: Visual Inspection**
```
Action: View README.md on GitHub
Expected: Green "security | passing" badge
Location: Third badge in Tier 1 row
```

**Method 2: HTTP 200 Check**
```bash
curl -I "https://img.shields.io/github/actions/workflow/status/stabbotco1/mypylogger/security.yml?branch=main"
# Expected: HTTP 200 OK
```

**Method 3: Link Target Validation**
```bash
curl -I "https://github.com/stabbotco1/mypylogger/actions/workflows/security.yml"
# Expected: HTTP 200 OK
```

**Method 4: Local Security Scan**
```bash
# Run security scans locally
bandit -r mypylogger/ -f txt
safety check

# Verify no HIGH or CRITICAL issues
```

### Acceptance Criteria

**Working Correctly Means**:
- ✅ Badge URL returns HTTP 200
- ✅ Badge displays current security scan status
- ✅ Badge updates within 5 minutes of workflow completion
- ✅ Badge link navigates to security.yml workflow page
- ✅ Badge is green when all security scans pass
- ✅ Badge is red when any security scan fails

### Known Issues

**Issue 1: False Positives**
- **Symptom**: Security scan flags non-issues
- **Cause**: Overly aggressive security rules
- **Resolution**: Configure exceptions in tool configs (.bandit, etc.)
- **Status**: Managed through configuration

**Issue 2: Scheduled Scan Delays**
- **Symptom**: Daily scan may not reflect very recent changes
- **Cause**: Scheduled run at 2 AM UTC
- **Resolution**: Push-triggered scans provide real-time updates
- **Status**: Working as designed (daily scan is supplementary)

### Dependencies

**Workflow File**: `.github/workflows/security.yml`
```yaml
name: Security Scanning

on:
  push:
    branches: [ main, pre-release ]
  pull_request:
    branches: [ main, pre-release ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      # Bandit, Safety, CodeQL, Trivy scans
```

**External Services**:
- GitHub Actions (workflow execution)
- GitHub CodeQL (semantic analysis)
- Shields.io (badge generation)

**Security Tools**:
- Bandit: Python security linter
- Safety: Dependency vulnerability scanner
- CodeQL: GitHub's semantic code analysis
- Trivy: Comprehensive vulnerability scanner

---

## Badge 4: License

**Status**: ✅ Working  
**Tier**: 1 (Core Status)  
**Update Mechanism**: Static (GitHub License Detection)

### Purpose
Displays the project license (MIT) to inform users of:
- Legal terms for using the library
- Permissions granted
- Limitations and warranty disclaimers
- Commercial use allowance

### Data Source
- **Source**: LICENSE file in repository root
- **Detection**: GitHub automatic license detection
- **Shields.io Query**: GitHub License API

### Current Implementation

```markdown
[![License](https://img.shields.io/github/license/stabbotco1/mypylogger?color=blue)](https://opensource.org/licenses/MIT)
```

**Badge URL Components**:
- Base: `https://img.shields.io/github/license/`
- Owner: `stabbotco1`
- Repo: `mypylogger`
- Color: `?color=blue`

**Link Target**: `https://opensource.org/licenses/MIT`

**Alt Text**: `License`

### Update Process

**Automatic**:
1. LICENSE file exists in repository root
2. GitHub detects license type (MIT)
3. Shields.io queries GitHub API for license info
4. Badge displays "MIT" automatically
5. Update only if LICENSE file changes (rare)

### Verification

**Method 1: Visual Inspection**
```
Action: View README.md on GitHub
Expected: Blue badge showing "license | MIT"
Location: Fourth badge in Tier 1 row
```

**Method 2: HTTP 200 Check**
```bash
curl -I "https://img.shields.io/github/license/stabbotco1/mypylogger"
# Expected: HTTP 200 OK
```

**Method 3: Link Target Validation**
```bash
curl -I "https://opensource.org/licenses/MIT"
# Expected: HTTP 200 OK
```

**Method 4: License File Verification**
```bash
# Verify LICENSE file exists and is MIT
cat LICENSE | head -n 5
# Expected: "MIT License" header
```

### Acceptance Criteria

**Working Correctly Means**:
- ✅ Badge URL returns HTTP 200
- ✅ Badge displays "MIT" (matches actual license)
- ✅ Badge link navigates to MIT license text
- ✅ Badge color is blue (informational, not status-based)
- ✅ LICENSE file exists in repository root
- ✅ GitHub correctly detects license type

### Known Issues

**Issue 1: License Detection Delay**
- **Symptom**: New repositories may show "unknown" briefly
- **Cause**: GitHub license detection runs asynchronously
- **Resolution**: Wait 5-10 minutes after creating LICENSE file
- **Status**: One-time issue during initial setup

**Issue 2: Non-Standard License Text**
- **Symptom**: GitHub fails to detect license if text is modified
- **Cause**: License detection requires standard formatting
- **Resolution**: Use unmodified MIT license text
- **Status**: Not applicable - using standard MIT text

### Dependencies

**License File**: `LICENSE` (repository root)
```text
MIT License

Copyright (c) [year] [author]

Permission is hereby granted, free of charge, to any person obtaining a copy
...
```

**Package Metadata**: `pyproject.toml`
```toml
[project]
license = {text = "MIT"}
```

**External Services**:
- GitHub License API (license detection)
- Shields.io (badge generation)
- opensource.org (license text reference)

---

## Tier 1 Summary

### Badge Health Status

| Badge | Status | Update Mechanism | Frequency | Critical? |
|-------|--------|------------------|-----------|-----------|
| Build Status | ✅ Working | Workflow-Driven | Every push | Yes |
| Coverage | ✅ Working | Static (Manual) | As needed | Yes |
| Security | ✅ Working | Workflow-Driven | Push + Daily | Yes |
| License | ✅ Working | Static (GitHub API) | Rarely | Yes |

### Common Patterns

**Workflow-Driven Badges** (Build, Security):
- Use GitHub Actions workflow status
- Update within 5 minutes via Shields.io polling
- Link to workflow runs page
- Green = passing, Red = failing

**Static Badges** (Coverage, License):
- Content embedded in badge URL or queried from API
- Update on manual commit or license file change
- Link to external service (Codecov, opensource.org)
- Color manually selected or API-determined

### Verification Schedule

**Automated** (via `.github/workflows/badge-health.yml`):
- On every push to main/pre-release
- On every pull request
- Daily at 6 AM UTC
- Manual workflow dispatch

**Manual**:
- Before every release
- After badge URL changes
- When troubleshooting issues

### Failure Response

**If Any Tier 1 Badge Fails**:
1. **Immediate**: Badge turns red (workflow badges) or shows error
2. **Automated**: GitHub issue created by badge-health.yml
3. **Developer Action**: Investigation required before release
4. **Resolution**: Fix underlying issue, verify badge updates
5. **Validation**: Run `validate_badges.py` to confirm

**Release Blocker**: Any Tier 1 badge failure blocks production release

### Maintenance Schedule

**Weekly**:
- Review badge health workflow results
- Check for slow response times

**Monthly**:
- Verify badge accuracy against actual status
- Review and update badge URLs if needed

**Per Release**:
- Verify all Tier 1 badges are green
- Run full badge validation
- Check badge display on PyPI after publish

### Integration Points

**All Tier 1 Badges Integrate With**:
- README.md (badge display)
- Shields.io (badge generation)
- validate_badges.py (automated validation)
- badge-health.yml (health monitoring)

**Workflow-Driven Badges Additionally Integrate With**:
- GitHub Actions (status source)
- GitHub API (status polling)

**Static Badges Additionally Integrate With**:
- Package metadata (pyproject.toml)
- External APIs (GitHub License, Codecov)

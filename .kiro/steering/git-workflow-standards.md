---
inclusion: always
---

# Git Workflow Standards

## Purpose
This document defines git branching strategy, merge policies, and automated quality gates to ensure code quality and project stability.

## Branch Strategy

### GitFlow Model
```
main (production)
├── pre-release (staging)
│   ├── feature/feature-name
│   ├── bugfix/issue-description
│   └── hotfix/critical-fix
└── develop (integration)
```

### Branch Types and Rules

#### Main Branch
- **Purpose**: Production-ready code only
- **Protection**: No direct commits allowed
- **Merges**: Only from pre-release via PR
- **Requirements**: All quality gates must pass
- **Tagging**: All releases tagged from main

#### Pre-release Branch
- **Purpose**: Release candidate testing
- **Protection**: No direct commits allowed
- **Merges**: From feature branches via PR
- **Requirements**: Full test suite + security scan
- **Promotion**: To main after validation

#### Feature Branches
- **Naming**: `feature/descriptive-name`
- **Source**: Branched from pre-release
- **Target**: Merge back to pre-release
- **Lifecycle**: Delete after successful merge
- **Requirements**: Local testing before push

#### Bugfix Branches
- **Naming**: `bugfix/issue-description`
- **Source**: Branched from pre-release
- **Target**: Merge back to pre-release
- **Priority**: Higher review priority than features

#### Hotfix Branches
- **Naming**: `hotfix/critical-issue`
- **Source**: Branched from main
- **Target**: Merge to both main and pre-release
- **Process**: Emergency process, expedited review

## Merge Policies

### Pull Request Requirements
- [ ] **Automated Tests**: All tests must pass
- [ ] **Code Coverage**: Coverage must not decrease
- [ ] **Security Scan**: Clean security scan required
- [ ] **Code Review**: At least one approving review
- [ ] **Documentation**: Updated if API changes
- [ ] **Changelog**: Entry added for user-facing changes

### Branch Protection Rules
```yaml
main:
  - Require PR reviews: 1
  - Dismiss stale reviews: true
  - Require status checks: true
  - Require up-to-date branches: true
  - Include administrators: true
  - Restrict pushes: true

pre-release:
  - Require PR reviews: 1
  - Require status checks: true
  - Require up-to-date branches: true
  - Allow force pushes: false
```

## Automated Quality Gates

### Pre-commit Hooks
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Fast unit tests

### GitHub Actions Workflows

#### On Push to Feature Branch
```yaml
- Code quality checks (lint, format, type)
- Unit tests
- Security scan (bandit)
- Coverage report
```

#### On Pull Request
```yaml
- Full test suite
- Integration tests
- Security scan (bandit, safety)
- Documentation build
- Coverage analysis
- Performance regression tests
```

#### On Merge to Pre-release
```yaml
- Full test matrix (all Python versions)
- End-to-end tests
- Security scan (trivy, codeql)
- Documentation deployment
- Pre-release package build
```

#### On Tag Creation (Release)
```yaml
- Full validation suite
- Security audit
- Package build and test
- PyPI publication
- Documentation update
- Release notes generation
```

## Local Development Standards

### Required Local Setup
- **Pre-commit hooks**: Installed and active
- **Virtual environment**: Isolated dependencies
- **Test runner**: Fast feedback loop
- **Coverage monitoring**: Real-time coverage display

### Development Workflow
1. **Branch**: Create feature branch from pre-release
2. **Develop**: Write tests first (TDD)
3. **Test**: Run full test suite locally
4. **Commit**: Use conventional commit messages
5. **Push**: Trigger automated validation
6. **PR**: Create pull request with description
7. **Review**: Address feedback and re-test
8. **Merge**: Squash and merge after approval

## Commit Standards

### Conventional Commits
```
type(scope): description

feat(auth): add user authentication
fix(logging): resolve timestamp formatting issue
docs(readme): update installation instructions
test(core): add singleton pattern tests
refactor(handlers): simplify file handler logic
```

### Commit Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **test**: Test additions or modifications
- **refactor**: Code refactoring
- **style**: Code style changes
- **perf**: Performance improvements
- **chore**: Maintenance tasks

## Quality Enforcement

### Automated Enforcement
- Branch protection prevents policy violations
- Status checks block merges on failures
- Automated testing prevents regressions
- Security scans prevent vulnerable code

### Manual Enforcement
- Code review ensures quality standards
- Documentation review ensures clarity
- Architecture review for significant changes
- Security review for sensitive modifications

## Emergency Procedures

### Hotfix Process
1. **Create hotfix branch** from main
2. **Implement minimal fix** with tests
3. **Fast-track review** (expedited process)
4. **Merge to main** and tag immediately
5. **Cherry-pick to pre-release** to sync branches
6. **Post-mortem** to prevent recurrence

### Rollback Process
1. **Identify issue** in production
2. **Revert commit** or tag previous version
3. **Deploy previous version** immediately
4. **Create hotfix** for proper resolution
5. **Document incident** and lessons learned

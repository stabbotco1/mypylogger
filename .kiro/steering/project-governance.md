---
inclusion: always
---

# Project Governance Standards

## Purpose
This document establishes governance standards for project licensing, versioning, security, and quality assurance that apply across all development phases.

## Licensing Standards

### MIT License Policy
- **License**: MIT License for maximum community adoption
- **Attribution**: Copyright retained by original author
- **Commercial Use**: Permitted with attribution
- **Modification**: Permitted with attribution
- **Distribution**: Permitted with attribution

### License Requirements
- LICENSE file must be present in project root
- All source files must include copyright header
- Third-party dependencies must be license-compatible
- License compatibility verified before adding dependencies

## Versioning Standards

### Semantic Versioning (SemVer)
- **Format**: MAJOR.MINOR.PATCH (e.g., 1.2.3)
- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New functionality (backward-compatible)
- **PATCH**: Bug fixes (backward-compatible)

### Pre-release Versioning
- **Alpha**: 0.1.0a1, 0.1.0a2 (early development)
- **Beta**: 0.1.0b1, 0.1.0b2 (feature complete, testing)
- **Release Candidate**: 0.1.0rc1 (production ready, final testing)

### Version Enforcement
- Git tags must match version in pyproject.toml
- Version bumps require explicit approval
- Breaking changes must increment MAJOR version
- All releases must be tagged in git

## Security Standards

### Vulnerability Management
- **SECURITY.md**: Document security reporting process
- **Known vulnerabilities**: Tracked in VULNERABILITIES.md
- **Security scanning**: Automated in CI/CD pipeline
- **Dependency scanning**: Regular updates and vulnerability checks

### Security Tools Integration
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **CodeQL**: GitHub's semantic code analysis
- **Trivy**: Container and filesystem vulnerability scanner

## Quality Assurance Standards

### Code Quality Requirements
- **Test Coverage**: Minimum 90% line coverage
- **Linting**: All code must pass flake8, black, isort
- **Type Checking**: All public APIs must have type hints
- **Documentation**: All public functions must have docstrings

### Badge Requirements
Projects must display badges for:
- **Build Status**: CI/CD pipeline status
- **Test Coverage**: Percentage coverage with link to report
- **Security Scan**: Clean security scan status
- **License**: MIT License badge
- **Version**: Current PyPI version
- **Python Versions**: Supported Python versions
- **Downloads**: PyPI download statistics

## Release Process

### Release Criteria
- [ ] All tests pass (100%)
- [ ] Coverage ≥ 90%
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] Version bumped appropriately
- [ ] CHANGELOG.md updated
- [ ] Git tag created

### Release Automation
- Automated testing on all supported Python versions
- Automated security scanning
- Automated PyPI publication on tag creation
- Automated documentation deployment

## Compliance and Monitoring

### Continuous Monitoring
- Daily dependency vulnerability scans
- Weekly security policy reviews
- Monthly license compliance audits
- Quarterly governance policy reviews

### Quality Gates
- No merge without passing tests
- No release without security scan
- No dependency addition without license review
- No version bump without changelog update
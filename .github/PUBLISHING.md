# PyPI Publishing Guide

This document describes the secure PyPI publishing process for mypylogger v0.2.0.

## Overview

The publishing workflow uses GitHub Actions with OIDC (OpenID Connect) authentication to securely publish packages to PyPI without storing long-lived tokens.

## Security Features

### OIDC Authentication
- **No stored secrets**: Uses GitHub's OIDC provider to authenticate with PyPI
- **Short-lived tokens**: Authentication tokens are generated per-workflow and expire quickly
- **Scoped permissions**: Tokens are scoped to specific repositories and workflows

### Quality Gates
- **Complete test suite**: All tests must pass with 95%+ coverage
- **Code quality checks**: Linting, formatting, and type checking must pass
- **Security scanning**: No security vulnerabilities allowed
- **Package verification**: Built packages are verified before upload

## Publishing Process

### Prerequisites

1. **PyPI Project Setup**
   - Project must exist on PyPI: https://pypi.org/project/mypylogger/
   - OIDC authentication must be configured for the repository

2. **Repository Configuration**
   - Publishing environment must be configured in repository settings
   - Workflow permissions must allow `id-token: write`

### Manual Publishing Steps

1. **Navigate to Actions**
   - Go to repository Actions tab
   - Select "Publish to PyPI" workflow

2. **Trigger Workflow**
   - Click "Run workflow"
   - Enter version number (e.g., "0.2.0")
   - Choose dry run mode for testing (optional)

3. **Monitor Progress**
   - Watch workflow execution in real-time
   - Review quality gate results
   - Verify package building and publishing

### Workflow Stages

#### Stage 1: Pre-Publishing Validation
- **Test Suite**: Complete test execution across Python versions
- **Quality Checks**: Linting, formatting, type checking
- **Version Validation**: Semantic version format verification
- **Security Scans**: Dependency and code security validation

#### Stage 2: Package Building
- **Clean Build**: Remove previous build artifacts
- **Standard Tools**: Use Python `build` package for sdist and wheel
- **Verification**: Validate package contents and metadata
- **Installation Test**: Test package installation in clean environment

#### Stage 3: PyPI Publishing
- **OIDC Authentication**: Secure authentication with PyPI
- **Upload**: Publish source distribution and wheel
- **Verification**: Confirm successful upload
- **Success Reporting**: Provide confirmation and next steps

## Dry Run Mode

### Purpose
- Test the complete publishing pipeline without actually publishing
- Validate package building and verification steps
- Ensure all quality gates pass before real publishing

### Usage
```bash
# In GitHub Actions UI:
# 1. Select "Publish to PyPI" workflow
# 2. Click "Run workflow"
# 3. Set dry_run: true
# 4. Enter version number
# 5. Click "Run workflow"
```

### What Gets Tested
- ✅ All quality gates and validations
- ✅ Package building with standard tools
- ✅ Package verification and metadata checks
- ✅ Installation testing in clean environment
- ❌ Actual PyPI upload (skipped in dry run)

## Version Management

### Semantic Versioning
- **Format**: `MAJOR.MINOR.PATCH` (e.g., 0.2.0)
- **Pre-releases**: `MAJOR.MINOR.PATCH-SUFFIX` (e.g., 0.2.0-beta1)
- **Validation**: Workflow validates version format automatically

### Version Consistency
- Version in workflow input must match project version
- Consider updating `pyproject.toml` version before publishing
- Create Git tags for published versions

## Security Considerations

### OIDC Configuration
```yaml
# Required permissions in workflow
permissions:
  id-token: write  # For OIDC authentication
  contents: read   # For repository access
```

### PyPI Trusted Publishing
1. **Configure on PyPI**:
   - Go to project settings on PyPI
   - Add GitHub as trusted publisher
   - Specify repository and workflow details

2. **Repository Settings**:
   - Create "pypi-publishing" environment
   - Configure environment protection rules
   - Require manual approval for production publishing

### Secret Management
- **No hardcoded secrets**: All authentication via OIDC
- **Environment isolation**: Use GitHub environments for protection
- **Audit trail**: All publishing actions are logged and traceable

## Troubleshooting

### Common Issues

#### Authentication Failures
```
Error: OIDC token request failed
```
**Solution**: Verify OIDC configuration on PyPI and GitHub repository settings

#### Quality Gate Failures
```
Error: Tests failed or coverage below threshold
```
**Solution**: Run quality checks locally before publishing:
```bash
./scripts/run_tests.sh
uv run pytest --cov=mypylogger --cov-fail-under=95
```

#### Version Conflicts
```
Error: Version already exists on PyPI
```
**Solution**: Use a new version number or delete the existing version on PyPI

#### Package Building Failures
```
Error: Package build failed
```
**Solution**: Verify `pyproject.toml` configuration and build dependencies

### Local Testing

#### Test Package Building
```bash
# Install build tools
uv add --dev build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
uv run python -m build --sdist --wheel --outdir dist/

# Verify package
uv run twine check dist/*

# Test installation
pip install dist/*.whl
```

#### Test Quality Gates
```bash
# Run complete quality suite
./scripts/run_tests.sh

# Individual checks
uv run pytest --cov=mypylogger --cov-fail-under=95
uv run ruff check .
uv run ruff format --check .
uv run mypy src/
```

## Post-Publishing Checklist

After successful publishing:

1. **Verify on PyPI**
   - Check package appears: https://pypi.org/project/mypylogger/
   - Verify version and metadata are correct

2. **Test Installation**
   ```bash
   pip install mypylogger==X.Y.Z
   python -c "import mypylogger; print('Success')"
   ```

3. **Create GitHub Release**
   - Tag the commit with version number
   - Create release notes
   - Link to PyPI package

4. **Update Documentation**
   - Update README with new version
   - Update installation instructions
   - Update changelog

5. **Announce Release**
   - Notify users of new version
   - Highlight new features or fixes
   - Provide migration guidance if needed

## Monitoring and Maintenance

### Package Statistics
- **PyPI Stats**: https://pypistats.org/packages/mypylogger
- **Download Metrics**: Monitor adoption and usage patterns
- **Version Distribution**: Track which versions are actively used

### Security Monitoring
- **Dependabot**: Automated dependency updates
- **Security Advisories**: Monitor for reported vulnerabilities
- **Regular Audits**: Periodic security reviews of dependencies

### Workflow Maintenance
- **Regular Testing**: Test publishing workflow with dry runs
- **Dependency Updates**: Keep GitHub Actions and tools updated
- **Performance Monitoring**: Track workflow execution times
- **Error Analysis**: Review failed publishing attempts

## Emergency Procedures

### Yanking a Release
If a published version has critical issues:

1. **Yank on PyPI**:
   - Go to PyPI project page
   - Select problematic version
   - Click "Yank" and provide reason

2. **Publish Fixed Version**:
   - Fix the issue in code
   - Increment version number
   - Publish new version immediately

3. **Communicate**:
   - Notify users of the issue
   - Provide upgrade instructions
   - Document the incident

### Workflow Failures
If publishing workflow fails:

1. **Immediate Actions**:
   - Check workflow logs for specific errors
   - Verify PyPI and GitHub service status
   - Test locally to isolate the issue

2. **Recovery Steps**:
   - Fix identified issues
   - Re-run workflow with same version
   - Consider manual publishing if workflow issues persist

3. **Prevention**:
   - Update workflow based on lessons learned
   - Add additional validation steps
   - Improve error handling and reporting

## References

- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Python Packaging](https://packaging.python.org/en/latest/)
- [Semantic Versioning](https://semver.org/)
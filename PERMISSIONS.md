# File Permissions Documentation

## Security Policy: Principle of Least Privilege

This document defines the required file permissions for the mypylogger project to ensure security best practices.

## Executable Files (755 permissions)

### Shell Scripts
- `scripts/pre-commit-branch-check.sh` - Pre-commit hook for branch protection
- `scripts/run-complete-test-suite.sh` - Test suite runner
- `scripts/security-scan.sh` - Security scanning automation
- `scripts/setup-dev.sh` - Development environment setup
- `scripts/test-runner.sh` - Test execution wrapper
- `verify_pypi_package.sh` - PyPI package verification

**Rationale**: These files need executable permissions as they are designed to be run directly as shell commands.

## Non-Executable Files (644 permissions)

### Python Scripts
- `scripts/generate_changelog.py` - Changelog generation
- `scripts/validate_release.py` - Release validation
- `scripts/version_bump.py` - Version management
- `scripts/verify-badges.py` - Badge verification
- All other `.py` files in scripts/

**Rationale**: Python files should be executed via `python script.py` rather than directly, removing the need for executable permissions and reducing attack surface.

### Configuration and Documentation
- All `.md`, `.txt`, `.yml`, `.yaml`, `.json`, `.toml` files
- Configuration files in `.kiro/`, `.github/`
- Documentation and specification files

**Rationale**: Configuration and documentation files should never be executable.

## Security Benefits

1. **Reduced Attack Surface**: Non-executable Python files cannot be accidentally executed with incorrect interpreters
2. **Clear Intent**: Executable permissions clearly indicate which files are meant to be run directly
3. **Deployment Safety**: Prevents accidental execution of configuration or data files
4. **Audit Trail**: Makes it easy to identify all executable files in the project

## Verification Commands

```bash
# List all executable files
find . -type f -perm +111 -not -path "./.git/*" -not -path "./venv/*"

# Verify Python files are not executable
find . -name "*.py" -perm +111 -not -path "./.git/*" -not -path "./venv/*"
```

## Maintenance

- Review file permissions during security audits
- Ensure new shell scripts get executable permissions
- Ensure new Python scripts do NOT get executable permissions
- Document any exceptions to these rules with security justification

---

**Last Updated**: Current session
**Next Review**: During next security audit
**Maintainer**: Project security team

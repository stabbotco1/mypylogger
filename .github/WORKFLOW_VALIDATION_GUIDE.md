# Workflow Validation System Guide

This guide provides comprehensive information about the workflow validation system implemented to prevent deployment of invalid GitHub Actions configurations.

## Overview

The workflow validation system provides multiple layers of protection to ensure that only valid, secure, and well-tested workflow configurations are deployed to the repository. It includes:

- **Pre-commit validation** - Prevents committing invalid workflows
- **CI/CD validation** - Comprehensive validation in pull requests
- **Change impact analysis** - Assesses the impact of workflow changes
- **Approval process** - Requires appropriate approvals based on risk level
- **Rollback capabilities** - Provides quick recovery from issues

## System Components

### 1. Pre-commit Hook

**File:** `.github/hooks/pre-commit-workflow-validation`

The pre-commit hook validates workflow files before they are committed to prevent invalid configurations from entering the repository.

**Features:**
- YAML syntax validation
- Basic workflow structure validation
- Security pattern detection
- Automatic installation via setup script

**Installation:**
```bash
# Run the setup script to install all components
./.github/scripts/setup-workflow-validation.sh

# Or manually install just the pre-commit hook
cp .github/hooks/pre-commit-workflow-validation .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Bypassing (Not Recommended):**
```bash
# Only use in emergency situations
git commit --no-verify
```

### 2. Validation Scripts

#### Workflow Validator (`workflow-validator.py`)

Comprehensive validation tool that checks:
- YAML syntax and structure
- Required workflow fields
- Job dependencies and circular references
- Action version compatibility
- Security patterns

**Usage:**
```bash
# Validate all workflows
python .github/scripts/workflow-validator.py --validate-all

# Validate specific workflow
python .github/scripts/workflow-validator.py --file quality-gate.yml

# Analyze changes against main branch
python .github/scripts/workflow-validator.py --analyze-changes

# Test workflow in isolation
python .github/scripts/workflow-validator.py --test-isolation quality-gate.yml
```

#### Workflow Linter (`workflow-linter.py`)

Advanced linting tool with comprehensive rule checking:
- Security rules (hardcoded secrets, permissions)
- Performance rules (caching, timeouts, parallelization)
- Best practices (naming, documentation, error handling)
- Maintainability rules (complexity, duplication)

**Usage:**
```bash
# Lint all workflows
python .github/scripts/workflow-linter.py .github/workflows

# Lint specific workflow
python .github/scripts/workflow-linter.py --file quality-gate.yml

# Filter by severity
python .github/scripts/workflow-linter.py --severity error

# JSON output
python .github/scripts/workflow-linter.py --output json
```

#### Impact Analyzer (`workflow-impact-analyzer.py`)

Analyzes the impact of workflow changes:
- Risk assessment (low, medium, high)
- Impact categories (security, performance, reliability)
- Change recommendations
- Testing strategy suggestions
- Rollback planning

**Usage:**
```bash
# Analyze changes against main
python .github/scripts/workflow-impact-analyzer.py

# Specify base and target references
python .github/scripts/workflow-impact-analyzer.py --base origin/main --target HEAD

# Generate report file
python .github/scripts/workflow-impact-analyzer.py --report-file impact-report.txt
```

#### Workflow Tester (`workflow-tester.py`)

Comprehensive testing framework:
- Syntax validation
- YAML linting (yamllint)
- Action linting (actionlint)
- Security scanning
- Dry run testing (act)
- Isolated execution testing

**Usage:**
```bash
# Test all workflows
python .github/scripts/workflow-tester.py --all

# Test specific workflow
python .github/scripts/workflow-tester.py --file quality-gate.yml

# Skip specific tests
python .github/scripts/workflow-tester.py --all --skip-tests dry_run isolated_execution
```

### 3. CI/CD Workflows

#### Workflow Validation (`workflow-validation.yml`)

Comprehensive validation workflow that runs on workflow changes:
- Syntax and structure validation
- Advanced linting and best practices
- Security validation
- Change impact analysis
- Isolated testing (comprehensive mode)

**Triggers:**
- Pull requests affecting `.github/workflows/`
- Push to main branch
- Manual dispatch with validation level selection

#### Workflow Change Approval (`workflow-change-approval.yml`)

Approval process workflow that enforces approval requirements:
- Change assessment and risk analysis
- Validation gate enforcement
- Approval status tracking
- Automated approval for low-risk changes
- Manual approval requirements for medium/high-risk changes

**Approval Requirements:**
- **Low Risk:** Auto-approved (≤3 files, low impact score)
- **Medium Risk:** 1 admin approval required
- **High Risk:** 2 admin approvals required
- **Security Impact:** Elevated approval required

### 4. Rollback System

#### Rollback Manager (`workflow-rollback.py`)

Automated rollback capabilities for quick recovery:
- Backup creation and management
- Rollback to previous backup
- Rollback to specific git commit
- Dry-run simulation
- Automatic cleanup of old backups

**Usage:**
```bash
# Create backup
python .github/scripts/workflow-rollback.py backup --name "pre-deployment"

# List available backups
python .github/scripts/workflow-rollback.py list

# Rollback to backup (dry run)
python .github/scripts/workflow-rollback.py rollback --backup backup_20241024_143022 --dry-run

# Rollback to backup (actual)
python .github/scripts/workflow-rollback.py rollback --backup backup_20241024_143022

# Rollback to git commit
python .github/scripts/workflow-rollback.py rollback --commit abc123def

# Clean up old backups
python .github/scripts/workflow-rollback.py cleanup --keep-count 10 --keep-days 30
```

## Configuration

### Validation Configuration

**File:** `.github/workflow-validation.yml`

```yaml
validation:
  default_level: standard  # basic, standard, comprehensive
  
  checks:
    syntax: true
    linting: true
    security: true
    performance: true
    best_practices: true
  
  pre_commit:
    enabled: true
    fail_on_warnings: false
  
  ci_integration:
    enabled: true
    block_on_failure: true
    comment_on_pr: true

rollback:
  auto_rollback: false
  backup_workflows: true
  timeout: 30

notifications:
  on_failure: true
  on_high_impact: true
```

### Tool Dependencies

#### Required Tools
- **Python 3.8+** - Core validation scripts
- **PyYAML** - YAML parsing and validation
- **Git** - Version control operations

#### Optional Tools (Enhanced Features)
- **yamllint** - YAML style linting
  ```bash
  pip install yamllint
  ```

- **actionlint** - GitHub Actions specific linting
  ```bash
  # Install from GitHub releases
  curl -s https://api.github.com/repos/rhysd/actionlint/releases/latest | \
    jq -r '.assets[] | select(.name | contains("linux_amd64")) | .browser_download_url' | \
    head -1 | xargs curl -L -o actionlint.tar.gz
  tar -xzf actionlint.tar.gz
  sudo mv actionlint /usr/local/bin/
  ```

- **act** - Local GitHub Actions runner
  ```bash
  # Install from GitHub releases
  curl -s https://api.github.com/repos/nektos/act/releases/latest | \
    jq -r '.assets[] | select(.name | contains("Linux_x86_64")) | .browser_download_url' | \
    head -1 | xargs curl -L -o act.tar.gz
  tar -xzf act.tar.gz
  sudo mv act /usr/local/bin/
  ```

## Workflow Change Process

### 1. Development Phase

1. **Make workflow changes** in your feature branch
2. **Pre-commit validation** runs automatically when committing
3. **Fix any validation errors** before the commit succeeds

### 2. Pull Request Phase

1. **Create pull request** with workflow changes
2. **Workflow validation** runs automatically
3. **Change impact analysis** assesses risk level
4. **Approval process** determines requirements based on risk

### 3. Approval Requirements

#### Automatic Approval (Low Risk)
- ≤3 workflow files changed
- Low impact score (<0.4)
- No security-sensitive changes
- All validations pass

#### Standard Approval (Medium Risk)
- Medium impact score (0.4-0.8)
- Multiple workflow files changed
- Performance or reliability impact
- **Requires:** 1 admin approval

#### Elevated Approval (High Risk)
- High impact score (≥0.8)
- Security-sensitive changes
- Critical workflow modifications
- **Requires:** 2 admin approvals

### 4. Deployment Phase

1. **Merge approved PR** to main branch
2. **Automatic backup** created before deployment
3. **Monitoring** for workflow execution issues
4. **Rollback available** if problems detected

## Troubleshooting

### Common Validation Errors

#### YAML Syntax Errors
```
Error: YAML syntax error: mapping values are not allowed here
```
**Solution:** Check YAML indentation and structure

#### Missing Required Fields
```
Error: Missing required field: runs-on
```
**Solution:** Add required fields to job definitions

#### Circular Dependencies
```
Error: Circular job dependencies detected
```
**Solution:** Review and fix job `needs` relationships

#### Security Issues
```
Warning: Potential hardcoded secret detected
```
**Solution:** Use GitHub Secrets instead of hardcoded values

### Validation Failures

#### Pre-commit Hook Failures
```bash
# Check what's failing
python .github/scripts/workflow-validator.py --file your-workflow.yml

# Fix issues and try again
git add .github/workflows/your-workflow.yml
git commit -m "Fix workflow validation issues"
```

#### CI/CD Validation Failures
1. Check the workflow run logs for specific errors
2. Run validation locally to debug issues
3. Fix problems and push corrected changes
4. Validation will re-run automatically

### Approval Issues

#### Insufficient Approvals
- Ensure you have the required number of approvals
- Check that approvers have admin permissions
- High-risk changes need 2 admin approvals

#### Validation Blocking Approval
- All validations must pass before approval
- Fix validation errors first
- Approval process will resume after fixes

### Rollback Scenarios

#### Immediate Issues After Deployment
```bash
# Quick rollback to last known good state
python .github/scripts/workflow-rollback.py rollback --backup latest

# Or rollback to specific commit
python .github/scripts/workflow-rollback.py rollback --commit abc123def
```

#### Workflow Execution Failures
1. Check workflow run logs for errors
2. Identify if issue is due to recent changes
3. Use rollback system to restore previous version
4. Investigate and fix issues in separate branch

## Best Practices

### Workflow Development

1. **Start with validation** - Run local validation before committing
2. **Small changes** - Make incremental changes for easier review
3. **Test locally** - Use `act` to test workflows locally when possible
4. **Document changes** - Add comments explaining complex logic
5. **Security first** - Never hardcode secrets or use overly broad permissions

### Change Management

1. **Create backups** before major changes
2. **Use feature branches** for workflow modifications
3. **Test thoroughly** in development environment
4. **Monitor after deployment** for any issues
5. **Have rollback plan** ready for critical changes

### Security Considerations

1. **Minimal permissions** - Use least privilege principle
2. **Pin action versions** - Avoid using `@main` or `@latest`
3. **Validate inputs** - Sanitize any user inputs
4. **Review dependencies** - Audit third-party actions
5. **Monitor for secrets** - Use secret scanning tools

## Emergency Procedures

### Bypassing Validation (Emergency Only)

```bash
# Bypass pre-commit hook (use sparingly)
git commit --no-verify -m "Emergency fix"

# Emergency approval override (admin only)
# Use workflow_dispatch with emergency approval level
```

### Emergency Rollback

```bash
# Immediate rollback to last backup
python .github/scripts/workflow-rollback.py rollback --backup latest

# Emergency rollback to specific commit
git checkout HEAD~1 -- .github/workflows/
git commit -m "Emergency rollback of workflow changes"
git push origin main
```

### Recovery Procedures

1. **Identify the issue** - Check workflow logs and error messages
2. **Assess impact** - Determine scope of affected workflows
3. **Execute rollback** - Use appropriate rollback method
4. **Verify recovery** - Test that workflows are functioning
5. **Post-incident review** - Analyze what went wrong and improve

## Support and Resources

### Getting Help

1. **Check this guide** for common issues and solutions
2. **Review workflow logs** for specific error messages
3. **Run local validation** to debug issues
4. **Contact repository maintainers** for complex issues

### Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [YAML Specification](https://yaml.org/spec/)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Security Hardening Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

### Tool Documentation

- [yamllint Documentation](https://yamllint.readthedocs.io/)
- [actionlint Documentation](https://github.com/rhysd/actionlint)
- [act Documentation](https://github.com/nektos/act)

---

*This guide is maintained as part of the workflow validation system. Please keep it updated as the system evolves.*
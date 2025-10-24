# Branch Protection Setup Guide

This directory contains the complete branch protection configuration for mypylogger v0.2.0, implementing automated quality gates and security requirements.

## Overview

Branch protection rules ensure that only quality-verified code can be merged to the main branch by enforcing:

- **Quality Gates**: All tests and code quality checks must pass
- **Security Scanning**: Zero-tolerance policy for security vulnerabilities  
- **Code Reviews**: Human approval required for all changes
- **Branch Currency**: Branches must be up-to-date before merging
- **Linear History**: Clean commit history maintenance

## Files in this Configuration

### Documentation
- **`BRANCH_PROTECTION.md`** - Complete configuration guide and reference
- **`README-BRANCH-PROTECTION.md`** - This setup guide

### Configuration Files
- **`branch-protection-config.json`** - JSON configuration for GitHub API
- **`scripts/setup-branch-protection.sh`** - Automated setup script
- **`scripts/validate-branch-protection.sh`** - Validation and testing script

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./.github/scripts/setup-branch-protection.sh --setup

# Validate the configuration
./.github/scripts/validate-branch-protection.sh --full
```

### Option 2: Manual Configuration

1. Go to repository **Settings** → **Branches**
2. Click **Add rule** for branch `main`
3. Follow the detailed configuration in `BRANCH_PROTECTION.md`

### Option 3: GitHub CLI

```bash
# Use the provided configuration
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --input .github/branch-protection-config.json
```

## Requirements Addressed

This configuration implements the following requirements from Phase 3:

| Requirement | Description | Implementation |
|-------------|-------------|----------------|
| **3.1** | Prevent direct pushes to main branch | Branch protection rule blocks direct pushes |
| **3.2** | Require all quality checks to pass | 12 required status checks configured |
| **3.3** | Require pull request reviews (≥1 approval) | Required approving review count: 1 |
| **3.4** | Require branches to be up-to-date | Strict status checks enabled |
| **3.5** | Enforce status checks for quality gates | All workflow jobs as required contexts |

## Required Status Checks

The following status checks must pass before merging:

### Quality Gate Workflow (`quality-gate.yml`)
- ✅ Tests (Python 3.8)
- ✅ Tests (Python 3.9)  
- ✅ Tests (Python 3.10)
- ✅ Tests (Python 3.11)
- ✅ Tests (Python 3.12)
- ✅ Code Quality Checks
- ✅ Quality Gate Summary & Performance Report

### Security Scanning Workflow (`security-scan.yml`)
- ✅ Dependency Security Scan
- ✅ CodeQL Security Analysis
- ✅ Secret Scanning Validation
- ✅ Security Configuration Validation
- ✅ Security Summary & Zero-Tolerance Policy

## Validation Checklist

After setup, verify these protections are active:

- [ ] Direct push to main branch is blocked
- [ ] Pull requests require 1 approval minimum
- [ ] All 12 status checks are required
- [ ] Branches must be up-to-date before merge
- [ ] Stale reviews are dismissed on new commits
- [ ] Conversation resolution is required
- [ ] Linear history is enforced
- [ ] Force pushes are blocked
- [ ] Branch deletion is blocked
- [ ] Admin enforcement is enabled

## Testing the Configuration

### Automated Validation

```bash
# Run comprehensive validation
./.github/scripts/validate-branch-protection.sh --full

# Quick check
./.github/scripts/validate-branch-protection.sh --quick

# Generate detailed report
./.github/scripts/validate-branch-protection.sh --report
```

### Manual Testing

1. **Test Direct Push Prevention**:
   ```bash
   git checkout main
   echo "test" >> README.md
   git add README.md
   git commit -m "test: direct push"
   git push origin main  # Should fail
   ```

2. **Test Pull Request Workflow**:
   - Create feature branch
   - Make changes and push
   - Open pull request
   - Verify all status checks appear
   - Verify approval is required
   - Verify merge is blocked until checks pass

3. **Test Status Check Enforcement**:
   - Create PR with failing tests
   - Verify merge is blocked
   - Fix tests
   - Verify merge becomes available

## Troubleshooting

### Common Issues

**Status checks not appearing:**
- Verify workflow files exist and are valid
- Check that workflows trigger on pull requests
- Ensure workflows have run at least once

**Merge allowed despite failing checks:**
- Verify all required contexts are configured
- Check "Include administrators" is enabled
- Ensure status check names match exactly

**Cannot configure protection rules:**
- Verify admin access to repository
- Check GitHub CLI authentication
- Ensure repository exists and is accessible

### Getting Help

1. **Check Configuration**: Review `BRANCH_PROTECTION.md` for detailed settings
2. **Run Validation**: Use validation script to identify issues
3. **Check Logs**: Review workflow logs for status check failures
4. **GitHub Docs**: [Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

## Maintenance

### Adding New Status Checks

When adding new workflow jobs that should block merges:

1. Update `branch-protection-config.json`
2. Run setup script to apply changes
3. Update documentation
4. Test with a pull request

### Removing Status Checks

When removing workflow jobs:

1. Remove from configuration files
2. Apply updated configuration
3. Update documentation
4. Verify existing PRs are not affected

### Regular Validation

Run validation monthly or after workflow changes:

```bash
# Schedule in cron or CI/CD
./.github/scripts/validate-branch-protection.sh --report
```

## Security Considerations

- **Zero-tolerance policy**: All security scans must pass
- **Admin enforcement**: Even administrators must follow rules
- **Review requirement**: Human oversight for all changes
- **Up-to-date branches**: Prevents integration conflicts
- **Linear history**: Maintains audit trail

## Integration with CI/CD

This branch protection configuration integrates with:

- **Quality Gate Workflow**: Enforces code quality standards
- **Security Scanning**: Implements zero-tolerance security policy
- **Publishing Workflow**: Ensures only quality code is released
- **Dependabot**: Automated dependency updates with protection

## Performance Impact

- **Parallel execution**: Status checks run concurrently
- **Caching**: Dependencies cached for faster execution
- **Fail-fast**: Critical issues stop execution early
- **Timeout limits**: Prevents runaway processes

Expected execution time: **< 5 minutes** for typical changes

## Compliance and Auditing

This configuration supports:

- **SOC 2 Type II**: Automated controls and audit trails
- **ISO 27001**: Security management requirements
- **NIST Framework**: Cybersecurity best practices
- **Internal Audits**: Complete change tracking and approval

## Next Steps

After implementing branch protection:

1. **Train Team**: Educate developers on new workflow
2. **Monitor Performance**: Track workflow execution times
3. **Gather Feedback**: Collect developer experience feedback
4. **Iterate**: Refine configuration based on usage patterns

For questions or issues, refer to the detailed documentation in `BRANCH_PROTECTION.md` or contact the development team.
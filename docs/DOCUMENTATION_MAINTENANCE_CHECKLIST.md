# Documentation Maintenance Checklist

## Overview

This checklist ensures documentation accuracy and consistency before merging pre-release to main. It helps maintain professional documentation standards and prevents outdated information from reaching production.

## Pre-Release to Main Merge Checklist

### Automated Validation
- [ ] **Run date validation**: `make validate-docs-dates`
- [ ] **Run badge validation**: `make verify-badges`
- [ ] **Check CI/CD status**: All documentation validation workflows pass

### Manual Review

#### Date Accuracy
- [ ] **Security scan dates**: Verify VULNERABILITIES.md and security documents reflect actual scan dates
- [ ] **Last updated dates**: Check all "Last Updated" fields are current
- [ ] **Example timestamps**: Ensure example dates are reasonable (not too old)
- [ ] **Expiration dates**: Verify safety policy and other expiration dates are appropriate

#### Content Accuracy
- [ ] **Version numbers**: Check all version references match current release
- [ ] **Badge status**: Verify all badges display correct information
- [ ] **Links**: Test that all documentation links work correctly
- [ ] **Examples**: Ensure all code examples are current and functional

#### Consistency
- [ ] **Date formats**: Consistent ISO 8601 format usage
- [ ] **Terminology**: Consistent use of project terminology
- [ ] **Styling**: Consistent markdown formatting
- [ ] **Structure**: Logical organization and navigation

### Specific Files to Review

#### Core Documentation
- [ ] **README.md**: Project overview, badges, examples
- [ ] **SECURITY.md**: Security policy and contact information
- [ ] **VULNERABILITIES.md**: Current vulnerability status
- [ ] **CONTRIBUTING.md**: Contribution guidelines and processes
- [ ] **USAGE.md**: Usage examples and tutorials

#### Technical Documentation
- [ ] **API Documentation**: Current and complete
- [ ] **Performance Documentation**: Current benchmark results
- [ ] **Configuration Documentation**: Up-to-date settings and options
- [ ] **Troubleshooting Guides**: Current and helpful

#### Project Management
- [ ] **Spec Documents**: Requirements, design, and tasks are current
- [ ] **Steering Documents**: Development standards and patterns
- [ ] **Workflow Documentation**: CI/CD and development processes

## Automated Tools

### Date Validation Script
```bash
# Check for outdated dates
make validate-docs-dates

# Detailed report with all dates
make validate-docs-dates-verbose

# Fail CI/CD on outdated dates
python scripts/validate_documentation_dates.py --fail-on-outdated
```

### Badge Validation
```bash
# Verify badge functionality
make verify-badges

# Detailed badge health check
make badge-health-check
```

### Documentation Completeness
```bash
# Check documentation structure
make docs-check
```

## Common Issues and Solutions

### Outdated Dates
**Issue**: Documentation contains dates from previous years
**Solution**:
1. Run `make validate-docs-dates` to identify issues
2. Update dates to reflect current status
3. For examples, use recent but not necessarily current dates

### Incorrect Badge Status
**Issue**: Badges show outdated or incorrect information
**Solution**:
1. Run `make verify-badges` to check badge health
2. Update badge URLs or configuration as needed
3. Verify badge automation is working correctly

### Broken Links
**Issue**: Documentation links return 404 or other errors
**Solution**:
1. Test all external links manually
2. Update or remove broken links
3. Consider using archived versions for historical references

### Version Mismatches
**Issue**: Documentation references old version numbers
**Solution**:
1. Search for version patterns: `grep -r "0\.[0-9]\.[0-9]" docs/`
2. Update to current version numbers
3. Ensure consistency across all files

## Maintenance Schedule

### Before Each Release
- [ ] Complete full checklist
- [ ] Run all automated validation tools
- [ ] Manual review of critical documentation

### Monthly
- [ ] Review and update security documentation
- [ ] Check for new broken links
- [ ] Update performance benchmarks if needed

### Quarterly
- [ ] Comprehensive documentation audit
- [ ] Review and update maintenance procedures
- [ ] Evaluate documentation effectiveness

## Quality Standards

### Date Accuracy
- **Current Status**: All status dates within 30 days of actual status
- **Examples**: Example dates within 1 year of current date
- **Expiration**: Expiration dates set appropriately in the future

### Content Quality
- **Accuracy**: All information is correct and current
- **Completeness**: All necessary information is included
- **Clarity**: Information is clear and easy to understand
- **Consistency**: Consistent formatting and terminology

### Professional Standards
- **No Placeholders**: No "TODO" or placeholder content in main branch
- **Proper Attribution**: Correct author and copyright information
- **Legal Compliance**: All legal requirements met (licenses, etc.)
- **Accessibility**: Documentation is accessible to all users

## Troubleshooting

### Date Validation Failures
If the date validation script reports issues:

1. **Review Context**: Check if dates are in acceptable contexts (tests, examples)
2. **Update Outdated**: Update genuinely outdated dates
3. **Exclude if Appropriate**: Add patterns to script exclusions if needed
4. **Document Decisions**: Note why certain dates are kept if unusual

### Badge Validation Failures
If badge validation fails:

1. **Check Service Status**: Verify badge services (Shields.io, etc.) are operational
2. **Update URLs**: Fix any broken badge URLs
3. **Test Manually**: Open badge URLs in browser to verify
4. **Update Automation**: Fix any badge update automation issues

### CI/CD Integration Issues
If documentation validation fails in CI/CD:

1. **Check Logs**: Review GitHub Actions logs for specific errors
2. **Test Locally**: Run validation scripts locally to reproduce issues
3. **Update Workflow**: Fix any workflow configuration issues
4. **Temporary Bypass**: Use workflow dispatch for urgent fixes if needed

## Integration with Development Workflow

### Pre-Commit Hooks
Consider adding documentation validation to pre-commit hooks:
```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-docs-dates
      name: Validate documentation dates
      entry: python scripts/validate_documentation_dates.py --fail-on-outdated
      language: system
      files: \.(md|txt|yml|yaml)$
```

### IDE Integration
Set up IDE tasks for quick validation:
- VS Code: Add tasks to `.vscode/tasks.json`
- PyCharm: Add external tools for validation scripts
- Command line: Use Makefile targets for consistent commands

This checklist ensures documentation maintains professional standards and accuracy throughout the development lifecycle.

# Branch Protection Configuration

This document specifies the branch protection rules that must be configured for the mypylogger v0.2.0 repository to enforce quality gates and security requirements.

## Overview

Branch protection rules ensure that only quality-verified code can be merged to the main branch by enforcing automated checks and review requirements before allowing pull request merges.

## Requirements Addressed

- **3.1**: Prevent direct pushes to the main branch
- **3.2**: Require all quality checks to pass before allowing pull request merges  
- **3.3**: Require at least one approving review for pull request merges
- **3.4**: Require branches to be up-to-date before merging
- **3.5**: Enforce status checks for all defined quality gates

## Branch Protection Rules Configuration

### Main Branch Protection

The following settings must be configured for the `main` branch:

#### General Protection Settings

```yaml
branch: main
enforce_admins: true
allow_deletions: false
allow_force_pushes: false
required_linear_history: true
```

#### Required Status Checks

**Strict Status Checks**: `true` (branches must be up to date before merging)

**Required Status Check Contexts**:
```yaml
required_status_checks:
  strict: true
  contexts:
    # Quality Gate Workflow - Test Matrix Jobs
    - "Tests (Python 3.8)"
    - "Tests (Python 3.9)"
    - "Tests (Python 3.10)"
    - "Tests (Python 3.11)"
    - "Tests (Python 3.12)"
    
    # Quality Gate Workflow - Code Quality
    - "Code Quality Checks"
    
    # Quality Gate Workflow - Summary
    - "Quality Gate Summary & Performance Report"
    
    # Security Scanning Workflow
    - "Dependency Security Scan"
    - "CodeQL Security Analysis"
    - "Secret Scanning Validation"
    - "Security Configuration Validation"
    - "Security Summary & Zero-Tolerance Policy"
```

#### Pull Request Reviews

```yaml
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: false
  require_last_push_approval: true
  bypass_pull_request_allowances:
    users: []
    teams: []
    apps: []
```

#### Restrictions

```yaml
restrictions:
  # No push restrictions - rely on required status checks
  users: []
  teams: []
  apps: []
```

## Configuration Methods

### Method 1: GitHub Web Interface

1. Navigate to repository **Settings** → **Branches**
2. Click **Add rule** for branch name pattern `main`
3. Configure the following settings:

**Branch Protection Rule Settings:**
- ✅ Restrict pushes that create files larger than 100 MB
- ✅ Require a pull request before merging
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from code owners: **No** (not configured yet)
  - ✅ Require approval of the most recent reviewable push
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - **Required status checks** (select all from list above)
- ✅ Require conversation resolution before merging
- ✅ Require linear history
- ✅ Include administrators
- ❌ Allow force pushes: **Disabled**
- ❌ Allow deletions: **Disabled**

### Method 2: GitHub CLI

```bash
# Install GitHub CLI if not available
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Authenticate with GitHub
gh auth login

# Create branch protection rule
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Tests (Python 3.8)","Tests (Python 3.9)","Tests (Python 3.10)","Tests (Python 3.11)","Tests (Python 3.12)","Code Quality Checks","Quality Gate Summary & Performance Report","Dependency Security Scan","CodeQL Security Analysis","Secret Scanning Validation","Security Configuration Validation","Security Summary & Zero-Tolerance Policy"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false,"require_last_push_approval":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_linear_history=true
```

### Method 3: Terraform Configuration

```hcl
resource "github_branch_protection" "main" {
  repository_id = var.repository_name
  pattern       = "main"

  enforce_admins         = true
  allows_deletions       = false
  allows_force_pushes    = false
  require_signed_commits = false
  required_linear_history = true

  required_status_checks {
    strict = true
    contexts = [
      "Tests (Python 3.8)",
      "Tests (Python 3.9)",
      "Tests (Python 3.10)",
      "Tests (Python 3.11)",
      "Tests (Python 3.12)",
      "Code Quality Checks",
      "Quality Gate Summary & Performance Report",
      "Dependency Security Scan",
      "CodeQL Security Analysis",
      "Secret Scanning Validation",
      "Security Configuration Validation",
      "Security Summary & Zero-Tolerance Policy"
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews          = true
    require_code_owner_reviews     = false
    require_last_push_approval     = true
  }
}
```

## Status Check Names Reference

The following table maps workflow jobs to their status check names:

| Workflow File | Job Name | Status Check Context |
|---------------|----------|---------------------|
| `quality-gate.yml` | `test-matrix` | `Tests (Python X.Y)` |
| `quality-gate.yml` | `quality-checks` | `Code Quality Checks` |
| `quality-gate.yml` | `quality-gate-summary` | `Quality Gate Summary & Performance Report` |
| `security-scan.yml` | `dependency-security-scan` | `Dependency Security Scan` |
| `security-scan.yml` | `codeql-security-analysis` | `CodeQL Security Analysis` |
| `security-scan.yml` | `secret-scanning-validation` | `Secret Scanning Validation` |
| `security-scan.yml` | `security-config-validation` | `Security Configuration Validation` |
| `security-scan.yml` | `security-summary` | `Security Summary & Zero-Tolerance Policy` |

## Validation

After configuring branch protection rules, validate the setup:

### 1. Test Direct Push Prevention

```bash
# This should fail with branch protection error
git checkout main
echo "test" >> README.md
git add README.md
git commit -m "test: direct push to main"
git push origin main
# Expected: Error about branch protection rules
```

### 2. Test Pull Request Requirements

1. Create a feature branch and make changes
2. Open a pull request to main
3. Verify all required status checks appear
4. Verify approval requirement is enforced
5. Verify merge is blocked until all checks pass

### 3. Test Status Check Enforcement

1. Create a pull request with failing tests
2. Verify merge is blocked
3. Fix the tests
4. Verify merge becomes available after checks pass

## Troubleshooting

### Common Issues

**Status checks not appearing:**
- Verify workflow names match exactly
- Check that workflows are triggered on pull requests
- Ensure workflows have run at least once

**Merge still allowed despite failing checks:**
- Verify "Require status checks to pass before merging" is enabled
- Check that all required contexts are listed
- Ensure "Include administrators" is enabled

**Cannot push to main despite being admin:**
- This is expected behavior when "Include administrators" is enabled
- Use pull requests even as an administrator

## Security Considerations

- **Zero-tolerance policy**: All security scans must pass
- **Quality gates**: All code quality checks must pass
- **Review requirement**: Human review required for all changes
- **Up-to-date requirement**: Branches must be current before merge
- **Linear history**: Maintains clean commit history

## Maintenance

### Adding New Status Checks

When adding new workflow jobs that should block merges:

1. Update the required status checks list in branch protection
2. Test the new check with a pull request
3. Update this documentation

### Removing Status Checks

When removing workflow jobs:

1. Remove from required status checks list
2. Update this documentation
3. Verify existing pull requests are not blocked

## Implementation Checklist

- [ ] Configure branch protection rules using preferred method
- [ ] Test direct push prevention
- [ ] Test pull request review requirements
- [ ] Test status check enforcement
- [ ] Verify all workflow status checks are required
- [ ] Document any custom configurations
- [ ] Train team members on new workflow

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [GitHub CLI Branch Protection](https://cli.github.com/manual/gh_api)
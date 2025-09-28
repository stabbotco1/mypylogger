# GitHub Branch Protection Setup

This document provides step-by-step instructions for configuring branch protection rules on GitHub to enforce the GitFlow workflow and quality standards.

## Required Branch Protection Rules

### Main Branch Protection

Navigate to: **Settings → Branches → Add rule**

**Branch name pattern:** `main`

**Protection Settings:**
- [x] **Restrict pushes that create files larger than 100MB**
- [x] **Require a pull request before merging**
  - [x] **Require approvals:** 1
  - [x] **Dismiss stale pull request approvals when new commits are pushed**
  - [x] **Require review from code owners** (when CODEOWNERS file exists)
- [x] **Require status checks to pass before merging**
  - [x] **Require branches to be up to date before merging**
  - **Required status checks:** (Add these when CI/CD is set up)
    - `CI / quality-gates`
    - `CI / security-scan` 
    - `CI / test-matrix`
- [x] **Require conversation resolution before merging**
- [x] **Require signed commits** (optional but recommended)
- [x] **Include administrators**
- [x] **Restrict pushes**
- [x] **Allow force pushes: Everyone** (unchecked - no force pushes)
- [x] **Allow deletions** (unchecked - prevent branch deletion)

### Pre-release Branch Protection

**Branch name pattern:** `pre-release`

**Protection Settings:**
- [x] **Restrict pushes that create files larger than 100MB**
- [x] **Require a pull request before merging**
  - [x] **Require approvals:** 1
  - [x] **Dismiss stale pull request approvals when new commits are pushed**
- [x] **Require status checks to pass before merging**
  - [x] **Require branches to be up to date before merging**
  - **Required status checks:** (Add these when CI/CD is set up)
    - `CI / quality-gates`
    - `CI / security-scan`
- [x] **Require conversation resolution before merging**
- [x] **Include administrators**
- [ ] **Restrict pushes** (allow direct pushes for hotfixes)
- [x] **Allow force pushes: Everyone** (unchecked)
- [x] **Allow deletions** (unchecked)

## Workflow Enforcement

### Merge Requirements
Both protected branches require:
1. **Pull Request Review:** At least 1 approving review
2. **Status Checks:** All CI/CD checks must pass
3. **Up-to-date Branch:** Must be current with target branch
4. **Conversation Resolution:** All review comments resolved

### Branch Naming Conventions
Enforce these patterns through team guidelines:
- `feature/descriptive-name` - New features
- `bugfix/issue-description` - Bug fixes  
- `hotfix/critical-issue` - Emergency fixes
- `docs/update-description` - Documentation updates

## Additional Repository Settings

### General Settings
Navigate to: **Settings → General**

- **Default branch:** `main`
- **Template repository:** Unchecked
- **Issues:** Enabled
- **Wiki:** Disabled (use README and docs/)
- **Discussions:** Enabled (optional)
- **Projects:** Enabled

### Merge Button Settings
Navigate to: **Settings → General → Pull Requests**

- [x] **Allow merge commits**
- [x] **Allow squash merging** (recommended default)
- [ ] **Allow rebase merging**
- [x] **Always suggest updating pull request branches**
- [x] **Allow auto-merge**
- [x] **Automatically delete head branches**

### Security Settings
Navigate to: **Settings → Security & analysis**

- [x] **Dependency graph**
- [x] **Dependabot alerts**
- [x] **Dependabot security updates**
- [x] **Code scanning alerts**
- [x] **Secret scanning alerts**

## Webhooks and Integrations

### Required Integrations (when available)
- **Codecov:** Test coverage reporting
- **Snyk:** Security vulnerability scanning
- **GitHub Actions:** CI/CD automation

### Notification Settings
Configure notifications for:
- Pull request reviews
- Status check failures
- Security alerts
- Dependency updates

## Team Access and Permissions

### Repository Roles
- **Admin:** Repository owner (stabbotco1)
- **Maintain:** Core maintainers (future team members)
- **Write:** Regular contributors
- **Triage:** Issue managers
- **Read:** Public access

### CODEOWNERS File (Future)
Create `.github/CODEOWNERS` when team grows:
```
# Global owners
* @stabbotco1

# Core library code
/mypylogger/ @stabbotco1

# Documentation
/docs/ @stabbotco1
*.md @stabbotco1

# CI/CD and workflows
/.github/ @stabbotco1
```

## Verification Checklist

After setting up branch protection:

- [ ] Cannot push directly to `main` branch
- [ ] Cannot push directly to `pre-release` branch  
- [ ] Pull requests require approval before merge
- [ ] Status checks block merging when failing
- [ ] Force pushes are prevented on protected branches
- [ ] Branch deletion is prevented on protected branches
- [ ] Administrators are included in restrictions

## Troubleshooting

### Common Issues
1. **Status checks not appearing:** Ensure GitHub Actions workflows are committed and have run at least once
2. **Cannot merge despite approvals:** Check that all required status checks are passing
3. **Force push blocked:** This is expected behavior on protected branches
4. **Admin bypass not working:** Verify "Include administrators" is checked

### Testing Branch Protection
1. Create a test feature branch
2. Make a small change and push
3. Create pull request to pre-release
4. Verify all protection rules are enforced
5. Test merge process end-to-end

## Maintenance

### Regular Reviews
- **Monthly:** Review branch protection settings
- **Quarterly:** Update required status checks as CI/CD evolves
- **Per release:** Verify protection rules are working correctly

### Updates
- Add new status checks as CI/CD pipeline expands
- Update approval requirements as team grows
- Adjust settings based on workflow feedback

---

**Note:** These settings should be configured through the GitHub web interface. Some settings may require repository admin permissions.
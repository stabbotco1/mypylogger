#!/bin/bash

# Branch Protection Validation Script for mypylogger v0.2.0
#
# This script validates that branch protection rules are properly configured
# and working as expected for the main branch.
#
# Requirements Validated:
# - 3.1: Direct pushes to main branch are prevented
# - 3.2: All quality checks must pass before merge
# - 3.3: Pull request reviews are required
# - 3.4: Branches must be up-to-date before merge
# - 3.5: Status checks are enforced

set -euo pipefail

# Configuration
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-}"
REPO_NAME="${GITHUB_REPOSITORY_NAME:-mypylogger}"
BRANCH_NAME="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites for validation..."
    
    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        exit 1
    fi
    
    # Check if authenticated with GitHub
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        exit 1
    fi
    
    # Check if jq is available for JSON parsing
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed (required for JSON parsing)"
        exit 1
    fi
    
    # Detect repository information if not provided
    if [[ -z "$REPO_OWNER" ]]; then
        REPO_OWNER=$(git remote get-url origin | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p' || echo "")
        if [[ -z "$REPO_OWNER" ]]; then
            log_error "Could not determine repository owner"
            exit 1
        fi
    fi
    
    log_success "Prerequisites validated"
    log_info "Repository: $REPO_OWNER/$REPO_NAME"
}

# Validate branch protection exists
validate_protection_exists() {
    log_info "Validating branch protection rule exists..."
    
    if gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection" > /dev/null 2>&1; then
        log_success "Branch protection rule exists for '$BRANCH_NAME'"
        return 0
    else
        log_error "Branch protection rule not found for '$BRANCH_NAME'"
        return 1
    fi
}

# Validate required status checks
validate_status_checks() {
    log_info "Validating required status checks configuration..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    # Check if status checks are required
    local status_checks_enabled
    status_checks_enabled=$(echo "$protection_info" | jq -r '.required_status_checks != null')
    
    if [[ "$status_checks_enabled" != "true" ]]; then
        log_error "Required status checks are not enabled"
        return 1
    fi
    
    # Check if strict mode is enabled (branches must be up-to-date)
    local strict_mode
    strict_mode=$(echo "$protection_info" | jq -r '.required_status_checks.strict // false')
    
    if [[ "$strict_mode" != "true" ]]; then
        log_error "Strict status checks not enabled (branches must be up-to-date)"
        return 1
    fi
    
    log_success "Status checks are properly configured with strict mode"
    
    # Validate required status check contexts
    local expected_checks=(
        "Tests (Python 3.8)"
        "Tests (Python 3.9)"
        "Tests (Python 3.10)"
        "Tests (Python 3.11)"
        "Tests (Python 3.12)"
        "Code Quality Checks"
        "Quality Gate Summary & Performance Report"
        "Dependency Security Scan"
        "CodeQL Security Analysis"
        "Secret Scanning Validation"
        "Security Configuration Validation"
        "Security Summary & Zero-Tolerance Policy"
    )
    
    local missing_checks=()
    local configured_checks
    configured_checks=$(echo "$protection_info" | jq -r '.required_status_checks.contexts[]')
    
    for expected_check in "${expected_checks[@]}"; do
        if ! echo "$configured_checks" | grep -Fxq "$expected_check"; then
            missing_checks+=("$expected_check")
        fi
    done
    
    if [[ ${#missing_checks[@]} -gt 0 ]]; then
        log_error "Missing required status checks:"
        for check in "${missing_checks[@]}"; do
            log_error "  - $check"
        done
        return 1
    fi
    
    log_success "All required status checks are configured"
    log_info "Total status checks: $(echo "$configured_checks" | wc -l)"
    
    return 0
}

# Validate pull request review requirements
validate_pr_reviews() {
    log_info "Validating pull request review requirements..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    # Check if PR reviews are required
    local pr_reviews_enabled
    pr_reviews_enabled=$(echo "$protection_info" | jq -r '.required_pull_request_reviews != null')
    
    if [[ "$pr_reviews_enabled" != "true" ]]; then
        log_error "Pull request reviews are not required"
        return 1
    fi
    
    # Check required approving review count
    local required_reviews
    required_reviews=$(echo "$protection_info" | jq -r '.required_pull_request_reviews.required_approving_review_count // 0')
    
    if [[ "$required_reviews" -lt 1 ]]; then
        log_error "Insufficient required approving reviews: $required_reviews (expected: >= 1)"
        return 1
    fi
    
    # Check if stale reviews are dismissed
    local dismiss_stale
    dismiss_stale=$(echo "$protection_info" | jq -r '.required_pull_request_reviews.dismiss_stale_reviews // false')
    
    if [[ "$dismiss_stale" != "true" ]]; then
        log_warning "Stale review dismissal is not enabled"
    fi
    
    log_success "Pull request reviews are properly configured"
    log_info "Required approving reviews: $required_reviews"
    log_info "Dismiss stale reviews: $dismiss_stale"
    
    return 0
}

# Validate admin enforcement
validate_admin_enforcement() {
    log_info "Validating admin enforcement..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    local enforce_admins
    enforce_admins=$(echo "$protection_info" | jq -r '.enforce_admins.enabled // false')
    
    if [[ "$enforce_admins" != "true" ]]; then
        log_error "Admin enforcement is not enabled"
        return 1
    fi
    
    log_success "Admin enforcement is enabled"
    return 0
}

# Validate push and deletion restrictions
validate_push_restrictions() {
    log_info "Validating push and deletion restrictions..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    # Check force push restrictions
    local allow_force_pushes
    allow_force_pushes=$(echo "$protection_info" | jq -r '.allow_force_pushes.enabled // true')
    
    if [[ "$allow_force_pushes" == "true" ]]; then
        log_error "Force pushes are allowed (should be disabled)"
        return 1
    fi
    
    # Check deletion restrictions
    local allow_deletions
    allow_deletions=$(echo "$protection_info" | jq -r '.allow_deletions.enabled // true')
    
    if [[ "$allow_deletions" == "true" ]]; then
        log_error "Branch deletions are allowed (should be disabled)"
        return 1
    fi
    
    log_success "Push and deletion restrictions are properly configured"
    return 0
}

# Validate linear history requirement
validate_linear_history() {
    log_info "Validating linear history requirement..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    local required_linear_history
    required_linear_history=$(echo "$protection_info" | jq -r '.required_linear_history.enabled // false')
    
    if [[ "$required_linear_history" != "true" ]]; then
        log_error "Linear history is not required"
        return 1
    fi
    
    log_success "Linear history requirement is enabled"
    return 0
}

# Test branch protection by attempting operations
test_branch_protection() {
    log_info "Testing branch protection enforcement..."
    
    # Note: These are informational tests that don't actually perform operations
    # Real testing would require creating test branches and PRs
    
    log_info "Branch protection tests that should be performed manually:"
    log_info "1. Attempt direct push to main branch (should fail)"
    log_info "2. Create PR without required status checks (should block merge)"
    log_info "3. Create PR without approval (should block merge)"
    log_info "4. Create PR with outdated branch (should require update)"
    log_info "5. Attempt force push to main branch (should fail)"
    
    log_warning "Automated testing of branch protection requires test PRs"
    log_warning "Manual validation recommended for complete verification"
    
    return 0
}

# Generate validation report
generate_report() {
    log_info "Generating branch protection validation report..."
    
    local protection_info
    protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection")
    
    echo ""
    echo "=========================================="
    echo "Branch Protection Validation Report"
    echo "=========================================="
    echo "Repository: $REPO_OWNER/$REPO_NAME"
    echo "Branch: $BRANCH_NAME"
    echo "Validation Time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    
    echo "Configuration Summary:"
    echo "---------------------"
    echo "Enforce Admins: $(echo "$protection_info" | jq -r '.enforce_admins.enabled // false')"
    echo "Required Reviews: $(echo "$protection_info" | jq -r '.required_pull_request_reviews.required_approving_review_count // 0')"
    echo "Dismiss Stale Reviews: $(echo "$protection_info" | jq -r '.required_pull_request_reviews.dismiss_stale_reviews // false')"
    echo "Strict Status Checks: $(echo "$protection_info" | jq -r '.required_status_checks.strict // false')"
    echo "Status Check Count: $(echo "$protection_info" | jq -r '.required_status_checks.contexts | length')"
    echo "Allow Force Pushes: $(echo "$protection_info" | jq -r '.allow_force_pushes.enabled // true')"
    echo "Allow Deletions: $(echo "$protection_info" | jq -r '.allow_deletions.enabled // true')"
    echo "Required Linear History: $(echo "$protection_info" | jq -r '.required_linear_history.enabled // false')"
    echo ""
    
    echo "Required Status Checks:"
    echo "----------------------"
    echo "$protection_info" | jq -r '.required_status_checks.contexts[]' | while read -r check; do
        echo "  ✓ $check"
    done
    echo ""
    
    echo "Validation Results:"
    echo "------------------"
    # Results will be shown by individual validation functions
}

# Display usage information
show_usage() {
    cat << EOF
Branch Protection Validation Script for mypylogger v0.2.0

Usage: $0 [OPTIONS]

Options:
  --full      Run complete validation (default)
  --quick     Run basic validation only
  --report    Generate detailed report
  --help      Show this help message

Environment Variables:
  GITHUB_REPOSITORY_OWNER    Repository owner (auto-detected if not set)
  GITHUB_REPOSITORY_NAME     Repository name (default: mypylogger)

Prerequisites:
  - GitHub CLI (gh) installed and authenticated
  - jq installed for JSON parsing
  - Access to the repository

Examples:
  $0                         # Run full validation
  $0 --quick                 # Run basic checks only
  $0 --report                # Generate detailed report

EOF
}

# Main execution
main() {
    local validation_type="full"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --full)
                validation_type="full"
                shift
                ;;
            --quick)
                validation_type="quick"
                shift
                ;;
            --report)
                validation_type="report"
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Run validation
    log_info "Starting branch protection validation for mypylogger v0.2.0"
    
    check_prerequisites
    
    local validation_passed=true
    
    # Basic validation
    if ! validate_protection_exists; then
        validation_passed=false
    fi
    
    if [[ "$validation_type" == "quick" ]]; then
        if [[ "$validation_passed" == "true" ]]; then
            log_success "Quick validation passed"
        else
            log_error "Quick validation failed"
            exit 1
        fi
        return 0
    fi
    
    # Full validation
    if ! validate_status_checks; then
        validation_passed=false
    fi
    
    if ! validate_pr_reviews; then
        validation_passed=false
    fi
    
    if ! validate_admin_enforcement; then
        validation_passed=false
    fi
    
    if ! validate_push_restrictions; then
        validation_passed=false
    fi
    
    if ! validate_linear_history; then
        validation_passed=false
    fi
    
    # Generate report
    if [[ "$validation_type" == "report" ]] || [[ "$validation_type" == "full" ]]; then
        generate_report
    fi
    
    # Test enforcement (informational)
    if [[ "$validation_type" == "full" ]]; then
        test_branch_protection
    fi
    
    # Final result
    echo ""
    if [[ "$validation_passed" == "true" ]]; then
        log_success "Branch protection validation completed successfully"
        log_success "All requirements are properly configured and enforced"
    else
        log_error "Branch protection validation failed"
        log_error "Some requirements are not properly configured"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"
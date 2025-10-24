#!/bin/bash

# Branch Protection Setup Script for mypylogger v0.2.0
#
# This script configures branch protection rules for the main branch
# to enforce quality gates and security requirements.
#
# Requirements Addressed:
# - 3.1: Prevent direct pushes to the main branch
# - 3.2: Require all quality checks to pass before allowing pull request merges
# - 3.3: Require at least one approving review for pull request merges
# - 3.4: Require branches to be up-to-date before merging
# - 3.5: Enforce status checks for all defined quality gates

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
    log_info "Checking prerequisites..."
    
    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        log_info "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check if authenticated with GitHub
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        log_info "Run: gh auth login"
        exit 1
    fi
    
    # Check if repository information is available
    if [[ -z "$REPO_OWNER" ]]; then
        log_warning "GITHUB_REPOSITORY_OWNER not set, attempting to detect from git remote"
        REPO_OWNER=$(git remote get-url origin | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p' || echo "")
        if [[ -z "$REPO_OWNER" ]]; then
            log_error "Could not determine repository owner"
            log_info "Set GITHUB_REPOSITORY_OWNER environment variable or run from git repository"
            exit 1
        fi
    fi
    
    log_success "Prerequisites check passed"
    log_info "Repository: $REPO_OWNER/$REPO_NAME"
}

# Define required status checks based on workflow configurations
get_required_status_checks() {
    cat << 'EOF'
[
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
EOF
}

# Create branch protection configuration
create_branch_protection() {
    log_info "Creating branch protection rule for '$BRANCH_NAME' branch..."
    
    # Get required status checks
    local status_checks
    status_checks=$(get_required_status_checks)
    
    # Create the protection rule using GitHub API
    local protection_config
    protection_config=$(cat << EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": $status_checks
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": true,
    "bypass_pull_request_allowances": {
      "users": [],
      "teams": [],
      "apps": []
    }
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true,
  "allow_auto_merge": false,
  "required_conversation_resolution": true
}
EOF
)
    
    # Apply the branch protection rule
    if gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection" \
        --method PUT \
        --input - <<< "$protection_config"; then
        log_success "Branch protection rule created successfully"
    else
        log_error "Failed to create branch protection rule"
        return 1
    fi
}

# Verify branch protection configuration
verify_branch_protection() {
    log_info "Verifying branch protection configuration..."
    
    # Get current protection settings
    local protection_info
    if protection_info=$(gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME/protection" 2>/dev/null); then
        log_success "Branch protection rule is active"
        
        # Parse and display key settings
        local enforce_admins
        local required_reviews
        local status_checks_strict
        local status_checks_count
        
        enforce_admins=$(echo "$protection_info" | jq -r '.enforce_admins.enabled // false')
        required_reviews=$(echo "$protection_info" | jq -r '.required_pull_request_reviews.required_approving_review_count // 0')
        status_checks_strict=$(echo "$protection_info" | jq -r '.required_status_checks.strict // false')
        status_checks_count=$(echo "$protection_info" | jq -r '.required_status_checks.contexts | length')
        
        log_info "Configuration summary:"
        log_info "  - Enforce for admins: $enforce_admins"
        log_info "  - Required reviews: $required_reviews"
        log_info "  - Strict status checks: $status_checks_strict"
        log_info "  - Required status checks: $status_checks_count"
        
        # List required status checks
        log_info "Required status checks:"
        echo "$protection_info" | jq -r '.required_status_checks.contexts[]' | while read -r check; do
            log_info "    - $check"
        done
        
    else
        log_error "Branch protection rule not found or not accessible"
        return 1
    fi
}

# Test branch protection (dry run)
test_branch_protection() {
    log_info "Testing branch protection configuration..."
    
    # Check if we can get branch information
    if gh api "repos/$REPO_OWNER/$REPO_NAME/branches/$BRANCH_NAME" > /dev/null 2>&1; then
        log_success "Branch '$BRANCH_NAME' is accessible"
    else
        log_error "Cannot access branch '$BRANCH_NAME'"
        return 1
    fi
    
    # Check repository permissions
    local repo_permissions
    if repo_permissions=$(gh api "repos/$REPO_OWNER/$REPO_NAME" --jq '.permissions' 2>/dev/null); then
        local admin_access
        admin_access=$(echo "$repo_permissions" | jq -r '.admin // false')
        
        if [[ "$admin_access" == "true" ]]; then
            log_success "Admin access confirmed - can configure branch protection"
        else
            log_warning "Limited access - may not be able to configure all protection settings"
        fi
    else
        log_warning "Could not determine repository permissions"
    fi
}

# Display usage information
show_usage() {
    cat << EOF
Branch Protection Setup Script for mypylogger v0.2.0

Usage: $0 [OPTIONS]

Options:
  --setup     Create branch protection rules (default)
  --verify    Verify existing branch protection configuration
  --test      Test branch protection setup (dry run)
  --help      Show this help message

Environment Variables:
  GITHUB_REPOSITORY_OWNER    Repository owner (auto-detected if not set)
  GITHUB_REPOSITORY_NAME     Repository name (default: mypylogger)

Prerequisites:
  - GitHub CLI (gh) installed and authenticated
  - Admin access to the repository
  - Repository must exist and be accessible

Examples:
  $0 --setup                 # Create branch protection rules
  $0 --verify                # Check current configuration
  $0 --test                  # Test setup without making changes

For more information, see: .github/BRANCH_PROTECTION.md
EOF
}

# Main execution
main() {
    local action="setup"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --setup)
                action="setup"
                shift
                ;;
            --verify)
                action="verify"
                shift
                ;;
            --test)
                action="test"
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
    
    # Execute based on action
    case $action in
        setup)
            log_info "Setting up branch protection for mypylogger v0.2.0"
            check_prerequisites
            test_branch_protection
            create_branch_protection
            verify_branch_protection
            log_success "Branch protection setup completed successfully"
            ;;
        verify)
            log_info "Verifying branch protection configuration"
            check_prerequisites
            verify_branch_protection
            ;;
        test)
            log_info "Testing branch protection setup (dry run)"
            check_prerequisites
            test_branch_protection
            log_success "Branch protection test completed"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
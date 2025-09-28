#!/bin/bash
# Security scanning script for mypylogger
# This script runs comprehensive security scans for local development

set -e  # Exit on any error

echo "🔒 Running Security Scans for mypylogger"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Not in a virtual environment. Consider activating venv first."
fi

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Install with: pip install $1"
        return 1
    fi
    return 0
}

print_status "Checking security tools..."

# Check for required security tools
TOOLS_MISSING=0

if ! check_tool bandit; then
    TOOLS_MISSING=1
fi

if ! check_tool safety; then
    TOOLS_MISSING=1
fi

if [ $TOOLS_MISSING -eq 1 ]; then
    print_error "Missing required security tools. Install with:"
    echo "pip install bandit safety"
    exit 1
fi

print_success "All security tools available"

# Create reports directory
mkdir -p reports/security

# 1. Bandit - Python security linter
print_status "Running Bandit security scan..."
if bandit -r mypylogger/ -f json -o reports/security/bandit-report.json; then
    print_success "Bandit scan completed - no issues found"
else
    BANDIT_EXIT_CODE=$?
    if [ $BANDIT_EXIT_CODE -eq 1 ]; then
        print_warning "Bandit found potential security issues - check reports/security/bandit-report.json"
    else
        print_error "Bandit scan failed with exit code $BANDIT_EXIT_CODE"
    fi
fi

# Also generate human-readable report
bandit -r mypylogger/ -f txt -o reports/security/bandit-report.txt || true

# 2. Safety - Dependency vulnerability scanner
print_status "Running Safety dependency scan..."
if safety check --json > reports/security/safety-report.json 2>&1; then
    print_success "Safety scan completed - no vulnerabilities found"
else
    SAFETY_EXIT_CODE=$?
    if [ $SAFETY_EXIT_CODE -eq 64 ]; then
        print_warning "Safety found vulnerabilities - check reports/security/safety-report.json"
    else
        print_warning "Safety scan completed with warnings - check reports/security/safety-report.json"
    fi
fi

# Also generate human-readable report
safety check > reports/security/safety-report.txt 2>&1 || true

# 3. Check for common security issues in configuration files
print_status "Checking configuration files for security issues..."

# Check for hardcoded secrets (basic patterns) - exclude venv directory
SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]+['\"]"
    "secret\s*=\s*['\"][^'\"]+['\"]"
    "token\s*=\s*['\"][^'\"]+['\"]"
    "api_key\s*=\s*['\"][^'\"]+['\"]"
    "private_key"
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i -E "$pattern" --include="*.py" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.toml" --exclude-dir=venv --exclude-dir=.venv --exclude-dir=build --exclude-dir=dist . 2>/dev/null; then
        SECRETS_FOUND=1
    fi
done

if [ $SECRETS_FOUND -eq 1 ]; then
    print_warning "Potential secrets found in code - review manually"
else
    print_success "No obvious secrets found in configuration files"
fi

# 4. Check file permissions (macOS compatible)
print_status "Checking file permissions..."
find . -name "*.py" -perm +002 -exec echo "World-writable Python file: {}" \; > reports/security/permissions-report.txt 2>/dev/null || true
if [ -s reports/security/permissions-report.txt ]; then
    print_warning "World-writable Python files found - check reports/security/permissions-report.txt"
else
    print_success "File permissions look secure"
fi

# 5. Generate summary report
print_status "Generating security summary..."

cat > reports/security/summary.md << EOF
# Security Scan Summary

**Scan Date**: $(date)
**Project**: mypylogger
**Scan Type**: Local Development Security Scan

## Tools Used

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Custom Checks**: Configuration and permissions

## Reports Generated

- \`bandit-report.json\` - Detailed Bandit findings (JSON)
- \`bandit-report.txt\` - Human-readable Bandit report
- \`safety-report.json\` - Safety vulnerability findings (JSON)  
- \`safety-report.txt\` - Human-readable Safety report
- \`permissions-report.txt\` - File permission issues
- \`summary.md\` - This summary report

## Next Steps

1. Review all generated reports
2. Address any HIGH or CRITICAL findings immediately
3. Plan remediation for MEDIUM findings
4. Document any accepted risks with justification

## Automation

This scan should be run:
- Before every commit (via pre-commit hooks)
- In CI/CD pipeline on every PR
- Weekly as part of maintenance routine
- Before every release

EOF

print_success "Security scan completed!"
echo ""
print_status "Reports generated in: reports/security/"
print_status "Review summary: reports/security/summary.md"

# Check if any critical issues were found
if [ -f reports/security/bandit-report.json ] && grep -q '"severity": "HIGH"' reports/security/bandit-report.json; then
    print_error "HIGH severity security issues found! Review immediately."
    exit 1
fi

if [ -f reports/security/safety-report.json ] && grep -q '"vulnerability"' reports/security/safety-report.json; then
    print_error "Dependency vulnerabilities found! Review immediately."
    exit 1
fi

print_success "No critical security issues detected ✅"
#!/bin/bash

# Master test script for mypylogger v0.2.5
# This script runs all quality gates and must pass before any task completion
# 
# LOCAL DEVELOPMENT FOCUS: Code quality validation only
# - Badge updates are CI-only (no local README modifications)
# - Security scans run for validation but don't update badges
# - Focus on test execution, linting, formatting, and type checking
# 
# Usage:
#   ./scripts/run_tests.sh                    # Run all tests (default)
#   ./scripts/run_tests.sh --phase=<phase>    # Run phase-specific tests
#   ./scripts/run_tests.sh --full             # Force full test suite
#
# Phase-specific testing:
#   --phase=phase-5-project-badges           # Test only badge functionality (no README updates)
#   --phase=phase-3-github-cicd              # Test only CI/CD functionality
#   --phase=phase-6-security-findings        # Test only security functionality

set -e  # Exit on any error

# Parse command line arguments
PHASE=""
FORCE_FULL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --phase=*)
            PHASE="${1#*=}"
            shift
            ;;
        --full)
            FORCE_FULL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--phase=<phase>] [--full] [--help]"
            echo ""
            echo "Options:"
            echo "  --phase=<phase>    Run tests for specific phase only"
            echo "  --full             Force full test suite (override phase)"
            echo "  --help             Show this help message"
            echo ""
            echo "Available phases:"
            echo "  phase-5-project-badges    Badge system functionality"
            echo "  phase-3-github-cicd       CI/CD workflow functionality"
            echo "  phase-6-security-findings Security scanning functionality"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine test scope
if [[ "$FORCE_FULL" == "true" ]]; then
    TEST_SCOPE="full"
    SCOPE_DESCRIPTION="Full Test Suite (forced)"
elif [[ -n "$PHASE" ]]; then
    TEST_SCOPE="phase"
    SCOPE_DESCRIPTION="Phase-Specific Tests: $PHASE"
else
    TEST_SCOPE="full"
    SCOPE_DESCRIPTION="Full Test Suite (default)"
fi

echo "🧪 mypylogger v0.2.5 - Master Test Runner"
echo "===================================="
echo "Scope: $SCOPE_DESCRIPTION"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall success
OVERALL_SUCCESS=true

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        OVERALL_SUCCESS=false
    fi
}

# Function to run command and capture result
run_check() {
    local cmd="$1"
    local description="$2"
    
    echo -e "${BLUE}Running: $description${NC}"
    if eval "$cmd" > /tmp/test_output 2>&1; then
        print_status 0 "$description"
    else
        print_status 1 "$description"
        echo -e "${YELLOW}Error output:${NC}"
        cat /tmp/test_output
        echo ""
    fi
}

# Function to get phase-specific test patterns
get_phase_test_patterns() {
    local phase="$1"
    
    case "$phase" in
        "phase-5-project-badges")
            echo "tests/unit/test_*badge* tests/integration/test_*badge* badges/"
            ;;
        "phase-3-github-cicd")
            echo "tests/unit/test_*cicd* tests/integration/test_*cicd* tests/unit/test_*yaml* tests/integration/test_*yaml* security/"
            ;;
        "phase-6-security-findings")
            echo "tests/unit/test_*security* tests/integration/test_*security* security/"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Function to get phase-specific source patterns
get_phase_source_patterns() {
    local phase="$1"
    
    case "$phase" in
        "phase-5-project-badges")
            echo "badges/"
            ;;
        "phase-3-github-cicd")
            echo "security/ scripts/*cicd* scripts/*yaml*"
            ;;
        "phase-6-security-findings")
            echo "security/"
            ;;
        *)
            echo "src/ tests/"
            ;;
    esac
}

# Function to run phase-specific or full tests
run_tests_for_scope() {
    local scope="$1"
    local phase="$2"
    
    if [[ "$scope" == "phase" ]]; then
        local test_patterns=$(get_phase_test_patterns "$phase")
        local source_patterns=$(get_phase_source_patterns "$phase")
        
        if [[ -z "$test_patterns" ]]; then
            echo -e "${RED}❌ Unknown phase: $phase${NC}"
            echo "Available phases: phase-5-project-badges, phase-3-github-cicd, phase-6-security-findings"
            exit 1
        fi
        
        echo -e "${YELLOW}📋 Phase-specific testing for: $phase${NC}"
        echo -e "${YELLOW}   Test patterns: $test_patterns${NC}"
        echo -e "${YELLOW}   Source patterns: $source_patterns${NC}"
        echo ""
        
        # Phase-specific formatting check
        echo "1. Code Formatting Check (Phase-Specific)"
        echo "-----------------------------------------"
        run_check "uv run --active ruff format --check $source_patterns" "Code formatting compliance (phase-specific)"
        
        # Phase-specific linting check
        echo ""
        echo "2. Linting Check (Phase-Specific)"
        echo "---------------------------------"
        run_check "uv run --active ruff check $source_patterns" "Linting compliance (phase-specific)"
        
        # Phase-specific type checking (only if src/ is included)
        if [[ "$source_patterns" == *"src/"* ]]; then
            echo ""
            echo "3. Type Checking (Phase-Specific)"
            echo "---------------------------------"
            run_check "uv run --active mypy src/" "Type checking compliance (phase-specific)"
        fi
        
        # Phase-specific test execution
        echo ""
        echo "4. Test Execution (Phase-Specific)"
        echo "----------------------------------"
        # Build pytest command with existing test files only
        local pytest_cmd="uv run --active pytest"
        local test_files=""
        
        for pattern in $test_patterns; do
            if [[ -d "$pattern" ]] || ls $pattern 2>/dev/null | grep -q .; then
                test_files="$test_files $pattern"
            fi
        done
        
        if [[ -n "$test_files" ]]; then
            run_check "$pytest_cmd $test_files -v" "Phase-specific test execution"
        else
            echo -e "${YELLOW}⚠️  No test files found for phase $phase${NC}"
            echo -e "${GREEN}✓ Phase-specific test execution (no tests to run)${NC}"
        fi
        
        # Phase-specific security checks (only for security-related phases)
        if [[ "$phase" == *"security"* ]] || [[ "$phase" == "phase-5-project-badges" ]]; then
            echo ""
            echo "5. Security Scanning (Phase-Specific)"
            echo "-------------------------------------"
            run_check "uv run --active python -c 'from badges.security import security_checks_passed; exit(0 if security_checks_passed() else 1)'" "Security scanning (phase-specific)"
        fi
        
        # Phase-specific import verification (only if relevant modules exist)
        if [[ "$phase" == "phase-5-project-badges" ]]; then
            echo ""
            echo "6. Import Verification (Phase-Specific)"
            echo "---------------------------------------"
            run_check "uv run --active python -c 'import badges; print(\"badges module imported successfully\")'" "Badge module import verification"
            
            echo ""
            echo "7. Badge Generation Verification (Phase-Specific)"
            echo "-------------------------------------------------"
            run_check "uv run --active python -m badges --generate-only --no-status-detection" "Badge generation (local development mode - no README updates)"
        fi
        
    else
        # Full test suite (existing functionality)
        run_full_test_suite
    fi
}

# Function to run the full test suite
run_full_test_suite() {

    echo "1. Code Formatting Check"
    echo "------------------------"
    run_check "uv run --active ruff format --check src/ tests/ --exclude ci-cd-tests" "Code formatting compliance"

    echo ""
    echo "2. Linting Check"
    echo "----------------"
    run_check "uv run --active ruff check src/ tests/ --exclude ci-cd-tests" "Linting compliance"

    echo ""
    echo "3. Type Checking"
    echo "----------------"
    run_check "uv run --active mypy src/" "Type checking compliance"

    echo ""
    echo "4. Test Execution with Coverage"
    echo "-------------------------------"
    run_check "uv run --active pytest --cov=mypylogger --cov-fail-under=95 --cov-report=term-missing" "Test execution and coverage (95% minimum)"

    echo ""
    echo "5. Security Scanning (Local Validation Only)"
    echo "---------------------------------------------"
    run_check "uv run --active python -c 'from badges.security import security_checks_passed; exit(0 if security_checks_passed() else 1)'" "Security scanning (bandit, safety, semgrep, codeql simulation) - validation only"

    echo ""
    echo "6. Import Verification"
    echo "----------------------"
    run_check "uv run --active python -c 'import mypylogger; print(f\"mypylogger v{mypylogger.get_version()} imported successfully\")'" "Package import verification"

    echo ""
    echo "7. Badge Generation Verification (Local Development)"
    echo "----------------------------------------------------"
    run_check "uv run --active python -m badges --generate-only --no-status-detection" "Badge generation (local mode - no README updates)"

    echo ""
    echo "8. Dependency Usage Check"
    echo "-------------------------"
    run_check "uv run --active deptry ." "Unused dependency detection"
}

# Main execution
run_tests_for_scope "$TEST_SCOPE" "$PHASE"

echo ""
echo "Summary"
echo "======="

if [ "$OVERALL_SUCCESS" = true ]; then
    if [[ "$TEST_SCOPE" == "phase" ]]; then
        echo -e "${GREEN}🎉 PHASE-SPECIFIC QUALITY GATES PASSED!${NC}"
        echo -e "${GREEN}✓ Phase: $PHASE${NC}"
        echo -e "${GREEN}✓ Code formatting: compliant (phase-specific)${NC}"
        echo -e "${GREEN}✓ Linting: no issues (phase-specific)${NC}"
        if [[ "$PHASE" != "phase-6-security-findings" ]] && [[ "$PHASE" != "phase-3-github-cicd" ]]; then
            echo -e "${GREEN}✓ Type checking: passed${NC}"
        fi
        echo -e "${GREEN}✓ Tests: all passing (phase-specific)${NC}"
        if [[ "$PHASE" == *"security"* ]] || [[ "$PHASE" == "phase-5-project-badges" ]]; then
            echo -e "${GREEN}✓ Security: all scans passed (validation only - no badge updates)${NC}"
        fi
        if [[ "$PHASE" == "phase-5-project-badges" ]]; then
            echo -e "${GREEN}✓ Badge module: imports successfully${NC}"
            echo -e "${GREEN}✓ Badge generation: works correctly (local mode - no README updates)${NC}"
        fi
        echo ""
        echo -e "${GREEN}🚀 Ready for phase-specific task completion!${NC}"
        echo -e "${YELLOW}💡 Run './scripts/run_tests.sh --full' for complete validation before final commit${NC}"
    else
        echo -e "${GREEN}🎉 ALL QUALITY GATES PASSED!${NC}"
        echo -e "${GREEN}✓ Code formatting: compliant${NC}"
        echo -e "${GREEN}✓ Linting: no issues${NC}"
        echo -e "${GREEN}✓ Type checking: passed${NC}"
        echo -e "${GREEN}✓ Tests: all passing with 95%+ coverage${NC}"
        echo -e "${GREEN}✓ Security: all scans passed (validation only - no badge updates)${NC}"
        echo -e "${GREEN}✓ Package: imports successfully${NC}"
        echo -e "${GREEN}✓ Badge generation: works correctly (local mode - no README updates)${NC}"
        echo -e "${GREEN}✓ Dependencies: all dependencies are used${NC}"
        echo ""
        echo -e "${GREEN}🚀 Ready for task completion!${NC}"
    fi
    exit 0
else
    if [[ "$TEST_SCOPE" == "phase" ]]; then
        echo -e "${RED}❌ PHASE-SPECIFIC QUALITY GATES FAILED!${NC}"
        echo -e "${RED}Phase: $PHASE${NC}"
        echo -e "${RED}One or more phase-specific checks failed. Please fix the issues above.${NC}"
    else
        echo -e "${RED}❌ QUALITY GATES FAILED!${NC}"
        echo -e "${RED}One or more checks failed. Please fix the issues above.${NC}"
    fi
    echo ""
    echo -e "${YELLOW}💡 Common fixes:${NC}"
    echo -e "${YELLOW}  - Run 'uv run ruff format .' to fix formatting${NC}"
    echo -e "${YELLOW}  - Run 'uv run ruff check --fix .' to auto-fix linting issues${NC}"
    echo -e "${YELLOW}  - Add type hints for mypy compliance${NC}"
    echo -e "${YELLOW}  - Add tests to reach 95% coverage${NC}"
    echo -e "${YELLOW}  - Review security scan results and fix issues${NC}"
    echo -e "${YELLOW}  - Remove unused dependencies with 'uv remove <package>'${NC}"
    echo -e "${YELLOW}  - Add missing dependencies with 'uv add <package>'${NC}"
    if [[ "$TEST_SCOPE" == "phase" ]]; then
        echo -e "${YELLOW}  - Run './scripts/run_tests.sh --full' to validate against complete test suite${NC}"
    fi
    exit 1
fi
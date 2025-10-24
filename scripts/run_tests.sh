#!/bin/bash

# Master test script for mypylogger v0.2.0
# This script runs all quality gates and must pass before any task completion

set -e  # Exit on any error

echo "🧪 mypylogger v0.2.0 - Master Test Runner"
echo "===================================="
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
echo "5. Import Verification"
echo "----------------------"
run_check "uv run --active python -c 'import mypylogger; print(f\"mypylogger v{mypylogger.get_version()} imported successfully\")'" "Package import verification"

echo ""
echo "Summary"
echo "======="

if [ "$OVERALL_SUCCESS" = true ]; then
    echo -e "${GREEN}🎉 ALL QUALITY GATES PASSED!${NC}"
    echo -e "${GREEN}✓ Code formatting: compliant${NC}"
    echo -e "${GREEN}✓ Linting: no issues${NC}"
    echo -e "${GREEN}✓ Type checking: passed${NC}"
    echo -e "${GREEN}✓ Tests: all passing with 95%+ coverage${NC}"
    echo -e "${GREEN}✓ Package: imports successfully${NC}"
    echo ""
    echo -e "${GREEN}🚀 Ready for task completion!${NC}"
    exit 0
else
    echo -e "${RED}❌ QUALITY GATES FAILED!${NC}"
    echo -e "${RED}One or more checks failed. Please fix the issues above.${NC}"
    echo ""
    echo -e "${YELLOW}💡 Common fixes:${NC}"
    echo -e "${YELLOW}  - Run 'uv run ruff format .' to fix formatting${NC}"
    echo -e "${YELLOW}  - Run 'uv run ruff check --fix .' to auto-fix linting issues${NC}"
    echo -e "${YELLOW}  - Add type hints for mypy compliance${NC}"
    echo -e "${YELLOW}  - Add tests to reach 95% coverage${NC}"
    exit 1
fi
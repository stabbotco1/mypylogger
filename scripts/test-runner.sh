#!/bin/bash
# Test script for the updated run-complete-test-suite.sh
# This script tests all the new functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing Updated Test Suite Runner${NC}"
echo -e "${BLUE}====================================${NC}"

# Function to run a test and show results
run_test() {
    local test_name="$1"
    local command="$2"

    echo ""
    echo -e "${CYAN}Testing: $test_name${NC}"
    echo -e "${YELLOW}Command: $command${NC}"
    echo "----------------------------------------"

    if eval "$command"; then
        echo -e "${GREEN}✅ Test passed: $test_name${NC}"
    else
        echo -e "${RED}❌ Test failed: $test_name${NC}"
        return 1
    fi
}

# Ensure we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "mypylogger" ]]; then
    echo -e "${RED}❌ Not in mypylogger project root directory${NC}"
    exit 1
fi

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not active, attempting activation...${NC}"

    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ Virtual environment not found at venv/bin/activate${NC}"
        echo "Please create and activate a virtual environment first:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -e \".[dev]\""
        exit 1
    fi
else
    echo -e "${GREEN}✅ Virtual environment already active: $VIRTUAL_ENV${NC}"
fi

# Make sure the script is executable
chmod +x scripts/run-complete-test-suite.sh

echo ""
echo -e "${BLUE}Running Test Suite Runner Tests${NC}"
echo -e "${BLUE}===============================${NC}"

# Test 1: Help output
run_test "Help Output" "./scripts/run-complete-test-suite.sh --help"

echo ""
echo -e "${CYAN}Press Enter to continue to summary mode test...${NC}"
read -r

# Test 2: Summary mode (default behavior)
run_test "Summary Mode (Default)" "./scripts/run-complete-test-suite.sh"

echo ""
echo -e "${CYAN}Press Enter to continue to fast mode test...${NC}"
read -r

# Test 3: Fast mode
run_test "Fast Mode" "./scripts/run-complete-test-suite.sh --fast"

echo ""
echo -e "${CYAN}Press Enter to continue to subset quality test...${NC}"
read -r

# Test 4: Subset mode - quality only
run_test "Subset Mode - Quality" "./scripts/run-complete-test-suite.sh --subset quality"

echo ""
echo -e "${CYAN}Press Enter to continue to subset tests test...${NC}"
read -r

# Test 5: Subset mode - tests only
run_test "Subset Mode - Tests" "./scripts/run-complete-test-suite.sh --subset tests"

echo ""
echo -e "${CYAN}Press Enter to continue to verbose mode test...${NC}"
read -r

# Test 6: Verbose mode (this will show detailed output)
run_test "Verbose Mode" "./scripts/run-complete-test-suite.sh --verbose --fast"

echo ""
echo -e "${GREEN}🎉 All tests completed!${NC}"
echo ""
echo -e "${BLUE}Summary of what was tested:${NC}"
echo "✅ Help output functionality"
echo "✅ Summary mode (new default behavior)"
echo "✅ Fast mode with summary output"
echo "✅ Subset mode - quality checks only"
echo "✅ Subset mode - tests only"
echo "✅ Verbose mode with detailed output"
echo ""
echo -e "${GREEN}The test suite runner is working correctly with the new summary-focused output!${NC}"

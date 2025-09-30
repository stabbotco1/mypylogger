#!/bin/bash
# Complete Test Suite Runner for mypylogger
# 
# This script runs the complete test suite with comprehensive reporting
# to verify task completion, test coverage, and detect regressions.
#
# Usage: ./scripts/run-complete-test-suite.sh [OPTIONS]
#
# Options:
#   --fast         Run only fast unit tests (skip integration and performance)
#   --performance  Include performance benchmark tests
#   --verbose      Show detailed output from all commands
#   --subset TYPE  Run only specific test subset (quality|tests|security|build|docs)
#   --help         Show this help message
#
# Default behavior: Run comprehensive testing with summary output only

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
FAST_MODE=false
PERFORMANCE_MODE=false
VERBOSE_MODE=false
SUBSET_MODE=""
COVERAGE_THRESHOLD=90
START_TIME=$(date +%s)

# Test execution tracking (compatible with older bash versions)
TEST_RESULTS=""
TEST_TIMES=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fast)
            FAST_MODE=true
            shift
            ;;
        --performance)
            PERFORMANCE_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE_MODE=true
            shift
            ;;
        --subset)
            SUBSET_MODE="$2"
            shift 2
            ;;
        --help)
            echo "Complete Test Suite Runner for mypylogger"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fast         Run only fast unit tests (skip integration and performance)"
            echo "  --performance  Include performance benchmark tests"
            echo "  --verbose      Show detailed output from all commands"
            echo "  --subset TYPE  Run only specific test subset:"
            echo "                   quality  - Code quality checks only"
            echo "                   tests    - Test execution only"
            echo "                   security - Security scans only"
            echo "                   build    - Package build verification only"
            echo "                   docs     - Documentation verification only"
            echo "  --help         Show this help message"
            echo ""
            echo "Default: Run comprehensive testing with summary output only"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run complete test suite (summary output)"
            echo "  $0 --fast            # Quick verification (unit tests only)"
            echo "  $0 --performance     # Include performance benchmarks"
            echo "  $0 --verbose         # Show detailed output"
            echo "  $0 --subset quality  # Run only code quality checks"
            echo "  $0 --subset tests    # Run only test execution"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

run_command() {
    local cmd="$1"
    local description="$2"
    local step_name="$3"
    local step_start=$(date +%s)
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        echo -e "${PURPLE}Running: $cmd${NC}"
        if eval "$cmd"; then
            local step_end=$(date +%s)
            local step_duration=$((step_end - step_start))
            TEST_RESULTS="${TEST_RESULTS}${step_name}:PASS;"
            TEST_TIMES="${TEST_TIMES}${step_name}:${step_duration}s;"
            print_success "$description (${step_duration}s)"
        else
            TEST_RESULTS="${TEST_RESULTS}${step_name}:FAIL;"
            TEST_TIMES="${TEST_TIMES}${step_name}:N/A;"
            print_error "$description failed"
            return 1
        fi
    else
        # Capture both stdout and stderr for better error reporting
        local output
        if output=$(eval "$cmd" 2>&1); then
            local step_end=$(date +%s)
            local step_duration=$((step_end - step_start))
            TEST_RESULTS="${TEST_RESULTS}${step_name}:PASS;"
            TEST_TIMES="${TEST_TIMES}${step_name}:${step_duration}s;"
            print_success "$description (${step_duration}s)"
        else
            TEST_RESULTS="${TEST_RESULTS}${step_name}:FAIL;"
            TEST_TIMES="${TEST_TIMES}${step_name}:N/A;"
            print_error "$description failed"
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                echo "Command: $cmd"
                if [[ -n "$output" ]]; then
                    echo "Output: $output"
                fi
            fi
            return 1
        fi
    fi
}

# Auto-detect and activate virtual environment
setup_environment() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "ENVIRONMENT SETUP"
    fi
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]] || [[ ! -d "mypylogger" ]]; then
        print_error "Not in mypylogger project root directory"
        exit 1
    fi
    
    # Auto-detect and activate virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_step "Virtual environment not active, attempting auto-activation..."
        fi
        
        # Try common virtual environment locations
        local venv_paths=("venv/bin/activate" ".venv/bin/activate" "env/bin/activate")
        local venv_activated=false
        
        for venv_path in "${venv_paths[@]}"; do
            if [[ -f "$venv_path" ]]; then
                if [[ "$VERBOSE_MODE" == "true" ]]; then
                    print_step "Found virtual environment at $venv_path"
                fi
                # Source the virtual environment
                source "$venv_path"
                if [[ -n "$VIRTUAL_ENV" ]]; then
                    if [[ "$VERBOSE_MODE" == "true" ]]; then
                        print_success "Virtual environment activated: $VIRTUAL_ENV"
                    fi
                    venv_activated=true
                    break
                fi
            fi
        done
        
        if [[ "$venv_activated" == "false" ]]; then
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_warning "No virtual environment found or activation failed"
                print_step "Attempting to create virtual environment..."
            fi
            
            # Try to create a virtual environment
            if command -v python3 >/dev/null 2>&1; then
                python3 -m venv venv >/dev/null 2>&1
                if [[ -f "venv/bin/activate" ]]; then
                    source venv/bin/activate
                    if [[ "$VERBOSE_MODE" == "true" ]]; then
                        print_success "Created and activated new virtual environment"
                        print_step "Installing development dependencies..."
                    fi
                    pip install --upgrade pip >/dev/null 2>&1
                    pip install -e ".[dev]" >/dev/null 2>&1
                else
                    print_error "Failed to create virtual environment"
                    if [[ "$VERBOSE_MODE" == "true" ]]; then
                        echo "Please manually create and activate a virtual environment:"
                        echo "  python3 -m venv venv"
                        echo "  source venv/bin/activate"
                        echo "  pip install -e \".[dev]\""
                    fi
                    exit 1
                fi
            else
                print_error "Python3 not found, cannot create virtual environment"
                exit 1
            fi
        fi
    else
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_success "Virtual environment already active: $VIRTUAL_ENV"
        fi
    fi
}

# Check prerequisites
check_prerequisites() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "VERIFYING PREREQUISITES"
        
        # Check Python version
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        print_success "Python version: $PYTHON_VERSION"
    fi
    
    # Check if dependencies are installed and install if missing
    if ! python -c "import mypylogger" 2>/dev/null; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_warning "mypylogger package not importable, installing dependencies..."
        fi
        pip install -e ".[dev]" >/dev/null 2>&1
        
        # Verify installation
        if python -c "import mypylogger" 2>/dev/null; then
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_success "mypylogger package installed and importable"
            fi
        else
            print_error "Failed to install mypylogger package"
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                echo "Please check your installation and try again"
            fi
            exit 1
        fi
    else
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_success "mypylogger package importable"
        fi
    fi
    
    # Verify all required development tools are available
    local missing_tools=()
    local required_tools=("black" "isort" "flake8" "mypy" "bandit" "safety" "pytest")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_warning "Missing development tools: ${missing_tools[*]}"
            print_step "Installing missing development dependencies..."
        fi
        pip install -e ".[dev]" >/dev/null 2>&1
        
        # Verify tools are now available
        local still_missing=()
        for tool in "${missing_tools[@]}"; do
            if ! command -v "$tool" >/dev/null 2>&1; then
                still_missing+=("$tool")
            fi
        done
        
        if [[ ${#still_missing[@]} -gt 0 ]]; then
            print_error "Still missing tools after installation: ${still_missing[*]}"
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                echo "Please check your development environment setup"
            fi
            exit 1
        else
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_success "All development tools now available"
            fi
        fi
    else
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_success "All required development tools available"
        fi
    fi
}

# Run code quality checks
run_quality_checks() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "CODE QUALITY CHECKS"
    fi
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_step "Running code formatting check (Black)"
    fi
    if ! run_command "black --check --diff ." "Code formatting check" "formatting"; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_warning "Code formatting issues found - attempting automatic fix"
            print_step "Fixing formatting with Black..."
        fi
        black . >/dev/null 2>&1
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_step "Fixing import sorting with isort..."
        fi
        isort . >/dev/null 2>&1
        
        # Verify the fix worked
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_step "Verifying formatting fix..."
        fi
        if run_command "black --check --diff ." "Black formatting verification" "formatting_fix" && run_command "isort --check-only --diff ." "Import sorting verification" "import_sorting"; then
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_success "Formatting issues automatically resolved"
            fi
        else
            print_error "Automatic formatting fix failed"
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                echo "Manual intervention required:"
                echo "  1. Run: black ."
                echo "  2. Run: isort ."
                echo "  3. Check for any remaining issues"
            fi
            return 1
        fi
    else
        if ! run_command "isort --check-only --diff ." "Import sorting check" "import_sorting"; then
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_warning "Import sorting issues found - attempting automatic fix"
                print_step "Fixing import sorting with isort..."
            fi
            isort . >/dev/null 2>&1
            
            # Verify the fix worked
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                print_step "Verifying import sorting fix..."
            fi
            if ! run_command "isort --check-only --diff ." "Import sorting verification" "import_sorting_fix"; then
                print_error "Automatic import sorting fix failed"
                if [[ "$VERBOSE_MODE" == "true" ]]; then
                    echo "Manual intervention required: run 'isort .'"
                fi
                return 1
            fi
        fi
    fi
    
    run_command "flake8 ." "Linting check" "linting"
    run_command "mypy mypylogger/" "Type checking" "type_checking"
    run_command "bandit -r mypylogger/ -f txt" "Security scan" "security_scan"
    run_command "safety check" "Dependency vulnerability scan" "vulnerability_scan"
}

# Run test suite with coverage
run_tests() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "TEST EXECUTION"
    fi
    
    local test_start=$(date +%s)
    
    if [[ "$FAST_MODE" == "true" ]]; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_step "Running fast unit tests only"
        fi
        TEST_CMD="pytest tests/unit/ -v --cov=mypylogger --cov-report=html --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD"
    else
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_step "Running complete test suite"
        fi
        TEST_CMD="pytest -v --cov=mypylogger --cov-report=html --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD"
    fi
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        if eval "$TEST_CMD"; then
            local test_end=$(date +%s)
            local test_duration=$((test_end - test_start))
            TEST_RESULTS="${TEST_RESULTS}tests:PASS;"
            TEST_TIMES="${TEST_TIMES}tests:${test_duration}s;"
        else
            TEST_RESULTS="${TEST_RESULTS}tests:FAIL;"
            TEST_TIMES="${TEST_TIMES}tests:N/A;"
            return 1
        fi
    else
        if eval "$TEST_CMD" > test_output.log 2>&1; then
            local test_end=$(date +%s)
            local test_duration=$((test_end - test_start))
            
            # Extract coverage percentage
            COVERAGE=$(grep "TOTAL" test_output.log | awk '{print $4}' | sed 's/%//')
            
            # Extract test count
            PASSED_TESTS=$(grep -o "[0-9]* passed" test_output.log | head -1 | awk '{print $1}')
            
            TEST_RESULTS["tests"]="PASS"
            TEST_TIMES["tests"]="${test_duration}s"
            
            print_success "Tests: ${PASSED_TESTS} passed, ${COVERAGE}% coverage (${test_duration}s)"
        else
            TEST_RESULTS["tests"]="FAIL"
            TEST_TIMES["tests"]="N/A"
            print_error "Tests failed"
            if [[ "$VERBOSE_MODE" == "true" ]]; then
                echo "Last 20 lines of test output:"
                tail -20 test_output.log
            fi
            return 1
        fi
    fi
}

# Run performance benchmarks
run_performance_tests() {
    if [[ "$PERFORMANCE_MODE" == "true" ]] && [[ "$FAST_MODE" == "false" ]]; then
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_header "PERFORMANCE BENCHMARKS"
            print_step "Running performance benchmark tests"
        fi
        
        local perf_start=$(date +%s)
        
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            if pytest tests/test_performance.py -v -m performance -s; then
                local perf_end=$(date +%s)
                local perf_duration=$((perf_end - perf_start))
                TEST_RESULTS["performance"]="PASS"
                TEST_TIMES["performance"]="${perf_duration}s"
            else
                TEST_RESULTS["performance"]="FAIL"
                TEST_TIMES["performance"]="N/A"
                return 1
            fi
        else
            if pytest tests/test_performance.py -v -m performance -s > perf_output.log 2>&1; then
                local perf_end=$(date +%s)
                local perf_duration=$((perf_end - perf_start))
                TEST_RESULTS["performance"]="PASS"
                TEST_TIMES["performance"]="${perf_duration}s"
                
                print_success "Performance benchmarks passed (${perf_duration}s)"
                
                # Extract key performance metrics for summary
                if grep -q "Latency Performance Metrics" perf_output.log; then
                    local avg_latency=$(grep -A 4 "Latency Performance Metrics" perf_output.log | grep "Average" | awk '{print $2}')
                    if [[ -n "$avg_latency" ]]; then
                        echo "  Average latency: ${avg_latency}"
                    fi
                fi
            else
                TEST_RESULTS["performance"]="FAIL"
                TEST_TIMES["performance"]="N/A"
                print_error "Performance benchmarks failed"
                if [[ "$VERBOSE_MODE" == "true" ]]; then
                    echo "Performance test output:"
                    cat perf_output.log
                fi
                return 1
            fi
        fi
    fi
}

# Verify package build
verify_package_build() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "PACKAGE BUILD VERIFICATION"
        print_step "Building package"
    fi
    
    run_command "python -m build" "Package build" "build"
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_step "Checking package"
    fi
    run_command "python -m twine check dist/*" "Package validation" "package_validation"
}

# Verify badges and documentation
verify_documentation() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_header "DOCUMENTATION VERIFICATION"
        print_step "Verifying README badges"
    fi
    
    if [[ -f "scripts/verify-badges.py" ]]; then
        run_command "python scripts/verify-badges.py" "Badge verification" "badges"
    else
        if [[ "$VERBOSE_MODE" == "true" ]]; then
            print_warning "Badge verification script not found"
        fi
        TEST_RESULTS["badges"]="SKIP"
        TEST_TIMES["badges"]="N/A"
    fi
    
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        print_step "Checking documentation completeness"
    fi
    run_command "python -c \"import mypylogger; help(mypylogger)\"" "Documentation check" "documentation"
}

# Generate final report
generate_report() {
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}TEST SUITE SUMMARY${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # Count results
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local skipped_tests=0
    
    for test in "${!TEST_RESULTS[@]}"; do
        total_tests=$((total_tests + 1))
        case "${TEST_RESULTS[$test]}" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "SKIP") skipped_tests=$((skipped_tests + 1)) ;;
        esac
    done
    
    # Overall status
    if [[ $failed_tests -eq 0 ]]; then
        echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    else
        echo -e "${RED}❌ ${failed_tests} CHECK(S) FAILED${NC}"
    fi
    
    echo ""
    echo "📊 Execution Summary:"
    echo "   Total Duration: ${DURATION}s"
    echo "   Mode: $(if [[ "$FAST_MODE" == "true" ]]; then echo "Fast"; elif [[ -n "$SUBSET_MODE" ]]; then echo "Subset ($SUBSET_MODE)"; else echo "Complete"; fi)"
    echo "   Results: ${passed_tests} passed, ${failed_tests} failed, ${skipped_tests} skipped"
    
    echo ""
    echo "🔍 Check Results:"
    
    # Define check order for consistent output
    local check_order=("formatting" "import_sorting" "linting" "type_checking" "security_scan" "vulnerability_scan" "tests" "performance" "build" "package_validation" "badges" "documentation")
    
    for check in "${check_order[@]}"; do
        if [[ -n "${TEST_RESULTS[$check]}" ]]; then
            local status="${TEST_RESULTS[$check]}"
            local time="${TEST_TIMES[$check]}"
            local icon
            local color
            
            case "$status" in
                "PASS") icon="✅"; color="$GREEN" ;;
                "FAIL") icon="❌"; color="$RED" ;;
                "SKIP") icon="⏭️"; color="$YELLOW" ;;
            esac
            
            printf "   %s %-20s %s %s\n" "$icon" "$check" "$time" ""
        fi
    done
    
    if [[ $failed_tests -eq 0 ]]; then
        echo ""
        echo -e "${GREEN}🚀 All quality gates passed - ready for deployment!${NC}"
        
        if [[ "$VERBOSE_MODE" == "false" ]]; then
            echo ""
            echo "💡 For detailed output, run with --verbose flag"
        fi
        
        echo ""
        echo "📁 Generated artifacts:"
        if [[ -d "htmlcov" ]]; then
            echo "   • htmlcov/index.html - Coverage report"
        fi
        if [[ -d "dist" ]]; then
            echo "   • dist/ - Built packages"
        fi
    else
        echo ""
        echo -e "${RED}🔧 Fix the failed checks above and re-run${NC}"
        
        if [[ "$VERBOSE_MODE" == "false" ]]; then
            echo ""
            echo "💡 For detailed error output, run with --verbose flag"
        fi
    fi
}

# Cleanup function
cleanup() {
    if [[ -f "test_output.log" ]] && [[ "$VERBOSE_MODE" == "false" ]]; then
        rm -f test_output.log
    fi
    if [[ -f "perf_output.log" ]] && [[ "$VERBOSE_MODE" == "false" ]]; then
        rm -f perf_output.log
    fi
}

# Main execution
main() {
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        echo -e "${PURPLE}🧪 mypylogger Complete Test Suite Runner${NC}"
        echo -e "${PURPLE}=======================================${NC}"
    else
        echo -e "${CYAN}🧪 Running test suite...${NC}"
    fi
    
    # Always setup environment and check prerequisites
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        setup_environment
        check_prerequisites
    else
        # Silent setup for summary mode
        setup_environment >/dev/null 2>&1
        check_prerequisites >/dev/null 2>&1
    fi
    
    # Track overall success
    local overall_success=true
    
    # Run checks based on mode
    if [[ -n "$SUBSET_MODE" ]]; then
        case "$SUBSET_MODE" in
            "quality")
                run_quality_checks || overall_success=false
                ;;
            "tests")
                run_tests || overall_success=false
                ;;
            "security")
                # Run only security-related checks
                run_command "bandit -r mypylogger/ -f txt" "Security scan" "security_scan" || overall_success=false
                run_command "safety check" "Dependency vulnerability scan" "vulnerability_scan" || overall_success=false
                ;;
            "build")
                verify_package_build || overall_success=false
                ;;
            "docs")
                verify_documentation || overall_success=false
                ;;
            *)
                echo "Unknown subset: $SUBSET_MODE"
                echo "Valid subsets: quality, tests, security, build, docs"
                exit 1
                ;;
        esac
    else
        # Run complete test suite
        run_quality_checks || overall_success=false
        run_tests || overall_success=false
        run_performance_tests || overall_success=false
        verify_package_build || overall_success=false
        verify_documentation || overall_success=false
    fi
    
    # Generate report
    generate_report
    
    # Cleanup
    cleanup
    
    # Exit with appropriate code
    if [[ "$overall_success" == "true" ]]; then
        exit 0
    else
        exit 1
    fi
}

# Error handling
trap 'echo -e "\n${RED}Test suite interrupted!${NC}"; cleanup; exit 1' INT TERM

# Run main function
main "$@"
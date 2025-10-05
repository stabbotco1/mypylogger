#!/bin/bash

# Environment Setup Improvement - Core Environment Detection Script
# This script implements progressive virtual environment detection and auto-setup
# Requirements: 1.1, 1.2, 2.1, 2.2

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_info() {
    print_status "$BLUE" "ℹ️  $1"
}

print_success() {
    print_status "$GREEN" "✅ $1"
}

print_warning() {
    print_status "$YELLOW" "⚠️  $1"
}

print_error() {
    print_status "$RED" "❌ $1"
}

# Function to check if we're in a virtual environment
check_virtual_env_active() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        return 0  # Virtual environment is active
    else
        return 1  # No virtual environment active
    fi
}

# Function to validate that the active venv is the project's venv
validate_project_venv() {
    local expected_venv_path="$PROJECT_ROOT/venv"
    
    if [[ -n "$VIRTUAL_ENV" ]]; then
        # Resolve both paths to handle symlinks and relative paths
        local active_venv=$(realpath "$VIRTUAL_ENV" 2>/dev/null || echo "$VIRTUAL_ENV")
        local expected_venv=$(realpath "$expected_venv_path" 2>/dev/null || echo "$expected_venv_path")
        
        if [[ "$active_venv" == "$expected_venv" ]]; then
            return 0  # Correct project venv is active
        else
            return 1  # Wrong venv is active
        fi
    else
        return 1  # No venv active
    fi
}

# Function to check if venv directory exists
check_venv_directory_exists() {
    if [[ -d "$PROJECT_ROOT/venv" ]]; then
        return 0  # venv directory exists
    else
        return 1  # venv directory does not exist
    fi
}

# Function to validate venv directory structure
validate_venv_structure() {
    local venv_path="$PROJECT_ROOT/venv"
    
    if [[ ! -d "$venv_path" ]]; then
        return 1  # Directory doesn't exist
    fi
    
    # Check for essential venv structure
    if [[ -f "$venv_path/bin/activate" ]] || [[ -f "$venv_path/Scripts/activate" ]]; then
        return 0  # Valid venv structure
    else
        return 1  # Invalid or corrupted venv
    fi
}

# Function to get current environment status
get_environment_status() {
    local status="unknown"
    local message=""
    
    if check_virtual_env_active && validate_project_venv; then
        status="active_correct"
        message="Project virtual environment is active and correct"
    elif check_virtual_env_active && ! validate_project_venv; then
        status="active_wrong"
        message="Wrong virtual environment is active (expected: $PROJECT_ROOT/venv, active: $VIRTUAL_ENV)"
    elif ! check_virtual_env_active && check_venv_directory_exists && validate_venv_structure; then
        status="exists_inactive"
        message="Project venv exists but is not activated"
    elif ! check_virtual_env_active && check_venv_directory_exists && ! validate_venv_structure; then
        status="exists_corrupted"
        message="Project venv directory exists but appears corrupted"
    elif ! check_virtual_env_active && ! check_venv_directory_exists; then
        status="missing"
        message="No virtual environment found"
    else
        status="unknown"
        message="Unable to determine environment status"
    fi
    
    echo "$status|$message"
}

# Function to display environment status
display_environment_status() {
    local status_info=$(get_environment_status)
    local status=$(echo "$status_info" | cut -d'|' -f1)
    local message=$(echo "$status_info" | cut -d'|' -f2)
    
    print_info "Environment Status Check"
    print_info "Project Root: $PROJECT_ROOT"
    print_info "Expected venv: $PROJECT_ROOT/venv"
    
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_info "Active venv: $VIRTUAL_ENV"
    else
        print_info "Active venv: None"
    fi
    
    echo
    
    case "$status" in
        "active_correct")
            print_success "$message"
            return 0
            ;;
        "active_wrong")
            print_warning "$message"
            print_warning "Please deactivate current venv and activate project venv:"
            print_warning "  deactivate"
            print_warning "  source $PROJECT_ROOT/venv/bin/activate"
            return 1
            ;;
        "exists_inactive")
            print_warning "$message"
            print_warning "To activate: source $PROJECT_ROOT/venv/bin/activate"
            return 1
            ;;
        "exists_corrupted")
            print_error "$message"
            print_error "Please remove and recreate the virtual environment:"
            print_error "  rm -rf $PROJECT_ROOT/venv"
            print_error "  python -m venv $PROJECT_ROOT/venv"
            print_error "  source $PROJECT_ROOT/venv/bin/activate"
            print_error "  pip install -e \".[dev]\""
            return 1
            ;;
        "missing")
            print_error "$message"
            print_error "Please create and activate a virtual environment:"
            print_error "  python -m venv $PROJECT_ROOT/venv"
            print_error "  source $PROJECT_ROOT/venv/bin/activate"
            print_error "  pip install -e \".[dev]\""
            return 1
            ;;
        *)
            print_error "$message"
            return 1
            ;;
    esac
}

# Function to validate Python availability
validate_python_availability() {
    local python_cmd=""
    
    # Try different Python commands in order of preference
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            # Check if it's Python 3.8+
            local version_output=$("$cmd" --version 2>&1)
            local version=$(echo "$version_output" | grep -oE '[0-9]+\.[0-9]+' | head -1)
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)
            
            if [[ "$major" -eq 3 ]] && [[ "$minor" -ge 8 ]]; then
                python_cmd="$cmd"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        return 1  # No suitable Python found
    else
        echo "$python_cmd"
        return 0  # Suitable Python found
    fi
}

# Function to get activation script path
get_activation_script_path() {
    local venv_path="$PROJECT_ROOT/venv"
    
    # Check for Unix-style activation script
    if [[ -f "$venv_path/bin/activate" ]]; then
        echo "$venv_path/bin/activate"
        return 0
    fi
    
    # Check for Windows-style activation script
    if [[ -f "$venv_path/Scripts/activate" ]]; then
        echo "$venv_path/Scripts/activate"
        return 0
    fi
    
    return 1  # No activation script found
}

# Function to activate virtual environment
activate_virtual_environment() {
    local venv_path="$PROJECT_ROOT/venv"
    
    # Check if already activated correctly
    if check_virtual_env_active && validate_project_venv; then
        print_success "Virtual environment is already active and correct"
        return 0
    fi
    
    # Validate venv structure first
    if ! validate_venv_structure; then
        print_error "Cannot activate: Virtual environment structure is invalid"
        print_error "Please recreate the virtual environment:"
        print_error "  rm -rf $venv_path"
        print_error "  python -m venv $venv_path"
        return 1
    fi
    
    # Get activation script path
    local activate_script
    activate_script=$(get_activation_script_path)
    local activate_result=$?
    
    if [[ $activate_result -ne 0 ]]; then
        print_error "Cannot find activation script in virtual environment"
        print_error "Expected locations:"
        print_error "  - $venv_path/bin/activate (Unix/Linux/macOS)"
        print_error "  - $venv_path/Scripts/activate (Windows)"
        print_error ""
        print_error "Please recreate the virtual environment:"
        print_error "  rm -rf $venv_path"
        print_error "  python -m venv $venv_path"
        return 1
    fi
    
    print_info "Activating virtual environment..."
    print_info "Activation script: $activate_script"
    
    # Note: We cannot actually activate the venv in this script context
    # because it would only affect this script's subshell, not the parent shell
    # Instead, we provide clear instructions to the user
    
    if [[ -n "$VIRTUAL_ENV" ]] && ! validate_project_venv; then
        print_warning "Wrong virtual environment is currently active"
        print_warning "Current: $VIRTUAL_ENV"
        print_warning "Expected: $venv_path"
        print_warning ""
        print_warning "Please deactivate current environment first:"
        print_warning "  deactivate"
        print_warning ""
    fi
    
    print_success "Virtual environment is ready for activation"
    print_info "To activate, run:"
    print_info "  source $activate_script"
    
    return 0
}

# Function to get pip executable path
get_pip_executable() {
    local venv_path="$PROJECT_ROOT/venv"
    
    # Check for Unix-style pip
    if [[ -f "$venv_path/bin/pip" ]]; then
        echo "$venv_path/bin/pip"
        return 0
    fi
    
    # Check for Windows-style pip
    if [[ -f "$venv_path/Scripts/pip.exe" ]]; then
        echo "$venv_path/Scripts/pip.exe"
        return 0
    fi
    
    return 1  # No pip executable found
}

# Function to install dependencies
install_dependencies() {
    local venv_path="$PROJECT_ROOT/venv"
    
    print_info "Installing dependencies..."
    
    # Validate venv structure first
    if ! validate_venv_structure; then
        print_error "Cannot install dependencies: Virtual environment is invalid"
        return 1
    fi
    
    # Get pip executable
    local pip_cmd
    pip_cmd=$(get_pip_executable)
    local pip_result=$?
    
    if [[ $pip_result -ne 0 ]]; then
        print_error "Cannot find pip executable in virtual environment"
        print_error "Expected locations:"
        print_error "  - $venv_path/bin/pip (Unix/Linux/macOS)"
        print_error "  - $venv_path/Scripts/pip.exe (Windows)"
        return 1
    fi
    
    print_info "Using pip: $pip_cmd"
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    if ! "$pip_cmd" install --upgrade pip; then
        print_warning "Failed to upgrade pip, continuing with current version"
    fi
    
    # Check for project configuration files
    local install_target=""
    if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        install_target="$PROJECT_ROOT"
        print_info "Found pyproject.toml, installing project in development mode"
    elif [[ -f "$PROJECT_ROOT/setup.py" ]]; then
        install_target="$PROJECT_ROOT"
        print_info "Found setup.py, installing project in development mode"
    else
        print_error "No pyproject.toml or setup.py found"
        print_error "Cannot install project dependencies"
        return 1
    fi
    
    # Install development dependencies
    print_info "Installing development dependencies..."
    print_info "Running: $pip_cmd install -e \".[dev]\""
    
    if ! "$pip_cmd" install -e ".[dev]"; then
        print_error "Failed to install development dependencies"
        print_error ""
        print_error "Common causes and solutions:"
        print_error "  1. Network connectivity issues - Check internet connection"
        print_error "  2. PyPI server issues - Try again later"
        print_error "  3. Package conflicts - Check pyproject.toml dependencies"
        print_error "  4. Insufficient disk space - Free up space and try again"
        print_error ""
        print_error "Manual installation command:"
        print_error "  source $venv_path/bin/activate"
        print_error "  pip install -e \".[dev]\""
        return 1
    fi
    
    print_success "Dependencies installed successfully"
    return 0
}

# Function to install pre-commit hooks
install_precommit_hooks() {
    local venv_path="$PROJECT_ROOT/venv"
    
    print_info "Installing pre-commit hooks..."
    
    # Check if pre-commit config exists
    if [[ ! -f "$PROJECT_ROOT/.pre-commit-config.yaml" ]]; then
        print_warning "No .pre-commit-config.yaml found, skipping pre-commit setup"
        return 0
    fi
    
    # Get pip executable to check if pre-commit is installed
    local pip_cmd
    pip_cmd=$(get_pip_executable)
    local pip_result=$?
    
    if [[ $pip_result -ne 0 ]]; then
        print_error "Cannot find pip executable for pre-commit installation"
        return 1
    fi
    
    # Check if pre-commit is available
    local precommit_cmd=""
    if [[ -f "$venv_path/bin/pre-commit" ]]; then
        precommit_cmd="$venv_path/bin/pre-commit"
    elif [[ -f "$venv_path/Scripts/pre-commit.exe" ]]; then
        precommit_cmd="$venv_path/Scripts/pre-commit.exe"
    else
        print_warning "pre-commit not found in virtual environment"
        print_warning "It should have been installed with development dependencies"
        print_warning "Skipping pre-commit hook installation"
        return 0
    fi
    
    print_info "Using pre-commit: $precommit_cmd"
    print_info "Installing pre-commit hooks..."
    
    # Change to project directory for pre-commit install
    if ! (cd "$PROJECT_ROOT" && "$precommit_cmd" install); then
        print_error "Failed to install pre-commit hooks"
        print_error ""
        print_error "Common causes and solutions:"
        print_error "  1. Git repository not initialized - Run 'git init' first"
        print_error "  2. Permission issues - Check write permissions to .git/hooks/"
        print_error "  3. pre-commit configuration issues - Check .pre-commit-config.yaml"
        print_error ""
        print_error "Manual installation command:"
        print_error "  source $venv_path/bin/activate"
        print_error "  pre-commit install"
        return 1
    fi
    
    print_success "Pre-commit hooks installed successfully"
    return 0
}

# Function to create virtual environment
create_virtual_environment() {
    local venv_path="$PROJECT_ROOT/venv"
    
    print_info "Creating virtual environment..."
    
    # Validate Python availability
    local python_cmd
    python_cmd=$(validate_python_availability)
    local python_check_result=$?
    
    if [[ $python_check_result -ne 0 ]]; then
        print_error "No suitable Python installation found"
        print_error "Requirements: Python 3.8 or higher"
        print_error ""
        print_error "Please install Python 3.8+ and try again:"
        print_error "  - macOS: brew install python@3.11"
        print_error "  - Ubuntu: sudo apt install python3.11 python3.11-venv"
        print_error "  - Windows: Download from https://python.org"
        return 1
    fi
    
    print_info "Using Python: $python_cmd ($($python_cmd --version))"
    
    # Remove existing venv if corrupted
    if [[ -d "$venv_path" ]] && ! validate_venv_structure; then
        print_warning "Removing corrupted virtual environment..."
        rm -rf "$venv_path"
    fi
    
    # Create the virtual environment
    print_info "Running: $python_cmd -m venv $venv_path"
    
    if ! "$python_cmd" -m venv "$venv_path"; then
        print_error "Failed to create virtual environment"
        print_error ""
        print_error "Common causes and solutions:"
        print_error "  1. Insufficient disk space - Free up space and try again"
        print_error "  2. Permission issues - Check write permissions to project directory"
        print_error "  3. Python venv module missing - Install with: sudo apt install python3-venv"
        print_error "  4. Antivirus interference - Temporarily disable and retry"
        print_error ""
        print_error "Manual creation command:"
        print_error "  $python_cmd -m venv $venv_path"
        return 1
    fi
    
    # Validate the created environment
    if ! validate_venv_structure; then
        print_error "Virtual environment created but appears invalid"
        print_error "Please try manual creation:"
        print_error "  rm -rf $venv_path"
        print_error "  $python_cmd -m venv $venv_path"
        return 1
    fi
    
    print_success "Virtual environment created successfully at: $venv_path"
    return 0
}

# Function to show usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Environment Detection Script for mypylogger project"
    echo
    echo "OPTIONS:"
    echo "  --status, -s     Show current environment status"
    echo "  --check, -c      Check environment and exit with status code"
    echo "  --create         Create virtual environment if missing"
    echo "  --activate       Prepare virtual environment for activation"
    echo "  --install-deps   Install development dependencies and pre-commit hooks"
    echo "  --auto-setup     Complete setup (create + activate + install-deps)"
    echo "  --quiet, -q      Quiet mode (minimal output)"
    echo "  --help, -h       Show this help message"
    echo
    echo "EXIT CODES:"
    echo "  0    Environment is correctly configured"
    echo "  1    Environment needs attention"
    echo "  2    Invalid arguments or script error"
}

# Main function
main() {
    local quiet_mode=false
    local check_only=false
    local create_mode=false
    local activate_mode=false
    local install_deps_mode=false
    local auto_setup_mode=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status|-s)
                # Default behavior, just show status
                shift
                ;;
            --check|-c)
                check_only=true
                shift
                ;;
            --create)
                create_mode=true
                shift
                ;;
            --activate)
                activate_mode=true
                shift
                ;;
            --install-deps)
                install_deps_mode=true
                shift
                ;;
            --auto-setup)
                auto_setup_mode=true
                shift
                ;;
            --quiet|-q)
                quiet_mode=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 2
                ;;
        esac
    done
    
    # Validate project path
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]] && [[ ! -f "$PROJECT_ROOT/setup.py" ]]; then
        print_error "Not in a Python project directory (no pyproject.toml or setup.py found)"
        print_error "Expected project root: $PROJECT_ROOT"
        exit 2
    fi
    
    # Handle auto-setup mode (create + activate + install-deps)
    if [[ "$auto_setup_mode" == "true" ]]; then
        local status_info=$(get_environment_status)
        local status=$(echo "$status_info" | cut -d'|' -f1)
        
        case "$status" in
            "active_correct")
                print_success "Virtual environment is already correctly configured"
                # Still install dependencies in case they're missing
                if install_dependencies && install_precommit_hooks; then
                    print_success "Dependencies and pre-commit hooks verified"
                    exit 0
                else
                    print_error "Failed to install dependencies or pre-commit hooks"
                    exit 1
                fi
                ;;
            "missing"|"exists_corrupted")
                if create_virtual_environment && activate_virtual_environment && install_dependencies && install_precommit_hooks; then
                    print_success "Complete virtual environment setup completed"
                    exit 0
                else
                    print_error "Failed to complete virtual environment setup"
                    exit 1
                fi
                ;;
            "exists_inactive")
                if activate_virtual_environment && install_dependencies && install_precommit_hooks; then
                    print_success "Virtual environment setup completed"
                    exit 0
                else
                    print_error "Failed to complete virtual environment setup"
                    exit 1
                fi
                ;;
            *)
                print_warning "Virtual environment exists but has issues"
                display_environment_status >/dev/null
                exit 1
                ;;
        esac
    fi
    
    # Handle create mode
    if [[ "$create_mode" == "true" ]]; then
        local status_info=$(get_environment_status)
        local status=$(echo "$status_info" | cut -d'|' -f1)
        
        case "$status" in
            "active_correct")
                print_success "Virtual environment is already correctly configured"
                exit 0
                ;;
            "missing"|"exists_corrupted")
                if create_virtual_environment; then
                    print_success "Virtual environment created successfully"
                    print_info "To activate: source $PROJECT_ROOT/venv/bin/activate"
                    exit 0
                else
                    print_error "Failed to create virtual environment"
                    exit 1
                fi
                ;;
            *)
                print_warning "Virtual environment exists but has issues"
                display_environment_status >/dev/null
                exit 1
                ;;
        esac
    fi
    
    # Handle activate mode
    if [[ "$activate_mode" == "true" ]]; then
        local status_info=$(get_environment_status)
        local status=$(echo "$status_info" | cut -d'|' -f1)
        
        case "$status" in
            "active_correct")
                print_success "Virtual environment is already correctly activated"
                exit 0
                ;;
            "exists_inactive"|"active_wrong")
                if activate_virtual_environment; then
                    print_success "Virtual environment prepared for activation"
                    exit 0
                else
                    print_error "Failed to prepare virtual environment for activation"
                    exit 1
                fi
                ;;
            "missing")
                print_error "No virtual environment found to activate"
                print_error "Create one first with: $0 --create"
                exit 1
                ;;
            "exists_corrupted")
                print_error "Virtual environment is corrupted and cannot be activated"
                print_error "Recreate it with: $0 --create"
                exit 1
                ;;
            *)
                print_error "Cannot determine environment status for activation"
                exit 1
                ;;
        esac
    fi
    
    # Handle install-deps mode
    if [[ "$install_deps_mode" == "true" ]]; then
        local status_info=$(get_environment_status)
        local status=$(echo "$status_info" | cut -d'|' -f1)
        
        case "$status" in
            "active_correct"|"exists_inactive")
                if install_dependencies && install_precommit_hooks; then
                    print_success "Dependencies and pre-commit hooks installed successfully"
                    exit 0
                else
                    print_error "Failed to install dependencies or pre-commit hooks"
                    exit 1
                fi
                ;;
            "missing")
                print_error "No virtual environment found for dependency installation"
                print_error "Create one first with: $0 --create"
                exit 1
                ;;
            "exists_corrupted")
                print_error "Virtual environment is corrupted, cannot install dependencies"
                print_error "Recreate it with: $0 --create"
                exit 1
                ;;
            "active_wrong")
                print_error "Wrong virtual environment is active"
                print_error "Please activate the correct environment first"
                exit 1
                ;;
            *)
                print_error "Cannot determine environment status for dependency installation"
                exit 1
                ;;
        esac
    fi
    
    # Check environment status
    if [[ "$quiet_mode" == "false" ]]; then
        display_environment_status
        exit_code=$?
    else
        # Quiet mode - just check status
        local status_info=$(get_environment_status)
        local status=$(echo "$status_info" | cut -d'|' -f1)
        
        if [[ "$status" == "active_correct" ]]; then
            exit_code=0
        else
            exit_code=1
        fi
        
        if [[ "$check_only" == "false" ]]; then
            local message=$(echo "$status_info" | cut -d'|' -f2)
            echo "$message"
        fi
    fi
    
    exit $exit_code
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
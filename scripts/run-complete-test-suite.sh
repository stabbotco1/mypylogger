#!/bin/bash
# Complete Test Suite Runner for mypylogger
# 
# This is a simple wrapper around the Python implementation for better
# structured error handling and reporting.
#
# Usage: ./scripts/run-complete-test-suite.sh [OPTIONS]
#
# All options are passed through to the Python implementation.

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Auto-detect and activate virtual environment if needed
if [[ -z "$VIRTUAL_ENV" ]]; then
    # Try common virtual environment locations
    local venv_paths=("$PROJECT_ROOT/venv/bin/activate" "$PROJECT_ROOT/.venv/bin/activate" "$PROJECT_ROOT/env/bin/activate")
    
    for venv_path in "${venv_paths[@]}"; do
        if [[ -f "$venv_path" ]]; then
            source "$venv_path"
            break
        fi
    done
fi

# Execute the Python implementation with all arguments passed through
exec python "$SCRIPT_DIR/run_complete_test_suite.py" "$@"


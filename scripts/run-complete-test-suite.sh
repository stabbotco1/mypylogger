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

# Fail-fast if not in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ ERROR: Not running in a virtual environment"
    echo ""
    echo "🔧 To fix this issue:"
    echo "   1. Create virtual environment: python -m venv venv"
    echo "   2. Activate it: source venv/bin/activate"
    echo "   3. Install dependencies: pip install -e \".[dev]\""
    echo "   4. Re-run this command"
    echo ""
    echo "💡 Or use the setup script: ./scripts/setup-dev.sh"
    exit 1
fi

# Execute the Python implementation with all arguments passed through
exec python "$SCRIPT_DIR/run_complete_test_suite.py" "$@"

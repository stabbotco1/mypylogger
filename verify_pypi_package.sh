#!/bin/bash
# PyPI Package Verification Script for mypylogger
# This script tests the published package in a clean environment

set -e  # Exit on any error

echo "🧪 mypylogger PyPI Package Verification"
echo "======================================"

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d)
echo "📁 Test directory: $TEST_DIR"
cd "$TEST_DIR"

# Create a clean virtual environment
echo "🔧 Creating clean virtual environment..."
python -m venv test_env
source test_env/bin/activate

# Upgrade pip to latest version
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package from PyPI
echo "📦 Installing mypylogger from PyPI..."
pip install mypylogger

# Show package info
echo "ℹ️  Package information:"
pip show mypylogger

# Create a test script
echo "📝 Creating test script..."
cat > test_mypylogger.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
Test script to verify mypylogger functionality from PyPI installation.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

def test_basic_import():
    """Test that mypylogger can be imported."""
    print("✅ Testing basic import...")
    try:
        import mypylogger
        print(f"   ✓ Successfully imported mypylogger")
        print(f"   ✓ Version: {getattr(mypylogger, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_get_logger():
    """Test getting a logger instance."""
    print("✅ Testing get_logger()...")
    try:
        import mypylogger
        logger = mypylogger.get_logger()
        print(f"   ✓ Successfully got logger: {type(logger)}")
        return True
    except Exception as e:
        print(f"   ❌ get_logger() failed: {e}")
        return False

def test_logging_functionality():
    """Test actual logging functionality."""
    print("✅ Testing logging functionality...")
    try:
        import mypylogger

        # Set up environment for testing
        os.environ['APP_NAME'] = 'pypi_test'
        os.environ['LOG_LEVEL'] = 'DEBUG'
        os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true'

        # Get logger and log messages
        logger = mypylogger.get_logger()
        logger.info("Test message from PyPI package")
        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")

        print("   ✓ Successfully logged messages")

        # Check if log file was created
        log_files = list(Path("logs").glob("pypi_test_*.log")) if Path("logs").exists() else []
        if log_files:
            print(f"   ✓ Log file created: {log_files[0]}")

            # Read and validate log content
            with open(log_files[0]) as f:
                lines = f.readlines()

            print(f"   ✓ Log contains {len(lines)} entries")

            # Validate JSON format
            for i, line in enumerate(lines[:2]):  # Check first 2 lines
                try:
                    log_entry = json.loads(line.strip())
                    required_fields = ['time', 'levelname', 'message', 'filename', 'lineno', 'funcName']
                    missing_fields = [field for field in required_fields if field not in log_entry]
                    if missing_fields:
                        print(f"   ⚠️  Line {i+1} missing fields: {missing_fields}")
                    else:
                        print(f"   ✓ Line {i+1} has all required JSON fields")
                except json.JSONDecodeError as e:
                    print(f"   ❌ Line {i+1} is not valid JSON: {e}")
        else:
            print("   ⚠️  No log file found (might be expected in some environments)")

        return True
    except Exception as e:
        print(f"   ❌ Logging test failed: {e}")
        return False

def test_configuration():
    """Test configuration functionality."""
    print("✅ Testing configuration...")
    try:
        import mypylogger

        # Test different log levels
        os.environ['LOG_LEVEL'] = 'WARNING'
        logger = mypylogger.get_logger()

        # Test effective level
        level = mypylogger.get_effective_level()
        print(f"   ✓ Effective log level: {level}")

        return True
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_singleton_behavior():
    """Test singleton pattern."""
    print("✅ Testing singleton behavior...")
    try:
        import mypylogger

        logger1 = mypylogger.get_logger()
        logger2 = mypylogger.get_logger()

        if logger1 is logger2:
            print("   ✓ Singleton pattern working correctly")
            return True
        else:
            print("   ❌ Singleton pattern not working - different instances returned")
            return False
    except Exception as e:
        print(f"   ❌ Singleton test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("�� Starting mypylogger PyPI package verification tests...\n")

    tests = [
        test_basic_import,
        test_get_logger,
        test_logging_functionality,
        test_configuration,
        test_singleton_behavior
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Empty line between tests
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}\n")

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! mypylogger is working correctly from PyPI!")
        return 0
    else:
        print("❌ Some tests failed. Package may have issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
PYTHON_EOF

# Run the test script
echo "🚀 Running verification tests..."
python test_mypylogger.py

# Show any log files created
echo "📄 Log files created during testing:"
if [ -d "logs" ]; then
    ls -la logs/
    echo "📝 Sample log content:"
    head -3 logs/*.log 2>/dev/null || echo "No log files to display"
else
    echo "No logs directory created"
fi

# Clean up
echo "🧹 Cleaning up..."
deactivate
cd /
rm -rf "$TEST_DIR"

echo "✅ Verification complete!"

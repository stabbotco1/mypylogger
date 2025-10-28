#!/usr/bin/env python3
"""Minimal test of mypylogger from PyPI - 5 lines of code"""

import mypylogger

# Test 1: Get logger and log a message
logger = mypylogger.get_logger("test_app")
logger.info("Hello from PyPI package!", extra={"test": True})

print("✅ mypylogger PyPI package works!")
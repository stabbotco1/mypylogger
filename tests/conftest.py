"""Shared test fixtures and configuration for mypylogger tests."""

import os
from pathlib import Path
import tempfile
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Clean environment variables before and after test."""
    # Store original environment
    original_env = dict(os.environ)

    # Clear mypylogger-related environment variables
    env_vars_to_clear = [
        "APP_NAME",
        "LOG_LEVEL",
        "LOG_TO_FILE",
        "LOG_FILE_DIR",
        "LOG_FILE_NAME",
        "LOG_IMMEDIATE_FLUSH",
    ]

    for var in env_vars_to_clear:
        os.environ.pop(var, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_log_data() -> dict:
    """Sample log data for testing."""
    return {
        "message": "Test log message",
        "level": "INFO",
        "extra_field": "extra_value",
    }

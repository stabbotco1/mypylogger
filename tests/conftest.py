"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files during testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def clean_environment():
    """Clean environment variables before and after tests."""
    # Store original values
    original_env = {}
    env_vars = ['APP_NAME', 'LOG_LEVEL', 'EMPTY_LOG_FILE_ON_RUN', 'PARALLEL_STDOUT_LOGGING']
    
    for var in env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
        if var in original_env:
            os.environ[var] = original_env[var]


@pytest.fixture
def mock_logger_instance():
    """Reset singleton instance for testing."""
    from mypylogger.core import SingletonLogger
    
    # Store original instance
    original_instance = SingletonLogger._instance
    original_logger = SingletonLogger._logger
    
    # Reset for test
    SingletonLogger._instance = None
    SingletonLogger._logger = None
    
    yield
    
    # Restore original state
    SingletonLogger._instance = original_instance
    SingletonLogger._logger = original_logger
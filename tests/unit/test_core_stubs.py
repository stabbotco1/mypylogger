"""
Unit tests for core module stubs.
"""
import pytest
import logging
from mypylogger.core import SingletonLogger


class TestSingletonLoggerStubs:
    """Test the stub implementations in core module."""
    
    def test_get_logger_stub_returns_logger(self):
        """Test that the stub get_logger returns a logger instance."""
        logger = SingletonLogger.get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "stub"
    
    def test_get_effective_level_stub_returns_info(self):
        """Test that the stub get_effective_level returns INFO level."""
        level = SingletonLogger.get_effective_level()
        assert level == logging.INFO
    
    def test_singleton_instance_creation(self):
        """Test that singleton instance is created properly."""
        instance1 = SingletonLogger()
        instance2 = SingletonLogger()
        assert instance1 is instance2
        assert isinstance(instance1, SingletonLogger)
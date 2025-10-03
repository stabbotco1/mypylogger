"""
Unit tests for core module stubs.
"""

import logging

from mypylogger.core import SingletonLogger


class TestSingletonLoggerStubs:
    """Test the stub implementations in core module."""

    def test_get_logger_returns_configured_logger(
        self, mock_logger_instance, clean_environment
    ):
        """Test that get_logger returns a properly configured logger instance."""
        logger = SingletonLogger.get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "default_app"  # Default app name from config

    def test_get_effective_level_returns_configured_level(
        self, mock_logger_instance, clean_environment
    ):
        """Test that get_effective_level returns the configured level."""
        level = SingletonLogger.get_effective_level()
        assert level == logging.INFO  # Default level from config

    def test_singleton_instance_creation(self, mock_logger_instance):
        """Test that singleton instance is created properly."""
        instance1 = SingletonLogger()
        instance2 = SingletonLogger()
        assert instance1 is instance2
        assert isinstance(instance1, SingletonLogger)

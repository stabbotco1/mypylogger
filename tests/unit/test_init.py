"""
Tests for mypylogger package initialization and public API.
"""

import logging

import mypylogger


class TestPublicAPI:
    """Test the public API functions and constants."""

    def test_get_logger_function(self):
        """Test that get_logger() returns a logger instance."""
        logger = mypylogger.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_effective_level_function(self):
        """Test that get_effective_level() returns an integer."""
        level = mypylogger.get_effective_level()
        assert isinstance(level, int)
        assert level >= 0

    def test_logging_constants_exist(self):
        """Test that logging level constants are available."""
        assert hasattr(mypylogger, "DEBUG")
        assert hasattr(mypylogger, "INFO")
        assert hasattr(mypylogger, "WARNING")
        assert hasattr(mypylogger, "ERROR")
        assert hasattr(mypylogger, "CRITICAL")

    def test_logging_constants_values(self):
        """Test that logging constants have correct values."""
        assert mypylogger.DEBUG == 10
        assert mypylogger.INFO == 20
        assert mypylogger.WARNING == 30
        assert mypylogger.ERROR == 40
        assert mypylogger.CRITICAL == 50

    def test_package_metadata(self):
        """Test package metadata is available."""
        assert hasattr(mypylogger, "__version__")
        assert hasattr(mypylogger, "__author__")
        assert isinstance(mypylogger.__version__, str)
        assert isinstance(mypylogger.__author__, str)

    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        expected_exports = [
            "get_logger",
            "get_effective_level",
            "SingletonLogger",
            "LogConfig",
            "CustomJsonFormatter",
            "ImmediateFlushFileHandler",
            "ParallelStdoutHandler",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

        for export in expected_exports:
            assert export in mypylogger.__all__
            assert hasattr(mypylogger, export)

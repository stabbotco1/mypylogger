"""
Tests for error conditions and exception handling in mypylogger.
"""

from unittest.mock import patch

import pytest

from mypylogger.core import SingletonLogger


class TestErrorConditions:
    """Test error handling and graceful degradation."""

    def test_logger_initialization_failure(self):
        """Test RuntimeError when logger initialization fails."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Mock the _initialize_logger to do nothing (simulate failure)
        with patch.object(SingletonLogger, "_initialize_logger") as mock_init:
            mock_init.return_value = None  # Simulate initialization failure

            with pytest.raises(RuntimeError, match="Logger initialization failed"):
                SingletonLogger.get_logger()

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None

    def test_stdout_handler_creation_failure(self):
        """Test graceful degradation when stdout handler creation fails."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Set environment to enable stdout logging
        with patch.dict("os.environ", {"PARALLEL_STDOUT_LOGGING": "INFO"}):
            # Mock ParallelStdoutHandler to raise an exception
            with patch(
                "mypylogger.handlers.ParallelStdoutHandler",
                side_effect=Exception("Stdout error"),
            ):
                # This should not raise an exception (graceful degradation)
                logger = SingletonLogger.get_logger()

                # Verify logger was still created
                assert logger is not None

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None


class TestImportErrorHandling:
    """Test handling of missing dependencies."""

    def test_missing_pythonjsonlogger_dependency(self):
        """Test that formatter works even without pythonjsonlogger."""
        # This test verifies the ImportError handling in formatters.py
        # The stub should be used when the real library is not available

        # We can't easily mock the import at module level, but we can test
        # that the formatter still works by importing it
        from mypylogger.formatters import CustomJsonFormatter

        # Create an instance - this should work even with stub
        formatter = CustomJsonFormatter()
        assert formatter is not None

        # Test that it can format a basic log record
        import logging

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # This should not raise an exception
        formatted = formatter.format(record)
        assert isinstance(formatted, str)
        assert "test message" in formatted


class TestConfigurationErrorHandling:
    """Test configuration error handling."""

    def test_invalid_log_level_handling(self):
        """Test handling of invalid log level values."""
        from mypylogger.config import LogConfig

        # Test with invalid log level - config stores the raw value
        with patch.dict("os.environ", {"LOG_LEVEL": "INVALID_LEVEL"}):
            config = LogConfig.from_environment()
            # Config stores the raw value, but get_log_level_int should handle it
            assert config.log_level == "INVALID_LEVEL"
            # The validation happens in get_log_level_int method
            level_int = config.get_log_level_int()
            assert level_int == 20  # Should default to INFO (20)

    def test_invalid_boolean_values(self):
        """Test handling of invalid boolean environment variables."""
        from mypylogger.config import LogConfig

        # Test with invalid boolean value
        with patch.dict("os.environ", {"EMPTY_LOG_FILE_ON_RUN": "maybe"}):
            config = LogConfig.from_environment()
            # Should default to False for invalid boolean
            assert config.empty_log_file_on_run is False

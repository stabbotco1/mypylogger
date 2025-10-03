"""
Tests for refactored error handling methods.
"""

from unittest.mock import patch

from mypylogger.core import SingletonLogger


class TestRefactoredErrorHandling:
    """Test the refactored error handling methods."""

    def test_handle_file_handler_error(self, capsys):
        """Test file handler error handling method."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        error = PermissionError("Permission denied")
        SingletonLogger._handle_file_handler_error(error)

        captured = capsys.readouterr()
        assert (
            "Warning: Failed to create file handler: Permission denied" in captured.err
        )

    def test_handle_stdout_handler_error(self, capsys):
        """Test stdout handler error handling method."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        error = OSError("Stdout unavailable")
        SingletonLogger._handle_stdout_handler_error(error)

        captured = capsys.readouterr()
        assert (
            "Warning: Failed to create stdout handler: Stdout unavailable"
            in captured.err
        )

    def test_add_file_handler_success(self):
        """Test successful file handler addition."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Initialize logger first
        logger = SingletonLogger.get_logger()

        # Clear existing handlers
        logger.handlers.clear()

        from mypylogger.formatters import CustomJsonFormatter

        formatter = CustomJsonFormatter()

        # This should succeed without errors
        SingletonLogger._add_file_handler(formatter)

        # Verify handler was added
        assert len(logger.handlers) > 0

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None

    def test_add_file_handler_failure(self, capsys):
        """Test file handler addition with failure."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Initialize logger first
        logger = SingletonLogger.get_logger()
        logger.handlers.clear()

        from mypylogger.formatters import CustomJsonFormatter

        formatter = CustomJsonFormatter()

        # Mock ImmediateFlushFileHandler to raise exception
        with patch(
            "mypylogger.handlers.ImmediateFlushFileHandler",
            side_effect=PermissionError("Access denied"),
        ):
            SingletonLogger._add_file_handler(formatter)

            # Should have printed error message
            captured = capsys.readouterr()
            assert (
                "Warning: Failed to create file handler: Access denied" in captured.err
            )

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None

    def test_add_stdout_handler_success(self):
        """Test successful stdout handler addition."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Set environment to enable stdout logging
        with patch.dict("os.environ", {"PARALLEL_STDOUT_LOGGING": "INFO"}):
            # Initialize logger and config
            logger = SingletonLogger.get_logger()
            logger.handlers.clear()

            # This should succeed
            SingletonLogger._add_stdout_handler()

            # Verify handler was added
            assert len(logger.handlers) > 0

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None

    def test_add_stdout_handler_disabled(self):
        """Test stdout handler when disabled."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        # Set environment to disable stdout logging
        with patch.dict("os.environ", {"PARALLEL_STDOUT_LOGGING": "false"}):
            # Initialize logger and config
            logger = SingletonLogger.get_logger()
            logger.handlers.clear()

            # This should not add handler
            SingletonLogger._add_stdout_handler()

            # Verify no handler was added
            assert len(logger.handlers) == 0

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None

    def test_add_stdout_handler_failure(self, capsys):
        """Test stdout handler addition with failure."""
        # Reset singleton state
        SingletonLogger._instance = None
        SingletonLogger._logger = None

        with patch.dict("os.environ", {"PARALLEL_STDOUT_LOGGING": "INFO"}):
            # Initialize logger and config
            logger = SingletonLogger.get_logger()
            logger.handlers.clear()

            # Mock ParallelStdoutHandler to raise exception
            with patch(
                "mypylogger.handlers.ParallelStdoutHandler",
                side_effect=OSError("Stdout error"),
            ):
                SingletonLogger._add_stdout_handler()

                # Should have printed error message
                captured = capsys.readouterr()
                assert (
                    "Warning: Failed to create stdout handler: Stdout error"
                    in captured.err
                )

        # Clean up
        SingletonLogger._instance = None
        SingletonLogger._logger = None


class TestFallbackJsonLogger:
    """Test the fallback JSON logger implementation."""

    def test_create_fallback_jsonlogger(self):
        """Test fallback JSON logger creation."""
        from mypylogger.formatters import _create_fallback_jsonlogger

        fallback = _create_fallback_jsonlogger()
        assert hasattr(fallback, "JsonFormatter")

        # Test that we can create an instance
        formatter = fallback.JsonFormatter()
        assert formatter is not None

    def test_fallback_formatter_functionality(self):
        """Test that fallback formatter works."""
        import logging

        from mypylogger.formatters import _create_fallback_jsonlogger

        fallback = _create_fallback_jsonlogger()
        formatter = fallback.JsonFormatter()

        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Should be able to format without error
        formatted = formatter.format(record)
        assert isinstance(formatted, str)
        assert "Test message" in formatted

    def test_import_fallback_integration(self):
        """Test that import fallback works in real usage."""
        # This test verifies the import mechanism works
        from mypylogger.formatters import CustomJsonFormatter

        # Should be able to create formatter regardless of import path
        formatter = CustomJsonFormatter()
        assert formatter is not None

"""
Tests for custom logging handlers.
"""
import os
import sys
import tempfile
import logging
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from mypylogger.handlers import ImmediateFlushFileHandler, ParallelStdoutHandler


class TestImmediateFlushFileHandler:
    """Tests for ImmediateFlushFileHandler."""
    
    def test_creates_log_directory_if_not_exists(self, tmp_path):
        """Test that handler creates log directory if it doesn't exist."""
        logs_dir = tmp_path / "logs"
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        # Ensure directory doesn't exist initially
        assert not logs_dir.exists()
        
        # Create handler - should create directory
        handler = ImmediateFlushFileHandler(str(log_file))
        
        # Directory should now exist
        assert logs_dir.exists()
        assert logs_dir.is_dir()
        
        handler.close()
    
    def test_log_file_naming_format(self, tmp_path):
        """Test that log files follow the {APP_NAME}_{YYYY_MM_DD}.log format."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        
        app_name = "test_app"
        date_str = "2024_01_15"
        expected_filename = f"{app_name}_{date_str}.log"
        log_file = logs_dir / expected_filename
        
        handler = ImmediateFlushFileHandler(str(log_file))
        
        # File should be created
        assert log_file.exists()
        assert log_file.name == expected_filename
        
        handler.close()
    
    def test_immediate_flush_behavior(self, tmp_path):
        """Test that logs are flushed immediately after writing."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        handler = ImmediateFlushFileHandler(str(log_file))
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Mock the flush method to verify it's called
        with patch.object(handler, 'flush') as mock_flush:
            handler.emit(record)
            # flush() should be called at least once (our implementation calls it explicitly)
            assert mock_flush.call_count >= 1
        
        handler.close()
    
    def test_file_truncation_when_empty_log_file_on_run_true(self, tmp_path):
        """Test that log file is truncated when empty_log_file_on_run is True."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        # Create file with existing content
        log_file.write_text("Existing log content\n")
        assert log_file.read_text() == "Existing log content\n"
        
        # Create handler with truncation mode
        handler = ImmediateFlushFileHandler(str(log_file), mode='w')
        
        # File should be empty after handler creation
        handler.close()
        assert log_file.read_text() == ""
    
    def test_file_append_when_empty_log_file_on_run_false(self, tmp_path):
        """Test that log file is appended to when empty_log_file_on_run is False."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        # Create file with existing content
        existing_content = "Existing log content\n"
        log_file.write_text(existing_content)
        
        # Create handler with append mode (default)
        handler = ImmediateFlushFileHandler(str(log_file), mode='a')
        
        # Add a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="New message",
            args=(),
            exc_info=None
        )
        
        handler.emit(record)
        handler.close()
        
        # File should contain both old and new content
        content = log_file.read_text()
        assert existing_content in content
        assert "New message" in content
    
    def test_real_time_visibility(self, tmp_path):
        """Test that logs are visible in real-time without waiting for program termination."""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        handler = ImmediateFlushFileHandler(str(log_file))
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Real-time test message",
            args=(),
            exc_info=None
        )
        
        # Emit the record
        handler.emit(record)
        
        # Content should be immediately available (without closing handler)
        content = log_file.read_text()
        assert "Real-time test message" in content
        
        handler.close()
    
    def test_creates_logs_directory_in_project_root(self, tmp_path, monkeypatch):
        """Test that handler creates /logs directory in project root."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)
        
        logs_dir = Path("logs")
        log_file = logs_dir / "test_app_2024_01_15.log"
        
        # Ensure directory doesn't exist initially
        assert not logs_dir.exists()
        
        # Create handler - should create logs directory in current (project) root
        handler = ImmediateFlushFileHandler(str(log_file))
        
        # Directory should be created in project root
        assert logs_dir.exists()
        assert logs_dir.is_dir()
        assert (tmp_path / "logs").exists()
        
        handler.close()


class TestParallelStdoutHandler:
    """Tests for ParallelStdoutHandler."""
    
    def test_handler_creation_with_default_level(self):
        """Test that ParallelStdoutHandler can be created with default level."""
        handler = ParallelStdoutHandler()
        assert handler.stdout_level == logging.INFO
        assert handler.stream == sys.stdout
        handler.close()
    
    def test_handler_creation_with_custom_level(self):
        """Test that ParallelStdoutHandler can be created with custom level."""
        handler = ParallelStdoutHandler(logging.WARNING)
        assert handler.stdout_level == logging.WARNING
        assert handler.stream == sys.stdout
        handler.close()
    
    def test_level_filtering_info_level(self, capsys):
        """Test that handler filters based on INFO level."""
        handler = ParallelStdoutHandler(logging.INFO)
        
        # Create records at different levels
        debug_record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="test.py", lineno=1,
            msg="Debug message", args=(), exc_info=None
        )
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=1,
            msg="Info message", args=(), exc_info=None
        )
        warning_record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py", lineno=1,
            msg="Warning message", args=(), exc_info=None
        )
        
        # Emit all records
        handler.emit(debug_record)
        handler.emit(info_record)
        handler.emit(warning_record)
        
        captured = capsys.readouterr()
        
        # Debug should be filtered out, info and warning should be output
        assert "Debug message" not in captured.out
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
        
        handler.close()
    
    def test_level_filtering_warning_level(self, capsys):
        """Test that handler filters based on WARNING level."""
        handler = ParallelStdoutHandler(logging.WARNING)
        
        # Create records at different levels
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=1,
            msg="Info message", args=(), exc_info=None
        )
        warning_record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py", lineno=1,
            msg="Warning message", args=(), exc_info=None
        )
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py", lineno=1,
            msg="Error message", args=(), exc_info=None
        )
        
        # Emit all records
        handler.emit(info_record)
        handler.emit(warning_record)
        handler.emit(error_record)
        
        captured = capsys.readouterr()
        
        # Only warning and error should be output (info filtered out)
        assert "Info message" not in captured.out
        assert "Warning message" in captured.out
        assert "Error message" in captured.out
        
        handler.close()
    
    def test_level_filtering_error_level(self, capsys):
        """Test that handler filters based on ERROR level."""
        handler = ParallelStdoutHandler(logging.ERROR)
        
        # Create records at different levels
        warning_record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py", lineno=1,
            msg="Warning message", args=(), exc_info=None
        )
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py", lineno=1,
            msg="Error message", args=(), exc_info=None
        )
        critical_record = logging.LogRecord(
            name="test", level=logging.CRITICAL, pathname="test.py", lineno=1,
            msg="Critical message", args=(), exc_info=None
        )
        
        # Emit all records
        handler.emit(warning_record)
        handler.emit(error_record)
        handler.emit(critical_record)
        
        captured = capsys.readouterr()
        
        # Only error and critical should be output (warning filtered out)
        assert "Warning message" not in captured.out
        assert "Error message" in captured.out
        assert "Critical message" in captured.out
        
        handler.close()
    
    def test_stdout_output_format(self, capsys):
        """Test that stdout output is properly formatted."""
        handler = ParallelStdoutHandler(logging.INFO)
        
        # Set a formatter to test formatting
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        
        # Create a log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=42,
            msg="Test message", args=(), exc_info=None
        )
        
        # Emit the record
        handler.emit(record)
        
        captured = capsys.readouterr()
        
        # Should contain formatted output
        assert "INFO: Test message" in captured.out
        
        handler.close()
    
    def test_multiple_records_output(self, capsys):
        """Test that multiple records are output correctly."""
        handler = ParallelStdoutHandler(logging.INFO)
        
        # Create multiple log records
        records = [
            logging.LogRecord(
                name="test", level=logging.INFO, pathname="test.py", lineno=1,
                msg=f"Message {i}", args=(), exc_info=None
            )
            for i in range(3)
        ]
        
        # Emit all records
        for record in records:
            handler.emit(record)
        
        captured = capsys.readouterr()
        
        # All messages should be present
        for i in range(3):
            assert f"Message {i}" in captured.out
        
        handler.close()
    
    def test_handler_with_file_handler_integration(self, tmp_path, capsys):
        """Test that ParallelStdoutHandler works together with file handler."""
        # Create a logger with both handlers
        logger = logging.getLogger("test_integration")
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Add file handler
        log_file = tmp_path / "test.log"
        file_handler = ImmediateFlushFileHandler(str(log_file))
        file_formatter = logging.Formatter('FILE: %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Add stdout handler
        stdout_handler = ParallelStdoutHandler(logging.INFO)
        stdout_formatter = logging.Formatter('STDOUT: %(message)s')
        stdout_handler.setFormatter(stdout_formatter)
        logger.addHandler(stdout_handler)
        
        # Log a message
        logger.info("Integration test message")
        
        # Check stdout output
        captured = capsys.readouterr()
        assert "STDOUT: Integration test message" in captured.out
        
        # Check file output
        file_content = log_file.read_text()
        assert "FILE: Integration test message" in file_content
        
        # Clean up
        file_handler.close()
        stdout_handler.close()
    
    def test_conditional_stdout_logging_disabled(self, capsys):
        """Test that stdout logging can be conditionally disabled."""
        # This test simulates the behavior when PARALLEL_STDOUT_LOGGING is disabled
        # In practice, the handler wouldn't be created, but we test the filtering behavior
        
        # Create handler with very high level to effectively disable it
        handler = ParallelStdoutHandler(logging.CRITICAL + 1)
        
        # Create records at various levels
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=1,
            msg="Info message", args=(), exc_info=None
        )
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py", lineno=1,
            msg="Error message", args=(), exc_info=None
        )
        critical_record = logging.LogRecord(
            name="test", level=logging.CRITICAL, pathname="test.py", lineno=1,
            msg="Critical message", args=(), exc_info=None
        )
        
        # Emit all records
        handler.emit(info_record)
        handler.emit(error_record)
        handler.emit(critical_record)
        
        captured = capsys.readouterr()
        
        # Nothing should be output due to high threshold
        assert "Info message" not in captured.out
        assert "Error message" not in captured.out
        assert "Critical message" not in captured.out
        
        handler.close()
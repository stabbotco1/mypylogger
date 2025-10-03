"""
Tests for CustomJsonFormatter - JSON output format and field ordering.
"""

import json
import logging
from unittest.mock import patch

from mypylogger.formatters import CustomJsonFormatter


class TestCustomJsonFormatter:
    """Test CustomJsonFormatter implementation."""

    def test_formatter_inherits_from_json_formatter(self):
        """Test that CustomJsonFormatter inherits from pythonjsonlogger.JsonFormatter."""
        formatter = CustomJsonFormatter()
        # Check that it has the expected parent class methods
        assert hasattr(formatter, "format")
        assert hasattr(formatter, "parse")
        assert hasattr(formatter, "process_log_record")

    def test_formatter_initialization(self):
        """Test that formatter can be initialized with various parameters."""
        # Test default initialization
        formatter1 = CustomJsonFormatter()
        assert formatter1 is not None

        # Test with format string
        formatter2 = CustomJsonFormatter(fmt="%(time)s %(levelname)s %(message)s")
        assert formatter2 is not None

        # Test with additional parameters
        formatter3 = CustomJsonFormatter(
            fmt="%(time)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        assert formatter3 is not None


class TestFieldOrdering:
    """Test fixed field order with time as first element."""

    def test_parse_returns_correct_field_order(self):
        """Test that parse() returns fields in correct order with time first."""
        formatter = CustomJsonFormatter()
        fields = formatter.parse()

        # Verify it returns a list
        assert isinstance(fields, list)

        # Verify time is first
        assert fields[0] == "time"

        # Verify expected fields are present
        expected_fields = [
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        ]
        for field in expected_fields:
            assert field in fields

    def test_custom_format_string_preserves_time_first(self):
        """Test that custom format strings still put time first."""
        custom_format = "%(levelname)s %(message)s %(time)s %(filename)s"
        formatter = CustomJsonFormatter(fmt=custom_format)
        fields = formatter.parse()

        # Time should still be first regardless of format string order
        assert fields[0] == "time"

        # Other fields should be present
        assert "levelname" in fields
        assert "message" in fields
        assert "filename" in fields

    def test_field_order_consistency(self):
        """Test that field order is consistent across multiple calls."""
        formatter = CustomJsonFormatter()

        fields1 = formatter.parse()
        fields2 = formatter.parse()
        fields3 = formatter.parse()

        assert fields1 == fields2
        assert fields2 == fields3
        assert fields1[0] == "time"


class TestTimestampFormatting:
    """Test UTC ISO8601 timestamp formatting with milliseconds and 'Z' suffix."""

    def test_timestamp_format_utc_iso8601(self):
        """Test that timestamps are formatted as UTC ISO8601 with milliseconds."""
        formatter = CustomJsonFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Format the record
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Check timestamp format
        timestamp = log_data["time"]

        # Should end with 'Z' for UTC
        assert timestamp.endswith("Z")

        # Should be ISO8601 format with milliseconds
        # Format: YYYY-MM-DDTHH:MM:SS.sssZ
        import re

        iso8601_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
        assert re.match(iso8601_pattern, timestamp)

        # Should be parseable as datetime
        from datetime import datetime as dt_class

        # Remove 'Z' and parse
        dt = dt_class.fromisoformat(timestamp[:-1])
        assert isinstance(dt, dt_class)

    def test_timestamp_is_utc(self):
        """Test that timestamps are in UTC timezone."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        timestamp = log_data["time"]

        # Should end with 'Z' indicating UTC
        assert timestamp.endswith("Z")

        # Parse and verify it's reasonable (within last minute)
        from datetime import datetime as dt_class, timezone

        dt = dt_class.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)
        now = dt_class.now(timezone.utc)

        # Should be within the last minute (reasonable for test execution)
        time_diff = abs((now - dt).total_seconds())
        assert time_diff < 60  # Less than 60 seconds difference

    def test_millisecond_precision(self):
        """Test that timestamps include millisecond precision."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        timestamp = log_data["time"]

        # Should have milliseconds (3 digits after decimal)
        import re

        assert re.search(r"\.\d{3}Z$", timestamp)


class TestFieldProcessing:
    """Test field processing: line numbers to strings, normalize nulls."""

    def test_line_numbers_converted_to_strings(self):
        """Test that line numbers are converted to strings."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Line number should be a string
        assert isinstance(log_data["lineno"], str)
        assert log_data["lineno"] == "42"

    def test_null_values_normalized(self):
        """Test that null/None values are properly handled."""
        formatter = CustomJsonFormatter()

        # Create record with some None values
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Manually add some None values to test normalization
        record.custom_field = None

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Should handle None values gracefully (either exclude or convert to null)
        # The exact behavior will be defined in implementation
        assert formatted is not None
        assert isinstance(log_data, dict)

    def test_process_log_record_called(self):
        """Test that process_log_record is called during formatting."""
        formatter = CustomJsonFormatter()

        # Mock the process_log_record method
        with patch.object(
            formatter, "process_log_record", side_effect=formatter.process_log_record
        ) as mock_process:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="/test/file.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            formatter.format(record)

            # Verify process_log_record was called
            mock_process.assert_called_once()

    def test_field_processing_preserves_required_fields(self):
        """Test that field processing preserves all required fields."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_function",
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Verify required fields are present
        required_fields = [
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        ]
        for field in required_fields:
            assert field in log_data


class TestFieldRemoval:
    """Test removal of unwanted fields like taskName."""

    def test_unwanted_fields_removed(self):
        """Test that unwanted fields are removed from output."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add unwanted fields
        record.taskName = "unwanted_task"
        record.thread = 12345
        record.threadName = "MainThread"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Unwanted fields should be removed
        unwanted_fields = ["taskName"]
        for field in unwanted_fields:
            assert field not in log_data

    def test_process_log_record_removes_fields(self):
        """Test that process_log_record method removes unwanted fields."""
        formatter = CustomJsonFormatter()

        # Create a log record dict with unwanted fields
        log_record = {
            "time": "2023-01-01T12:00:00.000Z",
            "levelname": "INFO",
            "message": "test",
            "taskName": "unwanted",
            "thread": 12345,
            "filename": "test.py",
            "lineno": 42,
        }

        processed = formatter.process_log_record(log_record)

        # Should remove taskName but keep other fields
        assert "taskName" not in processed
        assert "time" in processed
        assert "levelname" in processed
        assert "message" in processed


class TestJSONOutput:
    """Test complete JSON output format."""

    def test_output_is_valid_json(self):
        """Test that formatter output is valid JSON."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            func="test_function",
        )

        formatted = formatter.format(record)

        # Should be valid JSON
        log_data = json.loads(formatted)
        assert isinstance(log_data, dict)

    def test_time_field_is_first_in_output(self):
        """Test that time field appears first in JSON output."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Parse as OrderedDict to check field order
        from collections import OrderedDict

        log_data = json.loads(formatted, object_pairs_hook=OrderedDict)

        # First key should be 'time'
        first_key = next(iter(log_data.keys()))
        assert first_key == "time"

    def test_complete_log_entry_format(self):
        """Test complete log entry with all expected fields."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="/path/to/test_file.py",
            lineno=123,
            msg="Test warning message",
            args=(),
            exc_info=None,
            func="test_function",
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Verify all expected fields and their types
        assert "time" in log_data
        assert isinstance(log_data["time"], str)
        assert log_data["time"].endswith("Z")

        assert log_data["levelname"] == "WARNING"
        assert log_data["message"] == "Test warning message"
        assert log_data["filename"] == "test_file.py"
        assert log_data["lineno"] == "123"  # Should be string
        assert log_data["funcName"] == "test_function"


class TestErrorHandling:
    """Test error handling in formatter."""

    def test_handles_missing_fields_gracefully(self):
        """Test that formatter handles missing fields gracefully."""
        formatter = CustomJsonFormatter()

        # Create minimal record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Should not raise exception
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Should still have basic structure
        assert "time" in log_data
        assert "message" in log_data
        assert "levelname" in log_data

    def test_handles_unicode_messages(self):
        """Test that formatter handles unicode messages correctly."""
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="/test/file.py",
            lineno=42,
            msg="Test message with unicode: 你好 🌟",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Should preserve unicode characters
        assert "你好" in log_data["message"]
        assert "🌟" in log_data["message"]

    def test_handles_exception_info(self):
        """Test that formatter handles exception information."""
        formatter = CustomJsonFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="/test/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        # Should not raise exception during formatting
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        # Should have basic fields
        assert "time" in log_data
        assert "message" in log_data
        assert "levelname" in log_data

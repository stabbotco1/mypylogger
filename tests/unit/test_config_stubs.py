"""
Unit tests for config module stubs.
"""

import pytest

from mypylogger.config import LogConfig


class TestLogConfigStubs:
    """Test the stub implementations in config module."""

    def test_logconfig_default_values(self):
        """Test that LogConfig has expected default values."""
        config = LogConfig()
        assert config.app_name == "default_app"
        assert config.log_level == "INFO"
        assert config.empty_log_file_on_run is False
        assert config.parallel_stdout_logging == "false"

    def test_from_environment_stub_returns_default(self, clean_environment):
        """Test that from_environment stub returns default config."""
        config = LogConfig.from_environment()
        assert isinstance(config, LogConfig)
        assert config.app_name == "default_app"

    def test_get_log_level_int_stub_returns_info(self):
        """Test that get_log_level_int stub returns INFO level."""
        config = LogConfig()
        level = config.get_log_level_int()
        assert level == 20  # INFO level

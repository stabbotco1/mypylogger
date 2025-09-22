"""
Unit tests for configuration module.
"""
import os
import pytest
import logging
from mypylogger.config import LogConfig


class TestLogConfig:
    """Test LogConfig dataclass and environment parsing."""
    
    def test_default_configuration(self):
        """Test that default configuration values are correct."""
        config = LogConfig()
        
        assert config.app_name == "default_app"
        assert config.log_level == "INFO"
        assert config.empty_log_file_on_run is False
        assert config.parallel_stdout_logging == "false"
    
    def test_from_environment_with_no_env_vars(self, clean_environment):
        """Test configuration creation when no environment variables are set."""
        config = LogConfig.from_environment()
        
        assert config.app_name == "default_app"
        assert config.log_level == "INFO"
        assert config.empty_log_file_on_run is False
        assert config.parallel_stdout_logging == "false"
    
    def test_from_environment_with_app_name(self, clean_environment):
        """Test APP_NAME environment variable parsing."""
        os.environ['APP_NAME'] = 'test_application'
        
        config = LogConfig.from_environment()
        
        assert config.app_name == 'test_application'
        assert config.log_level == "INFO"  # Should use default
    
    def test_from_environment_with_log_level(self, clean_environment):
        """Test LOG_LEVEL environment variable parsing."""
        os.environ['LOG_LEVEL'] = 'DEBUG'
        
        config = LogConfig.from_environment()
        
        assert config.log_level == 'DEBUG'
        assert config.app_name == "default_app"  # Should use default
    
    def test_from_environment_with_empty_log_file_true(self, clean_environment):
        """Test EMPTY_LOG_FILE_ON_RUN environment variable parsing - true case."""
        os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true'
        
        config = LogConfig.from_environment()
        
        assert config.empty_log_file_on_run is True
    
    def test_from_environment_with_empty_log_file_false(self, clean_environment):
        """Test EMPTY_LOG_FILE_ON_RUN environment variable parsing - false case."""
        os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'false'
        
        config = LogConfig.from_environment()
        
        assert config.empty_log_file_on_run is False
    
    def test_from_environment_with_parallel_stdout_logging(self, clean_environment):
        """Test PARALLEL_STDOUT_LOGGING environment variable parsing."""
        os.environ['PARALLEL_STDOUT_LOGGING'] = 'INFO'
        
        config = LogConfig.from_environment()
        
        assert config.parallel_stdout_logging == 'INFO'
    
    def test_from_environment_with_all_variables(self, clean_environment):
        """Test configuration with all environment variables set."""
        os.environ['APP_NAME'] = 'my_app'
        os.environ['LOG_LEVEL'] = 'WARNING'
        os.environ['EMPTY_LOG_FILE_ON_RUN'] = 'true'
        os.environ['PARALLEL_STDOUT_LOGGING'] = 'DEBUG'
        
        config = LogConfig.from_environment()
        
        assert config.app_name == 'my_app'
        assert config.log_level == 'WARNING'
        assert config.empty_log_file_on_run is True
        assert config.parallel_stdout_logging == 'DEBUG'
    
    def test_get_log_level_int_valid_levels(self):
        """Test conversion of valid log level strings to integers."""
        test_cases = [
            ('DEBUG', logging.DEBUG),
            ('INFO', logging.INFO),
            ('WARNING', logging.WARNING),
            ('ERROR', logging.ERROR),
            ('CRITICAL', logging.CRITICAL),
        ]
        
        for level_str, expected_int in test_cases:
            config = LogConfig(log_level=level_str)
            assert config.get_log_level_int() == expected_int
    
    def test_get_log_level_int_invalid_level(self):
        """Test conversion of invalid log level defaults to INFO."""
        config = LogConfig(log_level='INVALID_LEVEL')
        assert config.get_log_level_int() == logging.INFO
    
    def test_get_log_level_int_case_insensitive(self):
        """Test that log level conversion is case insensitive."""
        test_cases = [
            ('debug', logging.DEBUG),
            ('info', logging.INFO),
            ('warning', logging.WARNING),
            ('error', logging.ERROR),
            ('critical', logging.CRITICAL),
        ]
        
        for level_str, expected_int in test_cases:
            config = LogConfig(log_level=level_str)
            assert config.get_log_level_int() == expected_int
    
    def test_boolean_parsing_variations(self, clean_environment):
        """Test various boolean string representations for EMPTY_LOG_FILE_ON_RUN."""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES']
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'No', 'NO', '']
        
        for true_val in true_values:
            os.environ['EMPTY_LOG_FILE_ON_RUN'] = true_val
            config = LogConfig.from_environment()
            assert config.empty_log_file_on_run is True, f"Failed for value: {true_val}"
            del os.environ['EMPTY_LOG_FILE_ON_RUN']
        
        for false_val in false_values:
            os.environ['EMPTY_LOG_FILE_ON_RUN'] = false_val
            config = LogConfig.from_environment()
            assert config.empty_log_file_on_run is False, f"Failed for value: {false_val}"
            del os.environ['EMPTY_LOG_FILE_ON_RUN']
    
    def test_validation_with_empty_strings(self, clean_environment):
        """Test handling of empty string environment variables."""
        os.environ['APP_NAME'] = ''
        os.environ['LOG_LEVEL'] = ''
        os.environ['PARALLEL_STDOUT_LOGGING'] = ''
        
        config = LogConfig.from_environment()
        
        # Empty strings should use defaults
        assert config.app_name == "default_app"
        assert config.log_level == "INFO"
        assert config.parallel_stdout_logging == "false"
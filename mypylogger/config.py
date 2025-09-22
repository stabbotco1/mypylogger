"""
Configuration management for environment-driven logging setup.
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogConfig:
    """Configuration class for logging settings."""
    app_name: str = "default_app"
    log_level: str = "INFO"
    empty_log_file_on_run: bool = False
    parallel_stdout_logging: str = "false"
    
    @classmethod
    def from_environment(cls) -> 'LogConfig':
        """Create configuration from environment variables."""
        app_name = os.environ.get('APP_NAME', 'default_app')
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        empty_log_file_on_run = cls._parse_boolean(os.environ.get('EMPTY_LOG_FILE_ON_RUN', 'false'))
        parallel_stdout_logging = os.environ.get('PARALLEL_STDOUT_LOGGING', 'false')
        
        # Handle empty strings by using defaults
        if not app_name.strip():
            app_name = 'default_app'
        if not log_level.strip():
            log_level = 'INFO'
        if not parallel_stdout_logging.strip():
            parallel_stdout_logging = 'false'
        
        return cls(
            app_name=app_name,
            log_level=log_level,
            empty_log_file_on_run=empty_log_file_on_run,
            parallel_stdout_logging=parallel_stdout_logging
        )
    
    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """Parse string value to boolean."""
        if not value:
            return False
        return value.lower() in ('true', '1', 'yes')
    
    def get_log_level_int(self) -> int:
        """Convert string log level to integer."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        
        # Convert to uppercase for case-insensitive matching
        level_upper = self.log_level.upper()
        
        # Return the mapped level or default to INFO if invalid
        return level_map.get(level_upper, logging.INFO)
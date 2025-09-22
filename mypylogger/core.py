"""
Core singleton logger implementation.
"""
import logging
import threading
from typing import Optional

from .config import LogConfig


class SingletonLogger:
    """Singleton logger class that provides consistent logging configuration."""
    
    _instance: Optional['SingletonLogger'] = None
    _logger: Optional[logging.Logger] = None
    _config: Optional[LogConfig] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the configured logger instance."""
        if cls._logger is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._logger is None:
                    cls._initialize_logger()
        return cls._logger
    
    @classmethod
    def _initialize_logger(cls) -> None:
        """Initialize the logger with configuration."""
        # Get configuration from environment
        cls._config = LogConfig.from_environment()
        
        # Create logger with app name
        cls._logger = logging.getLogger(cls._config.app_name)
        
        # Set the logging level
        cls._logger.setLevel(cls._config.get_log_level_int())
        
        # Prevent adding duplicate handlers
        if not cls._logger.handlers:
            # For now, just add a basic handler - full handler setup will be in later tasks
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)
    
    @classmethod
    def get_effective_level(cls) -> int:
        """Get the effective logging level."""
        logger = cls.get_logger()
        return logger.getEffectiveLevel()
    
    # Expose logging constants
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
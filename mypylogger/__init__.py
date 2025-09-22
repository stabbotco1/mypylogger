# mypylogger - Production-quality Python logging library
# Provides structured JSON logging with real-time development support

__version__ = "0.1.0"
__author__ = "Developer"

# Import main components
from .core import SingletonLogger
from .config import LogConfig
from .formatters import CustomJsonFormatter
from .handlers import ImmediateFlushFileHandler, ParallelStdoutHandler

# Public API exports
def get_logger():
    """Get the configured logger instance."""
    return SingletonLogger.get_logger()

def get_effective_level():
    """Get the effective logging level."""
    return SingletonLogger.get_effective_level()

# Expose logging constants for convenience
DEBUG = SingletonLogger.DEBUG
INFO = SingletonLogger.INFO
WARNING = SingletonLogger.WARNING
ERROR = SingletonLogger.ERROR
CRITICAL = SingletonLogger.CRITICAL

__all__ = [
    'get_logger',
    'get_effective_level',
    'SingletonLogger',
    'LogConfig',
    'CustomJsonFormatter',
    'ImmediateFlushFileHandler',
    'ParallelStdoutHandler',
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL'
]
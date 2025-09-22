"""
Custom logging handlers for file and stdout output.
"""
import logging
import sys
from typing import Optional


class ImmediateFlushFileHandler(logging.FileHandler):
    """File handler that flushes immediately after each log entry."""
    
    def __init__(self, filename: str, mode: str = 'a', encoding: Optional[str] = None):
        # Stub implementation - will be fully implemented in later tasks
        super().__init__(filename, mode, encoding)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with immediate flush."""
        # Stub implementation
        super().emit(record)


class ParallelStdoutHandler(logging.StreamHandler):
    """Handler that outputs to stdout with level filtering."""
    
    def __init__(self, stdout_level: int = logging.INFO):
        # Stub implementation - will be fully implemented in later tasks
        super().__init__(sys.stdout)
        self.stdout_level = stdout_level
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to stdout if level is appropriate."""
        # Stub implementation
        if record.levelno >= self.stdout_level:
            super().emit(record)
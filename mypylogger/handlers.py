"""
Custom logging handlers for file and stdout output.
"""
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_log_file_path(app_name: str, logs_dir: str = "logs") -> str:
    """
    Generate log file path with format: {logs_dir}/{APP_NAME}_{YYYY_MM_DD}.log
    
    Args:
        app_name: Application name for the log file prefix
        logs_dir: Directory where log files should be stored (default: "logs")
    
    Returns:
        Full path to the log file
    """
    today = datetime.now().strftime("%Y_%m_%d")
    filename = f"{app_name}_{today}.log"
    return str(Path(logs_dir) / filename)


class ImmediateFlushFileHandler(logging.FileHandler):
    """File handler that flushes immediately after each log entry."""
    
    def __init__(self, filename: str, mode: str = 'a', encoding: Optional[str] = None):
        # Create directory if it doesn't exist
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, mode, encoding)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with immediate flush."""
        super().emit(record)
        # Flush immediately after each log entry for real-time visibility
        self.flush()


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
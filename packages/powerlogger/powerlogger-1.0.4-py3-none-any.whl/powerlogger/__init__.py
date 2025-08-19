"""
PowerLogger - Enhanced logging functionality with Rich console output and file rotation.

A Python logging library that provides:
- Rich console output with colors and formatting
- File logging with automatic rotation
- Thread-safe queue-based logging
- Windows-optimized file handling
- Configuration management via INI files
"""

__version__ = "1.0.4"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"

from .powerlogger import (
    get_logger,
    get_logger_with_queue,
    get_logger_with_queue_and_file,
    get_logger_with_file_handler,
    cleanup_loggers,
    WindowsSafeRotatingFileHandler,
    ThreadSafeQueueHandler
)

__all__ = [
    "get_logger",
    "get_logger_with_queue", 
    "get_logger_with_queue_and_file",
    "get_logger_with_file_handler",
    "cleanup_loggers",
    "WindowsSafeRotatingFileHandler",
    "ThreadSafeQueueHandler"
]

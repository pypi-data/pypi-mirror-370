"""
PowerLogger - A high-performance, thread-safe logging library with Rich console output and UTF-8 support.

This package provides enhanced logging capabilities with beautiful console formatting,
thread-safe queue-based logging, file rotation, and full Unicode support.
"""

__version__ = "1.0.3"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"
__description__ = "A high-performance, thread-safe logging library with Rich console output and UTF-8 support"

from .powerlogger import (
    get_logger,
    get_logger_with_file_handler,
    get_logger_with_queue,
    get_logger_with_queue_and_file,
    WindowsSafeRotatingFileHandler,
    ThreadSafeQueueHandler
)

__all__ = [
    "get_logger",
    "get_logger_with_file_handler", 
    "get_logger_with_queue",
    "get_logger_with_queue_and_file",
    "WindowsSafeRotatingFileHandler",
    "ThreadSafeQueueHandler"
]

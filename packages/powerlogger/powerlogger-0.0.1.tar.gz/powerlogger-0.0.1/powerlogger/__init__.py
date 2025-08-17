"""
PowerLogger Package

A high-performance, thread-safe logging library built with Python's logging module 
and enhanced with the Rich library for beautiful console output with full UTF-8 support.
"""

__version__ = "0.0.1"
__author__ = "Pandiyaraj Karuppasamy"
__email__ = "pandiyarajk@live.com"
__description__ = "A high-performance, thread-safe logging library with Rich console output and UTF-8 support"

# Import main functions for easy access
from .powerlogger import (
    get_logger,
    get_logger_with_file_handler,
    get_logger_with_queue,
    get_logger_with_queue_and_file,
    cleanup_loggers,
    load_config,
    get_log_level_from_config,
    WindowsSafeRotatingFileHandler,
    ThreadSafeQueueHandler,
)

# Make these available at package level
__all__ = [
    "get_logger",
    "get_logger_with_file_handler", 
    "get_logger_with_queue",
    "get_logger_with_queue_and_file",
    "cleanup_loggers",
    "load_config",
    "get_log_level_from_config",
    "WindowsSafeRotatingFileHandler",
    "ThreadSafeQueueHandler",
]

"""Basic logging test for powerlogger package"""

import tempfile
import os
from powerlogger import get_logger_with_file_handler


def test_logging():
    """Test basic logging functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp:
        log_file = tmp.name
    
    try:
        logger = get_logger_with_file_handler("test_logging", log_file=log_file)
        logger.info("Test message")
        
        # Check if log file was created
        assert os.path.exists(log_file)
        
        # Check if message was written
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test message" in content
            
    finally:
        # Cleanup
        if os.path.exists(log_file):
            os.unlink(log_file)

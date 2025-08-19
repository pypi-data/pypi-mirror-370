"""
Logging handlers for different output destinations and configurations.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Union, TextIO
from datetime import datetime

def create_file_handler(
    log_file: Union[str, Path],
    level: int = logging.INFO,
    formatter: Optional[logging.Formatter] = None
) -> logging.FileHandler:
    """Create a file handler for logging.
    
    Args:
        log_file: Path to the log file
        level: Logging level
        formatter: Custom formatter for the handler
    
    Returns:
        Configured file handler
    """
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    if formatter:
        handler.setFormatter(formatter)
    return handler

def create_console_handler(
    level: int = logging.INFO,
    formatter: Optional[logging.Formatter] = None
) -> logging.StreamHandler:
    """Create a console handler for logging.
    
    Args:
        level: Logging level
        formatter: Custom formatter for the handler
    
    Returns:
        Configured console handler
    """
    handler = logging.StreamHandler()
    handler.setLevel(level)
    if formatter:
        handler.setFormatter(formatter)
    return handler

# Note: add_file_handler moved to utils.py for better functionality
# Use utils.add_file_handler instead

def setup_secondary_log(
    logger: logging.Logger,
    log_dir: Union[str, Path],
    name: str,
    level: int = logging.INFO
) -> logging.Logger:
    """Set up a secondary logger for specific purposes.
    
    Args:
        logger: Main logger to base the secondary logger on
        log_dir: Directory for log files
        name: Name for the secondary logger
        level: Logging level
    
    Returns:
        Configured secondary logger
    """
    secondary_logger = logging.getLogger(f"{logger.name}.{name}")
    secondary_logger.setLevel(level)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Path(log_dir) / f"{name}_{timestamp}.log"
    
    # Add file handler
    from .utils import add_file_handler
    add_file_handler(secondary_logger.name, log_file, str(level))
    
    return secondary_logger 
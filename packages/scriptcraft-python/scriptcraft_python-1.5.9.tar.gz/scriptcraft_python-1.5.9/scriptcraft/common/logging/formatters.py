"""
Logging formatters for different output formats and contexts.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

class QCFormatter(logging.Formatter):
    """Formatter for QC-specific logging with structured output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with QC-specific structure."""
        if hasattr(record, 'qc_context'):
            return f"[QC] {record.getMessage()}"
        return super().format(record)

class TimestampFormatter(logging.Formatter):
    """Formatter that includes timestamps in log messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] {record.getMessage()}"

def create_formatter(
    log_format: Optional[str] = None,
    include_timestamp: bool = True,
    qc_format: bool = False
) -> logging.Formatter:
    """Create a formatter with specified options.
    
    Args:
        log_format: Custom format string for the formatter
        include_timestamp: Whether to include timestamps
        qc_format: Whether to use QC-specific formatting
    
    Returns:
        Configured logging formatter
    """
    if qc_format:
        return QCFormatter()
    
    if log_format:
        return logging.Formatter(log_format)
    
    if include_timestamp:
        return TimestampFormatter()
    
    return logging.Formatter('%(message)s') 
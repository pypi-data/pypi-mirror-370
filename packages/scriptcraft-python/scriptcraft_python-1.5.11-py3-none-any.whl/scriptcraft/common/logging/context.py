"""
Context management for logging operations.
"""

import logging
import contextlib
from pathlib import Path
from typing import Optional, Dict, Any, Generator, Union, Callable, TypeVar
from datetime import datetime

T = TypeVar('T')

class QCLogContext:
    """Context manager for QC-specific logging."""
    
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]) -> None:
        """Initialize QC log context.
        
        Args:
            logger: Logger to use
            context: Context information for logging
        """
        self.logger = logger
        self.context = context
        self.start_time = datetime.now()
    
    def __enter__(self) -> 'QCLogContext':
        """Enter the QC log context."""
        self.logger.info(f"Starting QC operation: {self.context.get('operation', 'Unknown')}")
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], 
                 exc_tb: Optional[Any]) -> None:
        """Exit the QC log context."""
        duration = datetime.now() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed QC operation in {duration.total_seconds():.2f} seconds")
        else:
            self.logger.error(f"QC operation failed after {duration.total_seconds():.2f} seconds: {exc_val}")

@contextlib.contextmanager
def qc_log_context(
    log_path: Union[str, Path],
    operation: Optional[str] = None,
    **context: Any
) -> Generator[logging.Logger, None, None]:
    """Context manager for QC logging operations."""
    from .core import setup_logger
    if isinstance(log_path, (str, Path)):
        logger = setup_logger(log_file=log_path, clear_handlers=False)
    else:
        logger = log_path
    if operation:
        context['operation'] = operation
    start_time = datetime.now()
    if operation:
        logger.info(f"Starting QC operation: {operation}")
    success = False
    try:
        yield logger
        success = True
    except Exception as e:
        duration = datetime.now() - start_time
        if operation:
            logger.error(f"QC operation '{operation}' failed after {duration.total_seconds():.2f} seconds: {e}")
        raise
    finally:
        if success and operation:
            duration = datetime.now() - start_time
            logger.info(f"Completed QC operation '{operation}' in {duration.total_seconds():.2f} seconds")


@contextlib.contextmanager
def with_domain_logger(
    log_path: Union[str, Path],
    func: Callable[[], T]
) -> Generator[None, None, None]:
    """Context manager for domain-specific logging operations.
    
    Args:
        log_path: Path to log file
        func: Function to execute within the logging context
    
    Yields:
        None
    """
    # Import here to avoid circular imports
    from .core import setup_logger
    
    # Set up logger for this context
    logger = setup_logger(log_file=log_path, clear_handlers=False)
    
    start_time = datetime.now()
    logger.info(f"Starting domain operation")
    
    try:
        func()
        yield
    except Exception as e:
        duration = datetime.now() - start_time
        logger.error(f"Domain operation failed after {duration.total_seconds():.2f} seconds: {e}")
        raise
    else:
        duration = datetime.now() - start_time
        logger.info(f"Completed domain operation in {duration.total_seconds():.2f} seconds")


def log_fix_summary(
    logger: logging.Logger,
    fixes: Dict[str, int],
    total_items: int
) -> None:
    """Log a summary of fixes applied.
    
    Args:
        logger: Logger to use
        fixes: Dictionary of fix types and counts
        total_items: Total number of items processed
    """
    logger.info("Fix Summary:")
    for fix_type, count in fixes.items():
        logger.info(f"  - {fix_type}: {count} items")
    logger.info(f"Total items processed: {total_items}") 
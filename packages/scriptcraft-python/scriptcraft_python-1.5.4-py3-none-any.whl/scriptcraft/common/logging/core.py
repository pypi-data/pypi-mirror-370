"""
Core Logging Module

This module provides basic logging functionality without dependencies on other modules.
It is designed to be imported by other modules that need logging capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union, List

# Configure stdout for UTF-8 encoding to handle emojis in Windows PowerShell
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Python < 3.7 or non-Windows systems
    pass

def log_and_print(
    message: str,
    level: str = "info",
    logger_name: str = "root",
    verbose: bool = True
) -> None:
    """
    Log a message and optionally print it to console.
    
    Args:
        message: Message to log
        level: Logging level
        logger_name: Name of logger to use
        verbose: Whether to print to console
    """
    logger = logging.getLogger(logger_name)
    
    # Add emoji prefixes based on level if not already present
    emoji_prefixes: Dict[str, str] = {
        'debug': '🔍 ',
        'info': '📝 ',
        'warning': '⚠️ ',
        'error': '❌ ',
        'critical': '💥 '
    }
    
    # Don't add emoji if message already starts with an emoji
    if not any(char in message[:3] for char in '🔍📝⚠️❌💥🚀✅🎯📊📁🔧💡🎉🏁'):
        emoji = emoji_prefixes.get(level.lower(), '')
        if emoji:
            message = emoji + message
    
    # Log to file
    log_func = getattr(logger, level.lower())
    log_func(message)
    
    # Print to console if verbose (avoid duplicate output if named logger handles console)
    if verbose:
        # Check if we have a named logger with console output to prevent duplicates
        should_print = True
        if logger_name == "root":
            # Check if any named logger has a stream handler
            for name in logging.getLogger().manager.loggerDict:
                named_logger = logging.getLogger(name)
                if any(isinstance(h, logging.StreamHandler) for h in named_logger.handlers):
                    should_print = False
                    break
        
        if should_print:
            try:
                print(message)
            except UnicodeEncodeError:
                # Fallback to ASCII if UTF-8 fails
                print(message.encode('ascii', 'replace').decode())


def log_message(message: str, level: str = "info") -> None:
    """
    Log message without printing to console.
    
    Args:
        message: Message to log
        level: Log level (debug, info, warning, error, critical)
    """
    logger = logging.getLogger()
    log_func = getattr(logger, level.lower())
    log_func(message)


def log_fix_summary(fixes: Dict[str, Any]) -> None:
    """
    Log summary of fixes applied.
    
    Args:
        fixes: Dictionary of fixes applied
    """
    if not fixes:
        log_and_print("ℹ️ No fixes were applied")
        return
    
    log_and_print("\n📊 Fix Summary:")
    for key, value in fixes.items():
        if isinstance(value, (int, float)):
            log_and_print(f"  - {key}: {value}")
        elif isinstance(value, dict):
            log_and_print(f"  - {key}:")
            for subkey, subvalue in value.items():
                log_and_print(f"    - {subkey}: {subvalue}")
        else:
            log_and_print(f"  - {key}: {value}")


def setup_logger(
    name: str = "root",
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    verbose: bool = True,
    clear_handlers: bool = True,
    rotate_logs: bool = True
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Name of the logger
        level: Logging level (string or int)
        log_file: Optional path to log file
        log_format: Format string for log messages
        verbose: Whether to enable verbose logging
        clear_handlers: Whether to clear existing handlers
        rotate_logs: Whether to rotate/backup old log files
        
    Returns:
        Configured logger instance
    """
    # Get named logger or root logger
    logger = logging.getLogger(name) if name != "root" else logging.getLogger()
    
    # Set level
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)
    
    # Clear existing handlers to prevent duplicates
    if clear_handlers:
        logger.handlers.clear()
    
    # Check if handlers already exist to prevent duplicates
    has_file_handler = any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    has_stream_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    
    # Create formatter with UTF-8 encoding
    class Utf8Formatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            try:
                return super().format(record)
            except UnicodeEncodeError:
                # If encoding fails, replace problematic characters
                record.msg = record.msg.encode('ascii', 'replace').decode()
                return super().format(record)
    
    formatter = Utf8Formatter(log_format)
    
    # Add file handler if log_file specified and not already present
    if log_file and not has_file_handler:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotate old log files if requested
        if rotate_logs and log_file.exists():
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = log_file.with_suffix(f".{timestamp}{log_file.suffix}")
            try:
                log_file.rename(backup_file)
                print(f"📁 Rotated old log to: {backup_file}")
            except Exception as e:
                print(f"⚠️ Could not rotate log file: {e}")
        
        try:
            file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Could not create file handler with UTF-8 encoding: {e}")
            # Fallback to default encoding
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    # Add stream handler for console output if verbose and not already present
    if verbose and not has_stream_handler:
        try:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        except Exception as e:
            print(f"⚠️ Could not create stream handler: {e}")
    
    # Disable propagation for named loggers to prevent double logging
    if name != "root":
        logger.propagate = False
    else:
        logger.propagate = True
        

    
    # Log initialization only once with emojis
    if not hasattr(logger, '_initialized') or clear_handlers:
        try:
            logger.info(f"🚀 Logger '{name}' initialized with level {logging.getLevelName(level)}")
            if log_file:
                logger.info(f"📝 Log file: {log_file}")
        except UnicodeEncodeError:
            # Fallback to ASCII if UTF-8 fails
            logger.info(f"Logger '{name}' initialized with level {logging.getLevelName(level)}")
            if log_file:
                logger.info(f"Log file: {log_file}")
        setattr(logger, '_initialized', True)
    
    return logger


def clear_handlers(logger_name: str = "root") -> None:
    """Clear all handlers from the specified logger."""
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()


def get_handler_paths(logger_name: str = "root") -> List[str]:
    """Get paths of all file handlers for the specified logger."""
    logger = logging.getLogger(logger_name)
    return [
        handler.baseFilename
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    ] 
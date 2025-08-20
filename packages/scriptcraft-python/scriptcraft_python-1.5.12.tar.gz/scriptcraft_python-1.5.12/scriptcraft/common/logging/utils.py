"""
scripts/common/logging_utils.py

📝 Centralized logging configuration and utilities for consistent logging behavior 
across the project. Supports dynamic timestamp control, structured logging (JSON),
verbose mode control, and flexible log level settings.
"""

import logging
import json
import yaml
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Union, Dict, Any, Generator
import sys

from ..io.paths import LOG_LEVEL
# from .file_path_utils import get_project_root
from ..core.config import Config
from .core import setup_logger as core_setup_logger, log_and_print
from .formatters import create_formatter
from .handlers import create_file_handler, create_console_handler

# ==== 🔧 Logging Configuration Classes ====

class LogConfig:
    """
    📚 Centralized logging configuration management.

    Controls timestamp formatting, log levels, structured logging, 
    verbose console output, and default log file locations.

    Example:
        config.set_log_level("DEBUG")
        config.set_structured_logging(True)

    Attributes:
        use_timestamps (bool): Whether to include timestamps in logs.
        log_level (int): Current logging level.
        verbose_mode (bool): Whether logs should also print to console.
        use_structured_logging (bool): Whether to use JSON structured logging.
        default_log_dir (Path): Default directory for log files.
        formatter (logging.Formatter): Current formatter instance.
    """

    def __init__(self) -> None:
        self.use_timestamps = True
        self.log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        self.verbose_mode = True  # Default to True for better visibility
        self.use_structured_logging = False
        self.default_log_dir = Path("logs")
        self.formatter: logging.Formatter = logging.Formatter()
        self._update_formatter()

    def _update_formatter(self) -> None:
        """🔄 Update the formatter based on current settings."""
        if self.use_structured_logging:
            self.formatter = StructuredFormatter(use_timestamps=self.use_timestamps)
        else:
            self.formatter = logging.Formatter(
                "%(asctime)s — %(levelname)s — %(message)s" if self.use_timestamps else "%(levelname)s — %(message)s",
                "%Y-%m-%d %H:%M:%S" if self.use_timestamps else None
            )

    def set_timestamps(self, enabled: bool) -> None:
        """
        📅 Toggle timestamp inclusion in log messages.

        Args:
            enabled (bool): Enable or disable timestamps in logs.
        """
        self.use_timestamps = enabled
        self._update_formatter()
        self._update_all_handlers()

    def set_log_level(self, level: Union[str, int]) -> None:
        """
        📈 Dynamically update the log level.

        Args:
            level (str | int): New log level (e.g., "INFO", "DEBUG", 20).
        """
        if isinstance(level, str):
            self.log_level = getattr(logging, level.upper(), logging.INFO)
        else:
            self.log_level = level
        logging.getLogger().setLevel(self.log_level)

    def set_structured_logging(self, enabled: bool) -> None:
        """
        📦 Enable or disable structured (JSON) logging.

        Args:
            enabled (bool): Enable structured JSON logging if True.
        """
        self.use_structured_logging = enabled
        self._update_formatter()
        self._update_all_handlers()

    def set_verbose_mode(self, enabled: bool) -> None:
        """
        📢 Toggle verbose mode for console output.

        Args:
            enabled (bool): If True, logs will also print to console.
        """
        self.verbose_mode = enabled

    def set_default_log_dir(self, path: Union[str, Path]) -> None:
        """
        📁 Set the default directory for log files.

        Args:
            path (str | Path): New default directory for log files.
        """
        self.default_log_dir = Path(path)
        self.default_log_dir.mkdir(parents=True, exist_ok=True)

    def _update_all_handlers(self) -> None:
        """🔄 Refresh all existing log handlers with the current formatter."""
        logger = logging.getLogger()
        for handler in logger.handlers:
            handler.setFormatter(self.formatter)


class StructuredFormatter(logging.Formatter):
    """
    📦 Formatter for structured JSON logging.

    Adds timestamp and extra data fields to log records when enabled.
    """

    def __init__(self, use_timestamps: bool = True) -> None:
        super().__init__()
        self.use_timestamps = use_timestamps

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if self.use_timestamps:
            log_data["timestamp"] = self.formatTime(record)
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        return json.dumps(log_data)


# Initialize Global Config Instance
config = LogConfig()

# Load verbose mode from config.yaml if it exists
config_path = Path("config.yaml")
if config_path.exists():
    try:
        with open(config_path, encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        config.set_verbose_mode(yaml_config.get("verbose_mode", True))  # Default to True if not specified
    except Exception as e:
        logging.warning(f"Failed to load verbose mode from config: {e}")
        config.set_verbose_mode(True)  # Default to True on error
else:
    config.set_verbose_mode(True)  # Default to True if no config file

# config_path = get_project_root() / "config.yaml"
# if config_path.exists():
#     with open(config_path) as f:
#         yaml_config = yaml.safe_load(f)
#     config.set_verbose_mode(yaml_config.get("verbose_mode", False))
# else:
#     # You can optionally log or silently continue with default settings
#     config.set_verbose_mode(False)


# ==== 🧰 Logging Utility Functions ====

def clear_handlers(logger: Optional[logging.Logger] = None) -> None:
    """
    🧹 Safely remove all log handlers from a logger.

    Args:
        logger (Logger, optional): The logger to clear. Defaults to root logger.
    """
    logger = logger or logging.getLogger()
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])


def get_handler_paths() -> Dict[str, Path]:
    """
    📂 Retrieve paths of all active file-based log handlers.

    Returns:
        Dict[str, Path]: Dictionary of log file paths and their resolved Path objects.
    """
    logger = logging.getLogger()
    return {
        str(Path(h.baseFilename).resolve()): Path(h.baseFilename)
        for h in logger.handlers
        if isinstance(h, logging.FileHandler)
    }


# ==== 📝 Core Logging Functions ====

def log_message(
    message: str,
    level: str = "info",
    logger_name: str = "root",
    verbose: bool = True
) -> None:
    """
    Log a message with optional console output.
    
    Args:
        message: Message to log
        level: Logging level
        logger_name: Name of logger to use
        verbose: Whether to print to console
    """
    log_and_print(message, level=level, logger_name=logger_name, verbose=verbose)


def log_fix_summary(
    fixes: Dict[str, Any],
    logger_name: str = "root",
    verbose: bool = True
) -> None:
    """
    Log a summary of fixes applied.
    
    Args:
        fixes: Dictionary of fixes applied
        logger_name: Name of logger to use
        verbose: Whether to print to console
    """
    if not fixes:
        log_and_print("No fixes applied", level="info", logger_name=logger_name, verbose=verbose)
        return
    
    log_and_print("\nFix Summary:", level="info", logger_name=logger_name, verbose=verbose)
    for key, value in fixes.items():
        if isinstance(value, dict):
            log_and_print(f"\n{key}:", level="info", logger_name=logger_name, verbose=verbose)
            for subkey, subvalue in value.items():
                log_and_print(f"  {subkey}: {subvalue}", level="info", logger_name=logger_name, verbose=verbose)
        else:
            log_and_print(f"{key}: {value}", level="info", logger_name=logger_name, verbose=verbose)


# ==== 📁 File Handler Utilities ====

def add_file_handler(
    logger_name: str,
    log_file: Union[str, Path],
    level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """
    Add a file handler to an existing logger.
    
    Args:
        logger_name: Name of logger to add handler to
        log_file: Path to log file
        level: Logging level
        log_format: Format string for log messages
    """
    logger = logging.getLogger(logger_name)
    
    # Convert level string to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Create file handler
    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(file_handler)
    logger.info(f"Added file handler: {log_file}")


# REMOVED: Duplicate setup_logger function - use core.setup_logger instead


def setup_secondary_log(
    name: str,
    log_file: Union[str, Path],
    level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    verbose: bool = True
) -> logging.Logger:
    """
    Set up a secondary logger for a specific component.
    
    Args:
        name: Name of the logger
        log_file: Path to log file
        level: Logging level
        log_format: Format string for log messages
        verbose: Whether to enable verbose logging
        
    Returns:
        Configured logger instance
    """
    return core_setup_logger(
        name=name,
        level=level,
        log_file=log_file,
        log_format=log_format,
        verbose=verbose,
        clear_handlers=False
    )


def setup_logging_with_timestamp(
    log_dir: Path,
    mode: str,
    clear_handlers: bool = False
) -> Path:
    """Set up logging with timestamp-based log files.
    
    Args:
        log_dir: Directory to store log files
        mode: Mode identifier for the log file
        clear_handlers: Whether to clear existing handlers
        
    Returns:
        Path to the created log file
    """
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp and log file path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{mode}_{timestamp}.log"
    
    # Set up logging
    core_setup_logger(
        log_file=log_file,
        level=LOG_LEVEL,
        clear_handlers=clear_handlers
    )
    
    return log_file


def setup_logging_with_config(
    config: Config,
    mode: str,
    clear_handlers: bool = False
) -> Path:
    """Set up logging using configuration settings.
    
    Args:
        config: Configuration object
        mode: Mode identifier for the log file
        clear_handlers: Whether to clear existing handlers
        
    Returns:
        Path to the created log file
    """
    log_dir = Path(config.logging.log_dir)
    return setup_logging_with_timestamp(log_dir, mode, clear_handlers)


@contextmanager
def qc_log_context(
    log_file: Union[str, Path],
    level: str = "INFO"
) -> Generator[logging.Logger, None, None]:
    """
    Context manager for QC logging operations.
    
    Args:
        log_file: Path to log file
        level: Logging level
        
    Yields:
        Logger instance
    """
    # Set up logging for this context
    logger = core_setup_logger(log_file=log_file, level=level, clear_handlers=False)
    
    try:
        yield logger
    finally:
        # Clean up if needed
        pass


# Set up default logging if this module is imported directly
# NOTE: Commented out to avoid config loading issues during imports
# This should be handled by the calling code, not during module import
# try:
#     loaded_config = Config.from_yaml(Path("config.yaml"))
#     log_config = loaded_config.get_logging_config()
#     core_setup_logger(level=log_config.level)
# except Exception as e:
#     print(f"Warning: Failed to load logging config: {e}")
#     core_setup_logger(level=LOG_LEVEL)  # Default to console output

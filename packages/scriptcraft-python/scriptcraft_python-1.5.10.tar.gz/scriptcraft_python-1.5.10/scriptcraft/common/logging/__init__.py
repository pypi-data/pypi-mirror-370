"""
Logging package for the project.

This package provides logging functionality organized into:
- core: Basic logging setup and configuration
- formatters: Log message formatting
- handlers: Log output handlers
- context: Logging context management
- utils: Additional logging utilities
"""

# === EXPLICIT IMPORTS TO AVOID CONFLICTS ===
from .core import (
    setup_logger, log_and_print, log_message, 
    clear_handlers as core_clear_handlers,
    get_handler_paths as core_get_handler_paths
)
from .formatters import create_formatter, QCFormatter, TimestampFormatter
from .handlers import create_file_handler, create_console_handler
from .context import qc_log_context, with_domain_logger
from .utils import (
    add_file_handler, setup_secondary_log, setup_logging_with_timestamp,
    setup_logging_with_config, log_fix_summary
)

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Core logging
#     'setup_logger', 'setup_logging', 'log_and_print', 'log_message', 'log_fix_summary',
#     # Formatters
#     'create_formatter', 'QCFormatter', 'TimestampFormatter',
#     # Handlers
#     'create_file_handler', 'create_console_handler', 'add_file_handler',
#     # Context
#     'qc_log_context', 'with_domain_logger',
#     # Utilities
#     'setup_secondary_log', 'setup_logging_with_timestamp', 'setup_logging_with_config'
# ]

# Alias for backward compatibility
setup_logging = setup_logger
clear_handlers = core_clear_handlers
get_handler_paths = core_get_handler_paths 
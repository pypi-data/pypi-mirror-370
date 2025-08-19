"""
Environment detection for dictionary_validator tool.
"""

import os
from pathlib import Path


def is_development_environment() -> bool:
    """
    Detect if running in development environment.
    
    Returns:
        True if in development environment, False if in distributable
    """
    # Check if we're in the development workspace structure
    current_file = Path(__file__)
    
    # Development path: implementations/python/scriptcraft/tools/dictionary_validator/env.py
    # Distributable path: scripts/dictionary_validator/env.py
    return "implementations" in str(current_file.parent.parent.parent.parent) 
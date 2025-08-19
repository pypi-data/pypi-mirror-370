"""
Environment Detection Module

This module provides self-contained environment detection logic that can be
copied into any distributable package without external dependencies.

Usage:
    # Copy this entire module into your distributable
    from env import is_distributable_environment, import_dual_env
    
    # Detect environment
    if is_distributable_environment():
        # Distributable logic
        pass
    else:
        # Development logic
        pass
    
    # Import with fallback
    utils = import_dual_env("scriptcraft.tools.my_tool.utils", "utils")
"""

import sys
import importlib
from pathlib import Path
from typing import Any, Optional


def is_distributable_environment() -> bool:
    """
    Detect if we're running in a distributable environment.
    
    Returns:
        True if in distributable environment, False if in development
    """
    current_file = Path(__file__)
    
    # Check if 'common' folder exists at same level (distributable environment)
    is_distributable = (current_file.parent / 'common').exists()
    
    # Additional checks for distributable environment
    if not is_distributable:
        # Check if we're in a scripts/ subdirectory (common in distributables)
        if 'scripts' in current_file.parts:
            is_distributable = True
    
    return is_distributable


def get_environment_type() -> str:
    """
    Get a human-readable description of the current environment.
    
    Returns:
        Environment type: 'development', 'distributable', or 'unknown'
    """
    if is_distributable_environment():
        return 'distributable'
    else:
        return 'development'


def setup_import_paths() -> None:
    """
    Set up import paths based on the detected environment.
    This should be called early in your main.py file.
    """
    if is_distributable_environment():
        # Distributable environment: add current directory to path
        current_dir = str(Path(__file__).parent)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        print(f"🏗️ Distributable environment detected, added {current_dir} to path")
    else:
        print("🛠️ Development environment detected")


def import_dual_env(dev_path: str, local_name: str) -> Any:
    """
    Import a module with fallback for dual environment support.
    
    Args:
        dev_path: Full import path for development environment
        local_name: Local module name for distributable environment
        
    Returns:
        The imported module
        
    Example:
        # In development: imports from scriptcraft.tools.my_tool.utils
        # In distributable: imports from utils (local file)
        utils = import_dual_env("scriptcraft.tools.my_tool.utils", "utils")
    """
    try:
        # Try development import first
        return importlib.import_module(dev_path)
    except ImportError:
        try:
            # Fallback to local import (distributable environment)
            return importlib.import_module(local_name)
        except ImportError as e:
            raise ImportError(f"Could not import {dev_path} or {local_name}: {e}")


def get_config_path() -> Path:
    """
    Get the appropriate config file path for the current environment.
    
    Returns:
        Path to config.yaml file
    """
    if is_distributable_environment():
        # In distributable, config is typically one level up
        return Path(__file__).parent.parent / "config.yaml"
    else:
        # In development, config is in the workspace root
        return Path(__file__).parent.parent.parent.parent / "config.yaml"


def get_input_directory() -> Path:
    """
    Get the appropriate input directory for the current environment.
    
    Returns:
        Path to input directory
    """
    if is_distributable_environment():
        # In distributable, input is typically one level up
        return Path(__file__).parent.parent / "input"
    else:
        # In development, input is in the workspace root
        return Path(__file__).parent.parent.parent.parent / "input"


def get_output_directory() -> Path:
    """
    Get the appropriate output directory for the current environment.
    
    Returns:
        Path to output directory
    """
    if is_distributable_environment():
        # In distributable, output is typically one level up
        return Path(__file__).parent.parent / "output"
    else:
        # In development, output is in the workspace root
        return Path(__file__).parent.parent.parent.parent / "output"


def get_logs_directory() -> Path:
    """
    Get the appropriate logs directory for the current environment.
    
    Returns:
        Path to logs directory
    """
    if is_distributable_environment():
        # In distributable, logs is typically one level up
        return Path(__file__).parent.parent / "logs"
    else:
        # In development, logs is in the workspace root
        return Path(__file__).parent.parent.parent.parent / "logs"


# Global flag to prevent multiple setup calls
_environment_setup_called = False

# Convenience function for setting up environment at module import
def setup_environment() -> bool:
    """
    Complete environment setup - call this at the top of your main.py.
    
    Returns:
        True if in distributable environment, False if in development
    """
    global _environment_setup_called
    
    if not _environment_setup_called:
        setup_import_paths()
        _environment_setup_called = True
    
    return is_distributable_environment() 
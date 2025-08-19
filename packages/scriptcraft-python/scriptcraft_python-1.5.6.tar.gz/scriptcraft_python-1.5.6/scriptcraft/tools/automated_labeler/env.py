"""
Environment detection and setup for Automated Labeler Tool.

This module provides dual-environment support for both development and distributable modes.
It automatically detects the environment and sets up import paths accordingly.
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

# === Environment Detection ===

def is_distributable_environment() -> bool:
    """
    Detect if we're running in a distributable environment.
    
    Returns:
        True if running in distributable mode, False if in development
    """
    current_dir = Path.cwd()
    
    # Check for distributable indicators
    distributable_indicators = [
        current_dir.name == 'scripts',
        'distributable' in str(current_dir).lower(),
        'packaged' in str(current_dir).lower(),
        current_dir.name == 'automated_labeler' and current_dir.parent.name == 'tools'
    ]
    
    return any(distributable_indicators)


def get_environment_type() -> str:
    """
    Get the current environment type.
    
    Returns:
        'development' or 'distributable'
    """
    return "distributable" if is_distributable_environment() else "development"


def setup_import_paths() -> None:
    """
    Set up import paths based on the current environment.
    
    This function modifies sys.path to ensure the correct modules can be imported.
    """
    if is_distributable_environment():
        # In distributable mode, add the parent directory to path
        current_dir = Path.cwd()
        if current_dir.name == 'scripts':
            # We're in the scripts directory of a distributable
            parent_dir = current_dir.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
        else:
            # We're in the tool directory of a distributable
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
    else:
        # In development mode, ensure the project root is in path
        project_root = Path(__file__).parent.parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))


def import_dual_env(dev_path: str, local_name: str) -> Any:
    """
    Import a module with dual-environment support.
    
    Args:
        dev_path: Import path for development environment
        local_name: Local name for the imported module
        
    Returns:
        The imported module
        
    Raises:
        ImportError: If the module cannot be imported in either environment
    """
    try:
        # Try development import first
        module = __import__(dev_path, fromlist=[local_name])
        return getattr(module, local_name)
    except ImportError:
        try:
            # Try distributable import
            module = __import__(local_name, fromlist=[local_name])
            return getattr(module, local_name)
        except ImportError as e:
            raise ImportError(f"Could not import {local_name} in either environment: {e}")


def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    
    Returns:
        Path to config.yaml
    """
    if is_distributable_environment():
        current_dir = Path.cwd()
        if current_dir.name == 'scripts':
            return current_dir.parent / "config.yaml"
        else:
            return current_dir / "config.yaml"
    else:
        return Path("config.yaml")


def get_input_directory() -> Path:
    """
    Get the input directory path.
    
    Returns:
        Path to input directory
    """
    if is_distributable_environment():
        current_dir = Path.cwd()
        if current_dir.name == 'scripts':
            return current_dir.parent / "input"
        else:
            return current_dir / "input"
    else:
        return Path("input")


def get_output_directory() -> Path:
    """
    Get the output directory path.
    
    Returns:
        Path to output directory
    """
    if is_distributable_environment():
        current_dir = Path.cwd()
        if current_dir.name == 'scripts':
            return current_dir.parent / "output"
        else:
            return current_dir / "output"
    else:
        return Path("output")


def get_logs_directory() -> Path:
    """
    Get the logs directory path.
    
    Returns:
        Path to logs directory
    """
    if is_distributable_environment():
        current_dir = Path.cwd()
        if current_dir.name == 'scripts':
            return current_dir.parent / "logs"
        else:
            return current_dir / "logs"
    else:
        return Path("logs")


def setup_environment() -> bool:
    """
    Set up the environment for the tool.
    
    This function should be called at the start of any tool execution.
    It sets up import paths and returns the environment type.
    
    Returns:
        True if in distributable mode, False if in development mode
    """
    # Set up import paths
    setup_import_paths()
    
    # Log environment type
    env_type = get_environment_type()
    print(f"🔧 Environment: {env_type}")
    
    return is_distributable_environment() 
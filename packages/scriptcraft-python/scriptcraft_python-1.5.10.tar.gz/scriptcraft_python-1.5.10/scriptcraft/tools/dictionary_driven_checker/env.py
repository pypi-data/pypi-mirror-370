"""
Environment detection and setup for Dictionary-Driven Checker Tool.

This module handles the detection of whether the tool is running in
development or distributable mode and sets up the appropriate import paths.
"""

import os
import sys
from pathlib import Path
from typing import Tuple


def setup_environment() -> bool:
    """
    Detect if running in distributable mode and set up environment.
    
    Returns:
        bool: True if running in distributable mode, False if in development
    """
    # Check if we're running from a distributable package
    # Distributable packages have a specific structure
    current_file = Path(__file__).resolve()
    
    # Check for distributable indicators
    is_distributable = (
        # Check if we're in a distributable directory structure
        "distributables" in str(current_file) or
        # Check if we're running from a packaged directory
        current_file.parent.name == "scripts" and
        current_file.parent.parent.name in ["distributables", "packages"] or
        # Check if config.yaml is in parent directory (distributable structure)
        (current_file.parent.parent / "config.yaml").exists()
    )
    
    # Set environment variable for other modules
    os.environ["SCRIPTCRAFT_ENV"] = "distributable" if is_distributable else "development"
    
    return is_distributable


def import_dual_env() -> Tuple[bool, object]:
    """
    Import the appropriate common module based on environment.
    
    Returns:
        Tuple[bool, object]: (is_distributable, common_module)
    """
    is_distributable = setup_environment()
    
    if is_distributable:
        # In distributable mode, import from local common
        try:
            import common as cu
        except ImportError:
            # Fallback: try relative import
            sys.path.insert(0, str(Path(__file__).parent.parent))
            import common as cu
    else:
        # In development mode, import from scriptcraft.common
        try:
            import scriptcraft.common as cu
        except ImportError:
            # Fallback: try adding the project root to path
            project_root = Path(__file__).parent.parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            import scriptcraft.common as cu
    
    return is_distributable, cu


# Initialize environment on module import
IS_DISTRIBUTABLE = setup_environment() 
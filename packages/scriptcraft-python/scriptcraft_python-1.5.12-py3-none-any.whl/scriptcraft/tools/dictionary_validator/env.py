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
    # Use improved environment detection logic
    current_dir = Path.cwd()
    
    # Check for distributable indicators
    distributable_indicators = [
        # Classic distributable structure
        current_dir.name == 'scripts',
        'distributable' in str(current_dir).lower(),
        
        # New PyPI-based structure indicators
        (current_dir / 'embed_py311').exists(),  # Embedded Python
        (current_dir / 'config.bat').exists(),   # Config bat file
        (current_dir / 'run.bat').exists(),      # Run script
        
        # Environment variable set by config.bat
        os.environ.get('TOOL_TO_SHIP') is not None,
        
        # Check if we're in a tool_distributable directory
        current_dir.name.endswith('_distributable')
    ]
    
    # Return False if any distributable indicator is found (i.e., NOT development)
    return not any(distributable_indicators) 
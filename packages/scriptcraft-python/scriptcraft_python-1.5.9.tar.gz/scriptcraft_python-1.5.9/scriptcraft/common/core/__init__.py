"""
Core package for ScriptCraft common utilities.

This package contains base classes and configuration management.
Registry functionality has been moved to the registry package.
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .base import *
from .config import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Base classes
#     'BaseTool', 'BaseMainRunner',
#     
#     # Configuration
#     'Config', 'get_config', 'load_config'
# ]
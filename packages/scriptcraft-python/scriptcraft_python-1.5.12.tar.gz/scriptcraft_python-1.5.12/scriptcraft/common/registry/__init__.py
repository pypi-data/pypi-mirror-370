"""
Unified Registry System for ScriptCraft

This package provides a single, comprehensive registry system that handles:
- Tool discovery and management
- Plugin registration and discovery
- Validation plugin management
- Metadata management

This is the ONLY registry system in ScriptCraft - all other registry code should be removed.
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .registry import *
from .plugin_registry import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Registry functionality
#     'unified_registry', 'registry', 'ToolRegistry', 'PluginRegistry',
#     'register_tool', 'get_tool', 'list_tools', 'get_available_tools'
# ]

# Main registry instance (the ONE registry to rule them all)
registry = unified_registry 
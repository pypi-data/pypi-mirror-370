"""
Plugin System for ScriptCraft

This package redirects to the unified registry system.
All plugin functionality is now in scriptcraft.common.registry
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
# Redirect all imports to the new registry package
from ..registry import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Plugin registry functionality (redirected from registry)
#     'PluginRegistry', 'register_plugin', 'get_plugin', 'list_plugins'
# ]

# Deprecation warning
import warnings
warnings.warn(
    "scriptcraft.common.plugins is deprecated. Use scriptcraft.common.registry instead.",
    DeprecationWarning,
    stacklevel=2
) 
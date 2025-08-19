"""
Plugin system for Release Manager Tool.

This module provides a plugin-based architecture for different release workflows.
"""

from .registry import PluginRegistry
from .python_package_plugin import run_mode as python_package_mode
from .workspace_plugin import run_mode as workspace_mode
from .pypi_plugin import run_mode as pypi_mode
from .workspace_sync_plugin import WorkspaceSyncPlugin

# Plugin registry instance
_plugin_registry = PluginRegistry()

def load_builtin_plugins(registry: PluginRegistry) -> None:
    """Load all built-in plugins into the registry."""
    # Python package release plugin
    registry.register_plugin(
        "python_package",
        python_package_mode,
        {
            "description": "Release a Python package with version bumping and PyPI upload",
            "version_types": ["major", "minor", "patch"],
            "supports_pypi": True,
            "supports_git": True
        }
    )
    
    # Workspace release plugin (like your Mystic Empire script)
    registry.register_plugin(
        "workspace",
        workspace_mode,
        {
            "description": "Release a workspace with version bumping and git operations",
            "version_types": ["major", "minor", "patch"],
            "supports_pypi": False,
            "supports_git": True
        }
    )
    
    # PyPI-only plugin
    registry.register_plugin(
        "pypi",
        pypi_mode,
        {
            "description": "Upload existing package to PyPI without version changes",
            "version_types": [],
            "supports_pypi": True,
            "supports_git": False
        }
    )
    
    # Workspace sync plugin (replaces PowerShell scripts)
    from .workspace_sync_plugin import run_mode as workspace_sync_mode
    registry.register_plugin(
        "workspace_sync",
        workspace_sync_mode,
        {
            "description": "Synchronize workspace and submodule repositories",
            "operations": ["sync", "workspace_sync", "submodule_update"],
            "supports_pypi": False,
            "supports_git": True
        }
    )

def get_plugin(mode: str):
    """Get plugin function by mode name."""
    return _plugin_registry.get_plugin(mode)

def list_plugins():
    """List available plugins."""
    return _plugin_registry.list_plugins()

def get_plugin_info(mode: str):
    """Get plugin information."""
    return _plugin_registry.get_plugin_info(mode)

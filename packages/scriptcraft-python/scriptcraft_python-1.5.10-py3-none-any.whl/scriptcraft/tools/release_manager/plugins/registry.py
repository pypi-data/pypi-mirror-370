"""
Plugin registry for Release Manager Tool.

This module provides a registry system for managing different release workflow plugins.
"""

from typing import Any, Dict, List, Optional, Callable
from pathlib import Path


class PluginRegistry:
    """Registry for managing release workflow plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Callable] = {}
        self._plugin_info: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, name: str, plugin_func: Callable, info: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a plugin with the registry.
        
        Args:
            name: Plugin name
            plugin_func: Plugin function to register
            info: Optional plugin information dictionary
        """
        self._plugins[name] = plugin_func
        self._plugin_info[name] = info or {}
        
        print(f"🔌 Registered plugin: {name}")
    
    def get_plugin(self, name: str) -> Optional[Callable]:
        """
        Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin function or None if not found
        """
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())
    
    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin information dictionary or None if not found
        """
        return self._plugin_info.get(name)
    
    def get_plugins_by_feature(self, feature: str) -> List[str]:
        """
        Get plugins that support a specific feature.
        
        Args:
            feature: Feature name (e.g., 'supports_pypi', 'supports_git')
            
        Returns:
            List of plugin names that support the feature
        """
        supported_plugins = []
        for name, info in self._plugin_info.items():
            if info.get(feature, False):
                supported_plugins.append(name)
        return supported_plugins
    
    def get_plugins_by_version_type(self, version_type: str) -> List[str]:
        """
        Get plugins that support a specific version type.
        
        Args:
            version_type: Version type (e.g., 'major', 'minor', 'patch')
            
        Returns:
            List of plugin names that support the version type
        """
        supported_plugins = []
        for name, info in self._plugin_info.items():
            version_types = info.get('version_types', [])
            if version_type in version_types:
                supported_plugins.append(name)
        return supported_plugins
    
    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin from the registry.
        
        Args:
            name: Plugin name to unregister
            
        Returns:
            True if plugin was unregistered, False if not found
        """
        if name in self._plugins:
            del self._plugins[name]
            del self._plugin_info[name]
            print(f"🔌 Unregistered plugin: {name}")
            return True
        return False
    
    def clear_plugins(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()
        self._plugin_info.clear()
        print("🔌 Cleared all plugins")
    
    def plugin_count(self) -> int:
        """
        Get the number of registered plugins.
        
        Returns:
            Number of plugins
        """
        return len(self._plugins)
    
    def has_plugin(self, name: str) -> bool:
        """
        Check if a plugin is registered.
        
        Args:
            name: Plugin name to check
            
        Returns:
            True if plugin is registered, False otherwise
        """
        return name in self._plugins

"""
Unified Registry System for ScriptCraft

This module provides a single, scalable registry system that handles:
- Tool discovery and instantiation
- Tool metadata management
- Plugin registration and discovery
- Automatic loading and caching
- Integration with CLI and pipeline systems

The registry is designed to be DRY, scalable, and actually useful.
"""

import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import logging

from ..logging import log_and_print
from ..core.base import BaseTool
from scriptcraft._version import __version__

logger = logging.getLogger(__name__)

class ToolMaturity(Enum):
    """Tool maturity levels."""
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    MATURE = "mature"
    DEPRECATED = "deprecated"


class DistributionType(Enum):
    """How the tool can be distributed."""
    STANDALONE = "standalone"
    PIPELINE_ONLY = "pipeline"
    HYBRID = "hybrid"


class ComponentType(Enum):
    """Types of components that can be registered."""
    TOOL = "tool"
    CHECKER = "checker"
    VALIDATOR = "validator"
    TRANSFORMER = "transformer"
    ENHANCEMENT = "enhancement"
    PLUGIN = "plugin"


@dataclass
class ToolMetadata:
    """Comprehensive tool metadata."""
    name: str
    version: str = __version__
    description: str = ""
    category: str = "uncategorized"
    tags: List[str] = field(default_factory=list)
    data_types: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    complexity: str = "simple"
    maturity: str = "stable"
    distribution: str = "hybrid"
    dependencies: List[str] = field(default_factory=list)
    author: str = ""
    maintainer: str = ""
    
    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        # All fields are already initialized as lists by default_factory
        pass


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    plugin_type: str
    description: str = ""
    version: str = __version__
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentMetadata:
    """Metadata for a registered component."""
    name: str
    type: ComponentType
    description: str
    tags: List[str] = field(default_factory=list)
    version: str = __version__
    author: str = "ScriptCraft Team"
    entry_point: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    is_experimental: bool = False
    is_deprecated: bool = False


class UnifiedRegistry:
    """
    Unified registry for tools, plugins, and metadata.
    
    This is the single source of truth for all registry functionality.
    """
    
    def __init__(self) -> None:
        # Tool registry
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._tool_instances: Dict[str, BaseTool] = {}
        self._tool_metadata: Dict[str, ToolMetadata] = {}
        
        # Plugin registry
        self._plugins: Dict[str, Dict[str, Any]] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        
        # Discovery cache
        self._discovered: bool = False
        self._discovery_paths: List[Path] = []
        
        # Auto-discovery enabled by default
        self._auto_discover: bool = True
    
    def discover_tools(self, paths: Optional[List[Path]] = None) -> Dict[str, Type[BaseTool]]:
        """
        Discover all available tools from specified paths.
        
        Args:
            paths: List of paths to search for tools. If None, uses default paths.
            
        Returns:
            Dictionary mapping tool names to tool classes
        """
        if paths is None:
            # Default discovery paths - focus on the actual tools directory
            base_path = Path(__file__).parent.parent.parent
            paths = [
                base_path / "tools"  # This is where the tools actually live
            ]
        
        self._discovery_paths = paths
        discovered_tools: Dict[str, Type[BaseTool]] = {}
        
        for path in paths:
            if not path.exists():
                continue
                
            log_and_print(f"🔍 Discovering tools in: {path}")
            
            # Discover tools in this path
            for _, name, is_pkg in pkgutil.iter_modules([str(path)]):
                if is_pkg and not name.startswith('_'):
                    tool_class = self._discover_tool_class(path, name)
                    if tool_class:
                        discovered_tools[name] = tool_class
                        log_and_print(f"✅ Discovered tool: {name}")
        
        # Update registry
        self._tools.update(discovered_tools)
        self._discovered = True
        
        return discovered_tools
    
    def _discover_tool_class(self, path: Path, tool_name: str) -> Optional[Type[BaseTool]]:
        """
        Discover a specific tool class from a module.
        
        Args:
            path: Path to the tool directory
            tool_name: Name of the tool module
            
        Returns:
            Tool class if found, None otherwise
        """
        try:
            # Try to import the tool module
            module_path = f"scriptcraft.{path.name}.{tool_name}"
            module = importlib.import_module(module_path)
            
            # Look for tool class (common patterns)
            tool_class: Optional[Type[BaseTool]] = None
            
            # Pattern 1: Direct class export
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    issubclass(attr, BaseTool) and 
                    attr != BaseTool):
                    tool_class = attr
                    break
            
            # Pattern 2: Tool instance in module
            if tool_class is None:
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, BaseTool):
                        tool_class = type(attr)
                        break
            
            # Pattern 3: Main class (common naming)
            if tool_class is None:
                main_class_names = [
                    tool_name.replace('_', '').title(),
                    tool_name.title().replace('_', ''),
                    tool_name.upper(),
                    tool_name.capitalize()
                ]
                
                for class_name in main_class_names:
                    if hasattr(module, class_name):
                        attr = getattr(module, class_name)
                        if inspect.isclass(attr) and issubclass(attr, BaseTool):
                            tool_class = attr
                            break
            
            return tool_class
            
        except ImportError as e:
            log_and_print(f"⚠️ Could not import tool {tool_name}: {e}")
            return None
        except Exception as e:
            log_and_print(f"⚠️ Error discovering tool {tool_name}: {e}")
            return None
    
    def discover_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """
        Discover metadata for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolMetadata object if found, None otherwise
        """
        try:
            # Try to import the tool module
            for path in self._discovery_paths:
                if not path.exists():
                    continue
                    
                module_path = f"scriptcraft.{path.name}.{tool_name}"
                try:
                    module = importlib.import_module(module_path)
                    break
                except ImportError:
                    continue
            else:
                return None
            
            # Extract metadata from module attributes
            metadata = ToolMetadata(
                name=tool_name,
                version=getattr(module, '__version__', __version__),
                description=getattr(module, '__description__', f"🔧 {tool_name.replace('_', ' ').title()}"),
                category=getattr(module, '__category__', 'uncategorized'),
                tags=getattr(module, '__tags__', []),
                data_types=getattr(module, '__data_types__', []),
                domains=getattr(module, '__domains__', []),
                complexity=getattr(module, '__complexity__', 'simple'),
                maturity=getattr(module, '__maturity__', 'stable'),
                distribution=getattr(module, '__distribution__', 'hybrid'),
                dependencies=getattr(module, '__dependencies__', []),
                author=getattr(module, '__author__', ''),
                maintainer=getattr(module, '__maintainer__', '')
            )
            
            return metadata
            
        except Exception as e:
            log_and_print(f"⚠️ Error discovering metadata for {tool_name}: {e}")
            return None
    
    def get_tool(self, tool_name: str, create_instance: bool = True) -> Optional[Union[Type[BaseTool], BaseTool]]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            create_instance: Whether to create an instance (default: True)
            
        Returns:
            Tool class or instance, or None if not found
        """
        if tool_name not in self._tools:
            return None
        
        if create_instance:
            # Return the tool class instead of trying to instantiate it
            # Tools should be instantiated by their own constructors
            return self._tools[tool_name]
        else:
            return self._tools[tool_name]
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool."""
        if tool_name not in self._tool_metadata:
            metadata = self.discover_tool_metadata(tool_name)
            if metadata:
                self._tool_metadata[tool_name] = metadata
        
        return self._tool_metadata.get(tool_name)
    
    def list_tools(self, category: Optional[str] = None) -> Dict[str, str]:
        """
        List available tools with descriptions.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary mapping tool names to descriptions
        """
        # Auto-discover if not done yet
        if not self._discovered and self._auto_discover:
            self.discover_tools()
        
        tools = {}
        for tool_name in self._tools:
            metadata = self.get_tool_metadata(tool_name)
            if category is None or (metadata and metadata.category == category):
                description = metadata.description if metadata else f"Tool: {tool_name}"
                tools[tool_name] = description
        
        return tools
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Get tools organized by category."""
        # Auto-discover if not done yet
        if not self._discovered and self._auto_discover:
            self.discover_tools()
        
        categories: Dict[str, List[str]] = {}
        for tool_name in self._tools:
            metadata = self.get_tool_metadata(tool_name)
            category = metadata.category if metadata else "uncategorized"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        
        return categories
    
    def register_tool(self, name: str, tool_class: Type[BaseTool], metadata: Optional[ToolMetadata] = None) -> None:
        """
        Manually register a tool.
        
        Args:
            name: Tool name
            tool_class: Tool class
            metadata: Optional metadata
        """
        self._tools[name] = tool_class
        if metadata:
            self._tool_metadata[name] = metadata
        
        log_and_print(f"🔧 Manually registered tool: {name}")
    
    def register_plugin(self, plugin_type: str, name: str, plugin_class: Type, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a plugin.
        
        Args:
            plugin_type: Type of plugin
            name: Plugin name
            plugin_class: Plugin class
            metadata: Optional metadata
        """
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = {}
        
        self._plugins[plugin_type][name] = plugin_class
        
        plugin_metadata = PluginMetadata(
            name=name,
            plugin_type=plugin_type,
            description=metadata.get('description', '') if metadata else '',
            version=metadata.get('version', __version__) if metadata else __version__,
            tags=metadata.get('tags', []) if metadata else [],
            metadata=metadata or {}
        )
        
        self._plugin_metadata[name] = plugin_metadata
        log_and_print(f"🔌 Registered {plugin_type} plugin: {name}")
    
    def get_plugin(self, plugin_type: str, name: str) -> Optional[Type]:
        """Get a registered plugin."""
        return self._plugins.get(plugin_type, {}).get(name)
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> Dict[str, List[str]]:
        """List registered plugins."""
        if plugin_type:
            return {plugin_type: list(self._plugins.get(plugin_type, {}).keys())}
        
        return {pt: list(plugins.keys()) for pt, plugins in self._plugins.items()}
    
    def get_all_validators(self) -> Dict[str, Type]:
        """Get all registered validators (backward compatibility)."""
        return self._plugins.get('validator', {})
    
    def get_all_plugins(self) -> Dict[str, Dict[str, Type]]:
        """Get all registered plugins (backward compatibility)."""
        return self._plugins
    
    def run_tool(self, tool_name: str, **kwargs: Any) -> None:
        """
        Run a tool by name.
        
        Args:
            tool_name: Name of the tool to run
            **kwargs: Arguments to pass to the tool
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            available = list(self._tools.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available}")
        
        tool.run(**kwargs)
    
    def refresh(self) -> None:
        """Refresh the registry by re-discovering tools."""
        self._tools.clear()
        self._tool_instances.clear()
        self._tool_metadata.clear()
        self._discovered = False
        
        if self._auto_discover:
            self.discover_tools()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the registry state."""
        # Auto-discover if not done yet
        if not self._discovered and self._auto_discover:
            self.discover_tools()
        
        return {
            'tools': {
                'count': len(self._tools),
                'names': list(self._tools.keys()),
                'categories': self.get_tools_by_category()
            },
            'plugins': {
                'count': sum(len(plugins) for plugins in self._plugins.values()),
                'types': list(self._plugins.keys()),
                'by_type': {pt: len(plugins) for pt, plugins in self._plugins.items()}
            },
            'discovery': {
                'discovered': self._discovered,
                'paths': [str(p) for p in self._discovery_paths],
                'auto_discover': self._auto_discover
            }
        }


# Global registry instance
unified_registry = UnifiedRegistry()


# ===== CONVENIENCE FUNCTIONS =====

def get_available_tools() -> Dict[str, Type[BaseTool]]:
    """Get all available tool classes (convenience function)."""
    # Auto-discover if not done yet
    if not unified_registry._discovered and unified_registry._auto_discover:
        unified_registry.discover_tools()
    
    tools: Dict[str, Type[BaseTool]] = {}
    for name in unified_registry._tools:
        tool_class = unified_registry.get_tool(name, create_instance=False)
        if tool_class is not None and isinstance(tool_class, type) and issubclass(tool_class, BaseTool):
            tools[name] = tool_class
    return tools

def get_available_tool_instances() -> Dict[str, BaseTool]:
    """Get all available tool instances (convenience function)."""
    # Auto-discover if not done yet
    if not unified_registry._discovered and unified_registry._auto_discover:
        unified_registry.discover_tools()
    
    tools: Dict[str, BaseTool] = {}
    for name in unified_registry._tools:
        tool_class = unified_registry.get_tool(name, create_instance=False)
        if tool_class is not None and isinstance(tool_class, type) and issubclass(tool_class, BaseTool):
            try:
                # Create instance using the tool's own constructor
                tools[name] = tool_class()
            except Exception as e:
                # Log error but continue with other tools
                print(f"⚠️ Failed to instantiate {name}: {e}")
    return tools

def list_tools_by_category(category: Optional[str] = None) -> Dict[str, List[str]]:
    """List tools by category (convenience function)."""
    if category:
        return {category: unified_registry.get_tools_by_category().get(category, [])}
    return unified_registry.get_tools_by_category()

def discover_tool_metadata(tool_name: str) -> Optional[ToolMetadata]:
    """Discover metadata for a tool (convenience function)."""
    return unified_registry.get_tool_metadata(tool_name)


# ===== DECORATORS =====

def register_tool_decorator(name: str, **metadata: Any) -> Callable[[Type[BaseTool]], Type[BaseTool]]:
    """Decorator for registering tools."""
    def decorator(tool_class: Type[BaseTool]) -> Type[BaseTool]:
        tool_metadata = ToolMetadata(
            name=name,
            description=metadata.get('description', ''),
            category=metadata.get('category', 'uncategorized'),
            tags=metadata.get('tags', []),
            data_types=metadata.get('data_types', []),
            domains=metadata.get('domains', []),
            complexity=metadata.get('complexity', 'simple'),
            maturity=metadata.get('maturity', 'stable'),
            distribution=metadata.get('distribution', 'hybrid'),
            dependencies=metadata.get('dependencies', []),
            author=metadata.get('author', ''),
            maintainer=metadata.get('maintainer', '')
        )
        
        unified_registry.register_tool(name, tool_class, tool_metadata)
        return tool_class
    return decorator

def register_plugin_decorator(plugin_type: str, name: str, **metadata: Any) -> Callable[[Type], Type]:
    """Decorator for registering plugins."""
    def decorator(plugin_class: Type) -> Type:
        unified_registry.register_plugin(plugin_type, name, plugin_class, metadata)
        return plugin_class
    return decorator 
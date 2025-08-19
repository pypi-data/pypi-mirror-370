"""
Tool metadata discovery system.

This module discovers tool metadata from individual tool __init__.py files,
which is the established pattern in the codebase. This avoids duplication
and keeps metadata co-located with tool code.
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

from scriptcraft._version import __version__

class ToolMaturity(Enum):
    """Tool maturity levels."""
    EXPERIMENTAL = "experimental"  # New, may change significantly
    BETA = "beta"                 # Stable API, minor changes possible
    STABLE = "stable"             # Production ready, backwards compatible
    MATURE = "mature"             # Well-established, minimal changes
    DEPRECATED = "deprecated"     # Being phased out

class DistributionType(Enum):
    """How the tool can be distributed."""
    STANDALONE = "standalone"     # Can run independently
    PIPELINE_ONLY = "pipeline"    # Only runs as part of pipeline
    HYBRID = "hybrid"            # Both standalone and pipeline

@dataclass
class ToolMetadata:
    """
    Metadata discovered from a tool's __init__.py file.
    """
    name: str
    version: str
    description: str
    tags: List[str]
    data_types: List[str]
    domains: List[str]
    complexity: str = "simple"
    maturity: str = "stable"
    distribution: str = "hybrid"
    
    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        if self.tags is None:
            self.tags = []
        if self.data_types is None:
            self.data_types = []
        if self.domains is None:
            self.domains = []

def discover_tool_metadata(tool_name: str) -> Optional[ToolMetadata]:
    """
    Discover metadata for a specific tool from its __init__.py file.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        ToolMetadata object or None if not found
    """
    try:
        # Import the tool module
        module = importlib.import_module(f"scriptcraft.tools.{tool_name}")
        
        # Extract metadata from module attributes
        metadata = ToolMetadata(
            name=tool_name,
            version=getattr(module, '__version__', __version__),
            description=getattr(module, '__description__', f"🔧 {tool_name.replace('_', ' ').title()}"),
            tags=getattr(module, '__tags__', []),
            data_types=getattr(module, '__data_types__', []),
            domains=getattr(module, '__domains__', []),
            complexity=getattr(module, '__complexity__', 'simple'),
            maturity=getattr(module, '__maturity__', 'stable'),
            distribution=getattr(module, '__distribution__', 'hybrid')
        )
        
        return metadata
        
    except ImportError:
        return None

def discover_all_tool_metadata() -> Dict[str, ToolMetadata]:
    """
    Discover metadata for all available tools.
    
    Returns:
        Dictionary mapping tool names to their metadata
    """
    tools_metadata = {}
    
    # Get the tools directory path
    tools_dir = Path(__file__).parent
    
    # Scan all tool modules
    for _, name, is_pkg in pkgutil.iter_modules([str(tools_dir)]):
        if is_pkg and not name.startswith('_'):
            metadata = discover_tool_metadata(name)
            if metadata:
                tools_metadata[name] = metadata
    
    return tools_metadata

def get_tools_by_category() -> Dict[str, List[str]]:
    """
    Get tools organized by their tags (categories).
    
    Returns:
        Dictionary mapping categories to lists of tool names
    """
    all_metadata = discover_all_tool_metadata()
    categories: Dict[str, List[str]] = {}
    
    for tool_name, metadata in all_metadata.items():
        for tag in metadata.tags:
            if tag not in categories:
                categories[tag] = []
            categories[tag].append(tool_name)
    
    return categories

def get_tools_by_maturity(maturity: str) -> List[str]:
    """
    Get tools at a specific maturity level.
    
    Args:
        maturity: Maturity level to filter by
        
    Returns:
        List of tool names
    """
    all_metadata = discover_all_tool_metadata()
    return [
        tool_name for tool_name, metadata in all_metadata.items()
        if metadata.maturity == maturity
    ]

def get_distributable_tools() -> List[str]:
    """
    Get tools that can be distributed standalone.
    
    Returns:
        List of tool names
    """
    all_metadata = discover_all_tool_metadata()
    return [
        tool_name for tool_name, metadata in all_metadata.items()
        if metadata.distribution in ('standalone', 'hybrid')
    ]

def update_tool_metadata(tool_name: str, **updates) -> bool:
    """
    Helper to suggest metadata updates (for development use).
    
    This doesn't actually update files, but returns what should be added.
    """
    metadata = discover_tool_metadata(tool_name)
    if not metadata:
        return False
    
    suggestions = []
    for key, value in updates.items():
        attr_name = f"__{key}__"
        current_value = getattr(metadata, key, None)
        if current_value != value:
            if isinstance(value, list):
                suggestions.append(f'{attr_name} = {value}')
            else:
                suggestions.append(f'{attr_name} = "{value}"')
    
    return len(suggestions) > 0

def generate_metadata_summary() -> str:
    """Generate a summary of all tool metadata."""
    all_metadata = discover_all_tool_metadata()
    
    lines = ["# Tool Metadata Summary\n"]
    
    for tool_name, metadata in sorted(all_metadata.items()):
        lines.append(f"## {metadata.name}")
        lines.append(f"- **Version**: {metadata.version}")
        lines.append(f"- **Description**: {metadata.description}")
        lines.append(f"- **Complexity**: {metadata.complexity}")
        lines.append(f"- **Maturity**: {metadata.maturity}")
        lines.append(f"- **Distribution**: {metadata.distribution}")
        if metadata.tags:
            lines.append(f"- **Tags**: {', '.join(metadata.tags)}")
        if metadata.data_types:
            lines.append(f"- **Data Types**: {', '.join(metadata.data_types)}")
        if metadata.domains:
            lines.append(f"- **Domains**: {', '.join(metadata.domains)}")
        lines.append("")
    
    return "\n".join(lines) 
# scripts/tools/tool_dispatcher.py

"""
Tool dispatcher for managing and running tools in the scriptcraft/tools directory.

This module provides functionality to discover and dispatch tools using a
consistent interface and error handling. It now uses the unified tool interface
from the tools package.
"""

from pathlib import Path
from typing import Dict, Optional, Any
from . import get_available_tools, run_tool, discover_tool_metadata
from ..common import *
import scriptcraft.common as cu

class ToolRegistry:
    """
    Registry for managing available tools.
    
    This class now wraps the unified tool interface from tools/__init__.py
    to maintain backward compatibility.
    """
    
    def __init__(self) -> None:
        # Use the unified tool discovery system
        pass
    
    def get_tool(self, tool_name: str) -> Optional[cu.BaseTool]:
        """
        Get a tool instance by name.
        
        Args:
            tool_name: Name of the tool to get
        
        Returns:
            Optional[BaseTool]: Tool instance if found, None otherwise
        """
        try:
            tools = get_available_tools()
            return tools.get(tool_name)
        except Exception as e:
            cu.log_and_print(f"❌ Failed to get tool '{tool_name}': {e}")
            return None
    
    def list_tools(self) -> Dict[str, str]:
        """
        Get a dictionary of available tools.
        
        Returns:
            Dict[str, str]: Dictionary mapping tool names to descriptions
        """
        try:
            tools = get_available_tools()
            # Return tool names mapped to descriptions for backward compatibility
            result = {}
            for tool_name, tool_instance in tools.items():
                metadata = discover_tool_metadata(tool_name)
                result[tool_name] = metadata.get("description", f"Tool: {tool_name}")
            return result
        except Exception as e:
            cu.log_and_print(f"❌ Failed to list tools: {e}")
            return {}

# Create singleton registry
registry = ToolRegistry()

def dispatch_tool(tool_name: str, args: Any) -> None:
    """
    Dispatch a tool based on CLI args.
    
    Args:
        tool_name: Name of the tool to run
        args: Parsed command line arguments
    """
    try:
        # Convert input paths to list if provided
        input_paths = None
        if hasattr(args, 'input'):
            if isinstance(args.input, (str, Path)):
                input_paths = [args.input]
            else:
                input_paths = args.input
        
        # Get the tool class
        tool_class = registry.get_tool(tool_name)
        if tool_class is None:
            raise ValueError(f"Tool '{tool_name}' not found.")
        tool_instance = tool_class()  # Instantiate the tool
        tool_instance.run(
            mode=getattr(args, "mode", None),
            input_paths=input_paths,
            output_dir=getattr(args, "output", "output"),
            domain=getattr(args, "domain", None),
            output_filename=getattr(args, "output_filename", None)
        )
    except Exception as e:
        cu.log_and_print(f"\u274c Error running tool '{tool_name}': {e}")
        raise

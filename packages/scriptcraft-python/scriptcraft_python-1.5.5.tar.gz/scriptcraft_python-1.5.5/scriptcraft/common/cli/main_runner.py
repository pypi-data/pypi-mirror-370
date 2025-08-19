"""
Unified Main Runner for ScriptCraft Tools

This module provides a standardized way to run tools from both development
and distributable environments. It consolidates CLI patterns and eliminates
duplication across tools.

Usage:
    # In __main__.py files:
    from scriptcraft.common.cli.main_runner import run_tool_main
    
    if __name__ == "__main__":
        run_tool_main("tool_name", "Tool description")
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Callable, Any, Dict, List, Union, Type
from abc import ABC, abstractmethod

from ..logging import setup_logger, log_and_print
from ..core import BaseTool
from .argument_parsers import ParserFactory


class ToolRunner(ABC):
    """Abstract base class for tool runners."""
    
    @abstractmethod
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for this tool."""
        pass
    
    @abstractmethod
    def run_tool(self, args: argparse.Namespace, **kwargs) -> bool:
        """Run the tool with the given arguments."""
        pass


class StandardToolRunner(ToolRunner):
    """Standard tool runner that works with BaseTool subclasses."""
    
    def __init__(self, tool_class: Type[BaseTool], tool_name: str, description: str) -> None:
        self.tool_class = tool_class
        self.tool_name = tool_name
        self.description = description
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create a standard argument parser."""
        parser = ParserFactory.create_tool_parser(self.tool_name, self.description)
        
        # Add tool-specific arguments if the tool class has them
        if hasattr(self.tool_class, 'add_cli_arguments'):
            self.tool_class.add_cli_arguments(parser)
        
        return parser
    
    def run_tool(self, args: argparse.Namespace, **kwargs) -> bool:
        """Run the tool with standard BaseTool interface."""
        try:
            # Create tool instance with required arguments
            tool = self.tool_class(name=self.tool_name, description=self.description)
            
            # Convert args to kwargs for tool.run()
            tool_kwargs: Dict[str, Any] = vars(args)
            
            # Handle special cases
            if hasattr(args, 'input_paths') and args.input_paths:
                tool_kwargs['input_paths'] = args.input_paths
            
            # Run the tool
            tool.run(**tool_kwargs, **kwargs)
            return True
            
        except Exception as e:
            log_and_print(f"❌ {self.tool_name} failed: {e}", level="error")
            return False


class CustomToolRunner(ToolRunner):
    """Custom tool runner for tools that need special handling."""
    
    def __init__(self, create_parser_func: Callable[[], argparse.ArgumentParser], 
                 run_func: Callable[[argparse.Namespace], bool]) -> None:
        self.create_parser_func = create_parser_func
        self.run_func = run_func
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser using the provided function."""
        return self.create_parser_func()
    
    def run_tool(self, args: argparse.Namespace, **kwargs) -> bool:
        """Run tool using the provided function."""
        try:
            return self.run_func(args, **kwargs)
        except Exception as e:
            log_and_print(f"❌ Tool failed: {e}", level="error")
            return False


def run_tool_main(tool_name: str, description: str, 
                  tool_class: Optional[Type[BaseTool]] = None,
                  create_parser_func: Optional[Callable[[], argparse.ArgumentParser]] = None,
                  run_func: Optional[Callable[[argparse.Namespace], bool]] = None,
                  **kwargs) -> int:
    """
    Main entry point for tool execution.
    
    Args:
        tool_name: Name of the tool
        description: Tool description
        tool_class: BaseTool subclass (for standard tools)
        create_parser_func: Function to create custom parser
        run_func: Function to run custom tool logic
        **kwargs: Extra arguments to forward to tool.run()
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Create appropriate runner
        if tool_class and issubclass(tool_class, BaseTool):
            runner: ToolRunner = StandardToolRunner(tool_class, tool_name, description)
        elif create_parser_func and run_func:
            runner = CustomToolRunner(create_parser_func, run_func)
        else:
            raise ValueError("Must provide either tool_class or both create_parser_func and run_func")
        
        # Create parser and parse arguments
        parser = runner.create_parser()
        args = parser.parse_args()
        
        # Set up logging
        logger = setup_logger(tool_name)
        log_and_print(f"🚀 Starting {tool_name}...")
        
        # Run the tool (pass extra kwargs)
        success = runner.run_tool(args, **kwargs)
        
        if success:
            log_and_print(f"✅ {tool_name} completed successfully")
            return 0
        else:
            log_and_print(f"❌ {tool_name} failed")
            return 1
            
    except KeyboardInterrupt:
        log_and_print("🛑 Tool interrupted by user")
        return 1
    except Exception as e:
        log_and_print(f"❌ Fatal error: {e}", level="error")
        return 1


def run_tool_from_cli(tool_name: str, description: str, 
                     tool_class: Optional[Type[BaseTool]] = None,
                     **kwargs: Any) -> None:
    """
    Convenience function for running tools from CLI.
    Exits with appropriate code.
    """
    exit_code = run_tool_main(tool_name, description, tool_class, **kwargs)
    sys.exit(exit_code)


# ===== LEGACY SUPPORT =====

def create_standard_parser(tool_name: str, description: str) -> argparse.ArgumentParser:
    """Create a standard parser for backward compatibility."""
    return ParserFactory.create_tool_parser(tool_name, description)


def run_with_standard_args(tool_class: Type[BaseTool], tool_name: str, description: str) -> int:
    """Run a tool with standard argument parsing for backward compatibility."""
    return run_tool_main(tool_name, description, tool_class=tool_class) 
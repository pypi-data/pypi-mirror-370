"""
Centralized argument parser definitions for consistent CLI interfaces.
Provides reusable argument groups and parser factories to maintain DRY principles.
"""

import argparse
import sys
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from ..logging import log_and_print


class ArgumentGroups:
    """Reusable argument group definitions."""
    
    @staticmethod
    def add_common_args(parser: argparse.ArgumentParser) -> None:
        """Add common arguments used across most tools and pipelines."""
        parser.add_argument("--config", default="config.yaml", 
                          help="Path to config file (default: config.yaml)")
        parser.add_argument("--workspace", default="development",
                          help="Workspace to use (default: development)")
        parser.add_argument("--debug", action="store_true", 
                          help="Enable debug logging")
        parser.add_argument("--dry-run", action="store_true", 
                          help="Preview actions without executing them")
        parser.add_argument("--verbose", action="store_true", 
                          help="Enable verbose output")
    
    @staticmethod
    def add_pipeline_args(parser: argparse.ArgumentParser) -> None:
        """Add pipeline-specific arguments."""
        parser.add_argument("--pipeline", 
                          help="Pipeline to run (e.g., full, test)")
        parser.add_argument("--tag", type=str,
                          help="Run only steps with this tag")
        parser.add_argument("--domain", type=str,
                          help="Specify domain for 'single_domain' run mode")
        parser.add_argument("--time", action="store_true",
                          help="Show timing information")
        
    @staticmethod
    def add_supplement_args(parser: argparse.ArgumentParser) -> None:
        """Add supplement-related arguments."""
        parser.add_argument("--prepare-supplement", action="store_true",
                          help="Include supplement prepper step")
        parser.add_argument("--merge-supplement", action="store_true",
                          help="Include supplement splitter step")
    
    @staticmethod
    def add_tool_args(parser: argparse.ArgumentParser) -> None:
        """Add tool-specific arguments."""
        parser.add_argument("--tool", type=str,
                          help="Run a specific tool (e.g., data_comparer, rhq_checker)")
        parser.add_argument("--mode", type=str,
                          help="Tool mode (e.g., standard, rhq). Required if --tool is used")
    
    @staticmethod
    def add_io_args(parser: argparse.ArgumentParser) -> None:
        """Add input/output related arguments."""
        parser.add_argument("--input-path", type=str,
                          help="Input file or directory path")
        parser.add_argument("--output-dir", type=str, default="output",
                          help="Output directory (default: output)")
        parser.add_argument("--output-filename", type=str,
                          help="Specific output filename")
    
    @staticmethod
    def add_listing_args(parser: argparse.ArgumentParser) -> None:
        """Add arguments for listing available options."""
        parser.add_argument("--list", action="store_true",
                          help="List available options and exit")
    
    @staticmethod
    def add_tool_io_args(parser: argparse.ArgumentParser, input_paths_required: bool = True) -> None:
        """Add tool I/O specific arguments."""
        if input_paths_required:
            parser.add_argument("input_paths", nargs='+',
                              help="Input file paths.")
        else:
            parser.add_argument("--input-paths", nargs='+',
                              help="Input file paths (optional for some modes).")
        
        # Try to get config-based default output directory
        default_output_dir = "data/output"  # Default fallback
        try:
            import scriptcraft.common as cu
            config = cu.get_config()
            if config:
                workspace_config = config.get_workspace_config()
                if workspace_config and hasattr(workspace_config, 'paths'):
                    workspace_paths = workspace_config.paths
                    if isinstance(workspace_paths, dict) and 'output_dir' in workspace_paths:
                        default_output_dir = workspace_paths['output_dir']
        except Exception:
            pass  # Use fallback if config loading fails
        
        parser.add_argument("--output-dir", default=default_output_dir,
                          help=f"Output directory (default: {default_output_dir}).")
        parser.add_argument("--domain",
                          help="Domain name (e.g., Clinical, Biomarkers).")
        parser.add_argument("--output-filename",
                          help="Output filename (default: auto-generated).")
        parser.add_argument("--mode", 
                          help="Tool mode (e.g., standard, custom).")
    
    @staticmethod
    def add_dictionary_workflow_args(parser: argparse.ArgumentParser) -> None:
        """Add dictionary workflow specific arguments."""
        parser.add_argument("--dictionary-paths", nargs='+', required=True,
                          help="Dictionary file paths to enhance.")
        parser.add_argument("--workflow-steps", nargs='+', 
                          choices=['prepare', 'split', 'enhance'],
                          default=['prepare', 'split', 'enhance'],
                          help="Workflow steps to run (default: all steps).")
        parser.add_argument("--merge-strategy", 
                          choices=['outer', 'inner', 'left', 'right'],
                          default='outer',
                          help="Strategy for merging supplements (default: outer).")
        parser.add_argument("--enhancement-strategy", 
                          choices=['append', 'merge', 'replace'],
                          default='append',
                          help="Strategy for enhancing dictionaries (default: append).")
        parser.add_argument("--domain-column", default='domain',
                          help="Column name containing domain information (default: domain).")
        parser.add_argument("--clean-data", action='store_true', default=True,
                          help="Clean data during processing (default: True).")
        parser.add_argument("--no-clean-data", action='store_false', dest='clean_data',
                          help="Disable data cleaning during processing.")


class ParserFactory:
    """Factory for creating different types of argument parsers."""
    
    @staticmethod
    def create_pipeline_parser(description: str = "Pipeline & Tool Controller") -> argparse.ArgumentParser:
        """Create a parser for pipeline operations."""
        parser = argparse.ArgumentParser(description=f"📊 {description}")
        
        ArgumentGroups.add_common_args(parser)
        ArgumentGroups.add_pipeline_args(parser)
        ArgumentGroups.add_supplement_args(parser)
        ArgumentGroups.add_tool_args(parser)
        ArgumentGroups.add_listing_args(parser)
        
        return parser
    
    @staticmethod
    def create_tool_parser(tool_name: str, description: Optional[str] = None) -> argparse.ArgumentParser:
        """Create a parser for tool operations."""
        desc = description or f"{tool_name} Tool"
        parser = argparse.ArgumentParser(description=f"🛠️ {desc}")
        
        ArgumentGroups.add_common_args(parser)
        ArgumentGroups.add_io_args(parser)
        
        return parser
    
    @staticmethod
    def create_standard_tool_parser(tool_name: str, description: Optional[str] = None, input_paths_required: bool = True) -> argparse.ArgumentParser:
        """Create a standard parser for tools with common I/O patterns."""
        desc = description or f"{tool_name} Tool"
        parser = argparse.ArgumentParser(description=f"🛠️ {desc}")
        
        ArgumentGroups.add_tool_io_args(parser, input_paths_required=input_paths_required)
        
        return parser
    
    @staticmethod
    def create_dictionary_workflow_parser(tool_name: str, description: Optional[str] = None) -> argparse.ArgumentParser:
        """Create a parser for dictionary workflow tools."""
        desc = description or f"{tool_name} Tool"
        parser = argparse.ArgumentParser(description=f"📚 {desc}")
        
        ArgumentGroups.add_tool_io_args(parser)
        ArgumentGroups.add_dictionary_workflow_args(parser)
        
        return parser
    
    @staticmethod
    def create_main_parser(description: str = "Main Application") -> argparse.ArgumentParser:
        """Create a parser for main application entry point."""
        parser = argparse.ArgumentParser(description=description)
        
        ArgumentGroups.add_common_args(parser)
        ArgumentGroups.add_pipeline_args(parser)
        ArgumentGroups.add_tool_args(parser)
        ArgumentGroups.add_listing_args(parser)
        
        return parser


class ArgumentValidator:
    """Validation utilities for parsed arguments."""
    
    @staticmethod
    def validate_required_args(args: argparse.Namespace, required: List[str]) -> bool:
        """Validate that required arguments are present."""
        missing = [arg for arg in required if not getattr(args, arg.replace('-', '_'), None)]
        if missing:
            print(f"❌ Missing required arguments: {', '.join(missing)}")
            return False
        return True
    
    @staticmethod
    def validate_file_exists(file_path: Optional[str]) -> bool:
        """Validate that a file path exists."""
        if file_path and not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return False
        return True
    
    @staticmethod
    def ensure_output_dir(output_dir: str) -> Path:
        """Ensure output directory exists and return Path object."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


def create_standard_main_function(tool_class: type, tool_name: str, description: str) -> Callable[[], None]:
    """
    Create a standard main function for tools.
    
    Args:
        tool_class: The tool class to instantiate
        tool_name: Name of the tool for argument parsing
        description: Description of the tool
        
    Returns:
        A main function that can be used as the entry point
    """
    def main() -> None:
        """Standard main entry point for tools."""
        try:
            # Parse arguments
            parser = ParserFactory.create_standard_tool_parser(tool_name, description)
            args = parser.parse_args()
            
            # Create and run tool
            tool = tool_class()
            tool.run(
                input_paths=args.input_paths,
                output_dir=args.output_dir,
                domain=args.domain,
                output_filename=args.output_filename,
                mode=args.mode
            )
            
        except KeyboardInterrupt:
            log_and_print("🛑 Interrupted by user")
            sys.exit(1)
        except Exception as e:
            log_and_print(f"❌ Fatal error: {e}", level="error")
            sys.exit(1)
    
    return main


# Convenience functions for common parser patterns
def parse_pipeline_args(description: Optional[str] = None) -> argparse.Namespace:
    """Parse arguments for pipeline operations."""
    parser = ParserFactory.create_pipeline_parser(description or "Pipeline & Tool Controller")
    return parser.parse_args()


def parse_tool_args(tool_name: str, description: Optional[str] = None) -> argparse.Namespace:
    """Parse arguments for tool operations."""
    parser = ParserFactory.create_tool_parser(tool_name, description)
    return parser.parse_args()


def parse_standard_tool_args(tool_name: str, description: Optional[str] = None, input_paths_required: bool = True) -> argparse.Namespace:
    """Parse arguments for standard tool operations."""
    parser = ParserFactory.create_standard_tool_parser(tool_name, description, input_paths_required=input_paths_required)
    return parser.parse_args()


def parse_dictionary_workflow_args(tool_name: str, description: Optional[str] = None) -> argparse.Namespace:
    """Parse arguments for dictionary workflow tool operations."""
    parser = ParserFactory.create_dictionary_workflow_parser(tool_name, description)
    return parser.parse_args()


def parse_main_args(description: Optional[str] = None) -> argparse.Namespace:
    """Parse arguments for main application."""
    parser = ParserFactory.create_main_parser(description or "Main Application")
    return parser.parse_args()


# Export commonly used parsers
__all__ = [
    'ArgumentGroups',
    'ParserFactory', 
    'ArgumentValidator',
    'create_standard_main_function',
    'parse_pipeline_args',
    'parse_tool_args',
    'parse_standard_tool_args',
    'parse_dictionary_workflow_args',
    'parse_main_args'
] 
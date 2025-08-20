"""
Centralized CLI utilities for consistent command-line interfaces.
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .argument_parsers import *
from .main_runner import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Argument parsing
#     'ArgumentGroups', 'ParserFactory', 'ArgumentValidator',
#     'create_standard_main_function', 'parse_pipeline_args',
#     'parse_tool_args', 'parse_standard_tool_args',
#     'parse_dictionary_workflow_args', 'parse_main_args',
#     # Main runner
#     'main'
# ]

def main() -> None:
    """Main entry point for ScriptCraft CLI."""
    from scriptcraft.common.registry import get_available_tool_instances
    print("🚀 ScriptCraft CLI")
    print("Available commands:")
    print("  scriptcraft --help         Show detailed help")
    print("  scriptcraft tools          List available tools")
    print("  scriptcraft run <tool>     Run a specific tool")
    print("")
    print("Available tools:")
    tools = get_available_tool_instances()
    for tool_name, tool_instance in tools.items():
        print(f"  - {tool_name}: {getattr(tool_instance, 'description', 'No description')}")
    print("")
    print("Or import directly in Python:")
    print("  from scriptcraft import setup_logger, Config, BaseTool") 
"""
ScriptCraft - Data processing and quality control tools for research.

This package provides a comprehensive framework for data processing, validation,
and quality control, specifically designed for research data workflows.

Quick Start:
    # For internal development (recommended)
    import scriptcraft.common as cu
    
    # Create a tool
    class MyTool(cu.BaseTool):
        def run(self, input_paths, output_dir=None, **kwargs):
            # Your logic here
            pass
    
    # Load configuration
    config = cu.Config.from_yaml("config.yaml")
    
    # Setup logging
    logger = cu.setup_logger("my_tool")

Import Patterns:
    # Pattern 1: Import everything (internal use)
    import scriptcraft.common as cu
    cu.BaseTool, cu.load_data, cu.setup_logger
    
    # Pattern 2: Import specific items (external use)
    from scriptcraft.common import BaseTool, Config, setup_logger
    
    # Pattern 3: Import tools directly
    from scriptcraft.tools import RHQFormAutofiller

Common Utilities:
    from scriptcraft.common import (
        # Core functionality
        BaseTool, Config, load_config,
        
        # Logging
        setup_logger, log_and_print,
        
        # Data operations
        load_data, ensure_output_dir, compare_dataframes,
        
        # Path utilities
        get_project_root, resolve_path
    )

Tools:
    from scriptcraft.tools import (
        # Automation
        RHQFormAutofiller,
        
        # Data Processing
        DataContentComparer, SchemaDetector,
        
        # Validation
        DictionaryDrivenChecker, ReleaseConsistencyChecker,
        
        # Transformation
        DictionaryCleaner, DateFormatStandardizer
    )

Tool Discovery:
    from scriptcraft.tools import get_available_tools, list_tools_by_category
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
# Import version info from centralized location
from ._version import __version__, __author__

# Import the most commonly used utilities
from .common import (
    # Core functionality
    BaseTool, Config, load_config,
    
    # Logging
    setup_logger, log_and_print
)

# Make tools discoverable
from . import tools
from . import pipelines

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Version info
#     "__version__", "__author__",
#     
#     # Core classes
#     "BaseTool", "Config", "load_config",
#     
#     # Logging
#     "setup_logger", "log_and_print", 
#     
#     # Sub-packages
#     "tools", "pipelines"
# ]

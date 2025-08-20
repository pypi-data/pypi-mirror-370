"""
📊 Data Content Comparer Tool

This tool compares the content of two datasets and generates a detailed report
of their differences, including column differences, data type mismatches,
value discrepancies, and missing or extra rows.

Usage:
    Development: python -m scriptcraft.tools.data_content_comparer.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# === Environment Detection & Import Setup ===
# Import the environment detection module
from .env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment with fallback
try:
    if IS_DISTRIBUTABLE:
        # Distributable imports - use cu pattern for consistency
        import common as cu
    else:
        # Development imports - use cu pattern for consistency
        import scriptcraft.common as cu
except ImportError:
    # Fallback: try scriptcraft.common in both environments
    try:
        import scriptcraft.common as cu
    except ImportError:
        # Last resort: try relative import
        from .. import common as cu

# Import utils (same in both environments since it's local)
try:
    from .utils import (
        load_datasets_as_list, compare_datasets, generate_report, load_mode
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        load_datasets_as_list, compare_datasets, generate_report, load_mode
    )


class DataContentComparer(cu.BaseTool):
    """Tool for comparing content between datasets."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Data Content Comparer",
            description="📊 Compares content between datasets and generates detailed reports",
            tool_name="data_content_comparer"
        )
        
        # Set up file logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up file logging for the tool."""
        try:
            if self.config:
                # Get log directory from config
                workspace_config = self.config.get_workspace_config()
                if workspace_config and hasattr(workspace_config, 'logging'):
                    log_config = workspace_config.logging
                    if isinstance(log_config, dict) and 'log_dir' in log_config:
                        log_dir = Path(log_config['log_dir'])
                    else:
                        log_dir = Path("data/logs")
                else:
                    log_dir = Path("data/logs")
            else:
                log_dir = Path("data/logs")
            
            # Ensure log directory exists
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up logging with timestamp
            from scriptcraft.common.logging import setup_logging_with_timestamp
            log_file = setup_logging_with_timestamp(log_dir, mode="data_content_comparer")
            
            cu.log_and_print(f"📝 Logging to: {log_file}")
            
        except Exception as e:
            cu.log_and_print(f"⚠️ Could not set up file logging: {e}", level="warning")
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """
        Run the data content comparison.
        
        Args:
            mode: Comparison mode (e.g., 'standard', 'rhq', 'domain', 'release_consistency', 'release')
            input_paths: List containing paths to the datasets to compare
            output_dir: Directory to save comparison reports
            domain: Optional domain to filter comparison
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - comparison_type: Type of comparison to perform
                - output_format: Format for the output report
                - debug: Enable debug mode (for release_consistency mode)
        """
        self.log_start()
        
        try:
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Load and run the appropriate plugin
            from .plugins import get_plugin, list_plugins
            
            # Set default mode if not specified
            if not mode:
                mode = "standard"
            
            # Get the plugin function
            plugin_func = get_plugin(mode)
            
            if not plugin_func:
                available_modes = list_plugins()
                raise ValueError(f"❌ Unknown mode '{mode}'. Available modes: {available_modes}")
            
            # For release_consistency mode, we don't require exactly 2 input files
            if mode in ["release_consistency", "release"]:
                # Release consistency mode can work with domain-only or manual files
                if input_paths and len(input_paths) >= 2:
                    # Manual file comparison mode
                    cu.log_and_print(f"📁 Manual file comparison mode with {len(input_paths)} files")
                elif domain:
                    # Domain-based comparison mode
                    cu.log_and_print(f"📊 Domain-based comparison for: {domain}")
                else:
                    # Default to all domains
                    cu.log_and_print("📊 Processing all available domains")
            else:
                # For other modes, validate input files
                if not self.validate_input_files(input_paths or [], required_count=2):
                    raise ValueError("❌ Need at least two input files to compare")
            
            # Run the plugin
            cu.log_and_print(f"🔧 Running {mode} mode...")
            plugin_func(
                input_paths=input_paths or [],
                output_dir=output_path,
                domain=domain,
                **kwargs
            )
            
            self.log_completion(output_path)
            
        except Exception as e:
            self.log_error(f"Comparison failed: {e}")
            raise


def main():
    """Main entry point for the data content comparer tool."""
    import sys
    # For release_consistency mode, input_paths is optional (can use domain-based discovery)
    # Check if release_consistency mode is being used
    release_consistency_mode = "--mode" in sys.argv and ("release_consistency" in sys.argv or "release" in sys.argv)
    input_paths_required = not release_consistency_mode
    
    args = cu.parse_standard_tool_args(
        "data_content_comparer",
        "📊 Compares content between datasets and generates detailed reports",
        input_paths_required=input_paths_required
    )
    # Create and run the tool
    tool = DataContentComparer()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main() 
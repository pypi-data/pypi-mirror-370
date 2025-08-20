"""
🔍 Dictionary-Driven Checker Tool

A flexible checker that validates data against dictionaries using configurable plugins.
Supports multiple validation types and provides detailed reporting.

Usage:
    Development: python -m scriptcraft.tools.dictionary_driven_checker.main [args]
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

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports - use cu pattern for consistency
    import common as cu
else:
    # Development imports - use cu pattern for consistency
    import scriptcraft.common as cu

# Import utils (same in both environments since it's local)
try:
    from .utils import run_dictionary_checker
except ImportError:
    # If utils import fails, try current directory
    from .utils import run_dictionary_checker


def initialize_plugins(config: Any) -> None:
    """Initialize plugin system with configuration."""
    # Register any additional plugins from config
    # Config object doesn't have .get() method, so we need to access attributes directly
    plugin_settings = getattr(config, 'plugins', {}) if hasattr(config, 'plugins') else {}
    validators = cu.plugin_registry.get_all_plugins('validator')
    for plugin_type, settings in plugin_settings.items():
        if plugin_type in validators:
            validator = validators[plugin_type]
            for key, value in settings.items():
                setattr(validator, key, value)


class DictionaryDrivenChecker(cu.BaseTool):
    """Tool for validating data against a data dictionary using plugins."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Dictionary Driven Checker",
            description="🔍 Validates data against a data dictionary using configurable plugins",
            tool_name="dictionary_driven_checker"
        )
        
        # Get tool-specific configuration
        tool_config = self.get_tool_config()
        self.outlier_method = tool_config.get("outlier_detection", "IQR")
        
        # Initialize plugins
        initialize_plugins(self.config)
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """
        Run the dictionary-driven validation process.
        
        Args:
            mode: Validation mode (e.g., 'standard', 'strict')
            input_paths: List containing paths to the data files to validate
            output_dir: Directory to save validation results
            domain: Domain to validate (e.g., "Biomarkers", "Clinical")
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - dictionary_path: Path to dictionary file
                - outlier_method: Outlier detection method
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or []):
                raise ValueError("❌ No input files provided")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Get validation settings
            outlier_method = kwargs.get('outlier_method', self.outlier_method)
            dictionary_path = kwargs.get('dictionary_path')
            
            # Process each input file
            for input_path in input_paths:
                cu.log_and_print(f"🔍 Validating: {input_path}")
                
                # Load data using DRY method
                data = self.load_data_file(input_path)
                
                # Determine dictionary path
                if dictionary_path:
                    dict_path = Path(dictionary_path)
                else:
                    # Auto-discover dictionary based on domain
                    dict_path = self._find_dictionary_file(input_path, domain)
                
                if not dict_path.exists():
                    raise FileNotFoundError(f"Dictionary not found: {dict_path}")
                
                # Load dictionary using DRY method
                cu.log_and_print(f"📂 Loading dictionary: {dict_path}")
                dict_data = self.load_data_file(dict_path)
                
                # Normalize column names
                data.columns = cu.normalize_column_names(data.columns)
                dict_data.columns = cu.normalize_column_names(dict_data.columns)
                
                # Run validation
                cu.log_and_print(f"🔄 Running validation for {domain or 'dataset'}...")
                run_dictionary_checker(
                    df=data,
                    dict_df=dict_data,
                    domain=domain or "unknown",
                    output_path=output_path,
                    outlier_method=cu.OutlierMethod[outlier_method.upper()]
                )
                
                cu.log_and_print(f"✅ Validation completed: {output_path}")
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Dictionary validation failed: {e}")
            raise
    
    def _find_dictionary_file(self, input_path: Union[str, Path], domain: Optional[str]) -> Path:
        """Find the appropriate dictionary file for the given input and domain."""
        input_path = Path(input_path)
        
        # Try domain-specific dictionary first
        if domain:
            dict_name = f"{domain}_dictionary.csv"
            dict_path = input_path.parent / dict_name
            if dict_path.exists():
                return dict_path
            
            # Try Excel version
            dict_path = input_path.parent / f"{domain}_dictionary.xlsx"
            if dict_path.exists():
                return dict_path
        
        # Try generic dictionary files
        for dict_name in ["dictionary.csv", "dictionary.xlsx", "data_dictionary.csv", "data_dictionary.xlsx"]:
            dict_path = input_path.parent / dict_name
            if dict_path.exists():
                return dict_path
        
        # If no dictionary found, raise error
        raise FileNotFoundError(f"No dictionary file found for {input_path}")


def main():
    """Main entry point for the dictionary driven checker tool."""
    args = cu.parse_tool_args("🔍 Validates data against a data dictionary using configurable plugins")
    
    # Create and run the tool
    tool = DictionaryDrivenChecker()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main() 
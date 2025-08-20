"""
📅 Date Format Standardizer Tool

Standardizes date formats across datasets by detecting and converting various
date representations to consistent formats.

Usage:
    Development: python -m scriptcraft.tools.date_format_standardizer.main [args]
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


class DateFormatStandardizer(cu.BaseTool):
    """Tool for standardizing date formats in datasets."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Date Format Standardizer",
            description="📅 Standardizes date formats in datasets to ensure consistency",
            tool_name="date_format_standardizer"
        )
    
    def run(self, 
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> bool:
        """
        Run the date format standardizer.
        
        Args:
            input_paths: List of input file paths
            output_dir: Output directory
            domain: Domain name
            output_filename: Output filename
            **kwargs: Additional arguments
            
        Returns:
            True if successful, False otherwise
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or []):
                raise ValueError("❌ No input files provided")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Process each input file
            for input_path in input_paths:
                cu.log_and_print(f"📅 Processing: {input_path}")
                
                # Load data using DRY method
                data = self.load_data_file(input_path)
                
                # Transform date formats
                cu.log_and_print(f"🔄 Standardizing date formats for {domain or 'dataset'}...")
                transformed_data = self._standardize_dates(data, domain)
                
                # Generate output filename using DRY method
                if not output_filename:
                    output_filename = self.get_output_filename(
                        input_path, 
                        suffix="date_standardized"
                    )
                
                # Save data using DRY method
                output_file = output_path / output_filename
                self.save_data_file(transformed_data, output_file, include_index=False)
                
                cu.log_and_print(f"✅ Date standardization completed: {output_file}")
            
            self.log_completion()
            return True
            
        except Exception as e:
            self.log_error(f"Date format standardization failed: {e}")
            return False
    
    def _standardize_dates(self, data: Any, domain: Optional[str] = None) -> Any:
        """
        Standardize date formats in the dataset.
        
        Args:
            data: DataFrame to transform
            domain: The domain being processed
            
        Returns:
            Transformed DataFrame
        """
        # Use the common utility for date standardization
        return cu.standardize_dates_in_dataframe(data)


def main():
    """Main entry point for the date format standardizer tool."""
    args = cu.parse_tool_args("📅 Standardizes date formats in datasets to ensure consistency")
    
    # Create and run the tool
    tool = DateFormatStandardizer()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename
    )


if __name__ == "__main__":
    main() 
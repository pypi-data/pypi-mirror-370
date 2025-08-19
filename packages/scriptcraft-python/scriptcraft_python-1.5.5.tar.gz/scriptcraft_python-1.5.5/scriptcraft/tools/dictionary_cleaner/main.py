"""
🧹 Dictionary Cleaner Tool

This tool standardizes and validates dictionary entries, including normalizing value types,
standardizing expected values, and ensuring consistent formatting across all dictionary fields.

Usage:
    Development: python -m scriptcraft.tools.dictionary_cleaner.main [args]
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
    from .utils import (
        clean_data, parse_values, fix_language_blocks,
        convert_numeric_keys_to_ints
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        clean_data, parse_values, fix_language_blocks,
        convert_numeric_keys_to_ints
    )


# Standard mappings for value types
VALUE_TYPE_MAP = {
    "numeric": "numeric",
    "number": "numeric",
    "float": "numeric",
    "int": "numeric",
    "integer": "numeric",
    "categorical": "categorical",
    "category": "categorical",
    "text": "text",
    "string": "text",
    "date": "date",
    "datetime": "date",
    "timestamp": "date"
}


class DictionaryCleaner(cu.BaseTool):
    """Tool for cleaning and standardizing data dictionary entries."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Dictionary Cleaner",
            description="🧹 Cleans and standardizes data dictionary entries including value types and expected values",
            tool_name="dictionary_cleaner",
            supported_formats=['.csv', '.xlsx', '.xls']
        )
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """
        Run the dictionary cleaning process.
        
        Args:
            mode: Cleaning mode (e.g., 'standard', 'aggressive')
            input_paths: List containing paths to the dictionary files to clean
            output_dir: Directory to save cleaned dictionaries
            domain: Optional domain to filter cleaning
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - cleaning_level: Level of cleaning to apply
                - output_format: Format for the output data
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or []):
                raise ValueError("❌ No input files provided")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Get cleaning settings
            cleaning_level = kwargs.get('cleaning_level', 'standard')
            output_format = kwargs.get('output_format', 'excel')
            
            # Process each input file
            for input_path in input_paths:
                cu.log_and_print(f"🧹 Processing dictionary: {input_path}")
                
                # Load data using DRY method
                data = self.load_data_file(input_path)
                
                # Clean dictionary
                cu.log_and_print(f"🔄 Cleaning dictionary for {domain or 'dataset'}...")
                cleaned_data = self._clean_dictionary(data, cleaning_level)
                
                # Generate output filename using DRY method
                if not output_filename:
                    output_filename = self.get_output_filename(
                        input_path, 
                        suffix="cleaned"
                    )
                
                # Save data using DRY method
                output_file = output_path / output_filename
                self.save_data_file(cleaned_data, output_file, include_index=False)
                
                cu.log_and_print(f"✅ Dictionary cleaning completed: {output_file}")
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Dictionary cleaning failed: {e}")
            raise
    
    def _clean_dictionary(self, df: Any, cleaning_level: str = 'standard') -> Any:
        """
        Clean and standardize dictionary entries.
        
        Args:
            df: Input dictionary DataFrame
            cleaning_level: Level of cleaning to apply
        
        Returns:
            Cleaned dictionary DataFrame
        """
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        
        # Clean and standardize each column
        for col in ["Main Variable", "Value Type", "Expected Values"]:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(lambda x: x.strip())
        
        # Standardize value types
        if "Value Type" in df.columns:
            df["Value Type"] = df["Value Type"].str.lower().map(VALUE_TYPE_MAP).fillna("text")
        
        # Handle expected values based on type
        if "Expected Values" in df.columns:
            df["Expected Values"] = df.apply(self._clean_expected_values, axis=1)
        
        return df
    
    def _clean_expected_values(self, row: Any) -> str:
        """
        Clean and standardize expected values based on value type.
        
        Args:
            row: Dictionary row with Value Type and Expected Values
        
        Returns:
            str: Cleaned expected values
        """
        if cu.is_missing_like(row["Expected Values"]):
            return row["Expected Values"]
        
        val_type = row["Value Type"]
        values = str(row["Expected Values"]).strip()
        
        if val_type == "numeric":
            # Standardize numeric ranges
            if "-" in values:
                try:
                    min_val, max_val = map(float, values.split("-"))
                    return f"{min_val}-{max_val}"
                except:
                    return values
            return values
            
        elif val_type == "categorical":
            # Standardize categorical lists
            items = [v.strip() for v in values.split(",")]
            return ", ".join(sorted(set(items)))
            
        elif val_type == "date":
            # Standardize date formats
            if "-" in values:
                try:
                    start, end = map(str.strip, values.split("-"))
                    return f"{start} - {end}"
                except:
                    return values
            return values
            
        return values


def main():
    """Main entry point for the dictionary cleaner tool."""
    args = cu.parse_tool_args("🧹 Cleans and standardizes data dictionary entries including value types and expected values")
    
    # Create and run the tool
    tool = DictionaryCleaner()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main() 
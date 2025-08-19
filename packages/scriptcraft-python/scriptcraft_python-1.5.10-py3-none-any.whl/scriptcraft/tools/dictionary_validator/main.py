"""
Dictionary Validator Tool

Validates consistency between dataset columns and dictionary columns.
"""

import sys
from pathlib import Path
from typing import Optional

from scriptcraft.common.cli import parse_tool_args
from scriptcraft.common.logging import setup_logger
from scriptcraft.common.core.base import BaseTool
from scriptcraft.common import log_and_print, load_dataset_columns, load_dictionary_columns
from .env import is_development_environment
from .utils import compare_columns


class DictionaryValidator(BaseTool):
    """Validates dataset columns against dictionary columns."""
    
    def __init__(self):
        super().__init__(
            name="Dictionary Validator",
            description="Validates consistency between dataset columns and dictionary columns",
            tool_name="dictionary_validator",
            requires_dictionary=True
        )
    
    def run(self, *args, **kwargs) -> None:
        """
        Run the dictionary validation process.
        
        Args:
            *args: Positional arguments (can include dataset_file, dictionary_file)
            **kwargs: Keyword arguments including:
                - dataset_file: Path to dataset file
                - dictionary_file: Path to dictionary file
                - domain: Domain to validate
                - output_dir: Output directory
        """
        self.log_start()
        
        try:
            # Extract arguments
            dataset_file = kwargs.get('dataset_file') or (args[0] if args else None)
            dictionary_file = kwargs.get('dictionary_file') or (args[1] if len(args) > 1 else None)
            domain = kwargs.get('domain', 'unknown')
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            
            # Validate inputs
            if not dataset_file or not dictionary_file:
                raise ValueError("❌ Both dataset_file and dictionary_file are required")
            
            dataset_file = Path(dataset_file)
            dictionary_file = Path(dictionary_file)
            
            if not dataset_file.exists():
                raise FileNotFoundError(f"❌ Dataset file not found: {dataset_file}")
            if not dictionary_file.exists():
                raise FileNotFoundError(f"❌ Dictionary file not found: {dictionary_file}")
            
            # Resolve output directory
            output_path = self.resolve_output_directory(output_dir)
            
            # Process the validation
            self.process_domain(domain, dataset_file, dictionary_file, output_path, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Dictionary validation failed: {e}")
            raise
    
    def process_domain(self, domain: str, dataset_file: Path, dictionary_file: Path, 
                      output_path: Path, **kwargs) -> None:
        """
        Validate dataset columns against dictionary columns.
        
        Args:
            domain: The domain to validate
            dataset_file: Path to dataset file
            dictionary_file: Path to dictionary file
            output_path: Not used (results are logged)
            **kwargs: Additional arguments
        """
        log_and_print(f"🔍 Validating {dataset_file.name} against {dictionary_file.name}...\n")

        # Load and compare columns
        dataset_columns = load_dataset_columns(dataset_file)
        dictionary_columns = load_dictionary_columns(dictionary_file)
        comparison = compare_columns(dataset_columns, dictionary_columns)

        # Log results
        log_and_print(f"✅ Columns in both: {len(comparison['in_both'])}")
        log_and_print(f"❌ Only in dataset ({len(comparison['only_in_dataset'])}): {comparison['only_in_dataset']}")
        log_and_print(f"❌ Only in dictionary ({len(comparison['only_in_dictionary'])}): {comparison['only_in_dictionary']}")
        log_and_print(f"🔄 Case mismatches ({len(comparison['case_mismatches'])}): {comparison['case_mismatches']}\n")


def main():
    """Main entry point for the dictionary validator tool."""
    args = parse_tool_args("Validates consistency between dataset columns and dictionary columns")
    logger = setup_logger("dictionary_validator")
    
    # Create and run the tool
    tool = DictionaryValidator()
    tool.run(args)


if __name__ == "__main__":
    main() 
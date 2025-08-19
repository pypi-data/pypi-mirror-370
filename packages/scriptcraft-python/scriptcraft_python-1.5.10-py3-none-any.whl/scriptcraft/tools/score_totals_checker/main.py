"""
Score Totals Checker Tool

This checker validates that calculated totals match expected totals in datasets.
"""

import sys
from pathlib import Path
from typing import Optional
import pandas as pd

from scriptcraft.common.cli import parse_tool_args
from scriptcraft.common.logging import setup_logger
from scriptcraft.common.core.base import BaseTool
from scriptcraft.common import log_and_print, load_data
from .env import is_development_environment
from .utils import calculate_totals_and_compare


class ScoreTotalsChecker(BaseTool):
    """Checker for validating that calculated totals match expected totals in datasets."""
    
    def __init__(self):
        super().__init__(
            name="Score Totals Checker",
            description="Validates that calculated totals match expected totals in datasets",
            tool_name="score_totals_checker"
        )
    
    def run(self, *args, **kwargs) -> None:
        """
        Run the score totals checking process.
        
        Args:
            *args: Positional arguments (can include input_paths, domain)
            **kwargs: Keyword arguments including:
                - input_paths: List of input file paths
                - output_dir: Output directory
                - domain: Domain to process
        """
        self.log_start()
        
        try:
            # Extract arguments
            input_paths = kwargs.get('input_paths') or (args[0] if args else None)
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            domain = kwargs.get('domain', 'unknown')
            
            # Validate inputs
            if not input_paths:
                raise ValueError("❌ No input paths provided")
            
            if isinstance(input_paths, str):
                input_paths = [input_paths]
            
            # Validate input files
            if not self.validate_input_files(input_paths):
                raise ValueError("❌ Invalid input files")
            
            # Resolve output directory
            output_path = self.resolve_output_directory(output_dir)
            
            # Process each input file
            for input_path in input_paths:
                input_path = Path(input_path)
                log_and_print(f"🔍 Processing: {input_path}")
                
                # Process the domain
                self.process_domain(domain, input_path, None, output_path, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Score totals checking failed: {e}")
            raise
    
    def process_domain(self, domain: str, dataset_file: Path, dictionary_file: Optional[Path], 
                      output_path: Path, **kwargs) -> None:
        """
        Check calculated totals against expected totals.
        
        Args:
            domain: The domain to check
            dataset_file: Path to dataset file
            dictionary_file: Not used for this tool
            output_path: Path to save results
            **kwargs: Additional arguments
        """
        log_and_print(f"🔍 Checking totals in {dataset_file.name} for {domain}...")

        try:
            # Load data
            df = load_data(dataset_file)
            
            # Calculate totals and compare
            results = calculate_totals_and_compare(df, domain)
            
            # Save results
            if not results.empty:
                output_file = output_path / f"{domain}_totals_check.csv"
                results.to_csv(output_file, index=False)
                log_and_print(f"✅ Results saved to: {output_file}")
            else:
                log_and_print(f"⚠️ No total columns found to check in {domain}")
                
        except Exception as e:
            log_and_print(f"❌ Error checking totals for {domain}: {e}", level="error")
            raise


def main():
    """Main entry point for the score totals checker tool."""
    args = parse_tool_args("Validates that calculated totals match expected totals in datasets")
    logger = setup_logger("score_totals_checker")
    
    # Create and run the tool
    tool = ScoreTotalsChecker()
    tool.run(args)


if __name__ == "__main__":
    main() 
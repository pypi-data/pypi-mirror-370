"""
Feature Change Checker Tool

Tracks and categorizes changes in feature values between visits or timepoints.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from scriptcraft.common.cli import parse_tool_args
from scriptcraft.common.logging import setup_logger
from scriptcraft.common.core.base import BaseTool
from scriptcraft.common import (
    log_and_print, load_data, find_matching_file, FILE_PATTERNS
)
from .env import is_development_environment
from .utils import run_categorized_changes, run_between_visit_changes


class FeatureChangeChecker(BaseTool):
    """Checker for tracking changes in feature values between visits."""
    
    def __init__(self, feature_name: str = "CDX_Cog", categorize: bool = True):
        """
        Initialize the feature change checker.
        
        Args:
            feature_name: Name of the feature to track changes for
            categorize: Whether to categorize changes or just track differences
        """
        super().__init__(
            name="Feature Change Checker",
            description=f"Tracks changes in {feature_name} values between visits",
            tool_name="feature_change_checker"
        )
        self.feature_name = feature_name
        self.categorize = categorize
    
    def run(self, *args, **kwargs) -> None:
        """
        Run the feature change checking process.
        
        Args:
            *args: Positional arguments (can include dataset_file, domain)
            **kwargs: Keyword arguments including:
                - input_paths: List of input file paths
                - output_dir: Output directory
                - domain: Domain to process
                - feature_name: Name of feature to track
                - categorize: Whether to categorize changes
        """
        self.log_start()
        
        try:
            # Extract arguments
            input_paths = kwargs.get('input_paths') or (args[0] if args else None)
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            domain = kwargs.get('domain', 'unknown')
            feature_name = kwargs.get('feature_name', self.feature_name)
            categorize = kwargs.get('categorize', self.categorize)
            
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
                self.process_domain(domain, input_path, None, output_path, 
                                  feature_name=feature_name, categorize=categorize, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Feature change checking failed: {e}")
            raise
    
    def process_domain(self, domain: str, dataset_file: Path, dictionary_file: Optional[Path], 
                      output_path: Path, **kwargs) -> None:
        """
        Check feature changes between visits.
        
        Args:
            domain: The domain to check (e.g., "Biomarkers", "Clinical")
            dataset_file: Path to dataset file
            dictionary_file: Not used for this tool
            output_path: Path to output directory
            **kwargs: Additional arguments
        """
        log_and_print(f"🔍 Checking feature changes for '{self.feature_name}' in {domain}...")
        
        # Load data
        df = load_data(dataset_file)
        
        if self.feature_name not in df.columns:
            log_and_print(f"❌ Feature '{self.feature_name}' not found in dataset", level="error")
            return
        
        # Run analysis based on configuration
        if self.categorize:
            run_categorized_changes(df, self.feature_name, output_path)
        else:
            run_between_visit_changes(df, self.feature_name, output_path)
        
        log_and_print(f"✅ Feature change analysis completed for {domain}")


def main():
    """Main entry point for the feature change checker tool."""
    args = parse_tool_args("Tracks and categorizes changes in feature values between visits")
    logger = setup_logger("feature_change_checker")
    
    # Get feature name from args if provided
    feature_name = getattr(args, 'feature', 'CDX_Cog')
    categorize = getattr(args, 'categorize', True)
    
    # Create and run the tool
    tool = FeatureChangeChecker(feature_name=feature_name, categorize=categorize)
    tool.run(args)


if __name__ == "__main__":
    main() 
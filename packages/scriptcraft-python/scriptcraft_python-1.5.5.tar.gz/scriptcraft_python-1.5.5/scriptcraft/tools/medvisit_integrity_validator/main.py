"""
MedVisit Integrity Validator Tool

This validator checks Med_ID and Visit_ID integrity between old and new datasets.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

from scriptcraft.common.cli import parse_tool_args
from scriptcraft.common.logging import setup_logger
from scriptcraft.common.core.base import BaseTool
from scriptcraft.common import (
    log_and_print, load_datasets, standardize_columns, 
    ensure_output_dir, compare_dataframes
)
from .env import is_development_environment


# File mapping for different domains
FILENAME_MAP: Dict[str, Dict[str, str]] = {
    "Biomarkers": {
        "old": "HD Release 6 Biomarkers_FINAL.csv",
        "new": "HD6 + New data_Biomarkers---MatthewReviewPending.xlsx"
    },
    # "Clinical": {
    #     "old": "HD Release 6 Clinical_FINAL.csv",
    #     "new": "HD6 + New data_Clinical---Review.xlsx"
    # },
    # Add Genomics/Imaging when ready
}


class MedVisitIntegrityValidator(BaseTool):
    """Validator for checking Med_ID and Visit_ID integrity between old and new datasets."""
    
    def __init__(self):
        super().__init__(
            name="MedVisit Integrity Validator",
            description="Validates the integrity of Med_ID and Visit_ID combinations between datasets",
            tool_name="medvisit_integrity_validator"
        )
    
    def run(self, *args, **kwargs) -> None:
        """
        Run the MedVisit integrity validation process.
        
        Args:
            *args: Positional arguments (can include domains)
            **kwargs: Keyword arguments including:
                - domains: List of domains to process
                - output_dir: Output directory
        """
        self.log_start()
        
        try:
            # Extract arguments
            domains = kwargs.get('domains') or (args[0] if args else None)
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            
            # Validate inputs
            if not domains:
                # Default to all available domains
                domains = list(FILENAME_MAP.keys())
            
            if isinstance(domains, str):
                domains = [domains]
            
            # Resolve output directory
            output_path = self.resolve_output_directory(output_dir)
            
            # Process each domain
            for domain in domains:
                if domain not in FILENAME_MAP:
                    log_and_print(f"⚠️ Skipping {domain} — no file mapping found.")
                    continue
                
                log_and_print(f"🔍 Processing domain: {domain}")
                
                # Create domain-specific output file
                domain_output = output_path / f"{domain}_medvisit_integrity.xlsx"
                
                # Process the domain
                self.process_domain(domain, None, None, domain_output, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"MedVisit integrity validation failed: {e}")
            raise
    
    def process_domain(self, domain: str, dataset_file: Path, dictionary_file: Optional[Path], 
                      output_path: Path, **kwargs) -> None:
        """
        Validate Med_ID and Visit_ID integrity between old and new datasets.
        
        Args:
            domain: The domain to validate (e.g., "Biomarkers", "Clinical")
            dataset_file: Not used in this validator
            dictionary_file: Not used in this validator
            output_path: Path to save the validation results
            **kwargs: Additional arguments
        """
        filenames = FILENAME_MAP.get(domain)
        if not filenames:
            log_and_print(f"⏩ Skipping {domain} — no file mapping found.")
            return

        log_and_print(f"🔍 Validating Med/Visit ID integrity for {domain}...")

        df_old, df_new = load_datasets(
            old_filename=filenames["old"],
            new_filename=filenames["new"],
            data_dir=domain,
            mode="standard"
        )

        df_new = standardize_columns(df_new, {"Visit": "Visit_ID", "Med ID": "Med_ID"})
        
        # Use compare_dataframes with med_ids step to check Med/Visit ID integrity
        comparison_result = compare_dataframes(
            df_old, 
            df_new, 
            dataset_name=domain,
            steps=["med_ids"]
        )
        
        # Extract missing IDs from the comparison result
        missing_in_new, missing_in_old = comparison_result.missing_ids or (pd.DataFrame(), pd.DataFrame())

        ensure_output_dir(output_path)
        with pd.ExcelWriter(output_path) as writer:
            missing_in_new.to_excel(writer, sheet_name="Missing in New", index=False)
            missing_in_old.to_excel(writer, sheet_name="Missing in Old", index=False)

        log_and_print(f"🔍 Combos missing in new dataset: {len(missing_in_new)}")
        log_and_print(f"🔍 Combos missing in old dataset: {len(missing_in_old)}")
        log_and_print(f"✅ Comparison saved to: {output_path}")


def main():
    """Main entry point for the medvisit integrity validator tool."""
    args = parse_tool_args("Validates the integrity of Med_ID and Visit_ID combinations between datasets")
    logger = setup_logger("medvisit_integrity_validator")
    
    # Create and run the tool
    tool = MedVisitIntegrityValidator()
    tool.run(args)


if __name__ == "__main__":
    main() 
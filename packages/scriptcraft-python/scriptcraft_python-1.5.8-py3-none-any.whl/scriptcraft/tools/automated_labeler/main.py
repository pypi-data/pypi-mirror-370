"""
🏷️ Automated Labeler Tool

This tool automatically generates labels and fills document templates with data from Excel files.
Supports form automation and document generation for research workflows.

Usage:
    Development: python -m scriptcraft.tools.automated_labeler.main [args]
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
        fill_full_page, apply_labeling_rules, 
        save_labeled_data, process_data
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        fill_full_page, apply_labeling_rules, 
        save_labeled_data, process_data
    )

# Document processing imports
from docx import Document
from docx.shared import Pt


class AutomatedLabeler(cu.BaseTool):
    """Tool for automated data labeling and document template filling."""
    
    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__(
            name="Automated Labeler",
            description="🏷️ Automatically generates labels and fills document templates with data",
            tool_name="automated_labeler"
        )
        
        # Get tool-specific configuration
        tool_config = self.get_tool_config()
        self.sets_per_page = tool_config.get("sets_per_page", 8)
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs: Any) -> None:
        """
        Run the automated labeling process.
        
        Args:
            mode: Labeling mode (e.g., 'standard', 'custom', 'template')
            input_paths: List containing paths to the data files to label
            output_dir: Directory to save labeled data
            domain: Optional domain to filter labeling
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - labeling_rules: Custom labeling rules to apply
                - output_format: Format for the output data
                - template_path: Path to DOCX template file
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or []):
                raise ValueError("❌ No input files provided")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Get labeling settings
            labeling_rules = kwargs.get('labeling_rules', {})
            output_format = kwargs.get('output_format', 'excel')
            template_path = kwargs.get('template_path')
            
            # Determine mode and execute accordingly
            if mode == 'template' or template_path:
                self._process_template_mode(input_paths, output_path, template_path, output_filename, **kwargs)
            else:
                self._process_labeling_mode(input_paths, output_path, domain, labeling_rules, output_format, output_filename, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Error: {str(e)}")
            raise
    
    def _process_labeling_mode(self, input_paths: List[Union[str, Path]], output_path: Path, 
                             domain: Optional[str], labeling_rules: Dict[str, Any], 
                             output_format: str, output_filename: Optional[str], **kwargs: Any) -> None:
        """Process data labeling mode."""
        # Load data using DRY method
        data = self.load_data_file(input_paths[0])
        
        # Apply labeling rules
        cu.log_and_print("🔄 Applying labeling rules...")
        labeled_data = apply_labeling_rules(data, rules=labeling_rules, domain=domain)
        
        # Save labeled data using DRY method
        if output_filename:
            output_file = output_path / output_filename
        else:
            output_file = output_path / f"labeled_data.{output_format}"
        
        self.save_data_file(labeled_data, output_file, include_index=False)
        cu.log_and_print(f"✅ Labeled data saved to: {output_file}")
    
    def _process_template_mode(self, input_paths: List[Union[str, Path]], output_path: Path, 
                             template_path: Optional[str], output_filename: Optional[str], **kwargs: Any) -> None:
        """Process document template filling mode."""
        # Load data using DRY method
        data = self.load_data_file(input_paths[0])
        
        # Load template
        if template_path:
            template_file = Path(template_path)
        elif len(input_paths) > 1:
            template_file = Path(input_paths[1])
        else:
            raise ValueError("❌ Template file required for template mode")
        
        if not template_file.exists():
            raise ValueError(f"❌ Template file not found: {template_file}")
        
        cu.log_and_print(f"📄 Loading template: {template_file}")
        template_doc = Document(template_file)
        
        # Process template filling
        cu.log_and_print("🔄 Filling template with data...")
        filled_doc = self._fill_template_with_data(template_doc, data)
        
        # Save filled document
        if output_filename:
            output_file = output_path / output_filename
        else:
            output_file = output_path / "Labels.docx"
        
        filled_doc.save(output_file)
        cu.log_and_print(f"✅ Filled template saved to: {output_file}")
    
    def _fill_template_with_data(self, template_doc: Document, data: Any) -> Document:
        """Fill template with data from DataFrame."""
        # Extract ID columns if they exist
        id_columns = ['RID', 'MID', 'Visit_ID']
        available_columns = [col for col in id_columns if col in data.columns]
        
        if not available_columns:
            raise ValueError("❌ No ID columns found in data")
        
        # Create ID pairs for template filling
        id_pairs = []
        for _, row in data.iterrows():
            rid = str(row.get('RID', ''))
            mid = str(row.get('MID', ''))
            visit = str(row.get('Visit_ID', ''))
            id_pairs.append((rid, mid, visit))
        
        # Fill template using utility function
        return fill_full_page(template_doc, id_pairs)


def main():
    """Main entry point for the automated labeler tool."""
    args = cu.parse_tool_args("🏷️ Automatically generates labels and fills document templates with data")
    
    # Create and run the tool
    tool = AutomatedLabeler()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main() 
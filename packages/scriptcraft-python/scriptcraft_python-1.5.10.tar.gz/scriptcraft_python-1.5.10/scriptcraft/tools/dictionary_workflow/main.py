"""
📚 Dictionary Workflow Tool

This tool handles the complete dictionary enhancement workflow:
1. Prepare supplements (merge and clean)
2. Split supplements by domain
3. Enhance dictionaries with domain-specific supplements

This tool consolidates the functionality of the three separate enhancement packages
into a single, streamlined workflow.

Usage:
    Development: python -m scriptcraft.tools.dictionary_workflow.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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
        prepare_supplements, split_supplements_by_domain, enhance_dictionaries,
        run_complete_workflow
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        prepare_supplements, split_supplements_by_domain, enhance_dictionaries,
        run_complete_workflow
    )


class DictionaryWorkflow(cu.BaseTool):
    """Tool for complete dictionary enhancement workflow."""
    
    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__(
            name="Dictionary Workflow",
            description="📚 Complete dictionary enhancement workflow tool",
            tool_name="dictionary_workflow"
        )
        
        # Get tool-specific configuration
        tool_config = self.get_tool_config()
        self.default_workflow_steps = tool_config.get("default_workflow_steps", ["prepare", "split", "enhance"])
        self.default_merge_strategy = tool_config.get("default_merge_strategy", "outer")
        self.default_enhancement_strategy = tool_config.get("default_enhancement_strategy", "append")
    
    def run(self,
            input_paths: Optional[List[Union[str, Path]]] = None,
            dictionary_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            workflow_steps: Optional[List[str]] = None,
            merge_strategy: Optional[str] = None,
            enhancement_strategy: Optional[str] = None,
            domain_column: Optional[str] = None,
            clean_data: Optional[bool] = None,
            **kwargs: Any) -> None:
        """
        Run the dictionary enhancement workflow.
        
        Args:
            input_paths: List containing paths to supplement files
            dictionary_paths: List containing paths to dictionary files
            output_dir: Directory to save workflow outputs
            workflow_steps: List of workflow steps to run (default: all steps)
            merge_strategy: Strategy for merging supplements ('outer', 'inner', 'left', 'right')
            enhancement_strategy: Strategy for enhancing dictionaries ('append', 'merge', 'replace')
            domain_column: Column name containing domain information
            clean_data: Whether to clean data during processing
            **kwargs: Additional arguments for workflow steps
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or []):
                raise ValueError("❌ No input supplement files provided")
            
            if not self.validate_input_files(dictionary_paths or []):
                raise ValueError("❌ No input dictionary files provided")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Set default values
            workflow_steps = workflow_steps or self.default_workflow_steps
            merge_strategy = merge_strategy or self.default_merge_strategy
            enhancement_strategy = enhancement_strategy or self.default_enhancement_strategy
            domain_column = domain_column or "domain"
            clean_data = clean_data if clean_data is not None else True
            
            # Run the complete workflow
            results = run_complete_workflow(
                input_paths=input_paths,
                dictionary_paths=dictionary_paths,
                output_dir=output_path,
                workflow_steps=workflow_steps,
                merge_strategy=merge_strategy,
                enhancement_strategy=enhancement_strategy,
                domain_column=domain_column,
                clean_data=clean_data,
                **kwargs
            )
            
            # Log summary
            self._log_workflow_summary(results, output_path)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Error: {str(e)}")
            raise
    
    def _log_workflow_summary(self, results: Dict[str, Any], output_path: Path) -> None:
        """Log a summary of the workflow results."""
        cu.log_and_print("📊 Workflow Summary:")
        
        if 'prepared_supplements' in results:
            prepared = results['prepared_supplements']
            cu.log_and_print(f"  📋 Prepared supplements: {len(prepared)} rows")
        
        if 'domain_supplements' in results:
            domain_supps = results['domain_supplements']
            cu.log_and_print(f"  ✂️ Split supplements: {len(domain_supps)} domains")
            for domain, data in domain_supps.items():
                cu.log_and_print(f"    - {domain}: {len(data)} rows")
        
        if 'enhanced_dictionaries' in results:
            enhanced = results['enhanced_dictionaries']
            cu.log_and_print(f"  🔧 Enhanced dictionaries: {len(enhanced)} files")
            for dict_name, data in enhanced.items():
                cu.log_and_print(f"    - {dict_name}: {len(data)} rows")
        
        cu.log_and_print(f"  📁 Output directory: {output_path}")


def main():
    """Main entry point for the dictionary workflow tool."""
    args = cu.parse_dictionary_workflow_args("dictionary_workflow", "📚 Complete dictionary enhancement workflow tool")
    
    # Create and run the tool
    tool = DictionaryWorkflow()
    tool.run(
        input_paths=args.input_paths,
        dictionary_paths=args.dictionary_paths,
        output_dir=args.output_dir,
        workflow_steps=args.workflow_steps,
        merge_strategy=args.merge_strategy,
        enhancement_strategy=args.enhancement_strategy,
        domain_column=args.domain_column,
        clean_data=args.clean_data
    )


if __name__ == "__main__":
    main() 
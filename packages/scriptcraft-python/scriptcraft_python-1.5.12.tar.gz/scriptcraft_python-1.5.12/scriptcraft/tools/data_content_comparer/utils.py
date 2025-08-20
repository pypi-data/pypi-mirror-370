# scripts/tools/data_content_comparer/utils.py

from pathlib import Path
import importlib.util
from typing import List, Union, Optional, Dict, Any
import pandas as pd

import scriptcraft.common as cu

def load_mode(mode_name: str) -> None:
    """Dynamically load a mode plugin from the plugins/ directory relative to this script."""
    try:
        # Resolve the actual plugins path based on this file's location
        plugins_dir = Path(__file__).resolve().parent / "plugins"
        plugin_file = plugins_dir / f"{mode_name}.py"

        if not plugin_file.exists():
            cu.log_and_print(f"❌ Mode file '{plugin_file}' not found.")
            return None

        # Dynamically import using importlib
        spec = importlib.util.spec_from_file_location(mode_name, plugin_file)
        if spec is None:
            cu.log_and_print(f"❌ Failed to create spec for '{plugin_file}'")
            return None
            
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            cu.log_and_print(f"❌ Failed to get loader for '{plugin_file}'")
            return None
            
        spec.loader.exec_module(module)

        if hasattr(module, "run_mode"):
            return getattr(module, "run_mode")
        else:
            cu.log_and_print(f"❌ Mode '{mode_name}' exists but does not define a 'run_mode()' function.")
            return None

    except Exception as e:
        cu.log_and_print(f"❌ Failed to load mode '{mode_name}': {e}")
        return None


def resolve_input_files(mode, input_dir: Path, input_paths=None) -> None:
    """Handles logic for resolving input files based on mode and paths provided."""
    if input_paths:
        return input_paths

    if mode == "rhq_mode":
        # Still use input_dir if provided, otherwise default
        # base = input_dir if input_dir else (cu.get_project_root() / "input")
        base = input_dir.resolve()

        cu.log_and_print(f"🔎 Resolving input files in RHQ mode from: {base.resolve()}")
        return cu.auto_resolve_input_files(base, required_count=2)
   
    # Default to getting latest 2 files from input_dir
    cu.log_and_print(f"🔎 Looking for input files in: {input_dir.resolve()}")
    input_files = sorted(input_dir.glob("*.[cx]sv*"))[-2:]
    if not input_files:
        cu.log_and_print(f"⚠️ No matching files found in directory: {input_dir.resolve()}")
    else:
        cu.log_and_print(f"📂 Found files: {[str(f) for f in input_files]}")

    if len(input_files) != 2:
        cu.log_and_print(f"⚠️ Warning: Expected 2 files in {input_dir}, but found {len(input_files)}. Exiting.")
        return
    return input_files


def load_datasets_as_list(input_paths: List[Union[str, Path]]) -> List[pd.DataFrame]:
    """
    Load multiple datasets from the provided paths.
    
    Args:
        input_paths: List of paths to the datasets to load
        
    Returns:
        List of loaded DataFrames in the same order as input paths
    """
    datasets = []
    for path in input_paths:
        try:
            df = cu.load_data(path)
            if df is not None:
                datasets.append(df)
            else:
                cu.log_and_print(f"⚠️ Warning: Failed to load dataset from {path}")
        except Exception as e:
            cu.log_and_print(f"❌ Error loading dataset from {path}: {e}")
            
    return datasets

def compare_datasets(df1: pd.DataFrame, df2: pd.DataFrame, comparison_type: str = 'full', domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare two datasets and return the comparison results.
    
    Args:
        df1: First DataFrame to compare
        df2: Second DataFrame to compare
        comparison_type: Type of comparison to perform ('full' or 'quick')
        domain: Optional domain to filter comparison
        
    Returns:
        Dictionary containing comparison results
    """
    # Apply domain filtering if specified
    if domain:
        df1 = df1[df1['Domain'] == domain].copy()
        df2 = df2[df2['Domain'] == domain].copy()
    
    # Perform comparison using common utils
    comparison_results = cu.compare_dataframes(df1, df2)
    
    return comparison_results

def generate_report(comparison_results: Dict[str, Any], report_path: Union[str, Path], format: str = 'excel') -> None:
    """
    Generate a report from the comparison results.
    
    Args:
        comparison_results: Dictionary containing comparison results
        report_path: Path where to save the report
        format: Output format ('excel' or 'csv')
    """
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(comparison_results)
    
    # Save based on format
    if format.lower() == 'excel':
        results_df.to_excel(report_path, index=False)
    else:
        results_df.to_csv(report_path, index=False)
    
    cu.log_and_print(f"📄 Report saved to: {report_path.resolve()}")


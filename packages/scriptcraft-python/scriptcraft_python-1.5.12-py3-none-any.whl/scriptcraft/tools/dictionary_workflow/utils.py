"""
🧰 Helper functions for the Dictionary Workflow Tool.

This module consolidates the functionality from the three enhancement packages:
- supplement_prepper: Prepare and merge supplements
- supplement_splitter: Split supplements by domain
- dictionary_supplementer: Enhance dictionaries with supplements

Includes:
- prepare_supplements(): Merge and clean supplement files
- split_supplements_by_domain(): Split supplements by domain
- enhance_dictionaries(): Enhance dictionaries with domain supplements
- Workflow orchestration functions

Example:
    from .utils import prepare_supplements, split_supplements_by_domain, enhance_dictionaries
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import pandas as pd

# Try to import common utilities with fallback
try:
    import scriptcraft.common as cu
except ImportError:
    try:
        import common as cu
    except ImportError:
        # Fallback to basic pandas operations
        cu = None


def prepare_supplements(input_paths: List[Union[str, Path]], 
                       output_path: Optional[Union[str, Path]] = None,
                       merge_strategy: str = 'outer',
                       clean_data: bool = True,
                       **kwargs: Any) -> pd.DataFrame:
    """
    Prepare supplements by merging multiple files and cleaning the data.
    
    Args:
        input_paths: List of paths to supplement files
        output_path: Optional path to save prepared supplements
        merge_strategy: Merge strategy ('outer', 'inner', 'left', 'right')
        clean_data: Whether to clean the data after merging
        **kwargs: Additional arguments for data loading
        
    Returns:
        DataFrame with prepared supplements
    """
    if not input_paths:
        raise ValueError("❌ No input paths provided")
    
    cu.log_and_print(f"🔄 Preparing supplements from {len(input_paths)} files...")
    
    # Load all supplement files
    supplements = []
    for path in input_paths:
        path = Path(path)
        if not path.exists():
            cu.log_and_print(f"⚠️ Warning: File not found: {path}")
            continue
            
        try:
            if cu:
                data = cu.load_data(path, **kwargs)
            else:
                # Fallback loading
                if path.suffix.lower() == '.csv':
                    data = pd.read_csv(path, **kwargs)
                elif path.suffix.lower() in ['.xlsx', '.xls']:
                    data = pd.read_excel(path, **kwargs)
                else:
                    cu.log_and_print(f"⚠️ Warning: Unsupported file format: {path}")
                    continue
                    
            supplements.append(data)
            cu.log_and_print(f"✅ Loaded: {path.name} ({len(data)} rows)")
        except Exception as e:
            cu.log_and_print(f"❌ Error loading {path}: {e}")
    
    if not supplements:
        raise ValueError("❌ No valid supplement files loaded")
    
    # Merge supplements
    cu.log_and_print(f"🔄 Merging {len(supplements)} supplement files...")
    if len(supplements) == 1:
        merged_data = supplements[0]
    else:
        merged_data = pd.concat(supplements, ignore_index=True, sort=False)
    
    # Clean data if requested
    if clean_data:
        cu.log_and_print("🧹 Cleaning merged supplements...")
        if cu:
            merged_data = cu.clean_dataframe(merged_data)
        else:
            # Basic cleaning fallback
            merged_data = merged_data.dropna(how='all')
            merged_data = merged_data.drop_duplicates()
    
    cu.log_and_print(f"✅ Prepared supplements: {len(merged_data)} rows")
    
    # Save if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if cu:
            cu.save_data(merged_data, output_path)
        else:
            if output_path.suffix.lower() == '.csv':
                merged_data.to_csv(output_path, index=False)
            elif output_path.suffix.lower() in ['.xlsx', '.xls']:
                merged_data.to_excel(output_path, index=False)
        cu.log_and_print(f"💾 Saved prepared supplements to: {output_path}")
    
    return merged_data


def split_supplements_by_domain(supplements_data: pd.DataFrame,
                               output_dir: Union[str, Path],
                               domain_column: str = 'domain',
                               split_strategy: str = 'standard',
                               **kwargs: Any) -> Dict[str, pd.DataFrame]:
    """
    Split supplements by domain and save to separate files.
    
    Args:
        supplements_data: DataFrame with supplements data
        output_dir: Directory to save domain-specific supplements
        domain_column: Column name containing domain information
        split_strategy: Split strategy ('standard', 'custom')
        **kwargs: Additional arguments for data processing
        
    Returns:
        Dictionary mapping domain names to DataFrames
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cu.log_and_print(f"🔄 Splitting supplements by domain...")
    
    # Validate domain column exists
    if domain_column not in supplements_data.columns:
        raise ValueError(f"❌ Domain column '{domain_column}' not found in supplements data")
    
    # Get unique domains
    domains = supplements_data[domain_column].dropna().unique()
    cu.log_and_print(f"📊 Found {len(domains)} domains: {', '.join(domains)}")
    
    domain_data = {}
    
    for domain in domains:
        # Filter data for this domain
        domain_mask = supplements_data[domain_column] == domain
        domain_df = supplements_data[domain_mask].copy()
        
        if len(domain_df) == 0:
            cu.log_and_print(f"⚠️ Warning: No data for domain '{domain}'")
            continue
        
        # Process domain data
        if cu:
            domain_df = cu.process_domain_data(domain_df, domain, **kwargs)
        else:
            # Basic processing fallback
            domain_df = domain_df.dropna(how='all')
            domain_df = domain_df.drop_duplicates()
        
        # Save domain-specific supplements
        domain_filename = f"supplements_{domain.lower()}.csv"
        domain_path = output_dir / domain_filename
        
        if cu:
            cu.save_data(domain_df, domain_path)
        else:
            domain_df.to_csv(domain_path, index=False)
        
        domain_data[domain] = domain_df
        cu.log_and_print(f"✅ Domain '{domain}': {len(domain_df)} rows -> {domain_path}")
    
    cu.log_and_print(f"✅ Split supplements into {len(domain_data)} domain files")
    return domain_data


def enhance_dictionaries(dictionary_paths: List[Union[str, Path]],
                        supplement_paths: List[Union[str, Path]],
                        output_dir: Union[str, Path],
                        domain_mapping: Optional[Dict[str, str]] = None,
                        enhancement_strategy: str = 'append',
                        **kwargs: Any) -> Dict[str, pd.DataFrame]:
    """
    Enhance dictionaries with domain-specific supplements.
    
    Args:
        dictionary_paths: List of paths to dictionary files
        supplement_paths: List of paths to supplement files (or directory)
        output_dir: Directory to save enhanced dictionaries
        domain_mapping: Optional mapping of supplement files to domains
        enhancement_strategy: Strategy for enhancement ('append', 'merge', 'replace')
        **kwargs: Additional arguments for data processing
        
    Returns:
        Dictionary mapping dictionary names to enhanced DataFrames
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cu.log_and_print(f"🔄 Enhancing {len(dictionary_paths)} dictionaries...")
    
    # Load dictionaries
    dictionaries = {}
    for path in dictionary_paths:
        path = Path(path)
        if not path.exists():
            cu.log_and_print(f"⚠️ Warning: Dictionary not found: {path}")
            continue
            
        try:
            if cu:
                data = cu.load_data(path, **kwargs)
            else:
                # Fallback loading
                if path.suffix.lower() == '.csv':
                    data = pd.read_csv(path, **kwargs)
                elif path.suffix.lower() in ['.xlsx', '.xls']:
                    data = pd.read_excel(path, **kwargs)
                else:
                    cu.log_and_print(f"⚠️ Warning: Unsupported file format: {path}")
                    continue
                    
            dictionaries[path.stem] = data
            cu.log_and_print(f"✅ Loaded dictionary: {path.name} ({len(data)} rows)")
        except Exception as e:
            cu.log_and_print(f"❌ Error loading dictionary {path}: {e}")
    
    if not dictionaries:
        raise ValueError("❌ No valid dictionaries loaded")
    
    # Load supplements
    supplements = {}
    for path in supplement_paths:
        path = Path(path)
        if path.is_dir():
            # Load all supplement files in directory
            for supplement_file in path.glob("*.csv"):
                domain = supplement_file.stem.replace("supplements_", "")
                try:
                    if cu:
                        data = cu.load_data(supplement_file, **kwargs)
                    else:
                        data = pd.read_csv(supplement_file, **kwargs)
                    supplements[domain] = data
                    cu.log_and_print(f"✅ Loaded supplement: {supplement_file.name} ({len(data)} rows)")
                except Exception as e:
                    cu.log_and_print(f"❌ Error loading supplement {supplement_file}: {e}")
        else:
            # Single supplement file
            if not path.exists():
                cu.log_and_print(f"⚠️ Warning: Supplement not found: {path}")
                continue
                
            try:
                if cu:
                    data = cu.load_data(path, **kwargs)
                else:
                    if path.suffix.lower() == '.csv':
                        data = pd.read_csv(path, **kwargs)
                    elif path.suffix.lower() in ['.xlsx', '.xls']:
                        data = pd.read_excel(path, **kwargs)
                    else:
                        cu.log_and_print(f"⚠️ Warning: Unsupported file format: {path}")
                        continue
                        
                # Determine domain from filename or mapping
                domain = domain_mapping.get(str(path), path.stem) if domain_mapping else path.stem
                supplements[domain] = data
                cu.log_and_print(f"✅ Loaded supplement: {path.name} ({len(data)} rows)")
            except Exception as e:
                cu.log_and_print(f"❌ Error loading supplement {path}: {e}")
    
    # Enhance each dictionary
    enhanced_dictionaries = {}
    for dict_name, dict_data in dictionaries.items():
        cu.log_and_print(f"🔄 Enhancing dictionary: {dict_name}")
        
        # Find matching supplements for this dictionary
        matching_supplements = []
        for domain, supplement_data in supplements.items():
            # Simple matching logic - can be enhanced
            if domain.lower() in dict_name.lower() or dict_name.lower() in domain.lower():
                matching_supplements.append(supplement_data)
        
        if not matching_supplements:
            cu.log_and_print(f"⚠️ No matching supplements found for {dict_name}")
            enhanced_dictionaries[dict_name] = dict_data
            continue
        
        # Combine supplements for this dictionary
        if len(matching_supplements) == 1:
            combined_supplements = matching_supplements[0]
        else:
            combined_supplements = pd.concat(matching_supplements, ignore_index=True, sort=False)
            combined_supplements = combined_supplements.drop_duplicates()
        
        # Enhance dictionary based on strategy
        if enhancement_strategy == 'append':
            enhanced_data = pd.concat([dict_data, combined_supplements], ignore_index=True, sort=False)
        elif enhancement_strategy == 'merge':
            # Merge on common columns
            common_columns = set(dict_data.columns) & set(combined_supplements.columns)
            if common_columns:
                enhanced_data = pd.merge(dict_data, combined_supplements, on=list(common_columns), how='outer')
            else:
                enhanced_data = pd.concat([dict_data, combined_supplements], ignore_index=True, sort=False)
        else:  # replace
            enhanced_data = combined_supplements
        
        # Clean enhanced data
        if cu:
            enhanced_data = cu.clean_dataframe(enhanced_data)
        else:
            enhanced_data = enhanced_data.dropna(how='all')
            enhanced_data = enhanced_data.drop_duplicates()
        
        # Save enhanced dictionary
        enhanced_filename = f"{dict_name}_enhanced.csv"
        enhanced_path = output_dir / enhanced_filename
        
        if cu:
            cu.save_data(enhanced_data, enhanced_path)
        else:
            enhanced_data.to_csv(enhanced_path, index=False)
        
        enhanced_dictionaries[dict_name] = enhanced_data
        cu.log_and_print(f"✅ Enhanced {dict_name}: {len(dict_data)} -> {len(enhanced_data)} rows -> {enhanced_path}")
    
    cu.log_and_print(f"✅ Enhanced {len(enhanced_dictionaries)} dictionaries")
    return enhanced_dictionaries


def run_complete_workflow(input_paths: List[Union[str, Path]],
                         dictionary_paths: List[Union[str, Path]],
                         output_dir: Union[str, Path],
                         workflow_steps: Optional[List[str]] = None,
                         **kwargs: Any) -> Dict[str, Any]:
    """
    Run the complete dictionary enhancement workflow.
    
    Args:
        input_paths: List of paths to supplement files
        dictionary_paths: List of paths to dictionary files
        output_dir: Base directory for all outputs
        workflow_steps: List of steps to run (default: all steps)
        **kwargs: Additional arguments for workflow steps
        
    Returns:
        Dictionary containing results from each workflow step
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Default workflow steps
    if workflow_steps is None:
        workflow_steps = ['prepare', 'split', 'enhance']
    
    cu.log_and_print(f"🚀 Starting Dictionary Workflow with steps: {', '.join(workflow_steps)}")
    
    results = {}
    
    # Step 1: Prepare supplements
    if 'prepare' in workflow_steps:
        cu.log_and_print("📋 Step 1: Preparing supplements...")
        prepared_supplements = prepare_supplements(
            input_paths=input_paths,
            output_path=output_dir / "prepared_supplements.csv",
            **kwargs
        )
        results['prepared_supplements'] = prepared_supplements
        cu.log_and_print("✅ Step 1 completed")
    
    # Step 2: Split supplements by domain
    if 'split' in workflow_steps:
        cu.log_and_print("✂️ Step 2: Splitting supplements by domain...")
        supplements_data = results.get('prepared_supplements', prepared_supplements)
        split_dir = output_dir / "split_supplements"
        domain_supplements = split_supplements_by_domain(
            supplements_data=supplements_data,
            output_dir=split_dir,
            **kwargs
        )
        results['domain_supplements'] = domain_supplements
        cu.log_and_print("✅ Step 2 completed")
    
    # Step 3: Enhance dictionaries
    if 'enhance' in workflow_steps:
        cu.log_and_print("🔧 Step 3: Enhancing dictionaries...")
        split_dir = output_dir / "split_supplements"
        enhanced_dir = output_dir / "enhanced_dictionaries"
        
        # Use split supplements if available, otherwise use original supplements
        if 'domain_supplements' in results:
            supplement_paths = [split_dir]
        else:
            supplement_paths = input_paths
        
        enhanced_dictionaries = enhance_dictionaries(
            dictionary_paths=dictionary_paths,
            supplement_paths=supplement_paths,
            output_dir=enhanced_dir,
            **kwargs
        )
        results['enhanced_dictionaries'] = enhanced_dictionaries
        cu.log_and_print("✅ Step 3 completed")
    
    cu.log_and_print("🎉 Dictionary Workflow completed successfully!")
    return results 
# data_content_comparer/plugins/release_consistency_mode.py

"""
Release Consistency Mode Plugin

This plugin consolidates the release_consistency_checker functionality
into the data_content_comparer tool as a specialized comparison mode.

Features:
- Release-to-release comparison (R5 vs R6)
- Domain-specific configurations
- Dtype alignment and missing value handling
- Change detection and reporting
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from ....common import cu

# Release constants for comparison
RELEASE_1 = "Release_1"  # Old release
RELEASE_2 = "Release_2"  # New release


def extract_release_labels(old_file: Path, new_file: Path) -> Tuple[str, str]:
    """
    Extract release numbers from filenames and create dynamic labels.
    
    Args:
        old_file: Path to the older release file
        new_file: Path to the newer release file
        
    Returns:
        Tuple of (label_old, label_new) for use in comparisons
    """
    # Extract release number from old file (e.g., "HD Release 6 Biomarkers_FINAL.csv")
    old_match = re.search(r"Release (\d+)", old_file.name)
    release_num_old = old_match.group(1) if old_match else "unknown"
    
    # Extract release number from new file (e.g., "RP_HD7_Biomarkers.xlsx")
    new_match = re.search(r"HD(\d+)|Release (\d+)", new_file.name)
    if new_match:
        # Handle both "HD7" and "Release 7" patterns
        release_num_new = new_match.group(1) or new_match.group(2)
    else:
        release_num_new = "unknown"
    
    # Create dynamic labels
    label_old = f"Release_{release_num_old}"
    label_new = f"Release_{release_num_new}"
    
    cu.log_and_print(f"📊 Using dynamic labels: {label_old} vs {label_new}")
    
    return label_old, label_new


def get_domain_config(domain: str) -> Optional[Dict[str, Any]]:
    """
    Get domain-specific configuration from config.yaml.
    
    Args:
        domain: Domain name (e.g., "Clinical", "Biomarkers")
        
    Returns:
        Domain configuration dictionary or None if not found
    """
    try:
        config = cu.get_config()
        tool_configs = config.tool_configs
        data_comparer_config = tool_configs.get('data_content_comparer', {})
        domains_config = data_comparer_config.get('domains', {})
        
        return domains_config.get(domain)
    except Exception as e:
        cu.log_and_print(f"⚠️ Could not load config for {domain}: {e}", level="warning")
        return None


def get_release_consistency_config() -> Dict[str, Any]:
    """
    Get global release consistency configuration from config.yaml.
    
    Returns:
        Release consistency configuration dictionary
    """
    try:
        config = cu.get_config()
        tool_configs = config.tool_configs
        data_comparer_config = tool_configs.get('data_content_comparer', {})
        return data_comparer_config.get('release_consistency', {})
    except Exception as e:
        cu.log_and_print(f"⚠️ Could not load release consistency config: {e}", level="warning")
        # Return default configuration
        return {
            "base_path": "data/domains",
            "release_file_pattern": "HD Release *.csv",
            "release_number_regex": r"HD Release (\d+)",
            "fallback_patterns": ["RP_HD*.xlsx", "HD Release *.xlsx"]
        }


def find_highest_release_file(domain_path: Path, old_data_dir: str = "old_data") -> Optional[Path]:
    """
    Find the highest release number file in the old_data directory.
    
    Args:
        domain_path: Path to the domain directory
        old_data_dir: Name of the old data subdirectory
        
    Returns:
        Path to the highest release file, or None if not found
    """
    import re
    old_data_path = domain_path / old_data_dir
    if not old_data_path.exists():
        cu.log_and_print(f"❌ Old data directory not found: {old_data_path}", level="error")
        return None
    
    # Get configuration
    config = get_release_consistency_config()
    release_pattern = config.get("release_file_pattern", "HD Release *.csv")
    # Patch: Allow for optional suffixes like _FINAL or _Domain
    release_regex = config.get("release_number_regex", r"HD Release (\d+)")
    # Fixed regex to match: "HD Release 6 Clinical_FINAL.csv", "HD Release 5 Clinical.csv", etc.
    patched_release_regex = r"HD Release (\d+)(?: [^_]*)?(?:_FINAL)?\.csv$"
    
    # Test the regex with actual filenames to debug
    test_files = ["HD Release 6 Clinical_FINAL.csv", "HD Release 5 Clinical.csv"]
    for test_file in test_files:
        test_match = re.search(patched_release_regex, test_file)
        cu.log_and_print(f"  🧪 Test regex '{patched_release_regex}' on '{test_file}': {'✅ Match' if test_match else '❌ No match'}")
    
    cu.log_and_print(f"🔎 Scanning for release files in {old_data_path} with pattern '{release_pattern}' and regex '{patched_release_regex}'")
    
    # Look for files matching the release pattern
    release_files = []
    for file_path in old_data_path.glob(release_pattern):
        cu.log_and_print(f"  🗂️ Found candidate: {file_path.name}")
        match = re.search(patched_release_regex, file_path.name)
        if match:
            release_num = int(match.group(1))
            cu.log_and_print(f"    ✅ Matched release {release_num} in {file_path.name}")
            release_files.append((release_num, file_path))
        else:
            cu.log_and_print(f"    ❌ Skipped (no match): {file_path.name}")
    
    if not release_files:
        cu.log_and_print(f"❌ No release files found in {old_data_path}", level="error")
        return None
    
    # Return the highest release number file
    highest_release = max(release_files, key=lambda x: x[0])
    cu.log_and_print(f"📊 Found highest release file: {highest_release[1].name} (Release {highest_release[0]})")
    return highest_release[1]


def find_newest_file(domain_path: Path, file_pattern: str) -> Optional[Path]:
    """
    Find the newest file in the domain root directory.
    
    Args:
        domain_path: Path to the domain directory
        file_pattern: Pattern to match the newest file
        
    Returns:
        Path to the newest file, or None if not found
    """
    # Get configuration for fallback patterns
    config = get_release_consistency_config()
    fallback_patterns = config.get("fallback_patterns", ["RP_HD*.xlsx", "HD Release *.xlsx"])
    
    # Look for exact filename match first
    exact_match = domain_path / file_pattern
    if exact_match.exists():
        cu.log_and_print(f"📊 Found newest file: {exact_match.name}")
        return exact_match
    
    # If exact match not found, try fallback patterns
    for pattern in fallback_patterns:
        for file_path in domain_path.glob(pattern):
            if not file_path.name.startswith("HD Data Dictionary"):
                cu.log_and_print(f"📊 Found newest file: {file_path.name}")
                return file_path
    
    cu.log_and_print(f"❌ Newest file not found in {domain_path}", level="error")
    return None


def run_mode(input_paths: List[Path], output_dir: Path, domain: Optional[str] = None, 
             mode: str = "old_only", debug: bool = False, **kwargs) -> None:
    """
    Run release consistency comparison mode.
    
    Args:
        input_paths: List of input file paths (can be empty for domain mode)
        output_dir: Output directory for results
        domain: Domain to process (e.g., "Clinical", "Biomarkers")
        mode: Comparison mode ('old_only' or 'standard')
        debug: Enable debug mode for dtype checks
        **kwargs: Additional arguments
    """
    cu.log_and_print("🔍 Running Release Consistency Mode...")
    
    if input_paths and len(input_paths) >= 2:
        # Manual file comparison mode
        cu.log_and_print("📁 Manual file comparison mode detected")
        run_manual_comparison(input_paths[0], input_paths[1], output_dir, mode, debug)
    elif domain:
        # Domain-based comparison mode
        cu.log_and_print(f"📊 Domain-based comparison for: {domain}")
        run_domain_comparison(domain, output_dir, mode, debug)
    else:
        # Default to all available domains from config
        cu.log_and_print("📊 Processing all available domains")
        config = get_release_consistency_config()
        base_path = Path(config.get("base_path", "data/domains"))
        
        if base_path.exists():
            for domain_dir in base_path.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    domain_name = domain_dir.name
                    cu.log_and_print(f"🔍 Checking domain: {domain_name}")
                    run_domain_comparison(domain_name, output_dir, mode, debug)
        else:
            cu.log_and_print(f"❌ Base path not found: {base_path}", level="error")


def run_manual_comparison(old_file: Path, new_file: Path, output_dir: Path, 
                         mode: str = "old_only", debug: bool = False) -> None:
    """
    Run manual comparison between two specific files.
    
    Args:
        old_file: Path to older file
        new_file: Path to newer file
        output_dir: Output directory
        mode: Comparison mode
        debug: Enable debug mode
    """
    cu.log_and_print(f"📂 Loading files: {old_file.name} vs {new_file.name}")
    
    # Load datasets
    df_old = cu.load_data(old_file)
    df_new = cu.load_data(new_file)
    
    # Run comparison
    monitor_changes(
        dataset_name="Manual_Run",
        df_old=df_old,
        df_new=df_new,
        output_path=output_dir,
        debug=debug,
        mode=mode,
        old_file=old_file,
        new_file=new_file
    )


def run_domain_comparison(domain: str, output_dir: Path, mode: str = "old_only", 
                         debug: bool = False) -> None:
    """
    Run comparison for a specific domain.
    
    Args:
        domain: Domain name to process
        output_dir: Output directory
        mode: Comparison mode
        debug: Enable debug mode
    """
    # Get domain-specific configuration
    dataset_config = get_domain_config(domain)
    if not dataset_config:
        cu.log_and_print(f"❌ No configuration found for domain: {domain}", level="error")
        return

    # Get global configuration
    global_config = get_release_consistency_config()
    base_path = Path(global_config.get("base_path", "data/domains"))
    domain_path = base_path / domain
    
    if not domain_path.exists():
        cu.log_and_print(f"❌ Domain directory not found: {domain_path}", level="error")
        return
    
    cu.log_and_print(f"🔍 Looking for data in: {domain_path}")

    try:
        # Find the newest file in domain root
        newest_file_pattern = dataset_config.get("newest_file_pattern", "RP_HD*.xlsx")
        newest_file = find_newest_file(domain_path, newest_file_pattern)
        if not newest_file:
            return
        
        # Find the highest release file in old_data directory
        old_data_dir = dataset_config.get("old_data_dir", "old_data")
        highest_release_file = find_highest_release_file(domain_path, old_data_dir)
        if not highest_release_file:
            return
        
        cu.log_and_print(f"📊 Comparing: {highest_release_file.name} vs {newest_file.name}")
        
        # Create domain-specific output directory
        domain_output_dir = output_dir / domain
        domain_output_dir.mkdir(parents=True, exist_ok=True)
        cu.log_and_print(f"📁 Output directory: {domain_output_dir}")
        
        # Load datasets
        df_old = cu.load_data(highest_release_file)
        df_new = cu.load_data(newest_file)
        
        # Run comparison with dataset config
        monitor_changes(
            dataset_name=domain,
            df_old=df_old,
            df_new=df_new,
            output_path=domain_output_dir,
            dataset_config=dataset_config,
            debug=debug,
            mode=mode,
            old_file=highest_release_file,
            new_file=newest_file
        )
        
    except Exception as e:
        cu.log_and_print(f"❌ Error while processing {domain}: {e}", level="error")
        raise


def monitor_changes(
    dataset_name: str,
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    output_path: Path,
    dataset_config: Optional[Dict[str, Any]] = None,
    debug: bool = False,
    mode: str = "old_only",
    old_file: Optional[Path] = None,
    new_file: Optional[Path] = None
) -> None:
    """
    Monitor changes between two datasets (consolidated from release_consistency_checker).
    
    Args:
        dataset_name: Name of the dataset being compared
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        output_path: Directory to save comparison results
        dataset_config: Dataset-specific configuration
        debug: Enable debug mode
        mode: Comparison mode
        old_file: Path to old file (for dynamic labeling)
        new_file: Path to new file (for dynamic labeling)
    """
    cu.log_and_print(f"🔍 Processing {dataset_name}...")
    
    # Apply dataset-specific configuration if provided
    if dataset_config:
        missing_values = dataset_config.get("missing_values", ["-9999", "-8888"])
        initial_drop_cols = dataset_config.get("initial_drop_cols", [])
        add_to_dict = dataset_config.get("add_to_dict", {})
        
        # Drop initial columns if specified
        if initial_drop_cols:
            df_old = df_old.drop(columns=initial_drop_cols, errors="ignore")
            df_new = df_new.drop(columns=initial_drop_cols, errors="ignore")
            cu.log_and_print(f"🗑️ Dropped columns: {initial_drop_cols}")
    else:
        missing_values = ["-9999", "-8888"]
        add_to_dict = {}
    
    # Align dtypes if debug mode is enabled
    if debug:
        align_dtypes(df_old, df_new, dataset_name, missing_values)
    
    # Run comparison based on mode
    if mode == "old_only":
        compare_datasets_filtered(df_old, df_new, dataset_name, output_path, old_file, new_file)
    else:
        compare_datasets(df_old, df_new, dataset_name, output_path, old_file, new_file)
    
    # Analyze column changes
    analyze_column_changes(
        set(df_old.columns) - set(df_new.columns),
        set(df_new.columns) - set(df_old.columns),
        dataset_name
    )


def compare_datasets(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    output_path: Path,
    old_file: Optional[Path] = None,
    new_file: Optional[Path] = None
) -> None:
    """
    Compare row-level values and identify changes.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        output_path: Directory to save comparison results
        old_file: Path to old file (for dynamic labeling)
        new_file: Path to new file (for dynamic labeling)
    """
    # Extract dynamic release labels from filenames
    if old_file and new_file:
        label_old, label_new = extract_release_labels(old_file, new_file)
    else:
        # Fallback to static labels if files not provided
        label_old, label_new = RELEASE_1, RELEASE_2

    df_old["Release"] = label_old
    df_new["Release"] = label_new

    combined = pd.concat([df_old, df_new], ignore_index=True).copy()
    combined = combined.groupby(["Med_ID", "Visit_ID", "Release"]).agg(lambda x: list(x)).reset_index()

    pivoted = combined.pivot(index=["Med_ID", "Visit_ID"], columns="Release")
    diffs = pivoted.xs(label_old, level="Release", axis=1) != pivoted.xs(label_new, level="Release", axis=1)
    changed_rows = pivoted[diffs.any(axis=1)]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{dataset_name}_changed_rows.csv"
    changed_rows.to_csv(output_file)

    cu.log_and_print(f"🔍 {dataset_name}: {changed_rows.shape[0]} rows with changes saved to {output_file}")


def compare_datasets_filtered(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    output_path: Path,
    old_file: Optional[Path] = None,
    new_file: Optional[Path] = None
) -> None:
    """
    Compare datasets, excluding participants unique to one release.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        output_path: Directory to save comparison results
        old_file: Path to old file (for dynamic labeling)
        new_file: Path to new file (for dynamic labeling)
    """
    # Extract dynamic release labels from filenames
    if old_file and new_file:
        label_old, label_new = extract_release_labels(old_file, new_file)
    else:
        # Fallback to static labels if files not provided
        label_old, label_new = RELEASE_1, RELEASE_2

    # Drop any existing "Release" columns before setting
    df_old = df_old.drop(columns=["Release"], errors="ignore")
    df_new = df_new.drop(columns=["Release"], errors="ignore")

    df_old["Release"] = label_old
    df_new["Release"] = label_new

    combined = pd.concat([df_old, df_new], ignore_index=True)

    # Pivot directly
    pivoted = combined.pivot_table(
        index=["Med_ID", "Visit_ID"], 
        columns="Release",
        aggfunc="first"
    )

    # Flatten multi-index columns
    pivoted.columns = [f"{col}_{release}" for col, release in pivoted.columns]

    # Identify changes properly
    col_pairs = [(col.replace(f"_{label_old}", ""), col.replace(f"_{label_new}", "")) 
                 for col in pivoted.columns if f"_{label_old}" in col]

    changed_rows = []

    for col_base, _ in col_pairs:
        col_r1 = f"{col_base}_{label_old}"
        col_r2 = f"{col_base}_{label_new}"

        if col_r1 in pivoted.columns and col_r2 in pivoted.columns:
            # Compare non-missing and unequal
            mask = (pivoted[col_r1] != pivoted[col_r2]) & ~(pivoted[col_r1].isna() & pivoted[col_r2].isna())
            changed_rows.append(mask)

    if changed_rows:
        full_mask = changed_rows[0]
        for mask in changed_rows[1:]:
            full_mask |= mask
        filtered_rows = pivoted[full_mask]
    else:
        filtered_rows = pivoted.iloc[[]]  # empty DataFrame

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Save filtered rows
    output_file = output_path / f"{dataset_name}_filtered_rows.csv"
    filtered_rows.to_csv(output_file)

    cu.log_and_print(f"🔍 {dataset_name}: {filtered_rows.shape[0]} filtered rows with true changes saved to {output_file}")


def align_dtypes(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    missing_values: List[str]
) -> None:
    """
    Align dtypes of old dataset to match new dataset for shared columns.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        missing_values: List of values to treat as missing/NA
    """
    common_cols = set(df_old.columns).intersection(set(df_new.columns))

    mismatches = {
        col: (df_old[col].dtype, df_new[col].dtype)
        for col in common_cols if df_old[col].dtype != df_new[col].dtype
    }

    if mismatches:
        cu.log_and_print(f"\n🔍 Fixing dtype mismatches in {dataset_name}:")
        for col, (dtype_old, dtype_new) in mismatches.items():
            cu.log_and_print(f"🔄 Converting {col}: {dtype_old} → {dtype_new}")
            try:
                df_old[col] = df_old[col].replace(missing_values, np.nan)
                df_old[col] = df_old[col].astype(dtype_new)
            except Exception as e:
                cu.log_and_print(f"⚠️ Could not convert {col}: {e}")
        cu.log_and_print(f"✅ Dtype alignment complete.")
    else:
        cu.log_and_print(f"\n✅ No dtype mismatches found in {dataset_name}.")


def analyze_column_changes(
    only_in_old: Set[str],
    only_in_new: Set[str],
    dataset_name: str
) -> None:
    """
    Analyze and report column changes between releases.
    
    Args:
        only_in_old: Columns only in the old release
        only_in_new: Columns only in the new release
        dataset_name: Name of the dataset being analyzed
    """
    if only_in_old or only_in_new:
        cu.log_and_print(f"\n📊 Column changes in {dataset_name}:")
        
        if only_in_old:
            cu.log_and_print(f"🗑️ Removed columns: {sorted(only_in_old)}")
        
        if only_in_new:
            cu.log_and_print(f"➕ Added columns: {sorted(only_in_new)}")
    else:
        cu.log_and_print(f"\n✅ No column changes detected in {dataset_name}.") 
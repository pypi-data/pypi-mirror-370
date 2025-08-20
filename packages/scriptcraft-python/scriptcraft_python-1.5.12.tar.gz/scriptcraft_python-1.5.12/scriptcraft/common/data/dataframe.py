"""
scripts/common/dataframe_utils.py

📊 Utility functions for working with pandas DataFrames,
including column renaming, normalization, and diagnostics.
"""

from typing import Dict, List, Optional, Union, Callable, Set, Any
from pathlib import Path
import pandas as pd
from ..logging import log_and_print
from ..io.paths import COLUMN_ALIASES

# ==== 📉 Missing Values Analysis ====

def display_missing_values(
    data_dict: Dict[str, pd.DataFrame],
    output_file: Optional[Union[str, Path]] = None
) -> None:
    """
    Displays missing value counts for each dataset and optionally saves to file.

    Args:
        data_dict: Dictionary where keys are dataset names and values are DataFrames.
        output_file: Optional path to save the missing values report.

    Example:
        >>> display_missing_values({"Clinical": clinical_df}, output_file="missing_report.txt")

    """
    output = []
    for name, df in data_dict.items():
        missing_counts = df.isna().sum().sort_values(ascending=False)
        missing_counts = missing_counts[missing_counts > 0]
        if not missing_counts.empty:
            info = f"\n🔍 Missing Values in {name}:\n{missing_counts.to_string()}"
            log_and_print(info)
            output.append(info)

    if output_file and output:
        with open(output_file, "a", encoding="utf-8") as f:
            f.writelines(output)

# ==== 📄 Column Name Normalization ====

def normalize_column_names(
    df: pd.DataFrame,
    alias_map: Dict[str, List[str]],
    required_columns: Optional[List[str]] = None,
    context_label: str = ""
) -> pd.DataFrame:
    """
    Standardizes DataFrame column names based on a provided alias map and logs changes.

    Args:
        df: The input DataFrame.
        alias_map: Mapping from standard name to list of possible aliases.
        required_columns: List of columns that must exist after renaming (optional).
        context_label: Label used in logs to identify the dataset.

    Returns:
        DataFrame with standardized column names.

    Example:
        >>> normalize_column_names(df, {"Age": ["age", "AGE"]}, required_columns=["Age"])
    """
    rename_map = {}
    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = standard_name

    if rename_map:
        log_and_print(f"🔧 [{context_label}] Renamed columns: {rename_map}")
    else:
        log_and_print(f"ℹ️ [{context_label}] No column renaming needed.")

    df = df.rename(columns=rename_map)

    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            log_and_print(f"⚠️ [{context_label}] Missing expected standardized columns after renaming: {missing}")

    return df

# ==== 🔧 Safe Transform Utilities ====

def apply_safe_transform(
    df: pd.DataFrame,
    columns: List[str],
    transform_fn: Callable[[Any], Any],
    error_value: Optional[Any] = None
) -> pd.DataFrame:
    """
    Safely applies a transformation function to specified columns.

    Args:
        df: Input DataFrame
        columns: List of columns to transform
        transform_fn: Function to apply to each value
        error_value: Value to use when transformation fails (None keeps original value)

    Returns:
        DataFrame with transformed values

    Example:
        >>> apply_safe_transform(df, ["Age"], lambda x: int(x), error_value=0)
    """
    result = df.copy()
    for col in columns:
        if col in df.columns:
            try:
                result[col] = df[col].apply(lambda x: transform_fn(x) if pd.notna(x) else x)
            except Exception as e:
                log_and_print(f"⚠️ Error transforming column {col}: {str(e)}")
                if error_value is not None:
                    result[col] = error_value
    return result

# ==== 📊 Column Statistics ====

def get_column_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive column statistics for a DataFrame.

    Returns:
        DataFrame containing column statistics (type, missing values, unique values, etc.)

    Example:
        >>> stats_df = get_column_stats(df)
    """
    stats = []
    for col in df.columns:
        unique_count = df[col].nunique()
        missing_count = df[col].isna().sum()
        stats.append({
            'column': col,
            'dtype': str(df[col].dtype),
            'unique_values': unique_count,
            'missing_values': missing_count,
            'missing_percentage': (missing_count / len(df)) * 100
        })
    return pd.DataFrame(stats)

def get_column_letter(column_number: int) -> str:
    """
    Convert a column number to Excel column letters.
    
    Args:
        column_number: Column number (1-based)
    
    Returns:
        Excel column letter (e.g., A, B, ..., Z, AA, AB, etc.)
    """
    result = ""
    while column_number > 0:
        column_number -= 1
        result = chr(65 + (column_number % 26)) + result
        column_number //= 26
    return result

def get_common_columns(df1: pd.DataFrame, df2: pd.DataFrame) -> Set[str]:
    """
    Get set of column names common to both DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
    
    Returns:
        Set of common column names
    """
    return set(df1.columns) & set(df2.columns)

def validate_required_columns(df: pd.DataFrame, required_cols: List[str]) -> bool:
    """
    Check if DataFrame has all required columns.
    
    Args:
        df: DataFrame to check
        required_cols: List of required column names
    
    Returns:
        True if all required columns present, False otherwise
    """
    missing = set(required_cols) - set(df.columns)
    if missing:
        print(f"❌ Missing required columns: {missing}")
        return False
    return True

def get_column_dtypes(df: pd.DataFrame) -> Dict[str, str]:
    """
    Get dictionary of column names to their data types.
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        Dict mapping column names to dtype strings
    """
    return {col: str(dtype) for col, dtype in df.dtypes.items()}

def compare_column_dtypes(df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, tuple]:
    """
    Compare data types of common columns between DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
    
    Returns:
        Dict mapping column names to (df1_dtype, df2_dtype) tuples
    """
    common_cols = get_common_columns(df1, df2)
    return {
        col: (str(df1[col].dtype), str(df2[col].dtype))
        for col in common_cols
    }

def find_duplicate_rows(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Find duplicate rows in DataFrame.
    
    Args:
        df: DataFrame to check
        subset: Optional list of columns to consider
    
    Returns:
        DataFrame containing only the duplicate rows
    """
    return df[df.duplicated(subset=subset, keep=False)].sort_values(
        by=subset or df.columns.tolist()
    )

def drop_empty_columns(df: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
    """
    Drop columns with too many null values.
    
    Args:
        df: DataFrame to process
        threshold: Fraction of values that must be null to drop (0.0-1.0)
    
    Returns:
        DataFrame with empty columns removed
    """
    null_frac = df.isnull().mean()
    cols_to_drop = null_frac[null_frac >= threshold].index
    return df.drop(columns=cols_to_drop)

def to_numeric_safe(series: pd.Series) -> pd.Series:
    """
    Convert series to numeric, preserving non-numeric values as null.
    
    Args:
        series: Series to convert
    
    Returns:
        Numeric series with non-numeric values as null
    """
    return pd.to_numeric(series, errors='coerce')

def find_non_numeric(series: pd.Series) -> pd.Series:
    """
    Find non-numeric values in a series.
    
    Args:
        series: Series to check
    
    Returns:
        Series containing only the non-numeric values
    """
    numeric = pd.to_numeric(series, errors='coerce')
    return series[numeric.isna() & series.notna()].unique()

def describe_numeric(df: pd.DataFrame, include_nulls: bool = True) -> pd.DataFrame:
    """
    Get descriptive statistics for numeric columns.
    
    Args:
        df: DataFrame to analyze
        include_nulls: Whether to include null counts
    
    Returns:
        DataFrame with descriptive statistics
    """
    stats = df.describe()
    if include_nulls:
        stats.loc['null_count'] = df.isnull().sum()
        stats.loc['null_pct'] = df.isnull().mean()
    return stats

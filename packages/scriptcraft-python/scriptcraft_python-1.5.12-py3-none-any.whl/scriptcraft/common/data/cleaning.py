"""
scripts/common/value_cleaning.py

🧹 Utilities for standardizing and cleaning value formats in datasets,
including handling missing values, normalizing numeric formats, 
and cleaning brace formatting.
"""

import re
from typing import Any, Dict, Optional, Union
import pandas as pd
from ..logging import log_and_print
from ..io.paths import MISSING_VALUE_STRINGS

# ==== 🚫 Missing Value Handling ====

def is_missing_like(val: Any) -> bool:
    """
    Check if a value should be treated as missing.

    Args:
        val: Input value.

    Returns:
        True if the value is missing-like, False otherwise.

    Example:
        >>> is_missing_like("-9999")
        True
        >>> is_missing_like("Valid Entry")
        False
    """
    if pd.isna(val):
        return True
    return str(val).strip().upper() in MISSING_VALUE_STRINGS


def normalize_value(val: Any) -> str:
    """
    Normalize a value by handling missing values and converting numerics to string.

    Args:
        val: Input value.

    Returns:
        Normalized value as a string.

    Example:
        >>> normalize_value("-9999")
        'MISSING'
        >>> normalize_value(5.0)
        '5'
    """
    if is_missing_like(val):
        return "MISSING"
    if isinstance(val, (int, float)):
        return str(int(val)) if float(val).is_integer() else str(val)
    return str(val).strip()


# ==== ✍️ Brace/Text Formatting Utilities ====

def prevent_pipe_inside_braces(text: str) -> str:
    """
    Prevent insertion of ' | ' between numeric and alphabetic characters inside text,
    while preserving content within `{}` groups unchanged.

    Example:
        Input:  "5 Female {5-Female}"
        Output: "5 | Female {5-Female}"

    Args:
        text: Input string to clean.

    Returns:
        Cleaned string with ' | ' added only outside of brace groups.
    """
    parts = re.split(r'(\{[^}]*\})', text)
    for i in range(len(parts)):
        if not parts[i].startswith('{'):
            parts[i] = re.sub(r'(\d)\s([A-Za-z])', r'\1 | \2', parts[i])
    return ''.join(parts)


def fix_numeric_dash_inside_braces(text: str) -> str:
    """
    Remove spacing around '-' between two numbers inside `{}` groups.

    Example:
        Input:  "{5 - 10}"
        Output: "{5-10}"

    Args:
        text: Input string to clean.

    Returns:
        Cleaned string with numeric ranges formatted correctly inside braces.
    """
    parts = re.split(r'(\{[^}]*\})', text)
    for i in range(len(parts)):
        if parts[i].startswith('{') and parts[i].endswith('}'):
            parts[i] = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', parts[i])
    return ''.join(parts)


def fix_word_number_dash_inside_braces(text: str) -> str:
    """
    Standardize spacing around dashes between words and numbers inside `{}` groups.
    Handles both word-number and number-word patterns.

    Examples:
        Input:  "{5 - Male}" → "{5- Male}"
                "{Male - 5}" → "{Male -5}"

    Args:
        text: Input string to clean.

    Returns:
        Cleaned string with proper dash spacing inside braces.
    """
    parts = re.split(r'(\{[^}]*\})', text)
    for i in range(len(parts)):
        if parts[i].startswith('{') and parts[i].endswith('}'):
            parts[i] = re.sub(r'(?<=\d)\s*-\s*(?=[A-Za-z])', ' - ', parts[i])
            parts[i] = re.sub(r'(\{[^}]*?)\s+-\s+(\d+)', r'\1-\2', parts[i])
    return ''.join(parts)


def clean_brace_formatting(text: str) -> str:
    """
    Apply all standard brace-related cleaning steps in the correct order:
    1. Prevent unwanted pipes being inserted inside braces.
    2. Fix spacing for numeric ranges inside braces.
    3. Fix spacing for word-number and number-word dashes inside braces.

    Args:
        text: Input text to clean.

    Returns:
        Cleaned text with consistent brace formatting.
        
    Example:
        >>> clean_brace_formatting("5 Female {5 - Male}")
        '5 | Female {5- Male}'
    """
    text = prevent_pipe_inside_braces(text)
    text = fix_numeric_dash_inside_braces(text)
    text = fix_word_number_dash_inside_braces(text)
    return text


# ==== 📄 Column & DataFrame Operations ====

def standardize_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Rename columns in a DataFrame based on a mapping and log any missing columns.

    Args:
        df: Input DataFrame.
        mapping: Dictionary mapping original column names to standardized names.

    Returns:
        DataFrame with renamed columns.
    """
    df = df.rename(columns=mapping)
    missing = [col for col in mapping.values() if col not in df.columns]
    if missing:
        log_and_print(f"⚠️ Missing expected columns after renaming: {missing}")
    return df


def parse_missing_unit(value: Any) -> Any:
    """
    Standardizes the Missing/Unit of Measure column formatting.

    Args:
        value: Value to standardize.

    Returns:
        Standardized value.
    """
    if pd.isna(value) or isinstance(value, (int, float)):
        return value
    return re.sub(r'=\s*', '= ', str(value))


# ==== 🔢 Numeric Cleaning Utilities ====

def get_clean_numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Returns a cleaned numeric Series from a DataFrame column,
    excluding known missing codes and non-numeric entries.

    Args:
        df: Input DataFrame.
        col: Column to clean.

    Returns:
        Cleaned Series containing only numeric values.
    """
    if col not in df.columns:
        return pd.Series(dtype=float)

    series = df[col]
    series = series[~series.apply(is_missing_like)]

    numeric_series = pd.to_numeric(series, errors="coerce")
    cleaned = numeric_series.dropna()

    if len(series) != len(cleaned):
        log_and_print(
            f"⚠️ Removed {len(series) - len(cleaned)} non-numeric values from '{col}' before numeric analysis."
        )

    return cleaned


def clean_supplement_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard supplement data cleaning.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
    
    # Remove completely empty columns
    df = df.dropna(axis=1, how='all')
    
    # Fill NaN values with empty string
    df = df.fillna("")
    
    return df


def standardize_supplement_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize supplement column names and structure.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with standardized columns
    """
    # Standard column mappings
    column_mappings = {
        'variable': 'Main Variable',
        'notes': 'Label',
        'min': 'Min_Value',
        'max': 'Max_Value'
    }
    
    # Rename columns if they exist
    for old_col, new_col in column_mappings.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    return df


def create_standardized_supplement_row(
    variable: str,
    label: str = "",
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    missing_unit: str = "-9999",
    quality_level: str = "Supplement",
    visits: str = "",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create a standardized supplement row.
    
    Args:
        variable: Main variable name
        label: Variable label
        min_val: Minimum value
        max_val: Maximum value
        missing_unit: Missing value/unit of measure
        quality_level: Level of quality check
        visits: Visit information
        notes: Additional notes
        
    Returns:
        Dictionary representing a standardized supplement row
    """
    # Determine value field
    if min_val is not None and max_val is not None:
        try:
            min_int = int(float(min_val))
            max_int = int(float(max_val))
            value = f"{{{min_int}-{max_int}}}"
        except (ValueError, TypeError):
            value = "Numeric"
    else:
        value = "Numeric"
    
    return {
        "Main Variable": str(variable).strip(),
        "Label": str(label).strip(),
        "Value": value,
        "Missing/Unit of Measure": str(missing_unit),
        "Level of quality check": str(quality_level),
        "Visits": str(visits),
        "Notes": str(notes)
    }

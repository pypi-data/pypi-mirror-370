# dictionary_driven_checker/utils.py

"""Core utilities for dictionary-driven validation.

This module provides the core logic for validating data against a dictionary,
with plugin validators as fallbacks for special cases.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from scriptcraft.common import (
    log_and_print, extract_expected_values,
    OutlierMethod
)

# Import registry from the plugins module (which now gets it from common)
from scriptcraft.common.plugins import registry

@dataclass
class ValidationResult:
    """Container for validation results of a single value."""
    row_index: int
    visit_number: int 
    column: str
    value: Any
    message: str
    is_warning: bool = False

def validate_against_dictionary(
    value: Any,
    expected_values: Optional[str],
    value_type: str,
    column: str
) -> Optional[str]:
    """Core dictionary validation logic.
    
    Args:
        value: The value to validate
        expected_values: Valid values/ranges from dictionary 
        value_type: Type of validation from dictionary
        column: Column name for context
        
    Returns:
        Error message if validation fails, None if passes
    """
    if pd.isna(value):
        return None
        
    if not expected_values:
        return None
        
    # Handle different dictionary value types
    value_type = str(value_type).lower().strip()
    
    if value_type == 'categorical':
        valid_values = extract_expected_values(expected_values)
        if str(value).strip() not in valid_values:
            return f"Not in dictionary"
            
    elif value_type == 'numeric':
        try:
            value = float(value)
            # Parse numeric ranges like "1-100" or ">= 0"
            if '-' in expected_values:
                min_val, max_val = map(float, expected_values.split('-'))
                if not (min_val <= value <= max_val):
                    return f"Outside valid range: {expected_values}"
            elif any(op in expected_values for op in ['>', '<', '=']):
                if not eval(f"{value} {expected_values}"):
                    return f"Does not satisfy: {expected_values}"
        except ValueError:
            return "Non-numeric value"
    
    # Try plugin validators as fallbacks
    validator_class = registry.get_all_validators().get(value_type)
    if validator_class:
        validator = validator_class()
        error = validator.validate_value(value, expected_values)
        if error:
            return error
            
    return None

def run_dictionary_checker(
    df: pd.DataFrame, 
    dict_df: pd.DataFrame,
    domain: str,
    output_path: Path,
    outlier_method: OutlierMethod
) -> None:
    """Validate dataset against data dictionary with plugin fallbacks.
    
    Args:
        df: Dataset to validate
        dict_df: Data dictionary DataFrame
        domain: Domain name for context
        output_path: Where to save results
        outlier_method: Method for numeric outlier detection
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Track validation results and stats
        results: List[ValidationResult] = []
        column_stats: Dict[str, Dict] = {}
        skipped_columns: List[str] = []
        
        log_and_print(f"\n🔍 Validating {domain} dataset against dictionary...")

        # Initialize plugin validators as fallbacks
        validators = {
            plugin_type: plugin_class(outlier_method) if plugin_type == "numeric" else plugin_class()
            for plugin_type, plugin_class in registry.get_all_plugins('validator').items()
        }

        # Process each column in the dictionary
        processed_cols = set()
        for _, row in dict_df.iterrows():
            col = str(row.get("Main Variable", "")).strip()
            if not col or col in processed_cols:
                continue
                
            processed_cols.add(col)
            if col not in df.columns:
                skipped_columns.append(col)
                continue

            # Extract validation rules
            value_type = str(row.get("Value Type", "")).strip().lower()
            expected_values = str(row.get("Expected Values", "")).strip()
            
            # Track stats for this column
            column_stats[col] = {
                "type": value_type,
                "total": len(df[col].dropna()),
                "flagged": 0
            }

            # Validate each value in the column
            for idx, value in df[col].items():
                visit = df.at[idx, "Visit"] if "Visit" in df.columns else 1
                
                # Try dictionary validation first
                error = validate_against_dictionary(
                    value, expected_values, value_type, col
                )
                
                # Fall back to plugins if no dictionary error
                if not error:
                    validator = validators.get(value_type)
                    if validator:
                        error = validator.validate_value(value, expected_values)
                
                if error:
                    results.append(ValidationResult(
                        row_index=idx,
                        visit_number=visit,
                        column=col,
                        value=value,
                        message=error,
                        is_warning=value_type == "numeric"  # Numeric issues are warnings
                    ))
                    column_stats[col]["flagged"] += 1

        # Save results
        if results:
            results_df = pd.DataFrame([
                {
                    "Row": r.row_index,
                    "Visit": r.visit_number,
                    "Column": r.column,
                    "Value": r.value,
                    "Message": r.message,
                    "Type": "Warning" if r.is_warning else "Error"
                }
                for r in results
            ])
            results_df.to_csv(output_path / f"{domain}_validation_results.csv", index=False)
            
            # Log summary
            total_errors = sum(1 for r in results if not r.is_warning)
            total_warnings = sum(1 for r in results if r.is_warning)
            log_and_print(f"\n📊 Validation Summary for {domain}:")
            log_and_print(f"   • {total_errors} errors")
            log_and_print(f"   • {total_warnings} warnings")
            log_and_print(f"   • {len(skipped_columns)} columns skipped")
            
            # Log column-specific stats
            for col, stats in column_stats.items():
                if stats["flagged"] > 0:
                    log_and_print(
                        f"   • {col}: {stats['flagged']} / {stats['total']} "
                        f"values flagged ({stats['type']})"
                    )
        else:
            log_and_print(f"✅ No validation issues found in {domain}")
            
    except Exception as e:
        log_and_print(f"❌ Error during validation: {str(e)}")
        raise

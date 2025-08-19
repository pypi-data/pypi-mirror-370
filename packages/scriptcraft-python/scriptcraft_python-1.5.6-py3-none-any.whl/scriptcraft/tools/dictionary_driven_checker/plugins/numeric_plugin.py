# dictionary_driven_checker/plugins/numeric_plugin.py

from typing import List, Dict, Tuple, Set, Optional
import pandas as pd
from scriptcraft.common.data.cleaning import get_clean_numeric_series, MISSING_VALUE_STRINGS
from scriptcraft.common.data.validation import FlaggedValue, ColumnValidator, get_status_emoji
from scriptcraft.common.logging import log_and_print
from scriptcraft.common.io.paths import OutlierMethod
from . import registry
from scriptcraft.common import cu

# Load configuration
config = cu.load_config()
checker_config = config.checkers.dictionary_checker

class NumericValidationError(Exception):
    """Custom exception for numeric validation errors"""
    pass

@registry.register("numeric")
class NumericValidator(ColumnValidator):
    """Plugin for numeric validation including outlier detection"""
    
    def __init__(self, method: Optional[OutlierMethod] = None):
        """Initialize with outlier detection method"""
        self.method = method or getattr(OutlierMethod, checker_config.get('outlier_method', 'IQR'))
        
    def validate(self, df: pd.DataFrame, col: str, expected_values: Set[Tuple[float, float]] = None) -> List[FlaggedValue]:
        """Validates numeric columns by checking for outliers or range violations"""
        try:
            if expected_values:
                return self._validate_ranges(df, col, expected_values)
            return self._validate_outliers(df, col)
        except NumericValidationError as e:
            log_and_print(f"{get_status_emoji('warning')} Validation error for column '{col}': {str(e)}")
            return []
        except Exception as e:
            log_and_print(f"{get_status_emoji('error')} Unexpected error validating column '{col}': {str(e)}")
            return []
        
    def _validate_ranges(self, df: pd.DataFrame, col: str, ranges: Set[Tuple[float, float]]) -> List[FlaggedValue]:
        """Validates numeric values against defined ranges using vectorized operations"""
        flagged = []
        
        if col not in df.columns:
            log_and_print(f"{get_status_emoji('warning')} Column '{col}' not found in dataframe")
            return flagged
            
        series = df[col].dropna()
        
        try:
            log_and_print(f"{get_status_emoji('processing')} Validating ranges in '{col}'...")
            
            # Convert to numeric, errors='coerce' will set invalid values to NaN
            numeric_series = pd.to_numeric(series, errors='coerce')
            
            # Create a mask for values outside all ranges
            in_range_mask = pd.Series(False, index=series.index)
            for low, high in ranges:
                in_range_mask |= (numeric_series >= low) & (numeric_series <= high)
            
            # Get indices where values are outside ranges
            outside_range_idx = series.index[~in_range_mask]
            
            # Flag values outside ranges
            for idx in outside_range_idx:
                if pd.isna(numeric_series[idx]):
                    flagged.append(
                        FlaggedValue.from_df_row(
                            df, idx, col, series[idx],
                            f"{get_status_emoji('invalid')} Non-numeric in range column"
                        )
                    )
                else:
                    flagged.append(
                        FlaggedValue.from_df_row(
                            df, idx, col, series[idx],
                            f"{get_status_emoji('invalid')} Outside defined range"
                        )
                    )
                    
            if flagged:
                log_and_print(f"{get_status_emoji('found_issues')} Found {len(flagged)} values outside defined ranges in '{col}'")
            else:
                log_and_print(f"{get_status_emoji('valid')} All values in '{col}' are within defined ranges")
                
        except Exception as e:
            raise NumericValidationError(f"Error validating ranges: {str(e)}")
                
        return flagged
        
    def _validate_outliers(self, df: pd.DataFrame, col: str) -> List[FlaggedValue]:
        """Validates numeric values by detecting outliers using vectorized operations"""
        flagged = []
        
        if col not in df.columns:
            log_and_print(f"{get_status_emoji('warning')} Column '{col}' not found in dataframe")
            return flagged
            
        try:
            log_and_print(f"{get_status_emoji('processing')} Starting outlier detection in '{col}'...")
            
            col_data = get_clean_numeric_series(df, col)
            
            # Early returns for invalid cases using vectorized operations
            if col_data.empty:
                log_and_print(f"{get_status_emoji('empty')} No valid numeric data in '{col}'")
                return flagged
                
            if (col_data.nunique() <= 1 or 
                col_data.std() < 0.01 or
                (set(col_data.unique()).issubset({0, 1}) and col_data.sum() <= 5) or
                (col_data.max() <= 10 and col_data.nunique() <= 10)):
                log_and_print(f"{get_status_emoji('skipped')} Skipping outlier detection for '{col}' - insufficient variation")
                return flagged

            df_clean = df.loc[col_data.index]
            log_and_print(f"{get_status_emoji('cleaning')} Removed {len(df) - len(df_clean)} missing-like values from '{col}' before {self.method.value} outlier check")

            log_and_print(f"{get_status_emoji('analyzing')} Analyzing distribution in '{col}'...")
            thresholds = self._calculate_thresholds(col_data)
            
            # Use vectorized operations to find outliers
            outlier_mask = pd.Series(False, index=col_data.index)
            for label, (low, high) in thresholds.items():
                current_mask = (col_data < low) | (col_data > high)
                # Only flag values not already flagged by a stricter threshold
                new_outliers = current_mask & ~outlier_mask
                if new_outliers.any():
                    outlier_idx = new_outliers[new_outliers].index
                    for idx in outlier_idx:
                        flagged.append(
                            FlaggedValue.from_df_row(
                                df_clean, idx, col, 
                                df_clean.loc[idx, col],
                                f"{get_status_emoji('found_issues')} {self.method.value} Outlier ({label})"
                            )
                        )
                outlier_mask |= current_mask

            if flagged:
                log_and_print(f"{get_status_emoji('found_issues')} Found {len(flagged)} outliers in '{col}' using {self.method.value}")
            else:
                log_and_print(f"{get_status_emoji('success')} No outliers detected in '{col}'")

        except Exception as e:
            raise NumericValidationError(f"Error detecting outliers: {str(e)}")

        return flagged
        
    def _calculate_thresholds(self, series: pd.Series) -> Dict[str, Tuple[float, float]]:
        """Calculate outlier thresholds based on method using vectorized operations"""
        if self.method == OutlierMethod.STD:
            mean, std = series.mean(), series.std()
            return {
                "3.0*STD": (mean - 3.0 * std, mean + 3.0 * std),
                "2.0*STD": (mean - 2.0 * std, mean + 2.0 * std),
            }
        else:  # Default to IQR
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            return {
                "3.0*IQR": (q1 - 3.0 * iqr, q3 + 3.0 * iqr),
                "2.0*IQR": (q1 - 2.0 * iqr, q3 + 2.0 * iqr),
                "1.5*IQR": (q1 - 1.5 * iqr, q3 + 1.5 * iqr),
            }

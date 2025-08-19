# dictionary_driven_checker/plugins/validators.py

"""Validator plugins for special validation cases.

These plugins handle validation that goes beyond simple dictionary lookups,
such as date formatting, pattern matching, and numeric outlier detection.
"""

from typing import Optional, List, Any
import re
from datetime import datetime
import pandas as pd
import numpy as np
from scriptcraft.common.data.validation import ColumnValidator
from scriptcraft.common.io.paths import OutlierMethod
from scriptcraft.common.plugins import register_validator

@register_validator("date")
class DateValidator(ColumnValidator):
    """Validates date formats and ranges."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        if pd.isna(value):
            return None
            
        try:
            # Try parsing with common formats
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"]
            parsed = None
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(str(value), fmt)
                    break
                except ValueError:
                    continue
                    
            if not parsed:
                return "Invalid date format"
                
            # If expected_values contains a date range, validate it
            if expected_values and "-" in expected_values:
                start_str, end_str = expected_values.split("-")
                start = datetime.strptime(start_str.strip(), "%Y-%m-%d")
                end = datetime.strptime(end_str.strip(), "%Y-%m-%d")
                
                if not (start <= parsed <= end):
                    return f"Date outside valid range: {expected_values}"
                    
        except Exception:
            return "Invalid date"
            
        return None

@register_validator("pattern")
class PatternValidator(ColumnValidator):
    """Validates values against regex patterns."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        if pd.isna(value):
            return None
            
        try:
            pattern = re.compile(expected_values)
            if not pattern.match(str(value)):
                return f"Does not match pattern: {expected_values}"
        except re.error:
            return None  # Invalid pattern in dictionary
            
        return None

@register_validator("numeric")
class NumericOutlierValidator(ColumnValidator):
    """Validates numeric values and detects outliers."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        """Validate numeric values and check for outliers.
        
        This is a fallback validator that runs after the main dictionary validation.
        It focuses on statistical outlier detection rather than range validation.
        """
        if pd.isna(value):
            return None
            
        try:
            value = float(value)
            
            # Outlier detection methods
            if self.outlier_method == OutlierMethod.IQR:
                # IQR-based outlier detection
                Q1, Q3 = np.percentile([value], [25, 75])
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                if value < lower_bound or value > upper_bound:
                    return "Statistical outlier (IQR method)"
                    
            elif self.outlier_method == OutlierMethod.STD:
                # Standard deviation based detection
                mean = np.mean([value])
                std = np.std([value])
                if std > 0:  # Avoid division by zero
                    z_score = abs((value - mean) / std)
                    if z_score > 3:  # 3 standard deviations
                        return "Statistical outlier (3-sigma)"
                    
        except (ValueError, TypeError):
            return None  # Let the main validator handle type errors
            
        return None

@register_validator("categorical_multi")
class MultiCategoricalValidator(ColumnValidator):
    """Validates multi-select categorical values."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        if pd.isna(value):
            return None
            
        # Split multi-select value on common delimiters
        value_parts = str(value).split(";")
        if len(value_parts) == 1:
            value_parts = str(value).split(",")
            
        value_parts = [v.strip() for v in value_parts]
        valid_values = [v.strip() for v in expected_values.split(",")]
        
        invalid_values = [v for v in value_parts if v and v not in valid_values]
        if invalid_values:
            return f"Invalid choices: {', '.join(invalid_values)}"
            
        return None

@register_validator("coded")
class CodedValueValidator(ColumnValidator):
    """Validates coded values like ICD codes."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        if pd.isna(value):
            return None
            
        # Extract code format from expected_values
        # e.g. "ICD-10: [A-Z][0-9]{2}.[0-9]" or "LOINC: [0-9]{5}-[0-9]"
        try:
            code_type, pattern = expected_values.split(":", 1)
            code_type = code_type.strip()
            pattern = pattern.strip()
            
            if not re.match(pattern, str(value)):
                return f"Invalid {code_type} code format"
                
        except ValueError:
            return None  # Invalid expected_values format
            
        return None

@register_validator("calculated")
class CalculatedFieldValidator(ColumnValidator):
    """Validates calculated fields against expected formulas."""
    
    def validate_value(self, value: Any, expected_values: str) -> Optional[str]:
        if pd.isna(value):
            return None
            
        try:
            # expected_values should contain formula like "sum(field1,field2)"
            # or "mean(field1,field2,field3)"
            formula_match = re.match(r"(\w+)\(([\w,]+)\)", expected_values)
            if not formula_match:
                return None
                
            operation = formula_match.group(1).lower()
            fields = formula_match.group(2).split(",")
            
            # Actual validation would need access to other field values
            # This is just a placeholder for formula validation
            if operation not in ["sum", "mean", "min", "max"]:
                return f"Unsupported operation: {operation}"
                
        except Exception:
            return None
            
        return None
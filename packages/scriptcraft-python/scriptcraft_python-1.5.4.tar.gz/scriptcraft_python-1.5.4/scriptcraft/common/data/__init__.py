"""
Data package for the project.

This package provides data processing and validation utilities organized into:
- cleaning: Data cleaning and preprocessing
- comparison: Data comparison utilities  
- validation: Data validation functions
- dataframe: DataFrame manipulation utilities
- processing: Data processing patterns and utilities
- processor: Universal data processor for common operations

Usage:
    # Import everything (recommended for internal use)
    from scriptcraft.common.data import *
    
    # Import specific items (recommended for external use)
    from scriptcraft.common.data import compare_dataframes, FlaggedValue
"""

# === EXPLICIT IMPORTS TO AVOID CONFLICTS ===
from .cleaning import *
from .comparison import (
    compare_dataframes, DataFrameComparer as ComparisonDataFrameComparer,
    ComparisonResult as ComparisonComparisonResult
)
from .comparison_core import (
    DataFrameComparer as CoreDataFrameComparer,
    ComparisonResult as CoreComparisonResult
)
from .dataframe import *
from .validation import *
from .processing import *
from .processor import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Data cleaning
#     'clean_dataframe', 'standardize_columns', 'remove_duplicates',
#     # Data comparison
#     'compare_dataframes', 'FlaggedValue', 'ComparisonResult',
#     # Data validation
#     'validate_data', 'validate_column', 'ValidationResult',
#     # DataFrame utilities
#     'safe_merge', 'safe_concat', 'DataFrameProcessor',
#     # Data processing
#     'process_data', 'DataProcessor', 'ProcessingResult'
# ] 
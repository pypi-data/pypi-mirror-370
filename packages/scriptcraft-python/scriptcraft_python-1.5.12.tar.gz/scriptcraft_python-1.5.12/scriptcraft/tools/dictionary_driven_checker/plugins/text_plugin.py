# dictionary_driven_checker/plugins/text_plugin.py

from typing import List, Optional
import pandas as pd
from scriptcraft.common.logging import log_and_print
from scriptcraft.common.data.cleaning import MISSING_VALUE_STRINGS
from scriptcraft.common.data.validation import FlaggedValue, ColumnValidator
from . import registry
from scriptcraft.common import cu

# Load configuration
config = cu.load_config()
text_config = config.checkers.dictionary_checker.text_validation

class TextValidationError(Exception):
    """Custom exception for text validation errors"""
    pass

@registry.register("text")
class TextValidator(ColumnValidator):
    """Plugin for text validation"""
    
    def __init__(self, rare_threshold: Optional[int] = None):
        self.rare_threshold = rare_threshold or text_config.get('rare_threshold', 3)
        
    def validate(self, df: pd.DataFrame, col: str, _: None) -> List[FlaggedValue]:
        """Validates text columns by identifying rare values using vectorized operations"""
        flagged = []
        
        try:
            if col not in df.columns:
                return flagged

            # Convert series to string and handle missing values in a vectorized way
            series = df[col].astype(str)
            mask = ~series.isin(MISSING_VALUE_STRINGS)
            series = series[mask]
            
            if series.empty:
                return flagged

            # Calculate value counts once and use for all operations
            value_counts = series.value_counts(dropna=False)
            rare_values = value_counts[value_counts < self.rare_threshold].index
            
            # Use vectorized operation to find rare values
            rare_mask = series.isin(rare_values)
            rare_indices = series[rare_mask].index
            
            for idx in rare_indices:
                flagged.append(
                    FlaggedValue.from_df_row(
                        df, idx, col,
                        df.loc[idx, col],
                        f"Rare Value (seen < {self.rare_threshold} times)"
                    )
                )

            if flagged:
                log_and_print(f"🔍 Found {len(flagged)} rare values in '{col}' (threshold: {self.rare_threshold})")
                
        except Exception as e:
            log_and_print(f"❌ Error validating text column '{col}': {str(e)}")
            
        return flagged



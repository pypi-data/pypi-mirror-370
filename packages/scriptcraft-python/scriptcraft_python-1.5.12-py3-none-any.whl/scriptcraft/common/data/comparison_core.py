"""
Core comparison functionality for datasets.
"""

import pandas as pd
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ComparisonResult:
    """Result of a dataset comparison."""
    added_rows: pd.DataFrame
    removed_rows: pd.DataFrame
    modified_rows: pd.DataFrame
    unchanged_rows: pd.DataFrame
    column_changes: Dict[str, Dict[str, int]]
    summary: Dict[str, int]

class DataFrameComparer:
    """Core class for comparing DataFrames."""
    
    def __init__(
        self,
        old_df: pd.DataFrame,
        new_df: pd.DataFrame,
        key_columns: List[str],
        compare_columns: Optional[List[str]] = None
    ) -> None:
        """Initialize the comparer.
        
        Args:
            old_df: Old version of the DataFrame
            new_df: New version of the DataFrame
            key_columns: Columns that uniquely identify rows
            compare_columns: Columns to compare (defaults to all non-key columns)
        """
        self.old_df = old_df.copy()
        self.new_df = new_df.copy()
        self.key_columns = key_columns
        
        if compare_columns is None:
            self.compare_columns = [
                col for col in self.old_df.columns
                if col not in key_columns
            ]
        else:
            self.compare_columns = compare_columns
    
    def compare(self) -> ComparisonResult:
        """Perform the comparison.
        
        Returns:
            ComparisonResult containing all changes
        """
        # Find added and removed rows
        old_keys = set(map(tuple, self.old_df[self.key_columns].values))
        new_keys = set(map(tuple, self.new_df[self.key_columns].values))
        
        added_keys = new_keys - old_keys
        removed_keys = old_keys - new_keys
        common_keys = old_keys & new_keys
        
        # Get the actual rows
        added_rows = self.new_df[
            self.new_df[self.key_columns].apply(tuple, axis=1).isin(added_keys)
        ]
        removed_rows = self.old_df[
            self.old_df[self.key_columns].apply(tuple, axis=1).isin(removed_keys)
        ]
        
        # Compare modified rows
        modified_rows = []
        unchanged_rows = []
        column_changes = {col: {'added': 0, 'removed': 0, 'modified': 0}
                         for col in self.compare_columns}
        
        for key in common_keys:
            old_row = self.old_df[
                self.old_df[self.key_columns].apply(tuple, axis=1) == key
            ].iloc[0]
            new_row = self.new_df[
                self.new_df[self.key_columns].apply(tuple, axis=1) == key
            ].iloc[0]
            
            changes = False
            for col in self.compare_columns:
                if old_row[col] != new_row[col]:
                    changes = True
                    column_changes[col]['modified'] += 1
            
            if changes:
                modified_rows.append(new_row)
            else:
                unchanged_rows.append(new_row)
        
        modified_df = pd.DataFrame(modified_rows) if modified_rows else pd.DataFrame(columns=self.new_df.columns)
        unchanged_df = pd.DataFrame(unchanged_rows) if unchanged_rows else pd.DataFrame(columns=self.new_df.columns)
        
        # Create summary
        summary = {
            'added': len(added_rows),
            'removed': len(removed_rows),
            'modified': len(modified_df),
            'unchanged': len(unchanged_df)
        }
        
        return ComparisonResult(
            added_rows=added_rows,
            removed_rows=removed_rows,
            modified_rows=modified_df,
            unchanged_rows=unchanged_df,
            column_changes=column_changes,
            summary=summary
        ) 
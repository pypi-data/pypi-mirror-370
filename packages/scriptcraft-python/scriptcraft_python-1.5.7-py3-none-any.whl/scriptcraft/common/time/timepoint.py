"""
scripts/common/timepoint_utils.py

📈 Utilities for processing and comparing features across timepoints,
such as visit sequences or longitudinal identifiers.
"""

from pathlib import Path
from typing import Union, List
import pandas as pd
from ..logging import log_and_print
from ..io import get_project_root

# ==== 🔢 Sequence Cleaning Utilities ====

def clean_sequence_ids(df: pd.DataFrame, sequence_col: str = "Visit_ID") -> pd.DataFrame:
    """
    Clean a sequence/index column by coercing to numeric, removing NAs, and casting to int.
    Useful for visit IDs, version numbers, etc.

    Args:
        df: Input DataFrame.
        sequence_col: Column name to clean (default is "Visit_ID").

    Returns:
        DataFrame with cleaned and integer-converted sequence column.
    """
    df[sequence_col] = pd.to_numeric(df[sequence_col], errors="coerce")
    df = df.dropna(subset=[sequence_col])
    df[sequence_col] = df[sequence_col].astype(int)
    return df

# ==== 📊 Timepoint Comparison Utilities ====

def compare_entity_changes_over_sequence(
    df: pd.DataFrame,
    entity_id_col: str,
    sequence_col: str,
    feature_col: str,
    output_name: str,
    output_dir: Union[str, Path] = "output",
    missing_placeholder: Union[int, float, str] = 99
) -> None:
    """
    Compare a feature across consecutive sequence points for each entity and 
    output a CSV summarizing the number of changes.

    Args:
        df: DataFrame containing entity, sequence, and feature columns.
        entity_id_col: Column name for entity IDs (e.g., "Med_ID").
        sequence_col: Column name for sequence (e.g., "Visit_ID", "Day", "Version").
        feature_col: Feature to track changes in across the sequence.
        output_name: Filename stem for output CSV (e.g., "feature_diff").
        output_dir: Directory to save output file (relative to project root).
        missing_placeholder: Value to substitute for missing entries (default is 99).
    """
    # Sort and pivot data for comparison
    df_sorted = df.sort_values(by=[entity_id_col, sequence_col])
    df_pivot = df_sorted.pivot(index=entity_id_col, columns=sequence_col, values=feature_col)

    sequence_values: List[Union[int, float, str]] = sorted(df[sequence_col].dropna().unique())
    df_pivot = df_pivot.fillna(missing_placeholder)

    # Count changes between consecutive timepoints
    change_counts = pd.Series(0, index=df_pivot.index)
    for i in range(1, len(sequence_values)):
        prev_seq = sequence_values[i - 1]
        curr_seq = sequence_values[i]

        if prev_seq in df_pivot.columns and curr_seq in df_pivot.columns:
            diff = (
                (df_pivot[prev_seq] != df_pivot[curr_seq]) &
                (df_pivot[prev_seq] != missing_placeholder) &
                (df_pivot[curr_seq] != missing_placeholder)
            )
            change_counts += diff.astype(int)

    # Append change counts and filter for entities with at least one change
    df_pivot["# of Changes"] = change_counts
    df_pivot = df_pivot[df_pivot["# of Changes"] > 0].copy()

    # Save results to output
    output_path = get_project_root() / output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"{output_name}.csv"
    df_pivot.to_csv(output_file, index=True)

    log_and_print(f"📈 {output_name}: {df_pivot.shape[0]} entities with changes. Saved to {output_file}.")

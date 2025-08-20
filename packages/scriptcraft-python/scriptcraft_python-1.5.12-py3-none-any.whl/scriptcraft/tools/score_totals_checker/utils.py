# zscore_totals_checker/utils.py

import pandas as pd
from scipy.stats import zscore
from scriptcraft.common.logging import log_and_print

def calculate_totals_and_compare(df: pd.DataFrame, domain: str) -> pd.DataFrame:
    """
    Calculate totals and compare with existing total columns.
    
    Args:
        df: DataFrame to analyze
        domain: Domain name for context
        
    Returns:
        DataFrame with calculated totals and comparisons
    """
    # Identify numeric columns (excluding known total columns)
    numeric_cols = df.select_dtypes(include='number').columns
    total_like_cols = [col for col in numeric_cols if "total" in col.lower() or "sum" in col.lower()]
    
    if not total_like_cols:
        log_and_print(f"⚠️ No existing total/sum columns found in {domain}.")
        return df

    component_cols = [col for col in numeric_cols if col not in total_like_cols]
    log_and_print(f"🔍 Found total-like column(s): {total_like_cols}")
    log_and_print(f"📊 Using components: {component_cols}")

    df["Calculated_Total"] = df[component_cols].sum(axis=1)
    df["Zscore_Calculated"] = zscore(df["Calculated_Total"].fillna(0))

    for col in total_like_cols:
        df[f"Zscore_{col}"] = zscore(df[col].fillna(0))
        df[f"Diff_vs_{col}"] = df["Calculated_Total"] - df[col]

    return df

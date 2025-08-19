# feature_change_tracker/utils.py

from pathlib import Path
from typing import Union, List, Dict, Any
import pandas as pd
from scriptcraft.common import (
    clean_sequence_ids, compare_entity_changes_over_sequence,
    log_and_print, ensure_output_dir
)


def run_between_visit_changes(df: pd.DataFrame, feature: str, output_dir: Union[str, Path]) -> None:
    """Run between visit changes analysis."""
    df = df[["Med_ID", "Visit_ID", feature]]
    df = clean_sequence_ids(df)
    compare_entity_changes_over_sequence(df, dataset_name="BetweenVisitChanges", chosen_feature=feature, output_folder=output_dir)


def run_categorized_changes(df: pd.DataFrame, feature: str, output_dir: Union[str, Path]) -> None:
    """Run categorized changes analysis."""
    visit_ids = sorted([int(col) for col in df.columns if col.isdigit()])
    category_data: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        med_id = row["Med_ID"]
        for visit in visit_ids[:-1]:
            prev = row.get(str(visit), None)
            curr = row.get(str(visit + 1), None)
            if pd.notna(prev) and pd.notna(curr) and prev != 99 and curr != 99 and prev != curr:
                if prev == 0 and curr == 1 or prev == 1 and curr == 2:
                    category = "normal progression"
                elif prev == 0 and curr == 2:
                    category = "fast progression"
                elif prev == 9 and curr in [0, 1, 2]:
                    category = "no longer undefined"
                elif prev in [0, 1, 2] and curr == 9:
                    category = "now undefined"
                elif (prev in [1, 2] and curr == 0) or (prev == 2 and curr == 1):
                    category = "flagged"
                else:
                    category = "other change"
                category_data.append({
                    "Med_ID": med_id, "Visit_From": visit, "Visit_To": visit + 1,
                    "Prev_Value": prev, "Curr_Value": curr, "Category": category
                })

    df_out = pd.DataFrame(category_data)
    safe_feature = feature.replace(" ", "_").replace("/", "-")  # etc.
    output_path = Path(output_dir) / f"{safe_feature}_Category_Changes.csv"
    ensure_output_dir(output_path)

    if df_out.empty:
        log_and_print("⚠️ No visit-to-visit changes met the criteria.")
    else:
        log_and_print(f"\n🔢 Change Type Counts:\n{df_out['Category'].value_counts()}")

    df_out.to_csv(output_path, index=False)
    log_and_print(f"✅ Categorized changes saved to: {output_path.resolve()} ({len(df_out)} rows)")




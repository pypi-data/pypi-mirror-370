"""
scripts/common/expected_values.py

📖 Utilities for parsing expected value formats from data dictionaries, 
including handling numeric ranges, text values, categorical sets, and loading 
min/max supplements from external files.
"""

from enum import Enum
from pathlib import Path
from typing import Union, Set, Tuple, List, Dict, Any
import re
import pandas as pd
from ..logging import log_and_print

# ==== 📚 Configuration & Constants ====

class ValueType(Enum):
    """Enum representing different parsed value types."""
    NUMERIC = "numeric"
    TEXT = "text"
    DATE = "date"
    RANGE_SET = "range_set"
    SET = "set"
    MIXED_SET = "mixed_set"
    UNKNOWN = "unknown"

NOTES_COLUMN_NAMES: List[str] = ["notes(numeric, integer only, text-don't want \"\", etc)", 'notes']
DATE_KEYWORDS: List[str] = ['date', 'mm/yyyy', 'month/year']
RANGE_KEYWORDS: List[str] = ['range']
VALUE_PATTERNS: Dict[str, str] = {
    'range': r'^\d+(\.\d+)?\s*-\s*\d+(\.\d+)?$',
    'set_entry': r'\{(.*?)\}'
}

# ==== 📏 Value Parsing Utilities ====

def extract_expected_values(
    value_string: str, 
    strict: bool = False
) -> Tuple[str, Union[Set[str], List[Tuple[float, float]], Tuple[Set[str], List[Tuple[float, float]]]]]:
    """
    Parse value column strings into expected types, numeric ranges, or sets.

    Args:
        value_string: The raw value string to parse.
        strict: If True, raise exceptions instead of returning UNKNOWN.

    Returns:
        Tuple containing (value_type, parsed_values).
    """
    if pd.isna(value_string) or not str(value_string).strip():
        log_and_print("⚠️ Empty or null value string")
        return ValueType.UNKNOWN.value, set()

    text = str(value_string).strip()
    lowered = text.lower()

    # Handle general types
    if lowered == ValueType.NUMERIC.value:
        return ValueType.NUMERIC.value, set()
    if lowered == ValueType.TEXT.value:
        return ValueType.TEXT.value, set()
    if lowered == "mm/yyyy":
        return ValueType.DATE.value, set()

    try:
        matches = re.findall(VALUE_PATTERNS['set_entry'], text)
        if not matches:
            if strict:
                raise ValueError(f"No valid set entries found in: {text}")
            return ValueType.UNKNOWN.value, set()

        parsed: Set[str] = set()
        ranges: List[Tuple[float, float]] = []

        for entry in matches:
            parts = [p.strip() for p in entry.split(",")]
            key_part = parts[0]
            label = parts[1].lower() if len(parts) > 1 else ""

            if any(kw in label for kw in RANGE_KEYWORDS) or re.match(VALUE_PATTERNS['range'], key_part):
                try:
                    low, high = map(float, key_part.replace(" ", "").split("-"))
                    ranges.append((low, high))
                    log_and_print(f"📊 Parsed range: {low}-{high}")
                except Exception as e:
                    log_and_print(f"⚠️ Failed to parse range '{key_part}': {e}")
                    if strict:
                        raise
                    parsed.add(key_part)
            else:
                try:
                    key_numeric = float(key_part)
                    parsed.add(str(int(key_numeric)) if key_numeric.is_integer() else str(key_numeric))
                except ValueError:
                    parsed.add(key_part)

        if ranges and not parsed:
            return ValueType.RANGE_SET.value, ranges
        if parsed and not ranges:
            return ValueType.SET.value, parsed
        return ValueType.MIXED_SET.value, (parsed, ranges)

    except Exception as e:
        log_and_print(f"❌ Error parsing value string '{text}': {e}")
        if strict:
            raise
        return ValueType.UNKNOWN.value, set()

# ==== 📄 Min/Max Supplement Loading ====

def load_minmax_updated(file_paths: List[str]) -> pd.DataFrame:
    """
    Load and merge one or more minmaxUpdated files into a 'fake dictionary' DataFrame.

    Args:
        file_paths: List of file paths to process.

    Returns:
        DataFrame with columns: Main Variable, Value, Source.
    """
    all_dict_rows: List[Dict[str, str]] = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            log_and_print(f"❌ File not found: {file_path}")
            continue

        try:
            df = pd.read_excel(file_path)
            log_and_print(f"📖 Successfully loaded {file_path}")
        except Exception as e:
            log_and_print(f"❌ Failed to load {file_path}: {e}")
            continue

        for idx, row in df.iterrows():
            try:
                variable = str(row.get('variable', '')).strip()
                if not variable or variable.lower() == 'nan':
                    log_and_print(f"⚠️ Skipping row {idx}: Empty or invalid variable name")
                    continue

                min_val = row.get('min', '')
                max_val = row.get('max', '')

                notes = next(
                    (str(row.get(col, "")).lower() for col in NOTES_COLUMN_NAMES if pd.notna(row.get(col))), 
                    ""
                )

                if (pd.isna(min_val) or pd.isna(max_val) or 
                    str(min_val).upper() == "N/A" or str(max_val).upper() == "N/A"):
                    if any(kw in notes for kw in DATE_KEYWORDS):
                        value_spec = "Mm/Yyyy"
                        log_and_print(f"📅 Set {variable} as date type")
                    else:
                        value_spec = "Text"
                        log_and_print(f"📝 Set {variable} as text type")
                else:
                    try:
                        min_val_clean = str(min_val).strip()
                        max_val_clean = str(max_val).strip()

                        min_val = float(min_val_clean)
                        max_val = float(max_val_clean)

                        min_val = int(min_val) if min_val.is_integer() else min_val
                        max_val = int(max_val) if max_val.is_integer() else max_val

                        value_spec = f"{{{min_val}-{max_val}}}"
                        log_and_print(f"📊 Set {variable} range to {min_val}-{max_val}")
                    except Exception as e:
                        log_and_print(f"⚠️ Could not convert {variable} min={min_val} max={max_val}: {e}")
                        value_spec = "Numeric"

                all_dict_rows.append({
                    "Main Variable": variable,
                    "Value": value_spec,
                    "Source": "supplement"
                })

            except Exception as e:
                log_and_print(f"❌ Error processing row {idx}: {e}")
                continue

    result_df = pd.DataFrame(all_dict_rows)
    log_and_print(f"✅ Processed {len(result_df)} valid rows from {len(file_paths)} files")
    return result_df

# dictionary_cleaner/utils.py

from pathlib import Path
import re
from typing import Union, Any, Dict, List
import pandas as pd
from scriptcraft.common import (
    log_and_print, load_data,
    parse_missing_unit, prevent_pipe_inside_braces,
    fix_numeric_dash_inside_braces, fix_word_number_dash_inside_braces,
    get_project_root, get_domain_paths,
    log_fix_summary,
)


# Define paths
PROJECT_ROOT = get_project_root()
DOMAIN_PATHS = get_domain_paths(PROJECT_ROOT)


# Global dictionary to store fix counts for summary
fix_counts: Dict[str, int] = {
    "Switched numerical representations of categorical variables to integers": 0,
    "Normalized = or : to comma": 0,
    "Ensure space after comma in '{}' pairs": 0,
    "Inserted missing comma between key and label": 0,
    "Curly brace spacing fixed": 0,
    "Multiple spaces replaced with ' | '": 0,
    "Leading zero added inside '{}'": 0,
    "Missing space between number and word fixed": 0,
    # "' | ' added only at necessary separations": 0,
    "Removed spaces before and after '/' for consistency": 0,
    "Replaced incorrect ']' inside '{}'": 0,
    "Ensured `[` remains for labels": 0,
    "Replaced incorrect '(' with '{'": 0,
    "Removed extra spaces after '{'": 0,
    "Fixed incorrect `}` in numeric ranges": 0,
    "Removed space before a comma": 0,
    "Remove commas between `{}` pairs": 0,
    "Ensured exactly one space between '{}' pairs": 0,
    "Removed unnecessary trailing spaces": 0,
    "Add space before and after '='": 0,
    "Removed trailing spaces inside '{}'": 0,
    "Removed spaces around '-' between numbers inside '{}'": 0,
    "Added spaces around '-' between words and numbers inside '{}'": 0,
    "Removed random trailing ' - '": 0,
    "Fixed incorrect 'Don't' capitalization": 0,
    "Added space before '{' following '-'": 0,
    "Collapsed multiple spaces to single space": 0,

}


def convert_numeric_keys_to_ints(text: str) -> str:
    """Converts numeric keys like 1.0 or 2.00 to integers inside {key, value} pairs, but skips ranges like {0-1}."""
    count = 0
    malformed: List[str] = []

    def replace(match: re.Match) -> str:
        nonlocal count, malformed
        content = match.group(1).strip()

        # ✅ Skip numeric ranges like {0-1}, {1.0 - 5.0}, etc.
        if re.match(r'^\d+(\.\d+)?\s*-\s*\d+(\.\d+)?$', content):
            return f"{{{content}}}"

        if "," not in content:
            malformed.append(content)
            return f"{{{content}}}"

        key, label = content.split(",", 1)
        key = key.strip()
        label = label.strip()

        try:
            key_val = float(key)
            new_key = str(int(key_val)) if key_val.is_integer() else str(key_val)
            if new_key != key:
                count += 1
                key = new_key
        except ValueError:
            pass

        return f"{{{key}, {label}}}"

    new_text = re.sub(r'\{([^{}]+?)\}', replace, text)

    if count > 0:
        fix_counts["Switched numerical representations of categorical variables to integers"] += count

    if malformed:
        log_and_print(f"⚠️ Malformed pairs in: {text}")
        for item in malformed:
            log_and_print(f"   - {{{item}}}")

    return new_text


def parse_values(value: Union[str, float, None], filename: str) -> Union[str, float, None]:
    global fix_counts

    if pd.isna(value) or value in ["Numeric", "Text", "Mm/YYYY"]:
        return value

    original_value = value

    # {value}{value} → {value} {value}
    fixed_braces = re.sub(r'\}\s*\{', '} {', value)
    if original_value != fixed_braces:
        fix_counts["Curly brace spacing fixed"] += 1

    # Only apply " | " rule to Biomarkers
    if "biomarkers" in filename.lower():
        fixed_spaces = re.sub(r'(?<!\{)\s{2,}(?!\})', ' | ', fixed_braces)
        if fixed_braces != fixed_spaces:
            fix_counts["Multiple spaces replaced with ' | '"] += 1
        fixed_pipe_separation = prevent_pipe_inside_braces(fixed_spaces)
    else:
        fixed_pipe_separation = fixed_braces

    # ✅ Use this consistently as base for all further replacements
    fixed = fixed_pipe_separation
    # Handle bilingual/language blocks separately before running general rules
    fixed = fix_language_blocks(fixed)

    # Split overstuffed {0:No, 1:Yes} → {0:No} {1:Yes}
    fixed = re.sub(r'\{([^{}]*?),\s*(\d+\s*[:=])', r'{\1} {\2', fixed)
    fixed = re.sub(r'(?<!\{)(\d+(?:\.\d+)?)[\s]*[:=][\s]*([^\{\}]+)(?!\})', r'{\1, \2}', fixed)

    steps = [
        (r'\{([^{}]*?)(?:\s*[=:]\s*)([^{}]*?)\}', r'{\1, \2}', "Normalized = or : to comma"),
        (r'(\{[^,]+),\s*([^\}]+)', r'\1, \2', "Ensure space after comma in '{}' pairs"),
        (r'\{(\d+(?:\.\d+)?)\s+([^\{\}]+?)\}', r'{\1, \2}', "Inserted missing comma between key and label"),

        (r'\{(\.)', r'{0.', "Leading zero added inside '{}'"),
        (r'(\d)([A-Za-z])', r'\1 \2', "Missing space between number and word fixed"),
        (r'\s*/\s*', '/', "Removed spaces before and after '/' for consistency"),
        (r'(\{[^}]+)\]', r'\1}', "Replaced incorrect ']' inside '{}'"),
        (r'(?<=\w)\[', '[', "Ensured `[` remains for labels"),
        (r'\((\d+\.\d+, [^\}]+?)\}', r'{\1}', "Replaced incorrect '(' with '{'"),
        (r'\{\s+', '{', "Removed extra spaces after '{'"),
        (r'(\[\d+-\d+)}', r'\1]', "Fixed incorrect `}` in numeric ranges"),
        (r'(\d)\s+,', r'\1,', "Removed space before a comma"),
        (r'\}\s*,\s*\{', '} {', "Remove commas between `{}` pairs"),
        (r'\} {', '} {', "Ensured exactly one space between '{}' pairs"),
        (r'\s*=\s*', ' = ', "Add space before and after '='"),
        (r'\{\s*([^}]*\S)\s*\}', r'{\1}', "Removed trailing spaces inside '{}'"),
        (r'\s+-\s*$', '', "Removed random trailing ' - '"),
        (r"[''`´ʹ]", "'", None),  # Normalize apostrophes
        (r"\b[Dd]on[''`]?[Tt]+\b", "Don't", "Fixed incorrect 'Don't' capitalization"),
        (r'-(\{)', r' - \1', "Added space before '{' following '-'"),
        # Collapse multiple spaces outside of curly braces
        (r' {2,}', ' ', "Collapsed multiple spaces to single space"),
    ]

    for pattern, repl, desc in steps:
        updated = re.sub(pattern, repl, fixed)
        if updated != fixed and desc:
            fix_counts[desc] += 1
        fixed = updated

    # Apply dash fixes
    dash_fixed = fix_numeric_dash_inside_braces(fixed)
    if fixed != dash_fixed:
        fix_counts["Removed spaces around '-' between numbers inside '{}'"] += 1

    word_dash_fixed = fix_word_number_dash_inside_braces(dash_fixed)

    # Check for unclosed brace
    if fixed.count('{') > fixed.count('}'):
        log_and_print(f"⚠️ Detected unclosed brace in: {fixed}")

    # Convert float-like numeric keys to ints in {key, value} format
    try:
        converted = convert_numeric_keys_to_ints(word_dash_fixed)
    except Exception as e:
        log_and_print(f"❌ Failed to convert numeric keys for value: {word_dash_fixed} → {e}")
        converted = word_dash_fixed  # fallback

    if converted != word_dash_fixed:
        fix_counts["Switched numerical representations of categorical variables to integers"] = \
            fix_counts.get("Switched numerical representations of categorical variables to integers", 0) + 1

    return converted


def fix_language_blocks(text: str) -> str:
    """Fix bilingual value blocks like [Spanish = {...} {...}] [English = {...} {...}]"""
    def fix_block(match: re.Match) -> str:
        full = match.group(0)
        content = match.group(1)
        fixed_content = re.sub(r'\{(\d+(?:\.\d+)?)\s*[:=]?\s*([^\{\}]+?)\}', r'{\1, \2}', content)
        fixed_content = convert_numeric_keys_to_ints(fixed_content)
        return f"[{fixed_content}]"

    # This safely finds blocks like [Spanish = {1:...} {2:...}]
    pattern = r'\[([^\[\]]*?=\s*(?:\{.*?\}\s*)+)\]'
    return re.sub(pattern, fix_block, text)


def clean_data(file_path: Path, output_folder: Path) -> None:
    global fix_counts
    fix_counts = {key: 0 for key in fix_counts}  # ✅ Reset early to avoid carryover

    df = load_data(file_path)
    is_imaging = "Missing" in df.columns and "Unit of Measurement" in df.columns
    filename = file_path.name

    if "Value" in df.columns:
        log_and_print("\n--- Unique Values in 'Value' Column (Before Cleaning) ---")
        log_and_print(df["Value"].dropna().unique())

        df["Value"] = df["Value"].apply(lambda x: parse_values(x, filename))

        log_and_print("\n--- Unique Values in 'Value' Column (After Cleaning) ---")
        log_and_print(df["Value"].dropna().unique())

    else:
        log_and_print("⚠️ No 'Value' column found — skipping value cleaning.")

    columns_to_check = ["Missing", "Unit of Measurement"] if is_imaging else ["Missing/Unit of Measure"]
    for col in columns_to_check:
        if col in df.columns:
            log_and_print(f"\n--- Unique Values in '{col}' Column (Before Cleaning) ---")
            log_and_print(df[col].dropna().unique())

            df[col] = df[col].apply(parse_missing_unit)

            log_and_print(f"\n--- Unique Values in '{col}' Column (After Cleaning) ---")
            log_and_print(df[col].dropna().unique())

    # Prevent duplicate _cleaned suffixes
    cleaned_filename = (
        file_path.name if file_path.stem.endswith("_cleaned")
        else f"{file_path.stem}_cleaned{file_path.suffix}"
    )

    cleaned_path = output_folder / cleaned_filename

    df.to_csv(cleaned_path, index=False) if file_path.suffix == ".csv" else df.to_excel(cleaned_path, index=False)

    log_and_print(f"\nCleaned file saved as: {cleaned_path}\n")
    log_fix_summary(fix_counts, label=f"Fix Summary for {file_path.name}")

    fix_counts = {key: 0 for key in fix_counts}
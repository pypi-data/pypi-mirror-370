# dictionary_validator/utils.py

from typing import List, Set, Dict, Any

def compare_columns(dataset_cols: List[str], dictionary_cols: List[str]) -> Dict[str, Any]:
    """Compare dataset vs dictionary column sets and return a detailed dictionary."""
    dataset_cols_set = set(dataset_cols)
    dictionary_cols_set = set(dictionary_cols)

    in_both = dataset_cols_set & dictionary_cols_set
    only_in_dataset = dataset_cols_set - dictionary_cols_set
    only_in_dictionary = dictionary_cols_set - dataset_cols_set

    # Case-insensitive mismatch detection
    lower_dataset = {col.lower(): col for col in dataset_cols_set}
    lower_dict = {col.lower(): col for col in dictionary_cols_set}
    case_mismatches = [
        lower_dataset[name] for name in (set(lower_dataset) & set(lower_dict))
        if lower_dataset[name] != lower_dict[name]
    ]

    return {
        "in_both": in_both,
        "only_in_dataset": only_in_dataset,
        "only_in_dictionary": only_in_dictionary,
        "case_mismatches": case_mismatches
    }


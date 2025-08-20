"""
scripts/common/comparison_utils.py

📏 Utilities for comparing pandas DataFrames, including column checks, 
data type mismatches, content differences, and ID integrity validation.
"""

from dataclasses import dataclass
from typing import Set, Tuple, Dict, Union, Optional, List, Any, Callable
import pandas as pd
from pathlib import Path
from functools import wraps

from ..logging import log_and_print
from ..io.paths import ID_COLUMNS, OUTPUT_DIR

# ==== 📦 Comparison Results Data Class ====

@dataclass
class ComparisonResult:
    """
    Class to hold comparison results between two data sources.
    
    Attributes:
        common: Set of common columns between the two data sources.
        only_in_first: Set of columns only in the first data source.
        only_in_second: Set of columns only in the second data source.
        differences: DataFrame containing content differences, if any.
        dtype_mismatches: Dictionary of columns with mismatched data types.
        shape_mismatch: Tuple of shapes if they differ, otherwise None.
        missing_ids: Tuple of DataFrames with missing IDs in each dataset.
        index_comparison: Tuple of sets for index comparison results.

    Example:
        >>> result = ComparisonResult(...)
        >>> print(result.common)
    """
    common: Set[str]
    only_in_first: Set[str]
    only_in_second: Set[str]
    differences: Optional[pd.DataFrame] = None
    dtype_mismatches: Optional[Dict[str, Tuple[Any, Any]]] = None
    shape_mismatch: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    missing_ids: Optional[Tuple[pd.DataFrame, pd.DataFrame]] = None
    index_comparison: Optional[Tuple[Set[Any], Set[Any], Set[Any]]] = None

    def __post_init__(self) -> None:
        if self.dtype_mismatches is None:
            self.dtype_mismatches = {}

# ==== 🚨 Error Handling Decorator ====

def handle_comparison_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to handle and log errors in comparison functions.
    
    Args:
        func: The function to be decorated.
    
    Returns:
        A wrapper function that catches exceptions and logs them.
    
    Example:
        >>> @handle_comparison_errors
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_and_print(f"❌ Error in {func.__name__}: {type(e).__name__}: {e}")
            return None
    return wrapper

# ==== 📊 DataFrame Comparer Class ====

class DataFrameComparer:
    # ==== 📏 Initialization & Alignment ====
    def __init__(
        self, 
        df1: Union[pd.DataFrame, Set[Any]], 
        df2: Union[pd.DataFrame, Set[Any]], 
        dataset_name: str = "Dataset", 
        output_dir: Union[str, Path] = OUTPUT_DIR
    ) -> None:
        self.df1 = df1
        self.df2 = df2
        self.dataset_name = dataset_name
        self.output_dir = Path(output_dir)
        self._align_dataframes()

    def _align_dataframes(self) -> None:
        """
        Align DataFrames using ID_COLUMNS if available.

        Args:
            None

        Returns:
            None

        Example:
            >>> comparer._align_dataframes()
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return
        if all(col in self.df1.columns and col in self.df2.columns for col in ID_COLUMNS):
            self.df1 = self.df1.set_index(ID_COLUMNS)
            self.df2 = self.df2.set_index(ID_COLUMNS)
            log_and_print(f"🔑 Set composite index on {ID_COLUMNS} for both datasets.")
        self.df1 = self.df1.sort_index()
        self.df2 = self.df2.sort_index()

    # ==== 📋 Column & Dtype Comparison ====
    @handle_comparison_errors
    def compare_columns(self, label_a: str = "Old", label_b: str = "New") -> ComparisonResult:
        """
        Compare columns between two DataFrames or sets.
        
        Args:
            label_a: Label for the first DataFrame.
            label_b: Label for the second DataFrame.

        Returns:
            A ComparisonResult object with common and unique columns.

        Example:
            >>> comparer.compare_columns()
        """
        cols_a = set(self.df1.columns) if isinstance(self.df1, pd.DataFrame) else set(self.df1)
        cols_b = set(self.df2.columns) if isinstance(self.df2, pd.DataFrame) else set(self.df2)

        common = cols_a & cols_b
        only_a = cols_a - cols_b
        only_b = cols_b - cols_a

        self._log_column_comparison(common, only_a, only_b, label_a, label_b)
        
        return ComparisonResult(
            common=common,
            only_in_first=only_a,
            only_in_second=only_b,
            differences=None,
            dtype_mismatches={},
            shape_mismatch=None,
            missing_ids=None,
            index_comparison=None
        )

    def _log_column_comparison(self, common: Set[str], only_a: Set[str], only_b: Set[str], 
                              label_a: str, label_b: str) -> None:
        log_and_print(f"\n🔍 Column Comparison for {self.dataset_name}")
        log_and_print(f"🔹 Total Columns in {label_a}: {len(only_a) + len(common)}")
        log_and_print(f"🔹 Total Columns in {label_b}: {len(only_b) + len(common)}")
        log_and_print(f"✅ Common Columns: {len(common)}")
        if only_a:
            log_and_print(f"❌ Columns Only in {label_a} ({len(only_a)}): {only_a}")
        if only_b:
            log_and_print(f"❌ Columns Only in {label_b} ({len(only_b)}): {only_b}")

    @handle_comparison_errors
    def compare_dtypes(self) -> Dict[str, Tuple[Any, Any]]:
        """
        Compare data types of common columns between two DataFrames.

        Returns:
            A dictionary with column names as keys and a tuple of data types as values.
            
        Example:
                >>> comparer.compare_dtypes()
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return {}
        common_cols = set(self.df1.columns) & set(self.df2.columns)
        mismatches = {
            col: (self.df1[col].dtype, self.df2[col].dtype)
            for col in common_cols if self.df1[col].dtype != self.df2[col].dtype
        }
        self._log_dtype_comparison(mismatches)
        return mismatches

    def _log_dtype_comparison(self, mismatches: Dict[str, Tuple[Any, Any]]) -> None:
        if mismatches:
            log_and_print(f"\n🔍 Dtype mismatches in {self.dataset_name}:")
            for col, (dtype_old, dtype_new) in mismatches.items():
                log_and_print(f"❌ Column: {col} - Old: {dtype_old} | New: {dtype_new}")
        else:
            log_and_print(f"\n✅ No dtype mismatches found in {self.dataset_name}.")

    # ==== 📄 Content & Shape Comparison ====
    @handle_comparison_errors
    def compare_content(self) -> Optional[pd.DataFrame]:
        """
        Compare content of common columns between two DataFrames.

        Returns:
            A DataFrame with differences, or None if no differences found.
        
        Example:
            >>> comparer.compare_content()    
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return None
        common_cols = self.df1.columns.intersection(self.df2.columns).tolist()
        differences = self.df1[common_cols].compare(self.df2[common_cols])
        self._log_and_save_differences(differences)
        return differences

    def _log_and_save_differences(self, differences: pd.DataFrame) -> None:
        """
        Log and save differences to a CSV file.

        Args:
            differences: DataFrame containing differences.    
        """
        if differences.empty:
            log_and_print("✅ No content differences found.")
            return
        log_and_print(f"❌ Found {differences.shape[0]} differing rows.")
        self.output_dir.mkdir(exist_ok=True)
        output_path = self.output_dir / f"{self.dataset_name}_content_differences.csv"
        differences.to_csv(output_path, index=True)
        log_and_print(f"📁 Differences saved to {output_path.resolve()}")

    @handle_comparison_errors
    def compare_shapes(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Compare shapes of two DataFrames.

        Returns:
            A tuple of shapes if they differ, or None if they are the same.

        Example:
            >>> comparer.compare_shapes()
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return None
        shape1, shape2 = self.df1.shape, self.df2.shape
        if shape1 == shape2:
            log_and_print("✅ Datasets have the same shape.")
            return None
        log_and_print(f"❌ Shape mismatch: {shape1} vs {shape2}")
        return shape1, shape2

    # ==== 🔑 ID & Index Comparison ====
    @handle_comparison_errors
    def compare_med_visit_ids(self) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Compare Med/Visit IDs between two DataFrames.

        Returns:
            A tuple of DataFrames with missing IDs in each dataset.

        Example:
            >>> comparer.compare_med_visit_ids()
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return None
        if not all(col in self.df1.columns and col in self.df2.columns for col in ID_COLUMNS):
            log_and_print(f"⚠️ Cannot compare Med/Visit IDs - missing columns: {ID_COLUMNS}")
            return None
        old_combos = self.df1[ID_COLUMNS].drop_duplicates()
        new_combos = self.df2[ID_COLUMNS].drop_duplicates()

        missing_in_new = old_combos.merge(new_combos, on=ID_COLUMNS, how='left', indicator=True)
        missing_in_new = missing_in_new[missing_in_new['_merge'] == 'left_only'].drop(columns=['_merge'])

        missing_in_old = new_combos.merge(old_combos, on=ID_COLUMNS, how='left', indicator=True)
        missing_in_old = missing_in_old[missing_in_old['_merge'] == 'left_only'].drop(columns=['_merge'])

        return missing_in_new, missing_in_old

    @handle_comparison_errors
    def compare_indexes(self) -> Optional[Tuple[Set[Any], Set[Any], Set[Any]]]:
        """
        Compare indexes of two DataFrames.

        Returns:
            A tuple of common indexes, indexes only in the first DataFrame, and indexes only in the second DataFrame.

        Example:
            >>> comparer.compare_indexes()
        """
        if not (isinstance(self.df1, pd.DataFrame) and isinstance(self.df2, pd.DataFrame)):
            return None
        idx_old = set(self.df1.index)
        idx_new = set(self.df2.index)

        common_idx = idx_old & idx_new
        only_old = idx_old - idx_new
        only_new = idx_new - idx_old

        log_and_print(f"\n🔍 Index Comparison for {self.dataset_name}")
        log_and_print(f"✅ Common Index Values: {len(common_idx)}")
        if only_old:
            log_and_print(f"❌ Indexes Only in Old ({len(only_old)}): Sample -> {list(only_old)[:5]}")
        if only_new:
            log_and_print(f"❌ Indexes Only in New ({len(only_new)}): Sample -> {list(only_new)[:5]}")

        return common_idx, only_old, only_new

    # ==== 🚀 Run Full Comparison ====
    def run_full_comparison(self, steps: Optional[List[str]] = None) -> ComparisonResult:
        """
        Run selected or all comparison checks.
        
        Args:
            steps: List of comparison steps to run. 
                   Options: ["columns", "dtypes", "shape", "index", "rows", "med_ids"].
                     If None, all steps are run.
        
        Returns:
            A ComparisonResult object with results from all selected checks.

        Example:
            >>> comparer.run_full_comparison(steps=["columns", "dtypes"])
        """
        steps = steps or ["columns", "dtypes", "shape", "index", "rows", "med_ids"]

        column_results = self.compare_columns() if "columns" in steps else ComparisonResult(set(), set(), set())
        dtype_mismatches = self.compare_dtypes() if "dtypes" in steps else {}
        shape_mismatch = self.compare_shapes() if "shape" in steps else None
        index_comparison = self.compare_indexes() if "index" in steps else None
        content_differences = self.compare_content() if "rows" in steps else None
        missing_ids = self.compare_med_visit_ids() if "med_ids" in steps else None

        return ComparisonResult(
            common=column_results.common,
            only_in_first=column_results.only_in_first,
            only_in_second=column_results.only_in_second,
            differences=content_differences,
            dtype_mismatches=dtype_mismatches,
            shape_mismatch=shape_mismatch,
            missing_ids=missing_ids,
            index_comparison=index_comparison
        )

# ==== 🧩 Convenience Function ====

def compare_dataframes(
    df1: Union[pd.DataFrame, Set[Any]], 
    df2: Union[pd.DataFrame, Set[Any]], 
    dataset_name: str = "Dataset", 
    output_dir: Union[str, Path] = OUTPUT_DIR, 
    steps: Optional[List[str]] = None
) -> ComparisonResult:
    """
    Convenient API function to perform full or partial comparison.
    
    Args:
        df1: First DataFrame or set of columns.
        df2: Second DataFrame or set of columns.
        dataset_name: Name of the dataset for logging.
        output_dir: Directory to save output files.
        steps: List of comparison steps to run. 
               Options: ["columns", "dtypes", "shape", "index", "rows", "med_ids"].
                 If None, all steps are run.    
    
    Returns:
        A ComparisonResult object with results from all selected checks.

    Example:
        >>> compare_dataframes(df1, df2, dataset_name="MyDataset", steps=["columns", "dtypes"])
    """
    comparer = DataFrameComparer(df1, df2, dataset_name, output_dir)
    return comparer.run_full_comparison(steps)

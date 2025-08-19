# scripts/tools/data_content_diff/plugins/standard_mode.py

from ....common import cu


def run_mode(input_paths, output_dir, domain=None, **kwargs) -> None:
    """Standard row-wise content comparison without special logic."""
    if not input_paths:
        raise ValueError("Standard mode requires two input files provided via --input.")

    cu.log_and_print(f"📌 Running Standard Comparison{' for domain: ' + domain if domain else ''}...")

    df1, df2, dataset_name = cu.load_comparison_datasets(input_paths)

    # Run the generic comparison from shared utils
    cu.compare_dataframes(df1, df2, dataset_name, output_dir)

    cu.log_and_print(f"📁 Results saved to: {output_dir.resolve()}")

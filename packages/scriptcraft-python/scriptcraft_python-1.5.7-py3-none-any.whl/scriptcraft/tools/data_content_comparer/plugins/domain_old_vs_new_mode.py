# scripts/tools/data_content_diff/plugins/domain_old_vs_new_mode.py

import pandas as pd

from ....common import cu


def run_mode(input_paths, output_dir, domain=None, **kwargs) -> None:
    """Domain-based old vs new content comparison."""
    domain_paths = cu.get_domain_paths(cu.get_project_root())

    for domain, paths in domain_paths.items():
        cu.log_and_print(f"📌 Comparing domain: {domain}")
        old_file = paths["old_data"] / "your_old_file.xlsx"
        new_file = paths["processed_data"] / "your_new_file.xlsx"
        
        try:
            df1, df2, dataset_name = cu.load_comparison_datasets([old_file, new_file])
            cu.compare_dataframes(df1, df2, dataset_name, output_dir)
        except Exception as e:
            cu.log_and_print(f"❌ Failed comparison for {domain}: {e}")

    cu.log_and_print(f"📁 All domain comparisons completed. Results saved to: {output_dir.resolve()}")

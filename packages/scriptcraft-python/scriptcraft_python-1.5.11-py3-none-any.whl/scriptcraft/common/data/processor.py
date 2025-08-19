"""
Data processor utilities for common data processing patterns.

This module consolidates common data processing patterns used across tools,
including data loading, validation, transformation, and saving operations.
"""

import pandas as pd
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Callable, Tuple
from ..logging import log_and_print
from ..io import load_data, ensure_output_dir, find_latest_file, find_matching_file, FILE_PATTERNS


class DataProcessor:
    """
    Standardized data processor for common data processing patterns.
    
    This class consolidates common patterns used across tools for:
    - Loading and validating data
    - Processing data with custom functions
    - Saving results with standard formatting
    - Error handling and logging
    """
    
    def __init__(self, name: str = "DataProcessor") -> None:
        """
        Initialize the data processor.
        
        Args:
            name: Name of the processor for logging
        """
        self.name = name
    
    def load_and_validate(
        self,
        input_paths: Union[str, Path, List[Union[str, Path]]],
        required_columns: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """
        Load and validate data from input paths.
        
        Args:
            input_paths: Single path or list of paths to load
            required_columns: Optional list of required columns
            **kwargs: Additional arguments for load_data
            
        Returns:
            Loaded DataFrame(s)
        """
        if isinstance(input_paths, (str, Path)):
            input_paths = [input_paths]
        
        dataframes = []
        for path in input_paths:
            try:
                df = load_data(path, **kwargs)
                if df is not None:
                    # Basic validation
                    if required_columns:
                        missing = set(required_columns) - set(df.columns)
                        if missing:
                            log_and_print(f"⚠️ Missing required columns in {path}: {missing}")
                    
                    dataframes.append(df)
                    log_and_print(f"✅ Loaded {Path(path).name}: {df.shape[0]} rows, {df.shape[1]} columns")
                else:
                    log_and_print(f"⚠️ Failed to load {path}")
            except Exception as e:
                log_and_print(f"❌ Error loading {path}: {e}")
        
        return dataframes[0] if len(dataframes) == 1 else dataframes
    
    def process_data(
        self,
        data: Union[pd.DataFrame, List[pd.DataFrame]],
        process_func: Callable[..., Any],
        **kwargs: Any
    ) -> Any:
        """
        Process data using a custom function.
        
        Args:
            data: DataFrame(s) to process
            process_func: Function to apply to the data
            **kwargs: Additional arguments for the process function
            
        Returns:
            Processed data
        """
        try:
            result = process_func(data, **kwargs)
            log_and_print(f"✅ Data processing completed successfully")
            return result
        except Exception as e:
            log_and_print(f"❌ Error processing data: {e}")
            raise
    
    def save_results(
        self,
        data: Any,
        output_path: Union[str, Path],
        format: str = 'excel',
        **kwargs: Any
    ) -> Path:
        """
        Save results to output path with standard formatting.
        
        Args:
            data: Data to save
            output_path: Path to save the data
            format: Output format ('excel' or 'csv')
            **kwargs: Additional arguments for saving
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        ensure_output_dir(output_path.parent)
        
        try:
            if isinstance(data, pd.DataFrame):
                if format.lower() == 'excel':
                    data.to_excel(output_path, index=False, **kwargs)
                else:
                    data.to_csv(output_path, index=False, **kwargs)
            else:
                # Handle other data types (dict, list, etc.)
                if format.lower() == 'excel':
                    pd.DataFrame(data).to_excel(output_path, index=False, **kwargs)
                else:
                    pd.DataFrame(data).to_csv(output_path, index=False, **kwargs)
            
            log_and_print(f"💾 Results saved to: {output_path}")
            return output_path
        except Exception as e:
            log_and_print(f"❌ Error saving results: {e}")
            raise
    
    def run_pipeline(
        self,
        input_paths: Union[str, Path, List[Union[str, Path]]],
        process_func: Callable[..., Any],
        output_path: Union[str, Path],
        required_columns: Optional[List[str]] = None,
        format: str = 'excel',
        **kwargs: Any
    ) -> Tuple[Any, Path]:
        """
        Run a complete data processing pipeline.
        
        Args:
            input_paths: Input file path(s)
            process_func: Function to process the data
            output_path: Path to save results
            required_columns: Optional required columns for validation
            format: Output format
            **kwargs: Additional arguments for processing
            
        Returns:
            Tuple of (processed_data, output_path)
        """
        log_and_print(f"🚀 Starting {self.name} pipeline")
        
        # Load and validate data
        data = self.load_and_validate(input_paths, required_columns)
        
        # Process data
        result = self.process_data(data, process_func, **kwargs)
        
        # Save results
        saved_path = self.save_results(result, output_path, format)
        
        log_and_print(f"✅ {self.name} pipeline completed successfully")
        return result, saved_path


def load_and_process_data(
    input_paths: Union[str, Path, List[Union[str, Path]]],
    process_func: Callable[..., Any],
    output_path: Union[str, Path],
    required_columns: Optional[List[str]] = None,
    format: str = 'excel',
    **kwargs: Any
) -> Tuple[Any, Path]:
    """
    Convenience function for loading and processing data.
    
    Args:
        input_paths: Input file path(s)
        process_func: Function to process the data
        output_path: Path to save results
        required_columns: Optional required columns for validation
        format: Output format
        **kwargs: Additional arguments for processing
        
    Returns:
        Tuple of (processed_data, output_path)
    """
    processor = DataProcessor("DataProcessor")
    return processor.run_pipeline(
        input_paths, process_func, output_path, 
        required_columns, format, **kwargs
    )


def validate_and_transform_data(
    data: pd.DataFrame,
    validation_rules: Dict[str, Any],
    transform_func: Optional[Callable[..., Any]] = None,
    **kwargs: Any
) -> pd.DataFrame:
    """
    Validate and optionally transform data.
    
    Args:
        data: DataFrame to validate and transform
        validation_rules: Rules for validation
        transform_func: Optional function to transform data
        **kwargs: Additional arguments for transformation
        
    Returns:
        Validated and optionally transformed DataFrame
    """
    # Validate data
    for rule_name, rule_config in validation_rules.items():
        # Apply validation rule
        if rule_config.get('required_columns'):
            missing = set(rule_config['required_columns']) - set(data.columns)
            if missing:
                log_and_print(f"❌ Validation failed for {rule_name}: missing columns {missing}")
                raise ValueError(f"Missing required columns: {missing}")
    
    # Transform data if function provided
    if transform_func:
        data = transform_func(data, **kwargs)
        log_and_print(f"✅ Data transformation completed")
    
    return data


def batch_process_files(
    input_dir: Union[str, Path],
    process_func: Callable[..., Any],
    output_dir: Union[str, Path],
    file_pattern: str = "*.csv",
    **kwargs: Any
) -> List[Path]:
    """
    Process multiple files in a directory.
    
    Args:
        input_dir: Directory containing input files
        process_func: Function to process each file
        output_dir: Directory to save processed files
        file_pattern: Pattern to match input files
        **kwargs: Additional arguments for processing
        
    Returns:
        List of output file paths
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input_files = list(input_dir.glob(file_pattern))
    output_files = []
    
    log_and_print(f"🔄 Processing {len(input_files)} files from {input_dir}")
    
    for input_file in input_files:
        try:
            output_file = output_dir / f"processed_{input_file.name}"
            result, saved_path = load_and_process_data(
                input_file, process_func, output_file, **kwargs
            )
            output_files.append(saved_path)
        except Exception as e:
            log_and_print(f"❌ Error processing {input_file}: {e}")
    
    log_and_print(f"✅ Batch processing completed: {len(output_files)} files processed")
    return output_files 
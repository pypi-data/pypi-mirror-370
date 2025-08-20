"""
Common tool patterns and utilities.

This module provides simple functions to create tools with standard patterns.
"""

from typing import Any, Dict, Optional, Union, Callable, Type, Tuple
from pathlib import Path
import pandas as pd

from ..core import BaseTool
from ..data.processing import setup_tool_files, save_data
from ..io import load_data, find_first_data_file
from ..logging import log_and_print


def create_standard_tool(
    tool_type: str,
    name: str,
    description: str,
    func: Callable,
    **kwargs: Any
) -> Type[BaseTool]:
    """
    Create a standard tool with common patterns.
    
    Args:
        tool_type: Type of tool ('validation', 'transformation', 'checker')
        name: Tool name
        description: Tool description
        func: Function that performs the tool's main operation
        **kwargs: Additional arguments for the tool factory
        
    Returns:
        Tool class with standard patterns
    """
    requires_dictionary: bool = kwargs.get('requires_dictionary', True)
    
    class StandardTool(BaseTool):
        def __init__(self) -> None:
            super().__init__(name=name, description=description)
        
        def validate_input(self, input_data: Any) -> bool:
            """Standard validation - always returns True for file-based tools."""
            return True
        
        def run(self, *args: Any, **kwargs: Any) -> None:
            """Run method for BaseTool compatibility."""
            pass
        
        def validate(self, domain: str, input_path: str, output_path: str, paths: Dict[str, Any]) -> None:
            """Standard validation pattern."""
            if tool_type == 'validation':
                if requires_dictionary:
                    dataset_file, dictionary_file = setup_tool_files(paths, domain, name)
                    if not dataset_file or not dictionary_file:
                        return
                    func(domain, dataset_file, dictionary_file, output_path, paths)
                else:
                    dataset_file = find_first_data_file(input_path)
                    if not dataset_file:
                        log_and_print(f"❌ No input file found for {domain}")
                        return
                    func(domain, dataset_file, output_path, paths)
        
        def transform(self, domain: str, input_path: Union[str, Path], output_path: Union[str, Path], paths: Optional[Dict[str, Any]] = None) -> None:
            """Standard transformation pattern."""
            if tool_type == 'transformation':
                try:
                    dataset_file = find_first_data_file(input_path)
                    if not dataset_file:
                        log_and_print(f"❌ No input file found for {domain}")
                        return
                    
                    df = load_data(dataset_file)
                    transformed = func(df, domain)
                    
                    save_data(transformed, output_path, format='excel')
                    log_and_print(f"✅ Transformed data saved to: {output_path}")
                    
                except Exception as e:
                    log_and_print(f"❌ Error processing {domain}: {e}")
        
        def check(self, domain: str, input_path: str, output_path: str, paths: Dict[str, Any]) -> None:
            """Standard checking pattern."""
            if tool_type == 'checker':
                if requires_dictionary:
                    dataset_file, dictionary_file = setup_tool_files(paths, domain, name)
                    if not dataset_file or not dictionary_file:
                        return
                    results = func(dataset_file, dictionary_file, domain)
                else:
                    dataset_file = find_first_data_file(input_path)
                    if not dataset_file:
                        log_and_print(f"❌ No input file found for {domain}")
                        return
                    results = func(dataset_file, domain)
                
                if results is not None:
                    save_data(results, output_path, format='excel')
    
    return StandardTool


def create_runner_function(tool_class: Type[BaseTool], **default_kwargs: Any) -> Callable[[str, str, str, Dict[str, Any]], None]:
    """
    Create a standardized runner function for a tool.
    
    Args:
        tool_class: Tool class to create runner for
        **default_kwargs: Default arguments for the tool
        
    Returns:
        Function that can be used as a tool runner
    """
    def runner(domain: str, input_path: str, output_path: str, paths: Dict[str, Any], **kwargs: Any) -> None:
        """Standardized tool runner function."""
        try:
            # Create tool instance
            tool = tool_class(name=tool_class.__name__, description=getattr(tool_class, '__doc__', '') or '')
            
            # Merge default kwargs with provided kwargs
            execution_kwargs = {**default_kwargs, **kwargs}
            
            # Execute tool based on available methods
            if hasattr(tool, 'check'):
                tool.check(domain, input_path, output_path, paths, **execution_kwargs)
            elif hasattr(tool, 'validate'):
                tool.validate(domain, input_path, output_path, paths, **execution_kwargs)
            elif hasattr(tool, 'transform'):
                tool.transform(domain, input_path, output_path, paths, **execution_kwargs)
            elif hasattr(tool, 'run'):
                tool.run(domain=domain, input_path=input_path, output_path=output_path, paths=paths, **execution_kwargs)
            else:
                raise AttributeError(f"Tool {tool_class.__name__} has no recognized execution method")
                
        except Exception as e:
            log_and_print(f"❌ Error in {tool_class.__name__} for {domain}: {e}")
            raise
    
    return runner


def create_simple_tool(
    name: str,
    description: str,
    process_func: Callable,
    tool_type: str = 'validation',
    **kwargs: Any
) -> Tuple[Type[BaseTool], Callable[[str, str, str, Dict[str, Any]], None]]:
    """
    Create a simple tool with standard patterns and runner function.
    
    Args:
        name: Tool name
        description: Tool description
        process_func: Function that performs the tool's main operation
        tool_type: Type of tool ('validation', 'transformation', 'checker')
        **kwargs: Additional arguments for the tool factory
        
    Returns:
        Tuple of (tool_class, runner_function)
    """
    tool_class = create_standard_tool(tool_type, name, description, process_func, **kwargs)
    runner_func = create_runner_function(tool_class)
    
    return tool_class, runner_func 
"""
Pipeline execution utilities.

This module consolidates common pipeline execution patterns used across
the ScriptCraft framework.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from ..logging import log_and_print
from ..io import ensure_output_dir


class PipelineExecutor:
    """
    Standardized pipeline executor for common patterns.
    
    Provides DRY implementations of common pipeline execution operations
    used across multiple pipelines.
    """
    
    def __init__(self, name: str = "PipelineExecutor") -> None:
        """Initialize the pipeline executor."""
        self.name = name
        self.step_timings: List[tuple] = []
    
    def run_step(
        self,
        step_name: str,
        step_func: Callable[..., Any],
        domain: Optional[str] = None,
        input_path: Optional[Union[str, Path]] = None,
        output_path: Optional[Union[str, Path]] = None,
        paths: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> bool:
        """
        Run a single pipeline step with standardized logging and error handling.
        
        Args:
            step_name: Name of the step
            step_func: Function to execute
            domain: Optional domain for domain-specific steps
            input_path: Optional input path
            output_path: Optional output path
            paths: Optional path configuration
            **kwargs: Additional arguments for the step
            
        Returns:
            True if step completed successfully, False otherwise
        """
        start_time = time.time()
        
        try:
            log_and_print(f"🚀 Starting step: {step_name}")
            
            # Execute the step
            if domain and input_path and output_path and paths:
                step_func(domain=domain, input_path=input_path, output_path=output_path, paths=paths, **kwargs)
            elif domain and paths:
                step_func(domain=domain, paths=paths, **kwargs)
            else:
                step_func(**kwargs)
            
            duration = time.time() - start_time
            self.step_timings.append((step_name, duration))
            
            log_and_print(f"✅ Completed step: {step_name} in {duration:.2f}s")
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.step_timings.append((step_name, duration))
            
            log_and_print(f"❌ Error in step: {step_name} after {duration:.2f}s: {e}")
            return False
    
    def run_steps(
        self,
        steps: List[Dict[str, Any]],
        domain: Optional[str] = None,
        paths: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, bool]:
        """
        Run multiple pipeline steps.
        
        Args:
            steps: List of step configurations
            domain: Optional domain for domain-specific steps
            paths: Optional path configuration
            **kwargs: Additional arguments for steps
            
        Returns:
            Dictionary mapping step names to success status
        """
        results = {}
        
        for i, step_config in enumerate(steps, 1):
            step_name = step_config.get('name', f"Step_{i}")
            step_func = step_config.get('func')
            
            if not step_func:
                log_and_print(f"⚠️ Step {step_name} has no function defined")
                results[step_name] = False
                continue
            
            # Get step-specific arguments
            step_kwargs = {**kwargs, **step_config.get('kwargs', {})}
            
            # Run the step
            success = self.run_step(
                step_name=step_name,
                step_func=step_func,
                domain=domain,
                paths=paths,
                **step_kwargs
            )
            
            results[step_name] = success
        
        return results
    
    def get_timing_summary(self) -> str:
        """Get a summary of step timings."""
        if not self.step_timings:
            return "No steps executed"
        
        summary = f"\n🧾 {self.name} Timing Summary:\n"
        total_time = sum(duration for _, duration in self.step_timings)
        
        for step_name, duration in self.step_timings:
            summary += f"   ⏱️ {step_name}: {duration:.2f}s\n"
        
        summary += f"   📊 Total: {total_time:.2f}s"
        return summary


def run_pipeline_step(
    step_name: str,
    step_func: Callable[..., Any],
    domain: Optional[str] = None,
    input_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    paths: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> bool:
    """
    Run a single pipeline step with standardized execution.
    
    Args:
        step_name: Name of the step
        step_func: Function to execute
        domain: Optional domain for domain-specific steps
        input_path: Optional input path
        output_path: Optional output path
        paths: Optional path configuration
        **kwargs: Additional arguments for the step
        
    Returns:
        True if step completed successfully, False otherwise
    """
    executor = PipelineExecutor()
    return executor.run_step(
        step_name=step_name,
        step_func=step_func,
        domain=domain,
        input_path=input_path,
        output_path=output_path,
        paths=paths,
        **kwargs
    )


def run_pipeline_steps(
    steps: List[Dict[str, Any]],
    domain: Optional[str] = None,
    paths: Optional[Dict[str, Any]] = None,
    **kwargs: Any
) -> Dict[str, bool]:
    """
    Run multiple pipeline steps with standardized execution.
    
    Args:
        steps: List of step configurations
        domain: Optional domain for domain-specific steps
        paths: Optional path configuration
        **kwargs: Additional arguments for steps
        
    Returns:
        Dictionary mapping step names to success status
    """
    executor = PipelineExecutor()
    results = executor.run_steps(steps, domain, paths, **kwargs)
    
    # Print timing summary
    log_and_print(executor.get_timing_summary())
    
    return results


def create_pipeline_step(
    name: str,
    func: Callable[..., Any],
    input_key: str = "input",
    output_key: str = "output",
    check_exists: bool = True,
    run_mode: str = "domain",
    tags: Optional[List[str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a standardized pipeline step configuration.
    
    Args:
        name: Step name
        func: Function to execute
        input_key: Key for input path in paths dict
        output_key: Key for output path in paths dict
        check_exists: Whether to check if input exists
        run_mode: Execution mode ('domain', 'global', 'single_domain')
        tags: Optional tags for filtering
        **kwargs: Additional step configuration
        
    Returns:
        Step configuration dictionary
    """
    return {
        'name': name,
        'func': func,
        'input_key': input_key,
        'output_key': output_key,
        'check_exists': check_exists,
        'run_mode': run_mode,
        'tags': tags or [],
        'kwargs': kwargs
    }


def validate_pipeline_steps(steps: List[Dict[str, Any]]) -> bool:
    """
    Validate pipeline step configurations.
    
    Args:
        steps: List of step configurations
        
    Returns:
        True if all steps are valid, False otherwise
    """
    valid = True
    
    for i, step in enumerate(steps):
        if not step.get('name'):
            log_and_print(f"❌ Step {i} has no name")
            valid = False
        
        if not step.get('func') or not callable(step['func']):
            log_and_print(f"❌ Step {step.get('name', i)} has no callable function")
            valid = False
    
    return valid 
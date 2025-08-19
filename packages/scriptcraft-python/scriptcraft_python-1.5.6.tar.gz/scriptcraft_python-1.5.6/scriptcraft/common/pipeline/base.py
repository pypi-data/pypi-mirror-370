"""
Core pipeline classes and data structures.

This module provides the fundamental building blocks for pipeline execution:
- PipelineStep: Data structure for pipeline steps
- BasePipeline: Core pipeline implementation
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
import argparse

from ..logging import log_and_print
from ..io.path_resolver import PathResolver
from ..io import get_domain_paths, get_domain_output_path


@dataclass
class PipelineStep:
    """A single step in a pipeline."""
    name: str
    log_filename: str
    qc_func: Callable
    input_key: str
    output_filename: Optional[str] = None
    check_exists: bool = False
    run_mode: str = "domain"
    tags: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []
        self._validate_run_mode()
    
    def _validate_run_mode(self) -> None:
        """Validate run mode and input key combinations."""
        DOMAIN_SCOPED_INPUTS = {"raw_data", "merged_data", "processed_data", "old_data"}
        GLOBAL_INPUTS = {"rhq_inputs", "global_data"}
        
        if self.run_mode == "domain" and self.input_key in GLOBAL_INPUTS:
            log_and_print(f"⚠️ Warning: Step '{self.name}' uses domain mode with global input_key '{self.input_key}'.")
        if self.run_mode == "single_domain" and self.input_key not in DOMAIN_SCOPED_INPUTS:
            log_and_print(f"⚠️ Warning: Step '{self.name}' uses single_domain mode with possible mismatch input_key '{self.input_key}'.")
        if self.run_mode == "global" and self.input_key in DOMAIN_SCOPED_INPUTS:
            log_and_print(f"⚠️ Warning: Step '{self.name}' uses global mode with domain-level input_key '{self.input_key}'.")
        if self.run_mode == "custom":
            log_and_print(f"ℹ️ Info: Step '{self.name}' uses custom mode. Ensure qc_func handles everything explicitly.")


class BasePipeline:
    """Base class for all pipelines."""
    
    def __init__(self, config: Any, name: Optional[str] = None, description: Optional[str] = None) -> None:
        self.config = config
        self.name = name or getattr(config, 'name', 'Unknown Pipeline')
        self.description = description or getattr(config, 'description', None)
        self.steps: List[PipelineStep] = []
        self._validate_config()
        self.step_timings: List[tuple] = []
        
        # Dependency injection: get path resolver from config
        if hasattr(config, 'get_path_resolver'):
            self.path_resolver = config.get_path_resolver()
        else:
            # Fallback for config objects without path resolver
            self.path_resolver = None
        
        # Backward compatibility: still provide root for legacy code
        if self.path_resolver:
            self.root = self.path_resolver.get_workspace_root()
        else:
            self.root = Path.cwd()

    def _validate_config(self) -> None:
        """Validate the pipeline configuration."""
        if not hasattr(self.config, 'domains'):
            raise ValueError("Pipeline config must have 'domains' defined")
        if not isinstance(self.config.domains, list):
            raise ValueError("Pipeline config 'domains' must be a list")

    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline."""
        self.steps.append(step)

    def insert_step(self, index: int, step: PipelineStep) -> None:
        """Insert a step at a specific position."""
        self.steps.insert(index, step)

    def get_steps(self, tag_filter: Optional[str] = None) -> List[PipelineStep]:
        """Get pipeline steps, optionally filtered by tag."""
        if tag_filter:
            return [s for s in self.steps if s.tags and tag_filter in s.tags]
        return self.steps

    def validate(self) -> bool:
        """Validate pipeline configuration."""
        valid = True
        if not self.steps:
            log_and_print(f"⚠️ Pipeline '{self.config.name}' has no steps.")
            valid = False
        for step in self.steps:
            if not callable(step.qc_func):
                log_and_print(f"❌ Step '{step.name}' has no callable qc_func.")
                valid = False
        return valid

    def _run_domain_step(self, step: PipelineStep, domain: str) -> None:
        """Run a step for a specific domain."""
        # Use path resolver if available, otherwise fallback
        if self.path_resolver:
            domain_paths = self.path_resolver.get_domain_paths(domain)
            if not domain_paths:
                log_and_print(f"❌ Domain '{domain}' not found.")
                return
            input_path = self.path_resolver.resolve_input_path(step.input_key, domain)
            output_path = self.path_resolver.resolve_output_path(step.output_filename, domain)
            log_path = self.path_resolver.get_logs_dir() / f"{step.log_filename.replace('.log', '')}_{domain}.log"
        else:
            # Fallback for legacy config objects
            domain_paths = get_domain_paths(self.root).get(domain)
            if not domain_paths:
                log_and_print(f"❌ Domain '{domain}' not found.")
                return
            input_path = domain_paths.get(step.input_key)
            output_path = get_domain_output_path(domain_paths, step.output_filename)
            log_path = self.root / "logs" / f"{step.log_filename.replace('.log', '')}_{domain}.log"
        if step.check_exists and (not input_path or not input_path.exists()):
            log_and_print(f"⚠️ Input path not found: {input_path}")
            return
        log_path.parent.mkdir(parents=True, exist_ok=True)
        # Use logging context if available
        try:
            from ..logging import with_domain_logger
            with with_domain_logger(log_path, lambda: step.qc_func(
                domain=domain,
                input_path=input_path,
                output_path=output_path,
                paths=domain_paths
            )):
                pass  # Success logging is handled by the context manager
        except ImportError:
            # Fallback logging
            log_and_print(f"🚀 Running {step.name} for {domain}")
            step.qc_func(
                domain=domain,
                input_path=input_path,
                output_path=output_path,
                paths=domain_paths
            )
            log_and_print(f"✅ Completed {step.name} for {domain}")
    
    def _run_global_step(self, step: PipelineStep) -> None:
        """Run a global step."""
        # Use path resolver if available, otherwise fallback
        if self.path_resolver:
            log_path = self.path_resolver.get_logs_dir() / step.log_filename
            input_path = self.path_resolver.resolve_input_path(step.input_key)
            output_path = self.path_resolver.resolve_output_path(step.output_filename)
        else:
            # Fallback for legacy config objects
            log_path = self.root / "logs" / step.log_filename
            from ..io import get_input_dir, get_output_dir
            input_path = get_input_dir(self.root)
            output_path = get_output_dir(self.root)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        # Use logging context if available
        try:
            from ..logging import qc_log_context
            with qc_log_context(log_path):
                self._execute_global_step(step, input_path, output_path)
        except ImportError:
            # Fallback logging
            log_and_print(f"🚀 Running global step: {step.name}")
            self._execute_global_step(step, input_path, output_path)
            log_and_print(f"✅ Finished global step: {step.name}")
    
    def _execute_global_step(self, step: PipelineStep, input_path: Path, output_path: Path) -> None:
        """Execute a global step with prepared paths."""
        try:
            # Build kwargs from step configuration and resolved paths
            input_paths_param = None
            if input_path and input_path.is_file():
                input_paths_param = [input_path]
            kwargs = {
                'input_paths': input_paths_param,
                'output_dir': output_path,
                'config': self.config,
                'input_key': step.input_key,
                'output_filename': step.output_filename,
                'check_exists': step.check_exists,
            }
            # Add path resolver info if available
            if self.path_resolver:
                kwargs.update({
                    'log_dir': self.path_resolver.get_logs_dir(),
                    'input_dir': self.path_resolver.get_input_dir()
                })
            # Call the function with step-configured arguments
            step.qc_func(**kwargs)
        except Exception as e:
            log_and_print(f"❌ Error in global step: {e}")
            import traceback
            log_and_print(f"Traceback: {traceback.format_exc()}", level="debug")
    
    def run(self, tag_filter: Optional[str] = None, domain: Optional[str] = None) -> None:
        """
        Run the pipeline.
        
        Args:
            tag_filter: Optional tag to filter steps
            domain: Optional domain for single_domain mode
        """
        log_and_print(f"🔍 Pipeline '{self.name}' starting with {len(self.steps)} total steps")
        if not self.validate():
            log_and_print("❌ Pipeline validation failed. Aborting.")
            return
        filtered_steps = self.get_steps(tag_filter)
        log_and_print(f"🔍 After filtering, running {len(filtered_steps)} steps")
        self.step_timings = []
        for idx, step in enumerate(filtered_steps, 1):
            log_and_print(f"\n[{idx}/{len(filtered_steps)}] 🚀 Running {step.name}...")
            start = time.time()
            try:
                if step.run_mode == "global":
                    self._run_global_step(step)
                elif step.run_mode == "single_domain":
                    if not domain:
                        log_and_print("❌ 'single_domain' mode requires domain parameter.")
                        continue
                    self._run_domain_step(step, domain)
                elif step.run_mode == "custom":
                    step.qc_func()
                else:  # domain mode
                    # Get all domains
                    if self.path_resolver:
                        all_domain_paths = self.path_resolver.get_all_domain_paths()
                    else:
                        from ..io import get_domain_paths
                        all_domain_paths = get_domain_paths(self.root).keys()
                    for domain_name in all_domain_paths:
                        self._run_domain_step(step, domain_name)
                duration = time.time() - start
                log_and_print(f"[{idx}/{len(filtered_steps)}] ✅ Finished {step.name} in {duration:.2f}s.")
                self.step_timings.append((step.name, duration))
            except Exception as e:
                duration = time.time() - start
                log_and_print(f"[{idx}/{len(filtered_steps)}] ❌ Error in {step.name} after {duration:.2f}s: {e}")
                self.step_timings.append((step.name, duration))

    def print_summary(self) -> None:
        """Print pipeline execution summary."""
        if not self.step_timings:
            return
        log_and_print("\n🧾 Step Timing Summary:")
        total_time = 0
        for name, duration in self.step_timings:
            log_and_print(f"   ⏱️ {name}: {duration:.2f} sec")
            total_time += duration
        log_and_print(f"\n⏱️ Total pipeline duration: {total_time:.2f} seconds.") 
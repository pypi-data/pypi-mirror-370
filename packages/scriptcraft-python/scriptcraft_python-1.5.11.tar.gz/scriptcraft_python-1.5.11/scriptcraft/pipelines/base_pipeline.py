"""
scripts/pipelines/base_pipeline.py

📦 Base pipeline and step definitions.

This module provides:
- BasePipeline class for pipeline execution
- PipelineStep dataclass for step configuration
- Core pipeline validation and execution logic
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
import argparse
from ..common import *
import scriptcraft.common as cu
from ..common.io.path_resolver import PathResolver


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
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        self._validate_run_mode()
    
    def _validate_run_mode(self):
        """Validate run mode and input key combinations."""
        DOMAIN_SCOPED_INPUTS = {"raw_data", "merged_data", "processed_data", "old_data"}
        GLOBAL_INPUTS = {"rhq_inputs", "global_data"}
        
        if self.run_mode == "domain" and self.input_key in GLOBAL_INPUTS:
            cu.log_and_print(f"⚠️ Warning: Step '{self.name}' uses domain mode with global input_key '{self.input_key}'.")
        if self.run_mode == "single_domain" and self.input_key not in DOMAIN_SCOPED_INPUTS:
            cu.log_and_print(f"⚠️ Warning: Step '{self.name}' uses single_domain mode with possible mismatch input_key '{self.input_key}'.")
        if self.run_mode == "global" and self.input_key in DOMAIN_SCOPED_INPUTS:
            cu.log_and_print(f"⚠️ Warning: Step '{self.name}' uses global mode with domain-level input_key '{self.input_key}'.")
        if self.run_mode == "custom":
            cu.log_and_print(f"ℹ️ Info: Step '{self.name}' uses custom mode. Ensure qc_func handles everything explicitly.")


class BasePipeline:
    """Base class for all pipelines."""
    
    def __init__(self, config: cu.Config, name: str = None, description: str = None):
        self.config = config
        self.name = name or getattr(config, 'name', 'Unknown Pipeline')
        self.description = description or getattr(config, 'description', None)
        self.steps: List[PipelineStep] = []
        self._validate_config()
        self.step_timings: List[tuple] = []
        
        # Dependency injection: get path resolver from config
        self.path_resolver = config.get_path_resolver()
        
        # Backward compatibility: still provide root for legacy code
        self.root = self.path_resolver.get_workspace_root()
    
    def _validate_config(self):
        """Validate the pipeline configuration."""
        if not hasattr(self.config, 'domains'):
            raise ValueError("Pipeline config must have 'domains' defined")
        if not isinstance(self.config.domains, list):
            raise ValueError("Pipeline config 'domains' must be a list")
    
    def add_step(self, step: PipelineStep):
        """Add a step to the pipeline."""
        self.steps.append(step)
    
    def insert_step(self, index: int, step: PipelineStep) -> None:
        """Insert a step at a specific position."""
        self.steps.insert(index, step)
    
    def get_steps(self, tag_filter: Optional[str] = None) -> List[PipelineStep]:
        """Get pipeline steps, optionally filtered by tag."""
        if tag_filter:
            return [s for s in self.steps if tag_filter in s.tags]
        return self.steps
    
    def validate(self) -> bool:
        """Validate pipeline configuration."""
        valid = True
        if not self.steps:
            cu.log_and_print(f"⚠️ Pipeline '{self.config.name}' has no steps.")
            valid = False
        for step in self.steps:
            if not callable(step.qc_func):
                cu.log_and_print(f"❌ Step '{step.name}' has no callable qc_func.")
                valid = False
        return valid
    
    def _run_domain_step(self, step: PipelineStep, domain: str) -> None:
        """Run a step for a specific domain."""
        # Use path resolver instead of global function
        domain_paths = self.path_resolver.get_domain_paths(domain)
        if not domain_paths:
            cu.log_and_print(f"❌ Domain '{domain}' not found.")
            return
        
        input_path = self.path_resolver.resolve_input_path(step.input_key, domain)
        output_path = self.path_resolver.resolve_output_path(step.output_filename, domain)
        
        if step.check_exists and (not input_path or not input_path.exists()):
            cu.log_and_print(f"⚠️ Input path not found: {input_path}")
            return
        
        log_path = self.path_resolver.get_logs_dir() / f"{step.log_filename.replace('.log', '')}_{domain}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with cu.with_domain_logger(log_path, lambda: step.qc_func(
            domain=domain,
            input_path=input_path,
            output_path=output_path,
            paths=domain_paths
        )):
            cu.log_and_print(f"✅ Completed {step.name} for {domain}")
    
    def _run_global_step(self, step: PipelineStep) -> None:
        """Run a global step."""
        # Use path resolver for workspace-aware log path
        log_path = self.path_resolver.get_logs_dir() / step.log_filename
        with cu.qc_log_context(log_path):
            try:
                # Prepare arguments for global tools
                input_path = self.path_resolver.resolve_input_path(step.input_key)
                output_path = self.path_resolver.resolve_output_path(step.output_filename)
                
                # Build kwargs from step configuration and resolved paths
                # For global tools, don't pass input_paths if it's a directory (let tool auto-discover)
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
                    'log_dir': self.path_resolver.get_logs_dir(),
                    'input_dir': self.path_resolver.get_input_dir()  # Add explicit input directory
                }
                
                # Call the function with step-configured arguments
                step.qc_func(**kwargs)
                cu.log_and_print(f"✅ Finished global step: {step.name}", logger_name="run_all")
            except Exception as e:
                cu.log_and_print(f"❌ Error in global step: {e}", logger_name="run_all")
                import traceback
                cu.log_and_print(f"Traceback: {traceback.format_exc()}", level="debug", logger_name="run_all")
    
    def run(self, tag_filter: Optional[str] = None, domain: Optional[str] = None) -> None:
        """
        Run the pipeline.
        
        Args:
            tag_filter: Optional tag to filter steps
            domain: Optional domain for single_domain mode
        """
        cu.log_and_print(f"🔍 Pipeline '{self.name}' starting with {len(self.steps)} total steps", logger_name="run_all")
        
        if not self.validate():
            cu.log_and_print("❌ Pipeline validation failed. Aborting.", logger_name="run_all")
            return
        
        filtered_steps = self.get_steps(tag_filter)
        cu.log_and_print(f"🔍 After filtering, running {len(filtered_steps)} steps", logger_name="run_all")
        self.step_timings = []
        
        for idx, step in enumerate(filtered_steps, 1):
            cu.log_and_print(f"\n[{idx}/{len(filtered_steps)}] 🚀 Running {step.name}...", logger_name="run_all")
            start = time.time()
            
            try:
                if step.run_mode == "global":
                    self._run_global_step(step)
                elif step.run_mode == "single_domain":
                    if not domain:
                        cu.log_and_print("❌ 'single_domain' mode requires domain parameter.", logger_name="run_all")
                        continue
                    self._run_domain_step(step, domain)
                elif step.run_mode == "custom":
                    step.qc_func()
                else:  # domain mode
                    # Use path resolver to get all domains
                    all_domain_paths = self.path_resolver.get_all_domain_paths()
                    for domain_name in all_domain_paths:
                        self._run_domain_step(step, domain_name)
                
                duration = time.time() - start
                cu.log_and_print(f"[{idx}/{len(filtered_steps)}] ✅ Finished {step.name} in {duration:.2f}s.", logger_name="run_all")
                self.step_timings.append((step.name, duration))
                
            except Exception as e:
                duration = time.time() - start
                cu.log_and_print(f"[{idx}/{len(filtered_steps)}] ❌ Error in {step.name} after {duration:.2f}s: {e}", logger_name="run_all")
                self.step_timings.append((step.name, duration))
    
    def print_summary(self) -> None:
        """Print pipeline execution summary."""
        if not self.step_timings:
            return
        
        cu.log_and_print("\n🧾 Step Timing Summary:")
        total_time = 0
        for name, duration in self.step_timings:
            cu.log_and_print(f"   ⏱️ {name}: {duration:.2f} sec")
            total_time += duration
        cu.log_and_print(f"\n⏱️ Total pipeline duration: {total_time:.2f} seconds.") 
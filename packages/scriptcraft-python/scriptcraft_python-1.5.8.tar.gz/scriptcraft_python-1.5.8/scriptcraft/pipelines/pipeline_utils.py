"""
scripts/pipelines/pipeline_utils.py

📦 Pipeline and QC orchestration helpers.

This module manages:
- Definition of pipeline steps
- Execution of steps across domains or globally
- Flexible logging and error handling
- Core pipeline run logic
"""

import time
import argparse
from pathlib import Path
from collections import namedtuple
from typing import Dict, Optional, List, Any, Callable, Union
from ..common import *
import scriptcraft.common as cu
from .base_pipeline import BasePipeline

# === 🏗️ PipelineStep Data Structure ===
PipelineStep = namedtuple(
    "PipelineStep",
    ["name", "log_filename", "qc_func", "input_key",
     "output_filename", "check_exists", "run_mode", "tags"]
)

# === 🧩 Create a Pipeline Step ===
def make_step(name: str, log_filename: str, qc_func: Callable, input_key: str, 
              output_filename: Optional[str] = None, check_exists: bool = False, 
              run_mode: str = "domain", tags: Optional[List[str]] = None) -> PipelineStep:
    """
    Create a pipeline step with validation.
    
    Args:
        name: Step name
        log_filename: Log file name
        qc_func: Function to execute
        input_key: Input key for path resolution
        output_filename: Optional output filename
        check_exists: Whether to check if input exists
        run_mode: Execution mode
        tags: Optional tags for filtering
        
    Returns:
        PipelineStep object
    """
    DOMAIN_SCOPED_INPUTS = {"raw_data", "merged_data", "processed_data", "old_data"}
    GLOBAL_INPUTS = {"rhq_inputs", "global_data"}

    if run_mode == "domain" and input_key in GLOBAL_INPUTS:
        cu.log_and_print(f"⚠️ Warning: Step '{name}' uses domain mode with global input_key '{input_key}'.")
    if run_mode == "single_domain" and input_key not in DOMAIN_SCOPED_INPUTS:
        cu.log_and_print(f"⚠️ Warning: Step '{name}' uses single_domain mode with possible mismatch input_key '{input_key}'.")
    if run_mode == "global" and input_key in DOMAIN_SCOPED_INPUTS:
        cu.log_and_print(f"⚠️ Warning: Step '{name}' uses global mode with domain-level input_key '{input_key}'.")
    if run_mode == "custom":
        cu.log_and_print(f"ℹ️ Info: Step '{name}' uses custom mode. Ensure qc_func handles everything explicitly.")

    return PipelineStep(name, log_filename, qc_func, input_key, output_filename, check_exists, run_mode, tags or [])


# === ✅ Validate Pipeline Definitions ===
def validate_pipelines(step_map: Dict[str, List[PipelineStep]]) -> bool:
    """
    Validate pipeline definitions.
    
    Args:
        step_map: Dictionary mapping pipeline names to step lists
        
    Returns:
        True if all pipelines are valid
    """
    valid = True
    for name, steps in step_map.items():
        if not steps:
            cu.log_and_print(f"⚠️ Pipeline '{name}' has no steps.")
            valid = False
        for step in steps:
            if not callable(step.qc_func):
                cu.log_and_print(f"❌ Step '{step.name}' in pipeline '{name}' has no callable qc_func.")
                valid = False
    return valid


# === ➕ Add Supplement Steps Dynamically ===
def add_supplement_steps(pipeline: BasePipeline, prepare: bool = False, merge: bool = False) -> None:
    """
    Add supplement-related steps to a pipeline.
    
    Args:
        pipeline: Pipeline to add steps to
        prepare: Whether to add supplement prepper step
        merge: Whether to add supplement splitter step
    """
    if prepare:
        pipeline.insert_step(0, cu.load_func(
            "scripts.enhancements.supplement_prepper.main.enhancement.enhance"
        ))
    if merge:
        pipeline.insert_step(1, cu.load_func(
            "scripts.enhancements.supplement_splitter.main.enhancement.enhance"
        ))


# === 🚀 Core Execution Logic ===
def run_qc_for_each_domain(log_filename: str, qc_func: Callable, 
                          input_key: str = cu.STANDARD_KEYS["input"], 
                          output_filename: Optional[str] = None, 
                          filename_suffix: Optional[str] = None, 
                          check_exists: bool = True) -> None:
    """
    Run QC function for each domain.
    
    Args:
        log_filename: Log file name
        qc_func: Function to execute
        input_key: Input key for path resolution
        output_filename: Optional output filename
        filename_suffix: Optional filename suffix
        check_exists: Whether to check if input exists
    """
    root = cu.get_project_root()
    domain_paths = cu.get_domain_paths(root)

    for domain, paths in domain_paths.items():
        cu.log_and_print(f"\n🚀 Starting QC for **{domain}**")
        input_path = paths[input_key]
        output_path = cu.get_output_path(paths, output_filename, filename_suffix)

        if check_exists and (not input_path or not input_path.exists()):
            cu.log_and_print(f"⚠️ Input path not found: {input_path}")
            continue

        log_path = paths["qc_output"].parent / "qc_logs" / f"{log_filename.replace('.log', '')}_{domain}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with cu.with_domain_logger(log_path, lambda: qc_func(domain=domain, input_path=input_path, output_path=output_path, paths=paths)):
            cu.log_and_print(f"✅ Completed QC for {domain}")


def run_qc_for_single_domain(domain: str, log_filename: str, qc_func: Callable, 
                            input_key: str, output_filename: Optional[str] = None, 
                            check_exists: bool = True) -> None:
    """
    Run QC function for a single domain.
    
    Args:
        domain: Domain name
        log_filename: Log file name
        qc_func: Function to execute
        input_key: Input key for path resolution
        output_filename: Optional output filename
        check_exists: Whether to check if input exists
    """
    root = cu.get_project_root()
    domain_paths = cu.get_domain_paths(root).get(domain)

    if not domain_paths:
        cu.log_and_print(f"❌ Domain '{domain}' not found.")
        return

    input_path = domain_paths[input_key]
    output_path = cu.get_output_path(domain_paths, output_filename)

    if check_exists and (not input_path or not input_path.exists()):
        cu.log_and_print(f"⚠️ Input path not found: {input_path}")
        return

    log_path = domain_paths["qc_output"].parent / "qc_logs" / f"{log_filename.replace('.log', '')}_{domain}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with cu.with_domain_logger(log_path, lambda: qc_func(domain=domain, input_path=input_path, output_path=output_path, paths=domain_paths)):
        cu.log_and_print(f"✅ Completed QC for {domain}")


def run_qc_single_step(log_filename: str, qc_func: Callable) -> None:
    """
    Run a single QC step.
    
    Args:
        log_filename: Log file name
        qc_func: Function to execute
    """
    log_path = cu.get_project_root() / "logs" / Path(log_filename).name
    with cu.qc_log_context(log_path):
        try:
            qc_func()
            cu.log_and_print(f"✅ Finished single-step QC: {qc_func.__name__}")
        except Exception as e:
            cu.log_and_print(f"❌ Error in single-step QC: {e}")


def run_global_tool(qc_func: Callable, tool_name: Optional[str] = None) -> None:
    """
    Run a global tool with standard input/output handling.
    
    Args:
        qc_func: Function to run
        tool_name: Optional name of the tool
    """
    config = cu.get_config()
    input_dir = cu.get_input_dir()
    output_dir = cu.get_output_dir()
    input_file = config.get("tool_input_file", f"{tool_name}.xlsx") if tool_name else None
    input_path = input_dir / input_file if input_file else input_dir
    
    cu.log_and_print(f"\n==== 🚀 Starting {tool_name or qc_func.__name__} ====")
    cu.log_and_print(f"🔧 Using input: {input_path}, output: {output_dir}")
    qc_func(input_path=input_path, output_path=output_dir, config=config)


# === 🔁 Main Pipeline Executor ===
def run_pipeline_from_steps(steps: List[PipelineStep], tag_filter: Optional[str] = None, 
                           args: Optional[argparse.Namespace] = None) -> None:
    """
    Run pipeline from a list of steps.
    
    Args:
        steps: List of pipeline steps
        tag_filter: Optional tag to filter steps
        args: Optional command line arguments
    """
    step_timings: List[tuple] = []
    filtered = [s for s in steps if tag_filter is None or tag_filter in s.tags]

    for idx, step in enumerate(filtered, 1):
        cu.log_and_print(f"\n[{idx}/{len(filtered)}] 🚀 Running {step.name}...")
        start = time.time()
        log_path = cu.get_project_root() / "logs" / step.log_filename

        with cu.qc_log_context(log_path):
            try:
                if step.run_mode == "global":
                    run_qc_single_step(step.log_filename, step.qc_func)
                elif step.run_mode == "single_domain":
                    if not hasattr(args, "domain") or not args.domain:
                        cu.log_and_print("❌ 'single_domain' mode requires --domain flag.")
                        continue
                    run_qc_for_single_domain(
                        domain=args.domain, log_filename=step.log_filename, qc_func=step.qc_func,
                        input_key=step.input_key, output_filename=step.output_filename, check_exists=step.check_exists
                    )
                elif step.run_mode == "custom":
                    step.qc_func()
                else:
                    run_qc_for_each_domain(
                        log_filename=step.log_filename, qc_func=step.qc_func,
                        input_key=step.input_key, output_filename=step.output_filename, check_exists=step.check_exists
                    )
                duration = time.time() - start
                cu.log_and_print(f"[{idx}/{len(filtered)}] ✅ Finished {step.name} in {duration:.2f}s.")
                step_timings.append((step.name, duration))
            except Exception as e:
                duration = time.time() - start
                cu.log_and_print(f"[{idx}/{len(filtered)}] ❌ Error in {step.name} after {duration:.2f}s: {e}")
                step_timings.append((step.name, duration))

    cu.log_and_print("\n🧾 Step Timing Summary:")
    for name, duration in step_timings:
        cu.log_and_print(f"   ⏱️ {name}: {duration:.2f} sec")


# === 🕒 Timed Pipeline Runner ===
def timed_pipeline(pipeline_func: Callable) -> None:
    """
    Run a pipeline function with timing.
    
    Args:
        pipeline_func: Pipeline function to run
    """
    start = time.time()
    pipeline_func()
    duration = time.time() - start
    cu.log_and_print(f"\n⏱️ Total pipeline duration: {duration:.2f} seconds.")


def list_pipelines(pipelines: Dict[str, BasePipeline]) -> None:
    """
    List available pipelines and their steps.
    
    Args:
        pipelines: Dictionary of pipeline objects
    """
    cu.log_and_print("\n📋 Available Pipelines:")
    for name, pipeline in pipelines.items():
        cu.log_and_print(f"\n🔷 {name}")
        if pipeline.description:
            cu.log_and_print(f"   📝 {pipeline.description}")
        cu.log_and_print("   Steps:")
        for step in pipeline.steps:
            tags = f" [{', '.join(step.tags)}]" if step.tags else ""
            cu.log_and_print(f"   - {step.name}{tags}")


def preview_pipeline(pipeline: BasePipeline, tag_filter: Optional[str] = None) -> None:
    """
    Preview pipeline steps without running them.
    
    Args:
        pipeline: Pipeline to preview
        tag_filter: Optional tag to filter steps
    """
    steps = pipeline.get_steps(tag_filter)
    cu.log_and_print(f"\n🔍 Preview of {pipeline.name} pipeline:")
    if pipeline.description:
        cu.log_and_print(f"📝 {pipeline.description}")
    cu.log_and_print("\nSteps to run:")
    for i, step in enumerate(steps, 1):
        tags = f" [{', '.join(step.tags)}]" if step.tags else ""
        cu.log_and_print(f"{i}. {step.name}{tags}")
        cu.log_and_print(f"   Mode: {step.run_mode}")
        cu.log_and_print(f"   Input: {step.input_key}")
        if step.output_filename:
            cu.log_and_print(f"   Output: {step.output_filename}")


def run_pipeline(pipeline: BasePipeline, args: argparse.Namespace) -> None:
    """
    Run a pipeline with the specified arguments.
    
    Args:
        pipeline: Pipeline to run
        args: Command line arguments
    """
    cu.log_and_print(f"🔍 run_pipeline called with args: tag={getattr(args, 'tag', None)}, domain={getattr(args, 'domain', None)}, dry_run={getattr(args, 'dry_run', False)}", logger_name="run_all")
    
    if getattr(args, 'dry_run', False):
        preview_pipeline(pipeline, getattr(args, 'tag', None))
        return
    
    # Handle supplement arguments safely (they might not exist in all parsers)
    prepare_supplement = getattr(args, 'prepare_supplement', False)
    merge_supplement = getattr(args, 'merge_supplement', False)
    
    if prepare_supplement or merge_supplement:
        add_supplement_steps(pipeline, prepare_supplement, merge_supplement)
    
    cu.log_and_print(f"🔍 About to call pipeline.run with tag_filter={getattr(args, 'tag', None)}, domain={getattr(args, 'domain', None)}", logger_name="run_all")
    pipeline.run(tag_filter=getattr(args, 'tag', None), domain=getattr(args, 'domain', None))
    
    if getattr(args, 'time', False):
        pipeline.print_summary()

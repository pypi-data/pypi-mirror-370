"""
scripts/pipelines/__init__.py

📦 Pipeline package for managing data processing workflows.

This package now imports from the consolidated common.pipeline module
and re-exports for backward compatibility. Domain-specific pipeline
implementations can be added here as separate modules.
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from ..common.pipeline import *

# Legacy alias for backward compatibility
PipelineStepTuple = PipelineStep

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Base Pipeline
#     'BasePipeline', 'PipelineStep', 'PipelineStepTuple',
#     # Factory functionality
#     'PipelineFactory', 'build_step', 'import_function', 'get_pipeline_steps',
#     # Execution utilities
#     'PipelineExecutor', 'run_pipeline_step', 'run_pipeline_steps',
#     'create_pipeline_step', 'validate_pipeline_steps',
#     # Pipeline Utilities
#     'make_step', 'validate_pipelines', 'add_supplement_steps',
#     'run_qc_for_each_domain', 'run_qc_for_single_domain', 'run_qc_single_step',
#     'run_global_tool', 'run_pipeline_from_steps', 'timed_pipeline',
#     'list_pipelines', 'preview_pipeline', 'run_pipeline',
# ]

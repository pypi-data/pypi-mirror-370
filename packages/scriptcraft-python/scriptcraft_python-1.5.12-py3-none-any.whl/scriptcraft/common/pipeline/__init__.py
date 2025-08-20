"""
Pipeline utilities package for common pipeline patterns and utilities.

This module consolidates all core pipeline functionality:
- Base pipeline classes and data structures
- Pipeline factory for configuration-driven creation
- Execution utilities and helpers
- Validation and management functions
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .base import *
from .factory import *
from .execution import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Base classes
#     'BasePipeline', 'PipelineStep',
#     
#     # Factory functionality
#     'PipelineFactory', 'build_step', 'import_function', 'get_pipeline_steps',
#     
#     # Execution utilities
#     'PipelineExecutor', 'run_pipeline_step', 'run_pipeline_steps',
#     'create_pipeline_step', 'validate_pipeline_steps',
#     
#     # Pipeline utilities
#     'make_step', 'validate_pipelines', 'add_supplement_steps',
#     'run_qc_for_each_domain', 'run_qc_for_single_domain', 'run_qc_single_step',
#     'run_global_tool', 'run_pipeline_from_steps', 'timed_pipeline',
#     'list_pipelines', 'preview_pipeline', 'run_pipeline'
# ] 
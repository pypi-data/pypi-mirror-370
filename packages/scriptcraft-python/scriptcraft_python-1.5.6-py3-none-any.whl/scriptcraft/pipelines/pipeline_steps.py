"""
Pipeline Steps Module

This module handles dynamic loading and configuration of pipeline steps from config.yaml.
"""

import importlib
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path

from ..common import *
import scriptcraft.common as cu
from .base_pipeline import BasePipeline, PipelineStep


def import_function(import_path: str) -> Callable[..., Any]:
    """
    Dynamically imports a function from its string path.
    
    Args:
        import_path: Full dotted path to the function
    
    Returns:
        Callable function object
    """
    module_path, func_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    return func


def build_step(step_def: Dict[str, Any]) -> PipelineStep:
    """
    Builds a pipeline step from a config dictionary.
    
    Args:
        step_def: Dictionary with step configuration
    
    Returns:
        PipelineStep object
    """
    # Handle dynamic lambda function if present
    if step_def.get("func") == "scripts.tools.data_content_comparer.tool.run_content_comparer":
        func = lambda **kwargs: import_function(step_def["func"])(
            mode="rhq_mode",
            input_dir="input",
            **kwargs
        )
    else:
        func = import_function(step_def["func"])
    
    return PipelineStep(
        name=step_def["name"],
        log_filename=step_def["log"],
        qc_func=func,
        input_key=step_def.get("input_key", "raw_data"),
        output_filename=step_def.get("output_filename"),
        check_exists=step_def.get("check_exists", False),
        run_mode=step_def.get("run_mode", "domain"),
        tags=step_def.get("tags", [])
    )


class PipelineFactory:
    """Factory class for creating pipelines from configuration."""
    
    def __init__(self, config_obj: Optional[Any] = None) -> None:
        """Initialize the pipeline factory.
        
        Args:
            config_obj: Optional Config object. If None, loads default config.
        """
        if config_obj is None:
            config_obj = cu.load_config()
        
        self.config_obj = config_obj
        self.config = {
            "pipelines": config_obj.pipelines,
            "pipeline_descriptions": getattr(config_obj, "pipeline_descriptions", {})
        }
        self.pipeline_defs = self.config.get("pipelines", {})
        self.pipelines: Dict[str, BasePipeline] = {}
    
    def _build_pipeline(self, name: str, pipeline_config: Any) -> BasePipeline:
        """
        Build a pipeline from its configuration.
        
        Args:
            name: Name of the pipeline
            pipeline_config: Pipeline configuration (can be list or dict with description/steps)
        
        Returns:
            Configured BasePipeline object
        """
        # Use the config object from factory
        config_obj = self.config_obj
        
        # Extract description and steps from new config format
        if isinstance(pipeline_config, dict) and "steps" in pipeline_config:
            description = pipeline_config.get("description", "")
            steps_or_refs = pipeline_config["steps"]
        else:
            # Legacy format - just a list of steps
            description = ""
            steps_or_refs = pipeline_config
        
        pipeline = BasePipeline(config_obj, name=name, description=description)
        
        for item in steps_or_refs:
            if isinstance(item, dict):
                if "func" in item:
                    # Build actual step
                    pipeline.add_step(build_step(item))
                elif "ref" in item:
                    # It's a reference to another pipeline
                    ref_pipeline = self.pipelines.get(item["ref"])
                    if ref_pipeline:
                        for step in ref_pipeline.steps:
                            pipeline.add_step(step)
            else:
                # Legacy single string (like "full"), treat as ref
                ref_pipeline = self.pipelines.get(item)
                if ref_pipeline:
                    for step in ref_pipeline.steps:
                        pipeline.add_step(step)
        
        return pipeline
    
    def create_pipelines(self) -> Dict[str, BasePipeline]:
        """
        Create all pipelines defined in config.
        
        Returns:
            Dictionary mapping pipeline names to BasePipeline objects
        """
        # First pass: Create pipelines that don't have references
        for name, pipeline_config in self.pipeline_defs.items():
            # Extract steps from new config format
            if isinstance(pipeline_config, dict) and "steps" in pipeline_config:
                steps_list = pipeline_config["steps"]
            else:
                steps_list = pipeline_config
                
            if all(not isinstance(item, dict) or "func" in item for item in steps_list):
                self.pipelines[name] = self._build_pipeline(name, pipeline_config)
        
        # Second pass: Create pipelines with references
        for name, pipeline_config in self.pipeline_defs.items():
            if name not in self.pipelines:
                self.pipelines[name] = self._build_pipeline(name, pipeline_config)
        
        return self.pipelines


def get_pipeline_steps() -> Dict[str, List[PipelineStep]]:
    """
    Get all pipeline steps defined in config.yaml.
    
    Returns:
        Dictionary mapping pipeline names to lists of steps
    """
    factory = PipelineFactory()
    pipelines = factory.create_pipelines()
    return {name: pipeline.steps for name, pipeline in pipelines.items()}

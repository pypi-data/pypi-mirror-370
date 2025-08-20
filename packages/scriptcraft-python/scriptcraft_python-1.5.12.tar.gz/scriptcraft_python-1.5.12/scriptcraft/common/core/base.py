"""
Base Classes Module

Provides a SINGLE, DRY base class for ALL tools.
Every tool follows the same pattern: Input → Process → Output + Logs

No artificial distinctions. No organizational cruft. Just functionality.
"""

import logging
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
import pandas as pd

from ..io import ensure_output_dir
from ..logging import log_and_print
from ..core.config import Config


class BaseTool(ABC):
    """
    Universal base class for ALL tools.
    
    Handles the complete pattern: Input → Process → Output + Logs
    No artificial distinctions between "processors", "analyzers", "comparers".
    """
    
    def __init__(self, name: str, description: str, supported_formats: Optional[List[str]] = None,
                 tool_name: Optional[str] = None, requires_dictionary: bool = False) -> None:
        """
        Initialize tool.
        
        Args:
            name: Tool name
            description: Tool description  
            supported_formats: List of supported file formats (e.g., ['.csv', '.xlsx'])
            tool_name: Tool name for configuration (defaults to name.lower().replace(' ', '_'))
            requires_dictionary: Whether this tool requires a dictionary file
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(name)
        self.supported_formats = supported_formats or ['.csv', '.xlsx', '.xls']
        self.requires_dictionary = requires_dictionary
        
        # Use provided tool_name or generate from name
        self.tool_name = tool_name or name.lower().replace(' ', '_')
        
        # Load configuration with standardized pattern
        self.config = self._load_configuration()
        self.default_output_dir = self._get_default_output_dir()
    
    def _load_configuration(self) -> Optional[Config]:
        """
        Load configuration with standardized fallback pattern.
        
        Returns:
            Config object or None if loading fails
        """
        try:
            if self.is_distributable_environment():
                # In distributable environment, use environment variables from config.bat
                config = Config._from_environment()
                self.log_message("📋 Configuration loaded from environment variables (distributable mode)")
                return config
            else:
                # In development environment, load from config.yaml
                config_path = "config.yaml"
                config = Config.from_yaml(config_path)
                self.log_message(f"📋 Configuration loaded from: {config_path}")
                return config
            
        except Exception as e:
            self.log_message(f"⚠️ Config loading failed, using defaults: {e}", level="warning")
            return None
    
    def _get_default_output_dir(self) -> str:
        """Get default output directory from config or use fallback."""
        if self.config:
            try:
                # Try to get workspace-specific output directory first
                workspace_config = self.config.get_workspace_config()
                if workspace_config and hasattr(workspace_config, 'paths'):
                    workspace_paths = workspace_config.paths
                    if isinstance(workspace_paths, dict) and 'output_dir' in workspace_paths:
                        return workspace_paths['output_dir']
                
                # Fallback to template config
                template_config = self.config.get_template_config()
                package_structure = template_config.get("package_structure", {})
                if isinstance(package_structure, dict):
                    default_dir = package_structure.get("default_output_dir", "data/output")
                    if isinstance(default_dir, str):
                        return default_dir
            except Exception:
                pass
        return "data/output"
    
    def get_tool_config(self) -> Dict[str, Any]:
        """Get tool-specific configuration."""
        if self.config:
            try:
                return self.config.get_tool_config(self.tool_name)
            except Exception:
                pass
        return {}
    
    # ===== LOGGING (DRY) =====
    
    def log_message(self, message: str, level: str = "info") -> None:
        """Log a message with emoji formatting."""
        log_and_print(message, level=level)
    
    def log_start(self) -> None:
        """Log tool start."""
        self.log_message(f"🚀 Starting {self.name}...")
    
    def log_completion(self, output_path: Optional[Path] = None) -> None:
        """Log successful completion."""
        if output_path:
            self.log_message(f"✅ {self.name} completed successfully: {output_path}")
        else:
            self.log_message(f"✅ {self.name} completed successfully")
    
    def log_error(self, error: Union[str, Exception]) -> None:
        """Log an error."""
        error_msg = str(error)
        self.log_message(f"❌ {self.name} error: {error_msg}", level="error")
    
    # ===== ENVIRONMENT DETECTION (DRY) =====
    
    @staticmethod
    def is_distributable_environment() -> bool:
        """Detect if we're running in a distributable environment."""
        current_dir = Path.cwd()
        
        # Check for distributable indicators
        distributable_indicators = [
            # Classic distributable structure
            current_dir.name == 'scripts',
            'distributable' in str(current_dir).lower(),
            
            # New PyPI-based structure indicators
            (current_dir / 'embed_py311').exists(),  # Embedded Python
            (current_dir / 'config.bat').exists(),   # Config bat file
            (current_dir / 'run.bat').exists(),      # Run script
            
            # Environment variable set by config.bat
            os.environ.get('TOOL_TO_SHIP') is not None,
            
            # Check if we're in a tool_distributable directory
            current_dir.name.endswith('_distributable')
        ]
        
        return any(distributable_indicators)
    
    def resolve_input_directory(self, input_dir: Optional[Union[str, Path]] = None, 
                               config: Optional[Any] = None) -> Path:
        """Resolve input directory path for both environments."""
        if input_dir:
            return Path(input_dir)
        
        if config and hasattr(config, 'paths') and hasattr(config.paths, 'input_dir'):
            return Path(config.paths.input_dir)
        
        # Environment-based defaults
        if self.is_distributable_environment():
            current_dir = Path.cwd()
            if current_dir.name == 'scripts':
                return current_dir.parent / "input"
            else:
                return current_dir / "input"
        else:
            return Path("input")
    
    def resolve_output_directory(self, output_dir: Optional[Union[str, Path]] = None) -> Path:
        """Resolve output directory path for both environments."""
        if output_dir:
            output_path = Path(output_dir)
        elif self.config:
            try:
                # Try to get workspace-specific output directory
                workspace_config = self.config.get_workspace_config()
                if workspace_config and hasattr(workspace_config, 'paths'):
                    workspace_paths = workspace_config.paths
                    if isinstance(workspace_paths, dict) and 'output_dir' in workspace_paths:
                        output_path = Path(workspace_paths['output_dir'])
                    else:
                        # Fallback to default
                        output_path = Path("data/output")
                else:
                    # Fallback to default
                    output_path = Path("data/output")
            except Exception:
                # Fallback to environment-based defaults
                if self.is_distributable_environment():
                    current_dir = Path.cwd()
                    if current_dir.name == 'scripts':
                        output_path = current_dir.parent / "output"
                    else:
                        output_path = current_dir / "output"
                else:
                    output_path = Path("data/output")
        else:
            # No config available, use environment-based defaults
            if self.is_distributable_environment():
                current_dir = Path.cwd()
                if current_dir.name == 'scripts':
                    output_path = current_dir.parent / "output"
                else:
                    output_path = current_dir / "output"
            else:
                output_path = Path("data/output")
        
        ensure_output_dir(output_path)
        return output_path
    
    # ===== FILE OPERATIONS (DRY) =====
    
    def validate_input_files(self, input_paths: List[Union[str, Path]], 
                            required_count: Optional[int] = None) -> bool:
        """Validate input files with standard checks."""
        if not input_paths:
            self.log_error("No input paths provided")
            return False
        
        if required_count and len(input_paths) < required_count:
            self.log_error(f"Need at least {required_count} input files, got {len(input_paths)}")
            return False
            
        for path in input_paths:
            path = Path(path)
            if not path.exists():
                self.log_error(f"Input file not found: {path}")
                return False
            
            if path.suffix.lower() not in [ext.lower() for ext in self.supported_formats]:
                self.log_error(f"Unsupported file type: {path.suffix}. Supported: {self.supported_formats}")
                return False
        
        return True
    
    def load_data_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Universal data file loader with format detection."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        if file_path.suffix.lower() not in [ext.lower() for ext in self.supported_formats]:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            self.log_message(f"📂 Loaded {file_path.name}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            self.log_error(f"Failed to load {file_path}: {e}")
            raise
    
    def save_data_file(self, data: pd.DataFrame, output_path: Union[str, Path], 
                      include_index: bool = False) -> Path:
        """Universal data file saver with format detection."""
        output_path = Path(output_path)
        ensure_output_dir(output_path.parent)
        
        try:
            if output_path.suffix.lower() == '.csv':
                data.to_csv(output_path, index=include_index)
            elif output_path.suffix.lower() in ['.xlsx', '.xls']:
                data.to_excel(output_path, index=include_index)
            else:
                # Default to CSV
                output_path = output_path.with_suffix('.csv')
                data.to_csv(output_path, index=include_index)
            
            self.log_message(f"💾 Saved to: {output_path}")
            self.log_message(f"📊 Output shape: {data.shape[0]} rows, {data.shape[1]} columns")
            return output_path
            
        except Exception as e:
            self.log_error(f"Failed to save {output_path}: {e}")
            raise
    
    def get_output_filename(self, input_path: Union[str, Path], 
                           suffix: Optional[str] = None,
                           extension: str = '.csv') -> str:
        """Generate output filename with standardized naming."""
        input_path = Path(input_path)
        base_name = input_path.stem
        
        if suffix:
            base_name = f"{base_name}_{suffix}"
        
        return f"{base_name}{extension}"
    
    # ===== EXECUTION PATTERNS (DRY) =====
    
    def run_with_error_handling(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute a function with standardized logging and error handling."""
        self.log_start()
        try:
            result = func(*args, **kwargs)
            self.log_completion()
            return result
        except Exception as e:
            self.log_error(e)
            raise
    
    def compare_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          compare_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Compare two dataframes and return comparison results."""
        comparison = {
            'shape_difference': (df1.shape != df2.shape),
            'df1_shape': df1.shape,
            'df2_shape': df2.shape,
            'column_differences': set(df1.columns) ^ set(df2.columns),
            'common_columns': set(df1.columns) & set(df2.columns)
        }
        
        if compare_columns:
            comparison['column_differences'] = set(compare_columns) ^ set(df1.columns) ^ set(df2.columns)
        
        return comparison
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data for the tool."""
        return True
    
    def process(self, data: Any) -> Any:
        """Process data (to be implemented by subclasses)."""
        return data
    
    def transform(self, domain: str, input_path: Union[str, Path], 
                 output_path: Union[str, Path], paths: Optional[Dict[str, Any]] = None) -> None:
        """Transform data from input to output."""
        data = self.load_data_file(input_path)
        processed_data = self.process(data)
        self.save_data_file(processed_data, output_path)
    
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool (to be implemented by subclasses)."""
        pass
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the tool."""
        return (f"{self.__class__.__name__}(name='{self.name}', "
                f"description='{self.description}', "
                f"supported_formats={self.supported_formats})")


# ===== LEGACY ALIASES FOR BACKWARD COMPATIBILITY =====
# These maintain compatibility during migration period

BaseComponent = BaseTool
BaseProcessor = BaseTool
BasePipelineStep = BaseTool
BaseEnhancement = BaseTool
DataAnalysisTool = BaseTool
DataComparisonTool = BaseTool
DataProcessorTool = BaseTool


# ===== UTILITY CLASSES (NOT BASE CLASSES) =====

class BaseMainRunner:
    """Base class for main runner functionality."""
    
    @staticmethod
    def setup_environment() -> None:
        """Set up the environment for running tools."""
        pass
    
    @staticmethod
    def import_tool(tool_name: str) -> Any:
        """Import a tool by name."""
        try:
            module = __import__(f"scriptcraft.tools.{tool_name}", fromlist=[tool_name])
            return getattr(module, tool_name)
        except ImportError as e:
            raise ImportError(f"Could not import tool {tool_name}: {e}")
    
    @classmethod
    def run(cls, tool_name: str, parse_args_func: Optional[Callable[[], Any]] = None) -> None:
        """Run a tool by name."""
        cls.setup_environment()
        tool_class = cls.import_tool(tool_name)
        
        if parse_args_func:
            args = parse_args_func()
            tool = tool_class()
            tool.run(**vars(args))
        else:
            tool = tool_class()
            tool.run() 
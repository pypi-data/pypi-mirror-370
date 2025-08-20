"""
Configuration management for the project.

This module provides configuration loading and management functionality.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass, field

from ..logging import log_and_print
from ..io.path_resolver import PathResolver, WorkspacePathResolver, create_path_resolver
try:
    from ..._version import get_version
except ImportError:
    def get_version():
        return "unknown"


# ===== CONVENIENCE FUNCTIONS =====

def load_config(path: Union[str, Path] = "config.yaml") -> 'Config':
    """Load configuration from YAML file."""
    return Config.from_yaml(path)

def get_config() -> 'Config':
    """Get configuration with default path."""
    return load_config()


# ===== CONFIGURATION CLASSES =====

@dataclass
class PathConfig:
    """Path configuration."""
    scripts_dir: Path = field(default_factory=lambda: Path("scripts"))
    common_dir: Path = field(default_factory=lambda: Path("scripts/common"))
    tools_dir: Path = field(default_factory=lambda: Path("scripts/tools"))
    templates_dir: Path = field(default_factory=lambda: Path("templates/distributable_template"))
    export_dir: Path = field(default_factory=lambda: Path("distributables"))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    input_dir: Path = field(default_factory=lambda: Path("input"))
    qc_output_dir: Path = field(default_factory=lambda: Path("qc_output"))

@dataclass
class LogConfig:
    """Logging configuration."""
    level: str = "INFO"
    verbose_mode: bool = True
    structured_logging: bool = True
    log_dir: str = "logs"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None  # Optional log file path

@dataclass
class FrameworkConfig:
    """Framework-level configuration."""
    version: str = field(default_factory=get_version)
    active_workspace: str = "data"
    workspace_base_path: str = "."
    available_workspaces: List[str] = field(default_factory=lambda: ["data"])
    packaging: Dict[str, Any] = field(default_factory=dict)
    paths: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkspaceConfig:
    """Workspace-specific configuration."""
    study_name: str = "HABS"
    default_pipeline: str = "test"
    log_level: str = "INFO"
    id_columns: List[str] = field(default_factory=lambda: ["Med_ID", "Visit_ID"])
    paths: Dict[str, Any] = field(default_factory=dict)
    domains: List[str] = field(default_factory=lambda: ["Clinical", "Biomarkers", "Genomics", "Imaging"])
    logging: Dict[str, Any] = field(default_factory=dict)
    template: Dict[str, Any] = field(default_factory=dict)
    dictionary_checker: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Config:
    """Configuration class for managing project settings."""
    
    # Framework configuration
    framework: FrameworkConfig = field(default_factory=FrameworkConfig)
    
    # Workspace configuration
    workspace: WorkspaceConfig = field(default_factory=WorkspaceConfig)
    
    # Shared configurations
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    pipelines: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tool_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Legacy compatibility fields (deprecated, use workspace.* instead)
    study_name: str = field(default="HABS", init=False)
    default_pipeline: str = field(default="test", init=False)
    log_level: str = field(default="INFO", init=False)
    id_columns: List[str] = field(default_factory=lambda: ["Med_ID", "Visit_ID"], init=False)
    paths: PathConfig = field(default_factory=PathConfig, init=False)
    domains: List[str] = field(default_factory=list, init=False)
    dictionary_checker: Dict[str, Any] = field(default_factory=dict, init=False)
    logging: LogConfig = field(default_factory=LogConfig, init=False)
    template: Dict[str, Any] = field(default_factory=dict, init=False)
    
    # Project configuration
    project_name: str = "Release Workspace"
    version: str = field(default_factory=get_version)
    
    # Workspace context (not serialized, set during loading)
    workspace_root: Optional[Path] = field(default=None, init=False)
    
    # Path resolver (dependency injection)
    _path_resolver: Optional[PathResolver] = field(default=None, init=False)
    
    def __post_init__(self):
        """Set up legacy compatibility fields after initialization."""
        # Legacy compatibility - map workspace config to old fields
        self.study_name = self.workspace.study_name
        self.default_pipeline = self.workspace.default_pipeline
        self.log_level = self.workspace.log_level
        self.id_columns = self.workspace.id_columns
        self.domains = self.workspace.domains
        self.dictionary_checker = self.workspace.dictionary_checker
        self.template = self.workspace.template
        
        # Convert workspace paths to PathConfig for legacy compatibility
        if self.workspace.paths:
            self.paths = PathConfig(**self.workspace.paths)
        
        # Convert workspace logging to LogConfig for legacy compatibility
        if self.workspace.logging:
            self.logging = LogConfig(**self.workspace.logging)
    
    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> 'Config':
        """Load configuration from a YAML file with unified structure support."""
        config_path = Path(config_path)
        
        if config_path.exists():
            # Load from YAML file
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Handle unified config structure
            if 'framework' in config_data:
                # This is a unified config (new structure)
                return cls._load_unified_config(config_data, config_path)
            else:
                # This is a legacy config (old structure)
                return cls._load_legacy_config(config_data, config_path)
        else:
            # Fallback to environment variables (distributable environment)
            log_and_print(f"Config file not found: {config_path}", level="warning")
            log_and_print("📦 No config.yaml found. Using config.bat environment variables.", level="info")
            return cls._from_environment()
    
    @classmethod
    def _load_unified_config(cls, config_data: Dict[str, Any], config_path: Path) -> 'Config':
        """Load unified configuration with framework, workspace, and environment support."""
        # Extract framework configuration
        framework_data = config_data.get('framework', {})
        framework_config = FrameworkConfig(**framework_data)
        
        # Get active workspace
        active_workspace = framework_config.active_workspace
        
        # Extract workspace configuration
        workspaces_data = config_data.get('workspaces', {})
        workspace_data = workspaces_data.get(active_workspace, {})
        workspace_config = WorkspaceConfig(**workspace_data)
        
        # Apply environment-specific overrides
        environment = cls._detect_environment()
        environments_data = config_data.get('environments', {})
        env_data = environments_data.get(environment, {})
        
        # Merge environment overrides into workspace config
        if env_data:
            workspace_config = cls._merge_configs(workspace_config, env_data)
                
        # Extract shared configurations
        tools = config_data.get('tools', {})
        pipelines = config_data.get('pipelines', {})
        environments = config_data.get('environments', {})
        tool_configs = config_data.get('tool_configs', {})
                
        # Create config instance
        config = cls(
            framework=framework_config,
            workspace=workspace_config,
            tools=tools,
            pipelines=pipelines,
            environments=environments,
            tool_configs=tool_configs
        )
            
        # Set workspace root based on config file location
        config.workspace_root = config_path.parent.resolve()
            
        # Create path resolver with dependency injection
        config._path_resolver = WorkspacePathResolver(config.workspace_root)
            
        return config
    
    @classmethod
    def _load_legacy_config(cls, config_data: Dict[str, Any], config_path: Path) -> 'Config':
        """Load legacy configuration (backward compatibility)."""
        # Handle legacy framework config (has active_workspace, packaging, etc.)
        if 'active_workspace' in config_data:
            # This is a legacy framework config
            framework_config = FrameworkConfig(
                active_workspace=config_data.get('active_workspace', 'data'),
                workspace_base_path=config_data.get('workspace_base_path', '.'),
                available_workspaces=config_data.get('workspaces', ['data']),
                packaging=config_data.get('packaging', {}),
                paths=config_data.get('paths', {})
            )
            
            # Create default workspace config
            workspace_config = WorkspaceConfig()
            
            # Extract tools and pipelines
            tools = config_data.get('tools', {})
            pipelines = config_data.get('pipelines', {})
            tool_configs = config_data.get('tool_configs', {})
            
            config = cls(
                framework=framework_config,
                workspace=workspace_config,
                tools=tools,
                pipelines=pipelines,
                tool_configs=tool_configs
            )
        else:
            # This is a legacy workspace config
            framework_config = FrameworkConfig()
            workspace_config = WorkspaceConfig(**config_data)
            
            config = cls(
                framework=framework_config,
                workspace=workspace_config,
                tools=config_data.get('tools', {}),
                pipelines=config_data.get('pipelines', {}),
                tool_configs=config_data.get('tool_configs', {})
            )
        
        # Set workspace root and path resolver
        config.workspace_root = config_path.parent.resolve()
        config._path_resolver = WorkspacePathResolver(config.workspace_root)
        
        return config
    
    @classmethod
    def _detect_environment(cls) -> str:
        """Detect the current environment."""
        # Check for environment variables
        if os.environ.get('SCRIPTCRAFT_ENV'):
            return os.environ.get('SCRIPTCRAFT_ENV')
        
        # Check for development indicators
        if os.path.exists('config.yaml') and os.path.exists('implementations/'):
            return 'development'
        
        # Check for distributable indicators
        current_dir = Path('.')
        distributable_indicators = [
            (current_dir / 'embed_py311').exists(),  # Embedded Python
            (current_dir / 'config.bat').exists(),   # Config bat file
            (current_dir / 'run.bat').exists(),      # Run script
            os.environ.get('TOOL_TO_SHIP') is not None,  # Environment variable
            current_dir.name.endswith('_distributable')  # Directory name
        ]
        
        if any(distributable_indicators):
            return 'production'
        
        # Default to development
        return 'development'
    
    @classmethod
    def _merge_configs(cls, base_config: WorkspaceConfig, override_data: Dict[str, Any]) -> WorkspaceConfig:
        """Merge environment overrides into workspace config."""
        # Create a copy of the base config
        merged_data = {
            'study_name': base_config.study_name,
            'default_pipeline': base_config.default_pipeline,
            'log_level': base_config.log_level,
            'id_columns': base_config.id_columns,
            'paths': base_config.paths,
            'domains': base_config.domains,
            'logging': base_config.logging,
            'template': base_config.template,
            'dictionary_checker': base_config.dictionary_checker
        }
        
        # Apply overrides
        for key, value in override_data.items():
            if key in merged_data:
                merged_data[key] = value
        
        return WorkspaceConfig(**merged_data)
    
    @classmethod
    def _from_environment(cls) -> 'Config':
        """Create configuration from environment variables (distributable mode)."""
        import os
        
        # Get tool name from environment (config.bat sets TOOL_TO_SHIP)
        tool_name = os.environ.get("TOOL_TO_SHIP", os.environ.get("TOOL_NAME", "unknown_tool"))
        
        # Build generic tool configuration from environment variables
        tool_config = {
            "tool_name": tool_name,
            "description": os.environ.get("TOOL_DESCRIPTION", f"🔧 {tool_name.replace('_', ' ').title()}"),
            "entry_command": os.environ.get("ENTRY_COMMAND", "main.py"),
            "packages": os.environ.get("TOOL_PACKAGES", "").split() if os.environ.get("TOOL_PACKAGES") else []
        }
        
        # Add tool-specific settings
        if tool_name == "rhq_form_autofiller":
            tool_config.update({
                "url_template": os.environ.get("URL_TEMPLATE", ""),
                "browser_timeout": int(os.environ.get("RHQ_BROWSER_TIMEOUT", "60")),
                "form_wait_time": int(os.environ.get("RHQ_FORM_WAIT_TIME", "10")),
                "auto_login": os.environ.get("RHQ_AUTO_LOGIN", "true").lower() == "true"
            })
        
        # Create default configuration with environment-based tools config
        config = cls()
        config.tools[tool_name] = tool_config
        
        # Set workspace root to current directory for distributables
        config.workspace_root = Path.cwd()
        
        log_and_print(f"✅ Configuration loaded from environment for tool: {tool_name}", level="info")
        return config
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool."""
        return self.tools.get(tool_name, {})
    
    def get_pipeline_step(self, step_name: str) -> Dict[str, Any]:
        """Get configuration for a specific pipeline step."""
        return self.pipelines.get(step_name, {})
    
    def get_logging_config(self) -> LogConfig:
        """Get logging configuration."""
        return self.logging
    
    def get_project_config(self) -> Dict[str, Any]:
        """Get project configuration."""
        return {
            'project_name': self.project_name,
            'version': self.version
        }
    
    def get_template_config(self) -> Dict[str, Any]:
        """Get template configuration."""
        return self.template
    
    def get_workspace_root(self) -> Path:
        """Get the workspace root directory."""
        if self.workspace_root:
            return self.workspace_root
        else:
            # Fallback to current directory for environment-based configs
            return Path.cwd()
    
    def get_path_resolver(self) -> PathResolver:
        """
        Get the path resolver for this configuration.
        
        Returns:
            PathResolver instance for workspace-aware path resolution
        """
        if not self._path_resolver:
            # Create path resolver on demand for environment-based configs
            self._path_resolver = create_path_resolver(self.get_workspace_root())
        
        return self._path_resolver
    
    def get_framework_config(self) -> FrameworkConfig:
        """Get framework configuration."""
        return self.framework
    
    def get_workspace_config(self) -> WorkspaceConfig:
        """Get workspace configuration."""
        return self.workspace
    
    def get_active_workspace(self) -> str:
        """Get the active workspace name."""
        return self.framework.active_workspace
    
    def get_environment(self) -> str:
        """Get the current environment."""
        return self._detect_environment()
    
    def discover_and_merge_tools(self) -> None:
        """Discover available tools and merge with existing config tools."""
        try:
            # Import tool discovery from tools package
            from ...tools import get_available_tools, discover_tool_metadata
            
            # Get discovered tools
            discovered_tools = get_available_tools()
            
            # Create tool entries for discovered tools not in config
            for tool_name, tool_instance in discovered_tools.items():
                if tool_name not in self.tools:
                    # Get tool metadata for description
                    metadata = discover_tool_metadata(tool_name)
                    if metadata:
                        description = metadata.description
                    else:
                        description = f"🔧 {tool_name.replace('_', ' ').title()}"
                    
                    self.tools[tool_name] = {
                        'description': description,
                        'tool_name': tool_name,
                        'import_path': f"scriptcraft.tools.{tool_name}"
                    }
                    
        except Exception as e:
            log_and_print(f"⚠️ Could not discover tools: {e}", level="warning")
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Basic validation - check that required fields are present
        if not self.workspace.study_name:
            log_and_print("Study name is required", level="error")
            return False
        
        if not self.workspace.domains:
            log_and_print("At least one domain must be configured", level="warning")
        
        return True


 
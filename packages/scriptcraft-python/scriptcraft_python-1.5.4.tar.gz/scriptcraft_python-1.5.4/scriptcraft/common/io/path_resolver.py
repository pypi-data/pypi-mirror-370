"""
Path Resolution Module

Provides workspace-aware path resolution following dependency injection principles.
This module separates path resolution logic from configuration and business logic.
"""

from pathlib import Path
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod


class PathResolver(ABC):
    """Abstract base class for path resolution strategies."""
    
    @abstractmethod
    def get_workspace_root(self) -> Path:
        """Get the workspace root directory."""
        pass
    
    @abstractmethod
    def get_input_dir(self) -> Path:
        """Get the input directory."""
        pass
    
    @abstractmethod
    def get_output_dir(self) -> Path:
        """Get the output directory."""
        pass
    
    @abstractmethod
    def get_logs_dir(self) -> Path:
        """Get the logs directory."""
        pass
    
    @abstractmethod
    def get_domains_dir(self) -> Path:
        """Get the domains directory."""
        pass
    
    @abstractmethod
    def get_domain_paths(self, domain: str) -> Dict[str, Path]:
        """Get all paths for a specific domain."""
        pass


class WorkspacePathResolver(PathResolver):
    """Workspace-aware path resolver for multi-workspace architecture."""
    
    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize with workspace root directory.
        
        Args:
            workspace_root: Path to the workspace root directory
        """
        self.workspace_root = Path(workspace_root).resolve()
        
        # Validate workspace structure
        self._validate_workspace()
    
    def _validate_workspace(self) -> None:
        """Validate that the workspace has the expected structure."""
        required_dirs = ['input', 'output', 'logs']
        for dir_name in required_dirs:
            dir_path = self.workspace_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_workspace_root(self) -> Path:
        """Get the workspace root directory."""
        return self.workspace_root
    
    def get_input_dir(self) -> Path:
        """Get the input directory."""
        return self.workspace_root / "input"
    
    def get_output_dir(self) -> Path:
        """Get the output directory."""
        return self.workspace_root / "output"
    
    def get_logs_dir(self) -> Path:
        """Get the logs directory."""
        return self.workspace_root / "logs"
    
    def get_domains_dir(self) -> Path:
        """Get the domains directory."""
        return self.workspace_root / "domains"
    
    def get_qc_output_dir(self) -> Path:
        """Get the QC output directory."""
        return self.workspace_root / "qc_output"
    
    def get_domain_paths(self, domain: str) -> Dict[str, Path]:
        """
        Get all paths for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary mapping path keys to Path objects
        """
        domain_base = self.get_domains_dir() / domain
        
        return {
            "root": domain_base,
            "raw_data": domain_base / "raw_data",
            "processed_data": domain_base / "processed_data",
            "merged_data": domain_base / "merged_data",
            "old_data": domain_base / "old_data",
            "dictionary": domain_base / "dictionary",
            "qc_output": domain_base / "qc_output",
            "qc_logs": domain_base / "qc_logs"
        }
    
    def get_all_domain_paths(self) -> Dict[str, Dict[str, Path]]:
        """
        Get paths for all domains in the workspace.
        
        Returns:
            Dictionary mapping domain names to their path dictionaries
        """
        domain_paths = {}
        domains_dir = self.get_domains_dir()
        
        if domains_dir.exists():
            for domain_dir in domains_dir.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    domain_name = domain_dir.name
                    domain_paths[domain_name] = self.get_domain_paths(domain_name)
        
        return domain_paths
    
    def resolve_input_path(self, input_key: str, domain: Optional[str] = None) -> Optional[Path]:
        """
        Resolve an input path based on input key and optional domain.
        
        Args:
            input_key: Key identifying the type of input ('raw_data', 'rhq_inputs', etc.)
            domain: Optional domain name for domain-specific inputs
            
        Returns:
            Resolved Path object or None if not found
        """
        # Global inputs (workspace-level)
        global_inputs = {
            'rhq_inputs': self.get_input_dir(),
            'global_data': self.get_input_dir(),
        }
        
        if input_key in global_inputs:
            return global_inputs[input_key]
        
        # Domain-specific inputs
        if domain:
            domain_paths = self.get_domain_paths(domain)
            return domain_paths.get(input_key)
        
        return None
    
    def resolve_output_path(self, output_filename: Optional[str] = None, domain: Optional[str] = None) -> Path:
        """
        Resolve an output path.
        
        Args:
            output_filename: Optional specific output filename
            domain: Optional domain name for domain-specific outputs
            
        Returns:
            Resolved output Path object
        """
        if domain:
            domain_paths = self.get_domain_paths(domain)
            base_output = domain_paths["qc_output"]
        else:
            base_output = self.get_output_dir()
        
        if output_filename:
            return base_output / output_filename
        else:
            return base_output


class LegacyPathResolver(PathResolver):
    """Legacy path resolver for backward compatibility with old project structure."""
    
    def __init__(self, project_root: Path) -> None:
        """
        Initialize with legacy project root.
        
        Args:
            project_root: Path to the legacy project root directory
        """
        self.project_root = Path(project_root).resolve()
    
    def get_workspace_root(self) -> Path:
        """Get the workspace root (same as project root in legacy mode)."""
        return self.project_root
    
    def get_input_dir(self) -> Path:
        """Get the input directory."""
        return self.project_root / "input"
    
    def get_output_dir(self) -> Path:
        """Get the output directory."""
        return self.project_root / "output"
    
    def get_logs_dir(self) -> Path:
        """Get the logs directory."""
        return self.project_root / "logs"
    
    def get_domains_dir(self) -> Path:
        """Get the domains directory."""
        return self.project_root / "domains"
    
    def get_domain_paths(self, domain: str) -> Dict[str, Path]:
        """Get all paths for a specific domain in legacy structure."""
        domain_base = self.get_domains_dir() / domain
        
        return {
            "root": domain_base,
            "raw_data": domain_base / "raw_data",
            "processed_data": domain_base / "processed_data",
            "merged_data": domain_base / "merged_data",
            "old_data": domain_base / "old_data",
            "dictionary": domain_base / "dictionary",
            "qc_output": domain_base / "qc_output",
            "qc_logs": domain_base / "qc_logs"
        }


def create_path_resolver(workspace_root: Optional[Path] = None) -> PathResolver:
    """
    Factory function to create the appropriate path resolver.
    
    Args:
        workspace_root: Optional workspace root path. If None, detects automatically.
        
    Returns:
        PathResolver instance
    """
    if workspace_root:
        return WorkspacePathResolver(workspace_root)
    
    # Auto-detection logic
    current_dir = Path.cwd()
    
    # Check if we're in a workspace directory (has config.yaml, input/, output/, domains/)
    workspace_markers = ['config.yaml', 'input', 'output', 'domains']
    if all((current_dir / marker).exists() for marker in workspace_markers):
        return WorkspacePathResolver(current_dir)
    
    # Check for workspace parent directory
    for parent in current_dir.parents:
        if (parent / "workspaces").exists():
            # This looks like the framework root, use legacy resolver
            return LegacyPathResolver(parent)
    
    # Fallback to current directory as workspace
    return WorkspacePathResolver(current_dir) 
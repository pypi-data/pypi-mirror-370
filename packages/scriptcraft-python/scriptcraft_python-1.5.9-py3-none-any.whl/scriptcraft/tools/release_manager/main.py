#!/usr/bin/env python3
"""
🚀 Release Manager Tool for ScriptCraft

Automated release management for Python packages with plugin-based workflows.
Supports version bumping, PyPI uploading, git operations, and custom release processes.

Usage:
    Development: python -m scriptcraft.tools.release_manager.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# === Environment Detection & Import Setup ===
# Import the environment detection module
from .env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports - use cu pattern for consistency
    import common as cu
else:
    # Development imports - use cu pattern for consistency
    import scriptcraft.common as cu

# Import plugins
from .plugins import get_plugin, list_plugins, PluginRegistry


class ReleaseManager(cu.BaseTool):
    """Tool for automated release management with plugin-based workflows."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Release Manager",
            description="🚀 Automated release management for Python packages with plugin-based workflows",
            tool_name="release_manager"
        )
        
        # Initialize plugin registry
        self.plugin_registry = PluginRegistry()
        self._load_plugins()
    
    def _load_plugins(self):
        """Load available release plugins."""
        try:
            # Load built-in plugins
            from .plugins import load_builtin_plugins
            load_builtin_plugins(self.plugin_registry)
            
            # Load custom plugins if any
            self._load_custom_plugins()
            
        except Exception as e:
            cu.log_and_print(f"⚠️ Could not load plugins: {e}", level="warning")
    
    def _load_custom_plugins(self):
        """Load custom plugins from plugins directory."""
        plugins_dir = Path(__file__).parent / "plugins"
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name.startswith("custom_") and plugin_file.name != "__init__.py":
                    try:
                        # Load custom plugin
                        plugin_name = plugin_file.stem.replace("custom_", "")
                        cu.log_and_print(f"🔌 Loading custom plugin: {plugin_name}")
                    except Exception as e:
                        cu.log_and_print(f"⚠️ Failed to load custom plugin {plugin_file.name}: {e}", level="warning")
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """
        Run the release management process.
        
        Args:
            mode: Release mode (e.g., 'python_package', 'workspace', 'custom')
            input_paths: List containing paths to files/directories to release
            output_dir: Directory to save release artifacts
            domain: Optional domain context
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - version_type: Type of version bump (major, minor, patch)
                - auto_push: Whether to push to remote automatically
                - force: Force release even if no changes
                - custom_message: Custom commit message
                - skip_pypi: Skip PyPI upload
                - plugin_config: Plugin-specific configuration
        """
        self.log_start()
        
        try:
            # Set default mode if not specified
            if not mode:
                mode = "python_package"
            
            # Get plugin function
            plugin_func = self.plugin_registry.get_plugin(mode)
            
            if not plugin_func:
                available_modes = self.plugin_registry.list_plugins()
                raise ValueError(f"❌ Unknown mode '{mode}'. Available modes: {available_modes}")
            
            # Run the plugin
            cu.log_and_print(f"🔧 Running {mode} release mode...")
            plugin_func(
                input_paths=input_paths or [],
                output_dir=output_dir or self.default_output_dir,
                domain=domain,
                **kwargs
            )
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Release failed: {e}")
            raise
    
    def list_available_modes(self) -> List[str]:
        """List all available release modes."""
        return self.plugin_registry.list_plugins()
    
    def get_plugin_info(self, mode: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin."""
        return self.plugin_registry.get_plugin_info(mode)


def run_command(command: str, description: str, cwd: Optional[Path] = None) -> Optional[str]:
    """Run a command and handle errors."""
    cu.log_and_print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, 
            check=True, encoding='utf-8', errors='replace', cwd=cwd
        )
        cu.log_and_print(f"✅ {description} completed")
        return result.stdout.strip() if result.stdout else ""
    except subprocess.CalledProcessError as e:
        cu.log_and_print(f"❌ {description} failed: {e}", level="error")
        if e.stderr:
            # Handle potential encoding issues in stderr
            try:
                error_output = e.stderr
            except UnicodeDecodeError:
                error_output = e.stderr.encode('utf-8', errors='replace').decode('utf-8')
            cu.log_and_print(f"Error output: {error_output}", level="error")
        return None
    except UnicodeDecodeError as e:
        cu.log_and_print(f"❌ {description} failed due to encoding issue: {e}", level="error")
        return None


def get_current_version() -> Optional[str]:
    """Get current version from _version.py file."""
    try:
        version_file = Path("scriptcraft/_version.py")
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'__version__ = "([^"]+)"', content)
            if match:
                return match.group(1)
        cu.log_and_print("❌ Could not find version in _version.py", level="error")
        return None
    except FileNotFoundError:
        cu.log_and_print("❌ _version.py file not found", level="error")
        return None


def bump_version(current_version: str, version_type: str) -> Optional[str]:
    """Bump version number based on type."""
    major, minor, patch = map(int, current_version.split('.'))
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        cu.log_and_print("❌ Invalid version type. Use: major, minor, or patch", level="error")
        return None
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str) -> bool:
    """Update the _version.py file."""
    try:
        version_file = Path("scriptcraft/_version.py")
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace version line
        updated_content = re.sub(
            r'__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content
        )
        
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        cu.log_and_print(f"✅ Updated _version.py to {new_version}")
        return True
    except Exception as e:
        cu.log_and_print(f"❌ Error updating _version.py: {e}", level="error")
        return False


def get_commit_message(new_version: str, version_type: str) -> str:
    """Generate a commit message based on version type."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if version_type == "major":
        return f"🚀 Major Release: ScriptCraft Python v{new_version}\n\nBreaking changes and major new features"
    elif version_type == "minor":
        return f"✨ Feature Release: ScriptCraft Python v{new_version}\n\nNew features and improvements"
    else:  # patch
        return f"🐛 Bug Fix Release: ScriptCraft Python v{new_version}\n\nBug fixes and minor improvements"


def main():
    """Main entry point for the release manager tool."""
    if len(sys.argv) < 2:
        print("🎯 ScriptCraft Release Manager Tool")
        print("Usage: python -m scriptcraft.tools.release_manager.main <mode> [args]")
        print("\nAvailable modes:")
        
        # Create tool instance to list modes
        tool = ReleaseManager()
        for mode in tool.list_available_modes():
            plugin_info = tool.get_plugin_info(mode)
            if plugin_info:
                print(f"  {mode}: {plugin_info.get('description', 'No description')}")
            else:
                print(f"  {mode}")
        
        print("\nExample: python -m scriptcraft.tools.release_manager.main python_package minor")
        print("Example: python -m scriptcraft.tools.release_manager.main workspace --push")
        print("\nFor detailed help on a specific mode:")
        print("  python -m scriptcraft.tools.release_manager.main <mode> --help")
        return
    
    mode = sys.argv[1].lower()
    
    # Handle help flags
    if mode in ['--help', '-h', 'help']:
        print("🎯 ScriptCraft Release Manager Tool")
        print("Usage: python -m scriptcraft.tools.release_manager.main <mode> [args]")
        print("\nAvailable modes:")
        
        # Create tool instance to list modes
        tool = ReleaseManager()
        for mode in tool.list_available_modes():
            plugin_info = tool.get_plugin_info(mode)
            if plugin_info:
                print(f"  {mode}: {plugin_info.get('description', 'No description')}")
            else:
                print(f"  {mode}")
        
        print("\nExample: python -m scriptcraft.tools.release_manager.main python_package minor")
        print("Example: python -m scriptcraft.tools.release_manager.main workspace --push")
        print("\nFor detailed help on a specific mode:")
        print("  python -m scriptcraft.tools.release_manager.main <mode> --help")
        return
    
    # Create and run the tool
    tool = ReleaseManager()
    
    # Parse remaining arguments for the specific mode
    remaining_args = sys.argv[2:]
    
    # Convert args to kwargs for the tool
    kwargs = {}
    i = 0
    while i < len(remaining_args):
        arg = remaining_args[i]
        if arg.startswith('--'):
            if i + 1 < len(remaining_args) and not remaining_args[i + 1].startswith('--'):
                kwargs[arg[2:].replace('-', '_')] = remaining_args[i + 1]
                i += 2
            else:
                kwargs[arg[2:].replace('-', '_')] = True
                i += 1
        else:
            # Positional arguments
            if 'input_paths' not in kwargs:
                kwargs['input_paths'] = []
            kwargs['input_paths'].append(arg)
            i += 1
    
    # Add mode to kwargs
    kwargs['mode'] = mode
    
    # Convert string values to appropriate types
    if 'version_type' in kwargs:
        kwargs['version_type'] = str(kwargs['version_type'])
    if 'auto_push' in kwargs:
        kwargs['auto_push'] = True
    if 'force' in kwargs:
        kwargs['force'] = True
    if 'skip_pypi' in kwargs:
        kwargs['skip_pypi'] = True
    
    # Run the tool
    tool.run(**kwargs)


if __name__ == "__main__":
    main()

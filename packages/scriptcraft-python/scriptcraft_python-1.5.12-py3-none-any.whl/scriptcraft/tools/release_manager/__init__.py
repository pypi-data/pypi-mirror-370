"""
🚀 Release Manager Tool

Automated release management for Python packages with plugin-based workflows.
Supports version bumping, PyPI uploading, git operations, and custom release processes.

Features:
- 🚀 Automated version management
- 📦 PyPI package building and uploading
- 🔄 Git operations and tagging
- 🔌 Plugin-based architecture
- 📊 Release workflow automation
- ⚙️ Customizable release processes

Author: ScriptCraft Team
"""

# === EXPLICIT IMPORTS TO AVOID CIRCULAR IMPORT ===
# Import main classes without wildcard to prevent circular import when running as module
from .main import ReleaseManager
from .plugins import PluginRegistry

# === PUBLIC API ===
__all__ = [
    'ReleaseManager',
    'PluginRegistry'
]

# Tool metadata
__description__ = "🚀 Automated release management for Python packages with plugin-based workflows"
__tags__ = ["release", "versioning", "pypi", "git", "automation", "packaging", "plugins"]
__data_types__ = ["python", "package", "version", "workspace"]
__domains__ = ["development", "deployment", "distribution", "automation"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "standalone"

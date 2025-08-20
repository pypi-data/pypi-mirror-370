# data_content_comparer/plugins/__init__.py

"""
Plugin registration for data content comparer modes.
"""

from .standard_mode import run_mode as standard_mode
from .rhq_mode import run_mode as rhq_mode
from .domain_old_vs_new_mode import run_mode as domain_mode
from .release_consistency_mode import run_mode as release_consistency_mode

# Plugin registry
PLUGINS = {
    "standard": standard_mode,
    "rhq": rhq_mode,
    "domain": domain_mode,
    "release_consistency": release_consistency_mode,
    "release": release_consistency_mode,  # Alias for convenience
}

def get_plugin(mode: str):
    """Get plugin function by mode name."""
    return PLUGINS.get(mode, standard_mode)

def list_plugins():
    """List available plugins."""
    return list(PLUGINS.keys())

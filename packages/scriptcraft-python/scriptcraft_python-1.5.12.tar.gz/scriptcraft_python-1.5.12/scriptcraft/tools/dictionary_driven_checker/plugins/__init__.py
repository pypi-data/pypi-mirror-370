# dictionary_driven_checker/plugins/__init__.py

"""Plugin system for dictionary-driven validation."""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from scriptcraft.common.plugins import registry

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'registry', '_load_plugins'
# ]

# Import plugins after registry is created to avoid circular dependency
def _load_plugins() -> None:
    """Load all plugins after registry is initialized."""
    try:
        from . import validators  # Load the main validators file
        # Individual plugin files are kept for reference but not loaded
        # from . import numeric_plugin
        # from . import text_plugin  
        # from . import date_plugin
    except ImportError as e:
        # Plugins are optional - if they fail to import, continue
        # Silently continue - plugins are optional
        pass

# Load plugins immediately
_load_plugins()

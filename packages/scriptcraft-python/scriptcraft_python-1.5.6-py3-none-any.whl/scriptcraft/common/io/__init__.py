"""
I/O package for the project.

This package provides input/output operations organized into:
- data_loading: Data loading operations
- directory_ops: Directory management
- file_ops: Basic file operations
- paths: Path constants and configuration
- path_resolver: Path resolution utilities
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .data_loading import *
from .directory_ops import *
from .file_ops import *
from .paths import *
from .path_resolver import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     # Data loading
#     'load_data', 'load_csv', 'load_excel', 'load_json',
#     # Directory operations
#     'ensure_output_dir', 'create_directory', 'list_files',
#     # File operations
#     'save_data', 'save_csv', 'save_excel', 'save_json',
#     # Path utilities
#     'get_project_root', 'resolve_path', 'get_domain_paths'
# ] 
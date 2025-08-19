"""
scripts/common/paths_and_constants.py

📁 Centralized constants and configuration for the project.
Includes folder structure, domain-level file patterns, alias mappings,
missing value handling, and project metadata.
"""

import os
import sys
from enum import Enum
from pathlib import Path
from typing import List, Dict, FrozenSet, Any, Optional
import yaml

# ==== 📄 Configuration Loading ====

CONFIG_PATH_YAML = Path(__file__).resolve().parents[3] / "config.yaml"
CONFIG_PATH_BAT = Path(__file__).resolve().parents[3] / "config.bat"
_CONFIG = {}

if CONFIG_PATH_YAML.exists():
    try:
        with open(CONFIG_PATH_YAML, "r", encoding="utf-8") as f:
            _CONFIG = yaml.safe_load(f)
        print(f"📄 Loaded config.yaml from {CONFIG_PATH_YAML}")
    except Exception as e:
        print(f"⚠️ Failed to load config.yaml from {CONFIG_PATH_YAML}. Reason: {e}", file=sys.stderr)
        _CONFIG = {}
elif CONFIG_PATH_BAT.exists():
    # Set UTF-8 encoding for console output
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print(f"📦 No config.yaml found. Using config.bat environment variables.")
    _CONFIG = {
        "study_name": os.environ.get("STUDY_NAME", "DEFAULT_STUDY"),
        "id_columns": os.environ.get("ID_COLUMNS", "Med_ID,Visit_ID").split(","),
        "output_dir": os.environ.get("OUTPUT_DIR", "output"),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
        "domains": os.environ.get("DOMAINS", "").split(","),
        "folder_structure": {}
    }
else:
    # Check if we're in a workspace environment before warning
    workspaces_dir = Path(__file__).resolve().parents[3] / "workspaces"
    has_workspaces = workspaces_dir.exists() and any(workspaces_dir.iterdir())
    
    if not has_workspaces:
        print(f"⚠️ No config.yaml or config.bat found. Using fallback hardcoded defaults.", file=sys.stderr)
    
    _CONFIG = {
        "study_name": "DEFAULT_STUDY",
        "id_columns": ["Med_ID", "Visit_ID"],
        "output_dir": "output",
        "log_level": "INFO",
        "domains": [],
        "folder_structure": {}
    }


def get_legacy_config(key: Any = None, default: Any = None) -> Any:
    """
    Get configuration values from the loaded YAML config (legacy function).
    
    Args:
        key: Optional key to retrieve specific config value
        default: Default value if key not found
    
    Returns:
        The entire config dict if no key provided, or the value for the specific key
    """
    if key is None:
        return _CONFIG
    return _CONFIG.get(key, default)


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root directory
    """
    # Start from the current file and go up to find the project root
    current_path = Path(__file__).resolve()
    
    # Look for config.yaml or other project markers
    for parent in current_path.parents:
        if (parent / "config.yaml").exists() or (parent / "run_all.py").exists():
            return parent
    
    # Fallback: assume we're in scripts/common/io, so go up 3 levels
    return current_path.parents[2]


def get_domain_paths(project_root: Path) -> Dict[str, Dict[str, Path]]:
    """
    Get paths for all domains based on the project structure.
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        Dictionary mapping domain names to their path dictionaries
    """
    domain_paths: Dict[str, Dict[str, Path]] = {}
    domains_dir = project_root / "domains"
    
    if not domains_dir.exists():
        return domain_paths
    
    for domain_dir in domains_dir.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
            domain_name = domain_dir.name
            domain_paths[domain_name] = {
                "root": domain_dir,
                "raw_data": domain_dir / "raw_data",
                "processed_data": domain_dir / "processed_data", 
                "merged_data": domain_dir / "merged_data",
                "old_data": domain_dir / "old_data",
                "dictionary": domain_dir / "dictionary",
                "qc_output": domain_dir / "qc_output",
                "qc_logs": domain_dir / "qc_logs"
            }
    
    return domain_paths


def get_domain_output_path(domain_paths: Dict[str, Path], filename: Optional[str] = None, suffix: Optional[str] = None) -> Path:
    """
    Get the output path for a domain using domain path dictionary.
    
    Args:
        domain_paths: Dictionary of domain paths
        filename: Optional filename to append
        suffix: Optional suffix to add to filename
        
    Returns:
        Path to the output file or directory
    """
    output_dir = domain_paths.get("qc_output", Path("output"))
    
    if filename:
        if suffix:
            name_parts = filename.split('.')
            if len(name_parts) > 1:
                base_name = '.'.join(name_parts[:-1])
                extension = name_parts[-1]
                filename = f"{base_name}_{suffix}.{extension}"
            else:
                filename = f"{filename}_{suffix}"
        return output_dir / filename
    
    return output_dir


# ==== 📌 Project Configuration Constants ====

STUDY_NAME: str = _CONFIG.get("study_name", "DEFAULT_STUDY")
ID_COLUMNS: List[str] = _CONFIG.get("id_columns", ["Med_ID", "Visit_ID"])
OUTPUT_DIR: Path = Path(_CONFIG.get("output_dir", "output"))
LOG_LEVEL: str = _CONFIG.get("log_level", "INFO")
DOMAINS: List[str] = _CONFIG.get("domains", [])
FOLDER_STRUCTURE: Dict[str, str] = _CONFIG.get("folder_structure", {})

# ==== 📚 Standard Keys and Patterns ====

STANDARD_KEYS: Dict[str, str] = {
    "input": "processed_data",
    "output": "qc_output",
    "dictionary": "dictionary",
    "merged_data": "merged_data",
}

FILE_PATTERNS: Dict[str, str] = {
    "final_csv": r"_FINAL\.(csv|xlsx|xls)$",
    "release_dict": r"_Release\.(csv|xlsx|xls)$",
    "clinical_final": r"Clinical_FINAL\.(csv|xlsx)$",
    "cleaned_dict": r"_cleaned\.(csv|xlsx)$",
    "supplement": r"_supplement\.(csv|xlsx|xls)$",
}

COLUMN_ALIASES: Dict[str, List[str]] = {
    "Med_ID": ["Med ID", "MedID", "Med id", "Med Id"],
    "Visit_ID": ["Visit_ID", "Visit ID", "Visit", "Visit id", "Visit Id"]
}

# ==== 🚫 Missing Value Handling ====

MISSING_VALUE_CODES: List[int] = [-9999, -8888, -777777]

MISSING_VALUE_STRINGS: FrozenSet[str] = frozenset({
    "-9999", "-9999.0", "-8888", "-8888.0", "-777777", "-777777.0",
    "NAN", "NAT", "NONE", "", "MISSING"
})

# ==== 📊 Outlier Detection Methods ====

class OutlierMethod(Enum):
    IQR = "IQR"
    STD = "STD"


# ==== 📌 Encoding Constants ====

DEFAULT_ENCODING: str = "utf-8"
FALLBACK_ENCODING: str = "ISO-8859-1"



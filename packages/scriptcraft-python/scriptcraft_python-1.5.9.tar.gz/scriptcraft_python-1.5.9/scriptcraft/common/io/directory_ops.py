"""
Directory operations for managing project structure.
"""

import os
from pathlib import Path
from typing import Optional, Union, List
import shutil

def ensure_output_dir(directory: Union[str, Path]) -> Path:
    """Ensure an output directory exists.
    
    Args:
        directory: Path to the directory
    
    Returns:
        Path to the ensured directory
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def get_input_dir(domain: str) -> Path:
    """Get the input directory for a domain.
    
    Args:
        domain: Domain name
    
    Returns:
        Path to the input directory
    """
    return Path("input") / domain

def get_output_dir(domain: str) -> Path:
    """Get the output directory for a domain.
    
    Args:
        domain: Domain name
    
    Returns:
        Path to the output directory
    """
    return Path("output") / domain

def get_qc_output_dir(domain: str) -> Path:
    """Get the QC output directory for a domain.
    
    Args:
        domain: Domain name
    
    Returns:
        Path to the QC output directory
    """
    return Path("qc_output") / domain

def get_file_output_path(
    domain: str,
    filename: str,
    subdir: Optional[str] = None
) -> Path:
    """Get the full output path for a file in a specific domain.
    
    Args:
        domain: Domain name
        filename: Name of the file
        subdir: Optional subdirectory
    
    Returns:
        Full path to the output file
    """
    output_dir = get_output_dir(domain)
    if subdir:
        output_dir = output_dir / subdir
    ensure_output_dir(output_dir)
    return output_dir / filename

def clean_directory(directory: Union[str, Path]) -> None:
    """Clean all files in a directory.
    
    Args:
        directory: Path to the directory
    """
    directory = Path(directory)
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)

def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """List files in a directory.
    
    Args:
        directory: Path to the directory
        pattern: File pattern to match
        recursive: Whether to search recursively
    
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    if recursive:
        return list(directory.rglob(pattern))
    return list(directory.glob(pattern)) 
"""
Basic file operations for the project.
"""

import os
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import shutil

def find_first_data_file(
    directory: Union[str, Path],
    pattern: str = "*.csv"
) -> Optional[Path]:
    """Find the first data file matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match
    
    Returns:
        Path to the first matching file, or None if not found
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))
    return files[0] if files else None

def find_latest_file(
    directory: Union[str, Path],
    pattern: str = "*.csv"
) -> Optional[Path]:
    """Find the latest file matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match
    
    Returns:
        Path to the latest matching file, or None if not found
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))
    return max(files, key=lambda x: x.stat().st_mtime) if files else None

def find_matching_file(
    directory: Union[str, Path],
    pattern: str
) -> Optional[Path]:
    """Find a file matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match
    
    Returns:
        Path to the matching file, or None if not found
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))
    return files[0] if files else None

def resolve_file(
    file_path: Union[str, Path],
    search_dirs: List[Union[str, Path]]
) -> Optional[Path]:
    """Resolve a file path by searching in multiple directories.
    
    Args:
        file_path: Path to the file
        search_dirs: List of directories to search in
    
    Returns:
        Resolved file path, or None if not found
    """
    file_path = Path(file_path)
    if file_path.is_absolute() and file_path.exists():
        return file_path
    
    for directory in search_dirs:
        full_path = Path(directory) / file_path
        if full_path.exists():
            return full_path
    
    return None

def resolve_path(
    path: Union[str, Path],
    base_dir: Union[str, Path]
) -> Path:
    """Resolve a path relative to a base directory.
    
    Args:
        path: Path to resolve
        base_dir: Base directory
    
    Returns:
        Resolved path
    """
    path = Path(path)
    if path.is_absolute():
        return path
    return Path(base_dir) / path

def copy_file(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False
) -> None:
    """Copy a file to a new location.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing files
    """
    source = Path(source)
    destination = Path(destination)
    
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Destination file exists: {destination}")
    
    shutil.copy2(source, destination)

def move_file(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False
) -> None:
    """Move a file to a new location.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing files
    """
    source = Path(source)
    destination = Path(destination)
    
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")
    
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Destination file exists: {destination}")
    
    shutil.move(str(source), str(destination)) 
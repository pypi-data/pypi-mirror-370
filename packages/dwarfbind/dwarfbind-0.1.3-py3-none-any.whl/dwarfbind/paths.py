"""
File path utilities for dwarfbind.

This module provides functions for handling file paths and names in a
consistent and safe manner.
"""

# Standard library imports
import os
import logging
from typing import List, Optional

# Global variables
logger = logging.getLogger("dwarfbind")


def resolve_header_path(header_path: str, include_paths: Optional[List[str]] = None) -> str:
    """
    Resolve a header file path using include paths.

    This function:
    - Returns absolute paths as-is
    - For relative paths, tries to find the file in:
        1. Current directory
        2. Each include path in order
    - Preserves the original path if not found

    Args:
        header_path: Path to the header file
        include_paths: List of include paths to search

    Returns:
        Resolved path to the header file
    """
    # Return absolute paths as-is
    if os.path.isabs(header_path):
        return header_path

    # Try current directory first
    if os.path.isfile(header_path):
        return os.path.abspath(header_path)

    # Try each include path
    if include_paths:
        for include_path in include_paths:
            full_path = os.path.join(include_path, header_path)
            if os.path.isfile(full_path):
                return full_path

    # If not found, return the original path
    # This allows cpp to handle system include paths
    return header_path


def generate_output_filename(
    library_name: str | None, fallback_path: str
) -> str:
    """
    Generate output filename based on library name.

    This function creates a Python-friendly filename by:
    - Using SONAME if available (preferred)
    - Falling back to library path if needed
    - Converting special characters to underscores
    - Ensuring .py extension
    - Maintaining uniqueness

    Args:
        library_name: Library name from SONAME
        fallback_path: Path to use if library_name is None or empty

    Returns:
        Generated filename
    """
    if library_name and library_name.strip():
        base = library_name
    else:
        base = os.path.basename(fallback_path)

    # Convert library name to Python module name
    base = base.replace("-", "_")
    base = base.replace(".", "_")
    base = base.replace("/", "_")

    return f"{base}.py"


def strip_trailing_whitespace_from_file(file_path: str) -> None:
    """
    Remove trailing whitespace from each line in the given file.

    This function ensures consistent file formatting by:
    - Removing trailing spaces and tabs
    - Ensuring exactly one newline at end of file
    - Preserving line content and order
    - Handling encoding correctly
    - Logging errors without failing
    """
    try:
        with open(file_path, encoding="utf-8") as file_handle:
            lines = file_handle.readlines()
        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.writelines(line.rstrip() + "\n" for line in lines)
    except Exception as error:
        logger.debug(f"Failed to strip whitespace: {error}")


def collect_header_files_from_directory(directory_path: str) -> list[str]:
    """
    Collect paths to all files in a directory.

    Args:
        directory_path: Path to directory to scan

    Returns:
        List of absolute paths to files
    """
    header_files = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            header_files.append(os.path.abspath(os.path.join(root, filename)))
    return sorted(header_files)


def resolve_header_or_directory_path(path: str, include_paths: Optional[List[str]] = None) -> list[str]:
    """
    Resolve a file or directory path, returning a list of file paths.

    For a file path:
    - Returns absolute path as-is
    - For relative paths, tries to find the file in:
        1. Current directory
        2. Each include path in order
    - Preserves the original path if not found

    For a directory path:
    - For absolute paths, collects all files from that directory
    - For relative paths, collects files from each matching directory in:
        1. Current directory
        2. Each include path in order

    Args:
        path: Path to file or directory
        include_paths: List of include paths to search

    Returns:
        List of resolved paths to files
    """
    # Handle absolute paths
    if os.path.isabs(path):
        if os.path.isdir(path):
            return collect_header_files_from_directory(path)
        if os.path.isfile(path):
            return [path]
        return []

    resolved_paths = []

    # Try current directory first
    current_path = os.path.abspath(path)
    if os.path.isdir(current_path):
        resolved_paths.extend(collect_header_files_from_directory(current_path))
    elif os.path.isfile(current_path):
        resolved_paths.append(current_path)
        return [current_path]  # For files, return first match only

    # Try each include path
    if include_paths:
        for include_path in include_paths:
            full_path = os.path.join(include_path, path)
            if os.path.isdir(full_path):
                resolved_paths.extend(collect_header_files_from_directory(full_path))
            elif os.path.isfile(full_path):
                resolved_paths.append(full_path)
                if not path.endswith(os.sep):  # Not a directory request
                    return [full_path]  # For files, return first match only

    # If nothing was found and it's not a directory, return original for cpp to handle
    if not resolved_paths and not path.endswith(os.sep):
        return [path]

    return sorted(set(resolved_paths))  # Remove duplicates and sort
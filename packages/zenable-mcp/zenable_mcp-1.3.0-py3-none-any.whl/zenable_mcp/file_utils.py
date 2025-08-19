"""
File enumeration utilities for handling glob patterns and file discovery.
"""

import logging
import warnings
from pathlib import Path
from typing import List, Optional, Set, Union

log = logging.getLogger(__name__)


def expand_file_patterns(
    patterns: List[str],
    base_path: Optional[Path] = None,
    exclude_patterns: Optional[List[str]] = None,
    max_files: Optional[int] = None,
) -> List[Path]:
    """
    Expand file patterns (including globs) into a list of file paths.

    Args:
        patterns: List of file patterns (can be paths or glob patterns like '**/*.py')
        base_path: Base directory to search from (defaults to current directory)
        exclude_patterns: Optional list of patterns to exclude
        max_files: Optional maximum number of files to return (for safety)

    Returns:
        List of resolved file paths

    Raises:
        ValueError: If dangerous patterns are detected
    """
    # Validate patterns for dangerous operations
    for pattern in patterns:
        _validate_pattern(pattern)

    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    exclude_patterns = exclude_patterns or []
    exclude_paths = _expand_patterns(exclude_patterns, base_path)

    all_files = []
    for pattern in patterns:
        files = _expand_pattern(pattern, base_path)
        # Filter out excluded files
        files = [f for f in files if f not in exclude_paths]
        all_files.extend(files)

    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    # Apply max_files limit if specified
    if max_files is not None and len(unique_files) > max_files:
        log.warning(
            f"Found {len(unique_files)} files, limiting to {max_files}. "
            "Consider using more specific patterns."
        )
        unique_files = unique_files[:max_files]

    return unique_files


def _expand_pattern(pattern: str, base_path: Path) -> List[Path]:
    """
    Expand a single pattern into file paths.

    Args:
        pattern: A file pattern (path or glob)
        base_path: Base directory to search from

    Returns:
        List of matching file paths
    """
    # Warn if pattern starts with / (even for absolute patterns)
    if pattern.startswith("/"):
        warnings.warn(
            f"Pattern '{pattern}' starts with '/'. Will be treated as relative to base path."
        )

    # First check if it's a direct file path
    path = Path(pattern)

    # If it's an absolute path
    if path.is_absolute():
        if path.exists() and path.is_file():
            return [path]
        elif path.exists() and path.is_dir():
            # Only get files directly in this directory, not recursively
            return [f for f in path.iterdir() if f.is_file()]
        # For non-existent absolute paths, strip the leading slash and try as relative
        pattern = pattern.lstrip("/")
        path = Path(pattern)

    # Try relative to base_path
    full_path = base_path / path
    if full_path.exists() and full_path.is_file():
        return [full_path]
    elif full_path.exists() and full_path.is_dir():
        # If it's a directory, get all files in it recursively
        return [f for f in full_path.rglob("*") if f.is_file()]

    # Treat as glob pattern
    # Handle special case of **/* patterns
    if "**" in pattern or "*" in pattern:
        matches = list(base_path.glob(pattern))
        return [m for m in matches if m.is_file()]

    # If no glob chars and doesn't exist, return empty
    log.warning(f"Pattern '{pattern}' did not match any files")
    return []


def _expand_patterns(patterns: List[str], base_path: Path) -> Set[Path]:
    """
    Expand multiple patterns into a set of file paths.

    Args:
        patterns: List of file patterns
        base_path: Base directory to search from

    Returns:
        Set of matching file paths
    """
    all_files = set()
    for pattern in patterns:
        files = _expand_pattern(pattern, base_path)
        all_files.update(files)
    return all_files


def filter_by_extensions(
    files: List[Path],
    extensions: Optional[List[str]] = None,
) -> List[Path]:
    """
    Filter files by their extensions.

    Args:
        files: List of file paths
        extensions: List of extensions to include (e.g., ['.py', '.js'])

    Returns:
        Filtered list of file paths
    """
    if not extensions:
        return files

    # Normalize extensions to include dot
    extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    return [f for f in files if f.suffix in extensions]


def get_relative_paths(
    files: List[Path],
    base_path: Optional[Path] = None,
) -> List[str]:
    """
    Convert absolute paths to relative paths.

    Args:
        files: List of file paths
        base_path: Base directory to make paths relative to

    Returns:
        List of relative path strings
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    relative_paths = []
    for file in files:
        try:
            rel_path = file.relative_to(base_path)
            relative_paths.append(str(rel_path))
        except ValueError:
            # If file is not under base_path, use absolute path
            relative_paths.append(str(file))

    return relative_paths


def validate_files_exist(files: List[Union[str, Path]]) -> List[Path]:
    """
    Validate that files exist and return resolved paths.

    Args:
        files: List of file paths (as strings or Path objects)

    Returns:
        List of validated Path objects

    Raises:
        FileNotFoundError: If any file does not exist
    """
    validated = []
    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file}")
        if not path.is_file():
            raise ValueError(f"Not a file: {file}")
        validated.append(path.resolve())

    return validated


def _validate_pattern(pattern: str) -> None:
    """
    Validate a file pattern for dangerous operations.

    Args:
        pattern: The pattern to validate

    Raises:
        ValueError: If the pattern is considered dangerous
    """

    # Dangerous patterns that could scan entire filesystem
    dangerous_patterns = [
        "/**",  # Recursive scan from root
        "/*",  # All files in root
        "/",  # Root directory
    ]

    # Check for exact dangerous patterns
    if pattern in dangerous_patterns:
        raise ValueError(
            f"Dangerous pattern '{pattern}' detected. "
            "This would scan the entire filesystem or root directory. "
            "Please use more specific patterns."
        )

    # Don't warn here, we warn in _expand_pattern for patterns starting with /

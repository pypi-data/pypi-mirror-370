"""
File discovery utilities that combine git operations with zenable filtering.
"""

import logging
from pathlib import Path
from typing import List, Optional

from zenable_mcp.utils.git import (
    get_git_modified_files,
)
from zenable_mcp.utils.zenable_config import filter_files_by_zenable_config

log = logging.getLogger(__name__)


def get_most_recently_edited_file_with_filtering(
    base_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Find the most recently edited file that is modified in git and not excluded by zenable config.

    This function combines git operations with zenable config filtering to find:
    1. Files modified in the git working tree
    2. Most recently modified based on filesystem timestamp
    3. Not ignored by .gitignore
    4. Not excluded by zenable_config skip patterns

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        Path to the most recently edited modified file after filtering, or None if no files
    """
    # First get the git-modified files
    modified_files = get_git_modified_files(base_path)

    if not modified_files:
        log.info("No modified files found in git repository")
        return None

    # Convert to Path objects for filtering
    path_objects = [Path(f) for f in modified_files]

    # Apply zenable config filtering
    files_before_filter = len(path_objects)
    filtered_paths = filter_files_by_zenable_config(path_objects)

    files_filtered = files_before_filter - len(filtered_paths)
    if files_filtered > 0:
        log.info(f"Filtered out {files_filtered} file(s) based on zenable config")

    if not filtered_paths:
        log.info("No modified files remaining after zenable config filtering")
        return None

    log.info(f"Files remaining after filtering: {len(filtered_paths)}")

    # Find the most recently modified file
    log.info(f"Checking modification times for {len(filtered_paths)} files...")
    for f in filtered_paths:
        mtime = f.stat().st_mtime
        from datetime import datetime

        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        log.debug(f"  {f}: {mtime_str}")

    most_recent_file = max(filtered_paths, key=lambda f: f.stat().st_mtime)

    log.info(f"Selected most recently edited file: {most_recent_file}")
    return str(most_recent_file)


def get_git_modified_files_with_filtering(
    base_path: Optional[Path] = None,
) -> List[str]:
    """
    Get all files modified in git that are not excluded by zenable config.

    This function combines git operations with zenable config filtering.

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        List of paths to modified files after filtering
    """
    # Get git-modified files
    modified_files = get_git_modified_files(base_path)

    if not modified_files:
        return []

    # Convert to Path objects for filtering
    path_objects = [Path(f) for f in modified_files]

    # Apply zenable config filtering
    filtered_paths = filter_files_by_zenable_config(path_objects)

    # Convert back to strings
    return [str(p) for p in filtered_paths]

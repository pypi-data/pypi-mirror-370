"""
Git utilities for finding modified files in the repository.
"""

import logging
from pathlib import Path
from typing import List, Optional

import git
from git import Repo

log = logging.getLogger(__name__)


def get_most_recently_edited_git_file(
    base_path: Optional[Path] = None,
) -> Optional[str]:
    """
    Find the most recently edited file that is also modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Most recently modified based on filesystem timestamp
    3. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        Path to the most recently edited modified file, or None if no modified files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository
        repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        log.info(f"Git repository root: {git_root}")

        # Get list of modified files (both staged and unstaged)
        modified_files = []

        # Get unstaged changes
        unstaged_count = 0
        for item in repo.index.diff(None):  # diff against working tree
            file_path = git_root / item.a_path
            if file_path.exists() and file_path.is_file():
                modified_files.append(file_path)
                unstaged_count += 1
                log.info(f"  Found unstaged file: {item.a_path}")

        if unstaged_count > 0:
            log.info(f"Found {unstaged_count} unstaged file(s)")

        # Get staged changes (only if there are commits in the repo)
        staged_count = 0
        if repo.head.is_valid():
            for item in repo.index.diff("HEAD"):  # diff against HEAD
                file_path = git_root / item.a_path
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and file_path not in modified_files
                ):
                    modified_files.append(file_path)
                    staged_count += 1
                    log.info(f"  Found staged file: {item.a_path}")
        else:
            # For repos with no commits, all staged files are new
            for (path, stage), entry in repo.index.entries.items():
                if stage == 0:  # Normal stage entry
                    file_path = git_root / path
                    if (
                        file_path.exists()
                        and file_path.is_file()
                        and file_path not in modified_files
                    ):
                        modified_files.append(file_path)
                        staged_count += 1
                        log.info(f"  Found staged file (no commits): {path}")

        if staged_count > 0:
            log.info(f"Found {staged_count} staged file(s)")

        # Get untracked files (repo.untracked_files already respects .gitignore)
        untracked_count = 0
        for file_path_str in repo.untracked_files:
            file_path = git_root / file_path_str
            if file_path.exists() and file_path.is_file():
                modified_files.append(file_path)
                untracked_count += 1
                log.info(f"  Found untracked file: {file_path_str}")

        if untracked_count > 0:
            log.info(f"Found {untracked_count} untracked file(s)")

        log.info(f"Total modified files found: {len(modified_files)}")

        if not modified_files:
            msg = "No modified files found in git repository"
            log.info(msg)
            return None

        # Find the most recently modified file based on filesystem timestamp
        log.info(f"Checking modification times for {len(modified_files)} files...")
        for f in modified_files:
            mtime = f.stat().st_mtime
            from datetime import datetime

            mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            log.debug(
                f"  {f.relative_to(git_root) if f.is_relative_to(git_root) else f}: {mtime_str}"
            )

        most_recent_file = max(modified_files, key=lambda f: f.stat().st_mtime)

        msg = f"Selected most recently edited file: {most_recent_file}"
        log.info(msg)
        return str(most_recent_file)

    except git.InvalidGitRepositoryError:
        log.debug(f"Not in a git repository: {base_path}")
        return None
    except Exception as e:
        log.debug(f"Error finding most recently edited file: {e}")
        return None


def get_git_modified_files(base_path: Optional[Path] = None) -> List[str]:
    """
    Get all files modified in the git working tree.

    This function finds files that are:
    1. Modified in the git working tree (either unstaged or staged, but not committed)
    2. Not ignored by .gitignore

    Args:
        base_path: The base directory to search from (defaults to current directory)

    Returns:
        List of paths to modified files
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path).resolve()

    try:
        # Find the git repository
        repo = Repo(base_path, search_parent_directories=True)
        git_root = Path(repo.working_tree_dir)

        modified_files = []

        # Get unstaged changes
        for item in repo.index.diff(None):  # diff against working tree
            file_path = git_root / item.a_path
            if file_path.exists() and file_path.is_file():
                modified_files.append(str(file_path))

        # Get staged changes (only if there are commits in the repo)
        if repo.head.is_valid():
            for item in repo.index.diff("HEAD"):  # diff against HEAD
                file_path = git_root / item.a_path
                if (
                    file_path.exists()
                    and file_path.is_file()
                    and str(file_path) not in modified_files
                ):
                    modified_files.append(str(file_path))
        else:
            # For repos with no commits, all staged files are new
            for (path, stage), entry in repo.index.entries.items():
                if stage == 0:  # Normal stage entry
                    file_path = git_root / path
                    if (
                        file_path.exists()
                        and file_path.is_file()
                        and str(file_path) not in modified_files
                    ):
                        modified_files.append(str(file_path))

        # Get untracked files (repo.untracked_files already respects .gitignore)
        for file_path_str in repo.untracked_files:
            file_path = git_root / file_path_str
            if file_path.exists() and file_path.is_file():
                modified_files.append(str(file_path))

        return modified_files

    except git.InvalidGitRepositoryError:
        return []
    except Exception:
        return []

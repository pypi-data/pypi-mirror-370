import fnmatch
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


def should_skip_file(filename: str, skip_patterns: list[str]) -> bool:
    """
    Check if a file should be skipped based on skip patterns.

    Supports:
    - Exact filename matches (e.g., "package-lock.json")
    - Glob patterns (e.g., "**/*.rbi", "foo/**/*.pyc")
    - Negation patterns with ! prefix (e.g., "!keep-this.json")
    - Escaped ! for literal filenames (e.g., "\\!important.txt" matches "!important.txt")

    Patterns are evaluated in order - the last matching pattern wins.
    This matches .gitignore behavior where later patterns can override earlier ones.

    Args:
        filename: The full file path from the PR
        skip_patterns: List of patterns to check against.
                      Order matters - the last matching pattern wins.

    Returns:
        True if the file should be skipped, False otherwise
    """
    # Create Path object once to avoid redundant instantiations
    file_path = Path(filename)
    file_parts = file_path.parts
    file_basename = file_path.name

    # Track whether file should be skipped - start with False
    should_skip = False

    # Process patterns in order - last match wins
    for pattern in skip_patterns:
        # Check if pattern starts with escaped exclamation mark
        if pattern.startswith("\\!"):
            # Remove the backslash and treat the rest as a literal pattern
            literal_pattern = pattern[1:]  # This gives us !filename
            if "*" in literal_pattern or "?" in literal_pattern:
                if _match_glob_pattern(
                    filename, literal_pattern, file_parts, file_basename
                ):
                    should_skip = True
            else:
                if _match_exact_pattern(filename, literal_pattern, file_basename):
                    should_skip = True
        elif pattern.startswith("!"):
            # Negation pattern - remove the ! and check if it matches
            negated_pattern = pattern[1:]
            if "*" in negated_pattern or "?" in negated_pattern:
                if _match_glob_pattern(
                    filename, negated_pattern, file_parts, file_basename
                ):
                    should_skip = False
            else:
                if _match_exact_pattern(filename, negated_pattern, file_basename):
                    should_skip = False
        else:
            # Regular pattern - if it matches, mark for skipping
            if "*" in pattern or "?" in pattern:
                if _match_glob_pattern(filename, pattern, file_parts, file_basename):
                    should_skip = True
            else:
                if _match_exact_pattern(filename, pattern, file_basename):
                    should_skip = True

    return should_skip


def _match_glob_pattern(
    filename: str, pattern: str, file_parts: tuple[str, ...], file_basename: str
) -> bool:
    """Helper function to handle glob pattern matching."""
    # Handle ** for recursive directory matching
    if "**" in pattern:
        return _match_double_star_pattern(filename, pattern, file_parts)
    else:
        # Simple glob patterns without **
        return fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(
            file_basename, pattern
        )


def _match_double_star_pattern(
    filename: str, pattern: str, file_parts: tuple[str, ...]
) -> bool:
    """Helper function to handle ** patterns."""
    if pattern.startswith("**/"):
        # **/*.ext matches foo.ext, bar/foo.ext, bar/baz/foo.ext, etc.
        simple_pattern = pattern[3:]  # Remove **/

        # Check direct match
        if fnmatch.fnmatch(filename, simple_pattern) or fnmatch.fnmatch(
            file_parts[-1], simple_pattern
        ):
            return True

        # Check if any suffix of the path matches
        for i in range(len(file_parts)):
            partial_path = "/".join(file_parts[i:])
            if fnmatch.fnmatch(partial_path, simple_pattern):
                return True

    elif "/**/" in pattern:
        # For patterns like dir/**/file, split and check
        parts = pattern.split("/**/", 1)  # Split only on first occurrence
        if len(parts) == 2:
            prefix, suffix = parts
            # Check if filename starts with prefix
            if filename.startswith(prefix + "/"):
                remaining = filename[len(prefix) + 1 :]
                return _match_suffix_pattern(remaining, suffix)
    else:
        # Handle other ** patterns by converting to *
        pattern_normalized = pattern.replace("**", "*")
        return fnmatch.fnmatch(filename, pattern_normalized)

    return False


def _match_suffix_pattern(remaining_path: str, suffix: str) -> bool:
    """Helper function to match suffix patterns in ** expressions."""
    if "*" in suffix or "?" in suffix:
        # For wildcards in suffix, check all possible subpaths
        remaining_parts = Path(remaining_path).parts
        for i in range(len(remaining_parts)):
            subpath = "/".join(remaining_parts[i:])
            # Use Path.match for proper glob matching where * doesn't match /
            if Path(subpath).match(suffix):
                return True
    else:
        # For non-wildcard suffixes, check if remaining ends with suffix
        return remaining_path.endswith(suffix)

    return False


def _match_exact_pattern(filename: str, pattern: str, file_basename: str) -> bool:
    """Helper function to handle exact pattern matching."""
    if pattern.startswith("/"):
        # Pattern starts with / - match only from root
        return filename == pattern[1:]
    elif pattern.startswith("./"):
        # Pattern starts with ./ - match only from root
        return filename == pattern[2:]
    elif "/" in pattern:
        # Pattern contains path separators but doesn't start with / or ./
        # Match exact path or as a suffix (but not partial directory names)
        if filename == pattern:
            return True
        # Check if filename ends with /pattern to avoid partial matches
        # This prevents "foobar/test" from matching pattern "bar/test"
        return (
            filename.endswith("/" + pattern)
            and len(filename) > len(pattern) + 1
            and filename[-(len(pattern) + 1)] == "/"
        )
    else:
        # No path separators - match any file with this basename
        return file_basename == pattern

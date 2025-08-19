"""Hook installation commands for zenable-mcp."""

import json
import re
from pathlib import Path

import click

from zenable_mcp import __version__

# Supported matchers for the zenable-mcp hook
SUPPORTED_MATCHERS = ["Write", "Edit"]

# Global variable to track temporary files for cleanup
_temp_files_to_cleanup: list[Path] = []


def cleanup_temp_files():
    """Clean up any temporary .zenable files that were created."""
    global _temp_files_to_cleanup
    for temp_file in _temp_files_to_cleanup:
        if temp_file.exists():
            try:
                temp_file.unlink()
                click.echo(f"Cleaned up temporary file: {temp_file}", err=True)
            except OSError:
                pass  # Best effort cleanup
    _temp_files_to_cleanup.clear()


def safe_write_json(settings_path: Path, settings: dict) -> None:
    """Safely write JSON settings using a .zenable temporary file.

    Args:
        settings_path: Path to the settings file
        settings: Dictionary to write as JSON

    Raises:
        click.ClickException: On any write error
    """
    global _temp_files_to_cleanup

    # Write to .zenable file first
    zenable_path = settings_path.with_suffix(".json.zenable")

    # Track the temp file for cleanup
    _temp_files_to_cleanup.append(zenable_path)

    try:
        # Test write permissions and disk space
        with open(zenable_path, "w") as f:
            json.dump(settings, f, indent=2)
            f.write("\n")
            f.flush()  # Ensure data is written
            import os

            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename (on POSIX systems)
        zenable_path.replace(settings_path)

        # Remove from cleanup list after successful rename
        if zenable_path in _temp_files_to_cleanup:
            _temp_files_to_cleanup.remove(zenable_path)

    except OSError as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass  # Best effort cleanup

        error_msg = f"Failed to write settings to {settings_path}: {e}"

        # Check for specific error conditions
        if "No space left on device" in str(e):
            error_msg += "\nDisk is full. Please free up space and try again."
        elif "Permission denied" in str(e):
            error_msg += (
                "\nInsufficient permissions. Check file and directory permissions."
            )

        raise click.ClickException(error_msg)

    except (TypeError, ValueError) as e:
        # Clean up zenable file on error
        if zenable_path.exists():
            try:
                zenable_path.unlink()
                # Remove from cleanup list after manual cleanup
                if zenable_path in _temp_files_to_cleanup:
                    _temp_files_to_cleanup.remove(zenable_path)
            except OSError:
                pass

        raise click.ClickException(
            f"Failed to encode settings as JSON: {e}\n"
            f"This is likely a bug in the application."
        )


def is_supported_matcher_config(matcher: str) -> bool:
    """Check if a matcher configuration is supported for zenable-mcp.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher contains only Edit and/or Write (in any order)
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    # Remove empty parts
    parts = [p for p in parts if p]

    # Check if all parts are in SUPPORTED_MATCHERS
    return all(part in SUPPORTED_MATCHERS for part in parts) and len(parts) > 0


def find_git_root():
    """Find the root of the git repository"""
    current = Path.cwd()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    return None


def get_settings_path(is_global: bool, find_git_root_func=None):
    """Determine the appropriate settings file path.

    Args:
        is_global: Whether to use global settings
        find_git_root_func: Function to find git root (for testing)

    Returns:
        Path to the settings file

    Raises:
        click.ClickException: If local install but not in a git repository
    """
    if find_git_root_func is None:
        find_git_root_func = find_git_root

    if is_global:
        return Path.home() / ".claude" / "settings.json"
    else:
        git_root = find_git_root_func()
        if not git_root:
            raise click.ClickException(
                "Not in a git repository.\n"
                "Did you mean to do the global installation with --global?"
            )
        return git_root / ".claude" / "settings.json"


def load_or_create_settings(settings_path: Path) -> dict:
    """Load existing settings or create new empty settings.

    Args:
        settings_path: Path to the settings file

    Returns:
        Dictionary of settings

    Raises:
        click.ClickException: If JSON is invalid
    """
    if settings_path.exists() and settings_path.stat().st_size > 0:
        with open(settings_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise click.ClickException(
                    f"Invalid JSON in {settings_path}\n"
                    f"Details: {e}\n"
                    f"Please fix the JSON syntax or backup and remove the file."
                )
    return {}


def ensure_hook_structure(settings: dict) -> None:
    """Ensure the settings have the required hook structure.

    Args:
        settings: Settings dictionary to update in place
    """
    settings.setdefault("hooks", {})
    settings["hooks"].setdefault("PostToolUse", [])


def create_hook_config(matcher: str = None) -> dict:
    """Create a standard hook configuration.

    Args:
        matcher: Optional custom matcher string. If None, uses default supported matchers.

    Returns:
        Hook configuration dictionary
    """
    if matcher is None:
        matcher = "|".join(SUPPORTED_MATCHERS)

    return {
        "matcher": matcher,
        "hooks": [{"type": "command", "command": "uvx zenable-mcp@latest check"}],
    }


def should_update_matcher(matcher: str) -> bool:
    """Check if a matcher should be updated to include both Edit and Write.

    Args:
        matcher: The matcher string to check

    Returns:
        True if the matcher should be updated
    """
    if not isinstance(matcher, str):
        return False

    parts = [part.strip() for part in matcher.split("|")]
    has_edit = "Edit" in parts
    has_write = "Write" in parts

    if (has_write and not has_edit) or (has_edit and not has_write):
        return len(parts) <= 2

    return False


def extract_command_from_hook(hook: dict) -> str:
    """Extract the command from a hook configuration.

    Args:
        hook: Hook configuration dictionary

    Returns:
        Command string or empty string if not found
    """
    if isinstance(hook, dict) and "hooks" in hook:
        for sub_hook in hook.get("hooks", []):
            if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                return sub_hook.get("command", "")
    return ""


def analyze_existing_hooks(post_tool_use: list, new_hook_config: dict) -> dict:
    """Analyze existing hooks for duplicates and similar configurations.

    Args:
        post_tool_use: List of existing PostToolUse hooks
        new_hook_config: The new hook configuration to check against

    Returns:
        Dictionary with analysis results
    """
    result = {
        "hook_exists": False,
        "has_latest": False,
        "similar_hook_indices": [],
        "pinned_version_indices": [],
        "matcher_update_indices": [],
    }

    # Matches semantic versions in package specifications (e.g., uvx zenable-mcp@1.2.3)
    # The @ prefix is required as it's part of the package@version syntax
    semver_pattern = re.compile(
        r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
    )

    for i, existing_hook in enumerate(post_tool_use):
        if existing_hook == new_hook_config:
            result["hook_exists"] = True
            break

        command = extract_command_from_hook(existing_hook)

        if command.startswith("uvx zenable-mcp"):
            matcher = existing_hook.get("matcher", "")

            if not is_supported_matcher_config(matcher):
                click.echo(
                    f"⚠️  Warning: Hook with matcher '{matcher}' is not a supported configuration for zenable-mcp.\n"
                    f"   Supported configuration should only contain {' and '.join(SUPPORTED_MATCHERS)}.\n"
                    f"   The check may not behave as expected.",
                    err=True,
                )

            if (
                should_update_matcher(matcher)
                and i not in result["matcher_update_indices"]
            ):
                result["matcher_update_indices"].append(i)

            if "@latest" in command:
                result["has_latest"] = True
            elif semver_pattern.search(command):
                result["pinned_version_indices"].append(i)
            elif command != "uvx zenable-mcp@latest check":
                result["similar_hook_indices"].append(i)

    return result


def update_hook_matcher(hook: dict, new_matcher: str = None) -> dict:
    """Update a hook's matcher to include both Edit and Write.

    Args:
        hook: Hook configuration to update
        new_matcher: Optional new matcher. If None, updates existing.

    Returns:
        Updated hook configuration
    """
    if new_matcher:
        hook["matcher"] = new_matcher
    else:
        old_matcher = hook.get("matcher", "")
        parts = [part.strip() for part in old_matcher.split("|")]
        if "Write" not in parts:
            parts.append("Write")
        if "Edit" not in parts:
            parts.append("Edit")
        hook["matcher"] = "|".join(parts)

    return hook


def _claude_impl(is_global: bool, find_git_root_func=None):
    """Implementation of claude command with dependency injection.

    Args:
        is_global: Whether to install globally
        find_git_root_func: Function to find git root (for testing)

    Returns:
        0 on success

    Raises:
        click.ClickException: On any error
    """
    settings_path = get_settings_path(is_global, find_git_root_func)

    new_hook_config = create_hook_config()

    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings = load_or_create_settings(settings_path)
    ensure_hook_structure(settings)

    post_tool_use = settings["hooks"]["PostToolUse"]
    analysis = analyze_existing_hooks(post_tool_use, new_hook_config)

    hook_exists = analysis["hook_exists"]
    has_latest = analysis["has_latest"]
    similar_hook_indices = analysis["similar_hook_indices"]
    pinned_version_indices = analysis["pinned_version_indices"]
    matcher_update_indices = analysis["matcher_update_indices"]

    # Matches semantic versions in package specifications (e.g., uvx zenable-mcp@1.2.3)
    # The @ prefix is required as it's part of the package@version syntax
    semver_pattern = re.compile(
        r"@(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
    )

    if hook_exists:
        click.echo(f"✓ Hook already installed in {settings_path} - no changes needed")
    elif has_latest and not matcher_update_indices:
        click.echo(
            f"✓ Hook with @latest already installed in {settings_path} - no changes needed"
        )
    elif pinned_version_indices:
        # Found pinned version hooks - update them to current version
        updated = False
        for idx in pinned_version_indices:
            old_hook = post_tool_use[idx]
            old_command = ""
            if isinstance(old_hook, dict) and "hooks" in old_hook:
                for sub_hook in old_hook.get("hooks", []):
                    if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                        old_command = sub_hook.get("command", "")
                        break

            # Extract the version from the command
            version_match = semver_pattern.search(old_command)
            old_version = version_match.group(1) if version_match else "unknown"

            old_matcher = old_hook.get("matcher", "")
            if should_update_matcher(old_matcher):
                post_tool_use[idx] = new_hook_config
            else:
                post_tool_use[idx] = create_hook_config(old_matcher)
            updated = True

            # Show upgrade message if old version differs from current
            if old_version != __version__:
                click.echo(
                    f"✓ Updated hook from pinned version ({old_version}) to @latest (current: {__version__})"
                )
            else:
                click.echo(
                    f"✓ Updated hook from pinned version ({old_version}) to @latest"
                )

        if updated:
            # Save the updated settings safely
            safe_write_json(settings_path, settings)
            click.echo(f"Successfully updated Claude hook in {settings_path}")
    elif similar_hook_indices:
        # Update similar hooks
        for idx in reversed(
            similar_hook_indices
        ):  # Reverse to maintain indices while removing
            old_hook = post_tool_use[idx]
            old_matcher = old_hook.get("matcher", "")

            if should_update_matcher(old_matcher):
                post_tool_use[idx] = new_hook_config
            else:
                post_tool_use[idx] = create_hook_config(old_matcher)

            old_command = extract_command_from_hook(old_hook)

            click.echo(
                f"✓ Updated existing hook from '{old_command}' to 'uvx zenable-mcp@latest check'"
            )

        # Save the updated settings safely
        safe_write_json(settings_path, settings)
        click.echo(f"Successfully updated Claude hook in {settings_path}")
    elif matcher_update_indices:
        # Update matchers for zenable-mcp hooks that need it
        # Remove any indices that were already handled in pinned_version_indices or similar_hook_indices
        remaining_matcher_indices = [
            idx
            for idx in matcher_update_indices
            if idx not in pinned_version_indices and idx not in similar_hook_indices
        ]

        if remaining_matcher_indices:
            updated_matchers = []
            for idx in remaining_matcher_indices:
                old_hook = post_tool_use[idx]
                old_matcher = old_hook.get("matcher", "")

                post_tool_use[idx] = update_hook_matcher(post_tool_use[idx])

                # Also update the command if needed
                for sub_hook in post_tool_use[idx].get("hooks", []):
                    if isinstance(sub_hook, dict) and sub_hook.get("type") == "command":
                        old_command = sub_hook.get("command", "")
                        if (
                            old_command.startswith("uvx zenable-mcp")
                            and old_command != "uvx zenable-mcp@latest check"
                        ):
                            sub_hook["command"] = "uvx zenable-mcp@latest check"

                new_matcher = post_tool_use[idx]["matcher"]
                updated_matchers.append(f"'{old_matcher}' → '{new_matcher}'")

            # Save the updated settings safely
            safe_write_json(settings_path, settings)

            if len(updated_matchers) == 1:
                click.echo(f"✓ Updated matcher from {updated_matchers[0]}")
            else:
                click.echo(f"✓ Updated {len(updated_matchers)} matchers:")
                for update in updated_matchers:
                    click.echo(f"  - {update}")

            click.echo(f"Successfully updated Claude hook in {settings_path}")
        else:
            # All matcher updates were handled by other scenarios, add new hook
            post_tool_use.append(new_hook_config)
            safe_write_json(settings_path, settings)
            click.echo(f"✓ Successfully installed Claude hook in {settings_path}")
    else:
        # Add new hook
        post_tool_use.append(new_hook_config)

        # Save the file safely
        safe_write_json(settings_path, settings)
        click.echo(f"✓ Successfully installed Claude hook in {settings_path}")

    return 0


@click.group()
@click.pass_context
def hook(ctx):
    """Install hooks for various tools"""
    pass


@hook.command()
@click.option(
    "--global",
    "-g",
    "is_global",
    is_flag=True,
    help="Install globally in ~/.claude/settings.json",
)
@click.pass_context
def claude(ctx, is_global):
    """Install the Claude hook for zenable-mcp conformance checking"""
    try:
        _claude_impl(is_global)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)

"""Install command group for zenable-mcp."""

import signal
import sys

import click

from zenable_mcp.commands.install.hook import cleanup_temp_files, hook


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    click.echo("\n⚠️  Installation interrupted by user", err=True)
    cleanup_temp_files()
    sys.exit(130)  # Standard exit code for SIGINT


@click.group()
@click.pass_context
def install(ctx):
    """Install zenable-mcp integrations"""
    # Set up signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)
    # Also handle SIGTERM for completeness
    signal.signal(signal.SIGTERM, signal_handler)


# Add the hook subcommand to the install group
install.add_command(hook)

# Export signal_handler for testing
__all__ = ["install", "signal_handler"]

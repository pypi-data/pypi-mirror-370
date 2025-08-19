import logging
import os

import click

from zenable_mcp.commands import check, install, version
from zenable_mcp.logging_config import configure_logging
from zenable_mcp.version_check import check_for_updates


@click.group()
@click.option(
    "--verbose", is_flag=True, help="Enable verbose output (sets log level to INFO)"
)
@click.option(
    "--debug", is_flag=True, help="Enable debug output (sets log level to DEBUG)"
)
@click.pass_context
def cli(ctx, verbose, debug):
    """Zenable MCP Client - Conformance checking for your code"""
    # Ensure that ctx.obj exists
    ctx.ensure_object(dict)

    # Store API key in context for subcommands to use
    ctx.obj["api_key"] = os.environ.get("ZENABLE_API_KEY")

    # Configure logging based on flags with colored output
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    configure_logging(log_level, debug=debug)


# Add commands to the CLI group
cli.add_command(version)
cli.add_command(check)
cli.add_command(install)


def main():
    """Main entry point"""
    from zenable_mcp import __version__

    # Check for updates before running the CLI
    check_for_updates(__version__)
    cli()


if __name__ == "__main__":
    main()

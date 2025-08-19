import logging

import click


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages based on level"""

    COLORS = {
        logging.DEBUG: "cyan",
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bright_red",
    }

    def format(self, record):
        # Get the base formatted message
        msg = super().format(record)

        # Add level prefix with distinct styling for debug and verbose
        if record.levelno == logging.DEBUG:
            prefix = click.style("[DEBUG] ", fg="cyan", bold=True)
            styled_msg = click.style(msg, fg="cyan", dim=True)
        elif record.levelno == logging.INFO:
            prefix = click.style("[INFO] ", fg="blue", bold=True)
            styled_msg = click.style(msg, fg="blue")
        elif record.levelno == logging.WARNING:
            prefix = click.style("[WARN] ", fg="yellow", bold=True)
            styled_msg = click.style(msg, fg="yellow")
        elif record.levelno == logging.ERROR:
            prefix = click.style("[ERROR] ", fg="red", bold=True)
            styled_msg = click.style(msg, fg="red")
        else:
            prefix = ""
            styled_msg = msg

        return prefix + styled_msg


def configure_logging(level: int, debug: bool = False):
    """Configure logging with colored output

    Args:
        level: The logging level to set
        debug: Whether debug mode is enabled
    """
    # Create a colored formatter
    formatter = ColoredFormatter("%(message)s")

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create and configure a stream handler with colored output
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    # FastMCP and its internals - suppress debug messages about SSE/connections
    logging.getLogger("fastmcp").setLevel(logging.WARNING)
    logging.getLogger("fastmcp.client").setLevel(logging.WARNING)
    logging.getLogger("fastmcp.sse").setLevel(logging.WARNING)
    logging.getLogger("fastmcp._client").setLevel(logging.WARNING)

    # HTTP libraries - always suppress verbose connection details
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(
        logging.ERROR
    )  # Very noisy, only show errors

    # Additional HTTP-related loggers that are very noisy
    logging.getLogger("httpcore.http11").setLevel(logging.ERROR)
    logging.getLogger("httpcore.connection").setLevel(logging.ERROR)
    logging.getLogger("httpx._client").setLevel(logging.WARNING)

    # Suppress all httpcore submodules
    logging.getLogger("httpcore._sync").setLevel(logging.ERROR)
    logging.getLogger("httpcore._async").setLevel(logging.ERROR)

    # SSE (Server-Sent Events) related
    logging.getLogger("sse").setLevel(logging.ERROR)
    logging.getLogger("sse_starlette").setLevel(logging.ERROR)
    logging.getLogger("httpx_sse").setLevel(logging.ERROR)

    # GitPython - suppress Popen debug messages
    logging.getLogger("git").setLevel(logging.WARNING)
    logging.getLogger("git.cmd").setLevel(logging.WARNING)
    logging.getLogger("git.util").setLevel(logging.WARNING)

    # Asyncio - suppress selector debug messages
    logging.getLogger("asyncio").setLevel(logging.WARNING)

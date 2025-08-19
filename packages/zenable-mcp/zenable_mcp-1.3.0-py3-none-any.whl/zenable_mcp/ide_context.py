"""
IDE context detection and file path extraction strategies.
"""

import logging
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from zenable_mcp.file_discovery import get_most_recently_edited_file_with_filtering

log = logging.getLogger(__name__)


class IDEType(Enum):
    """Supported IDE types."""

    CLAUDE = "claude"
    KIRO = "kiro"
    CURSOR = "cursor"
    VSCODE = "vscode"
    WINDSURF = "windsurf"
    UNKNOWN = "unknown"


class IDEContextStrategy(ABC):
    """Abstract base class for IDE context strategies."""

    @abstractmethod
    def detect(self) -> bool:
        """Detect if this IDE context is active."""
        pass

    @abstractmethod
    def get_file_paths(self) -> Optional[List[str]]:
        """Extract file paths from the IDE context."""
        pass

    @abstractmethod
    def get_ide_type(self) -> IDEType:
        """Return the IDE type."""
        pass


class ClaudeContextStrategy(IDEContextStrategy):
    """Strategy for Claude Code IDE context."""

    def detect(self) -> bool:
        """Detect Claude Code context by checking for CLAUDE_* environment variables."""
        # Claude sets various environment variables during hook execution
        claude_vars = [
            "CLAUDE_FILE_PATHS",
            "CLAUDE_TOOL_NAME",
            "CLAUDE_PROJECT_DIR",
        ]
        detected = any(os.environ.get(var) for var in claude_vars)
        if detected:
            log.debug("Claude Code context detected via environment variables")
            log.debug(
                f"CLAUDE_FILE_PATHS: {os.environ.get('CLAUDE_FILE_PATHS', 'Not set')}"
            )
            log.debug(
                f"CLAUDE_TOOL_NAME: {os.environ.get('CLAUDE_TOOL_NAME', 'Not set')}"
            )
        return detected

    def get_file_paths(self) -> Optional[List[str]]:
        """
        Extract file paths from Claude environment variables.

        Claude provides:
        - CLAUDE_FILE_PATHS: Space-separated list of file paths (for multi-file operations)

        Falls back to most recently edited git file if env var is not set.
        """
        file_paths = []

        # Check for multiple file paths first
        claude_file_paths = os.environ.get("CLAUDE_FILE_PATHS")
        if claude_file_paths:
            # Split space-separated paths and filter empty strings
            paths = [p.strip() for p in claude_file_paths.split() if p.strip()]
            file_paths.extend(paths)
            log.debug(f"Found {len(paths)} files in CLAUDE_FILE_PATHS")
        else:
            # Fallback to most recently edited file
            msg = "CLAUDE_FILE_PATHS not set, falling back to most recently edited file"
            log.info(msg)
            recent_file = get_most_recently_edited_file_with_filtering()
            if recent_file:
                file_paths.append(recent_file)
                msg = f"Using most recently edited file: {recent_file}"
                log.info(msg)

        return file_paths if file_paths else None

    def get_ide_type(self) -> IDEType:
        """Return Claude IDE type."""
        return IDEType.CLAUDE


class KiroContextStrategy(IDEContextStrategy):
    """Strategy for Kiro IDE context."""

    def detect(self) -> bool:
        """Detect Kiro IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[List[str]]:
        """Get file paths for Kiro - uses most recently edited file."""
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            msg = f"Kiro: Using most recently edited file: {recent_file}"
            log.info(msg)
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Kiro IDE type."""
        return IDEType.KIRO


class CursorContextStrategy(IDEContextStrategy):
    """Strategy for Cursor IDE context."""

    def detect(self) -> bool:
        """Detect Cursor IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[List[str]]:
        """Get file paths for Cursor."""
        msg = "Cursor: Using most recently edited file"
        log.info(msg)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Cursor IDE type."""
        return IDEType.CURSOR


class VSCodeContextStrategy(IDEContextStrategy):
    """Strategy for VSCode IDE context."""

    def detect(self) -> bool:
        """Detect VSCode IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[List[str]]:
        """Get file paths for VSCode."""
        msg = "VSCode: Using most recently edited file"
        log.info(msg)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return VSCode IDE type."""
        return IDEType.VSCODE


class WindsurfContextStrategy(IDEContextStrategy):
    """Strategy for Windsurf IDE context."""

    def detect(self) -> bool:
        """Detect Windsurf IDE context."""
        # No specific env vars for auto-detection
        return False

    def get_file_paths(self) -> Optional[List[str]]:
        """Get file paths for Windsurf."""
        msg = "Windsurf: Using most recently edited file"
        log.info(msg)
        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]
        return None

    def get_ide_type(self) -> IDEType:
        """Return Windsurf IDE type."""
        return IDEType.WINDSURF


class IDEContextDetector:
    """
    Detects IDE context and extracts file paths using appropriate strategy.
    """

    def __init__(self) -> None:
        """Initialize with all available strategies."""
        self.strategies: List[IDEContextStrategy] = [
            ClaudeContextStrategy(),
            CursorContextStrategy(),
            VSCodeContextStrategy(),
            WindsurfContextStrategy(),
            KiroContextStrategy(),
        ]
        self._detected_strategy: Optional[IDEContextStrategy] = None

    def detect_context(self) -> IDEType:
        """
        Detect the current IDE context.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        for strategy in self.strategies:
            if strategy.detect():
                self._detected_strategy = strategy
                ide_type = strategy.get_ide_type()
                log.info(f"Detected {ide_type.value} IDE context")
                return ide_type

        return IDEType.UNKNOWN

    def get_file_paths(self) -> Optional[List[str]]:
        """
        Get file paths from the detected IDE context.

        Returns:
            List of file paths if available, None otherwise
        """
        if self._detected_strategy:
            paths = self._detected_strategy.get_file_paths()
            if paths:
                msg = f"Extracted {len(paths)} file path(s) from {self._detected_strategy.get_ide_type().value} context"
                log.info(msg)
            return paths

        # Try each strategy if no context was previously detected
        for strategy in self.strategies:
            if strategy.detect():
                paths = strategy.get_file_paths()
                if paths:
                    msg = f"Extracted {len(paths)} file path(s) from {strategy.get_ide_type().value} context"
                    log.info(msg)
                    return paths

        # If no IDE context was detected, fall back to most recently edited file
        log.info(
            "No IDE context detected, attempting to find most recently edited file"
        )

        recent_file = get_most_recently_edited_file_with_filtering()
        if recent_file:
            return [recent_file]

        return None

    def get_detected_ide(self) -> IDEType:
        """
        Get the detected IDE type.

        Returns:
            IDEType: The detected IDE type, or UNKNOWN if none detected
        """
        if self._detected_strategy:
            return self._detected_strategy.get_ide_type()

        # Re-detect if needed
        return self.detect_context()


def get_files_from_environment() -> Optional[List[str]]:
    """
    Convenience function to get file paths from the current IDE context.

    Returns:
        List of file paths if available, None otherwise
    """
    detector = IDEContextDetector()
    detector.detect_context()
    return detector.get_file_paths()

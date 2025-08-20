"""Custom exceptions for Momovu.

This module defines custom exception classes used throughout the Momovu application
to handle specific error conditions with better context and debugging information.
"""

from typing import Any, Optional


class MomovuError(Exception):
    """Base exception for all Momovu-specific errors.

    All custom exceptions in the application should inherit from this class
    to allow for easy catching of application-specific errors.
    """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception with a message and optional details.

        Args:
            message: The error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


# Document-related exceptions


class DocumentLoadError(MomovuError):
    """Raised when a document fails to load."""

    def __init__(self, file_path: str, reason: str):
        """Initialize with file path and reason for failure.

        Args:
            file_path: Path to the document that failed to load
            reason: Reason for the load failure
        """
        super().__init__(
            f"Failed to load document '{file_path}': {reason}",
            {"file_path": file_path, "reason": reason},
        )


# Rendering-related exceptions


class PageRenderError(MomovuError):
    """Raised when a page fails to render."""

    def __init__(self, page_number: int, reason: str):
        """Initialize with page number and reason for failure.

        Args:
            page_number: The page that failed to render
            reason: Reason for the render failure
        """
        super().__init__(
            f"Failed to render page {page_number}: {reason}",
            {"page_number": page_number, "reason": reason},
        )

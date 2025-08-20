"""PDF document model for MVP architecture.

This model handles PDF document state without any UI dependencies.
It stores document metadata and provides validation.
"""

from typing import Any, Optional, cast

from momovu.models.base import BaseModel


class Document(BaseModel):
    """Model for PDF document data.

    This model stores:
    - File path
    - Page count
    - Page sizes
    - Document status

    It does NOT handle:
    - PDF rendering (that's a view concern)
    - PDF loading (that's a presenter concern)
    """

    def __init__(self) -> None:
        """Initialize empty document model with default validators."""
        super().__init__()

        # Define validation rules
        self.add_validator("page_count", lambda x: isinstance(x, int) and x >= 0)
        self.add_validator("page_sizes", self._validate_page_sizes)
        self.add_validator("is_loaded", lambda x: isinstance(x, bool))

        # Initialize properties with defaults
        self.set_property("file_path", None, validate=False)  # Optional path
        self.set_property("page_count", 0, validate=True)
        self.set_property("page_sizes", [], validate=True)
        self.set_property("is_loaded", False, validate=True)
        self.set_property("error_message", None, validate=False)  # Optional error

    @property
    def file_path(self) -> Optional[str]:
        """Path to the loaded PDF file, None if no document loaded."""
        return cast("Optional[str]", self.get_property("file_path"))

    @file_path.setter
    def file_path(self, value: Optional[str]) -> None:
        """Update the PDF file path."""
        self.set_property("file_path", value)

    @property
    def page_count(self) -> int:
        """Total number of pages in the document (0 if not loaded)."""
        return cast("int", self.get_property("page_count", 0))

    @page_count.setter
    def page_count(self, value: int) -> None:
        """Update the total page count."""
        self.set_property("page_count", value)

    @property
    def page_sizes(self) -> list[tuple[float, float]]:
        """List of (width, height) tuples in points for each page."""
        return cast("list[tuple[float, float]]", self.get_property("page_sizes", []))

    @page_sizes.setter
    def page_sizes(self, value: list[tuple[float, float]]) -> None:
        """Update the page dimensions list."""
        self.set_property("page_sizes", value)

    @property
    def is_loaded(self) -> bool:
        """True if a document is successfully loaded and ready."""
        return cast("bool", self.get_property("is_loaded", False))

    @is_loaded.setter
    def is_loaded(self, value: bool) -> None:
        """Update document loaded status."""
        self.set_property("is_loaded", value)

    @property
    def error_message(self) -> Optional[str]:
        """Error description if document failed to load, None otherwise."""
        return cast("Optional[str]", self.get_property("error_message"))

    @error_message.setter
    def error_message(self, value: Optional[str]) -> None:
        """Update the error message."""
        self.set_property("error_message", value)

    def get_page_size(self, page_index: int) -> Optional[tuple[float, float]]:
        """Get size of a specific page.

        Args:
            page_index: Zero-based page index

        Returns:
            Tuple of (width, height) or None if invalid index
        """
        sizes = self.page_sizes
        if 0 <= page_index < len(sizes):
            return sizes[page_index]
        return None

    def clear(self) -> None:
        """Reset model to initial unloaded state."""
        self.begin_batch_update()
        try:
            self.file_path = None
            self.page_count = 0
            self.page_sizes = []
            self.is_loaded = False
            self.error_message = None
        finally:
            self.end_batch_update()

    def update_from_document_info(
        self, file_path: str, page_count: int, page_sizes: list[tuple[float, float]]
    ) -> None:
        """Batch update all document properties after successful load.

        Args:
            file_path: Full path to the PDF file
            page_count: Total pages in document
            page_sizes: (width, height) tuples for each page
        """
        self.begin_batch_update()
        try:
            self.file_path = file_path
            self.page_count = page_count
            self.page_sizes = page_sizes
            self.is_loaded = True
            self.error_message = None
        finally:
            self.end_batch_update()

    def set_error(self, error_message: str) -> None:
        """Mark document as failed to load with error description.

        Args:
            error_message: Human-readable error explanation
        """
        self.begin_batch_update()
        try:
            self.is_loaded = False
            self.error_message = error_message
        finally:
            self.end_batch_update()

    def _validate_page_sizes(self, value: Any) -> bool:
        """Validate page_sizes is a list of (width, height) tuples with positive values.

        Args:
            value: The value to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, list):
            return False

        for item in value:
            # Check if it's a tuple with exactly 2 elements
            if not isinstance(item, tuple) or len(item) != 2:
                return False

            width, height = item

            # Check if both are numeric
            if not isinstance(width, (int, float)) or not isinstance(
                height, (int, float)
            ):
                return False

            # Check if both are positive
            if width <= 0 or height <= 0:
                return False

        return True

    def __repr__(self) -> str:
        """Developer-friendly string representation of document state."""
        return (
            f"Document(file_path={self.file_path!r}, "
            f"page_count={self.page_count}, is_loaded={self.is_loaded})"
        )

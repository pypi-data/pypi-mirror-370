"""Document presenter for handling PDF document logic.

This presenter manages PDF document operations without UI dependencies.
It coordinates between Document and the view layer.
"""

from pathlib import Path
from typing import Any, Optional

from PySide6.QtPdf import QPdfDocument

from momovu.lib.exceptions import DocumentLoadError
from momovu.lib.logger import (
    get_logger,
)
from momovu.models.document import Document
from momovu.presenters.base import BasePresenter

logger = get_logger(__name__)


class DocumentPresenter(BasePresenter):
    """Presenter for PDF document operations.

    This presenter handles:
    - PDF loading and error handling
    - Page management
    - Document type detection
    - Document state coordination
    """

    def __init__(self, model: Optional[Document] = None) -> None:
        """Initialize the document presenter.

        Args:
            model: Optional document model to use
        """
        super().__init__()
        self._model = model or Document()
        self._qt_document: Optional[QPdfDocument] = None

        self._model.add_observer(self._on_model_changed)

    def set_qt_document(self, qt_document: QPdfDocument) -> None:
        """Set the Qt PDF document for loading operations.

        Args:
            qt_document: The QPdfDocument instance to use

        Note:
            The presenter currently delegates PDF operations to QPdfDocument.
            This design allows for future migration to alternative PDF backends
            without affecting the view layer.
        """
        self._qt_document = qt_document

    def load_document(self, file_path: str) -> bool:
        """Load a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            True if loaded successfully
        """
        try:
            path = Path(file_path)
            if not path.exists():
                self._model.set_error(f"File not found: {file_path}")
                return False

            if not path.is_file():
                self._model.set_error(f"Not a file: {file_path}")
                return False

            # Use Qt document for PDF operations
            # The presenter acts as an abstraction layer over the Qt backend
            if self._qt_document:
                result = self._qt_document.load(file_path)

                if result == QPdfDocument.Error.None_:
                    page_count = self._qt_document.pageCount()
                    page_sizes = []

                    for i in range(page_count):
                        size = self._qt_document.pagePointSize(i)
                        page_sizes.append((size.width(), size.height()))

                    self._model.update_from_document_info(
                        file_path=file_path,
                        page_count=page_count,
                        page_sizes=page_sizes,
                    )

                    logger.info(f"Document loaded: {file_path} ({page_count} pages)")
                    return True
                else:
                    error_msg = self._get_error_message(result)
                    self._model.set_error(error_msg)
                    logger.error(f"Failed to load document: {error_msg}")
                    return False
            else:
                # Testing mode: update model without Qt backend
                # This allows unit tests to run without Qt dependencies
                self._model.file_path = file_path
                self._model.is_loaded = True
                logger.warning("Document presenter loaded without Qt backend")
                return True

        except DocumentLoadError:
            raise
        except Exception as e:
            error_msg = str(e)
            self._model.set_error(error_msg)
            logger.error(f"Error loading document: {error_msg}")
            raise DocumentLoadError(file_path, error_msg) from e

    def get_page_count(self) -> int:
        """Get the number of pages in the document.

        Returns:
            Number of pages, or 0 if no document is loaded
        """
        if self._qt_document:
            return self._qt_document.pageCount()
        return self._model.page_count

    def get_page_size(self, page_index: int) -> Optional[tuple[float, float]]:
        """Get the size of a specific page in points.

        Args:
            page_index: Zero-based page index

        Returns:
            Tuple of (width, height) in points, or None if page index is invalid
        """
        # Check for empty document first
        page_count = self.get_page_count()
        if page_count == 0:
            return None

        if self._qt_document and page_index >= 0 and page_index < page_count:
            size = self._qt_document.pagePointSize(page_index)
            return (size.width(), size.height())
        return self._model.get_page_size(page_index)

    def is_document_loaded(self) -> bool:
        """Check if a document is currently loaded.

        Returns:
            True if a document is loaded and ready for operations
        """
        return self._model.is_loaded

    def _on_model_changed(self, event: Any) -> None:
        """Handle model property changes.

        Args:
            event: Property changed event from the model
        """
        if self.has_view:
            self.update_view(**{event.property_name: event.new_value})

    def _get_error_message(self, error: QPdfDocument.Error) -> str:
        """Convert QPdfDocument error to user-friendly message.

        Args:
            error: QPdfDocument error code

        Returns:
            Error message string
        """
        error_messages = {
            QPdfDocument.Error.FileNotFound: "File not found",
            QPdfDocument.Error.InvalidFileFormat: "Invalid PDF format",
            QPdfDocument.Error.IncorrectPassword: "Password required",
            QPdfDocument.Error.UnsupportedSecurityScheme: "Unsupported security",
        }
        return error_messages.get(error, "Unknown error")

    def close_document(self) -> None:
        """Close the current document and reset to initial state.

        This method:
        - Closes the Qt PDF document
        - Clears the model state
        - Notifies observers of the change
        """
        logger.info("Closing current document")

        # Close the Qt document if loaded
        if self._qt_document:
            try:
                self._qt_document.close()
                logger.debug("Qt PDF document closed")
            except Exception as e:
                logger.warning(f"Error closing Qt PDF document: {e}")

        # Clear the model state
        self._model.clear()
        logger.info("Document closed and model cleared")

    def cleanup(self) -> None:
        """Release resources and remove model observers."""
        self._model.remove_observer(self._on_model_changed)

        # Properly close the Qt document before releasing reference
        if self._qt_document:
            try:
                self._qt_document.close()
            except Exception as e:
                logger.warning(f"Error closing PDF document: {e}")
            finally:
                self._qt_document = None

        super().cleanup()

    @property
    def model(self) -> Document:
        """Access the underlying document model."""
        return self._model

    @property
    def is_loaded(self) -> bool:
        """Backward compatibility property for is_document_loaded()."""
        return self._model.is_loaded

"""Margin presenter for handling margin calculations and logic.

This presenter manages margin operations without UI dependencies.
It coordinates between MarginSettingsModel and the view layer.
"""

from typing import Any, Optional

from momovu.lib.constants import (
    DEFAULT_SAFETY_MARGIN_MM,  # noqa: F401  # Imported for test_constants_imports.py
    FLAP_HEIGHT_RATIO,
    FLAP_WIDTH_RATIO,
    GUTTER_SIZE_THRESHOLDS,
    MM_TO_POINTS,
    SPINE_WIDTH_DIVISOR,
    SPINE_WIDTH_OFFSET,
)
from momovu.lib.logger import get_logger
from momovu.lib.sizes.dustjacket_spine_widths import get_dustjacket_spine_width
from momovu.models.margin_settings import MarginSettingsModel
from momovu.presenters.base import BasePresenter

logger = get_logger(__name__)


class MarginPresenter(BasePresenter):
    """Presenter for margin calculations and management.

    This presenter handles:
    - Margin calculations
    - Trim line positioning
    - Spine/flap calculations
    - Barcode area logic
    """

    def __init__(self, model: Optional[MarginSettingsModel] = None) -> None:
        """Initialize the margin presenter.

        Args:
            model: Optional margin settings model to use
        """
        super().__init__()
        self._model = model or MarginSettingsModel()

        self._model.add_observer(self._on_model_changed)

    def set_document_type(self, document_type: str) -> None:
        """Set the document type.

        Args:
            document_type: Type of document ('interior', 'cover', 'dustjacket')
        """
        self._model.document_type = document_type

        if document_type in ["cover", "dustjacket"]:
            self._calculate_spine_width()

            if document_type == "dustjacket":
                # Standard dustjacket flap dimensions from constants
                self._model.flap_width = FLAP_WIDTH_RATIO * MM_TO_POINTS
                self._model.flap_height = FLAP_HEIGHT_RATIO * MM_TO_POINTS

        # Calculate gutter width for interior documents
        if document_type == "interior":
            self._calculate_gutter_width()
        else:
            # No gutter for cover/dustjacket
            self._model.gutter_width = 0.0

        logger.info(f"Document type set to: {document_type}")

    def get_document_type(self) -> str:
        """Get the current document type.

        Returns:
            The current document type ('interior', 'cover', or 'dustjacket')
        """
        return self._model.document_type

    def set_num_pages(self, num_pages: int) -> None:
        """Update page count and recalculate spine width for cover/dustjacket.

        Args:
            num_pages: Total pages in the document
        """
        self._model.num_pages = num_pages
        if self._model.document_type in ["cover", "dustjacket"]:
            self._calculate_spine_width()
        elif self._model.document_type == "interior":
            self._calculate_gutter_width()

    def set_show_margins(self, show: bool) -> None:
        """Enable or disable safety margin overlay display.

        Args:
            show: True to display margin overlays
        """
        self._model.show_margins = show

    def set_show_trim_lines(self, show: bool) -> None:
        """Enable or disable trim line display at page edges.

        Args:
            show: True to display trim lines
        """
        self._model.show_trim_lines = show

    def set_show_barcode(self, show: bool) -> None:
        """Enable or disable barcode area indicator on covers.

        Args:
            show: True to display barcode area
        """
        self._model.show_barcode = show

    def set_show_fold_lines(self, show: bool) -> None:
        """Enable or disable spine/flap fold line display.

        Args:
            show: True to display fold lines
        """
        self._model.show_fold_lines = show

    def set_show_bleed_lines(self, show: bool) -> None:
        """Enable or disable bleed line display at page edges.

        Args:
            show: True to display bleed lines
        """
        self._model.show_bleed_lines = show

    def set_show_gutter(self, show: bool) -> None:
        """Enable or disable gutter margin display for interior documents.

        Args:
            show: True to display gutter margins
        """
        self._model.show_gutter = show

    def update_page_count(self, page_count: int) -> None:
        """Update gutter width based on actual document page count.

        This is called when a document is loaded to use actual page count
        instead of the num_pages spinbox value.

        Args:
            page_count: Actual number of pages in the loaded document
        """
        if self._model.document_type == "interior":
            self._calculate_gutter_width(page_count)

    def _calculate_gutter_width(self, page_count: Optional[int] = None) -> None:
        """Calculate gutter width based on page count for interior documents.

        Args:
            page_count: Optional page count to use (defaults to model's num_pages)
        """
        if self._model.document_type != "interior":
            self._model.gutter_width = 0.0
            return

        # Use provided page count or fall back to model's num_pages
        num_pages = page_count if page_count is not None else self._model.num_pages
        if num_pages <= 0:
            num_pages = 100  # Default

        # Find appropriate gutter size from thresholds
        gutter_width_mm = 0.0
        for threshold, width in GUTTER_SIZE_THRESHOLDS:
            if num_pages <= threshold:
                gutter_width_mm = width
                break

        self._model.gutter_width = gutter_width_mm * MM_TO_POINTS

        logger.info(
            f"Calculated gutter width: {gutter_width_mm:.2f}mm ({self._model.gutter_width:.2f} points) "
            f"for {num_pages} pages (interior document)"
        )

    def _calculate_spine_width(self) -> None:
        """Calculate spine thickness using appropriate method for document type."""
        num_pages = self._model.num_pages if self._model.num_pages > 0 else 100

        if self._model.document_type == "dustjacket":
            # Use lookup table for dustjackets
            spine_width_mm = get_dustjacket_spine_width(num_pages)
            calculation_method = "lookup table"
        else:
            # Use formula for covers (and fallback for other types)
            spine_width_mm = (num_pages / SPINE_WIDTH_DIVISOR) + SPINE_WIDTH_OFFSET
            calculation_method = "formula"

        self._model.spine_width = spine_width_mm * MM_TO_POINTS

        logger.info(
            f"Calculated spine width: {spine_width_mm:.2f}mm ({self._model.spine_width:.2f} points) "
            f"for {num_pages} pages using {calculation_method} ({self._model.document_type})"
        )

    def _on_model_changed(self, event: Any) -> None:
        """Handle model property changes.

        Args:
            event: Property changed event from the model
        """
        if self.has_view:
            self.update_view(**{event.property_name: event.new_value})

    def cleanup(self) -> None:
        """Remove model observer and release resources."""
        self._model.remove_observer(self._on_model_changed)
        super().cleanup()

    @property
    def model(self) -> MarginSettingsModel:
        """Access the underlying margin settings model."""
        return self._model

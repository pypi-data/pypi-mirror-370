"""Scroll controller for managing view scrolling to pages."""

from typing import Any

from momovu.lib.logger import get_logger
from momovu.views.components.page_positions import PagePositions

logger = get_logger(__name__)


class ScrollManager:
    """Manages scrolling the graphics view to show specific pages."""

    def __init__(
        self, graphics_view: Any, document_presenter: Any, navigation_presenter: Any
    ) -> None:
        """Initialize the scroll controller.

        Args:
            graphics_view: The QGraphicsView to control
            document_presenter: Presenter for document operations
            navigation_presenter: Presenter for navigation operations
        """
        self.graphics_view = graphics_view
        self.document_presenter = document_presenter
        self.navigation_presenter = navigation_presenter

        self.position_calculator = PagePositions(
            document_presenter, navigation_presenter
        )

    def scroll_to_current_page(self) -> None:
        """Center view on current page in stacked single-page layout."""
        current_page = self.navigation_presenter.get_current_page()
        center_x, center_y = self.position_calculator.calculate_single_page_position(
            current_page
        )

        if center_x > 0 or center_y > 0:
            self.graphics_view.centerOn(center_x, center_y)
            logger.debug(
                f"Scrolled to page {current_page + 1} at ({center_x}, {center_y})"
            )

    def scroll_to_current_page_pair(self) -> None:
        """Center view on current page pair in stacked side-by-side layout.

        Follows book convention: page 1 alone, then pairs (2-3), (4-5), etc.
        """
        current_page = self.navigation_presenter.get_current_page()
        center_x, center_y = self.position_calculator.calculate_page_pair_position(
            current_page
        )

        if center_x > 0 or center_y > 0:
            self.graphics_view.centerOn(center_x, center_y)
            logger.debug(
                f"Scrolled to page pair containing page {current_page + 1} at ({center_x}, {center_y})"
            )

"""Navigation presenter for handling page navigation logic.

This presenter manages navigation operations without UI dependencies.
It coordinates between ViewStateModel and the view layer.
"""

from typing import Any, Optional

from momovu.lib.logger import get_logger
from momovu.models.view_state import ViewStateModel
from momovu.presenters.base import BasePresenter

logger = get_logger(__name__)


class NavigationPresenter(BasePresenter):
    """Presenter for page navigation operations.

    This presenter handles:
    - Page navigation (next, previous, first, last)
    - Side-by-side pair navigation
    - Page jumping
    - Navigation validation
    """

    def __init__(
        self, model: Optional[ViewStateModel] = None, total_pages: int = 0
    ) -> None:
        """Initialize the navigation presenter.

        Args:
            model: Optional view state model to use
            total_pages: Total number of pages in the document
        """
        super().__init__()
        self._model = model or ViewStateModel()
        self._total_pages = total_pages

        self._model.add_observer(self._on_model_changed)

    def set_total_pages(self, total_pages: int) -> None:
        """Update page count and adjust current page if necessary.

        Args:
            total_pages: New total page count
        """
        self._total_pages = total_pages

        if self._model.current_page >= total_pages and total_pages > 0:
            self._model.current_page = total_pages - 1

        logger.info(f"Total pages set to: {total_pages}")

    def go_to_page(self, page_index: int) -> bool:
        """Navigate to a specific page.

        Args:
            page_index: Zero-based page index to navigate to

        Returns:
            True if navigation was successful
        """
        if page_index < 0 or page_index >= self._total_pages:
            logger.warning(f"Invalid page index: {page_index}")
            return False

        if self._model.is_side_by_side_mode() and page_index % 2 != 0:
            # Ensure we're on an even page for left side of spread
            page_index = max(0, page_index - 1)

        self._model.current_page = page_index
        logger.debug(f"Navigated to page {page_index}")
        return True

    def next_page(self) -> bool:
        """Advance to the next page or page pair in side-by-side mode.

        Returns:
            True if navigation occurred, False if already at end
        """
        if self._model.is_side_by_side_mode():
            # Check if we're near the end (within 2 pages)
            if self._model.current_page >= self._total_pages - 2:
                if self._model.current_page < self._total_pages - 1:
                    if self._total_pages == 1:
                        self._model.current_page = 0
                    elif self._total_pages % 2 == 0:
                        # Even total: last page appears alone on left
                        self._model.current_page = self._total_pages - 1
                    else:
                        # Odd total: last spread starts at second-to-last index
                        self._model.current_page = self._total_pages - 2
                    return True
                else:
                    logger.debug("Already at last page")
                    return False
            else:
                return self.go_to_page(self._model.current_page + 2)
        else:
            new_page = self._model.current_page + 1
            if new_page < self._total_pages:
                return self.go_to_page(new_page)

            logger.debug("Already at last page")
            return False

    def previous_page(self) -> bool:
        """Move back to the previous page or page pair in side-by-side mode.

        Returns:
            True if navigation occurred, False if already at start
        """
        if self._model.is_side_by_side_mode():
            # Move by 2 pages in side-by-side mode
            new_page = self._model.current_page - 2
        else:
            # Move by 1 page in single mode
            new_page = self._model.current_page - 1

        if new_page >= 0:
            return self.go_to_page(new_page)

        logger.debug("Already at first page")
        return False

    def go_to_first_page(self) -> bool:
        """Jump to the beginning of the document.

        Returns:
            True if navigation occurred
        """
        return self.go_to_page(0)

    def go_to_last_page(self) -> bool:
        """Jump to the end of the document, handling side-by-side edge cases.

        Returns:
            True if navigation occurred
        """
        if self._total_pages == 0:
            return False

        if self._model.is_side_by_side_mode():
            if self._total_pages == 1:
                # Special case: only one page
                self._model.current_page = 0
            elif self._total_pages % 2 == 0:
                # Even total: last page appears alone on left
                self._model.current_page = self._total_pages - 1
            else:
                # Odd total: last spread starts at second-to-last index
                self._model.current_page = self._total_pages - 2
            return True
        else:
            return self.go_to_page(self._total_pages - 1)

    def set_view_mode(self, mode: str) -> None:
        """Set the view mode.

        Args:
            mode: View mode ('single' or 'side_by_side')
        """
        if mode not in ["single", "side_by_side"]:
            logger.warning(f"Invalid view mode: {mode}")
            return

        old_mode = self._model.view_mode
        self._model.view_mode = mode

        logger.info(f"View mode changed from {old_mode} to {mode}")

    def toggle_view_mode(self) -> None:
        """Switch between single page and side-by-side page display."""
        old_mode = self._model.view_mode
        self._model.toggle_view_mode()

        logger.info(f"View mode changed from {old_mode} to {self._model.view_mode}")

    def get_current_page(self) -> int:
        """Get the zero-based index of the currently displayed page.

        Returns:
            Current page index (0 to total_pages-1)
        """
        return self._model.current_page

    def get_total_pages(self) -> int:
        """Get the total page count in the document.

        Returns:
            Number of pages, or 0 if no document loaded
        """
        return self._total_pages

    def get_current_page_pair(self) -> tuple[int, Optional[int]]:
        """Get the current page pair for side-by-side mode.

        Returns:
            Tuple of (left_page, right_page) where right_page may be None
        """
        if not self._model.is_side_by_side_mode():
            return (self._model.current_page, None)

        left_page = self._model.current_page
        right_page = left_page + 1 if left_page + 1 < self._total_pages else None

        return (left_page, right_page)

    def is_at_first_page(self) -> bool:
        """Check if navigation is at the document start.

        Returns:
            True if on page 0
        """
        return self._model.current_page == 0

    def is_at_last_page(self) -> bool:
        """Check if navigation is at the document end.

        Returns:
            True if no more pages can be navigated forward
        """
        if self._total_pages == 0:
            return True

        if self._model.is_side_by_side_mode():
            # In side-by-side, check if we can't go forward
            return self._model.current_page + 2 >= self._total_pages
        else:
            return self._model.current_page >= self._total_pages - 1

    def get_page_display_text(self) -> str:
        """Get formatted text for page display.

        Returns:
            Formatted page display text (e.g., "Page 1 of 10")
        """
        if self._total_pages == 0:
            return "No pages"

        if self._model.is_side_by_side_mode():
            left, right = self.get_current_page_pair()
            if right is not None:
                return f"Pages {left + 1}-{right + 1} of {self._total_pages}"
            else:
                return f"Page {left + 1} of {self._total_pages}"
        else:
            return f"Page {self._model.current_page + 1} of {self._total_pages}"

    def can_go_next(self) -> bool:
        """Check if forward navigation is available.

        Returns:
            True unless at the last page
        """
        return not self.is_at_last_page()

    def can_go_previous(self) -> bool:
        """Check if backward navigation is available.

        Returns:
            True unless at the first page
        """
        return not self.is_at_first_page()

    def _on_model_changed(self, event: Any) -> None:
        """Handle model property changes.

        Args:
            event: Property changed event from the model
        """
        if self.has_view:
            update_data = {event.property_name: event.new_value}

            if event.property_name in ["current_page", "view_mode"]:
                update_data["can_go_next"] = self.can_go_next()
                update_data["can_go_previous"] = self.can_go_previous()
                update_data["page_display"] = self.get_page_display_text()

            self.update_view(**update_data)

    def cleanup(self) -> None:
        """Remove model observer and release resources."""
        self._model.remove_observer(self._on_model_changed)
        super().cleanup()

    @property
    def model(self) -> ViewStateModel:
        """Access the underlying view state model."""
        return self._model

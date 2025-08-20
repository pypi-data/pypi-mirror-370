"""Centralized navigation controller - single source of truth for ALL navigation."""

from typing import Any, Callable, Optional

from momovu.lib.logger import get_logger
from momovu.views.components.scroll_manager import ScrollManager

logger = get_logger(__name__)


class NavigationController:
    """Controls all navigation in the application.

    This is the SINGLE place where navigation happens.
    No more scattered methods, no more event chains.
    """

    def __init__(self, main_window: Any) -> None:
        """Initialize the navigation controller.

        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self._scroll_controller: Optional[ScrollManager] = None

    @property
    def scroll_controller(self) -> Optional[ScrollManager]:
        """Lazy initialization of scroll controller."""
        if self._scroll_controller is None and hasattr(
            self.main_window, "graphics_view"
        ):
            self._scroll_controller = ScrollManager(
                self.main_window.graphics_view,
                self.main_window.document_presenter,
                self.main_window.navigation_presenter,
            )
        return self._scroll_controller

    def navigate_first(self) -> None:
        """Navigate to the first page."""
        if not self._has_navigation_presenter():
            logger.warning("Navigation attempted before presenter initialized")
            return
        self._navigate(self.main_window.navigation_presenter.go_to_first_page, "first")

    def navigate_previous(self) -> None:
        """Navigate to the previous page or page pair in side-by-side mode."""
        if not self._has_navigation_presenter():
            logger.warning("Navigation attempted before presenter initialized")
            return
        self._navigate(self.main_window.navigation_presenter.previous_page, "previous")

    def navigate_next(self) -> None:
        """Navigate to the next page or page pair in side-by-side mode."""
        if not self._has_navigation_presenter():
            logger.warning("Navigation attempted before presenter initialized")
            return
        self._navigate(self.main_window.navigation_presenter.next_page, "next")

    def navigate_last(self) -> None:
        """Navigate to the last page."""
        if not self._has_navigation_presenter():
            logger.warning("Navigation attempted before presenter initialized")
            return
        self._navigate(self.main_window.navigation_presenter.go_to_last_page, "last")

    def navigate_to_page(self, page_number: int) -> None:
        """Navigate to a specific page by number.

        Args:
            page_number: 1-based page number to navigate to
        """
        if not self._has_navigation_presenter():
            logger.warning("Navigation attempted before presenter initialized")
            return
        self._navigate(
            lambda: self.main_window.navigation_presenter.go_to_page(page_number - 1),
            f"page {page_number}",
        )

    def on_page_number_changed(self, value: int) -> None:
        """Handle page number spinbox change.

        Args:
            value: New page number (1-based)
        """
        self.navigate_to_page(value)

    def _navigate(self, nav_func: Callable[[], None], description: str) -> None:
        """Execute navigation and update all UI elements.

        This is the ONLY place where navigation state changes happen.

        Args:
            nav_func: The navigation function to call
            description: Description for logging
        """
        nav_func()

        self.main_window.update_page_label()
        self._handle_page_change()

        logger.debug(f"Navigated to {description}")

        # Save state after navigation
        if hasattr(self.main_window, "state_saver"):
            self.main_window.state_saver.save_state()

    def _handle_page_change(self) -> None:
        """Update the view after navigation based on current mode and document type.

        Behavior:
        - Presentation mode: Always re-render
        - Side-by-side interior: Scroll to page pair
        - Single page interior: Scroll to page
        - Cover/dustjacket: Re-render
        """
        if self.main_window.is_presentation_mode:
            self.main_window.render_current_page()
        elif (
            self.main_window.navigation_presenter.model.view_mode == "side_by_side"
            and self.main_window.margin_presenter.model.document_type == "interior"
        ):
            if self.scroll_controller:
                self.scroll_controller.scroll_to_current_page_pair()
        elif self.main_window.margin_presenter.model.document_type == "interior":
            if self.scroll_controller:
                self.scroll_controller.scroll_to_current_page()
        else:
            self.main_window.render_current_page()

    def _has_navigation_presenter(self) -> bool:
        """Check if navigation presenter is available."""
        return (
            hasattr(self.main_window, "navigation_presenter")
            and self.main_window.navigation_presenter is not None
        )

"""UI state manager component for handling presentation and fullscreen modes."""

from typing import Any

from PySide6.QtCore import Qt, QTimer

from momovu.lib.constants import (
    COMPLETE_TRANSITION_DELAY,
    FIT_TO_PAGE_DELAY,
    PRESENTATION_ENTER_DELAY,
    PRESENTATION_EXIT_DELAY,
    STANDARD_TRANSITION_DELAY,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class UIStateManager:
    """Manages UI state transitions like presentation and fullscreen modes."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the UI state manager.

        Args:
            main_window: The main window to manage
        """
        self.main_window = main_window
        self.is_presentation_mode = False
        self._transition_in_progress = False
        self._pending_timers: list[QTimer] = []

    def _cancel_pending_timers(self) -> None:
        """Stop all active transition timers to prevent conflicting state changes."""
        for timer in self._pending_timers:
            if timer and timer.isActive():
                timer.stop()
        self._pending_timers.clear()

    def _add_timer(self, delay: int, callback: Any) -> None:
        """Create a tracked timer for delayed UI operations during transitions.

        Args:
            delay: Milliseconds before callback execution
            callback: Function to call after delay
        """
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.timeout.connect(
            lambda: (
                self._pending_timers.remove(timer)
                if timer in self._pending_timers
                else None
            )
        )
        self._pending_timers.append(timer)
        timer.start(delay)

    def toggle_fullscreen(self) -> None:
        """Switch between fullscreen and maximized window states."""
        if self._transition_in_progress:
            logger.debug("Transition already in progress, ignoring fullscreen toggle")
            return

        self._transition_in_progress = True
        self._cancel_pending_timers()

        if self.main_window.isFullScreen():
            self.main_window.setWindowState(
                self.main_window.windowState() & ~Qt.WindowState.WindowFullScreen
                | Qt.WindowState.WindowMaximized
            )
            self.main_window.menuBar().show()
            self.main_window.toolbar.show()
        else:
            self.main_window.menuBar().hide()
            self.main_window.toolbar.hide()
            self.main_window.setWindowState(
                self.main_window.windowState() | Qt.WindowState.WindowFullScreen
            )

        logger.info(f"Fullscreen: {self.main_window.isFullScreen()}")

        self._add_timer(
            STANDARD_TRANSITION_DELAY,
            lambda: setattr(self, "_transition_in_progress", False),
        )

    def toggle_presentation(self) -> None:
        """Switch between presentation mode and normal viewing mode."""
        if self._transition_in_progress:
            logger.debug("Transition already in progress, ignoring presentation toggle")
            return

        if (
            self.main_window.isFullScreen()
            and not self.main_window.menuBar().isVisible()
        ):
            self.main_window.presentation_action.setChecked(False)
            self.exit_presentation_mode()
        else:
            self.main_window.presentation_action.setChecked(True)
            self.enter_presentation_mode()

    def enter_presentation_mode(self) -> None:
        """Hide all UI chrome and enter fullscreen for distraction-free viewing."""
        if self._transition_in_progress:
            logger.debug("Transition already in progress, ignoring enter presentation")
            return

        self._transition_in_progress = True
        self._cancel_pending_timers()

        self.is_presentation_mode = True
        self.main_window.menuBar().hide()
        self.main_window.toolbar.hide()
        self.main_window.setWindowState(
            self.main_window.windowState() | Qt.WindowState.WindowFullScreen
        )
        self.main_window.presentation_action.setChecked(True)

        # Set presentation mode flag on scene for PageItem to check
        if hasattr(self.main_window, "graphics_scene"):
            self.main_window.graphics_scene.is_presentation_mode = True

        # Hide scrollbars in presentation mode
        if hasattr(self.main_window, "graphics_view"):
            self.main_window.graphics_view.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.main_window.graphics_view.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        self._add_timer(PRESENTATION_ENTER_DELAY, self._render_after_presentation_enter)
        logger.info("Entered presentation mode")

    def _render_after_presentation_enter(self) -> None:
        """Re-render and fit page after presentation mode transition completes."""
        self.main_window.render_current_page()
        self._add_timer(FIT_TO_PAGE_DELAY, self.main_window.fit_to_page)
        self._add_timer(
            COMPLETE_TRANSITION_DELAY,
            lambda: setattr(self, "_transition_in_progress", False),
        )

    def exit_presentation_mode(self) -> None:
        """Restore UI elements and return to windowed viewing mode."""
        if self._transition_in_progress:
            logger.debug("Transition already in progress, ignoring exit presentation")
            return

        self._transition_in_progress = True
        self._cancel_pending_timers()

        self.is_presentation_mode = False
        self.main_window.presentation_action.setChecked(False)

        self.main_window.setWindowState(
            self.main_window.windowState() & ~Qt.WindowState.WindowFullScreen
            | Qt.WindowState.WindowMaximized
        )

        self.main_window.menuBar().show()
        self.main_window.toolbar.show()

        # Clear presentation mode flag on scene
        if hasattr(self.main_window, "graphics_scene"):
            self.main_window.graphics_scene.is_presentation_mode = False

        # Restore scrollbars
        if hasattr(self.main_window, "graphics_view"):
            self.main_window.graphics_view.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self.main_window.graphics_view.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )

        # Note: Removed QApplication.processEvents() to prevent re-entrancy issues

        self.main_window.render_current_page()

        if self.main_window.navigation_presenter.model.view_mode == "side_by_side":
            self._add_timer(
                PRESENTATION_EXIT_DELAY, self._scroll_to_current_page_and_fit
            )
        else:
            self._add_timer(FIT_TO_PAGE_DELAY, self.main_window.fit_to_page)

        self._add_timer(
            COMPLETE_TRANSITION_DELAY,
            lambda: setattr(self, "_transition_in_progress", False),
        )

        logger.info("Exited presentation mode")

    def _scroll_to_current_page_and_fit(self) -> None:
        """Center the view on the current page pair after exiting presentation mode."""
        current_page = self.main_window.navigation_presenter.get_current_page()
        logger.info(
            f"[DIAGNOSTIC] _scroll_to_current_page_and_fit: Looking for page {current_page}"
        )

        from momovu.views.page_item import PageItem

        all_scene_items = self.main_window.graphics_scene.items()
        all_page_items = [
            item for item in all_scene_items if isinstance(item, PageItem)
        ]
        page_numbers_in_scene = sorted([item.page_number for item in all_page_items])

        logger.info(f"[DIAGNOSTIC] Total items in scene: {len(all_scene_items)}")
        logger.info(f"[DIAGNOSTIC] PageItems in scene: {len(all_page_items)}")
        if page_numbers_in_scene:
            logger.info(
                f"[DIAGNOSTIC] Page numbers found: {page_numbers_in_scene[:10]}..."
                if len(page_numbers_in_scene) > 10
                else f"[DIAGNOSTIC] Page numbers found: {page_numbers_in_scene}"
            )
            logger.info(
                f"[DIAGNOSTIC] Min page: {min(page_numbers_in_scene)}, Max page: {max(page_numbers_in_scene)}"
            )
        else:
            logger.warning("[DIAGNOSTIC] No PageItems found in scene!")

        page_items = [
            item for item in all_page_items if item.page_number == current_page
        ]

        logger.info(
            f"[DIAGNOSTIC] Found {len(page_items)} PageItem(s) with page_number={current_page}"
        )

        if page_items:
            page_item = page_items[0]
            page_rect = page_item.mapRectToScene(page_item.boundingRect())
            logger.info(
                f"[DIAGNOSTIC] Using first PageItem at position: {page_rect.center()}"
            )

            if len(page_items) > 1:
                logger.warning(
                    f"[DIAGNOSTIC] WARNING: Found {len(page_items)} duplicate PageItems for page {current_page}!"
                )

            # For side-by-side, we need to show the page pair
            if current_page == 0:
                self.main_window.graphics_view.centerOn(page_rect.center())
            elif current_page % 2 == 1:
                right_page_items = [
                    item
                    for item in self.main_window.graphics_scene.items()
                    if isinstance(item, PageItem)
                    and item.page_number == current_page + 1
                ]
                if right_page_items:
                    right_rect = right_page_items[0].mapRectToScene(
                        right_page_items[0].boundingRect()
                    )
                    center_x = (page_rect.left() + right_rect.right()) / 2
                    center_y = page_rect.center().y()
                    self.main_window.graphics_view.centerOn(center_x, center_y)
                else:
                    self.main_window.graphics_view.centerOn(page_rect.center())
            else:
                left_page_items = [
                    item
                    for item in self.main_window.graphics_scene.items()
                    if isinstance(item, PageItem)
                    and item.page_number == current_page - 1
                ]
                if left_page_items:
                    left_rect = left_page_items[0].mapRectToScene(
                        left_page_items[0].boundingRect()
                    )
                    center_x = (left_rect.left() + page_rect.right()) / 2
                    center_y = page_rect.center().y()
                    self.main_window.graphics_view.centerOn(center_x, center_y)
                else:
                    self.main_window.graphics_view.centerOn(page_rect.center())

            # Don't call fit_entire_scene as it causes the pages to disappear
        else:
            logger.warning(
                f"[DIAGNOSTIC] No PageItem found for current page {current_page}!"
            )
            logger.warning(
                "[DIAGNOSTIC] Scene might be in transition or stale items present"
            )
            if all_page_items:
                logger.info(
                    f"[DIAGNOSTIC] Closest pages available: {sorted([abs(item.page_number - current_page) for item in all_page_items])[:5]}"
                )

    def apply_window_state(
        self, start_fullscreen: bool, start_presentation: bool
    ) -> None:
        """Set initial window display state based on startup parameters.

        Args:
            start_fullscreen: True to start in fullscreen mode
            start_presentation: True to start in presentation mode
        """
        if start_fullscreen:
            self.main_window.showFullScreen()
        else:
            self.main_window.showMaximized()

        if start_presentation:
            self.enter_presentation_mode()

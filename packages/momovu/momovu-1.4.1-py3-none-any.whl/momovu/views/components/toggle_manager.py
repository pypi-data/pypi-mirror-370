"""Toggle manager component for handling all UI toggle operations."""

from typing import Any, Optional

from PySide6.QtCore import QTimer

from momovu.lib.constants import IMMEDIATE_DELAY
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class ToggleManager:
    """Manages all toggle operations for the main window."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the toggle manager.

        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self._side_by_side_transition_in_progress = False
        self._side_by_side_timer: Optional[QTimer] = None

    def toggle_fullscreen(self) -> None:
        """Switch between fullscreen and windowed display modes."""
        self.main_window.ui_state_manager.toggle_fullscreen()
        logger.debug("Fullscreen toggled")

    def toggle_presentation(self) -> None:
        """Switch between presentation mode (fullscreen, no UI) and normal mode."""
        self.main_window.ui_state_manager.toggle_presentation()
        self.main_window.is_presentation_mode = (
            self.main_window.ui_state_manager.is_presentation_mode
        )
        logger.debug(f"Presentation mode: {self.main_window.is_presentation_mode}")

    def enter_presentation_mode(self) -> None:
        """Enable presentation mode with fullscreen display and hidden UI elements."""
        self.main_window.ui_state_manager.enter_presentation_mode()
        self.main_window.is_presentation_mode = (
            self.main_window.ui_state_manager.is_presentation_mode
        )
        logger.debug("Entered presentation mode")

    def exit_presentation_mode(self) -> None:
        """Return to normal viewing mode with visible UI elements."""
        self.main_window.ui_state_manager.exit_presentation_mode()
        self.main_window.is_presentation_mode = (
            self.main_window.ui_state_manager.is_presentation_mode
        )
        # Note: ui_state_manager.exit_presentation_mode() handles everything including:
        # - Restoring UI elements
        # - Re-rendering the page
        # - Scrolling to the current page for interior documents
        logger.debug("Exited presentation mode")

    def toggle_side_by_side(self) -> None:
        """Switch between single page and side-by-side page display for interior documents."""
        if self._side_by_side_transition_in_progress:
            logger.debug("Side-by-side transition already in progress, ignoring toggle")
            return

        if self._side_by_side_timer and self._side_by_side_timer.isActive():
            self._side_by_side_timer.stop()

        self._side_by_side_transition_in_progress = True

        current_page = self.main_window.navigation_presenter.get_current_page()
        logger.debug(f"Storing current page before view mode change: {current_page}")

        if self.main_window.side_by_side_action.isChecked():
            self.main_window.navigation_presenter.set_view_mode("side_by_side")
            # Set spinbox to increment by 2 in side-by-side mode
            if self.main_window.page_number_spinbox:
                self.main_window.page_number_spinbox.setSingleStep(2)
        else:
            self.main_window.navigation_presenter.set_view_mode("single")
            # Reset spinbox to increment by 1 in single page mode
            if self.main_window.page_number_spinbox:
                self.main_window.page_number_spinbox.setSingleStep(1)

        # Prevent the flash by disabling viewport updates during the transition
        view = self.main_window.graphics_view

        # Note: Removed QApplication.processEvents() to prevent re-entrancy issues

        view.setViewportUpdateMode(view.ViewportUpdateMode.NoViewportUpdate)
        view.setUpdatesEnabled(False)

        self.main_window.render_current_page()
        logger.debug(
            f"Side-by-side: {self.main_window.side_by_side_action.isChecked()}"
        )

        def restore_page_position() -> None:
            """Restore the page position after view mode change."""
            try:
                if (
                    self.main_window.navigation_presenter.get_current_page()
                    != current_page
                ):
                    logger.warning(
                        f"Page changed during transition from {current_page} to {self.main_window.navigation_presenter.get_current_page()}"
                    )
                    self.main_window.navigation_presenter.set_current_page(current_page)

                from momovu.views.page_item import PageItem

                page_items = [
                    item
                    for item in self.main_window.graphics_scene.items()
                    if isinstance(item, PageItem) and item.page_number == current_page
                ]

                if page_items:
                    page_item = page_items[0]
                    page_rect = page_item.mapRectToScene(page_item.boundingRect())

                    # For side-by-side view, we might need to center on the pair
                    if (
                        self.main_window.navigation_presenter.model.view_mode
                        == "side_by_side"
                    ):
                        if current_page > 0 and current_page % 2 == 0:
                            left_items = [
                                item
                                for item in self.main_window.graphics_scene.items()
                                if isinstance(item, PageItem)
                                and item.page_number == current_page - 1
                            ]
                            if left_items:
                                left_rect = left_items[0].mapRectToScene(
                                    left_items[0].boundingRect()
                                )
                                center_x = (left_rect.left() + page_rect.right()) / 2
                                center_y = page_rect.center().y()
                                self.main_window.graphics_view.centerOn(
                                    center_x, center_y
                                )
                            else:
                                self.main_window.graphics_view.centerOn(
                                    page_rect.center()
                                )
                        elif current_page % 2 == 1:
                            right_items = [
                                item
                                for item in self.main_window.graphics_scene.items()
                                if isinstance(item, PageItem)
                                and item.page_number == current_page + 1
                            ]
                            if right_items:
                                right_rect = right_items[0].mapRectToScene(
                                    right_items[0].boundingRect()
                                )
                                center_x = (page_rect.left() + right_rect.right()) / 2
                                center_y = page_rect.center().y()
                                self.main_window.graphics_view.centerOn(
                                    center_x, center_y
                                )
                            else:
                                self.main_window.graphics_view.centerOn(
                                    page_rect.center()
                                )
                        else:
                            self.main_window.graphics_view.centerOn(page_rect.center())
                    else:
                        self.main_window.graphics_view.centerOn(page_rect.center())

                    logger.debug(
                        f"Scrolled to page {current_page} after view mode change"
                    )
                else:
                    logger.warning(
                        f"Could not find PageItem for page {current_page} after view mode change"
                    )

                self.main_window.update_page_label()

            except Exception as e:
                logger.error(f"Error restoring page position: {e}")
            finally:
                self._side_by_side_transition_in_progress = False

        def restore_and_enable_updates() -> None:
            restore_page_position()
            view.setUpdatesEnabled(True)
            view.setViewportUpdateMode(view.ViewportUpdateMode.MinimalViewportUpdate)
            view.viewport().update()

        self._side_by_side_timer = QTimer()
        self._side_by_side_timer.setSingleShot(True)
        self._side_by_side_timer.timeout.connect(restore_and_enable_updates)
        self._side_by_side_timer.start(IMMEDIATE_DELAY)  # Next event loop

    def toggle_margins(self) -> None:
        """Show or hide the safety margin overlays on pages."""
        show = self.main_window.show_margins_action.isChecked()
        self.main_window.margin_presenter.set_show_margins(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Margins visible: {show}")

    def toggle_trim_lines(self) -> None:
        """Show or hide the trim/cut lines at page edges."""
        show = self.main_window.show_trim_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_trim_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Trim lines visible: {show}")

    def toggle_barcode(self) -> None:
        """Show or hide the barcode area indicator on cover/dustjacket documents."""
        show = self.main_window.show_barcode_action.isChecked()
        self.main_window.margin_presenter.set_show_barcode(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Barcode visible: {show}")

    def toggle_fold_lines(self) -> None:
        """Show or hide the spine/flap fold lines on cover/dustjacket documents."""
        show = self.main_window.show_fold_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_fold_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Fold lines visible: {show}")

    def toggle_bleed_lines(self) -> None:
        """Show or hide the bleed lines at page edges on cover/dustjacket documents."""
        show = self.main_window.show_bleed_lines_action.isChecked()
        self.main_window.margin_presenter.set_show_bleed_lines(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Bleed lines visible: {show}")

    def toggle_gutter(self) -> None:
        """Show or hide the gutter margin on interior documents."""
        show = self.main_window.show_gutter_action.isChecked()
        self.main_window.margin_presenter.set_show_gutter(show)

        # Skip refit in presentation mode to prevent resize
        skip_fit = self.main_window.ui_state_manager.is_presentation_mode
        self.main_window.render_current_page(skip_fit=skip_fit)

        logger.debug(f"Gutter visible: {show}")

    def set_document_type(self, doc_type: str) -> None:
        """Change the document type and update UI accordingly.

        Args:
            doc_type: One of 'interior', 'cover', or 'dustjacket'
        """
        self.main_window.interior_action.setChecked(doc_type == "interior")
        self.main_window.cover_action.setChecked(doc_type == "cover")
        self.main_window.dustjacket_action.setChecked(doc_type == "dustjacket")
        self.main_window.margin_presenter.set_document_type(doc_type)

        if hasattr(self.main_window, "menu_builder") and self.main_window.menu_builder:
            self.main_window.menu_builder.update_view_menu_for_document_type(doc_type)

        self.main_window.render_current_page()
        logger.info(f"Document type set to: {doc_type}")

        if (
            hasattr(self.main_window, "toolbar_builder")
            and self.main_window.toolbar_builder
        ):
            self.main_window.toolbar_builder.update_toolbar_visibility()

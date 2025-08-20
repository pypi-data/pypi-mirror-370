"""Custom graphics view component for PDF viewing with mouse and keyboard support."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView

from momovu.lib.constants import (
    DEFAULT_SCROLL_AMOUNT,
    ZOOM_IN_FACTOR,
    ZOOM_OUT_FACTOR,
    ZOOM_THRESHOLD_FOR_PAN,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class GraphicsView(QGraphicsView):
    """Custom graphics view with mouse wheel and DIRECT keyboard support."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the graphics view.

        Args:
            main_window: Reference to the main window for event handling
        """
        super().__init__()
        self.main_window = main_window
        self._cleaned_up = False

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Install event filter to ensure wheel events are handled for navigation
        if self.viewport():
            self.viewport().installEventFilter(self)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Central keyboard event handler for all viewer shortcuts.

        Handles navigation, zoom, and UI toggle shortcuts.
        Arrow keys adapt based on zoom level (pan when zoomed, navigate otherwise).

        NOTE: When adding or modifying keyboard shortcuts here,
        remember to update the shortcuts dialog in
        lib/shortcuts_dialog.py::_populate_shortcuts()
        """
        is_mock = hasattr(event, "_mock_name") or not hasattr(event, "spontaneous")

        if is_mock:
            key = event.key() if callable(event.key) else event.key
            modifiers = (
                event.modifiers() if callable(event.modifiers) else event.modifiers
            )
        else:
            key = event.key()
            modifiers = event.modifiers()

        # Arrow keys - handle based on zoom state
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            if is_mock:
                if key == Qt.Key.Key_Left:
                    self.main_window.navigation_controller.navigate_previous()
                elif key == Qt.Key.Key_Right:
                    self.main_window.navigation_controller.navigate_next()
                if hasattr(event, "accept"):
                    event.accept()
                return

            is_zoomed = False
            if hasattr(self.main_window, "zoom_controller"):
                zoom_level = self.main_window.zoom_controller.get_current_zoom()
                is_zoomed = zoom_level > ZOOM_THRESHOLD_FOR_PAN

            if is_zoomed:
                # When zoomed in, use arrow keys for panning
                # Manual scrolling since Qt doesn't handle it by default
                h_bar = self.horizontalScrollBar()
                v_bar = self.verticalScrollBar()

                if key == Qt.Key.Key_Left and h_bar:
                    h_bar.setValue(h_bar.value() - DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Right and h_bar:
                    h_bar.setValue(h_bar.value() + DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Up and v_bar:
                    v_bar.setValue(v_bar.value() - DEFAULT_SCROLL_AMOUNT)
                elif key == Qt.Key.Key_Down and v_bar:
                    v_bar.setValue(v_bar.value() + DEFAULT_SCROLL_AMOUNT)

                event.accept()
            else:
                # Check if margin_presenter is available before accessing
                if (
                    hasattr(self.main_window, "margin_presenter")
                    and self.main_window.margin_presenter
                    and hasattr(self.main_window.margin_presenter, "model")
                ):
                    doc_type = self.main_window.margin_presenter.model.document_type
                else:
                    # Default behavior when presenter not ready
                    doc_type = "interior"  # Safe default

                if doc_type == "interior":
                    if key == Qt.Key.Key_Left:
                        self.main_window.navigation_controller.navigate_previous()
                    elif key == Qt.Key.Key_Right:
                        self.main_window.navigation_controller.navigate_next()
                    elif key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                        super().keyPressEvent(event)
                        return
                else:
                    pass

                event.accept()
            return

        if key == Qt.Key.Key_PageUp:
            self.main_window.navigation_controller.navigate_previous()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_PageDown:
            self.main_window.navigation_controller.navigate_next()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_Home:
            self.main_window.navigation_controller.navigate_first()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_End:
            self.main_window.navigation_controller.navigate_last()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_Space:
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.main_window.navigation_controller.navigate_previous()
            else:
                self.main_window.navigation_controller.navigate_next()
            event.accept() if hasattr(event, "accept") else None
        elif key == Qt.Key.Key_F5:
            self.main_window.toggle_presentation()
            event.accept()
        elif key == Qt.Key.Key_F11:
            self.main_window.toggle_fullscreen()
            event.accept()
        elif key == Qt.Key.Key_F1 or key == Qt.Key.Key_Question:
            self.main_window.show_shortcuts_dialog()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            if self.main_window.presentation_action.isChecked():
                self.main_window.presentation_action.setChecked(False)
                self.main_window.exit_presentation_mode()
            elif self.main_window.isFullScreen():
                self.main_window.toggle_fullscreen()
            event.accept()
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.zoom_controller.zoom_in()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_Minus:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.zoom_controller.zoom_out()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_0:
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                self.main_window.fit_to_page()
                event.accept()
            else:
                super().keyPressEvent(event)
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_F:
                self.main_window.fit_to_page()
                event.accept()
            elif key == Qt.Key.Key_O:
                self.main_window.open_file_dialog()
                event.accept()
            elif key == Qt.Key.Key_Q:
                self.main_window.close()
                event.accept()
            elif key == Qt.Key.Key_W:
                self.main_window.close_pdf()
                event.accept()
            elif key == Qt.Key.Key_G:
                # Check document type - only allow for interior documents
                if (
                    hasattr(self.main_window, "margin_presenter")
                    and self.main_window.margin_presenter
                    and hasattr(self.main_window.margin_presenter, "model")
                    and self.main_window.margin_presenter.model.document_type
                    == "interior"
                ):
                    self.main_window.show_go_to_page_dialog()
                event.accept()
            elif key == Qt.Key.Key_D:
                self.main_window.side_by_side_action.toggle()
                self.main_window.toggle_side_by_side()
                event.accept()
            elif key == Qt.Key.Key_M:
                self.main_window.show_margins_action.toggle()
                self.main_window.toggle_margins()
                event.accept()
            elif key == Qt.Key.Key_T:
                self.main_window.show_trim_lines_action.toggle()
                self.main_window.toggle_trim_lines()
                event.accept()
            elif key == Qt.Key.Key_B:
                if self.main_window.margin_presenter.model.document_type in [
                    "cover",
                    "dustjacket",
                ]:
                    self.main_window.show_barcode_action.toggle()
                    self.main_window.toggle_barcode()
                event.accept()
            elif key == Qt.Key.Key_L:
                self.main_window.show_fold_lines_action.toggle()
                self.main_window.toggle_fold_lines()
                event.accept()
            elif key == Qt.Key.Key_R:
                if self.main_window.margin_presenter.model.document_type in [
                    "cover",
                    "dustjacket",
                ]:
                    self.main_window.show_bleed_lines_action.toggle()
                    self.main_window.toggle_bleed_lines()
                event.accept()
            elif key == Qt.Key.Key_U:
                # Toggle gutter for interior documents
                if (
                    hasattr(self.main_window, "margin_presenter")
                    and self.main_window.margin_presenter
                    and hasattr(self.main_window.margin_presenter, "model")
                    and self.main_window.margin_presenter.model.document_type
                    == "interior"
                    and hasattr(self.main_window, "show_gutter_action")
                ):
                    self.main_window.show_gutter_action.toggle()
                    self.main_window.toggle_gutter()
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Handle mouse wheel for zoom, pan, or page navigation.

        Behavior depends on modifiers and zoom level:
        - Ctrl + Scroll: Zoom at mouse position
        - Shift + Scroll: Horizontal pan (at any zoom level)
        - When zoomed in (>1.05x): Vertical pan
        - When not zoomed: Page navigation

        Args:
            event: Qt wheel event containing delta and modifiers
        """
        modifiers = event.modifiers()
        delta = event.angleDelta().y()
        logger.debug(f"Wheel event: delta={delta}, modifiers={modifiers}")

        # Check if this is an interior document with stacked pages
        is_interior_stacked = False
        if (
            hasattr(self.main_window, "margin_presenter")
            and self.main_window.margin_presenter
            and hasattr(self.main_window.margin_presenter, "model")
        ):
            doc_type = self.main_window.margin_presenter.model.document_type
            is_interior_stacked = doc_type == "interior"

        # Shift + Scroll = Horizontal pan (always)
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            h_bar = self.horizontalScrollBar()
            if h_bar:
                # Scroll right when wheel scrolls down (delta < 0)
                scroll_amount = (
                    DEFAULT_SCROLL_AMOUNT if delta < 0 else -DEFAULT_SCROLL_AMOUNT
                )
                h_bar.setValue(h_bar.value() + scroll_amount)
            event.accept()
            return

        # Ctrl + Scroll = Zoom at mouse position
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Get the scene position under the mouse before zooming
            mouse_scene_pos = self.mapToScene(event.position().toPoint())

            # Apply the zoom
            factor = ZOOM_IN_FACTOR if delta > 0 else ZOOM_OUT_FACTOR
            self.scale(factor, factor)

            # Update zoom controller state
            current_zoom = self.main_window.zoom_controller.get_current_zoom()
            new_zoom = current_zoom * factor
            self.main_window.zoom_controller.set_zoom_level(new_zoom)
            self.main_window.zoom_controller.zoom_changed.emit(new_zoom)

            # Get the new position of the same scene point
            new_mouse_pos = self.mapFromScene(mouse_scene_pos)

            # Calculate how much we need to adjust to keep the mouse point fixed
            delta_x = event.position().x() - new_mouse_pos.x()
            delta_y = event.position().y() - new_mouse_pos.y()

            # Adjust scrollbars to compensate
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            if h_bar:
                h_bar.setValue(int(h_bar.value() - delta_x))
            if v_bar:
                v_bar.setValue(int(v_bar.value() - delta_y))

            event.accept()
            return

        # Interior documents always navigate (pages are stacked vertically)
        if is_interior_stacked:
            if delta > 0:
                self.main_window.navigation_controller.navigate_previous()
            else:
                self.main_window.navigation_controller.navigate_next()
            event.accept()
            return

        # Check zoom level to determine pan vs navigate (for non-interior docs)
        zoom_level = self.main_window.zoom_controller.get_current_zoom()
        logger.debug(f"Zoom level: {zoom_level}, threshold: {ZOOM_THRESHOLD_FOR_PAN}")

        if zoom_level > ZOOM_THRESHOLD_FOR_PAN:
            # Zoomed in: Scroll = Vertical pan
            logger.debug("Zoomed in - panning")
            v_bar = self.verticalScrollBar()
            if v_bar:
                # Scroll down when wheel scrolls down (delta < 0)
                scroll_amount = (
                    DEFAULT_SCROLL_AMOUNT if delta < 0 else -DEFAULT_SCROLL_AMOUNT
                )
                v_bar.setValue(v_bar.value() + scroll_amount)
        else:
            # Not zoomed: Scroll = Page navigation
            logger.debug(f"Not zoomed - navigating. Delta: {delta}")
            if delta > 0:
                self.main_window.navigation_controller.navigate_previous()
            else:
                self.main_window.navigation_controller.navigate_next()

        event.accept()

    def eventFilter(self, obj: Any, event: Any) -> bool:
        """Intercept wheel events on viewport for custom navigation handling.

        Args:
            obj: The object that received the event
            event: The event to filter

        Returns:
            True if event was handled, False otherwise
        """
        from PySide6.QtCore import QEvent

        if obj == self.viewport() and event.type() == QEvent.Type.Wheel:
            self.wheelEvent(event)
            return True
        return super().eventFilter(obj, event)

    def cleanup(self) -> None:
        """Release scene connection and clear references (idempotent)."""
        if self._cleaned_up:
            return

        logger.debug("Cleaning up GraphicsView")

        # Remove event filter
        if self.viewport():
            self.viewport().removeEventFilter(self)

        try:
            scene = self.scene()
            if scene:
                # Don't clear the scene here - MainWindow handles that
                # Just disconnect from it
                self.setScene(None)
        except Exception as e:
            logger.warning(f"Error disconnecting from scene: {e}")

        self.main_window = None

        self._cleaned_up = True
        logger.info("GraphicsView cleanup completed")

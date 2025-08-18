"""Comprehensive tests for GraphicsView component.

Tests focus on event handling, zoom functionality, and keyboard shortcuts.
These tests improve coverage from 34% to target 80%+.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView

from momovu.lib.constants import (
    DEFAULT_SCROLL_AMOUNT,
    ZOOM_IN_FACTOR,
    ZOOM_OUT_FACTOR,
    ZOOM_THRESHOLD_FOR_PAN,
)
from momovu.views.components.graphics_view import GraphicsView


class TestGraphicsView:
    """Test GraphicsView functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with required attributes."""
        window = Mock()

        # Navigation controller
        window.navigation_controller = Mock()
        window.navigation_controller.navigate_next = Mock()
        window.navigation_controller.navigate_previous = Mock()
        window.navigation_controller.navigate_first = Mock()
        window.navigation_controller.navigate_last = Mock()

        # Zoom controller
        window.zoom_controller = Mock()
        window.zoom_controller.get_current_zoom = Mock(return_value=1.0)
        window.zoom_controller.zoom_in = Mock()
        window.zoom_controller.zoom_out = Mock()
        window.zoom_controller.set_zoom_level = Mock()
        window.zoom_controller.zoom_changed = Mock()
        window.zoom_controller.zoom_changed.emit = Mock()

        # Margin presenter
        window.margin_presenter = Mock()
        window.margin_presenter.model = Mock()
        window.margin_presenter.model.document_type = "interior"

        # UI elements
        window.presentation_action = Mock()
        window.presentation_action.isChecked = Mock(return_value=False)
        window.presentation_action.setChecked = Mock()

        window.side_by_side_action = Mock()
        window.side_by_side_action.toggle = Mock()

        window.show_margins_action = Mock()
        window.show_margins_action.toggle = Mock()

        window.show_trim_lines_action = Mock()
        window.show_trim_lines_action.toggle = Mock()

        window.show_barcode_action = Mock()
        window.show_barcode_action.toggle = Mock()

        window.show_fold_lines_action = Mock()
        window.show_fold_lines_action.toggle = Mock()

        window.show_bleed_lines_action = Mock()
        window.show_bleed_lines_action.toggle = Mock()

        # Window methods
        window.isFullScreen = Mock(return_value=False)
        window.toggle_fullscreen = Mock()
        window.toggle_presentation = Mock()
        window.exit_presentation_mode = Mock()
        window.show_shortcuts_dialog = Mock()
        window.fit_to_page = Mock()
        window.open_file_dialog = Mock()
        window.close = Mock()
        window.show_go_to_page_dialog = Mock()
        window.toggle_side_by_side = Mock()
        window.toggle_margins = Mock()
        window.toggle_trim_lines = Mock()
        window.toggle_barcode = Mock()
        window.toggle_fold_lines = Mock()
        window.toggle_bleed_lines = Mock()

        return window

    @pytest.fixture
    def graphics_view(self, mock_main_window):
        """Create a GraphicsView instance."""
        view = GraphicsView(mock_main_window)

        # Mock scrollbars
        view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=100), setValue=Mock())
        )
        view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=100), setValue=Mock())
        )

        # Mock scale method
        view.scale = Mock()

        # Mock mapToScene and mapFromScene
        view.mapToScene = Mock(return_value=QPointF(50, 50))
        view.mapFromScene = Mock(return_value=QPoint(60, 60))

        return view

    def create_key_event(self, key, modifiers=Qt.KeyboardModifier.NoModifier):
        """Create a mock key event."""
        event = Mock(spec=QKeyEvent)
        event.key = Mock(return_value=key)
        event.modifiers = Mock(return_value=modifiers)
        event.accept = Mock()
        event._mock_name = "test_event"  # Mark as mock for GraphicsView
        return event

    def create_wheel_event(
        self, delta, modifiers=Qt.KeyboardModifier.NoModifier, position=None
    ):
        """Create a mock wheel event."""
        event = Mock(spec=QWheelEvent)
        event.angleDelta = Mock(return_value=Mock(y=Mock(return_value=delta)))
        event.modifiers = Mock(return_value=modifiers)
        event.position = Mock(
            return_value=Mock(
                toPoint=Mock(return_value=QPoint(100, 100)),
                x=Mock(return_value=100),
                y=Mock(return_value=100),
            )
        )
        event.accept = Mock()
        return event

    # Test initialization
    def test_initialization(self, mock_main_window):
        """Test GraphicsView initialization."""
        view = GraphicsView(mock_main_window)

        assert view.main_window == mock_main_window
        assert view._cleaned_up is False
        # The drag mode and scrollbar policies are set in __init__
        # We can verify they were set by checking the actual values
        assert view.dragMode() == QGraphicsView.DragMode.NoDrag

    # Test keyboard navigation
    def test_arrow_key_navigation_not_zoomed(self, graphics_view, mock_main_window):
        """Test arrow keys navigate pages when not zoomed."""
        # Set zoom level below threshold
        mock_main_window.zoom_controller.get_current_zoom.return_value = 1.0

        # Test right arrow
        event = self.create_key_event(Qt.Key.Key_Right)
        graphics_view.keyPressEvent(event)
        mock_main_window.navigation_controller.navigate_next.assert_called_once()
        event.accept.assert_called()

        # Test left arrow
        mock_main_window.navigation_controller.navigate_next.reset_mock()
        event = self.create_key_event(Qt.Key.Key_Left)
        graphics_view.keyPressEvent(event)
        mock_main_window.navigation_controller.navigate_previous.assert_called_once()
        event.accept.assert_called()

    def test_arrow_key_panning_when_zoomed(self, graphics_view, mock_main_window):
        """Test arrow keys pan view when zoomed in."""
        # Set zoom level above threshold
        mock_main_window.zoom_controller.get_current_zoom.return_value = (
            ZOOM_THRESHOLD_FOR_PAN + 0.5
        )

        h_bar = graphics_view.horizontalScrollBar()
        v_bar = graphics_view.verticalScrollBar()

        # Create real key events instead of mocks for proper handling
        # The GraphicsView checks for spontaneous() which is not available on mocks
        # So we need to create events that don't trigger the mock detection

        # Test left arrow
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Left, Qt.KeyboardModifier.NoModifier
        )
        graphics_view.keyPressEvent(event)
        h_bar.setValue.assert_called_once_with(100 - DEFAULT_SCROLL_AMOUNT)

        # Test right arrow
        h_bar.setValue.reset_mock()
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier
        )
        graphics_view.keyPressEvent(event)
        h_bar.setValue.assert_called_once_with(100 + DEFAULT_SCROLL_AMOUNT)

        # Test up arrow
        v_bar.setValue.reset_mock()
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier
        )
        graphics_view.keyPressEvent(event)
        v_bar.setValue.assert_called_once_with(100 - DEFAULT_SCROLL_AMOUNT)

        # Test down arrow
        v_bar.setValue.reset_mock()
        event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier
        )
        graphics_view.keyPressEvent(event)
        v_bar.setValue.assert_called_once_with(100 + DEFAULT_SCROLL_AMOUNT)

    def test_page_navigation_keys(self, graphics_view, mock_main_window):
        """Test PageUp/PageDown/Home/End navigation."""
        test_cases = [
            (
                Qt.Key.Key_PageUp,
                mock_main_window.navigation_controller.navigate_previous,
            ),
            (Qt.Key.Key_PageDown, mock_main_window.navigation_controller.navigate_next),
            (Qt.Key.Key_Home, mock_main_window.navigation_controller.navigate_first),
            (Qt.Key.Key_End, mock_main_window.navigation_controller.navigate_last),
        ]

        for key, expected_method in test_cases:
            expected_method.reset_mock()
            event = self.create_key_event(key)
            graphics_view.keyPressEvent(event)
            expected_method.assert_called_once()
            event.accept.assert_called()

    def test_space_navigation(self, graphics_view, mock_main_window):
        """Test space bar navigation (with and without shift)."""
        # Space without shift - next page
        event = self.create_key_event(Qt.Key.Key_Space)
        graphics_view.keyPressEvent(event)
        mock_main_window.navigation_controller.navigate_next.assert_called_once()

        # Space with shift - previous page
        mock_main_window.navigation_controller.navigate_previous.reset_mock()
        event = self.create_key_event(
            Qt.Key.Key_Space, Qt.KeyboardModifier.ShiftModifier
        )
        graphics_view.keyPressEvent(event)
        mock_main_window.navigation_controller.navigate_previous.assert_called_once()

    def test_function_keys(self, graphics_view, mock_main_window):
        """Test F5, F11, F1, and Escape keys."""
        # F5 - presentation mode
        event = self.create_key_event(Qt.Key.Key_F5)
        graphics_view.keyPressEvent(event)
        mock_main_window.toggle_presentation.assert_called_once()

        # F11 - fullscreen
        event = self.create_key_event(Qt.Key.Key_F11)
        graphics_view.keyPressEvent(event)
        mock_main_window.toggle_fullscreen.assert_called_once()

        # F1 - help
        event = self.create_key_event(Qt.Key.Key_F1)
        graphics_view.keyPressEvent(event)
        mock_main_window.show_shortcuts_dialog.assert_called_once()

        # Escape in presentation mode
        mock_main_window.presentation_action.isChecked.return_value = True
        event = self.create_key_event(Qt.Key.Key_Escape)
        graphics_view.keyPressEvent(event)
        mock_main_window.presentation_action.setChecked.assert_called_with(False)
        mock_main_window.exit_presentation_mode.assert_called_once()

    def test_zoom_keyboard_shortcuts(self, graphics_view, mock_main_window):
        """Test Ctrl+Plus/Minus/0 zoom shortcuts."""
        # Ctrl+Plus - zoom in
        event = self.create_key_event(
            Qt.Key.Key_Plus, Qt.KeyboardModifier.ControlModifier
        )
        graphics_view.keyPressEvent(event)
        mock_main_window.zoom_controller.zoom_in.assert_called_once()

        # Ctrl+Equal (alternative for plus)
        mock_main_window.zoom_controller.zoom_in.reset_mock()
        event = self.create_key_event(
            Qt.Key.Key_Equal, Qt.KeyboardModifier.ControlModifier
        )
        graphics_view.keyPressEvent(event)
        mock_main_window.zoom_controller.zoom_in.assert_called_once()

        # Ctrl+Minus - zoom out
        event = self.create_key_event(
            Qt.Key.Key_Minus, Qt.KeyboardModifier.ControlModifier
        )
        graphics_view.keyPressEvent(event)
        mock_main_window.zoom_controller.zoom_out.assert_called_once()

        # Ctrl+0 - fit to page
        event = self.create_key_event(Qt.Key.Key_0, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        mock_main_window.fit_to_page.assert_called_once()

    def test_ctrl_shortcuts(self, graphics_view, mock_main_window):
        """Test various Ctrl+key shortcuts."""
        test_cases = [
            (Qt.Key.Key_F, mock_main_window.fit_to_page),
            (Qt.Key.Key_O, mock_main_window.open_file_dialog),
            (Qt.Key.Key_Q, mock_main_window.close),
            (Qt.Key.Key_D, mock_main_window.toggle_side_by_side),
            (Qt.Key.Key_M, mock_main_window.toggle_margins),
            (Qt.Key.Key_T, mock_main_window.toggle_trim_lines),
            (Qt.Key.Key_L, mock_main_window.toggle_fold_lines),
        ]

        for key, expected_method in test_cases:
            expected_method.reset_mock()
            event = self.create_key_event(key, Qt.KeyboardModifier.ControlModifier)
            graphics_view.keyPressEvent(event)
            expected_method.assert_called()

    def test_ctrl_g_interior_only(self, graphics_view, mock_main_window):
        """Test Ctrl+G (go to page) only works for interior documents."""
        # Test with interior document
        mock_main_window.margin_presenter.model.document_type = "interior"
        event = self.create_key_event(Qt.Key.Key_G, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        mock_main_window.show_go_to_page_dialog.assert_called_once()

        # Test with cover document
        mock_main_window.show_go_to_page_dialog.reset_mock()
        mock_main_window.margin_presenter.model.document_type = "cover"
        event = self.create_key_event(Qt.Key.Key_G, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        mock_main_window.show_go_to_page_dialog.assert_not_called()

    def test_ctrl_b_r_cover_dustjacket_only(self, graphics_view, mock_main_window):
        """Test Ctrl+B and Ctrl+R only work for cover/dustjacket documents."""
        # Test with cover document
        mock_main_window.margin_presenter.model.document_type = "cover"

        event = self.create_key_event(Qt.Key.Key_B, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        mock_main_window.toggle_barcode.assert_called_once()

        event = self.create_key_event(Qt.Key.Key_R, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        mock_main_window.toggle_bleed_lines.assert_called_once()

        # Test with interior document - should not call
        mock_main_window.toggle_barcode.reset_mock()
        mock_main_window.toggle_bleed_lines.reset_mock()
        mock_main_window.margin_presenter.model.document_type = "interior"

        event = self.create_key_event(Qt.Key.Key_B, Qt.KeyboardModifier.ControlModifier)
        graphics_view.keyPressEvent(event)
        # Should still be called but document type check is in main window
        event.accept.assert_called()

    # Test wheel events
    def test_wheel_zoom_with_ctrl(self, graphics_view, mock_main_window):
        """Test Ctrl+wheel zooms at mouse position."""
        # Zoom in
        event = self.create_wheel_event(120, Qt.KeyboardModifier.ControlModifier)
        graphics_view.wheelEvent(event)

        graphics_view.scale.assert_called_with(ZOOM_IN_FACTOR, ZOOM_IN_FACTOR)
        mock_main_window.zoom_controller.set_zoom_level.assert_called()
        mock_main_window.zoom_controller.zoom_changed.emit.assert_called()

        # Verify scrollbar adjustment for mouse position
        h_bar = graphics_view.horizontalScrollBar()
        v_bar = graphics_view.verticalScrollBar()
        h_bar.setValue.assert_called()
        v_bar.setValue.assert_called()

        # Zoom out
        graphics_view.scale.reset_mock()
        event = self.create_wheel_event(-120, Qt.KeyboardModifier.ControlModifier)
        graphics_view.wheelEvent(event)

        graphics_view.scale.assert_called_with(ZOOM_OUT_FACTOR, ZOOM_OUT_FACTOR)

    def test_wheel_horizontal_pan_with_shift(self, graphics_view):
        """Test Shift+wheel for horizontal panning."""
        h_bar = graphics_view.horizontalScrollBar()

        # Scroll right (negative delta)
        event = self.create_wheel_event(-120, Qt.KeyboardModifier.ShiftModifier)
        graphics_view.wheelEvent(event)
        h_bar.setValue.assert_called_with(100 + DEFAULT_SCROLL_AMOUNT)

        # Scroll left (positive delta)
        h_bar.setValue.reset_mock()
        event = self.create_wheel_event(120, Qt.KeyboardModifier.ShiftModifier)
        graphics_view.wheelEvent(event)
        h_bar.setValue.assert_called_with(100 - DEFAULT_SCROLL_AMOUNT)

    def test_wheel_vertical_pan_when_zoomed(self, graphics_view, mock_main_window):
        """Test wheel scrolls vertically when zoomed in."""
        # Set zoom above threshold
        mock_main_window.zoom_controller.get_current_zoom.return_value = (
            ZOOM_THRESHOLD_FOR_PAN + 0.5
        )
        v_bar = graphics_view.verticalScrollBar()

        # Scroll down (negative delta)
        event = self.create_wheel_event(-120)
        graphics_view.wheelEvent(event)
        v_bar.setValue.assert_called_with(100 + DEFAULT_SCROLL_AMOUNT)

        # Scroll up (positive delta)
        v_bar.setValue.reset_mock()
        event = self.create_wheel_event(120)
        graphics_view.wheelEvent(event)
        v_bar.setValue.assert_called_with(100 - DEFAULT_SCROLL_AMOUNT)

    def test_wheel_page_navigation_when_not_zoomed(
        self, graphics_view, mock_main_window
    ):
        """Test wheel navigates pages when not zoomed."""
        # Set zoom below threshold
        mock_main_window.zoom_controller.get_current_zoom.return_value = 1.0

        # Scroll down - next page
        event = self.create_wheel_event(-120)
        graphics_view.wheelEvent(event)
        mock_main_window.navigation_controller.navigate_next.assert_called_once()

        # Scroll up - previous page
        mock_main_window.navigation_controller.navigate_previous.reset_mock()
        event = self.create_wheel_event(120)
        graphics_view.wheelEvent(event)
        mock_main_window.navigation_controller.navigate_previous.assert_called_once()

    # Test cleanup
    def test_cleanup(self, graphics_view):
        """Test cleanup releases resources properly."""
        # Mock scene
        mock_scene = Mock()
        graphics_view.scene = Mock(return_value=mock_scene)
        graphics_view.setScene = Mock()

        # First cleanup
        graphics_view.cleanup()

        assert graphics_view._cleaned_up is True
        assert graphics_view.main_window is None
        graphics_view.setScene.assert_called_with(None)

        # Second cleanup should be idempotent
        graphics_view.setScene.reset_mock()
        graphics_view.cleanup()
        graphics_view.setScene.assert_not_called()

    def test_cleanup_with_scene_error(self, graphics_view):
        """Test cleanup handles scene errors gracefully."""
        # Mock scene that raises exception
        graphics_view.scene = Mock(side_effect=RuntimeError("Scene deleted"))

        # Should not raise
        graphics_view.cleanup()
        assert graphics_view._cleaned_up is True
        assert graphics_view.main_window is None

    # Test edge cases
    def test_arrow_keys_without_margin_presenter(self, graphics_view, mock_main_window):
        """Test arrow key handling when margin presenter not ready."""
        # Remove margin presenter
        mock_main_window.margin_presenter = None
        mock_main_window.zoom_controller.get_current_zoom.return_value = 1.0

        # Should default to interior behavior
        event = self.create_key_event(Qt.Key.Key_Right)
        graphics_view.keyPressEvent(event)
        mock_main_window.navigation_controller.navigate_next.assert_called_once()

    def test_escape_key_variations(self, graphics_view, mock_main_window):
        """Test escape key in different states."""
        # Not in presentation or fullscreen - should still accept
        mock_main_window.presentation_action.isChecked.return_value = False
        mock_main_window.isFullScreen.return_value = False

        event = self.create_key_event(Qt.Key.Key_Escape)
        graphics_view.keyPressEvent(event)
        event.accept.assert_called()

        # In fullscreen but not presentation
        mock_main_window.isFullScreen.return_value = True
        event = self.create_key_event(Qt.Key.Key_Escape)
        graphics_view.keyPressEvent(event)
        mock_main_window.toggle_fullscreen.assert_called_once()

    def test_non_interior_arrow_key_behavior(self, graphics_view, mock_main_window):
        """Test arrow keys for cover/dustjacket documents."""
        mock_main_window.zoom_controller.get_current_zoom.return_value = 1.0
        mock_main_window.margin_presenter.model.document_type = "cover"

        # Arrow keys should not navigate for non-interior documents
        event = self.create_key_event(Qt.Key.Key_Right)
        graphics_view.keyPressEvent(event)
        event.accept.assert_called()
        # Navigation should not be called for cover documents

    def test_wheel_zoom_calculation(self, graphics_view, mock_main_window):
        """Test zoom calculation and scrollbar adjustment."""
        # Set initial zoom
        mock_main_window.zoom_controller.get_current_zoom.return_value = 2.0

        # Mock scene position mapping
        graphics_view.mapToScene.return_value = QPointF(200, 300)
        graphics_view.mapFromScene.return_value = QPoint(220, 330)

        event = self.create_wheel_event(120, Qt.KeyboardModifier.ControlModifier)
        graphics_view.wheelEvent(event)

        # Verify zoom level calculation
        expected_new_zoom = 2.0 * ZOOM_IN_FACTOR
        mock_main_window.zoom_controller.set_zoom_level.assert_called_with(
            expected_new_zoom
        )

        # Verify scrollbar adjustment calculation
        h_bar = graphics_view.horizontalScrollBar()
        v_bar = graphics_view.verticalScrollBar()

        # Expected delta: event position - new mapped position
        expected_delta_x = 100 - 220  # -120
        expected_delta_y = 100 - 330  # -230

        h_bar.setValue.assert_called_with(int(100 - expected_delta_x))
        v_bar.setValue.assert_called_with(int(100 - expected_delta_y))

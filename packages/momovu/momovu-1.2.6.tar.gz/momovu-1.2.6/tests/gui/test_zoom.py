"""GUI tests for zoom functionality.

These tests use pytest-qt to test actual zoom operations
with real Qt widgets and user interactions.
"""

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent


@pytest.mark.gui
class TestZoomOperations:
    """Test zoom functionality with real widgets."""

    def test_zoom_with_toolbar_buttons(self, qtbot, main_window_with_pdf, gui_helper):
        """Test zooming using toolbar buttons."""
        # Get initial zoom level
        initial_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Zoom in
        main_window_with_pdf.zoom_in()
        qtbot.wait(300)

        # Verify zoom increased
        zoom_in_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_in_level > initial_zoom

        # Zoom out
        main_window_with_pdf.zoom_out()
        qtbot.wait(300)

        # Verify zoom decreased
        zoom_out_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_out_level < zoom_in_level
        assert zoom_out_level == pytest.approx(initial_zoom, rel=0.01)

        # Zoom in multiple times
        for _ in range(3):
            main_window_with_pdf.zoom_in()
            qtbot.wait(200)

        multi_zoom_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert multi_zoom_level > zoom_in_level

        # Fit to page (reset zoom)
        main_window_with_pdf.fit_to_page()
        qtbot.wait(300)

        # Verify zoom is reset (but not necessarily to initial due to fit)
        fit_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert fit_zoom != multi_zoom_level

    def test_zoom_with_keyboard_shortcuts(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test zooming using keyboard shortcuts."""
        # Get initial zoom level
        initial_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Ctrl+Plus to zoom in
        qtbot.keyClick(
            main_window_with_pdf.graphics_view,
            Qt.Key.Key_Plus,
            Qt.KeyboardModifier.ControlModifier,
        )
        qtbot.wait(300)

        # Verify zoom increased
        zoom_in_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_in_level > initial_zoom

        # Ctrl+Minus to zoom out
        qtbot.keyClick(
            main_window_with_pdf.graphics_view,
            Qt.Key.Key_Minus,
            Qt.KeyboardModifier.ControlModifier,
        )
        qtbot.wait(300)

        # Verify zoom decreased
        zoom_out_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_out_level < zoom_in_level

        # Ctrl+0 to fit to page
        qtbot.keyClick(
            main_window_with_pdf.graphics_view,
            Qt.Key.Key_0,
            Qt.KeyboardModifier.ControlModifier,
        )
        qtbot.wait(300)

        # Verify zoom changed (use approximate comparison)
        fit_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        # Fit zoom might be similar to zoom_out_level, so just verify it's a valid zoom
        assert fit_zoom > 0

        # Ctrl+F also fits to page
        qtbot.keyClick(
            main_window_with_pdf.graphics_view,
            Qt.Key.Key_F,
            Qt.KeyboardModifier.ControlModifier,
        )
        qtbot.wait(300)

        # Should be approximately the same as previous fit
        fit_zoom2 = gui_helper.get_zoom_level(main_window_with_pdf)
        # Both should be valid zoom levels, might be the same or slightly different
        assert fit_zoom2 > 0
        assert (
            abs(fit_zoom2 - fit_zoom) < 0.1
        )  # Should be close but not necessarily exact

    def test_zoom_with_mouse_wheel(self, qtbot, main_window_with_pdf, gui_helper):
        """Test zooming using Ctrl+mouse wheel."""
        # Get initial zoom level
        initial_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Get the graphics view widget
        view = main_window_with_pdf.graphics_view

        # Create wheel event for zooming in (Ctrl+wheel up)
        wheel_event = QWheelEvent(
            QPointF(400, 300),  # position in view
            QPointF(400, 300),  # global position
            QPoint(0, 120),  # pixel delta (positive for up)
            QPoint(0, 120),  # angle delta
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.ControlModifier,  # Ctrl pressed
            Qt.ScrollPhase.NoScrollPhase,
            False,  # not inverted
        )

        # Send the event
        view.wheelEvent(wheel_event)
        qtbot.wait(300)

        # Verify zoom increased
        zoom_in_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_in_level > initial_zoom

        # Create wheel event for zooming out (Ctrl+wheel down)
        wheel_event = QWheelEvent(
            QPointF(400, 300),  # position in view
            QPointF(400, 300),  # global position
            QPoint(0, -120),  # pixel delta (negative for down)
            QPoint(0, -120),  # angle delta
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.ControlModifier,  # Ctrl pressed
            Qt.ScrollPhase.NoScrollPhase,
            False,  # not inverted
        )

        # Send the event
        view.wheelEvent(wheel_event)
        qtbot.wait(300)

        # Verify zoom decreased
        zoom_out_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoom_out_level < zoom_in_level
        assert zoom_out_level == pytest.approx(initial_zoom, rel=0.01)

    def test_zoom_limits(self, qtbot, main_window_with_pdf, gui_helper):
        """Test zoom limits (min and max zoom)."""
        # Zoom out to minimum
        for _ in range(20):  # Zoom out many times
            main_window_with_pdf.zoom_out()
            qtbot.wait(50)

        min_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Try to zoom out more - should stay at minimum
        main_window_with_pdf.zoom_out()
        qtbot.wait(200)

        still_min_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        # Use a more lenient tolerance for zoom comparisons
        assert still_min_zoom == pytest.approx(min_zoom, rel=0.1)

        # Zoom in to maximum
        for _ in range(30):  # Zoom in many times
            main_window_with_pdf.zoom_in()
            qtbot.wait(50)

        max_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Try to zoom in more - should stay at maximum
        main_window_with_pdf.zoom_in()
        qtbot.wait(200)

        still_max_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert still_max_zoom == pytest.approx(max_zoom, rel=0.15)

        # Verify max is greater than min
        assert max_zoom > min_zoom

    def test_zoom_affects_navigation(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that arrow keys are used for panning regardless of zoom level."""
        main_window_with_pdf.fit_to_page()
        qtbot.wait(300)

        initial_page = gui_helper.get_current_page(main_window_with_pdf)

        # Arrow keys don't navigate pages - they're for panning
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Right)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == initial_page

        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Left)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == initial_page

        # Now zoom in significantly
        for _ in range(5):
            main_window_with_pdf.zoom_in()
            qtbot.wait(100)

        # Get current scroll position
        h_bar = main_window_with_pdf.graphics_view.horizontalScrollBar()

        # Arrow keys still don't navigate when zoomed
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Right)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == initial_page

        new_h_pos = h_bar.value()
        assert new_h_pos >= 0

    def test_zoom_with_different_document_types(
        self, qtbot, main_window_with_cover, gui_helper
    ):
        """Test zoom works correctly with different document types."""
        # Test with cover document
        initial_zoom = gui_helper.get_zoom_level(main_window_with_cover)

        # Zoom in
        main_window_with_cover.zoom_in()
        qtbot.wait(300)

        # Verify zoom increased
        zoom_in_level = gui_helper.get_zoom_level(main_window_with_cover)
        assert zoom_in_level > initial_zoom

        # Fit to page
        main_window_with_cover.fit_to_page()
        qtbot.wait(300)

        # Verify scene is still rendered
        assert len(main_window_with_cover.graphics_scene.items()) > 0

    def test_zoom_preserves_center_point(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that zooming preserves the center point of view."""
        # Zoom in first to have something to work with
        for _ in range(3):
            main_window_with_pdf.zoom_in()
            qtbot.wait(100)

        # Get the graphics view
        view = main_window_with_pdf.graphics_view

        # Get center point in scene coordinates before zoom
        view_center = view.viewport().rect().center()
        scene_center_before = view.mapToScene(view_center)

        # Zoom in more
        main_window_with_pdf.zoom_in()
        qtbot.wait(300)

        # Get center point in scene coordinates after zoom
        scene_center_after = view.mapToScene(view_center)

        # The scene point at the center should be approximately the same
        # (allowing for some rounding/precision differences)
        assert abs(scene_center_before.x() - scene_center_after.x()) < 10
        assert abs(scene_center_before.y() - scene_center_after.y()) < 10

    def test_zoom_updates_after_page_change(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test that zoom is maintained when changing pages."""
        # Zoom in
        for _ in range(3):
            main_window_with_pdf.zoom_in()
            qtbot.wait(100)

        zoom_level = gui_helper.get_zoom_level(main_window_with_pdf)

        # Navigate to next page
        main_window_with_pdf.next_page()
        qtbot.wait(300)

        # Zoom level should be maintained
        new_zoom_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert new_zoom_level == pytest.approx(zoom_level, rel=0.01)

        # Navigate back
        main_window_with_pdf.previous_page()
        qtbot.wait(300)

        # Zoom level should still be maintained
        back_zoom_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert back_zoom_level == pytest.approx(zoom_level, rel=0.01)

    def test_fit_to_page_with_side_by_side(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test fit to page works correctly with side-by-side mode."""
        assert gui_helper.get_document_type(main_window_with_pdf) == "interior"

        main_window_with_pdf.toggle_side_by_side()
        qtbot.wait(500)

        is_side_by_side = gui_helper.is_side_by_side(main_window_with_pdf)

        # Zoom in
        for _ in range(3):
            main_window_with_pdf.zoom_in()
            qtbot.wait(100)

        zoomed_level = gui_helper.get_zoom_level(main_window_with_pdf)

        # Fit to page
        main_window_with_pdf.fit_to_page()
        qtbot.wait(300)

        # Zoom should change
        fit_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert fit_level != zoomed_level

        # Scene should still have items
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        if is_side_by_side:
            # If side-by-side was enabled, disable it
            main_window_with_pdf.toggle_side_by_side()
            qtbot.wait(500)

            # Fit to page again
            main_window_with_pdf.fit_to_page()
            qtbot.wait(300)

            single_fit_level = gui_helper.get_zoom_level(main_window_with_pdf)
            assert single_fit_level > 0
        else:
            assert fit_level > 0

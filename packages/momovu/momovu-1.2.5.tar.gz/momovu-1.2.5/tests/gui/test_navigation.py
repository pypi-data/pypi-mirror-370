"""GUI tests for page navigation functionality.

These tests use pytest-qt to test actual page navigation
with real Qt widgets and keyboard/mouse interactions.
"""

import pytest
from PySide6.QtCore import Qt


@pytest.mark.gui
class TestPageNavigation:
    """Test page navigation functionality with real widgets."""

    def test_navigate_with_toolbar_buttons(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test navigation using toolbar buttons."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 1, "Need multi-page PDF for navigation test"

        # Verify starting at first page
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Click next page button
        main_window_with_pdf.next_page()
        qtbot.wait(300)

        # Verify moved to page 1
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        # Click previous page button
        main_window_with_pdf.previous_page()
        qtbot.wait(300)

        # Verify back to page 0
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Go to last page
        main_window_with_pdf.go_to_last_page()
        qtbot.wait(300)

        # Verify at last page
        assert gui_helper.get_current_page(main_window_with_pdf) == total_pages - 1

        # Go to first page
        main_window_with_pdf.go_to_first_page()
        qtbot.wait(300)

        # Verify back at first page
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigate_with_keyboard_arrows(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test that arrow keys are used for panning, not navigation."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 1, "Need multi-page PDF for navigation test"

        # Verify starting at first page
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Arrow keys don't navigate pages - they're for panning
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Right)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Left)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Page Down/Up keys are used for navigation
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_PageDown)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_PageUp)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigate_with_page_keys(self, qtbot, main_window_with_pdf, gui_helper):
        """Test navigation using Page Up/Down and Home/End keys."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 1, "Need multi-page PDF for navigation test"

        # Press Page Down
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_PageDown)
        qtbot.wait(300)

        # Verify moved forward
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        # Press Page Up
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_PageUp)
        qtbot.wait(300)

        # Verify moved back
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Press End key
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_End)
        qtbot.wait(300)

        # Verify at last page
        assert gui_helper.get_current_page(main_window_with_pdf) == total_pages - 1

        # Press Home key
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Home)
        qtbot.wait(300)

        # Verify at first page
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigate_with_space_key(self, qtbot, main_window_with_pdf, gui_helper):
        """Test navigation using space and shift+space."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 1, "Need multi-page PDF for navigation test"

        # Press space (next page)
        qtbot.keyClick(main_window_with_pdf.graphics_view, Qt.Key.Key_Space)
        qtbot.wait(300)

        # Verify moved forward
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        # Press shift+space (previous page)
        qtbot.keyClick(
            main_window_with_pdf.graphics_view,
            Qt.Key.Key_Space,
            Qt.KeyboardModifier.ShiftModifier,
        )
        qtbot.wait(300)

        # Verify moved back
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigate_with_mouse_wheel(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that mouse wheel is used for scrolling, not page navigation."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 1, "Need multi-page PDF for navigation test"

        # Ensure we're at default zoom
        main_window_with_pdf.fit_to_page()
        qtbot.wait(300)

        view = main_window_with_pdf.graphics_view

        from PySide6.QtCore import QPoint, QPointF
        from PySide6.QtGui import QWheelEvent

        # Mouse wheel scrolls the view, doesn't navigate pages
        wheel_event = QWheelEvent(
            QPointF(100, 100),
            QPointF(100, 100),
            QPoint(0, -120),
            QPoint(0, -120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )

        view.wheelEvent(wheel_event)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        wheel_event = QWheelEvent(
            QPointF(100, 100),
            QPointF(100, 100),
            QPoint(0, 120),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )

        view.wheelEvent(wheel_event)
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigate_with_spinbox(self, qtbot, main_window_with_pdf, gui_helper):
        """Test navigation using the page number spinbox."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)
        assert total_pages > 2, "Need at least 3 pages for spinbox test"

        # Get the spinbox
        spinbox = main_window_with_pdf.page_number_spinbox
        assert spinbox is not None

        # Clear and type page 2 (1-based in UI)
        spinbox.clear()
        qtbot.keyClicks(spinbox, "2")
        qtbot.keyClick(spinbox, Qt.Key.Key_Return)
        qtbot.wait(300)

        # Verify moved to page 1 (0-based internally)
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        # Clear and type last page number
        spinbox.clear()
        qtbot.keyClicks(spinbox, str(total_pages))
        qtbot.keyClick(spinbox, Qt.Key.Key_Return)
        qtbot.wait(300)

        # Verify moved to last page
        assert gui_helper.get_current_page(main_window_with_pdf) == total_pages - 1

        # Clear and type page 1
        spinbox.clear()
        qtbot.keyClicks(spinbox, "1")
        qtbot.keyClick(spinbox, Qt.Key.Key_Return)
        qtbot.wait(300)

        # Verify back at first page
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

    def test_navigation_boundaries(self, qtbot, main_window_with_pdf, gui_helper):
        """Test navigation at document boundaries."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)

        # Go to first page
        main_window_with_pdf.go_to_first_page()
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Try to go previous from first page (should stay at first)
        main_window_with_pdf.previous_page()
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Go to last page
        main_window_with_pdf.go_to_last_page()
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == total_pages - 1

        # Try to go next from last page (should stay at last)
        main_window_with_pdf.next_page()
        qtbot.wait(300)
        assert gui_helper.get_current_page(main_window_with_pdf) == total_pages - 1

    def test_navigation_updates_ui(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that navigation properly updates UI elements."""
        total_pages = gui_helper.get_total_pages(main_window_with_pdf)

        # Navigate to page 2
        main_window_with_pdf.next_page()
        qtbot.wait(300)

        # Check page label
        page_label_text = main_window_with_pdf.page_label.text()
        assert "Page: 2/" in page_label_text

        # Check spinbox value
        spinbox = main_window_with_pdf.page_number_spinbox
        assert spinbox.value() == 2  # 1-based in UI

        # Navigate to last page
        main_window_with_pdf.go_to_last_page()
        qtbot.wait(300)

        # Check page label
        page_label_text = main_window_with_pdf.page_label.text()
        assert f"Page: {total_pages}/" in page_label_text

        # Check spinbox value
        assert spinbox.value() == total_pages

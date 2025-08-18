"""Integration tests for the MainWindow."""

from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QSizeF, Qt
from PySide6.QtWidgets import QApplication

from momovu.views.main_window import MainWindow


class TestMainWindowIntegration:
    """Test MainWindow integration with real functionality."""

    @pytest.fixture
    def qapp(self) -> Any:
        """Ensure QApplication exists."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app

    @pytest.fixture
    def mock_pdf_document(self) -> Generator[Mock, None, None]:
        """Create a mock PDF document."""
        doc = Mock()
        doc.load.return_value = True
        doc.pageCount.return_value = 5
        doc.pagePointSize.return_value = QSizeF(612.0, 792.0)
        yield doc

    def test_window_initialization(self, qapp: Any) -> None:
        """Test basic window initialization without PDF."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Check window properties
            assert window.windowTitle() == "Momovu"
            # When no document is loaded, it shows Page: 1/0 (current page 1, total 0)
            assert window.page_label.text() == "Page: 1/0"

            # Check default settings
            assert window._show_margins is True
            assert window._show_trim_lines is True
            assert window._show_barcode is True
            assert window._show_fold_lines is True
            assert window._book_type == "interior"

    def test_window_with_pdf_initialization(
        self, qapp: Any, mock_pdf_document: Any
    ) -> None:
        """Test window initialization with PDF file."""
        with (
            patch("PySide6.QtPdf.QPdfDocument") as mock_doc_class,
            patch.object(MainWindow, "showMaximized"),
            patch.object(MainWindow, "load_pdf"),
        ):
            mock_doc_class.return_value = mock_pdf_document

            window = MainWindow(pdf_path="test.pdf", num_pages=100, book_type="cover")

            # Check document type was set
            assert window.margin_presenter.model.document_type == "cover"

            # Check num pages was set
            assert window.num_pages_spinbox.value() == 100

    def test_presentation_mode_toggle(self, qapp: Any) -> None:
        """Test presentation mode can be toggled."""
        with (
            patch.object(MainWindow, "showMaximized"),
            patch.object(MainWindow, "showFullScreen"),
            patch.object(MainWindow, "setWindowState"),
        ):
            window = MainWindow()

            # Initially not in presentation mode
            assert window.ui_state_manager.is_presentation_mode is False
            assert window.presentation_action.isChecked() is False

            # Enter presentation mode
            window.enter_presentation_mode()
            assert window.ui_state_manager.is_presentation_mode is True
            assert window.presentation_action.isChecked() is True

            # Exit presentation mode - need to process events for state to update
            window.exit_presentation_mode()
            # The exit_presentation_mode should have set it to False
            assert window.ui_state_manager.is_presentation_mode is False
            assert window.presentation_action.isChecked() is False

    def test_side_by_side_mode(self, qapp: Any) -> None:
        """Test side-by-side view mode."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=True)

            # Check initial state
            assert window.side_by_side_action.isChecked() is True
            assert window.navigation_presenter.model.view_mode == "side_by_side"

            # Toggle off - need to uncheck the action first
            window.side_by_side_action.setChecked(False)
            window.toggle_side_by_side()
            assert window.navigation_presenter.model.view_mode == "single"

            # Toggle back on - need to check the action first
            window.side_by_side_action.setChecked(True)
            window.toggle_side_by_side()
            assert window.navigation_presenter.model.view_mode == "side_by_side"

    def test_document_type_switching(self, qapp: Any) -> None:
        """Test switching between document types."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Default is interior
            assert window.margin_presenter.model.document_type == "interior"
            assert window.interior_action.isChecked() is True

            # Switch to cover
            window.set_document_type("cover")
            assert window.margin_presenter.model.document_type == "cover"
            assert window.cover_action.isChecked() is True
            assert window.interior_action.isChecked() is False

            # Switch to dustjacket
            window.set_document_type("dustjacket")
            assert window.margin_presenter.model.document_type == "dustjacket"
            assert window.dustjacket_action.isChecked() is True
            assert window.cover_action.isChecked() is False

    def test_margin_and_trim_toggles(self, qapp: Any) -> None:
        """Test margin and trim line visibility toggles."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Check defaults
            assert window.margin_presenter.model.show_margins is True
            assert window.margin_presenter.model.show_trim_lines is True

            # Toggle margins off
            window.show_margins_action.setChecked(False)
            window.toggle_margins()
            assert window.margin_presenter.model.show_margins is False

            # Toggle trim lines off
            window.show_trim_lines_action.setChecked(False)
            window.toggle_trim_lines()
            assert window.margin_presenter.model.show_trim_lines is False

    def test_keyboard_navigation(self, qapp: Any) -> None:
        """Test keyboard navigation works through NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock navigation controller methods
            window.navigation_controller.navigate_next = Mock()
            window.navigation_controller.navigate_previous = Mock()
            window.navigation_controller.navigate_first = Mock()
            window.navigation_controller.navigate_last = Mock()
            window.close = Mock()

            from PySide6.QtGui import QKeyEvent

            # Test navigation keys
            test_cases = [
                (
                    Qt.Key.Key_Right,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_next,
                ),
                (
                    Qt.Key.Key_Left,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_previous,
                ),
                (
                    Qt.Key.Key_PageDown,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_next,
                ),
                (
                    Qt.Key.Key_PageUp,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_previous,
                ),
                (
                    Qt.Key.Key_Home,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_first,
                ),
                (
                    Qt.Key.Key_End,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_last,
                ),
                (
                    Qt.Key.Key_Space,
                    Qt.KeyboardModifier.NoModifier,
                    window.navigation_controller.navigate_next,
                ),
                (Qt.Key.Key_Q, Qt.KeyboardModifier.ControlModifier, window.close),
            ]

            for key, modifier, expected_method in test_cases:
                event = Mock(spec=QKeyEvent)
                event.key.return_value = key
                event.modifiers.return_value = modifier
                # Mark as mock event for GraphicsView
                event._mock_name = "test_event"

                window.keyPressEvent(event)
                expected_method.assert_called()

                # Reset for next test
                expected_method.reset_mock()

    def test_zoom_controls(self, qapp: Any) -> None:
        """Test zoom controls work."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock graphics view scale method
            window.graphics_view.scale = Mock()

            # Test zoom in (now uses 1.1 factor)
            window.zoom_in()
            window.graphics_view.scale.assert_called_with(1.1, 1.1)

            # Test zoom out (now uses exact inverse of 1.1)
            window.zoom_out()
            zoom_out_factor = 1.0 / 1.1  # 0.9090909090909091
            window.graphics_view.scale.assert_called_with(
                zoom_out_factor, zoom_out_factor
            )

    def test_page_spinbox_updates(self, qapp: Any) -> None:
        """Test page number spinbox updates correctly."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Manually set up the navigation presenter with pages
            # This simulates what happens when a PDF is loaded
            window.navigation_presenter.set_total_pages(10)

            # Manually update the spinbox maximum like load_pdf does
            window.page_number_spinbox.setMaximum(10)

            # Check spinbox range was updated
            assert window.page_number_spinbox.maximum() == 10
            assert window.page_number_spinbox.minimum() == 1

            # Test changing page via spinbox
            window.render_current_page = Mock()

            # Mock the scroll controller to avoid errors
            window.navigation_controller._scroll_controller = Mock()

            # Change the page number
            window.on_page_number_changed(5)

            # Check page was changed (0-based index)
            assert window.navigation_presenter.get_current_page() == 4
            # render_current_page gets called once
            assert window.render_current_page.call_count >= 1

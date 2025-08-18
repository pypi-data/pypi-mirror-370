"""Test Ctrl+G functionality is disabled for cover and dustjacket documents."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QInputDialog

from momovu.views.main_window import MainWindow


class TestCtrlGDocumentType:
    """Test suite to verify Ctrl+G is only available for interior documents."""

    @pytest.fixture
    def qapp(self):
        """Ensure QApplication exists."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app

    def test_ctrl_g_works_for_interior_document(self, qapp):
        """Test that Ctrl+G works when viewing an interior document."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Set up as interior document (default)
            window.margin_presenter.model.document_type = "interior"

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)
            window.navigation_presenter.set_total_pages(10)

            # Mock the dialog
            with patch.object(QInputDialog, "getInt") as mock_dialog:
                mock_dialog.return_value = (5, True)

                # Create Ctrl+G key event
                event = Mock(spec=QKeyEvent)
                event.key.return_value = Qt.Key.Key_G
                event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
                event._mock_name = "test_event"

                # Trigger the key event
                window.graphics_view.keyPressEvent(event)

                # Dialog should have been shown
                mock_dialog.assert_called_once()

    def test_ctrl_g_disabled_for_cover_document(self, qapp):
        """Test that Ctrl+G is disabled when viewing a cover document."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Set up as cover document
            window.margin_presenter.model.document_type = "cover"

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)
            window.navigation_presenter.set_total_pages(1)  # Cover is always 1 page

            # Mock the dialog
            with patch.object(QInputDialog, "getInt") as mock_dialog:
                # Create Ctrl+G key event
                event = Mock(spec=QKeyEvent)
                event.key.return_value = Qt.Key.Key_G
                event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
                event._mock_name = "test_event"

                # Trigger the key event
                window.graphics_view.keyPressEvent(event)

                # Dialog should NOT have been shown
                mock_dialog.assert_not_called()

    def test_ctrl_g_disabled_for_dustjacket_document(self, qapp):
        """Test that Ctrl+G is disabled when viewing a dustjacket document."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Set up as dustjacket document
            window.margin_presenter.model.document_type = "dustjacket"

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)
            window.navigation_presenter.set_total_pages(
                1
            )  # Dustjacket is always 1 page

            # Mock the dialog
            with patch.object(QInputDialog, "getInt") as mock_dialog:
                # Create Ctrl+G key event
                event = Mock(spec=QKeyEvent)
                event.key.return_value = Qt.Key.Key_G
                event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
                event._mock_name = "test_event"

                # Trigger the key event
                window.graphics_view.keyPressEvent(event)

                # Dialog should NOT have been shown
                mock_dialog.assert_not_called()

    def test_dialog_manager_safety_check(self, qapp):
        """Test that dialog manager also checks document type as a safety measure."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Set up as cover document
            window.margin_presenter.model.document_type = "cover"

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)
            window.navigation_presenter.set_total_pages(1)

            # Mock the dialog
            with patch.object(QInputDialog, "getInt") as mock_dialog:
                # Call the dialog directly (bypassing keyboard check)
                window.show_go_to_page_dialog()

                # Dialog should still NOT be shown due to safety check
                mock_dialog.assert_not_called()

    def test_document_type_switching(self, qapp):
        """Test that Ctrl+G availability updates when switching document types."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)

            # Start with interior document
            window.margin_presenter.model.document_type = "interior"
            window.navigation_presenter.set_total_pages(10)

            with patch.object(QInputDialog, "getInt") as mock_dialog:
                mock_dialog.return_value = (5, True)

                # Create Ctrl+G key event
                event = Mock(spec=QKeyEvent)
                event.key.return_value = Qt.Key.Key_G
                event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
                event._mock_name = "test_event"

                # Should work for interior
                window.graphics_view.keyPressEvent(event)
                assert mock_dialog.call_count == 1

                # Switch to cover
                window.margin_presenter.model.document_type = "cover"
                window.navigation_presenter.set_total_pages(1)

                # Should not work for cover
                window.graphics_view.keyPressEvent(event)
                assert mock_dialog.call_count == 1  # Still 1, no new call

                # Switch back to interior
                window.margin_presenter.model.document_type = "interior"
                window.navigation_presenter.set_total_pages(10)

                # Should work again
                window.graphics_view.keyPressEvent(event)
                assert mock_dialog.call_count == 2  # Now 2 calls

    def test_no_margin_presenter_edge_case(self, qapp):
        """Test that missing margin presenter doesn't crash the application."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Remove margin presenter to simulate edge case
            window.margin_presenter = None

            # Mock the dialog
            with patch.object(QInputDialog, "getInt") as mock_dialog:
                # Create Ctrl+G key event
                event = Mock(spec=QKeyEvent)
                event.key.return_value = Qt.Key.Key_G
                event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier
                event._mock_name = "test_event"

                # Should not crash, dialog should not be shown
                window.graphics_view.keyPressEvent(event)
                mock_dialog.assert_not_called()

"""Tests for close document functionality (Ctrl+W)."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from momovu.views.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Create QApplication for tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(app, qtbot):
    """Create main window for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a temporary PDF file."""
    pdf_file = tmp_path / "test.pdf"
    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n203\n%%EOF"
    pdf_file.write_bytes(pdf_content)
    return str(pdf_file)


@pytest.fixture
def sample_pdf_2(tmp_path):
    """Create a second temporary PDF file."""
    pdf_file = tmp_path / "test2.pdf"
    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n203\n%%EOF"
    pdf_file.write_bytes(pdf_content)
    return str(pdf_file)


class TestCloseDocument:
    """Test close document functionality."""

    def test_close_action_exists(self, main_window):
        """Test that close action exists in File menu."""
        assert hasattr(main_window, "close_action")
        assert main_window.close_action is not None
        assert main_window.close_action.text() == "&Close"
        assert main_window.close_action.shortcut().toString() == "Ctrl+W"

    def test_close_action_disabled_initially(self, main_window):
        """Test that close action is disabled when no document is loaded."""
        assert not main_window.close_action.isEnabled()

    def test_close_pdf_no_document(self, main_window):
        """Test closing when no document is loaded."""
        # Should not raise any errors
        main_window.close_pdf()
        assert main_window.windowTitle() == "Momovu"

    def test_close_pdf_with_document(self, main_window):
        """Test closing a loaded document."""
        # Simulate a loaded document by setting the model state directly
        main_window.document_presenter._model.is_loaded = True
        main_window.document_presenter._model.file_path = "test.pdf"
        main_window.document_presenter._model.page_count = 5
        main_window.navigation_presenter.set_total_pages(5)
        main_window.close_action.setEnabled(True)

        # Close the document
        main_window.close_pdf()

        # Verify document is closed
        assert not main_window.document_presenter.is_document_loaded()
        assert not main_window.close_action.isEnabled()
        assert main_window.windowTitle() == "Momovu"
        assert main_window.page_label.text() == "Page: 0/0"
        assert main_window.page_number_spinbox.value() == 1
        assert not main_window.page_number_spinbox.isEnabled()

    def test_ctrl_w_shortcut(self, main_window, qtbot):
        """Test Ctrl+W keyboard shortcut."""
        # Simulate a loaded document
        main_window.document_presenter._model.is_loaded = True
        main_window.document_presenter._model.file_path = "test.pdf"
        main_window.close_action.setEnabled(True)

        # Press Ctrl+W
        key_event = QKeyEvent(
            QKeyEvent.Type.KeyPress, Qt.Key.Key_W, Qt.KeyboardModifier.ControlModifier
        )
        main_window.graphics_view.keyPressEvent(key_event)

        # Verify document is closed
        assert not main_window.document_presenter.is_document_loaded()

    def test_navigation_reset_on_close(self, main_window):
        """Test that navigation is reset when closing document."""
        # Simulate a loaded document
        main_window.document_presenter._model.is_loaded = True
        main_window.navigation_presenter.set_total_pages(5)
        main_window.navigation_presenter.go_to_page(2)  # Go to page 3
        assert main_window.navigation_presenter.get_current_page() == 2

        # Close the document
        main_window.close_pdf()

        # Verify navigation is reset
        assert main_window.navigation_presenter.get_current_page() == 0
        assert main_window.navigation_presenter.get_total_pages() == 0

    def test_scene_cleared_on_close(self, main_window):
        """Test that graphics scene is cleared when closing document."""
        # Simulate a loaded document
        main_window.document_presenter._model.is_loaded = True

        # Add some items to the scene
        main_window.graphics_scene.addRect(0, 0, 100, 100)
        main_window.graphics_scene.addRect(100, 100, 100, 100)
        assert len(main_window.graphics_scene.items()) > 0

        # Close the document
        main_window.close_pdf()

        # Verify scene is cleared
        assert len(main_window.graphics_scene.items()) == 0

    def test_close_action_triggered(self, main_window):
        """Test that close action triggers close_pdf."""
        # Simulate a loaded document
        main_window.document_presenter._model.is_loaded = True
        main_window.close_action.setEnabled(True)

        # Trigger the close action
        main_window.close_action.trigger()

        # Verify document is closed
        assert not main_window.document_presenter.is_document_loaded()

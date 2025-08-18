"""Integration tests for document loading scenarios.

These tests ensure that document loading works correctly across
different file types, sizes, and error conditions.
"""

from unittest.mock import patch

import pytest
from PySide6.QtPdf import QPdfDocument
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
def sample_pdf_path(tmp_path):
    """Create a temporary PDF file path."""
    pdf_file = tmp_path / "test_document.pdf"
    # Create a minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF"""
    pdf_file.write_bytes(pdf_content)
    return str(pdf_file)


class TestDocumentLoadingScenarios:
    """Test various document loading scenarios."""

    def test_successful_document_load(self, main_window, sample_pdf_path):
        """Test successful loading of a valid PDF document."""
        with (
            patch.object(QPdfDocument, "load"),
            patch.object(QPdfDocument, "status") as mock_status,
            patch.object(QPdfDocument, "pageCount", return_value=5),
        ):
            mock_status.return_value = QPdfDocument.Status.Ready
            # Load document
            main_window.document_presenter.load_document(sample_pdf_path)

            # Verify document is loaded
            assert main_window.document_presenter.is_loaded
            assert main_window.document_presenter.get_page_count() == 5

    def test_load_nonexistent_file(self, main_window):
        """Test loading a non-existent file."""
        fake_path = "/nonexistent/path/to/document.pdf"

        # Should handle gracefully
        result = main_window.document_presenter.load_document(fake_path)
        assert result is False
        assert not main_window.document_presenter.is_loaded

    def test_load_invalid_pdf(self, main_window, tmp_path):
        """Test loading an invalid PDF file."""
        # Create a file that's not a valid PDF
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a PDF file")

        with patch.object(QPdfDocument, "status") as mock_status:
            mock_status.return_value = QPdfDocument.Status.Error

            # Should handle invalid PDF gracefully
            result = main_window.document_presenter.load_document(str(invalid_pdf))
            assert result is False
            assert not main_window.document_presenter.is_loaded

    def test_load_empty_pdf(self, main_window, tmp_path):
        """Test loading an empty PDF file."""
        empty_pdf = tmp_path / "empty.pdf"
        empty_pdf.write_bytes(b"")

        with patch.object(QPdfDocument, "status") as mock_status:
            mock_status.return_value = QPdfDocument.Status.Error

            result = main_window.document_presenter.load_document(str(empty_pdf))
            assert result is False
            assert not main_window.document_presenter.is_loaded

    def test_load_large_document(self, main_window, sample_pdf_path):
        """Test loading a large document with many pages."""
        with (
            patch.object(QPdfDocument, "load"),
            patch.object(QPdfDocument, "status") as mock_status,
            patch.object(QPdfDocument, "pageCount", return_value=1000),
        ):
            mock_status.return_value = QPdfDocument.Status.Ready
            # Load large document
            main_window.document_presenter.load_document(sample_pdf_path)

            # Verify it handles large page counts
            assert main_window.document_presenter.get_page_count() == 1000
            assert main_window.navigation_presenter.get_total_pages() == 1000

    def test_reload_document(self, main_window, sample_pdf_path):
        """Test reloading a document (loading a new document when one is already loaded)."""
        # Load first document
        with patch.object(QPdfDocument, "status") as mock_status:
            mock_status.return_value = QPdfDocument.Status.Ready
            with patch.object(QPdfDocument, "pageCount", return_value=5):
                main_window.document_presenter.load_document(sample_pdf_path)
                assert main_window.document_presenter.get_page_count() == 5

        # Load second document
        with patch.object(QPdfDocument, "status") as mock_status:
            mock_status.return_value = QPdfDocument.Status.Ready
            with patch.object(QPdfDocument, "pageCount", return_value=10):
                main_window.document_presenter.load_document(sample_pdf_path)
                assert main_window.document_presenter.get_page_count() == 10

                # Navigation should reset
                assert main_window.navigation_presenter.get_current_page() == 0

    def test_document_type_detection(self, main_window, sample_pdf_path):
        """Test automatic document type detection based on filename."""
        # Test interior document
        interior_path = "/path/to/document-interior.pdf"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch.object(QPdfDocument, "load"),
            patch.object(QPdfDocument, "status") as mock_status,
        ):
            mock_status.return_value = QPdfDocument.Status.Ready
            main_window.load_pdf(interior_path)
            assert main_window.margin_presenter.get_document_type() == "interior"

        # Test cover document
        cover_path = "/path/to/document-cover.pdf"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch.object(QPdfDocument, "load"),
            patch.object(QPdfDocument, "status") as mock_status,
        ):
            mock_status.return_value = QPdfDocument.Status.Ready
            main_window.load_pdf(cover_path)
            assert main_window.margin_presenter.get_document_type() == "cover"

        # Test dustjacket document
        dustjacket_path = "/path/to/document-dustjacket.pdf"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch.object(QPdfDocument, "load"),
            patch.object(QPdfDocument, "status") as mock_status,
        ):
            mock_status.return_value = QPdfDocument.Status.Ready
            main_window.load_pdf(dustjacket_path)
            assert main_window.margin_presenter.get_document_type() == "dustjacket"


class TestDocumentOperationsWithoutDocument:
    """Test operations when no document is loaded."""

    def test_navigation_without_document(self, main_window):
        """Test navigation operations without a loaded document."""
        # Ensure no document is loaded
        assert not main_window.document_presenter.is_loaded()

        # Navigation should be disabled/do nothing
        initial_page = main_window.navigation_presenter.get_current_page()
        main_window.navigation_presenter.next_page()
        assert main_window.navigation_presenter.get_current_page() == initial_page

    def test_rendering_without_document(self, main_window):
        """Test rendering operations without a loaded document."""
        # Ensure no document is loaded
        assert not main_window.document_presenter.is_loaded

        # Rendering should handle gracefully
        main_window.page_renderer.render_current_page()

        # Scene should be empty or have minimal items
        items = main_window.graphics_scene.items()
        page_items = [item for item in items if hasattr(item, "page_index")]
        assert len(page_items) == 0

    def test_view_mode_switch_without_document(self, main_window):
        """Test view mode switching without a loaded document."""
        # Should be able to switch modes even without document
        initial_mode = main_window.navigation_presenter.model.view_mode
        main_window.toggle_manager.toggle_view_mode()
        assert main_window.navigation_presenter.model.view_mode != initial_mode

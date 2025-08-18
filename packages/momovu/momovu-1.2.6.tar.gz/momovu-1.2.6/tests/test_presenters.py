"""Fixed comprehensive tests for MVP presenters.

These are REAL tests that test actual functionality based on the actual implementation.
Following best practices: isolated, deterministic, and meaningful.
"""

from unittest.mock import Mock

from PySide6.QtPdf import QPdfDocument

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter


class TestDocumentPresenter:
    """Test DocumentPresenter with real methods."""

    def test_initialization(self):
        """Test presenter initialization."""
        # Without model
        presenter = DocumentPresenter()
        assert presenter.model is not None
        assert isinstance(presenter.model, Document)
        assert presenter._qt_document is None

        # With model
        model = Document()
        presenter = DocumentPresenter(model)
        assert presenter.model == model

    def test_set_qt_document(self):
        """Test setting Qt document."""
        presenter = DocumentPresenter()
        mock_doc = Mock(spec=QPdfDocument)

        presenter.set_qt_document(mock_doc)
        assert presenter._qt_document == mock_doc

    def test_load_document_file_not_found(self):
        """Test loading non-existent file."""
        presenter = DocumentPresenter()

        result = presenter.load_document("/nonexistent/file.pdf")

        assert result is False
        assert presenter.model.is_loaded is False
        assert presenter.model.error_message is not None
        assert "File not found" in presenter.model.error_message

    def test_load_document_not_a_file(self, tmp_path):
        """Test loading a directory instead of file."""
        presenter = DocumentPresenter()

        # Create a directory
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        result = presenter.load_document(str(test_dir))

        assert result is False
        assert presenter.model.is_loaded is False
        assert "Not a file" in presenter.model.error_message

    def test_load_document_with_qt_success(self, tmp_path):
        """Test successful document loading with Qt document."""
        presenter = DocumentPresenter()

        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_text("fake pdf content")

        # Mock Qt document
        mock_doc = Mock(spec=QPdfDocument)
        mock_doc.load.return_value = QPdfDocument.Error.None_
        mock_doc.pageCount.return_value = 3

        # Mock page sizes
        mock_size = Mock()
        mock_size.width.return_value = 612.0
        mock_size.height.return_value = 792.0
        mock_doc.pagePointSize.return_value = mock_size

        presenter.set_qt_document(mock_doc)

        result = presenter.load_document(str(test_file))

        assert result is True
        assert presenter.model.is_loaded is True
        assert presenter.model.file_path == str(test_file)
        assert presenter.model.page_count == 3
        assert presenter.model.error_message is None
        mock_doc.load.assert_called_once_with(str(test_file))

    def test_get_page_count_with_qt(self):
        """Test getting page count with Qt document."""
        presenter = DocumentPresenter()

        mock_doc = Mock(spec=QPdfDocument)
        mock_doc.pageCount.return_value = 10
        presenter.set_qt_document(mock_doc)

        count = presenter.get_page_count()
        assert count == 10

    def test_get_page_count_without_qt(self):
        """Test getting page count from model."""
        presenter = DocumentPresenter()
        presenter.model.page_count = 5

        count = presenter.get_page_count()
        assert count == 5

    def test_is_document_loaded(self):
        """Test checking if document is loaded."""
        presenter = DocumentPresenter()

        assert presenter.is_document_loaded() is False

        presenter.model.is_loaded = True
        assert presenter.is_document_loaded() is True


class TestMarginPresenter:
    """Test MarginPresenter with real methods."""

    def test_initialization(self):
        """Test presenter initialization."""
        # Without model
        presenter = MarginPresenter()
        assert presenter.model is not None
        assert isinstance(presenter.model, MarginSettingsModel)

        # With model
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)
        assert presenter.model == model

    def test_set_document_type(self):
        """Test setting document type."""
        presenter = MarginPresenter()

        presenter.set_document_type("cover")
        assert presenter.model.document_type == "cover"
        # Should calculate spine width
        assert presenter.model.spine_width is not None

    def test_set_document_type_dustjacket(self):
        """Test setting document type to dustjacket."""
        presenter = MarginPresenter()

        presenter.set_document_type("dustjacket")
        assert presenter.model.document_type == "dustjacket"
        # Should set flap dimensions
        assert presenter.model.flap_width is not None
        assert presenter.model.flap_height is not None

    def test_set_num_pages(self):
        """Test setting number of pages."""
        presenter = MarginPresenter()
        presenter.set_document_type("cover")  # Need cover/dustjacket for spine

        presenter.set_num_pages(200)
        assert presenter.model.num_pages == 200
        assert presenter.model.spine_width is not None
        assert presenter.model.spine_width > 0

    def test_visibility_setters(self):
        """Test all visibility flag setters."""
        presenter = MarginPresenter()

        presenter.set_show_margins(False)
        assert presenter.model.show_margins is False

        presenter.set_show_trim_lines(False)
        assert presenter.model.show_trim_lines is False

        presenter.set_show_barcode(False)
        assert presenter.model.show_barcode is False

        presenter.set_show_fold_lines(False)
        assert presenter.model.show_fold_lines is False


class TestNavigationPresenter:
    """Test NavigationPresenter with real methods."""

    def test_initialization(self):
        """Test presenter initialization."""
        # Without model
        presenter = NavigationPresenter()
        assert presenter.model is not None
        assert isinstance(presenter.model, ViewStateModel)
        assert presenter._total_pages == 0

        # With model and total pages
        model = ViewStateModel()
        presenter = NavigationPresenter(model, total_pages=10)
        assert presenter.model == model
        assert presenter._total_pages == 10

    def test_set_total_pages(self):
        """Test setting total pages."""
        presenter = NavigationPresenter()
        presenter.model.current_page = 15

        presenter.set_total_pages(10)
        assert presenter._total_pages == 10
        # Should adjust current page if out of bounds
        assert presenter.model.current_page == 9

    def test_go_to_page(self):
        """Test going to specific page."""
        presenter = NavigationPresenter(total_pages=10)

        # Valid page
        result = presenter.go_to_page(5)
        assert result is True
        assert presenter.model.current_page == 5

        # Invalid pages
        result = presenter.go_to_page(-1)
        assert result is False

        result = presenter.go_to_page(20)
        assert result is False

    def test_go_to_page_side_by_side(self):
        """Test going to page in side-by-side mode."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.view_mode = "side_by_side"

        # Odd page should adjust to even
        result = presenter.go_to_page(5)
        assert result is True
        assert presenter.model.current_page == 4  # Adjusted to even

    def test_next_page(self):
        """Test going to next page."""
        presenter = NavigationPresenter(total_pages=10)

        result = presenter.next_page()
        assert result is True
        assert presenter.model.current_page == 1

        # At last page
        presenter.model.current_page = 9
        result = presenter.next_page()
        assert result is False
        assert presenter.model.current_page == 9

    def test_next_page_side_by_side(self):
        """Test next page in side-by-side mode."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.view_mode = "side_by_side"

        result = presenter.next_page()
        assert result is True
        assert presenter.model.current_page == 2  # Moves by 2

    def test_previous_page(self):
        """Test going to previous page."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.current_page = 5

        result = presenter.previous_page()
        assert result is True
        assert presenter.model.current_page == 4

        # At first page
        presenter.model.current_page = 0
        result = presenter.previous_page()
        assert result is False
        assert presenter.model.current_page == 0

    def test_go_to_first_page(self):
        """Test going to first page."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.current_page = 5

        result = presenter.go_to_first_page()
        assert result is True
        assert presenter.model.current_page == 0

    def test_first_page_alias(self):
        """Test go_to_first_page method (previously first_page alias)."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.current_page = 5

        result = presenter.go_to_first_page()
        assert result is True
        assert presenter.model.current_page == 0

    def test_go_to_last_page(self):
        """Test going to last page."""
        presenter = NavigationPresenter(total_pages=10)

        result = presenter.go_to_last_page()
        assert result is True
        assert presenter.model.current_page == 9

    def test_go_to_last_page_side_by_side(self):
        """Test going to last page in side-by-side mode."""
        presenter = NavigationPresenter(total_pages=11)
        presenter.model.view_mode = "side_by_side"

        result = presenter.go_to_last_page()
        assert result is True
        assert presenter.model.current_page == 9  # Shows pages 10-11 (last spread)

    def test_last_page_alias(self):
        """Test go_to_last_page method (previously last_page alias)."""
        presenter = NavigationPresenter(total_pages=10)

        result = presenter.go_to_last_page()
        assert result is True
        assert presenter.model.current_page == 9

    def test_set_view_mode(self):
        """Test setting view mode."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.set_view_mode("side_by_side")
        assert presenter.model.view_mode == "side_by_side"

        # Invalid mode should be ignored
        presenter.set_view_mode("invalid")
        assert presenter.model.view_mode == "side_by_side"

    def test_toggle_view_mode(self):
        """Test toggling view mode."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.model.view_mode = "single"
        presenter.toggle_view_mode()
        assert presenter.model.view_mode == "side_by_side"

        presenter.toggle_view_mode()
        assert presenter.model.view_mode == "single"

    def test_get_current_page(self):
        """Test getting current page."""
        presenter = NavigationPresenter(total_pages=10)
        presenter.model.current_page = 7

        assert presenter.get_current_page() == 7

    def test_get_total_pages(self):
        """Test getting total pages."""
        presenter = NavigationPresenter(total_pages=15)

        assert presenter.get_total_pages() == 15

    def test_get_current_page_pair(self):
        """Test getting current page pair."""
        presenter = NavigationPresenter(total_pages=10)

        # Single mode
        presenter.model.view_mode = "single"
        presenter.model.current_page = 5
        left, right = presenter.get_current_page_pair()
        assert left == 5
        assert right is None

        # Side-by-side mode
        presenter.model.view_mode = "side_by_side"
        presenter.model.current_page = 4
        left, right = presenter.get_current_page_pair()
        assert left == 4
        assert right == 5

    def test_is_at_first_page(self):
        """Test checking if at first page."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.model.current_page = 0
        assert presenter.is_at_first_page() is True

        presenter.model.current_page = 5
        assert presenter.is_at_first_page() is False

    def test_is_at_last_page(self):
        """Test checking if at last page."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.model.current_page = 9
        assert presenter.is_at_last_page() is True

        presenter.model.current_page = 5
        assert presenter.is_at_last_page() is False

    def test_can_go_next(self):
        """Test checking if can go to next page."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.model.current_page = 5
        assert presenter.can_go_next() is True

        presenter.model.current_page = 9
        assert presenter.can_go_next() is False

    def test_can_go_previous(self):
        """Test checking if can go to previous page."""
        presenter = NavigationPresenter(total_pages=10)

        presenter.model.current_page = 0
        assert presenter.can_go_previous() is False

        presenter.model.current_page = 5
        assert presenter.can_go_previous() is True

    def test_get_page_display_text(self):
        """Test getting page display text."""
        presenter = NavigationPresenter(total_pages=10)

        # Single page
        presenter.model.current_page = 5
        text = presenter.get_page_display_text()
        assert text == "Page 6 of 10"

        # Side-by-side
        presenter.model.view_mode = "side_by_side"
        presenter.model.current_page = 4
        text = presenter.get_page_display_text()
        assert text == "Pages 5-6 of 10"

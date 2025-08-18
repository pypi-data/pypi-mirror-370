"""Fixed comprehensive tests for MVP models.

These are REAL tests that test actual functionality, not fake methods.
Following best practices: isolated, deterministic, and meaningful.
"""

from unittest.mock import Mock

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel


class TestMarginSettingsModel:
    """Test MarginSettingsModel with real methods."""

    def test_initialization_defaults(self):
        """Test model initializes with correct defaults."""
        model = MarginSettingsModel()

        # Test actual default values
        assert model.document_type == "interior"
        assert model.num_pages == 100
        assert model.safety_margin_mm == 12.7
        assert model.safety_margin_points == 36.0
        assert model.spine_width is None
        assert model.flap_width is None
        assert model.flap_height is None
        assert model.show_margins is True
        assert model.show_trim_lines is True
        assert model.show_barcode is True
        assert model.show_fold_lines is True

    def test_document_type_property(self):
        """Test document type getter and setter."""
        model = MarginSettingsModel()

        # Test setting valid document types
        model.document_type = "cover"
        assert model.document_type == "cover"

        model.document_type = "dustjacket"
        assert model.document_type == "dustjacket"

        model.document_type = "interior"
        assert model.document_type == "interior"

    def test_document_type_validation(self):
        """Test document type validation."""
        model = MarginSettingsModel()

        # Invalid document type should not change the value
        model.document_type = "interior"
        result = model.set_property("document_type", "invalid_type")
        assert result is False  # Validation failed
        assert model.document_type == "interior"  # Value unchanged

    def test_num_pages_property(self):
        """Test num_pages property with validation."""
        model = MarginSettingsModel()

        model.num_pages = 200
        assert model.num_pages == 200

        # Test validation - must be positive integer
        result = model.set_property("num_pages", -1)
        assert result is False
        assert model.num_pages == 200  # Unchanged

        result = model.set_property("num_pages", 0)
        assert result is False
        assert model.num_pages == 200  # Unchanged

    def test_safety_margin_properties(self):
        """Test safety margin in mm and points."""
        model = MarginSettingsModel()

        model.safety_margin_mm = 25.4  # 1 inch
        assert model.safety_margin_mm == 25.4

        model.safety_margin_points = 72.0  # 1 inch in points
        assert model.safety_margin_points == 72.0

        # Test validation - must be non-negative
        result = model.set_property("safety_margin_mm", -1.0)
        assert result is False
        assert model.safety_margin_mm == 25.4  # Unchanged

    def test_spine_dimensions_properties(self):
        """Test spine width and flap dimensions."""
        model = MarginSettingsModel()

        # Initially None
        assert model.spine_width is None
        assert model.flap_width is None
        assert model.flap_height is None

        # Set values
        model.spine_width = 10.5
        assert model.spine_width == 10.5

        model.flap_width = 100.0
        assert model.flap_width == 100.0

        model.flap_height = 200.0
        assert model.flap_height == 200.0

        # Can be set back to None
        model.spine_width = None
        assert model.spine_width is None

    def test_visibility_flags(self):
        """Test show_margins, show_trim_lines, etc."""
        model = MarginSettingsModel()

        # Test toggling each flag
        model.show_margins = False
        assert model.show_margins is False

        model.show_trim_lines = False
        assert model.show_trim_lines is False

        model.show_barcode = False
        assert model.show_barcode is False

        model.show_fold_lines = False
        assert model.show_fold_lines is False

    def test_repr(self):
        """Test string representation."""
        model = MarginSettingsModel()
        repr_str = repr(model)

        assert "MarginSettingsModel" in repr_str
        assert "document_type='interior'" in repr_str
        assert "safety_margin_mm=12.7" in repr_str


class TestPDFDocumentModel:
    """Test Document with real methods."""

    def test_initialization_defaults(self):
        """Test model initializes with correct defaults."""
        model = Document()

        assert model.file_path is None
        assert model.page_count == 0
        assert model.page_sizes == []
        assert model.is_loaded is False
        assert model.error_message is None

    def test_file_path_property(self):
        """Test file_path property."""
        model = Document()

        model.file_path = "/path/to/document.pdf"
        assert model.file_path == "/path/to/document.pdf"

        model.file_path = None
        assert model.file_path is None

    def test_page_count_property(self):
        """Test page_count property with validation."""
        model = Document()

        model.page_count = 10
        assert model.page_count == 10

        # Test validation - must be non-negative
        result = model.set_property("page_count", -1)
        assert result is False
        assert model.page_count == 10  # Unchanged

    def test_page_sizes_property(self):
        """Test page_sizes property."""
        model = Document()

        sizes = [(612.0, 792.0), (595.0, 842.0)]
        model.page_sizes = sizes
        assert model.page_sizes == sizes

        # Test validation - must be a list
        result = model.set_property("page_sizes", "not a list")
        assert result is False
        assert model.page_sizes == sizes  # Unchanged

    def test_is_loaded_property(self):
        """Test is_loaded property."""
        model = Document()

        assert model.is_loaded is False

        model.is_loaded = True
        assert model.is_loaded is True

    def test_error_message_property(self):
        """Test error_message property."""
        model = Document()

        assert model.error_message is None

        model.error_message = "Failed to load"
        assert model.error_message == "Failed to load"

    def test_get_page_size(self):
        """Test get_page_size method."""
        model = Document()

        sizes = [(612.0, 792.0), (595.0, 842.0), (420.0, 595.0)]
        model.page_sizes = sizes

        # Valid indices
        assert model.get_page_size(0) == (612.0, 792.0)
        assert model.get_page_size(1) == (595.0, 842.0)
        assert model.get_page_size(2) == (420.0, 595.0)

        # Invalid indices
        assert model.get_page_size(-1) is None
        assert model.get_page_size(3) is None
        assert model.get_page_size(100) is None

    def test_clear_method(self):
        """Test clear method resets all properties."""
        model = Document()

        # Set some values
        model.file_path = "/path/to/doc.pdf"
        model.page_count = 5
        model.page_sizes = [(612.0, 792.0)]
        model.is_loaded = True
        model.error_message = "Some error"

        # Clear
        model.clear()

        # Check all reset
        assert model.file_path is None
        assert model.page_count == 0
        assert model.page_sizes == []
        assert model.is_loaded is False
        assert model.error_message is None

    def test_update_from_document_info(self):
        """Test update_from_document_info batch update."""
        model = Document()
        observer = Mock()
        model.add_observer(observer)

        sizes = [(612.0, 792.0), (595.0, 842.0)]
        model.update_from_document_info(
            file_path="/path/to/doc.pdf", page_count=2, page_sizes=sizes
        )

        assert model.file_path == "/path/to/doc.pdf"
        assert model.page_count == 2
        assert model.page_sizes == sizes
        assert model.is_loaded is True
        assert model.error_message is None

    def test_set_error(self):
        """Test set_error method."""
        model = Document()

        model.is_loaded = True
        model.set_error("Failed to load PDF")

        assert model.is_loaded is False
        assert model.error_message == "Failed to load PDF"

    def test_repr(self):
        """Test string representation."""
        model = Document()
        model.file_path = "test.pdf"
        model.page_count = 5
        model.is_loaded = True

        repr_str = repr(model)
        assert "Document" in repr_str
        assert "file_path='test.pdf'" in repr_str
        assert "page_count=5" in repr_str
        assert "is_loaded=True" in repr_str


class TestViewStateModel:
    """Test ViewStateModel with real methods."""

    def test_initialization_defaults(self):
        """Test model initializes with correct defaults."""
        model = ViewStateModel()

        assert model.current_page == 0
        assert model.view_mode == "single"
        assert model.zoom_level == 1.0
        assert model.show_margins is True
        assert model.show_trim_lines is True
        assert model.show_spine_line is True
        assert model.show_fold_lines is True
        assert model.show_barcode is True
        assert model.is_fullscreen is False
        assert model.is_presentation is False

    def test_current_page_property(self):
        """Test current_page property with validation."""
        model = ViewStateModel()

        model.current_page = 5
        assert model.current_page == 5

        # Test validation - must be non-negative
        result = model.set_property("current_page", -1)
        assert result is False
        assert model.current_page == 5  # Unchanged

    def test_view_mode_property(self):
        """Test view_mode property with validation."""
        model = ViewStateModel()

        model.view_mode = "side_by_side"
        assert model.view_mode == "side_by_side"

        model.view_mode = "single"
        assert model.view_mode == "single"

        # Test validation
        result = model.set_property("view_mode", "invalid_mode")
        assert result is False
        assert model.view_mode == "single"  # Unchanged

    def test_view_mode_helper_methods(self):
        """Test is_single_page_mode and is_side_by_side_mode."""
        model = ViewStateModel()

        model.view_mode = "single"
        assert model.is_single_page_mode() is True
        assert model.is_side_by_side_mode() is False

        model.view_mode = "side_by_side"
        assert model.is_single_page_mode() is False
        assert model.is_side_by_side_mode() is True

    def test_toggle_view_mode(self):
        """Test toggle_view_mode method."""
        model = ViewStateModel()

        # Start in single mode
        assert model.view_mode == "single"

        # Toggle to side-by-side
        model.toggle_view_mode()
        assert model.view_mode == "side_by_side"

        # Toggle back to single
        model.toggle_view_mode()
        assert model.view_mode == "single"

    def test_zoom_level_property(self):
        """Test zoom_level property with validation."""
        model = ViewStateModel()

        model.zoom_level = 2.0
        assert model.zoom_level == 2.0

        # Test validation - must be between 0.1 and 10.0
        result = model.set_property("zoom_level", 0.05)
        assert result is False
        assert model.zoom_level == 2.0  # Unchanged

        result = model.set_property("zoom_level", 15.0)
        assert result is False
        assert model.zoom_level == 2.0  # Unchanged

    def test_visibility_flags(self):
        """Test all visibility flag properties."""
        model = ViewStateModel()

        # Test each flag can be toggled
        model.show_margins = False
        assert model.show_margins is False

        model.show_trim_lines = False
        assert model.show_trim_lines is False

        model.show_spine_line = False
        assert model.show_spine_line is False

        model.show_fold_lines = False
        assert model.show_fold_lines is False

        model.show_barcode = False
        assert model.show_barcode is False

    def test_fullscreen_and_presentation_properties(self):
        """Test fullscreen and presentation mode properties."""
        model = ViewStateModel()

        model.is_fullscreen = True
        assert model.is_fullscreen is True

        model.is_presentation = True
        assert model.is_presentation is True

    def test_repr(self):
        """Test string representation."""
        model = ViewStateModel()
        model.current_page = 5
        model.view_mode = "side_by_side"
        model.zoom_level = 1.5

        repr_str = repr(model)
        assert "ViewStateModel" in repr_str
        assert "current_page=5" in repr_str
        assert "view_mode='side_by_side'" in repr_str
        assert "zoom_level=1.5" in repr_str

    def test_property_change_notifications(self):
        """Test that property changes trigger notifications."""
        model = ViewStateModel()
        observer = Mock()
        model.add_observer(observer)

        # Change a property
        model.current_page = 5

        # Observer should be called
        observer.assert_called()

        # Check the event
        call_args = observer.call_args[0][0]
        assert hasattr(call_args, "property_name")
        assert hasattr(call_args, "old_value")
        assert hasattr(call_args, "new_value")

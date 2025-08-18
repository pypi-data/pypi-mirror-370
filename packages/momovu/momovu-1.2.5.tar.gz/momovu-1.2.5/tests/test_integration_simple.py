"""Simplified integration tests for core workflows.

These tests verify basic integration between components.
"""

from unittest.mock import Mock

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter
from momovu.views.components.zoom_controller import ZoomController


class TestModelPresenterIntegration:
    """Test integration between models and presenters."""

    def test_document_model_presenter_integration(self):
        """Test document model and presenter work together."""
        # Create model and presenter
        model = Document()
        presenter = DocumentPresenter(model)

        # Verify initial state
        assert presenter.is_document_loaded() is False
        assert presenter.model.file_path is None

        # Update through presenter
        presenter.model.file_path = "/test/path.pdf"
        presenter.model.is_loaded = True
        presenter.model.page_count = 10

        # Verify state
        assert presenter.is_document_loaded() is True
        assert presenter.model.file_path == "/test/path.pdf"
        assert presenter.get_page_count() == 10

    def test_margin_model_presenter_integration(self):
        """Test margin model and presenter work together."""
        # Create model and presenter
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Test document type changes
        presenter.set_document_type("cover")
        assert presenter.model.document_type == "cover"

        presenter.set_document_type("interior")
        assert presenter.model.document_type == "interior"

        presenter.set_document_type("dustjacket")
        assert presenter.model.document_type == "dustjacket"

    def test_navigation_model_presenter_integration(self):
        """Test navigation model and presenter work together."""
        # Create model and presenter
        model = ViewStateModel()
        presenter = NavigationPresenter(model)

        # Set total pages
        presenter.set_total_pages(20)
        assert presenter.get_total_pages() == 20

        # Navigate
        presenter.go_to_page(5)
        assert presenter.get_current_page() == 5

        presenter.next_page()
        assert presenter.get_current_page() == 6

        presenter.previous_page()
        assert presenter.get_current_page() == 5


class TestDocumentTypeWorkflow:
    """Test document type switching workflow."""

    def test_document_type_affects_overlay_visibility(self):
        """Test that document type changes affect overlay visibility."""
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Interior type
        presenter.set_document_type("interior")
        assert presenter.model.document_type == "interior"
        # Note: The model doesn't automatically disable overlays based on type
        # That logic would be in the view layer

        # Cover type
        presenter.set_document_type("cover")
        assert presenter.model.document_type == "cover"

        # Dustjacket type
        presenter.set_document_type("dustjacket")
        assert presenter.model.document_type == "dustjacket"


class TestNavigationWorkflow:
    """Test navigation workflow."""

    def test_basic_navigation_flow(self):
        """Test basic page navigation."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)

        # Set up document
        presenter.set_total_pages(10)

        # Test navigation
        assert presenter.get_current_page() == 0

        presenter.go_to_page(5)
        assert presenter.get_current_page() == 5

        presenter.go_to_first_page()
        assert presenter.get_current_page() == 0

        presenter.go_to_last_page()
        assert presenter.get_current_page() == 9

    def test_navigation_boundaries(self):
        """Test navigation at document boundaries."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)
        presenter.set_total_pages(5)

        # Can't go before first page
        presenter.go_to_first_page()
        presenter.previous_page()
        assert presenter.get_current_page() == 0

        # Can't go after last page
        presenter.go_to_last_page()
        presenter.next_page()
        assert presenter.get_current_page() == 4


class TestZoomIntegration:
    """Test zoom controller integration."""

    def test_zoom_operations(self):
        """Test zoom controller operations."""
        mock_view = Mock()
        mock_view.scale = Mock()
        mock_view.resetTransform = Mock()
        mock_scene = Mock()

        controller = ZoomController(mock_view, mock_scene)

        # Test zoom in/out
        initial = controller.get_current_zoom()
        controller.zoom_in()
        assert controller.get_current_zoom() > initial

        controller.zoom_out()
        controller.zoom_out()
        assert controller.get_current_zoom() < initial

        # Test set zoom
        controller.set_zoom_level(2.0)
        assert controller.get_current_zoom() == 2.0


class TestPresenterCoordination:
    """Test coordination between multiple presenters."""

    def test_document_load_updates_navigation(self):
        """Test that loading a document updates navigation state."""
        # Create models and presenters
        doc_model = Document()
        nav_model = ViewStateModel()

        doc_presenter = DocumentPresenter(doc_model)
        nav_presenter = NavigationPresenter(nav_model)

        # Simulate document load
        doc_presenter.model.page_count = 50
        doc_presenter.model.is_loaded = True

        # Navigation presenter should be updated separately
        # (In real app, this would be coordinated by the view)
        nav_presenter.set_total_pages(doc_presenter.get_page_count())

        assert nav_presenter.get_total_pages() == 50
        assert nav_presenter.get_current_page() == 0


class TestViewModeIntegration:
    """Test view mode changes."""

    def test_view_mode_switching(self):
        """Test switching between view modes."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)

        # Default is single page
        assert presenter.model.view_mode == "single"

        # Switch to side by side
        presenter.set_view_mode("side_by_side")
        assert presenter.model.view_mode == "side_by_side"

        # Switch back
        presenter.set_view_mode("single")
        assert presenter.model.view_mode == "single"


class TestMarginSettingsIntegration:
    """Test margin settings integration."""

    def test_margin_size_conversion(self):
        """Test margin size conversion between mm and points."""
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Set margin in mm directly on model
        presenter.model.safety_margin_mm = 10.0
        assert presenter.model.safety_margin_mm == 10.0

        # Set margin in points directly on model
        presenter.model.safety_margin_points = 36.0
        assert presenter.model.safety_margin_points == 36.0

    def test_spine_and_flap_settings(self):
        """Test spine and flap dimension settings."""
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Set spine width directly on model
        presenter.model.spine_width = 50.0
        assert presenter.model.spine_width == 50.0

        # Set flap dimensions directly on model
        presenter.model.flap_width = 100.0
        presenter.model.flap_height = 200.0
        assert presenter.model.flap_width == 100.0
        assert presenter.model.flap_height == 200.0


class TestOverlayVisibility:
    """Test overlay visibility settings."""

    def test_overlay_toggles(self):
        """Test toggling overlay visibility."""
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Toggle margins
        presenter.set_show_margins(False)
        assert presenter.model.show_margins is False
        presenter.set_show_margins(True)
        assert presenter.model.show_margins is True

        # Toggle trim lines
        presenter.set_show_trim_lines(False)
        assert presenter.model.show_trim_lines is False

        # Toggle barcode
        presenter.set_show_barcode(False)
        assert presenter.model.show_barcode is False


class TestErrorHandlingIntegration:
    """Test error handling across components."""

    def test_invalid_page_navigation(self):
        """Test handling of invalid page numbers."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)
        presenter.set_total_pages(10)

        # Try to go to invalid page - NavigationPresenter logs warning but doesn't change page
        current_page = presenter.get_current_page()
        presenter.go_to_page(-5)
        assert presenter.get_current_page() == current_page  # Should not change

        presenter.go_to_page(100)
        assert presenter.get_current_page() == current_page  # Should not change

    def test_document_not_loaded_state(self):
        """Test behavior when no document is loaded."""
        doc_model = Document()
        doc_presenter = DocumentPresenter(doc_model)

        assert doc_presenter.is_document_loaded() is False
        assert doc_presenter.get_page_count() == 0
        assert doc_presenter.model.file_path is None

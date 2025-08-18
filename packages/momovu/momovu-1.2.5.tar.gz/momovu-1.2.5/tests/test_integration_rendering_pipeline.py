"""Integration tests for the complete rendering pipeline.

These tests ensure that all rendering components work together correctly
from document loading through to final display.
"""

from unittest.mock import patch

import pytest
from PySide6.QtCore import QSizeF
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QApplication, QGraphicsScene

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter
from momovu.views.components.page_renderer import PageRenderer
from momovu.views.page_item import PageItem


@pytest.fixture
def app(qtbot):
    """Create QApplication for tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def rendering_pipeline(app):
    """Create a complete rendering pipeline setup."""
    # Create models
    document_model = Document()
    margin_model = MarginSettingsModel()
    view_model = ViewStateModel()

    # Create presenters
    document_presenter = DocumentPresenter(document_model)
    margin_presenter = MarginPresenter(margin_model)
    navigation_presenter = NavigationPresenter(view_model)

    # Create Qt components
    graphics_scene = QGraphicsScene()
    pdf_document = QPdfDocument()

    # Create renderer
    page_renderer = PageRenderer(
        graphics_scene,
        pdf_document,
        document_presenter,
        margin_presenter,
        navigation_presenter,
    )

    return {
        "scene": graphics_scene,
        "pdf_document": pdf_document,
        "document_presenter": document_presenter,
        "margin_presenter": margin_presenter,
        "navigation_presenter": navigation_presenter,
        "page_renderer": page_renderer,
        "document_model": document_model,
        "margin_model": margin_model,
        "view_model": view_model,
    }


class TestRenderingPipeline:
    """Test the complete rendering pipeline."""

    def test_single_page_rendering_flow(self, rendering_pipeline):
        """Test rendering a single page document."""
        pipeline = rendering_pipeline

        # Setup mock document
        with (
            patch.object(pipeline["pdf_document"], "pageCount", return_value=1),
            patch.object(pipeline["pdf_document"], "pagePointSize") as mock_size,
        ):
            mock_size.return_value = QSizeF(612, 792)  # US Letter

            # Simulate document loaded
            pipeline["document_model"].page_count = 1
            pipeline["document_model"].is_loaded = True
            pipeline["document_model"].page_sizes = [(612, 792)]

            # Render current page
            pipeline["page_renderer"].render_current_page()

            # Verify scene has items
            items = pipeline["scene"].items()
            assert len(items) > 0

            # Verify page item was created
            page_items = [item for item in items if isinstance(item, PageItem)]
            assert len(page_items) == 1

    def test_multi_page_interior_rendering(self, rendering_pipeline):
        """Test rendering multiple pages for interior document."""
        pipeline = rendering_pipeline

        # Setup as interior document with multiple pages
        pipeline["margin_model"].document_type = "interior"
        pipeline["document_model"].page_count = 10
        pipeline["document_model"].is_loaded = True
        pipeline["document_model"].page_sizes = [(612, 792)] * 10

        with (
            patch.object(pipeline["pdf_document"], "pageCount", return_value=10),
            patch.object(pipeline["pdf_document"], "pagePointSize") as mock_size,
        ):
            mock_size.return_value = QSizeF(612, 792)

            # Render

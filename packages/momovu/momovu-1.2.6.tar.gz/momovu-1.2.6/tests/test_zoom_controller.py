"""Comprehensive tests for ZoomController component.

Tests focus on zoom calculations, fit operations, and presenter integration.
These tests improve coverage from 31% to target 80%+.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from momovu.lib.constants import (
    SCENE_FIT_HEIGHT,
    VIEWPORT_FIT_MARGIN,
    ZOOM_IN_FACTOR,
    ZOOM_OUT_FACTOR,
)
from momovu.views.components.zoom_controller import ZoomController


class TestZoomController:
    """Test ZoomController functionality."""

    @pytest.fixture
    def mock_graphics_view(self):
        """Create a mock graphics view."""
        view = Mock(spec=QGraphicsView)
        view.scale = Mock()
        view.viewport = Mock(
            return_value=Mock(
                rect=Mock(
                    return_value=Mock(center=Mock(return_value=Mock()), adjust=Mock())
                )
            )
        )
        view.fitInView = Mock()
        view.mapToScene = Mock(return_value=Mock(y=Mock(return_value=100)))
        return view

    @pytest.fixture
    def mock_graphics_scene(self):
        """Create a mock graphics scene."""
        scene = Mock(spec=QGraphicsScene)
        scene.itemsBoundingRect = Mock(return_value=QRectF(0, 0, 612, 792))
        scene.items = Mock(return_value=[])
        return scene

    @pytest.fixture
    def zoom_controller(self, mock_graphics_view, mock_graphics_scene):
        """Create a ZoomController instance."""
        controller = ZoomController(mock_graphics_view, mock_graphics_scene)
        # Properly mock the signal
        controller.zoom_changed = Mock()
        controller.zoom_changed.emit = Mock()
        return controller

    @pytest.fixture
    def mock_presenters(self):
        """Create mock presenters."""
        margin_presenter = Mock()
        margin_presenter.model = Mock()
        margin_presenter.model.document_type = "interior"

        navigation_presenter = Mock()
        navigation_presenter.model = Mock()
        navigation_presenter.model.view_mode = "single"
        navigation_presenter.get_current_page = Mock(return_value=0)

        document_presenter = Mock()
        document_presenter.get_page_count = Mock(return_value=10)

        return margin_presenter, navigation_presenter, document_presenter

    # Test initialization
    def test_initialization(self, mock_graphics_view, mock_graphics_scene):
        """Test ZoomController initialization."""
        controller = ZoomController(mock_graphics_view, mock_graphics_scene)

        assert controller.graphics_view == mock_graphics_view
        assert controller.graphics_scene == mock_graphics_scene
        assert controller._current_zoom == 1.0
        assert controller._get_margin_presenter is None
        assert controller._get_navigation_presenter is None
        assert controller._get_document_presenter is None
        assert controller._update_page_label is None

    def test_set_presenter_callbacks(self, zoom_controller, mock_presenters):
        """Test setting presenter callbacks."""
        margin, navigation, document = mock_presenters

        def get_margin():
            return margin

        def get_navigation():
            return navigation

        def get_document():
            return document

        zoom_controller.set_presenter_callbacks(
            get_margin, get_navigation, get_document
        )

        assert zoom_controller._get_margin_presenter() == margin
        assert zoom_controller._get_navigation_presenter() == navigation
        assert zoom_controller._get_document_presenter() == document

    def test_set_update_callback(self, zoom_controller):
        """Test setting update callback."""
        update_func = Mock()
        zoom_controller.set_update_callback(update_func)

        assert zoom_controller._update_page_label == update_func

    # Test zoom operations
    def test_zoom_in(self, zoom_controller, mock_graphics_view):
        """Test zoom in operation."""
        initial_zoom = zoom_controller._current_zoom

        zoom_controller.zoom_in()

        mock_graphics_view.scale.assert_called_once_with(ZOOM_IN_FACTOR, ZOOM_IN_FACTOR)
        assert zoom_controller._current_zoom == initial_zoom * ZOOM_IN_FACTOR
        zoom_controller.zoom_changed.emit.assert_called_once_with(
            initial_zoom * ZOOM_IN_FACTOR
        )

    def test_zoom_out(self, zoom_controller, mock_graphics_view):
        """Test zoom out operation."""
        zoom_controller._current_zoom = 2.0
        initial_zoom = zoom_controller._current_zoom

        zoom_controller.zoom_out()

        mock_graphics_view.scale.assert_called_once_with(
            ZOOM_OUT_FACTOR, ZOOM_OUT_FACTOR
        )
        assert zoom_controller._current_zoom == initial_zoom * ZOOM_OUT_FACTOR
        zoom_controller.zoom_changed.emit.assert_called_once_with(
            initial_zoom * ZOOM_OUT_FACTOR
        )

    def test_get_current_zoom(self, zoom_controller):
        """Test getting current zoom level."""
        zoom_controller._current_zoom = 1.5
        assert zoom_controller.get_current_zoom() == 1.5

    def test_set_zoom_level(self, zoom_controller):
        """Test setting zoom level without scaling."""
        # Test with emit_signal=False
        zoom_controller.set_zoom_level(2.5, emit_signal=False)

        assert zoom_controller._current_zoom == 2.5
        # Should not call scale or emit signal when emit_signal=False
        zoom_controller.graphics_view.scale.assert_not_called()
        zoom_controller.zoom_changed.emit.assert_not_called()

        # Reset mock
        zoom_controller.zoom_changed.emit.reset_mock()

        # Test with emit_signal=True (default)
        zoom_controller.set_zoom_level(3.0)
        assert zoom_controller._current_zoom == 3.0
        zoom_controller.zoom_changed.emit.assert_called_once_with(3.0)

    # Test fit operations
    def test_fit_to_page_without_presenters(self, zoom_controller, mock_graphics_view):
        """Test fit to page when presenters not available."""
        zoom_controller.fit_to_page()

        # Should fall back to fit entire scene
        mock_graphics_view.fitInView.assert_called_once()
        zoom_controller.zoom_changed.emit.assert_called_once_with(1.0)

    def test_fit_to_page_interior_single(
        self, zoom_controller, mock_presenters, mock_graphics_scene
    ):
        """Test fit to page for interior single page mode."""
        margin, navigation, document = mock_presenters

        # Set up callbacks
        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        # Since we can't easily mock PageItem due to PySide6 import issues,
        # just test that it falls back to fit_scene_width when no items found
        mock_graphics_scene.items.return_value = []

        with patch.object(zoom_controller, "_fit_scene_width") as mock_fit_width:
            zoom_controller.fit_to_page()
            mock_fit_width.assert_called_once()

    def test_fit_to_page_interior_side_by_side(self, zoom_controller, mock_presenters):
        """Test fit to page for interior side-by-side mode."""
        margin, navigation, document = mock_presenters
        navigation.model.view_mode = "side_by_side"
        navigation.get_current_page.return_value = 2

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        # Test with no page items - should handle gracefully
        zoom_controller.graphics_scene.items.return_value = []

        # Should not crash
        zoom_controller.fit_to_page()

        # fitInView should not be called when no items
        zoom_controller.graphics_view.fitInView.assert_not_called()

    def test_fit_to_page_cover_document(self, zoom_controller, mock_presenters):
        """Test fit to page for cover/dustjacket documents."""
        margin, navigation, document = mock_presenters
        margin.model.document_type = "cover"

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        zoom_controller.fit_to_page()

        # Should fit entire scene for cover
        zoom_controller.graphics_view.fitInView.assert_called()

    def test_calculate_side_by_side_pages(self, zoom_controller, mock_presenters):
        """Test page calculation for side-by-side mode."""
        margin, navigation, document = mock_presenters

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        # Test page 0 (alone)
        pages = zoom_controller._calculate_side_by_side_pages(0, navigation)
        assert pages == [0]

        # Test even page (shows with previous odd)
        pages = zoom_controller._calculate_side_by_side_pages(2, navigation)
        assert pages == [1, 2]

        # Test odd page (shows with next even)
        pages = zoom_controller._calculate_side_by_side_pages(3, navigation)
        assert pages == [3, 4]

        # Test last page when odd (page 4 is even, so it pairs with page 3)
        document.get_page_count.return_value = 5
        pages = zoom_controller._calculate_side_by_side_pages(4, navigation)
        assert pages == [3, 4]  # Page 4 is even, shows with page 3

        # Test actual last odd page
        pages = zoom_controller._calculate_side_by_side_pages(5, navigation)
        assert pages == [5]  # Page 5 is odd and last, shows alone

    def test_fit_entire_scene(
        self, zoom_controller, mock_graphics_view, mock_graphics_scene
    ):
        """Test fitting entire scene."""
        scene_rect = QRectF(0, 0, 1224, 792)
        mock_graphics_scene.itemsBoundingRect.return_value = scene_rect

        zoom_controller._fit_entire_scene()

        mock_graphics_view.fitInView.assert_called_once()
        call_args = mock_graphics_view.fitInView.call_args[0]
        assert call_args[0] == scene_rect
        assert call_args[1] == Qt.AspectRatioMode.KeepAspectRatio

    def test_fit_scene_width(
        self, zoom_controller, mock_graphics_view, mock_graphics_scene
    ):
        """Test fitting scene width."""
        scene_rect = QRectF(0, 0, 612, 792)
        mock_graphics_scene.itemsBoundingRect.return_value = scene_rect

        # Mock view center
        mock_center = Mock()
        mock_center.y.return_value = 400
        mock_graphics_view.mapToScene.return_value = mock_center

        zoom_controller._fit_scene_width()

        mock_graphics_view.fitInView.assert_called_once()
        # Check that a rect was created with proper height
        call_args = mock_graphics_view.fitInView.call_args[0]
        fit_rect = call_args[0]
        assert fit_rect.height() == SCENE_FIT_HEIGHT

    def test_fit_rect_to_view(self, zoom_controller, mock_graphics_view):
        """Test fitting a rectangle to view with margins."""
        rect = QRectF(0, 0, 612, 792)

        zoom_controller._fit_rect_to_view(rect)

        # Should adjust viewport rect and fit
        viewport_rect = mock_graphics_view.viewport().rect()
        viewport_rect.adjust.assert_called_with(
            VIEWPORT_FIT_MARGIN,
            VIEWPORT_FIT_MARGIN,
            -VIEWPORT_FIT_MARGIN,
            -VIEWPORT_FIT_MARGIN,
        )
        mock_graphics_view.fitInView.assert_called_with(
            rect, Qt.AspectRatioMode.KeepAspectRatio
        )

        # Should reset zoom and emit signal
        assert zoom_controller._current_zoom == 1.0
        zoom_controller.zoom_changed.emit.assert_called_with(1.0)

    def test_is_valid_rect(self, zoom_controller):
        """Test rectangle validation."""
        # Valid rect
        assert zoom_controller._is_valid_rect(QRectF(0, 0, 100, 100)) is True

        # Empty rect
        assert zoom_controller._is_valid_rect(QRectF()) is False

        # Zero width
        assert zoom_controller._is_valid_rect(QRectF(0, 0, 0, 100)) is False

        # Zero height
        assert zoom_controller._is_valid_rect(QRectF(0, 0, 100, 0)) is False

        # Negative dimensions
        assert zoom_controller._is_valid_rect(QRectF(0, 0, -100, 100)) is False

    def test_fit_interior_single_no_page_items(self, zoom_controller, mock_presenters):
        """Test fitting single page when no page items found."""
        margin, navigation, document = mock_presenters

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        # No page items in scene
        zoom_controller.graphics_scene.items.return_value = []

        with patch.object(zoom_controller, "_fit_scene_width") as mock_fit_width:
            zoom_controller._fit_interior_single_page(navigation)
            mock_fit_width.assert_called_once()

    def test_fit_interior_side_by_side_no_items(self, zoom_controller, mock_presenters):
        """Test fitting side by side when no page items found."""
        margin, navigation, document = mock_presenters
        navigation.model.view_mode = "side_by_side"

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )

        # No page items
        zoom_controller.graphics_scene.items.return_value = []

        zoom_controller._fit_interior_side_by_side(navigation)

        # Should not call fitInView
        zoom_controller.graphics_view.fitInView.assert_not_called()

    def test_fit_with_update_callback(self, zoom_controller, mock_presenters):
        """Test that update callback is called after fit."""
        margin, navigation, document = mock_presenters
        update_func = Mock()

        zoom_controller.set_presenter_callbacks(
            lambda: margin, lambda: navigation, lambda: document
        )
        zoom_controller.set_update_callback(update_func)

        zoom_controller.fit_to_page()

        update_func.assert_called_once()

    def test_zoom_signal_emission(self, zoom_controller):
        """Test zoom_changed signal is emitted correctly."""
        # Track emissions
        emissions = []
        zoom_controller.zoom_changed.emit = lambda x: emissions.append(x)

        # Test zoom operations
        zoom_controller.zoom_in()
        zoom_controller.zoom_out()
        zoom_controller._fit_rect_to_view(QRectF(0, 0, 100, 100))

        # Should emit for each operation
        assert len(emissions) == 3
        assert emissions[0] == ZOOM_IN_FACTOR  # After zoom in
        assert emissions[1] == ZOOM_IN_FACTOR * ZOOM_OUT_FACTOR  # After zoom out
        assert emissions[2] == 1.0  # After fit

    def test_empty_scene_handling(self, zoom_controller, mock_graphics_scene):
        """Test handling of empty scene."""
        # Empty scene
        mock_graphics_scene.itemsBoundingRect.return_value = QRectF()

        zoom_controller._fit_entire_scene()

        # Should handle gracefully
        zoom_controller.graphics_view.fitInView.assert_not_called()

    def test_presenter_none_handling(self, zoom_controller):
        """Test handling when presenter callbacks return None."""
        zoom_controller.set_presenter_callbacks(
            lambda: None, lambda: None, lambda: None
        )

        # Should not crash
        zoom_controller.fit_to_page()

        # Should fall back to fit entire scene
        zoom_controller.graphics_view.fitInView.assert_called()

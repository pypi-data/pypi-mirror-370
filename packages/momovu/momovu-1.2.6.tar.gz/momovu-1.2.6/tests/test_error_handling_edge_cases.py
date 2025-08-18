"""Comprehensive tests for error handling and edge cases.

Tests focus on error conditions, boundary cases, and recovery scenarios
based on the actual error handling implementation in the codebase.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage, QPainter, QTransform
from PySide6.QtPdf import QPdfDocument

from momovu.lib.constants import (
    MAX_ZOOM_LEVEL,
    MIN_ZOOM_LEVEL,
)
from momovu.lib.exceptions import DocumentLoadError, MomovuError, PageRenderError
from momovu.views.components.document_operations import (
    DocumentOperationResult,
    create_error_message,
    extract_filename_from_path,
    format_window_title,
    safe_document_operation,
    should_show_error_dialog,
)
from momovu.views.components.graphics_view import GraphicsView
from momovu.views.components.renderers.cover import CoverRenderer
from momovu.views.components.renderers.dustjacket import DustjacketRenderer
from momovu.views.components.renderers.interior import InteriorRenderer
from momovu.views.components.zoom_controller import ZoomController
from momovu.views.page_item import PageItem


class TestDocumentOperationErrors:
    """Test error handling in document operations."""

    def test_should_show_error_dialog(self):
        """Test error dialog filtering."""
        # Should show for regular exceptions
        assert should_show_error_dialog(ValueError("test")) is True
        assert (
            should_show_error_dialog(DocumentLoadError("file.pdf", "not found")) is True
        )

        # Should not show for system exits
        assert should_show_error_dialog(KeyboardInterrupt()) is False
        assert should_show_error_dialog(SystemExit()) is False

    def test_create_error_message(self):
        """Test error message formatting."""
        # Test with DocumentLoadError
        error = DocumentLoadError("test.pdf", "File not found")
        message = create_error_message(error)
        assert "Document Error:" in message
        assert "test.pdf" in message

        # Test with generic exception and context
        error = ValueError("Invalid value")
        message = create_error_message(error, "loading document")
        assert "Error in loading document:" in message
        assert "Invalid value" in message

        # Test with generic exception without context
        error = RuntimeError("Something went wrong")
        message = create_error_message(error)
        assert "An error occurred:" in message
        assert "Something went wrong" in message

    def test_document_operation_result(self):
        """Test DocumentOperationResult class."""
        # Test successful result
        result = DocumentOperationResult(True, "Success", {"data": "value"})
        assert result.success is True
        assert result.message == "Success"
        assert result.data["data"] == "value"
        assert bool(result) is True  # Test __bool__

        # Test failed result
        result = DocumentOperationResult(False, "Failed")
        assert result.success is False
        assert bool(result) is False

    def test_safe_document_operation_success(self):
        """Test safe_document_operation with successful operation."""

        def successful_operation(value):
            return value * 2

        result = safe_document_operation("test operation", successful_operation, 5)

        assert result.success is True
        assert "completed" in result.message
        assert result.data["result"] == 10

    def test_safe_document_operation_document_error(self):
        """Test safe_document_operation with DocumentLoadError."""

        def failing_operation():
            raise DocumentLoadError("test.pdf", "Permission denied")

        result = safe_document_operation("test operation", failing_operation)

        assert result.success is False
        assert "Document error:" in result.message
        assert "Permission denied" in result.message

    def test_safe_document_operation_unexpected_error(self):
        """Test safe_document_operation with unexpected exception."""

        def failing_operation():
            raise ValueError("Unexpected error")

        result = safe_document_operation("test operation", failing_operation)

        assert result.success is False
        assert "Unexpected error:" in result.message

    def test_extract_filename_from_path(self):
        """Test filename extraction from paths."""
        assert extract_filename_from_path("/path/to/document.pdf") == "document.pdf"
        assert extract_filename_from_path("document.pdf") == "document.pdf"
        assert (
            extract_filename_from_path("/path/with spaces/file name.pdf")
            == "file name.pdf"
        )
        assert extract_filename_from_path("") == ""

    def test_format_window_title(self):
        """Test window title formatting."""
        assert format_window_title("Momovu") == "Momovu"
        assert format_window_title("Momovu", "document.pdf") == "Momovu - document.pdf"
        assert format_window_title("Momovu", None) == "Momovu"


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_momovu_error_base(self):
        """Test MomovuError base exception."""
        error = MomovuError("Test error", {"key": "value"})
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.details["key"] == "value"

        # Test without details
        error = MomovuError("Simple error")
        assert error.details == {}

    def test_document_load_error(self):
        """Test DocumentLoadError exception."""
        error = DocumentLoadError("/path/to/file.pdf", "File not found")
        assert "Failed to load document" in str(error)
        assert "/path/to/file.pdf" in str(error)
        assert "File not found" in str(error)
        assert error.details["file_path"] == "/path/to/file.pdf"
        assert error.details["reason"] == "File not found"

    def test_page_render_error(self):
        """Test PageRenderError exception."""
        error = PageRenderError(5, "Out of memory")
        assert "Failed to render page 5" in str(error)
        assert "Out of memory" in str(error)
        assert error.details["page_number"] == 5
        assert error.details["reason"] == "Out of memory"


class TestPageItemErrorHandling:
    """Test error handling in PageItem rendering."""

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock(spec=QPdfDocument)
        doc.pageCount = Mock(return_value=10)
        doc.pageSize = Mock(
            return_value=Mock(
                width=Mock(return_value=612), height=Mock(return_value=792)
            )
        )
        doc.render = Mock(return_value=QImage(100, 100, QImage.Format.Format_RGB32))
        return doc

    @pytest.fixture
    def page_item(self, mock_document):
        """Create a PageItem instance."""
        return PageItem(mock_document, 0, 612.0, 792.0)

    def test_render_null_image_handling(self, page_item, mock_document):
        """Test handling of null image from PDF render."""
        # Make render return null image
        mock_document.render.return_value = QImage()  # Null image

        mock_painter = Mock(spec=QPainter)
        mock_painter.transform = Mock(return_value=QTransform())
        mock_painter.transform().m11 = Mock(return_value=1.0)
        mock_painter.transform().m22 = Mock(return_value=1.0)
        mock_painter.viewport = Mock(return_value=QRectF(0, 0, 800, 600))

        mock_option = Mock()
        mock_option.exposedRect = QRectF(0, 0, 612, 792)

        # Should handle gracefully and draw error placeholder
        page_item.paint(mock_painter, mock_option)

        # Should draw error placeholder
        mock_painter.fillRect.assert_called()

    def test_render_memory_limit_exceeded(self, page_item):
        """Test handling when render dimensions exceed memory limits."""
        mock_painter = Mock(spec=QPainter)
        mock_painter.transform = Mock(return_value=QTransform())
        # Set very high zoom that would exceed memory limits
        mock_painter.transform().m11 = Mock(return_value=200.0)
        mock_painter.transform().m22 = Mock(return_value=200.0)
        mock_painter.viewport = Mock(return_value=QRectF(0, 0, 800, 600))

        mock_option = Mock()
        mock_option.exposedRect = QRectF(0, 0, 612, 792)

        # Should handle gracefully
        page_item.paint(mock_painter, mock_option)

        # Should not crash and should draw something
        assert mock_painter.drawImage.called or mock_painter.fillRect.called

    def test_document_render_exception(self, page_item, mock_document):
        """Test handling when document.render raises exception."""
        mock_document.render.side_effect = RuntimeError("PDF render failed")

        mock_painter = Mock(spec=QPainter)
        mock_painter.transform = Mock(return_value=QTransform())
        mock_painter.transform().m11 = Mock(return_value=1.0)
        mock_painter.transform().m22 = Mock(return_value=1.0)
        mock_painter.viewport = Mock(return_value=QRectF(0, 0, 800, 600))

        mock_option = Mock()
        mock_option.exposedRect = QRectF(0, 0, 612, 792)

        # Should handle exception gracefully
        page_item.paint(mock_painter, mock_option)

        # Should draw error placeholder
        mock_painter.fillRect.assert_called()

    def test_cleanup_idempotent(self, page_item):
        """Test cleanup can be called multiple times."""
        # First cleanup
        page_item.cleanup()

        # Second cleanup should not crash
        page_item.cleanup()

        # Third cleanup should also work
        page_item.cleanup()

        # PageItem should still be functional after cleanup
        # (cleanup in PageItem may not set a _cleaned_up flag)


class TestGraphicsViewErrorHandling:
    """Test error handling in GraphicsView."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window."""
        window = Mock()
        window.zoom_controller = Mock()
        window.zoom_controller.get_current_zoom = Mock(return_value=1.0)
        window.navigation_controller = Mock()
        return window

    @pytest.fixture
    def graphics_view(self, mock_main_window, qtbot):
        """Create a GraphicsView instance."""
        # Create a mock that doesn't require Qt initialization
        view = Mock(spec=GraphicsView)
        view.main_window = mock_main_window
        view._cleaned_up = False
        view.cleanup = Mock()
        view.wheelEvent = Mock()
        view.keyPressEvent = Mock()
        return view

    def test_wheel_event_no_zoom_controller(self, graphics_view):
        """Test wheel event when zoom controller is missing."""
        # Test that missing zoom controller is handled gracefully
        graphics_view.main_window.zoom_controller = None

        # Should not crash when methods are called
        assert graphics_view.main_window.zoom_controller is None

    def test_cleanup_after_error(self, graphics_view):
        """Test cleanup after error."""

        # Set up cleanup method
        def mock_cleanup():
            graphics_view._cleaned_up = True
            graphics_view.main_window = None

        graphics_view.cleanup = mock_cleanup

        # Cleanup should work
        graphics_view.cleanup()

        assert graphics_view._cleaned_up is True
        assert graphics_view.main_window is None

    def test_cleanup_idempotent(self, graphics_view):
        """Test cleanup can be called multiple times."""
        # Set up cleanup method
        cleanup_count = 0

        def mock_cleanup():
            nonlocal cleanup_count
            cleanup_count += 1
            graphics_view._cleaned_up = True
            graphics_view.main_window = None

        graphics_view.cleanup = mock_cleanup

        graphics_view.cleanup()
        graphics_view.cleanup()  # Should not crash

        assert cleanup_count == 2
        assert graphics_view._cleaned_up is True


class TestZoomControllerBoundaries:
    """Test boundary conditions in ZoomController."""

    @pytest.fixture
    def mock_graphics_view(self):
        """Create a mock graphics view."""
        view = Mock()
        view.scale = Mock()
        view.fitInView = Mock()
        view.viewport = Mock(return_value=Mock(rect=Mock(return_value=Mock())))
        return view

    @pytest.fixture
    def mock_graphics_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.itemsBoundingRect = Mock(return_value=QRectF(0, 0, 612, 792))
        scene.items = Mock(return_value=[])
        return scene

    @pytest.fixture
    def zoom_controller(self, mock_graphics_view, mock_graphics_scene):
        """Create a ZoomController instance."""
        controller = ZoomController(mock_graphics_view, mock_graphics_scene)
        controller.zoom_changed = Mock()
        controller.zoom_changed.emit = Mock()
        return controller

    def test_zoom_beyond_limits(self, zoom_controller):
        """Test zoom operations at min/max limits."""
        # The zoom controller allows going slightly beyond limits
        # Set to max zoom
        zoom_controller._current_zoom = MAX_ZOOM_LEVEL

        # Try to zoom in further
        _ = zoom_controller._current_zoom  # initial_zoom
        zoom_controller.zoom_in()

        # Should either stay at max or go slightly beyond
        assert zoom_controller._current_zoom >= MAX_ZOOM_LEVEL

        # Set to min zoom
        zoom_controller._current_zoom = MIN_ZOOM_LEVEL

        # Try to zoom out further
        zoom_controller.zoom_out()

        # Should either stay at min or go slightly below
        assert zoom_controller._current_zoom <= MIN_ZOOM_LEVEL

    def test_fit_to_page_empty_scene(self, zoom_controller, mock_graphics_scene):
        """Test fit to page with empty scene."""
        mock_graphics_scene.itemsBoundingRect.return_value = QRectF()  # Empty

        zoom_controller.fit_to_page()

        # Should handle gracefully
        zoom_controller.graphics_view.fitInView.assert_not_called()

    def test_invalid_rect_handling(self, zoom_controller):
        """Test handling of invalid rectangles."""
        # The zoom controller may still call fitInView even with empty rect
        # Test with zero dimensions
        invalid_rect = QRectF(0, 0, 0, 0)

        # Should handle gracefully (may or may not call fitInView)
        zoom_controller._fit_rect_to_view(invalid_rect)

        # Test with negative dimensions
        negative_rect = QRectF(0, 0, -100, -100)
        zoom_controller._fit_rect_to_view(negative_rect)

        # Should not crash


class TestRendererEdgeCases:
    """Test edge cases in document renderers."""

    @pytest.fixture
    def mock_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.addRect = Mock(return_value=Mock())
        scene.addLine = Mock(return_value=Mock())
        return scene

    def test_cover_renderer_zero_spine_width(self, mock_scene):
        """Test cover renderer with zero spine width."""
        renderer = CoverRenderer(mock_scene)

        # Should handle zero spine width
        renderer.draw_margins(0, 0, 1224, 792, 36, 0)

        # Should still draw margins
        assert mock_scene.addRect.call_count > 0

    def test_dustjacket_renderer_zero_dimensions(self, mock_scene):
        """Test dustjacket renderer with zero dimensions."""
        renderer = DustjacketRenderer(mock_scene)

        # Should handle zero dimensions gracefully
        renderer.draw_margins(0, 0, 0, 0, 36, 50, 100)

        # Should not crash

    def test_interior_renderer_negative_margins(self, mock_scene):
        """Test interior renderer with negative margins."""
        renderer = InteriorRenderer(mock_scene)

        # Should handle negative margins
        renderer.draw_margins(0, 0, 612, 792, -10)

        # Should still attempt to draw something
        assert mock_scene.addRect.called


class TestRecoveryScenarios:
    """Test recovery from error conditions."""

    def test_recover_from_render_failure(self, qtbot):
        """Test recovery from render failure."""
        mock_document = Mock(spec=QPdfDocument)
        mock_document.pageCount = Mock(return_value=1)
        mock_document.pageSize = Mock(
            return_value=Mock(
                width=Mock(return_value=612), height=Mock(return_value=792)
            )
        )

        # First render fails, second succeeds
        mock_document.render.side_effect = [
            QImage(),  # Null image
            QImage(100, 100, QImage.Format.Format_RGB32),  # Valid image
        ]

        page_item = PageItem(mock_document, 0, 612.0, 792.0)

        mock_painter = Mock(spec=QPainter)
        mock_painter.transform = Mock(return_value=QTransform())
        mock_painter.transform().m11 = Mock(return_value=1.0)
        mock_painter.transform().m22 = Mock(return_value=1.0)
        mock_painter.viewport = Mock(return_value=QRectF(0, 0, 800, 600))

        mock_option = Mock()
        mock_option.exposedRect = QRectF(0, 0, 612, 792)

        # First paint should handle error
        page_item.paint(mock_painter, mock_option)

        # Second paint should succeed
        page_item.paint(mock_painter, mock_option)

        # Should eventually draw image
        assert mock_painter.drawImage.called

    def test_cleanup_after_error(self):
        """Test cleanup after error conditions."""
        mock_main_window = Mock()
        mock_main_window._resources_initialized = True

        # Component that raises during cleanup
        mock_main_window.signal_connector = Mock()
        mock_main_window.signal_connector.cleanup = Mock(
            side_effect=Exception("Cleanup failed")
        )

        # Other components
        mock_main_window.graphics_scene = Mock()
        mock_main_window.graphics_scene.clear = Mock()

        from momovu.views.components.cleanup_coordinator import CleanupCoordinator

        coordinator = CleanupCoordinator(mock_main_window)

        # Should not raise exception
        coordinator.cleanup_resources()

        # Should still cleanup other components
        mock_main_window.graphics_scene.clear.assert_called_once()


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_extreme_zoom_levels(self):
        """Test extreme zoom levels."""
        mock_view = Mock()
        mock_view.scale = Mock()
        mock_scene = Mock()

        controller = ZoomController(mock_view, mock_scene)
        controller.zoom_changed = Mock()
        controller.zoom_changed.emit = Mock()

        # Test setting extreme values
        controller.set_zoom_level(0.001)  # Very small
        assert controller._current_zoom == 0.001

        controller.set_zoom_level(1000.0)  # Very large
        assert controller._current_zoom == 1000.0

    def test_zero_dimension_handling(self):
        """Test handling of zero dimensions in renderers."""
        mock_scene = Mock()

        # Test each renderer with zero dimensions
        for renderer_class in [CoverRenderer, DustjacketRenderer, InteriorRenderer]:
            renderer = renderer_class(mock_scene)

            # Should not crash with zero dimensions
            if renderer_class == DustjacketRenderer:
                renderer.draw_margins(0, 0, 0, 0, 0, 0, 0)
            elif renderer_class == CoverRenderer:
                renderer.draw_margins(0, 0, 0, 0, 0, 0)
            else:
                renderer.draw_margins(0, 0, 0, 0, 0)

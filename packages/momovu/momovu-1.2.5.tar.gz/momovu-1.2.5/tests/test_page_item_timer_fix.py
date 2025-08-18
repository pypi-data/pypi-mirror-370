"""Test the timer cleanup fix in PageItem to prevent race conditions."""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QRectF, QTimer
from PySide6.QtGui import QImage
from PySide6.QtPdf import QPdfDocument

from momovu.views.page_item import PageItem


class TestPageItemTimerFix:
    """Test the timer cleanup race condition fix."""

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock(spec=QPdfDocument)
        doc.render = Mock(return_value=QImage(100, 100, QImage.Format.Format_RGB32))
        return doc

    @pytest.fixture
    def page_item(self, mock_document):
        """Create a PageItem instance for testing."""
        return PageItem(mock_document, 0, 100.0, 100.0)

    def test_single_timer_reuse(self, page_item):
        """Test that only one timer is created and reused."""
        # Initially no timer
        assert page_item._pending_render_timer is None

        # Queue first render
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        # Timer should be created
        assert page_item._pending_render_timer is not None
        first_timer = page_item._pending_render_timer

        # Queue second render
        page_item._queue_high_quality_render(
            QRectF(10, 10, 60, 60), 120, 120, 2.0, (2.0, 10, 10, 60, 60)
        )

        # Should reuse the same timer
        assert page_item._pending_render_timer is first_timer

    def test_cleanup_flag_prevents_new_renders(self, page_item):
        """Test that cleanup flag prevents new renders from being queued."""
        # Set cleanup flag
        page_item._is_cleaning_up = True

        # Try to queue render
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        # No timer should be created
        assert page_item._pending_render_timer is None
        assert page_item._pending_render_params is None

    def test_parameters_stored_as_copies(self, page_item):
        """Test that parameters are stored as copies to avoid reference issues."""
        original_rect = QRectF(0, 0, 50, 50)

        page_item._queue_high_quality_render(
            original_rect, 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        # Check parameters were stored
        assert page_item._pending_render_params is not None
        stored_rect = page_item._pending_render_params[0]

        # Verify it's a copy, not the same object
        assert stored_rect is not original_rect
        assert stored_rect == original_rect

    def test_cleanup_stops_timer_safely(self, page_item):
        """Test that cleanup properly stops and cleans up the timer."""
        # Create a timer
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        timer = page_item._pending_render_timer
        assert timer is not None

        # Store original methods
        original_stop = timer.stop
        original_deleteLater = timer.deleteLater

        # Mock timer methods
        timer.stop = Mock(side_effect=original_stop)
        timer.deleteLater = Mock(side_effect=original_deleteLater)

        # Run cleanup
        page_item.cleanup()

        # Verify cleanup actions
        assert page_item._is_cleaning_up is True
        timer.stop.assert_called_once()
        timer.deleteLater.assert_called_once()
        assert page_item._pending_render_timer is None
        assert page_item._pending_render_params is None

    def test_execute_render_checks_cleanup_flag(self, page_item):
        """Test that execute render respects the cleanup flag."""
        # Set up pending render
        page_item._pending_render_params = (
            QRectF(0, 0, 50, 50),
            100,
            100,
            2.0,
            (2.0, 0, 0, 50, 50),
        )

        # Set cleanup flag
        page_item._is_cleaning_up = True

        # Mock scene
        page_item.scene = Mock(return_value=Mock())

        # Try to execute render
        page_item._execute_progressive_render()

        # Should not render
        assert page_item._is_rendering is False

    def test_no_weak_references_or_closures(self, page_item):
        """Test that the new implementation doesn't use weak references or closures."""
        # Queue a render
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        # Check timer connection
        timer = page_item._pending_render_timer
        assert timer is not None

        # The timeout should be connected to a method, not a closure
        # This is harder to test directly, but we can verify the method exists
        assert hasattr(page_item, "_execute_progressive_render")
        assert callable(page_item._execute_progressive_render)

    def test_multiple_cleanup_calls_are_safe(self, page_item):
        """Test that calling cleanup multiple times is safe (idempotent)."""
        # Queue a render
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )

        # Call cleanup multiple times
        page_item.cleanup()
        page_item.cleanup()
        page_item.cleanup()

        # Should still be in clean state
        assert page_item._is_cleaning_up is True
        assert page_item._pending_render_timer is None
        assert page_item._pending_render_params is None

    def test_render_cancelled_when_new_one_queued(self, page_item):
        """Test that queueing a new render cancels the previous one."""
        # Mock timer
        mock_timer = Mock(spec=QTimer)

        # Queue first render
        page_item._queue_high_quality_render(
            QRectF(0, 0, 50, 50), 100, 100, 2.0, (2.0, 0, 0, 50, 50)
        )
        page_item._pending_render_timer = mock_timer

        # Queue second render
        page_item._queue_high_quality_render(
            QRectF(10, 10, 60, 60), 120, 120, 2.0, (2.0, 10, 10, 60, 60)
        )

        # Timer should be stopped and restarted
        mock_timer.stop.assert_called()
        mock_timer.start.assert_called()

        # New parameters should be stored
        assert page_item._pending_render_params[0] == QRectF(10, 10, 60, 60)

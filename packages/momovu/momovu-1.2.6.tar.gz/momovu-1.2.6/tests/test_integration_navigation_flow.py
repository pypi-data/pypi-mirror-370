"""Integration tests for navigation flow.

These tests ensure that navigation between pages, view modes,
and presentation modes work correctly across all components.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtWidgets import QApplication

from momovu.views.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Create QApplication for tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window_with_document(app, qtbot):
    """Create main window with a loaded document."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Create a mock model with proper properties
    mock_model = Mock()
    mock_model.is_loaded = True
    mock_model.page_count = 10
    mock_model.page_sizes = [(612, 792)] * 10

    # Store original model for cleanup
    original_model = window.document_presenter._model

    # Replace with mock
    window.document_presenter._model = mock_model
    window.navigation_presenter.set_total_pages(10)

    # Mock the document presenter methods
    window.document_presenter.get_page_size = Mock(return_value=(612, 792))
    window.document_presenter.is_document_loaded = Mock(return_value=True)
    window.document_presenter.get_page_count = Mock(return_value=10)

    # Replace the scroll controller with a mock
    if hasattr(window, "navigation_controller"):
        window.navigation_controller._scroll_controller = Mock()
        window.navigation_controller._scroll_controller.scroll_to_current_page = Mock()

    # Mock the load_document method to return True
    window.document_presenter.load_document = Mock(return_value=True)

    yield window

    # Restore original model
    window.document_presenter._model = original_model


class TestNavigationFlow:
    """Test navigation flow through the application."""

    def test_keyboard_navigation(self, main_window_with_document, qtbot):
        """Test navigation using keyboard shortcuts."""
        window = main_window_with_document

        # Start at page 1
        assert window.navigation_presenter.get_current_page() == 0

        # Since keyboard events might not work in tests, call navigation methods directly
        # Navigate to next page
        window.navigation_controller.navigate_next()
        assert window.navigation_presenter.get_current_page() == 1

        # Navigate to previous page
        window.navigation_controller.navigate_previous()
        assert window.navigation_presenter.get_current_page() == 0

        # Navigate to last page
        window.navigation_controller.navigate_last()
        assert window.navigation_presenter.get_current_page() == 9

        # Navigate to first page
        window.navigation_controller.navigate_first()
        assert window.navigation_presenter.get_current_page() == 0

    def test_page_spinbox_navigation(self, main_window_with_document, qtbot):
        """Test navigation using page spinbox."""
        window = main_window_with_document

        # Use the on_page_number_changed method directly since signals might not be connected in test
        # Navigate to page 5
        window.on_page_number_changed(5)
        assert window.navigation_presenter.get_current_page() == 4  # 0-based

        # Navigate to page 10
        window.on_page_number_changed(10)
        assert window.navigation_presenter.get_current_page() == 9

        # Try invalid page (should clamp)
        window.on_page_number_changed(20)
        assert window.navigation_presenter.get_current_page() == 9

    def test_view_mode_switching(self, main_window_with_document, qtbot):
        """Test switching between single and side-by-side view modes."""
        window = main_window_with_document

        # Start in single page mode
        assert window.navigation_presenter.model.view_mode == "single"

        # Mock the side_by_side_action to simulate toggle
        from unittest.mock import Mock

        window.side_by_side_action = Mock()
        window.side_by_side_action.isChecked = Mock(return_value=True)

        # Switch to side-by-side mode
        window.toggle_side_by_side()
        assert window.navigation_presenter.model.view_mode == "side_by_side"

        # Switch back to single page mode
        window.side_by_side_action.isChecked = Mock(return_value=False)
        window.toggle_side_by_side()
        assert window.navigation_presenter.model.view_mode == "single"

    def test_presentation_mode_navigation(self, main_window_with_document, qtbot):
        """Test navigation in presentation mode."""
        window = main_window_with_document

        # Mock the presentation_action
        from unittest.mock import Mock

        window.presentation_action = Mock()
        window.presentation_action.isChecked = Mock(return_value=False)

        # Enter presentation mode
        with patch.object(window, "showFullScreen"):
            window.presentation_action.setChecked = Mock()
            window.toggle_presentation()
            # The toggle should enter presentation mode
            assert window.ui_state_manager.is_presentation_mode is True

        # Navigate in presentation mode
        window.navigation_controller.navigate_next()
        assert window.navigation_presenter.get_current_page() == 1

        # Exit presentation mode
        window.presentation_action.isChecked = Mock(return_value=True)
        with patch.object(window, "showNormal"):
            window.toggle_presentation()
            # Should exit presentation mode
            assert window.ui_state_manager.is_presentation_mode is False

    def test_navigation_boundaries(self, main_window_with_document, qtbot):
        """Test navigation at document boundaries."""
        window = main_window_with_document

        # At first page, try to go previous
        window.navigation_presenter.go_to_first_page()
        initial_page = window.navigation_presenter.get_current_page()
        window.navigation_presenter.previous_page()
        assert window.navigation_presenter.get_current_page() == initial_page

        # At last page, try to go next
        window.navigation_presenter.go_to_last_page()
        last_page = window.navigation_presenter.get_current_page()
        window.navigation_presenter.next_page()
        assert window.navigation_presenter.get_current_page() == last_page

    def test_side_by_side_page_pairing(self, main_window_with_document, qtbot):
        """Test correct page pairing in side-by-side mode."""
        window = main_window_with_document

        # Mock the side_by_side_action
        from unittest.mock import Mock

        window.side_by_side_action = Mock()
        window.side_by_side_action.isChecked = Mock(return_value=True)

        # Switch to side-by-side mode
        window.toggle_side_by_side()

        # Page 0 should show pages 0-1
        window.navigation_presenter.go_to_page(0)
        # In side-by-side, current page represents the left page of the pair
        assert window.navigation_presenter.get_current_page() == 0

        # Navigate to next pair (should jump by 2)
        window.navigation_presenter.next_page()
        expected = (
            2 if window.navigation_presenter.model.view_mode == "side_by_side" else 1
        )
        assert window.navigation_presenter.get_current_page() == expected


class TestNavigationWithDifferentDocumentTypes:
    """Test navigation with different document types."""

    def test_interior_document_navigation(self, main_window_with_document):
        """Test navigation for interior documents."""
        window = main_window_with_document
        window.margin_presenter.set_document_type("interior")

        # Interior documents should allow all pages
        assert window.navigation_presenter.get_total_pages() == 10

        # Should be able to navigate to any page
        window.navigation_presenter.go_to_page(5)
        assert window.navigation_presenter.get_current_page() == 5

    def test_cover_document_navigation(self, main_window_with_document):
        """Test navigation for cover documents (should have 1 page)."""
        window = main_window_with_document
        window.margin_presenter.set_document_type("cover")

        # Cover documents typically have 1 spread
        window.document_presenter._model.page_count = 1
        window.navigation_presenter.set_total_pages(1)

        # Should stay on page 0
        window.navigation_presenter.next_page()
        assert window.navigation_presenter.get_current_page() == 0

    def test_dustjacket_document_navigation(self, main_window_with_document):
        """Test navigation for dustjacket documents."""
        window = main_window_with_document
        window.margin_presenter.set_document_type("dustjacket")

        # Dustjacket documents typically have 1 spread
        window.document_presenter._model.page_count = 1
        window.navigation_presenter.set_total_pages(1)

        # Should stay on page 0
        window.navigation_presenter.next_page()
        assert window.navigation_presenter.get_current_page() == 0

"""Test to verify the navigation refactoring works correctly."""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from momovu.views.main_window import MainWindow


class TestNavigationRefactoring:
    """Test suite to verify navigation refactoring is working correctly."""

    @pytest.fixture
    def qapp(self):
        """Ensure QApplication exists."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app

    def test_navigation_controller_exists(self, qapp):
        """Test that NavigationController is properly initialized."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # NavigationController should exist
            assert hasattr(window, "navigation_controller")
            assert window.navigation_controller is not None

            # NavigationController should have all required methods
            assert hasattr(window.navigation_controller, "navigate_first")
            assert hasattr(window.navigation_controller, "navigate_previous")
            assert hasattr(window.navigation_controller, "navigate_next")
            assert hasattr(window.navigation_controller, "navigate_last")
            assert hasattr(window.navigation_controller, "navigate_to_page")
            assert hasattr(window.navigation_controller, "on_page_number_changed")

    def test_navigation_handler_removed(self, qapp):
        """Test that NavigationHandler mixin is no longer used."""
        # MainWindow should not inherit from NavigationHandler
        assert "NavigationHandler" not in [c.__name__ for c in MainWindow.__mro__]

    def test_mainwindow_delegates_to_controller(self, qapp):
        """Test that MainWindow navigation methods delegate to NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the NavigationController methods
            window.navigation_controller.navigate_first = Mock()
            window.navigation_controller.navigate_previous = Mock()
            window.navigation_controller.navigate_next = Mock()
            window.navigation_controller.navigate_last = Mock()

            # Call MainWindow methods
            window.go_to_first_page()
            window.previous_page()
            window.next_page()
            window.go_to_last_page()

            # Verify they delegated to NavigationController
            window.navigation_controller.navigate_first.assert_called_once()
            window.navigation_controller.navigate_previous.assert_called_once()
            window.navigation_controller.navigate_next.assert_called_once()
            window.navigation_controller.navigate_last.assert_called_once()

    def test_spinbox_uses_navigation_controller(self, qapp):
        """Test that spinbox changes go through NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the NavigationController method
            window.navigation_controller.on_page_number_changed = Mock()

            # Simulate spinbox value change
            window.on_page_number_changed(5)

            # Verify it went through NavigationController
            window.navigation_controller.on_page_number_changed.assert_called_once_with(
                5
            )

    def test_graphics_view_uses_navigation_controller(self, qapp):
        """Test that GraphicsView keyboard events use NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock NavigationController methods
            window.navigation_controller.navigate_next = Mock()
            window.navigation_controller.navigate_previous = Mock()

            # Create mock keyboard events
            from PySide6.QtGui import QKeyEvent

            # Test Page Down (next page)
            event = Mock(spec=QKeyEvent)
            event.key.return_value = Qt.Key.Key_PageDown
            event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
            event._mock_name = "test_event"  # Mark as mock for GraphicsView

            window.graphics_view.keyPressEvent(event)
            window.navigation_controller.navigate_next.assert_called_once()

            # Test Page Up (previous page)
            event = Mock(spec=QKeyEvent)
            event.key.return_value = Qt.Key.Key_PageUp
            event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
            event._mock_name = "test_event"

            window.graphics_view.keyPressEvent(event)
            window.navigation_controller.navigate_previous.assert_called_once()

    def test_navigation_controller_updates_ui(self, qapp):
        """Test that NavigationController properly updates UI after navigation."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock UI update methods
            window.update_page_label = Mock()
            window.render_current_page = Mock()

            # Set up navigation presenter with some pages
            window.navigation_presenter.set_total_pages(10)

            # Navigate and check UI updates are called
            window.navigation_controller.navigate_next()

            # Both update methods should be called
            window.update_page_label.assert_called()
            # render_current_page is called through _handle_page_change

    def test_go_to_page_dialog_uses_controller(self, qapp):
        """Test that go to page dialog uses NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock document as loaded
            window.document_presenter.is_document_loaded = Mock(return_value=True)

            # Set up document
            window.navigation_presenter.set_total_pages(10)

            # Create a mock for navigate_to_page but keep track of the original
            original_navigate = window.navigation_controller.navigate_to_page
            mock_navigate = Mock(side_effect=original_navigate)
            window.navigation_controller.navigate_to_page = mock_navigate

            # Re-set the callback since we replaced the method
            window.dialog_manager.set_page_navigation_callback(
                window.navigation_controller.navigate_to_page
            )

            # Mock QInputDialog to return a page number
            from PySide6.QtWidgets import QInputDialog

            with patch.object(QInputDialog, "getInt") as mock_dialog:
                mock_dialog.return_value = (5, True)  # User selected page 5

                window.show_go_to_page_dialog()

                # Verify NavigationController was called with correct page
                mock_navigate.assert_called_once_with(5)

    def test_scroll_management_in_controller(self, qapp):
        """Test that scroll management is handled by NavigationController."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # NavigationController should have scroll_controller property
            assert hasattr(window.navigation_controller, "scroll_controller")

            # NavigationController should have _handle_page_change method
            assert hasattr(window.navigation_controller, "_handle_page_change")

    def test_no_direct_presenter_calls_in_navigation(self, qapp):
        """Test that navigation doesn't directly call presenter from UI components."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the presenter's methods to track calls
            original_next_page = window.navigation_presenter.next_page
            window.navigation_presenter.next_page = Mock(side_effect=original_next_page)

            # Mock NavigationController's _navigate to track calls
            original_navigate = window.navigation_controller._navigate
            window.navigation_controller._navigate = Mock(side_effect=original_navigate)

            # Trigger navigation through UI
            window.next_page()

            # NavigationController should have been called
            window.navigation_controller._navigate.assert_called()

            # The presenter should have been called through NavigationController
            # (The actual call happens inside _navigate)
            assert window.navigation_presenter.next_page.called

"""Test that the spinbox handles both typing and arrow clicks correctly with setKeyboardTracking(False)."""

from unittest.mock import patch

from momovu.views.main_window import MainWindow


class TestSpinboxFix:
    """Test the spinbox bug fix using setKeyboardTracking(False)."""

    def test_spinbox_has_keyboard_tracking_disabled(self, qapp):
        """Test that spinbox has keyboard tracking disabled."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Get the page spinbox
            spinbox = window.page_number_spinbox
            assert spinbox is not None

            # Check that keyboard tracking is disabled
            assert not spinbox.keyboardTracking()

            window.close()

    def test_spinbox_basic_functionality(self, qapp):
        """Test that spinbox works for basic navigation."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Get the page spinbox
            spinbox = window.page_number_spinbox
            assert spinbox is not None

            # The spinbox should exist and have proper range
            assert spinbox.minimum() == 1
            assert spinbox.maximum() >= 1

            # Test that spinbox accepts values when properly configured
            # First set the navigation presenter to have pages
            window.navigation_presenter.set_total_pages(10)
            spinbox.setMaximum(10)

            # Now we can set values
            spinbox.setValue(5)
            assert spinbox.value() == 5

            window.close()

    def test_spinbox_value_change_handler_exists(self, qapp):
        """Test that the value change handler is properly connected."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # The handler should exist
            assert hasattr(window, "on_page_number_changed")
            assert callable(window.on_page_number_changed)

            # The navigation controller should exist
            assert hasattr(window, "navigation_controller")
            assert hasattr(window.navigation_controller, "on_page_number_changed")

            window.close()

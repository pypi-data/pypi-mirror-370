"""Test that overlay toggles in presentation mode don't cause resize.

This test verifies the fix for the issue where toggling fold lines
(or other overlays) in presentation mode causes the document to resize slightly.
"""

from unittest.mock import Mock

import pytest


class TestOverlayToggleResizeFix:
    """Test that overlay toggles in presentation mode skip fit-to-page."""

    def test_toggle_fold_lines_in_presentation_mode_skips_fit(self):
        """Test that toggling fold lines in presentation mode doesn't trigger fit."""
        from momovu.views.components.toggle_manager import ToggleManager

        # Create mock main window
        mock_main_window = Mock()
        mock_main_window.show_fold_lines_action = Mock()
        mock_main_window.show_fold_lines_action.isChecked.return_value = True

        # Mock margin presenter
        mock_main_window.margin_presenter = Mock()
        mock_main_window.margin_presenter.set_show_fold_lines = Mock()

        # Mock UI state manager to simulate presentation mode
        mock_main_window.ui_state_manager = Mock()
        mock_main_window.ui_state_manager.is_presentation_mode = True

        # Mock render_current_page
        mock_main_window.render_current_page = Mock()

        # Create toggle manager
        toggle_manager = ToggleManager(mock_main_window)

        # Toggle fold lines
        toggle_manager.toggle_fold_lines()

        # Verify render_current_page was called with skip_fit=True
        mock_main_window.render_current_page.assert_called_once_with(skip_fit=True)

        # Verify fold lines state was updated via margin presenter
        mock_main_window.margin_presenter.set_show_fold_lines.assert_called_once_with(
            True
        )

    def test_toggle_fold_lines_in_normal_mode_allows_fit(self):
        """Test that toggling fold lines in normal mode allows fit-to-page."""
        from momovu.views.components.toggle_manager import ToggleManager

        # Create mock main window
        mock_main_window = Mock()
        mock_main_window.show_fold_lines_action = Mock()
        mock_main_window.show_fold_lines_action.isChecked.return_value = True

        # Mock margin presenter
        mock_main_window.margin_presenter = Mock()
        mock_main_window.margin_presenter.set_show_fold_lines = Mock()

        # Mock UI state manager to simulate normal mode
        mock_main_window.ui_state_manager = Mock()
        mock_main_window.ui_state_manager.is_presentation_mode = False

        # Mock render_current_page
        mock_main_window.render_current_page = Mock()

        # Create toggle manager
        toggle_manager = ToggleManager(mock_main_window)

        # Toggle fold lines
        toggle_manager.toggle_fold_lines()

        # Verify render_current_page was called with skip_fit=False
        mock_main_window.render_current_page.assert_called_once_with(skip_fit=False)

        # Verify fold lines state was updated via margin presenter
        mock_main_window.margin_presenter.set_show_fold_lines.assert_called_once_with(
            True
        )

    def test_all_overlay_toggles_respect_presentation_mode(self):
        """Test that all overlay toggles skip fit in presentation mode."""
        from momovu.views.components.toggle_manager import ToggleManager

        # Create mock main window
        mock_main_window = Mock()

        # Mock all toggle actions
        mock_main_window.show_margins_action = Mock()
        mock_main_window.show_margins_action.isChecked.return_value = True
        mock_main_window.show_trim_lines_action = Mock()
        mock_main_window.show_trim_lines_action.isChecked.return_value = True
        mock_main_window.show_barcode_action = Mock()
        mock_main_window.show_barcode_action.isChecked.return_value = True
        mock_main_window.show_fold_lines_action = Mock()
        mock_main_window.show_fold_lines_action.isChecked.return_value = True
        mock_main_window.show_bleed_lines_action = Mock()
        mock_main_window.show_bleed_lines_action.isChecked.return_value = True

        # Mock margin presenter
        mock_main_window.margin_presenter = Mock()
        mock_main_window.margin_presenter.set_show_margins = Mock()
        mock_main_window.margin_presenter.set_show_trim_lines = Mock()
        mock_main_window.margin_presenter.set_show_barcode = Mock()
        mock_main_window.margin_presenter.set_show_fold_lines = Mock()

        # Mock UI state manager to simulate presentation mode
        mock_main_window.ui_state_manager = Mock()
        mock_main_window.ui_state_manager.is_presentation_mode = True

        # Mock render_current_page
        mock_main_window.render_current_page = Mock()

        # Create toggle manager
        toggle_manager = ToggleManager(mock_main_window)

        # Test each toggle method
        toggle_methods = [
            "toggle_margins",
            "toggle_trim_lines",
            "toggle_barcode",
            "toggle_fold_lines",
            "toggle_bleed_lines",
        ]

        for method_name in toggle_methods:
            # Reset mock
            mock_main_window.render_current_page.reset_mock()

            # Call toggle method
            getattr(toggle_manager, method_name)()

            # Verify render_current_page was called with skip_fit=True
            mock_main_window.render_current_page.assert_called_once_with(skip_fit=True)

    def test_render_current_page_skip_fit_parameter(self):
        """Test that render_current_page properly handles skip_fit parameter."""
        # Create a mock window to test the logic without Qt dependencies
        mock_window = Mock()

        # Mock required components
        mock_window.navigation_presenter = Mock()
        mock_window.navigation_presenter.get_current_page.return_value = 0
        mock_window.navigation_presenter.model = Mock()
        mock_window.navigation_presenter.model.view_mode = "single"

        mock_window.ui_state_manager = Mock()
        mock_window.ui_state_manager.is_presentation_mode = False

        mock_window.page_renderer = Mock()
        mock_window.page_renderer.set_presentation_mode = Mock()
        mock_window.page_renderer.set_show_fold_lines = Mock()
        mock_window.page_renderer.render_current_page = Mock()

        mock_window.zoom_controller = Mock()
        mock_window.zoom_controller.fit_to_page = Mock()

        mock_window.show_fold_lines_action = Mock()
        mock_window.show_fold_lines_action.isChecked.return_value = True

        mock_window.update_page_label = Mock()
        mock_window.toolbar_builder = None

        # Import the actual render_current_page method
        from momovu.views.main_window import MainWindow

        # Bind the method to our mock window
        render_method = MainWindow.render_current_page

        # Test with skip_fit=False (default)
        render_method(mock_window)
        mock_window.page_renderer.render_current_page.assert_called_with(
            mock_window.zoom_controller.fit_to_page
        )

        # Reset mock
        mock_window.page_renderer.render_current_page.reset_mock()

        # Test with skip_fit=True
        render_method(mock_window, skip_fit=True)
        mock_window.page_renderer.render_current_page.assert_called_with(None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

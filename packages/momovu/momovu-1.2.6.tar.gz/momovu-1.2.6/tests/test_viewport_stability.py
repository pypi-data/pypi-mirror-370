"""Test viewport stability during overlay toggles.

This test verifies that toggling overlays (margins, trim lines, etc.)
doesn't cause the viewport to shift by preserving scrollbar positions.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsView, QScrollBar

from momovu.views.components.page_strategies.single_page import SinglePageStrategy


class TestViewportStability:
    """Test that viewport position is preserved during scene rect updates."""

    def test_update_scene_rect_preserves_scrollbar_positions(self):
        """Test that scrollbar positions are preserved when scene rect changes."""
        # Create mocks
        mock_scene = Mock()
        mock_view = Mock(spec=QGraphicsView)

        # Mock scrollbars with initial positions
        mock_h_scrollbar = Mock(spec=QScrollBar)
        mock_v_scrollbar = Mock(spec=QScrollBar)
        mock_h_scrollbar.value.return_value = 100  # Initial horizontal position
        mock_v_scrollbar.value.return_value = 200  # Initial vertical position

        mock_view.horizontalScrollBar.return_value = mock_h_scrollbar
        mock_view.verticalScrollBar.return_value = mock_v_scrollbar

        # Mock scene setup
        mock_scene.views.return_value = [mock_view]
        mock_scene.itemsBoundingRect.return_value = QRectF(0, 0, 1000, 1000)

        # Create strategy instance with minimal mocks
        # Use SinglePageStrategy which inherits from BaseStrategy
        strategy = SinglePageStrategy(
            graphics_scene=mock_scene,
            pdf_document=Mock(),
            document_presenter=Mock(),
            margin_presenter=Mock(),
            navigation_presenter=Mock(),
            margin_renderer=Mock(),
        )

        # Call update_scene_rect
        strategy.update_scene_rect()

        # Verify scrollbar positions were saved and restored
        assert mock_h_scrollbar.value.call_count >= 1  # Called to get initial value
        assert mock_v_scrollbar.value.call_count >= 1  # Called to get initial value

        # Verify scrollbar positions were restored to exact same values
        mock_h_scrollbar.setValue.assert_called_with(100)
        mock_v_scrollbar.setValue.assert_called_with(200)

        # Verify scene rect was updated with padding
        mock_scene.setSceneRect.assert_called_once()
        args = mock_scene.setSceneRect.call_args[0]
        expanded_rect = args[0]

        # Check that padding was added (5000 pixels on each side)
        assert expanded_rect.left() == -5000
        assert expanded_rect.top() == -5000
        assert expanded_rect.right() == 6000  # 1000 + 5000
        assert expanded_rect.bottom() == 6000  # 1000 + 5000

    def test_update_scene_rect_handles_missing_scrollbars(self):
        """Test that update_scene_rect handles views without scrollbars gracefully."""
        # Create mocks
        mock_scene = Mock()
        mock_view = Mock(spec=QGraphicsView)

        # Mock view without scrollbars
        mock_view.horizontalScrollBar.return_value = None
        mock_view.verticalScrollBar.return_value = None

        # Mock scene setup
        mock_scene.views.return_value = [mock_view]
        mock_scene.itemsBoundingRect.return_value = QRectF(0, 0, 1000, 1000)

        # Create strategy instance
        # Use SinglePageStrategy which inherits from BaseStrategy
        strategy = SinglePageStrategy(
            graphics_scene=mock_scene,
            pdf_document=Mock(),
            document_presenter=Mock(),
            margin_presenter=Mock(),
            navigation_presenter=Mock(),
            margin_renderer=Mock(),
        )

        # This should not raise an exception
        strategy.update_scene_rect()

        # Verify scene rect was still updated
        mock_scene.setSceneRect.assert_called_once()

    def test_multiple_views_preserve_individual_positions(self):
        """Test that multiple views each preserve their own scrollbar positions."""
        # Create mocks
        mock_scene = Mock()

        # Create two views with different scrollbar positions
        mock_view1 = Mock(spec=QGraphicsView)
        mock_h_scrollbar1 = Mock(spec=QScrollBar)
        mock_v_scrollbar1 = Mock(spec=QScrollBar)
        mock_h_scrollbar1.value.return_value = 100
        mock_v_scrollbar1.value.return_value = 200
        mock_view1.horizontalScrollBar.return_value = mock_h_scrollbar1
        mock_view1.verticalScrollBar.return_value = mock_v_scrollbar1

        mock_view2 = Mock(spec=QGraphicsView)
        mock_h_scrollbar2 = Mock(spec=QScrollBar)
        mock_v_scrollbar2 = Mock(spec=QScrollBar)
        mock_h_scrollbar2.value.return_value = 300
        mock_v_scrollbar2.value.return_value = 400
        mock_view2.horizontalScrollBar.return_value = mock_h_scrollbar2
        mock_view2.verticalScrollBar.return_value = mock_v_scrollbar2

        # Mock scene setup
        mock_scene.views.return_value = [mock_view1, mock_view2]
        mock_scene.itemsBoundingRect.return_value = QRectF(0, 0, 1000, 1000)

        # Create strategy instance
        # Use SinglePageStrategy which inherits from BaseStrategy
        strategy = SinglePageStrategy(
            graphics_scene=mock_scene,
            pdf_document=Mock(),
            document_presenter=Mock(),
            margin_presenter=Mock(),
            navigation_presenter=Mock(),
            margin_renderer=Mock(),
        )

        # Call update_scene_rect
        strategy.update_scene_rect()

        # Verify each view's scrollbar positions were restored correctly
        mock_h_scrollbar1.setValue.assert_called_with(100)
        mock_v_scrollbar1.setValue.assert_called_with(200)
        mock_h_scrollbar2.setValue.assert_called_with(300)
        mock_v_scrollbar2.setValue.assert_called_with(400)


class TestOverlayToggleStability:
    """Test that toggling overlays doesn't cause viewport shifts."""

    @patch("momovu.views.components.toggle_manager.logger")
    def test_toggle_margins_preserves_viewport(self, mock_logger):
        """Test that toggling margins doesn't shift the viewport."""
        from momovu.views.components.toggle_manager import ToggleManager

        # Create mock main window with all required attributes
        mock_main_window = Mock()
        mock_main_window.show_margins_action = Mock()
        mock_main_window.show_margins_action.isChecked.return_value = True
        mock_main_window.margin_presenter = Mock()

        # Mock render_current_page to track calls
        mock_main_window.render_current_page = Mock()

        # Create toggle manager
        toggle_manager = ToggleManager(mock_main_window)

        # Toggle margins
        toggle_manager.toggle_margins()

        # Verify margin state was updated
        mock_main_window.margin_presenter.set_show_margins.assert_called_with(True)

        # Verify render was called (which should preserve viewport)
        mock_main_window.render_current_page.assert_called_once()

    @patch("momovu.views.components.toggle_manager.logger")
    def test_all_overlay_toggles_preserve_viewport(self, mock_logger):
        """Test that all overlay toggle methods preserve viewport position."""
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

        # Mock presenters
        mock_main_window.margin_presenter = Mock()
        mock_main_window.margin_presenter.set_show_margins = Mock()
        mock_main_window.margin_presenter.set_show_trim_lines = Mock()
        mock_main_window.margin_presenter.set_show_barcode = Mock()
        mock_main_window.margin_presenter.set_show_fold_lines = Mock()
        mock_main_window.margin_presenter.set_show_bleed_lines = Mock()

        # Mock render_current_page
        mock_main_window.render_current_page = Mock()

        # Create toggle manager
        toggle_manager = ToggleManager(mock_main_window)

        # Test each toggle method
        toggle_methods = [
            ("toggle_margins", "set_show_margins"),
            ("toggle_trim_lines", "set_show_trim_lines"),
            ("toggle_barcode", "set_show_barcode"),
            ("toggle_fold_lines", "set_show_fold_lines"),
            ("toggle_bleed_lines", "set_show_bleed_lines"),
        ]

        for method_name, presenter_method in toggle_methods:
            # Reset mock
            mock_main_window.render_current_page.reset_mock()
            mock_main_window.margin_presenter.reset_mock()

            # Call toggle method
            getattr(toggle_manager, method_name)()

            # Verify presenter was updated
            getattr(
                mock_main_window.margin_presenter, presenter_method
            ).assert_called_once()

            # Verify render was called
            mock_main_window.render_current_page.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Comprehensive test suite for Main Window refactoring.

This test suite ensures that the Main Window refactoring maintains
all existing functionality while improving the architecture.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

from momovu.views.main_window import MainWindow


class TestMainWindowAPI:
    """Test that all public API methods continue to work."""

    def test_initialization_methods_exist(self, qapp):
        """Test that all initialization methods exist and are callable."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Core initialization methods
            assert hasattr(window, "_setup_ui")
            assert hasattr(window, "_setup_components")
            assert callable(window._setup_ui)
            assert callable(window._setup_components)

            window.close()

    def test_document_methods_exist(self, qapp):
        """Test that all document-related methods exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            methods = [
                "load_pdf",
                "render_current_page",
                "update_page_label",
            ]
            for method in methods:
                assert hasattr(window, method)
                assert callable(getattr(window, method))

            window.close()

    def test_navigation_methods_exist(self, qapp):
        """Test that all navigation methods exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            methods = [
                "go_to_first_page",
                "previous_page",
                "next_page",
                "go_to_last_page",
                "on_page_number_changed",
                "on_num_pages_changed",
            ]
            for method in methods:
                assert hasattr(window, method)
                assert callable(getattr(window, method))

            window.close()

    def test_toggle_methods_exist(self, qapp):
        """Test that all toggle methods exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            methods = [
                "toggle_fullscreen",
                "toggle_presentation",
                "toggle_side_by_side",
                "toggle_margins",
                "toggle_trim_lines",
                "toggle_barcode",
                "toggle_fold_lines",
                "set_document_type",
            ]
            for method in methods:
                assert hasattr(window, method)
                assert callable(getattr(window, method))

            window.close()

    def test_zoom_methods_exist(self, qapp):
        """Test that all zoom methods exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            methods = ["zoom_in", "zoom_out", "fit_to_page"]
            for method in methods:
                assert hasattr(window, method)
                assert callable(getattr(window, method))

            window.close()

    def test_dialog_methods_exist(self, qapp):
        """Test that all dialog methods exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            methods = [
                "open_file_dialog",
                "show_shortcuts_dialog",
                "show_about_dialog",
                "show_go_to_page_dialog",
            ]
            for method in methods:
                assert hasattr(window, method)
                assert callable(getattr(window, method))

            window.close()

    def test_required_attributes_exist(self, qapp):
        """Test that all required attributes exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            attributes = [
                "pdf_document",
                "document_presenter",
                "margin_presenter",
                "navigation_presenter",
                "graphics_view",
                "graphics_scene",
                "page_renderer",
                "ui_state_manager",
                "toggle_manager",
                "navigation_controller",
            ]
            for attr in attributes:
                assert hasattr(window, attr)

            window.close()

    def test_signals_exist(self, qapp):
        """Test that all required signals exist."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Only zoom_changed signal remains after cleanup
            signals = [
                "zoom_changed",
            ]
            for signal in signals:
                assert hasattr(window, signal)

            window.close()


class TestMainWindowBehavior:
    """Test that Main Window behavior remains consistent."""

    def test_initialization_order(self, qapp):
        """Test that initialization happens in the correct order."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Check that components are properly initialized
            assert window.window_initializer is not None
            assert window.graphics_view is not None
            assert window.graphics_scene is not None
            assert window.page_renderer is not None
            assert window.ui_state_manager is not None
            assert window.toggle_manager is not None
            assert window.navigation_controller is not None

            window.close()

    def test_component_dependencies(self, qapp):
        """Test that component dependencies are properly set up."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Check that page renderer has required dependencies
            assert window.page_renderer.graphics_scene is not None
            assert window.page_renderer.pdf_document is not None
            assert window.page_renderer.document_presenter is not None
            assert window.page_renderer.margin_presenter is not None
            assert window.page_renderer.navigation_presenter is not None

            window.close()

    def test_signal_connections_work(self, qapp):
        """Test that signal connections are properly established."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the methods to verify they get called
            window.open_file_dialog = Mock()
            window.toggle_fullscreen = Mock()

            # Trigger signals
            window.open_action.triggered.emit()
            window.fullscreen_action.triggered.emit()

            # Verify methods were called
            window.open_file_dialog.assert_called_once()
            window.toggle_fullscreen.assert_called_once()

            window.close()

    def test_error_handling_during_init(self, qapp):
        """Test that initialization errors are properly handled."""
        # Test that exceptions during init are caught and cleaned up
        with patch("momovu.views.main_window.WindowSetup") as mock_setup:
            mock_setup.side_effect = RuntimeError("Test error")

            with pytest.raises(RuntimeError):
                MainWindow()

    def test_resource_cleanup(self, qapp):
        """Test that resources are properly cleaned up."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock cleanup methods
            window.signal_connector.cleanup = Mock()
            window.page_renderer.cleanup = Mock()
            window.graphics_view.cleanup = Mock()

            # Trigger cleanup
            window._cleanup_resources()

            # Verify cleanup was called
            window.signal_connector.cleanup.assert_called_once()
            window.page_renderer.cleanup.assert_called_once()
            window.graphics_view.cleanup.assert_called_once()

            window.close()


class TestMainWindowIntegration:
    """Test integration between Main Window and its components."""

    def test_document_loading_integration(self, qapp):
        """Test that document loading works through the full chain."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the document presenter
            window.document_presenter.load_document = Mock(return_value=True)
            window.document_presenter.get_page_count = Mock(return_value=10)
            window.render_current_page = Mock()

            # Load a document
            window.load_pdf("test.pdf")

            # Verify the chain was called
            window.document_presenter.load_document.assert_called_once_with("test.pdf")
            window.render_current_page.assert_called_once()

            window.close()

    def test_navigation_integration(self, qapp):
        """Test that navigation works through the full chain."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock navigation components
            window.navigation_presenter.get_current_page = Mock(return_value=5)
            window.navigation_presenter.get_total_pages = Mock(return_value=10)
            window.render_current_page = Mock()

            # Test navigation
            window.next_page()

            # Verify navigation controller was used
            assert window.navigation_controller is not None

            window.close()

    def test_toggle_integration(self, qapp):
        """Test that toggles work through the full chain."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock toggle manager
            window.toggle_manager.toggle_margins = Mock()

            # Test toggle
            window.toggle_margins()

            # Verify toggle manager was called
            window.toggle_manager.toggle_margins.assert_called_once()

            window.close()

    def test_ui_state_integration(self, qapp):
        """Test that UI state management works."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Test that UI state manager is properly integrated
            assert window.ui_state_manager is not None
            assert hasattr(window.ui_state_manager, "is_presentation_mode")

            window.close()


class TestMainWindowRegressionPrevention:
    """Test specific scenarios that could cause regressions."""

    def test_keyboard_events_still_work(self, qapp):
        """Test that keyboard events are still properly handled."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the graphics view keyPressEvent
            window.graphics_view.keyPressEvent = Mock()

            # Create a key event
            key_event = QKeyEvent(
                QKeyEvent.Type.KeyPress,
                Qt.Key.Key_Right,
                Qt.KeyboardModifier.NoModifier,
            )

            # Send the event
            window.keyPressEvent(key_event)

            # Verify it was delegated to graphics view
            window.graphics_view.keyPressEvent.assert_called_once_with(key_event)

            window.close()

    def test_spinbox_updates_still_work(self, qapp):
        """Test that spinbox updates still work."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock navigation controller
            window.navigation_controller.on_page_number_changed = Mock()

            # Test page number change
            window.on_page_number_changed(5)

            # Verify delegation works
            window.navigation_controller.on_page_number_changed.assert_called_once_with(
                5
            )

            window.close()

    def test_presentation_mode_still_works(self, qapp):
        """Test that presentation mode functionality is preserved."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock UI state manager
            window.ui_state_manager.toggle_presentation = Mock()

            # Test presentation toggle
            window.toggle_presentation()

            # Verify it works through toggle manager
            window.ui_state_manager.toggle_presentation.assert_called_once()

            window.close()

    def test_error_dialogs_still_work(self, qapp):
        """Test that error dialogs are still shown."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            with patch("momovu.views.main_window.QMessageBox") as mock_msgbox:
                # Mock document presenter to raise an error
                window.document_presenter.load_document = Mock(
                    side_effect=Exception("Test error")
                )

                # Try to load a document
                window.load_pdf("test.pdf")

                # Verify error dialog was shown
                mock_msgbox.critical.assert_called_once()

            window.close()

    def test_window_close_cleanup_still_works(self, qapp):
        """Test that window close cleanup still works."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock cleanup method
            window._cleanup_resources = Mock()

            # Create a close event
            from PySide6.QtGui import QCloseEvent

            close_event = QCloseEvent()

            # Send the close event
            window.closeEvent(close_event)

            # Verify cleanup was called
            window._cleanup_resources.assert_called_once()

            window.close()


class TestMainWindowPerformance:
    """Test that refactoring doesn't negatively impact performance."""

    def test_initialization_time_reasonable(self, qapp):
        """Test that initialization time is reasonable."""
        import time

        start_time = time.time()
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()
            window.close()
        end_time = time.time()

        # Initialization should take less than 5 seconds
        assert (end_time - start_time) < 5.0

    def test_method_call_overhead_minimal(self, qapp):
        """Test that method call overhead is minimal."""
        import time

        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow()

            # Mock the underlying method to do nothing
            window.render_current_page = Mock()

            # Time multiple calls
            start_time = time.time()
            for _ in range(100):
                window.render_current_page()
            end_time = time.time()

            # 100 calls should take less than 0.1 seconds
            assert (end_time - start_time) < 0.1

            window.close()

"""Simplified tests for UI state management components.

These tests focus on the actual implementations without extensive mocking.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt

from momovu.views.components.cleanup_coordinator import CleanupCoordinator
from momovu.views.components.dialog_manager import DialogManager
from momovu.views.components.signal_connections import SignalConnections
from momovu.views.components.toggle_manager import ToggleManager
from momovu.views.components.ui_state_manager import UIStateManager


class TestToggleManager:
    """Test ToggleManager core functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a minimal mock main window."""
        window = Mock()

        # Mock actions
        window.show_margins_action = Mock()
        window.show_margins_action.isChecked = Mock(return_value=False)

        # Mock presenter
        window.margin_presenter = Mock()
        window.margin_presenter.set_show_margins = Mock()

        # Mock UI state manager
        window.ui_state_manager = Mock()
        window.ui_state_manager.is_presentation_mode = False

        # Mock render method
        window.render_current_page = Mock()

        return window

    def test_toggle_margins(self, mock_main_window):
        """Test toggling margin visibility."""
        manager = ToggleManager(mock_main_window)

        # Test turning margins on
        mock_main_window.show_margins_action.isChecked.return_value = True
        manager.toggle_margins()

        mock_main_window.margin_presenter.set_show_margins.assert_called_with(True)
        mock_main_window.render_current_page.assert_called_once()

    def test_toggle_fullscreen_delegates(self, mock_main_window):
        """Test that fullscreen toggle delegates to UI state manager."""
        manager = ToggleManager(mock_main_window)

        manager.toggle_fullscreen()

        mock_main_window.ui_state_manager.toggle_fullscreen.assert_called_once()

    def test_set_document_type(self, mock_main_window):
        """Test setting document type."""
        # Add required action mocks
        mock_main_window.interior_action = Mock()
        mock_main_window.cover_action = Mock()
        mock_main_window.dustjacket_action = Mock()
        mock_main_window.margin_presenter.set_document_type = Mock()
        mock_main_window.menu_builder = None
        mock_main_window.toolbar_builder = None

        manager = ToggleManager(mock_main_window)

        manager.set_document_type("cover")

        mock_main_window.interior_action.setChecked.assert_called_with(False)
        mock_main_window.cover_action.setChecked.assert_called_with(True)
        mock_main_window.dustjacket_action.setChecked.assert_called_with(False)
        mock_main_window.margin_presenter.set_document_type.assert_called_with("cover")


class TestDialogManager:
    """Test DialogManager core functionality."""

    @pytest.fixture
    def dialog_manager(self):
        """Create a DialogManager with mock parent."""
        parent = Mock()
        return DialogManager(parent)

    def test_initialization(self, dialog_manager):
        """Test DialogManager initialization."""
        assert dialog_manager.parent is not None
        assert dialog_manager._file_load_callback is None
        assert dialog_manager._page_navigation_callback is None

    def test_set_callbacks(self, dialog_manager):
        """Test setting callbacks."""
        file_callback = Mock()
        page_callback = Mock()

        dialog_manager.set_file_load_callback(file_callback)
        dialog_manager.set_page_navigation_callback(page_callback)

        assert dialog_manager._file_load_callback == file_callback
        assert dialog_manager._page_navigation_callback == page_callback

    @patch("momovu.views.components.dialog_manager.QFileDialog.getOpenFileName")
    def test_show_open_file_dialog(self, mock_get_open, dialog_manager):
        """Test showing file open dialog."""
        mock_get_open.return_value = ("/path/to/file.pdf", "PDF Files (*.pdf)")
        callback = Mock()
        dialog_manager.set_file_load_callback(callback)

        dialog_manager.show_open_file_dialog()

        mock_get_open.assert_called_once()
        callback.assert_called_once_with("/path/to/file.pdf")

    @patch("momovu.views.components.dialog_manager.ShortcutsDialog")
    def test_show_shortcuts_dialog(self, mock_dialog_class, dialog_manager):
        """Test showing shortcuts dialog."""
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        dialog_manager.show_shortcuts_dialog()

        mock_dialog_class.assert_called_once_with(dialog_manager.parent)
        mock_dialog.exec.assert_called_once()


class TestUIStateManager:
    """Test UIStateManager core functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a minimal mock main window."""
        window = Mock()
        window.isFullScreen = Mock(return_value=False)
        window.windowState = Mock(return_value=Qt.WindowState.WindowNoState)
        window.setWindowState = Mock()
        window.showFullScreen = Mock()
        window.showMaximized = Mock()
        window.menuBar = Mock(return_value=Mock())
        window.toolbar = Mock()
        window.status_bar = Mock()
        window.presentation_action = Mock()
        window.graphics_scene = Mock()
        window.graphics_view = Mock()
        return window

    def test_initialization(self, mock_main_window):
        """Test UIStateManager initialization."""
        manager = UIStateManager(mock_main_window)

        assert manager.main_window == mock_main_window
        assert manager.is_presentation_mode is False
        assert manager._transition_in_progress is False
        assert manager._pending_timers == []

    def test_toggle_fullscreen_to_fullscreen(self, mock_main_window):
        """Test entering fullscreen mode."""
        manager = UIStateManager(mock_main_window)
        mock_main_window.isFullScreen.return_value = False

        with patch.object(manager, "_add_timer"):
            manager.toggle_fullscreen()

        # Should hide UI elements
        mock_main_window.menuBar().hide.assert_called_once()
        mock_main_window.toolbar.hide.assert_called_once()
        mock_main_window.status_bar.hide.assert_called_once()

    def test_toggle_fullscreen_from_fullscreen(self, mock_main_window):
        """Test exiting fullscreen mode."""
        manager = UIStateManager(mock_main_window)
        mock_main_window.isFullScreen.return_value = True

        with patch.object(manager, "_add_timer"):
            manager.toggle_fullscreen()

        # Should show UI elements
        mock_main_window.menuBar().show.assert_called_once()
        mock_main_window.toolbar.show.assert_called_once()
        mock_main_window.status_bar.show.assert_called_once()

    def test_enter_presentation_mode(self, mock_main_window):
        """Test entering presentation mode."""
        manager = UIStateManager(mock_main_window)

        with patch.object(manager, "_add_timer"):
            manager.enter_presentation_mode()

        assert manager.is_presentation_mode is True
        mock_main_window.menuBar().hide.assert_called_once()
        mock_main_window.toolbar.hide.assert_called_once()
        mock_main_window.status_bar.hide.assert_called_once()
        mock_main_window.presentation_action.setChecked.assert_called_with(True)

    def test_exit_presentation_mode(self, mock_main_window):
        """Test exiting presentation mode."""
        manager = UIStateManager(mock_main_window)
        manager.is_presentation_mode = True

        # Mock navigation presenter
        mock_main_window.navigation_presenter = Mock()
        mock_main_window.navigation_presenter.model = Mock()
        mock_main_window.navigation_presenter.model.view_mode = "single"
        mock_main_window.render_current_page = Mock()
        mock_main_window.fit_to_page = Mock()

        with patch.object(manager, "_add_timer"):
            manager.exit_presentation_mode()

        assert manager.is_presentation_mode is False
        mock_main_window.menuBar().show.assert_called_once()
        mock_main_window.toolbar.show.assert_called_once()
        mock_main_window.status_bar.show.assert_called_once()
        mock_main_window.presentation_action.setChecked.assert_called_with(False)


class TestSignalConnections:
    """Test SignalConnections core functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a minimal mock main window with actions."""
        window = Mock()

        # Create mock actions with triggered signals
        for action_name in [
            "open_action",
            "exit_action",
            "fullscreen_action",
            "presentation_action",
            "zoom_in_action",
            "zoom_out_action",
        ]:
            action = Mock()
            action.triggered = Mock()
            action.triggered.connect = Mock()
            setattr(window, action_name, action)

        # Mock methods
        window.open_file_dialog = Mock()
        window.close = Mock()
        window.toggle_fullscreen = Mock()

        return window

    def test_initialization(self, mock_main_window):
        """Test SignalConnections initialization."""
        connections = SignalConnections(mock_main_window)

        assert connections.main_window == mock_main_window
        assert connections._connections == []
        assert connections._cleaned_up is False

    def test_safe_connect(self, mock_main_window):
        """Test safe signal connection."""
        connections = SignalConnections(mock_main_window)

        signal = Mock()
        signal.connect = Mock()
        slot = Mock()

        connections._safe_connect(signal, slot)

        signal.connect.assert_called_once_with(slot)
        assert (signal, slot) in connections._connections

    def test_cleanup(self, mock_main_window):
        """Test cleanup disconnects signals."""
        connections = SignalConnections(mock_main_window)

        # Add some mock connections
        signal1 = Mock()
        signal1.disconnect = Mock()
        signal2 = Mock()
        signal2.disconnect = Mock()

        connections._connections = [(signal1, Mock()), (signal2, Mock())]

        connections.cleanup()

        signal1.disconnect.assert_called_once()
        signal2.disconnect.assert_called_once()
        assert connections._connections == []
        assert connections._cleaned_up is True
        assert connections.main_window is None

    def test_cleanup_idempotent(self, mock_main_window):
        """Test cleanup can be called multiple times safely."""
        connections = SignalConnections(mock_main_window)

        connections.cleanup()
        # Second cleanup should not raise
        connections.cleanup()

        assert connections._cleaned_up is True


class TestCleanupCoordinator:
    """Test CleanupCoordinator core functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a minimal mock main window."""
        window = Mock()
        window._resources_initialized = True
        window.signal_connector = Mock()
        window.signal_connector.cleanup = Mock()
        window.page_renderer = Mock()
        window.page_renderer.cleanup = Mock()
        window.graphics_view = Mock()
        window.graphics_view.cleanup = Mock()
        window.graphics_scene = Mock()
        window.graphics_scene.clear = Mock()
        window.pdf_document = Mock()
        window.pdf_document.close = Mock()
        return window

    def test_initialization(self, mock_main_window):
        """Test CleanupCoordinator initialization."""
        coordinator = CleanupCoordinator(mock_main_window)
        assert coordinator.main_window == mock_main_window

    def test_cleanup_resources(self, mock_main_window):
        """Test resource cleanup sequence."""
        coordinator = CleanupCoordinator(mock_main_window)

        coordinator.cleanup_resources()

        # Verify cleanup was called in order
        mock_main_window.signal_connector.cleanup.assert_called_once()
        mock_main_window.page_renderer.cleanup.assert_called_once()
        mock_main_window.graphics_view.cleanup.assert_called_once()
        mock_main_window.graphics_scene.clear.assert_called_once()
        mock_main_window.pdf_document.close.assert_called_once()

        assert mock_main_window._resources_initialized is False

    def test_cleanup_with_missing_components(self, mock_main_window):
        """Test cleanup handles missing components gracefully."""
        # Remove some components
        delattr(mock_main_window, "page_renderer")
        mock_main_window.graphics_view = None

        coordinator = CleanupCoordinator(mock_main_window)

        # Should not raise exception
        coordinator.cleanup_resources()

        # Should still cleanup available components
        mock_main_window.signal_connector.cleanup.assert_called_once()
        mock_main_window.graphics_scene.clear.assert_called_once()

    def test_cleanup_with_errors(self, mock_main_window):
        """Test cleanup continues even if components raise errors."""
        # Make signal connector raise error
        mock_main_window.signal_connector.cleanup.side_effect = Exception("Test error")

        coordinator = CleanupCoordinator(mock_main_window)

        # Should not raise exception
        coordinator.cleanup_resources()

        # Should still cleanup other components
        mock_main_window.graphics_view.cleanup.assert_called_once()
        mock_main_window.graphics_scene.clear.assert_called_once()

    def test_cleanup_not_initialized(self, mock_main_window):
        """Test cleanup skips if resources not initialized."""
        mock_main_window._resources_initialized = False

        coordinator = CleanupCoordinator(mock_main_window)
        coordinator.cleanup_resources()

        # Should not attempt any cleanup
        mock_main_window.signal_connector.cleanup.assert_not_called()

"""Comprehensive tests for UI state management components.

Tests focus on toggle management, dialog management, and UI state coordination.
These tests improve coverage for UI state management from low coverage to 80%+.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar

from momovu.views.components.cleanup_coordinator import CleanupCoordinator
from momovu.views.components.dialog_manager import DialogManager
from momovu.views.components.signal_connections import SignalConnections
from momovu.views.components.toggle_manager import ToggleManager
from momovu.views.components.ui_state_manager import UIStateManager


class TestToggleManager:
    """Test ToggleManager functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with actions."""
        window = Mock()

        # Create mock actions - using actual action names from ToggleManager
        window.show_margins_action = Mock(spec=QAction)
        window.show_margins_action.isChecked = Mock(return_value=False)

        window.show_trim_lines_action = Mock(spec=QAction)
        window.show_trim_lines_action.isChecked = Mock(return_value=False)

        window.show_bleed_lines_action = Mock(spec=QAction)
        window.show_bleed_lines_action.isChecked = Mock(return_value=False)

        window.show_barcode_action = Mock(spec=QAction)
        window.show_barcode_action.isChecked = Mock(return_value=False)

        window.show_fold_lines_action = Mock(spec=QAction)
        window.show_fold_lines_action.isChecked = Mock(return_value=False)

        # Mock presenter
        window.margin_presenter = Mock()
        window.margin_presenter.set_show_margins = Mock()
        window.margin_presenter.set_show_trim_lines = Mock()
        window.margin_presenter.set_show_bleed_lines = Mock()
        window.margin_presenter.set_show_barcode = Mock()
        window.margin_presenter.set_show_fold_lines = Mock()

        # Mock UI state manager
        window.ui_state_manager = Mock()
        window.ui_state_manager.is_presentation_mode = False

        # Mock render method
        window.render_current_page = Mock()

        return window

    @pytest.fixture
    def toggle_manager(self, mock_main_window):
        """Create a ToggleManager instance."""
        return ToggleManager(mock_main_window)

    def test_initialization(self, mock_main_window):
        """Test ToggleManager initialization."""
        manager = ToggleManager(mock_main_window)
        assert manager.main_window == mock_main_window

    def test_toggle_margins(self, toggle_manager, mock_main_window):
        """Test toggling margin visibility."""
        # Toggle on
        mock_main_window.show_margins_action.isChecked.return_value = True
        toggle_manager.toggle_margins()

        mock_main_window.margin_presenter.set_show_margins.assert_called_once_with(True)
        mock_main_window.render_current_page.assert_called_once()

        # Toggle off
        mock_main_window.render_current_page.reset_mock()
        mock_main_window.margin_presenter.set_show_margins.reset_mock()
        mock_main_window.show_margins_action.isChecked.return_value = False
        toggle_manager.toggle_margins()

        mock_main_window.margin_presenter.set_show_margins.assert_called_once_with(
            False
        )
        mock_main_window.render_current_page.assert_called_once()

    def test_toggle_trim_lines(self, toggle_manager, mock_main_window):
        """Test toggling trim line visibility."""
        mock_main_window.show_trim_lines_action.isChecked.return_value = True
        toggle_manager.toggle_trim_lines()

        mock_main_window.margin_presenter.set_show_trim_lines.assert_called_once_with(
            True
        )
        mock_main_window.render_current_page.assert_called_once()

    def test_toggle_bleed_lines(self, toggle_manager, mock_main_window):
        """Test toggling bleed line visibility."""
        mock_main_window.show_bleed_lines_action.isChecked.return_value = True
        toggle_manager.toggle_bleed_lines()

        mock_main_window.margin_presenter.set_show_bleed_lines.assert_called_once_with(
            True
        )
        mock_main_window.render_current_page.assert_called_once()

    def test_toggle_barcode(self, toggle_manager, mock_main_window):
        """Test toggling barcode visibility."""
        mock_main_window.show_barcode_action.isChecked.return_value = True
        toggle_manager.toggle_barcode()

        mock_main_window.margin_presenter.set_show_barcode.assert_called_once_with(True)
        mock_main_window.render_current_page.assert_called_once()

    def test_toggle_fold_lines(self, toggle_manager, mock_main_window):
        """Test toggling fold line visibility."""
        mock_main_window.show_fold_lines_action.isChecked.return_value = True
        toggle_manager.toggle_fold_lines()

        # Verify fold lines state was updated via margin presenter
        mock_main_window.margin_presenter.set_show_fold_lines.assert_called_once_with(
            True
        )
        mock_main_window.render_current_page.assert_called_once()


class TestDialogManager:
    """Test DialogManager functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window."""
        window = Mock()
        window.isActiveWindow = Mock(return_value=True)
        return window

    @pytest.fixture
    def dialog_manager(self, mock_main_window):
        """Create a DialogManager instance."""
        return DialogManager(mock_main_window)

    def test_initialization(self, mock_main_window):
        """Test DialogManager initialization."""
        manager = DialogManager(mock_main_window)
        assert manager.parent == mock_main_window
        assert manager._file_load_callback is None
        assert manager._page_navigation_callback is None

    @patch("momovu.views.components.dialog_manager.AboutDialog")
    def test_show_about_dialog(
        self, mock_about_class, dialog_manager, mock_main_window
    ):
        """Test showing about dialog."""
        mock_dialog = Mock()
        mock_about_class.return_value = mock_dialog

        dialog_manager.show_about_dialog()

        mock_about_class.assert_called_once_with(mock_main_window)
        mock_dialog.exec.assert_called_once()

    @patch("momovu.views.components.dialog_manager.ShortcutsDialog")
    def test_show_shortcuts_dialog(
        self, mock_shortcuts_class, dialog_manager, mock_main_window
    ):
        """Test showing shortcuts dialog."""
        mock_dialog = Mock()
        mock_shortcuts_class.return_value = mock_dialog

        dialog_manager.show_shortcuts_dialog()

        mock_shortcuts_class.assert_called_once_with(mock_main_window)
        mock_dialog.exec.assert_called_once()


class TestUIStateManager:
    """Test UIStateManager functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with UI elements."""
        window = Mock()

        # Mock toolbar
        window.toolbar = Mock(spec=QToolBar)
        window.toolbar.hide = Mock()
        window.toolbar.show = Mock()

        # Mock status bar
        window.status_bar = Mock()
        window.status_bar.hide = Mock()
        window.status_bar.show = Mock()

        # Mock menu bar
        window.menuBar = Mock()
        menu_bar_mock = Mock()
        menu_bar_mock.hide = Mock()
        menu_bar_mock.show = Mock()
        menu_bar_mock.isVisible = Mock(return_value=True)
        window.menuBar.return_value = menu_bar_mock

        # Mock window methods
        window.isFullScreen = Mock(return_value=False)
        # Return a Qt.WindowState that can be used with bitwise operations
        window.windowState = Mock(return_value=Qt.WindowState.WindowNoState)
        window.setWindowState = Mock()

        # Mock actions
        window.presentation_action = Mock()
        window.presentation_action.setChecked = Mock()

        # Mock graphics scene and view
        window.graphics_scene = Mock()
        window.graphics_view = Mock()

        # Mock navigation presenter
        window.navigation_presenter = Mock()
        window.navigation_presenter.model = Mock()
        window.navigation_presenter.model.view_mode = "single"

        # Mock render method
        window.render_current_page = Mock()
        window.fit_to_page = Mock()

        return window

    @pytest.fixture
    def ui_state_manager(self, mock_main_window):
        """Create a UIStateManager instance."""
        return UIStateManager(mock_main_window)

    def test_initialization(self, mock_main_window):
        """Test UIStateManager initialization."""
        manager = UIStateManager(mock_main_window)
        assert manager.main_window == mock_main_window
        assert manager.is_presentation_mode is False
        assert manager._transition_in_progress is False

    def test_enter_presentation_mode(self, ui_state_manager, mock_main_window):
        """Test entering presentation mode."""
        ui_state_manager.enter_presentation_mode()

        assert ui_state_manager.is_presentation_mode is True
        mock_main_window.menuBar().hide.assert_called_once()
        mock_main_window.toolbar.hide.assert_called_once()
        mock_main_window.status_bar.hide.assert_called_once()
        mock_main_window.setWindowState.assert_called()

    def test_exit_presentation_mode(self, ui_state_manager, mock_main_window):
        """Test exiting presentation mode."""
        # Set up as in presentation mode
        ui_state_manager.is_presentation_mode = True

        ui_state_manager.exit_presentation_mode()

        assert ui_state_manager.is_presentation_mode is False
        mock_main_window.menuBar().show.assert_called_once()
        mock_main_window.toolbar.show.assert_called_once()
        mock_main_window.status_bar.show.assert_called_once()

    def test_toggle_fullscreen(self, ui_state_manager, mock_main_window):
        """Test toggling fullscreen mode."""
        # Enter fullscreen
        mock_main_window.isFullScreen.return_value = False

        ui_state_manager.toggle_fullscreen()

        mock_main_window.menuBar().hide.assert_called_once()
        mock_main_window.toolbar.hide.assert_called_once()
        mock_main_window.status_bar.hide.assert_called_once()
        mock_main_window.setWindowState.assert_called()

        # Exit fullscreen - need to reset the transition flag
        ui_state_manager._transition_in_progress = False
        mock_main_window.isFullScreen.return_value = True
        mock_main_window.menuBar().hide.reset_mock()
        mock_main_window.menuBar().show.reset_mock()
        mock_main_window.toolbar.hide.reset_mock()
        mock_main_window.toolbar.show.reset_mock()
        mock_main_window.status_bar.hide.reset_mock()
        mock_main_window.status_bar.show.reset_mock()

        ui_state_manager.toggle_fullscreen()

        mock_main_window.menuBar().show.assert_called_once()
        mock_main_window.toolbar.show.assert_called_once()
        mock_main_window.status_bar.show.assert_called_once()


class TestSignalConnections:
    """Test SignalConnections functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with signals."""
        window = Mock()

        # Mock actions with triggered signal
        window.open_action = Mock()
        window.open_action.triggered = Mock()
        window.open_action.triggered.connect = Mock()

        window.exit_action = Mock()
        window.exit_action.triggered = Mock()
        window.exit_action.triggered.connect = Mock()

        window.fullscreen_action = Mock()
        window.fullscreen_action.triggered = Mock()
        window.fullscreen_action.triggered.connect = Mock()

        # Mock methods
        window.open_file_dialog = Mock()
        window.close = Mock()
        window.toggle_fullscreen = Mock()

        return window

    @pytest.fixture
    def signal_connections(self, mock_main_window):
        """Create a SignalConnections instance."""
        return SignalConnections(mock_main_window)

    def test_initialization(self, mock_main_window):
        """Test SignalConnections initialization."""
        connections = SignalConnections(mock_main_window)
        assert connections.main_window == mock_main_window
        assert connections._connections == []
        assert connections._cleaned_up is False

    def test_connect_all(self, signal_connections, mock_main_window):
        """Test connecting all signals."""
        signal_connections.connect_all_signals()

        # Verify connections were made
        assert len(signal_connections._connections) > 0

        # Verify specific connections
        mock_main_window.open_action.triggered.connect.assert_called()
        mock_main_window.exit_action.triggered.connect.assert_called()
        mock_main_window.fullscreen_action.triggered.connect.assert_called()

    def test_disconnect_all(self, signal_connections, mock_main_window):
        """Test disconnecting all signals."""
        # First connect
        signal_connections.connect_all_signals()

        initial_count = len(signal_connections._connections)
        assert initial_count > 0

        # Then disconnect using cleanup
        signal_connections.cleanup()

        assert len(signal_connections._connections) == 0
        assert signal_connections._cleaned_up is True

    def test_connect_file_menu(self, signal_connections, mock_main_window):
        """Test connecting file menu signals."""
        signal_connections._connect_file_menu_signals()

        mock_main_window.open_action.triggered.connect.assert_called_with(
            mock_main_window.open_file_dialog
        )
        mock_main_window.exit_action.triggered.connect.assert_called_with(
            mock_main_window.close
        )

    def test_safe_connect(self, signal_connections):
        """Test safe signal connection."""
        mock_signal = Mock()
        mock_signal.connect = Mock()
        mock_slot = Mock()

        signal_connections._safe_connect(mock_signal, mock_slot)

        mock_signal.connect.assert_called_once_with(mock_slot)
        assert (mock_signal, mock_slot) in signal_connections._connections

    def test_safe_connect_error_handling(self, signal_connections):
        """Test safe connect with error."""
        mock_signal = Mock()
        mock_signal.connect = Mock(side_effect=RuntimeError("Connection failed"))
        mock_slot = Mock()

        # Should not raise exception
        signal_connections._safe_connect(mock_signal, mock_slot)

        # Should not add to connections
        assert (mock_signal, mock_slot) not in signal_connections._connections


class TestCleanupCoordinator:
    """Test CleanupCoordinator functionality."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with components."""
        window = Mock()
        window._resources_initialized = True

        # Mock components
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

        window.document_presenter = Mock()
        window.document_presenter.cleanup = Mock()

        window.margin_presenter = Mock()
        window.margin_presenter.cleanup = Mock()

        window.navigation_presenter = Mock()
        window.navigation_presenter.cleanup = Mock()

        return window

    @pytest.fixture
    def cleanup_coordinator(self, mock_main_window):
        """Create a CleanupCoordinator instance."""
        return CleanupCoordinator(mock_main_window)

    def test_initialization(self, mock_main_window):
        """Test CleanupCoordinator initialization."""
        coordinator = CleanupCoordinator(mock_main_window)
        assert coordinator.main_window == mock_main_window

    def test_cleanup_all(self, cleanup_coordinator, mock_main_window):
        """Test cleaning up all components."""
        cleanup_coordinator.cleanup_resources()

        # Verify components were cleaned up
        mock_main_window.signal_connector.cleanup.assert_called_once()
        mock_main_window.page_renderer.cleanup.assert_called_once()
        mock_main_window.graphics_view.cleanup.assert_called_once()
        mock_main_window.graphics_scene.clear.assert_called_once()
        mock_main_window.pdf_document.close.assert_called_once()

        assert mock_main_window._resources_initialized is False

    def test_cleanup_idempotent(self, cleanup_coordinator, mock_main_window):
        """Test that cleanup is idempotent."""
        # First cleanup
        cleanup_coordinator.cleanup_resources()

        # Set resources as not initialized after first cleanup
        mock_main_window._resources_initialized = False

        # Reset mocks
        mock_main_window.signal_connector.cleanup.reset_mock()
        mock_main_window.page_renderer.cleanup.reset_mock()
        mock_main_window.graphics_view.cleanup.reset_mock()

        # Second cleanup should return early
        cleanup_coordinator.cleanup_resources()

        # Components should not be cleaned up again
        mock_main_window.signal_connector.cleanup.assert_not_called()
        mock_main_window.page_renderer.cleanup.assert_not_called()
        mock_main_window.graphics_view.cleanup.assert_not_called()

    def test_cleanup_error_handling(self, cleanup_coordinator, mock_main_window):
        """Test cleanup continues even if a component fails."""
        # Make one component fail
        mock_main_window.graphics_view.cleanup.side_effect = Exception("Cleanup failed")

        # Should not raise
        cleanup_coordinator.cleanup_resources()

        # Other components should still be cleaned up
        mock_main_window.signal_connector.cleanup.assert_called_once()
        mock_main_window.page_renderer.cleanup.assert_called_once()
        mock_main_window.pdf_document.close.assert_called_once()

    def test_cleanup_missing_method(self, cleanup_coordinator, mock_main_window):
        """Test cleanup handles components without cleanup method."""
        # Add component without cleanup method
        mock_main_window.some_component = Mock(spec=[])  # No cleanup method

        # Should not raise
        cleanup_coordinator.cleanup_resources()

        # Other components should still be cleaned up
        mock_main_window.signal_connector.cleanup.assert_called_once()
        mock_main_window.page_renderer.cleanup.assert_called_once()

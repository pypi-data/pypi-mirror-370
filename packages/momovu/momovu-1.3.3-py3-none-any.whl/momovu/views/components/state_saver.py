"""State saver component for automatically saving document state changes."""

from typing import Any

from PySide6.QtCore import QObject, QTimer

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class StateSaver(QObject):
    """Automatically saves document state when it changes.

    This component monitors various state changes and updates the
    recent file entry to ensure all state is persisted.
    """

    def __init__(self, main_window: Any) -> None:
        """Initialize the state saver.

        Args:
            main_window: Reference to the main window
        """
        super().__init__()
        self.main_window = main_window
        self._pending_save = False
        self._saves_enabled = True  # Flag to temporarily disable saves

        # Create a single reusable timer for debouncing
        self._save_timer = QTimer(self)  # Set parent for proper cleanup
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._perform_save)

    def __del__(self) -> None:
        """Cleanup when the state saver is destroyed."""
        try:
            if hasattr(self, "_save_timer") and self._save_timer:
                self._save_timer.stop()
                self._save_timer.deleteLater()
        except Exception as e:
            # Log the error but don't raise during cleanup
            logger.debug(f"Error during StateSaver cleanup: {e}")

    def connect_signals(self) -> None:
        """Connect to all signals that indicate state changes."""
        # Connect zoom changes
        if hasattr(self.main_window, "zoom_controller"):
            self.main_window.zoom_controller.zoom_changed.connect(self._on_zoom_changed)

        # We'll need to call save_state from other places since not all
        # state changes emit signals

    def save_state(self) -> None:
        """Save the current document state to recent files.

        This debounces rapid changes to avoid excessive saves.
        """
        if not self._saves_enabled or not self._is_document_loaded():
            return

        # Cancel any pending save and reschedule
        if self._save_timer.isActive():
            self._save_timer.stop()

        # Schedule a save after a short delay to debounce rapid changes
        self._save_timer.start(500)  # 500ms delay
        self._pending_save = True

    def disable_saves(self) -> None:
        """Temporarily disable state saving."""
        self._saves_enabled = False
        # Cancel any pending saves
        if self._save_timer.isActive():
            self._save_timer.stop()
            self._pending_save = False

    def enable_saves(self) -> None:
        """Re-enable state saving."""
        self._saves_enabled = True

    def save_state_immediate(self) -> None:
        """Save the current document state immediately without debouncing."""
        if not self._is_document_loaded():
            return

        # Cancel any pending debounced save
        if self._save_timer.isActive():
            self._save_timer.stop()
            self._pending_save = False

        self._perform_save()

    def _perform_save(self) -> None:
        """Actually perform the save operation."""
        self._pending_save = False

        if not self._is_document_loaded():
            return

        try:
            # Gather all current state
            file_path = self.main_window.document_presenter.model.file_path
            doc_type = self.main_window.margin_presenter.get_document_type()

            # Get num_pages for cover/dustjacket
            num_pages = None
            if doc_type != "interior" and self.main_window.margin_presenter:
                num_pages = self.main_window.margin_presenter.model.num_pages

            # Get current page
            current_page = self.main_window.navigation_presenter.get_current_page()

            # Get view mode
            view_mode = self.main_window.navigation_presenter.model.view_mode

            # Get zoom level
            zoom_level = 1.0
            if hasattr(self.main_window, "zoom_controller"):
                zoom_level = self.main_window.zoom_controller.get_current_zoom()

            # Get overlay states
            overlays = {
                "show_margins": self.main_window.margin_presenter.model.show_margins,
                "show_trim_lines": self.main_window.margin_presenter.model.show_trim_lines,
                "show_barcode": self.main_window.margin_presenter.model.show_barcode,
                "show_fold_lines": self.main_window.margin_presenter.model.show_fold_lines,
                "show_bleed_lines": self.main_window.margin_presenter.model.show_bleed_lines,
            }

            # Get presentation mode state
            is_presentation = False
            if hasattr(self.main_window, "ui_state_manager"):
                is_presentation = self.main_window.ui_state_manager.is_presentation_mode

            # Save to recent files with all state
            self.main_window.config_presenter.add_recent_file(
                file_path=file_path,
                document_type=doc_type,
                num_pages=num_pages,
                current_page=current_page,
                view_mode=view_mode,
                zoom_level=zoom_level,
                overlays=overlays,
                presentation_mode=is_presentation,
            )

            logger.debug(
                f"Saved state: page={current_page}, view={view_mode}, zoom={zoom_level:.2f}"
            )

        except Exception as e:
            logger.error(f"Failed to save document state: {e}")

    def _on_zoom_changed(self, zoom_level: float) -> None:
        """Handle zoom level changes.

        Args:
            zoom_level: New zoom level
        """
        logger.debug(f"Zoom changed to {zoom_level:.2f}, scheduling save")
        self.save_state()

    def _is_document_loaded(self) -> bool:
        """Check if a document is currently loaded.

        Returns:
            True if document is loaded and all required components are available
        """
        return (
            hasattr(self.main_window, "document_presenter")
            and self.main_window.document_presenter
            and self.main_window.document_presenter.is_document_loaded()
            and hasattr(self.main_window, "margin_presenter")
            and self.main_window.margin_presenter
            and hasattr(self.main_window, "navigation_presenter")
            and self.main_window.navigation_presenter
            and hasattr(self.main_window, "config_presenter")
            and self.main_window.config_presenter
        )

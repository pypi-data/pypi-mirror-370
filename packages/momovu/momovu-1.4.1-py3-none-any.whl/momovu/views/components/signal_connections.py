"""Signal connector component for managing all signal-slot connections."""

from typing import Any

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class SignalConnections:
    """Manages all signal-slot connections for the main window.

    This class tracks all connections for safe cleanup to prevent
    crashes from dangling signal connections.
    """

    def __init__(self, main_window: Any) -> None:
        """Initialize the signal connector.

        Args:
            main_window: The main window with signals to connect
        """
        self.main_window = main_window
        self._connections: list[tuple[Any, Any]] = []
        self._cleaned_up = False

    def connect_all_signals(self) -> None:
        """Establish all Qt signal-slot connections for the UI."""
        if self._cleaned_up:
            logger.warning("Cannot connect signals after cleanup")
            return

        self._connect_file_menu_signals()
        self._connect_view_menu_signals()
        self._connect_document_menu_signals()
        self._connect_help_menu_signals()
        self._connect_navigation_signals()
        self._connect_zoom_signals()
        self._connect_spinbox_signals()
        logger.info(f"All signals connected ({len(self._connections)} connections)")

    def _safe_connect(self, signal: Any, slot: Any) -> None:
        """Connect signal with error handling and tracking for cleanup.

        Args:
            signal: Qt signal object
            slot: Callable to invoke on signal emission
        """
        try:
            signal.connect(slot)
            self._connections.append((signal, slot))
        except Exception as e:
            logger.error(f"Failed to connect signal: {e}")

    def _connect_file_menu_signals(self) -> None:
        """Wire up File menu actions (Open, Close, Preferences, Exit)."""
        self._safe_connect(
            self.main_window.open_action.triggered, self.main_window.open_file_dialog
        )
        self._safe_connect(
            self.main_window.close_action.triggered, self.main_window.close_pdf
        )
        if hasattr(self.main_window, "preferences_action"):
            self._safe_connect(
                self.main_window.preferences_action.triggered,
                self.main_window.show_preferences_dialog,
            )
        self._safe_connect(
            self.main_window.exit_action.triggered, self.main_window.close
        )

    def _connect_view_menu_signals(self) -> None:
        """Wire up View menu toggles (fullscreen, margins, etc)."""
        self._safe_connect(
            self.main_window.fullscreen_action.triggered,
            self.main_window.toggle_fullscreen,
        )
        self._safe_connect(
            self.main_window.presentation_action.triggered,
            self.main_window.toggle_presentation,
        )
        self._safe_connect(
            self.main_window.side_by_side_action.triggered,
            self.main_window.toggle_side_by_side,
        )
        self._safe_connect(
            self.main_window.show_margins_action.triggered,
            self.main_window.toggle_margins,
        )
        self._safe_connect(
            self.main_window.show_trim_lines_action.triggered,
            self.main_window.toggle_trim_lines,
        )
        self._safe_connect(
            self.main_window.show_barcode_action.triggered,
            self.main_window.toggle_barcode,
        )
        self._safe_connect(
            self.main_window.show_fold_lines_action.triggered,
            self.main_window.toggle_fold_lines,
        )
        self._safe_connect(
            self.main_window.show_bleed_lines_action.triggered,
            self.main_window.toggle_bleed_lines,
        )
        if hasattr(self.main_window, "show_gutter_action"):
            self._safe_connect(
                self.main_window.show_gutter_action.triggered,
                self.main_window.toggle_gutter,
            )

    def _connect_document_menu_signals(self) -> None:
        """Wire up Document type selection (interior/cover/dustjacket)."""
        self._safe_connect(
            self.main_window.interior_action.triggered,
            lambda: self.main_window.set_document_type("interior"),
        )
        self._safe_connect(
            self.main_window.cover_action.triggered,
            lambda: self.main_window.set_document_type("cover"),
        )
        self._safe_connect(
            self.main_window.dustjacket_action.triggered,
            lambda: self.main_window.set_document_type("dustjacket"),
        )
        self._safe_connect(
            self.main_window.spine_calculator_action.triggered,
            self.main_window.show_spine_calculator_dialog,
        )

    def _connect_navigation_signals(self) -> None:
        """Wire up page navigation buttons to controller methods."""
        self._safe_connect(
            self.main_window.first_page_action.triggered,
            self.main_window.go_to_first_page,
        )
        self._safe_connect(
            self.main_window.prev_page_action.triggered,
            self.main_window.previous_page,
        )
        self._safe_connect(
            self.main_window.next_page_action.triggered,
            self.main_window.next_page,
        )
        self._safe_connect(
            self.main_window.last_page_action.triggered,
            self.main_window.go_to_last_page,
        )

    def _connect_zoom_signals(self) -> None:
        """Wire up zoom controls (in/out/fit)."""
        self._safe_connect(
            self.main_window.zoom_in_action.triggered, self.main_window.zoom_in
        )
        self._safe_connect(
            self.main_window.zoom_out_action.triggered, self.main_window.zoom_out
        )
        self._safe_connect(
            self.main_window.fit_page_action.triggered, self.main_window.fit_to_page
        )

    def _connect_spinbox_signals(self) -> None:
        """Wire up page number and page count spinbox changes."""
        # With setKeyboardTracking(False), valueChanged only fires on:
        # - Enter key press
        # - Arrow button clicks
        # - Focus lost after typing
        self._safe_connect(
            self.main_window.page_number_spinbox.valueChanged,
            self.main_window.on_page_number_changed,
        )
        self._safe_connect(
            self.main_window.num_pages_spinbox.valueChanged,
            self.main_window.on_num_pages_changed,
        )

    def _connect_help_menu_signals(self) -> None:
        """Wire up Help menu items (shortcuts, about)."""
        self._safe_connect(
            self.main_window.shortcuts_action.triggered,
            self.main_window.show_shortcuts_dialog,
        )
        self._safe_connect(
            self.main_window.about_action.triggered, self.main_window.show_about_dialog
        )

    def cleanup(self) -> None:
        """Disconnect all tracked signals to prevent dangling references (idempotent)."""
        if self._cleaned_up:
            return

        logger.debug(f"Disconnecting {len(self._connections)} signal connections")

        for signal, slot in reversed(self._connections):
            try:
                signal.disconnect(slot)
            except (TypeError, RuntimeError) as e:
                # Signal might already be disconnected or object deleted
                # This is OK - we just want to ensure cleanup
                logger.debug(f"Signal already disconnected or deleted: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error disconnecting signal: {e}")

        self._connections.clear()
        self._cleaned_up = True
        self.main_window = None
        logger.info("SignalConnections cleanup completed")

"""Configuration presenter for MVP architecture."""

from typing import Any, Optional

from PySide6.QtGui import QColor

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.logger import get_logger
from momovu.models.configuration import ConfigurationModel

logger = get_logger(__name__)


class ConfigurationPresenter:
    """Presenter for configuration management."""

    def __init__(self, model: ConfigurationModel, manager: ConfigurationManager):
        """Initialize the configuration presenter.

        Args:
            model: Configuration model
            manager: Configuration manager
        """
        self.model = model
        self.manager = manager

        # Connect signals
        self.manager.config_changed.connect(self._on_config_changed)

    def load_configuration(self) -> None:
        """Load configuration from storage into model."""
        logger.debug("Loading configuration from storage")

        # Load colors - always handle as strings internally
        colors = {}
        self.manager.settings.beginGroup("colors")
        for color_key in [
            "margin_overlay",
            "barcode_area",
            "fold_lines",
            "trim_lines",
            "bleed_lines",
        ]:
            color_path = f"{color_key}/color"
            opacity_path = f"{color_key}/opacity"

            # Get color value - could be string or QColor depending on when it was saved
            color_value = self.manager.get_value(color_path, "#000000")

            # Ensure we always work with strings internally
            if isinstance(color_value, QColor):
                color_string = color_value.name()
            elif isinstance(color_value, str):
                color_string = color_value
            else:
                logger.warning(
                    f"Unexpected color type for {color_key}: {type(color_value)}"
                )
                color_string = "#000000"

            opacity = self.manager.get_value(opacity_path, 1.0, type=float)
            colors[color_key] = {"color": color_string, "opacity": opacity}
        self.manager.settings.endGroup()
        self.model.set_property("colors", colors)

        # Load line widths
        line_widths = {}
        self.manager.settings.beginGroup("line_widths")
        for width_key in ["fold_lines", "trim_lines", "bleed_lines"]:
            line_widths[width_key] = self.manager.get_value(width_key, 1, type=int)
        self.manager.settings.endGroup()
        self.model.set_property("line_widths", line_widths)

        # Load preferences
        preferences = {}
        self.manager.settings.beginGroup("preferences")
        preferences["auto_fit_on_load"] = self.manager.get_value(
            "auto_fit_on_load", True, type=bool
        )
        preferences["auto_fit_on_resize"] = self.manager.get_value(
            "auto_fit_on_resize", False, type=bool
        )
        preferences["remember_zoom_per_document"] = self.manager.get_value(
            "remember_zoom_per_document", True, type=bool
        )
        preferences["smooth_scrolling"] = self.manager.get_value(
            "smooth_scrolling", True, type=bool
        )
        preferences["scroll_speed"] = self.manager.get_value(
            "scroll_speed", 50, type=int
        )
        preferences["zoom_increment"] = self.manager.get_value(
            "zoom_increment", 1.1, type=float
        )
        preferences["cache_max_pages"] = self.manager.get_value(
            "cache/max_rendered_pages", 20, type=int
        )
        preferences["cache_max_memory_mb"] = self.manager.get_value(
            "cache/max_memory_mb", 300, type=int
        )
        preferences["high_contrast_mode"] = self.manager.get_value(
            "high_contrast_mode", False, type=bool
        )
        self.manager.settings.endGroup()
        self.model.set_property("preferences", preferences)

        # Load document defaults
        document_defaults = {}
        for doc_type in ["interior", "cover", "dustjacket"]:
            self.manager.settings.beginGroup(f"document_defaults/{doc_type}")
            defaults = {
                "show_margins": self.manager.get_value("show_margins", True, type=bool),
                "show_trim_lines": self.manager.get_value(
                    "show_trim_lines", True, type=bool
                ),
            }

            if doc_type in ["cover", "dustjacket"]:
                defaults["show_barcode"] = self.manager.get_value(
                    "show_barcode", True, type=bool
                )
                defaults["show_fold_lines"] = self.manager.get_value(
                    "show_fold_lines", True, type=bool
                )
                defaults["show_bleed_lines"] = self.manager.get_value(
                    "show_bleed_lines", True, type=bool
                )
                defaults["default_num_pages"] = self.manager.get_value(
                    "default_num_pages", 100, type=int
                )

            self.manager.settings.endGroup()
            document_defaults[doc_type] = defaults

        self.model.set_property("document_defaults", document_defaults)
        logger.debug("Configuration loaded from storage")

    def save_configuration(self) -> None:
        """Save model configuration to storage."""
        logger.debug("Saving configuration to storage")

        # Save colors - always save as strings to prevent serialization issues
        colors = self.model.get_property("colors", {})
        self.manager.settings.beginGroup("colors")
        for color_key, color_data in colors.items():
            # Save color as string for proper serialization
            color_string = color_data.get("color", "#000000")
            if not isinstance(color_string, str):
                logger.warning(
                    f"Color for {color_key} is not a string: {type(color_string)}"
                )
                color_string = "#000000"

            self.manager.set_value(f"{color_key}/color", color_string)
            self.manager.set_value(
                f"{color_key}/opacity", color_data.get("opacity", 1.0)
            )
        self.manager.settings.endGroup()

        # Save line widths
        line_widths = self.model.get_property("line_widths", {})
        self.manager.settings.beginGroup("line_widths")
        for width_key, width_value in line_widths.items():
            self.manager.set_value(width_key, width_value)
        self.manager.settings.endGroup()

        # Save preferences
        preferences = self.model.get_property("preferences", {})
        self.manager.settings.beginGroup("preferences")
        for pref_key, pref_value in preferences.items():
            if pref_key == "cache_max_pages":
                self.manager.set_value("cache/max_rendered_pages", pref_value)
            elif pref_key == "cache_max_memory_mb":
                self.manager.set_value("cache/max_memory_mb", pref_value)
            else:
                self.manager.set_value(pref_key, pref_value)
        self.manager.settings.endGroup()

        # Save document defaults
        document_defaults = self.model.get_property("document_defaults", {})
        for doc_type, defaults in document_defaults.items():
            self.manager.settings.beginGroup(f"document_defaults/{doc_type}")
            for key, value in defaults.items():
                self.manager.set_value(key, value)
            self.manager.settings.endGroup()

        self.manager.settings.sync()
        logger.debug("Configuration saved to storage")

    def apply_configuration(
        self, main_window: Any, skip_window_state: bool = False
    ) -> None:
        """Apply configuration to the application.

        Args:
            main_window: Main window instance to apply configuration to
            skip_window_state: If True, skip restoring window geometry/state
        """
        logger.debug("Applying configuration to application")

        # Apply window state if not skipping (e.g., during preferences dialog)
        if not skip_window_state:
            window_state = self.manager.get_window_state()
            if window_state.get("geometry"):
                main_window.restoreGeometry(window_state["geometry"])
            if window_state.get("state"):
                main_window.restoreState(window_state["state"])

        # Apply preferences
        preferences = self.model.get_property("preferences", {})

        # Apply zoom increment if zoom controller exists
        if hasattr(main_window, "zoom_controller"):
            zoom_inc = preferences.get("zoom_increment", 1.1)
            # Store for later use in zoom operations
            main_window._zoom_increment = zoom_inc

        logger.debug(
            f"Configuration applied to application (skip_window_state={skip_window_state})"
        )

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        logger.info("Resetting configuration to defaults")
        self.manager.reset_to_defaults()
        self.load_configuration()  # Reload from defaults

    def get_document_overlays(self, doc_type: str) -> dict[str, bool]:
        """Get overlay settings for a document type.

        Args:
            doc_type: Document type (interior, cover, dustjacket)

        Returns:
            Dictionary of overlay visibility settings
        """
        return self.manager.get_document_overlays(doc_type)

    def save_document_overlays(self, doc_type: str, overlays: dict[str, bool]) -> None:
        """Save overlay settings for a document type.

        Args:
            doc_type: Document type
            overlays: Dictionary of overlay visibility settings
        """
        self.manager.save_document_overlays(doc_type, overlays)

        # Update model as well
        document_defaults = self.model.get_property("document_defaults", {})
        if doc_type in document_defaults:
            document_defaults[doc_type].update(overlays)
            self.model.set_property("document_defaults", document_defaults)

    def add_recent_file(
        self,
        file_path: str,
        document_type: str,
        num_pages: Optional[int],
        current_page: int,
        view_mode: str,
        zoom_level: float,
        overlays: dict[str, bool],
        presentation_mode: bool = False,
    ) -> None:
        """Add a file to the recent files list.

        Args:
            file_path: Path to the PDF file
            document_type: Type of document (interior, cover, dustjacket)
            num_pages: Number of pages (for covers/dustjackets)
            current_page: Current page being viewed
            view_mode: Current view mode (single, side_by_side)
            zoom_level: Current zoom level
            overlays: Current overlay visibility settings
            presentation_mode: Whether in presentation mode
        """
        from datetime import datetime

        file_info = {
            "path": file_path,
            "last_opened": datetime.now().isoformat(),
            "document_type": document_type,
            "num_pages": num_pages,
            "last_page": current_page,
            "view_mode": view_mode,
            "zoom_level": zoom_level,
            "overlays": overlays,
            "presentation_mode": presentation_mode,
        }

        self.manager.add_recent_file(file_info)

    def get_recent_files(self) -> list[dict[str, Any]]:
        """Get the list of recent files.

        Returns:
            List of recent file dictionaries
        """
        return self.manager.get_recent_files()

    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self.manager.clear_recent_files()

    def _on_config_changed(self, key: str) -> None:
        """Handle configuration change signal.

        Args:
            key: Configuration key that changed
        """
        logger.debug(f"Configuration changed: {key}")

        # Reload everything on full reset or batch update (indicated by "*")
        if key == "*":
            self.load_configuration()

"""Configuration management for Momovu application using PySide6 best practices."""

from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QMutex, QMutexLocker, QObject, QSettings, Signal

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class ConfigurationManager(QObject):
    """Central configuration management using PySide6 best practices."""

    # Signals for configuration changes
    config_changed = Signal(str)  # Emits the key that changed
    recent_files_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the configuration manager.

        Args:
            parent: Optional parent QObject for proper cleanup
        """
        super().__init__(parent)
        self.settings = QSettings()  # Uses app/org names set globally
        self.config_version = "1.0"
        self._write_mutex = QMutex()  # For thread safety
        self._batch_update_active = False  # Flag for batch updates
        self._pending_changes: set[str] = set()  # Track changed keys during batch

        # Check for first run
        if not self.settings.contains("config/version"):
            self._initialize_defaults()
        else:
            self._migrate_if_needed()

    def _initialize_defaults(self) -> None:
        """Initialize configuration with defaults on first run."""
        logger.info("Initializing configuration with defaults")

        self.settings.setValue("config/version", self.config_version)

        # Set default colors as strings for consistent serialization
        self.settings.beginGroup("colors")
        self.settings.setValue("margin_overlay/color", "#7F7FC1")
        self.settings.setValue("margin_overlay/opacity", 0.3)
        self.settings.setValue("barcode_area/color", "#FFFF00")
        self.settings.setValue("barcode_area/opacity", 0.5)
        self.settings.setValue("fold_lines/color", "#A41CAD")
        self.settings.setValue("fold_lines/opacity", 1.0)
        self.settings.setValue("trim_lines/color", "#000000")
        self.settings.setValue("trim_lines/opacity", 1.0)
        self.settings.setValue("bleed_lines/color", "#22B5F0")
        self.settings.setValue("bleed_lines/opacity", 1.0)
        self.settings.endGroup()

        # Set default line widths
        self.settings.beginGroup("line_widths")
        self.settings.setValue("fold_lines", 2)
        self.settings.setValue("trim_lines", 1)
        self.settings.setValue("bleed_lines", 1)
        self.settings.endGroup()

        # Set default preferences
        self.settings.beginGroup("preferences")
        self.settings.setValue("auto_fit_on_load", True)
        self.settings.setValue("auto_fit_on_resize", False)
        self.settings.setValue("remember_zoom_per_document", True)
        self.settings.setValue("smooth_scrolling", True)
        self.settings.setValue("scroll_speed", 50)
        self.settings.setValue("zoom_increment", 1.1)
        self.settings.setValue("cache/max_rendered_pages", 20)
        self.settings.setValue("cache/max_memory_mb", 300)
        self.settings.setValue("high_contrast_mode", False)
        self.settings.setValue("language", "")  # Empty string means use system locale
        self.settings.endGroup()

        # Set document type defaults
        for doc_type in ["interior", "cover", "dustjacket"]:
            self.settings.beginGroup(f"document_defaults/{doc_type}")
            self.settings.setValue("show_margins", True)
            self.settings.setValue("show_trim_lines", True)
            if doc_type in ["cover", "dustjacket"]:
                self.settings.setValue("show_barcode", True)
                self.settings.setValue("show_fold_lines", True)
                self.settings.setValue("show_bleed_lines", True)
                self.settings.setValue("default_num_pages", 100)
            self.settings.endGroup()

        self.settings.sync()  # Force write to disk
        logger.info("Default configuration initialized")

    def _migrate_if_needed(self) -> None:
        """Check and perform configuration migration if needed."""
        current_version = str(self.settings.value("config/version", "0.9"))
        if current_version < self.config_version:
            logger.info(
                f"Migrating configuration from {current_version} to {self.config_version}"
            )
            # Future migration logic would go here
            self.settings.setValue("config/version", self.config_version)
            self.settings.sync()

    def get_value(
        self, key: str, default: Any = None, type: Optional[type] = None
    ) -> Any:
        """Get value with automatic type conversion (PySide6 feature).

        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            type: Type to convert the value to

        Returns:
            The configuration value or default
        """
        if type:
            return self.settings.value(key, default, type=type)
        return self.settings.value(key, default)

    def set_value(self, key: str, value: Any) -> None:
        """Set value and emit change signal.

        Args:
            key: Configuration key
            value: Value to set
        """
        with QMutexLocker(self._write_mutex):
            old_value = self.settings.value(key)
            self.settings.setValue(key, value)
            if old_value != value:
                if self._batch_update_active:
                    # During batch update, just track the change
                    self._pending_changes.add(key)
                else:
                    # Normal operation - emit signal immediately
                    self.config_changed.emit(key)

    def add_recent_file(self, file_info: dict[str, Any]) -> None:
        """Add file to recent list with automatic cleanup.

        Args:
            file_info: Dictionary containing file metadata
        """
        with QMutexLocker(self._write_mutex):
            recent = self.get_recent_files()

            # Normalize the path to avoid duplicates
            file_path = file_info.get("path", "")
            if file_path:
                # Convert to absolute path and resolve symlinks
                normalized_path = str(Path(file_path).resolve())
                file_info["path"] = normalized_path

                # Remove existing entries with the same normalized path
                recent = [
                    f
                    for f in recent
                    if str(Path(f.get("path", "")).resolve()) != normalized_path
                ]
            else:
                # If no path, just remove by exact match
                recent = [f for f in recent if f.get("path") != file_path]

            # Add to beginning
            recent.insert(0, file_info)

            # Limit to 5 files
            recent = recent[:5]

            # Validate paths still exist
            validated_recent = []
            for file_data in recent:
                path = file_data.get("path", "")
                if path and Path(path).exists():
                    validated_recent.append(file_data)
                else:
                    logger.debug(f"Removing non-existent file from recent: {path}")

            # Save using array API
            self._save_recent_files(validated_recent)
            self.recent_files_changed.emit()

    def _save_recent_files(self, files: list[dict[str, Any]]) -> None:
        """Save recent files using QSettings array API.

        Args:
            files: List of file info dictionaries
        """
        self.settings.beginWriteArray("recent_files", len(files))
        for i, file_info in enumerate(files):
            self.settings.setArrayIndex(i)
            for key, value in file_info.items():
                if isinstance(value, dict):  # Handle nested overlays
                    self.settings.beginGroup(key)
                    for k, v in value.items():
                        self.settings.setValue(k, v)
                    self.settings.endGroup()
                else:
                    self.settings.setValue(key, value)
        self.settings.endArray()
        self.settings.sync()

    def get_recent_files(self) -> list[dict[str, Any]]:
        """Get recent files using QSettings array API.

        Returns:
            List of file info dictionaries
        """
        files = []
        size = self.settings.beginReadArray("recent_files")
        for i in range(size):
            self.settings.setArrayIndex(i)
            file_info = {
                "path": self.settings.value("path", ""),
                "last_opened": self.settings.value("last_opened", ""),
                "document_type": self.settings.value("document_type", "interior"),
                "num_pages": self.settings.value("num_pages", type=int),
                "last_page": self.settings.value("last_page", 0, type=int),
                "zoom_level": self.settings.value("zoom_level", 1.0, type=float),
                "view_mode": self.settings.value("view_mode", "single"),
            }

            # Read nested overlays
            self.settings.beginGroup("overlays")
            file_info["overlays"] = {
                "show_margins": self.settings.value("show_margins", True, type=bool),
                "show_trim_lines": self.settings.value(
                    "show_trim_lines", True, type=bool
                ),
                "show_barcode": self.settings.value("show_barcode", True, type=bool),
                "show_fold_lines": self.settings.value(
                    "show_fold_lines", True, type=bool
                ),
                "show_bleed_lines": self.settings.value(
                    "show_bleed_lines", True, type=bool
                ),
            }
            self.settings.endGroup()

            # Read presentation mode
            file_info["presentation_mode"] = self.settings.value(
                "presentation_mode", False, type=bool
            )

            files.append(file_info)
        self.settings.endArray()
        return files

    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        with QMutexLocker(self._write_mutex):
            self.settings.remove("recent_files")
            self.settings.sync()
            self.recent_files_changed.emit()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        with QMutexLocker(self._write_mutex):
            logger.info("Resetting configuration to defaults")
            self.settings.clear()
            self._initialize_defaults()
            self.config_changed.emit("*")  # Emit wildcard for full reset

    def get_config_file_path(self) -> str:
        """Get the actual configuration file path for debugging.

        Returns:
            Path to the configuration file
        """
        return self.settings.fileName()

    def is_writable(self) -> bool:
        """Check if configuration is writable.

        Returns:
            True if configuration can be written
        """
        return self.settings.isWritable()

    def get_status(self) -> QSettings.Status:
        """Get configuration status for error checking.

        Returns:
            QSettings status
        """
        return self.settings.status()

    def save_window_state(
        self, geometry: bytes, state: bytes, maximized: bool, fullscreen: bool
    ) -> None:
        """Save window state information.

        Args:
            geometry: Window geometry as bytes
            state: Window state as bytes
            maximized: Whether window is maximized
            fullscreen: Whether window is fullscreen
        """
        with QMutexLocker(self._write_mutex):
            self.settings.setValue("window/geometry", geometry)
            self.settings.setValue("window/state", state)
            self.settings.setValue("window/maximized", maximized)
            self.settings.setValue("window/fullscreen", fullscreen)
            self.settings.sync()

    def get_window_state(self) -> dict[str, Any]:
        """Get saved window state.

        Returns:
            Dictionary with window state information
        """
        return {
            "geometry": self.settings.value("window/geometry"),
            "state": self.settings.value("window/state"),
            "maximized": self.settings.value("window/maximized", False, type=bool),
            "fullscreen": self.settings.value("window/fullscreen", False, type=bool),
        }

    def save_document_overlays(self, doc_type: str, overlays: dict[str, bool]) -> None:
        """Save overlay settings for a document type.

        Args:
            doc_type: Document type (interior, cover, dustjacket)
            overlays: Dictionary of overlay visibility settings
        """
        with QMutexLocker(self._write_mutex):
            self.settings.beginGroup(f"document_defaults/{doc_type}")
            for key, value in overlays.items():
                self.settings.setValue(key, value)
            self.settings.endGroup()
            self.settings.sync()

    def get_document_overlays(self, doc_type: str) -> dict[str, bool]:
        """Get overlay settings for a document type.

        Args:
            doc_type: Document type (interior, cover, dustjacket)

        Returns:
            Dictionary of overlay visibility settings
        """
        overlays: dict[str, bool] = {}
        self.settings.beginGroup(f"document_defaults/{doc_type}")

        # Get all overlay settings with defaults
        overlays["show_margins"] = bool(
            self.settings.value("show_margins", True, type=bool)
        )
        overlays["show_trim_lines"] = bool(
            self.settings.value("show_trim_lines", True, type=bool)
        )

        if doc_type in ["cover", "dustjacket"]:
            overlays["show_barcode"] = bool(
                self.settings.value("show_barcode", True, type=bool)
            )
            overlays["show_fold_lines"] = bool(
                self.settings.value("show_fold_lines", True, type=bool)
            )
            overlays["show_bleed_lines"] = bool(
                self.settings.value("show_bleed_lines", True, type=bool)
            )

        self.settings.endGroup()
        return overlays

    def begin_batch_update(self) -> None:
        """Begin a batch update operation.

        During batch update, config_changed signals are suppressed until
        end_batch_update() is called. This prevents multiple signals during
        bulk configuration changes.
        """
        with QMutexLocker(self._write_mutex):
            self._batch_update_active = True
            self._pending_changes.clear()
            logger.debug("Batch update started")

    def end_batch_update(self) -> None:
        """End a batch update operation and emit a single change signal.

        This will emit a single config_changed signal with "*" to indicate
        multiple changes occurred, rather than individual signals for each change.
        """
        with QMutexLocker(self._write_mutex):
            if not self._batch_update_active:
                logger.warning("end_batch_update called without active batch")
                return

            self._batch_update_active = False

            # Sync settings to disk
            self.settings.sync()

            # If there were any changes, emit a single signal
            if self._pending_changes:
                logger.debug(
                    f"Batch update ended with {len(self._pending_changes)} changes"
                )
                self._pending_changes.clear()
                # Emit wildcard to indicate multiple changes
                self.config_changed.emit("*")
            else:
                logger.debug("Batch update ended with no changes")

    def get_available_languages(self) -> list[tuple[str, str]]:
        """Return list of available languages as (locale_code, display_name) tuples.

        Returns:
            List of tuples containing language code and display name
        """
        return [
            ("", "System Default"),  # Empty string means use system locale
            ("en", "English"),
            ("ar", "العربية"),  # Arabic
            ("bn", "বাংলা"),  # Bengali
            ("de", "Deutsch"),
            ("es", "Español"),
            ("fr", "Français"),
            ("hi", "हिन्दी"),  # Hindi
            ("id", "Bahasa Indonesia"),
            ("it", "Italiano"),
            ("ja", "日本語"),  # Japanese
            ("ko", "한국어"),  # Korean
            ("pl", "Polski"),
            ("pt", "Português"),
            ("ru", "Русский"),
            ("tr", "Türkçe"),
            ("zh", "中文"),  # Chinese
        ]

    def get_current_language(self) -> str:
        """Get the currently selected language code.

        Returns:
            Language code or empty string for system default
        """
        return str(self.get_value("preferences/language", ""))

    def set_language(self, language_code: str) -> None:
        """Set the application language.

        Args:
            language_code: Language code (e.g., 'en', 'es') or empty string for system default
        """
        self.set_value("preferences/language", language_code)

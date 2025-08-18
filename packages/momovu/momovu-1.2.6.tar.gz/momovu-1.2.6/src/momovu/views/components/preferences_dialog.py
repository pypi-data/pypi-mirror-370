"""Preferences dialog for Momovu application."""

from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class PreferencesDialog(QDialog):
    """Preferences dialog following PySide6 best practices."""

    preferences_changed = Signal()

    # Colorblind preset definitions
    COLORBLIND_PRESETS: dict[str, dict[str, dict[str, Any]]] = {
        "protanopia": {
            "margin_overlay": {"color": "#4A90E2", "opacity": 0.3},
            "barcode_area": {"color": "#FFD700", "opacity": 0.5},
            "fold_lines": {"color": "#2E7D32", "opacity": 1.0},
            "trim_lines": {"color": "#000000", "opacity": 1.0},
            "bleed_lines": {"color": "#1976D2", "opacity": 1.0},
        },
        "deuteranopia": {
            "margin_overlay": {"color": "#5E35B1", "opacity": 0.3},
            "barcode_area": {"color": "#FFC107", "opacity": 0.5},
            "fold_lines": {"color": "#7B1FA2", "opacity": 1.0},
            "trim_lines": {"color": "#000000", "opacity": 1.0},
            "bleed_lines": {"color": "#0288D1", "opacity": 1.0},
        },
        "tritanopia": {
            "margin_overlay": {"color": "#D32F2F", "opacity": 0.3},
            "barcode_area": {"color": "#FF6F00", "opacity": 0.5},
            "fold_lines": {"color": "#C2185B", "opacity": 1.0},
            "trim_lines": {"color": "#000000", "opacity": 1.0},
            "bleed_lines": {"color": "#388E3C", "opacity": 1.0},
        },
    }

    def __init__(
        self, config_manager: ConfigurationManager, parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the preferences dialog.

        Args:
            config_manager: Configuration manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle(self.tr("Preferences"))
        self.setModal(True)
        self.resize(600, 500)

        # Store original values for cancel
        self.original_values: dict[str, Any] = {}

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)

        # Tab widget for organized settings
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.tabs.addTab(self.create_general_tab(), self.tr("General"))
        self.tabs.addTab(self.create_language_tab(), self.tr("Language"))
        self.tabs.addTab(self.create_colors_tab(), self.tr("Colors"))
        self.tabs.addTab(self.create_recent_files_tab(), self.tr("Recent Files"))

        # Button box with Reset to Defaults prominently displayed
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Connect Reset to Defaults
        reset_button = button_box.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setToolTip(self.tr("Reset all settings to default values"))
        reset_button.setStyleSheet("QPushButton { font-weight: bold; color: #d40000; }")

        layout.addWidget(button_box)

    def create_general_tab(self) -> QWidget:
        """Create the general settings tab.

        Returns:
            Widget containing general settings
        """
        widget = QWidget()
        layout = QFormLayout(widget)

        # Auto-fit options
        self.auto_fit_load = QCheckBox(self.tr("Auto-fit on document load"))
        layout.addRow(self.tr("Fit Options:"), self.auto_fit_load)

        self.auto_fit_resize = QCheckBox(self.tr("Auto-fit on window resize"))
        layout.addRow("", self.auto_fit_resize)

        # Zoom settings
        self.zoom_increment = QDoubleSpinBox()
        self.zoom_increment.setRange(1.05, 2.00)
        self.zoom_increment.setSingleStep(0.05)
        self.zoom_increment.setDecimals(2)
        self.zoom_increment.setSuffix("x")
        layout.addRow(self.tr("Zoom Increment:"), self.zoom_increment)

        # Scroll settings
        self.smooth_scrolling = QCheckBox(self.tr("Enable smooth scrolling"))
        layout.addRow(self.tr("Scrolling:"), self.smooth_scrolling)

        self.scroll_speed = QSpinBox()
        self.scroll_speed.setRange(10, 200)
        self.scroll_speed.setSuffix(self.tr(" pixels"))
        layout.addRow(self.tr("Scroll Speed:"), self.scroll_speed)

        # Performance settings
        layout.addRow(QLabel(self.tr("<b>Performance</b>")))

        self.cache_max_pages = QSpinBox()
        self.cache_max_pages.setRange(5, 100)
        self.cache_max_pages.setSuffix(self.tr(" pages"))
        layout.addRow(self.tr("Max Cached Pages:"), self.cache_max_pages)

        self.cache_max_memory = QSpinBox()
        self.cache_max_memory.setRange(50, 1000)
        self.cache_max_memory.setSuffix(" MB")
        layout.addRow(self.tr("Max Cache Memory:"), self.cache_max_memory)

        return widget

    def create_colors_tab(self) -> QWidget:
        """Create the colors settings tab.

        Returns:
            Widget containing color settings
        """
        widget = QWidget()
        layout = QFormLayout(widget)

        # Color buttons for each overlay type
        self.color_buttons = {}
        self.opacity_spinboxes = {}

        overlay_types = [
            ("margin_overlay", self.tr("Margin Overlay")),
            ("barcode_area", self.tr("Barcode Area")),
            ("fold_lines", self.tr("Fold Lines")),
            ("trim_lines", self.tr("Trim Lines")),
            ("bleed_lines", self.tr("Bleed Lines")),
        ]

        for overlay_key, overlay_label in overlay_types:
            button = self.create_color_button(QColor("#000000"))
            button.clicked.connect(lambda _, t=overlay_key: self.choose_color(t))
            self.color_buttons[overlay_key] = button

            # Add opacity spinbox
            opacity_spin = QDoubleSpinBox()
            opacity_spin.setRange(0.0, 1.0)
            opacity_spin.setSingleStep(0.1)
            opacity_spin.setDecimals(1)
            self.opacity_spinboxes[overlay_key] = opacity_spin

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(button)
            row_layout.addWidget(QLabel(self.tr("Opacity:")))
            row_layout.addWidget(opacity_spin)
            row_layout.addStretch()

            layout.addRow(self.tr("{label}:").format(label=overlay_label), row_widget)

        # Line widths section
        layout.addRow(QLabel(self.tr("<b>Line Widths</b>")))

        self.line_width_spinboxes = {}
        line_types = [
            ("fold_lines", self.tr("Fold Lines")),
            ("trim_lines", self.tr("Trim Lines")),
            ("bleed_lines", self.tr("Bleed Lines")),
        ]

        for line_key, line_label in line_types:
            spinbox = QSpinBox()
            spinbox.setRange(1, 10)
            spinbox.setSuffix(" px")
            self.line_width_spinboxes[line_key] = spinbox
            layout.addRow(self.tr("{label}:").format(label=line_label), spinbox)

        # Add separator before preset buttons
        layout.addRow(QLabel(""))

        # Add colorblind preset buttons at the bottom
        preset_layout = QHBoxLayout()

        # Create and connect preset buttons
        protanopia_btn = QPushButton(self.tr("Protanopia"))
        protanopia_btn.setToolTip(
            self.tr("Apply colors optimized for red-blind vision")
        )
        protanopia_btn.clicked.connect(
            lambda: self.apply_colorblind_preset("protanopia")
        )
        preset_layout.addWidget(protanopia_btn)

        deuteranopia_btn = QPushButton(self.tr("Deuteranopia"))
        deuteranopia_btn.setToolTip(
            self.tr("Apply colors optimized for green-blind vision")
        )
        deuteranopia_btn.clicked.connect(
            lambda: self.apply_colorblind_preset("deuteranopia")
        )
        preset_layout.addWidget(deuteranopia_btn)

        tritanopia_btn = QPushButton(self.tr("Tritanopia"))
        tritanopia_btn.setToolTip(
            self.tr("Apply colors optimized for blue-blind vision")
        )
        tritanopia_btn.clicked.connect(
            lambda: self.apply_colorblind_preset("tritanopia")
        )
        preset_layout.addWidget(tritanopia_btn)

        preset_layout.addStretch()
        layout.addRow("", preset_layout)

        return widget

    def create_recent_files_tab(self) -> QWidget:
        """Create the recent files management tab.

        Returns:
            Widget containing recent files list
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info label
        info_label = QLabel(self.tr("Recently opened PDF files:"))
        layout.addWidget(info_label)

        # List of recent files
        self.recent_files_list = QListWidget()
        layout.addWidget(self.recent_files_list)

        # Buttons
        button_layout = QHBoxLayout()

        # Remove selected button
        self.remove_file_button = QPushButton(self.tr("Remove Selected"))
        self.remove_file_button.clicked.connect(self.remove_selected_file)
        self.remove_file_button.setEnabled(False)
        button_layout.addWidget(self.remove_file_button)

        button_layout.addStretch()

        # Clear all button
        clear_button = QPushButton(self.tr("Clear All Recent Files"))
        clear_button.clicked.connect(self.clear_recent_files)
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

        # Connect selection change
        self.recent_files_list.itemSelectionChanged.connect(
            self.on_recent_file_selection_changed
        )

        return widget

    def create_language_tab(self) -> QWidget:
        """Create the language settings tab.

        Returns:
            Widget containing language settings
        """
        widget = QWidget()
        layout = QFormLayout(widget)

        # Language selection
        self.language_combo = QComboBox()

        # Populate with available languages
        available_languages = self.config_manager.get_available_languages()
        current_language = self.config_manager.get_current_language()

        current_index = 0
        for i, (code, name) in enumerate(available_languages):
            self.language_combo.addItem(name, code)
            if code == current_language:
                current_index = i

        self.language_combo.setCurrentIndex(current_index)
        layout.addRow(self.tr("Interface Language:"), self.language_combo)

        # Add note about restart requirement
        restart_note = QLabel(
            self.tr(
                "<i>Note: Changing the language requires restarting the application.</i>"
            )
        )
        restart_note.setWordWrap(True)
        layout.addRow("", restart_note)

        # Add language info
        info_label = QLabel(
            self.tr(
                "<b>Supported Languages:</b><br>"
                "• Right-to-left languages (Arabic) are fully supported<br>"
                "• CJK languages (Chinese, Japanese, Korean) use system fonts<br>"
                "• All number and date formatting follows the selected locale"
            )
        )
        info_label.setWordWrap(True)
        layout.addRow("", info_label)

        return widget

    def create_color_button(self, color: QColor) -> QPushButton:
        """Create a color picker button with preview.

        Args:
            color: Initial color

        Returns:
            Color picker button
        """
        button = QPushButton()
        button.setFixedSize(50, 25)
        self.update_color_button(button, color)
        return button

    def update_color_button(self, button: QPushButton, color: QColor) -> None:
        """Update button appearance to show color.

        Args:
            button: Button to update
            color: Color to display
        """
        pixmap = QPixmap(48, 23)
        pixmap.fill(color)
        button.setIcon(pixmap)
        button.setIconSize(pixmap.size())
        # Store the color as a property for later retrieval
        button.setProperty("color", color)

    def choose_color(self, overlay_type: str) -> None:
        """Open color dialog for the specified overlay type.

        Args:
            overlay_type: Type of overlay to set color for
        """
        current_color_str = self.config_manager.get_value(
            f"colors/{overlay_type}/color", "#000000"
        )
        if isinstance(current_color_str, QColor):
            current_color = current_color_str
        else:
            current_color = QColor(current_color_str)

        # Use the main window as parent instead of self to avoid nested modal issues
        # This helps prevent paint event problems when dialogs are stacked
        parent_window = self.parent() if isinstance(self.parent(), QWidget) else self

        # Create color dialog with proper parent
        color = QColorDialog.getColor(
            current_color,
            parent_window,  # type: ignore[arg-type]
            self.tr("Choose {type} Color").format(
                type=overlay_type.replace("_", " ").title()
            ),
        )

        if color.isValid():
            self.update_color_button(self.color_buttons[overlay_type], color)
            # Force an update to ensure the button displays correctly
            self.color_buttons[overlay_type].update()

    def apply_colorblind_preset(self, preset_name: str) -> None:
        """Apply a colorblind preset to all color settings.

        Args:
            preset_name: Name of the preset to apply (protanopia, deuteranopia, or tritanopia)
        """
        if preset_name not in self.COLORBLIND_PRESETS:
            logger.warning(f"Unknown colorblind preset: {preset_name}")
            return

        preset = self.COLORBLIND_PRESETS[preset_name]
        logger.info(f"Applying colorblind preset: {preset_name}")

        # Update each color button and opacity spinbox
        for overlay_type, settings in preset.items():
            if overlay_type in self.color_buttons:
                # Update color button
                color = QColor(settings["color"])
                self.update_color_button(self.color_buttons[overlay_type], color)

                # Update opacity spinbox
                if overlay_type in self.opacity_spinboxes:
                    opacity_value = settings["opacity"]
                    if isinstance(opacity_value, (int, float)):
                        self.opacity_spinboxes[overlay_type].setValue(
                            float(opacity_value)
                        )

        logger.debug(f"Colorblind preset {preset_name} applied successfully")

    def on_recent_file_selection_changed(self) -> None:
        """Handle recent file selection change."""
        self.remove_file_button.setEnabled(
            len(self.recent_files_list.selectedItems()) > 0
        )

    def remove_selected_file(self) -> None:
        """Remove the selected file from recent files."""
        selected_items = self.recent_files_list.selectedItems()
        if not selected_items:
            return

        # Get current recent files
        recent_files = self.config_manager.get_recent_files()

        # Remove selected file
        selected_index = self.recent_files_list.row(selected_items[0])
        if 0 <= selected_index < len(recent_files):
            del recent_files[selected_index]

            # Save updated list
            self.config_manager._save_recent_files(recent_files)
            self.config_manager.recent_files_changed.emit()

            # Refresh list
            self.load_recent_files()

    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        reply = QMessageBox.question(
            self,
            self.tr("Clear Recent Files"),
            self.tr("Are you sure you want to clear all recent files?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.clear_recent_files()
            self.recent_files_list.clear()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults with confirmation."""
        reply = QMessageBox.question(
            self,
            self.tr("Reset to Defaults"),
            self.tr(
                "Are you sure you want to reset all settings to their default values?\n\nThis action cannot be undone."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            self.load_settings()  # Reload UI with defaults

            # Show success message before emitting signal
            QMessageBox.information(
                self,
                self.tr("Settings Reset"),
                self.tr("All settings have been reset to their default values."),
            )

            self.preferences_changed.emit()

    def load_settings(self) -> None:
        """Load current settings into the dialog."""
        # Store original values
        self.original_values = {}

        # Load general settings
        self.auto_fit_load.setChecked(
            self.config_manager.get_value(
                "preferences/auto_fit_on_load", True, type=bool
            )
        )
        self.auto_fit_resize.setChecked(
            self.config_manager.get_value(
                "preferences/auto_fit_on_resize", False, type=bool
            )
        )
        self.zoom_increment.setValue(
            self.config_manager.get_value("preferences/zoom_increment", 1.1, type=float)
        )
        self.smooth_scrolling.setChecked(
            self.config_manager.get_value(
                "preferences/smooth_scrolling", True, type=bool
            )
        )
        self.scroll_speed.setValue(
            self.config_manager.get_value("preferences/scroll_speed", 50, type=int)
        )
        self.cache_max_pages.setValue(
            self.config_manager.get_value(
                "preferences/cache/max_rendered_pages", 20, type=int
            )
        )
        self.cache_max_memory.setValue(
            self.config_manager.get_value(
                "preferences/cache/max_memory_mb", 300, type=int
            )
        )

        # Load color settings
        for overlay_type in self.color_buttons:
            color_str = self.config_manager.get_value(
                f"colors/{overlay_type}/color", "#000000"
            )
            color = color_str if isinstance(color_str, QColor) else QColor(color_str)
            self.update_color_button(self.color_buttons[overlay_type], color)

            opacity = self.config_manager.get_value(
                f"colors/{overlay_type}/opacity", 1.0, type=float
            )
            self.opacity_spinboxes[overlay_type].setValue(opacity)

        # Load line width settings
        for line_type in self.line_width_spinboxes:
            width = self.config_manager.get_value(
                f"line_widths/{line_type}", 1, type=int
            )
            self.line_width_spinboxes[line_type].setValue(width)

        # Load recent files
        self.load_recent_files()

    def load_recent_files(self) -> None:
        """Load recent files into the list widget."""
        self.recent_files_list.clear()
        recent_files = self.config_manager.get_recent_files()

        for file_info in recent_files:
            path = file_info.get("path", "")
            if path:
                filename = Path(path).name
                doc_type = file_info.get("document_type", "")
                item_text = f"{filename} ({doc_type})" if doc_type else filename

                self.recent_files_list.addItem(item_text)

    def save_settings(self) -> None:
        """Save settings from the dialog using batch update to prevent signal spam."""
        # Start batch update to suppress individual config_changed signals
        self.config_manager.begin_batch_update()

        try:
            # Save general settings
            self.config_manager.set_value(
                "preferences/auto_fit_on_load", self.auto_fit_load.isChecked()
            )
            self.config_manager.set_value(
                "preferences/auto_fit_on_resize", self.auto_fit_resize.isChecked()
            )
            self.config_manager.set_value(
                "preferences/zoom_increment", self.zoom_increment.value()
            )
            self.config_manager.set_value(
                "preferences/smooth_scrolling", self.smooth_scrolling.isChecked()
            )
            self.config_manager.set_value(
                "preferences/scroll_speed", self.scroll_speed.value()
            )
            self.config_manager.set_value(
                "preferences/cache/max_rendered_pages", self.cache_max_pages.value()
            )
            self.config_manager.set_value(
                "preferences/cache/max_memory_mb", self.cache_max_memory.value()
            )

            # Save color settings - ALWAYS save as string to avoid serialization issues
            for overlay_type in self.color_buttons:
                # Get color from button property (more reliable than extracting from icon)
                button = self.color_buttons[overlay_type]
                color = button.property("color")

                # Ensure we have a valid QColor
                if not color or not isinstance(color, QColor):
                    logger.warning(
                        f"Color property not found for {overlay_type}, using black as fallback"
                    )
                    color = QColor("#000000")

                # Always save color as string to prevent QSettings serialization issues
                color_string = color.name()
                self.config_manager.set_value(
                    f"colors/{overlay_type}/color", color_string
                )
                self.config_manager.set_value(
                    f"colors/{overlay_type}/opacity",
                    self.opacity_spinboxes[overlay_type].value(),
                )

            # Save line width settings
            for line_type in self.line_width_spinboxes:
                self.config_manager.set_value(
                    f"line_widths/{line_type}",
                    self.line_width_spinboxes[line_type].value(),
                )

            # Save language preference
            selected_language = self.language_combo.currentData()
            current_language = self.config_manager.get_current_language()
            if selected_language != current_language:
                self.config_manager.set_language(selected_language)
                # Show restart dialog
                QTimer.singleShot(100, self._show_restart_dialog)

        finally:
            # End batch update to emit a single config_changed signal
            self.config_manager.end_batch_update()

    def _show_restart_dialog(self) -> None:
        """Show dialog informing user to restart for language change."""
        parent: QWidget = self if not isinstance(self.parent(), QWidget) else self.parent()  # type: ignore[assignment]
        QMessageBox.information(
            parent,
            self.tr("Restart Required"),
            self.tr(
                "The language change will take effect after restarting the application."
            ),
            QMessageBox.StandardButton.Ok,
        )

    def accept(self) -> None:
        """Accept the dialog and save settings with proper cleanup."""
        # Save settings first (using batch update)
        self.save_settings()

        # Save and close dialog before emitting signal to avoid accessing deleted objects
        should_emit = True
        super().accept()

        # Emit signal after dialog is closed
        if should_emit:
            # Small delay ensures Qt cleanup is complete
            QTimer.singleShot(10, self.preferences_changed.emit)

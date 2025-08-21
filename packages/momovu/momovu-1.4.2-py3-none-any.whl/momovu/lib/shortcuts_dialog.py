"""Keyboard shortcuts dialog for Momovu.

This module provides a dialog that displays all available keyboard shortcuts
to help users learn and use the application more efficiently.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.constants import (
    SHORTCUTS_DIALOG_HEIGHT,
    SHORTCUTS_DIALOG_WIDTH,
    SHORTCUTS_TABLE_COLUMNS,
)


class ShortcutsDialog(QDialog):
    """Dialog displaying all keyboard shortcuts."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the shortcuts dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Keyboard Shortcuts"))
        self.setModal(True)
        self.resize(SHORTCUTS_DIALOG_WIDTH, SHORTCUTS_DIALOG_HEIGHT)

        self._setup_ui()
        self._populate_shortcuts()

    def _setup_ui(self) -> None:
        """Build table widget with category/action/shortcut columns."""
        layout = QVBoxLayout(self)

        # Title label
        title = QLabel(self.tr("Keyboard Shortcuts"))
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Shortcuts table
        self.table = QTableWidget()
        self.table.setColumnCount(SHORTCUTS_TABLE_COLUMNS)
        self.table.setHorizontalHeaderLabels(
            [self.tr("Category"), self.tr("Action"), self.tr("Shortcut")]
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Hide row numbers (vertical header)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _populate_shortcuts(self) -> None:
        """Fill table with all available keyboard shortcuts.

        NOTE: Keep this list synchronized with keyboard handling in
        views/components/graphics_view.py::keyPressEvent()
        """
        shortcuts = [
            # File operations
            (self.tr("File"), self.tr("Open Document"), "Ctrl+O"),
            (self.tr("File"), self.tr("Close Document"), "Ctrl+W"),
            (self.tr("File"), self.tr("Exit Application"), "Ctrl+Q"),
            # Navigation
            (self.tr("Navigation"), self.tr("Next Page"), "Page Down"),
            (self.tr("Navigation"), self.tr("Next Page (alternative)"), "Space"),
            (self.tr("Navigation"), self.tr("Previous Page"), "Page Up"),
            (
                self.tr("Navigation"),
                self.tr("Previous Page (alternative)"),
                "Shift+Space",
            ),
            (self.tr("Navigation"), self.tr("First Page"), "Home"),
            (self.tr("Navigation"), self.tr("Last Page"), "End"),
            (self.tr("Navigation"), self.tr("Go to Page (Interior only)"), "Ctrl+G"),
            (self.tr("Navigation"), self.tr("Navigate with Arrow Keys"), ""),
            (
                self.tr("Navigation"),
                self.tr("  • When zoomed"),
                self.tr("Arrow Keys = Pan document"),
            ),
            (
                self.tr("Navigation"),
                self.tr("  • Interior (not zoomed)"),
                self.tr("Left/Right = Previous/Next page"),
            ),
            (
                self.tr("Navigation"),
                self.tr("  • Cover/Dustjacket"),
                self.tr("Arrow Keys = No action"),
            ),
            (self.tr("Navigation"), self.tr("Navigate Pages"), "Mouse Wheel"),
            # View modes
            (self.tr("View"), self.tr("Fullscreen"), "F11"),
            (self.tr("View"), self.tr("Presentation Mode"), "F5"),
            (self.tr("View"), self.tr("Exit Presentation/Fullscreen"), "Escape"),
            (self.tr("View"), self.tr("Side by Side View"), "Ctrl+D"),
            # Document
            (self.tr("Document"), self.tr("Spine Width Calculator"), "Ctrl+K"),
            # Display options
            (self.tr("Display"), self.tr("Show/Hide Margins"), "Ctrl+M"),
            (self.tr("Display"), self.tr("Show/Hide Trim Lines"), "Ctrl+T"),
            (
                self.tr("Display"),
                self.tr("Show/Hide Barcode"),
                self.tr("Ctrl+B (Cover/Dustjacket only)"),
            ),
            (self.tr("Display"), self.tr("Show/Hide Fold Lines"), "Ctrl+L"),
            (
                self.tr("Display"),
                self.tr("Show/Hide Bleed Lines"),
                self.tr("Ctrl+R (Cover/Dustjacket only)"),
            ),
            (
                self.tr("Display"),
                self.tr("Show/Hide Gutter"),
                self.tr("Ctrl+U (Interior only)"),
            ),
            # Zoom
            (self.tr("Zoom"), self.tr("Zoom In"), "Ctrl+Plus / Ctrl+="),
            (self.tr("Zoom"), self.tr("Zoom Out"), "Ctrl+Minus"),
            (self.tr("Zoom"), self.tr("Fit to Page"), "Ctrl+0"),
            (self.tr("Zoom"), self.tr("Fit to Page (alternative)"), "Ctrl+F"),
            (self.tr("Zoom"), self.tr("Zoom with Mouse"), "Ctrl+Mouse Wheel"),
            # Help
            (self.tr("Help"), self.tr("Show Keyboard Shortcuts"), "F1 / ?"),
            (self.tr("Help"), self.tr("About"), ""),
        ]

        self.table.setRowCount(len(shortcuts))

        for row, (category, action, shortcut) in enumerate(shortcuts):
            # Category column
            category_item = QTableWidgetItem(category)
            category_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 0, category_item)

            # Action column
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.table.setItem(row, 1, action_item)

            # Shortcut column
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Make shortcut text bold
            font = shortcut_item.font()
            font.setBold(True)
            shortcut_item.setFont(font)
            self.table.setItem(row, 2, shortcut_item)

        # Adjust row heights for better readability
        self.table.resizeRowsToContents()

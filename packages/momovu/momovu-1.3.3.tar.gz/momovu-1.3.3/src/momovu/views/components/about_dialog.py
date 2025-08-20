"""About dialog component for the Momovu application.

This module provides a dedicated About dialog that displays application
information, version details, and links to resources.
"""

import sys
from typing import Optional

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from momovu._version import __version__
from momovu.lib.constants import (
    ABOUT_DIALOG_MIN_WIDTH,
    TITLE_FONT_SIZE,
    VERSION_FONT_SIZE,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class AboutDialog(QDialog):
    """About dialog showing application information and version details."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the About dialog.

        Args:
            parent: Parent widget for the dialog
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("About Momovu"))
        self.setModal(True)
        self.setMinimumWidth(ABOUT_DIALOG_MIN_WIDTH)
        self._setup_ui()
        logger.debug("About dialog initialized")

    def _setup_ui(self) -> None:
        """Build dialog layout with app info, features, and system details."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title and version
        title_label = QLabel(self.tr("<h2>Momovu</h2>"))
        title_font = QFont()
        title_font.setPointSize(TITLE_FONT_SIZE)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel(self.tr("Version {version}").format(version=__version__))
        version_font = QFont()
        version_font.setPointSize(VERSION_FONT_SIZE)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Description
        description_label = QLabel(
            self.tr(
                "A PDF viewer for book publishing workflows.\n\n"
                "Preview and validate book layouts with precise margin visualization, "
                "trim lines, and specialized viewing modes for interior pages, covers, "
                "and dust jackets."
            )
        )
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        # Features
        features_text = self.tr(
            """<p><b>Features:</b></p>
        <ul>
        <li>Interior, Cover, and Dustjacket viewing modes</li>
        <li>Margin and trim line visualization</li>
        <li>Side-by-side page viewing</li>
        <li>Presentation mode</li>
        <li>Barcode area display</li>
        <li>Fold line indicators</li>
        </ul>"""
        )
        features_label = QLabel(features_text)
        features_label.setWordWrap(True)
        layout.addWidget(features_label)

        # Links
        links_text = self.tr(
            """<p><b>Links:</b></p>
        <p>• Main page: <a href="https://momovu.org">https://momovu.org</a></p>
        <p>• Source code: <a href="https://spacecruft.org/books/momovu">https://spacecruft.org/books/momovu</a></p>"""
        )
        links_label = QLabel(links_text)
        links_label.setOpenExternalLinks(True)
        links_label.setWordWrap(True)
        layout.addWidget(links_label)

        # System information
        system_info_text = self.tr(
            """<p><b>System Information:</b></p>
        <p>• Python version: {python_version}</p>
        <p>• PySide6 version: {pyside_version}</p>"""
        ).format(python_version=sys.version.split()[0], pyside_version=pyside_version)
        system_info_label = QLabel(system_info_text)
        system_info_label.setWordWrap(True)
        layout.addWidget(system_info_label)

        # Copyright and license
        copyright_text = self.tr(
            """<p><b>Legal:</b></p>
        <p>Copyright © 2025 Jeff Moe<br>
        Licensed under the Apache License, Version 2.0</p>"""
        )
        copyright_label = QLabel(copyright_text)
        copyright_label.setWordWrap(True)
        layout.addWidget(copyright_label)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Set focus to OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()

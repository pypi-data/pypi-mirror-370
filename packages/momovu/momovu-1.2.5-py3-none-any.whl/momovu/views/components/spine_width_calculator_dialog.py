"""Spine width calculator dialog for book production.

This dialog allows users to calculate spine width based on page count
and document type (cover or dustjacket).
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from momovu.lib.logger import get_logger
from momovu.lib.sizes.dustjacket_spine_widths import get_dustjacket_spine_width

logger = get_logger(__name__)


def format_spine_width(width: float) -> str:
    """Format spine width removing unnecessary trailing zeros.

    Args:
        width: Spine width in millimeters

    Returns:
        Formatted string without trailing zeros
    """
    # Format to 3 decimal places, then remove trailing zeros
    formatted = f"{width:.3f}".rstrip("0").rstrip(".")
    return formatted


# Constants for spine width calculation
LULU_SPINE_FACTOR = 0.0572  # mm per page for Lulu's formula
MINIMUM_SPINE_WIDTH_MM = 6.35  # 0.25 inches minimum
MINIMUM_COVER_PAGES = 32  # Minimum pages for paperback covers


def calculate_cover_spine_width(page_count: int) -> float:
    """Calculate spine width for covers using Lulu's formula.

    Args:
        page_count: Number of pages in the book

    Returns:
        Spine width in millimeters, rounded to 3 decimal places
    """
    calculated_width = page_count * LULU_SPINE_FACTOR
    # Apply minimum spine width constraint
    final_width = max(calculated_width, MINIMUM_SPINE_WIDTH_MM)
    return round(final_width, 3)


class SpineWidthCalculatorDialog(QDialog):
    """Dialog for calculating spine width based on page count and document type."""

    def __init__(
        self, parent: Optional[QWidget] = None, initial_pages: int = 100
    ) -> None:
        """Initialize the spine width calculator dialog.

        Args:
            parent: Parent widget for the dialog
            initial_pages: Initial page count to display
        """
        super().__init__(parent)
        self.setWindowTitle(self.tr("Spine Width Calculator"))
        self.setModal(True)
        self.setFixedWidth(400)
        self.initial_pages = initial_pages

        self._setup_ui()
        self._connect_signals()

        # Calculate initial value
        self._calculate_spine_width()

        logger.debug(
            f"Spine width calculator dialog initialized with {initial_pages} pages"
        )

    def _setup_ui(self) -> None:
        """Build the dialog layout with input controls and result display."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            self.tr(
                "Calculate spine width based on page count and document type.\n"
                "Enter the number of pages and select the document type."
            )
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Page count input
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel(self.tr("Number of Pages:")))

        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(999)
        self.page_spinbox.setValue(self.initial_pages)
        self.page_spinbox.setToolTip(self.tr("Enter the total number of pages (1-999)"))
        page_layout.addWidget(self.page_spinbox)
        page_layout.addStretch()

        layout.addLayout(page_layout)

        # Document type selection
        type_group = QGroupBox(self.tr("Document Type"))
        type_layout = QVBoxLayout()

        self.cover_radio = QRadioButton(self.tr("Cover"))
        self.cover_radio.setChecked(True)  # Default selection
        type_layout.addWidget(self.cover_radio)

        self.dustjacket_radio = QRadioButton(self.tr("Dustjacket"))
        type_layout.addWidget(self.dustjacket_radio)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Result display
        result_group = QGroupBox(self.tr("Calculated Spine Width"))
        result_layout = QVBoxLayout()

        self.result_label = QLabel(
            self.tr("Spine Width: {width}mm").format(width="0.000")
        )
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.result_label)

        # Additional info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.info_label)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        # Set focus to OK button
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFocus()

    def _connect_signals(self) -> None:
        """Connect UI signals to calculation method."""
        self.page_spinbox.valueChanged.connect(self._calculate_spine_width)
        self.cover_radio.toggled.connect(self._calculate_spine_width)
        self.dustjacket_radio.toggled.connect(self._calculate_spine_width)

    def _calculate_spine_width(self) -> None:
        """Calculate and display spine width based on current inputs."""
        page_count = self.page_spinbox.value()

        if self.cover_radio.isChecked():
            # Check minimum page count for covers
            if page_count < MINIMUM_COVER_PAGES:
                self.info_label.setText(
                    self.tr("Minimum {pages} pages required for covers").format(
                        pages=MINIMUM_COVER_PAGES
                    )
                )
                self.result_label.setText(self.tr("Spine Width: --"))
                return

            # Use Lulu formula for covers
            spine_width = calculate_cover_spine_width(page_count)
            self.info_label.setText("")
        else:
            # Use lookup table for dustjackets
            if page_count < 24 or page_count > 800:
                self.info_label.setText(
                    self.tr("Note: Page count outside standard range")
                )
                self.result_label.setText(self.tr("Spine Width: --"))
                return
            else:
                spine_width = get_dustjacket_spine_width(page_count)
                self.info_label.setText("")

        # Update result display with proper formatting
        formatted_width = format_spine_width(spine_width)
        self.result_label.setText(
            self.tr("Spine Width: {width}mm").format(width=formatted_width)
        )

        logger.debug(
            f"Calculated spine width: {spine_width}mm for {page_count} pages "
            f"({'cover' if self.cover_radio.isChecked() else 'dustjacket'})"
        )

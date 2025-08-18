"""Unit tests for spine width calculator functionality."""

import pytest
from PySide6.QtWidgets import QApplication

from momovu.lib.sizes.dustjacket_spine_widths import get_dustjacket_spine_width
from momovu.views.components.spine_width_calculator_dialog import (
    SpineWidthCalculatorDialog,
    calculate_cover_spine_width,
    format_spine_width,
)


class TestSpineWidthFormatting:
    """Test the spine width formatting function."""

    def test_remove_trailing_zeros(self):
        """Test that trailing zeros are removed."""
        assert format_spine_width(6.000) == "6"
        assert format_spine_width(6.100) == "6.1"
        assert format_spine_width(6.120) == "6.12"
        assert format_spine_width(6.123) == "6.123"

    def test_whole_numbers(self):
        """Test that whole numbers don't show decimal point."""
        assert format_spine_width(6.0) == "6"
        assert format_spine_width(27.0) == "27"
        assert format_spine_width(100.0) == "100"

    def test_various_decimals(self):
        """Test various decimal cases."""
        assert format_spine_width(31.860) == "31.86"
        assert format_spine_width(11.440) == "11.44"
        assert format_spine_width(6.350) == "6.35"
        assert format_spine_width(28.600) == "28.6"
        assert format_spine_width(57.143) == "57.143"


class TestCoverSpineWidthCalculation:
    """Test the cover spine width calculation using Lulu's formula."""

    def test_basic_calculation(self):
        """Test basic spine width calculation."""
        # 100 pages * 0.0572 = 5.72mm, but minimum is 6.35mm
        assert calculate_cover_spine_width(100) == 6.350

        # 200 pages * 0.0572 = 11.44mm
        assert calculate_cover_spine_width(200) == 11.440

        # 500 pages * 0.0572 = 28.6mm
        assert calculate_cover_spine_width(500) == 28.600

    def test_minimum_spine_width(self):
        """Test that minimum spine width is enforced."""
        # Small page counts should return minimum 6.35mm
        assert calculate_cover_spine_width(1) == 6.350
        assert calculate_cover_spine_width(50) == 6.350  # 2.86mm -> 6.35mm
        assert calculate_cover_spine_width(110) == 6.350  # 6.292mm -> 6.35mm

        # 112 pages * 0.0572 = 6.4064mm (just above minimum)
        assert calculate_cover_spine_width(112) == 6.406

        # 120 pages * 0.0572 = 6.864mm (above minimum)
        assert calculate_cover_spine_width(120) == 6.864

    def test_rounding(self):
        """Test that results are rounded to 3 decimal places."""
        # 175 pages * 0.0572 = 10.01mm
        assert calculate_cover_spine_width(175) == 10.010

        # 176 pages * 0.0572 = 10.0672mm
        assert calculate_cover_spine_width(176) == 10.067

        # 999 pages * 0.0572 = 57.1428mm
        assert calculate_cover_spine_width(999) == 57.143

    def test_edge_cases(self):
        """Test edge cases for page count."""
        # Minimum page count
        assert calculate_cover_spine_width(1) == 6.350

        # Maximum page count in dialog (999)
        assert calculate_cover_spine_width(999) == 57.143

        # Even larger page counts should still work
        assert calculate_cover_spine_width(1000) == 57.200
        assert calculate_cover_spine_width(2000) == 114.400


class TestDustjacketSpineWidth:
    """Test the dustjacket spine width table lookup."""

    def test_table_ranges(self):
        """Test various page count ranges from the table."""
        # First range: 24-84 pages -> 6mm
        assert get_dustjacket_spine_width(24) == 6.0
        assert get_dustjacket_spine_width(50) == 6.0
        assert get_dustjacket_spine_width(84) == 6.0

        # Second range: 85-140 pages -> 13mm
        assert get_dustjacket_spine_width(85) == 13.0
        assert get_dustjacket_spine_width(100) == 13.0
        assert get_dustjacket_spine_width(140) == 13.0

        # Middle range: 335-360 pages -> 27mm
        assert get_dustjacket_spine_width(335) == 27.0
        assert get_dustjacket_spine_width(350) == 27.0
        assert get_dustjacket_spine_width(360) == 27.0

        # Last range: 779-799 pages -> 52mm
        assert get_dustjacket_spine_width(779) == 52.0
        assert get_dustjacket_spine_width(790) == 52.0
        assert get_dustjacket_spine_width(799) == 52.0

        # Exact 800 pages -> 54mm
        assert get_dustjacket_spine_width(800) == 54.0

    def test_out_of_range(self):
        """Test page counts outside the table range."""
        # Below minimum (< 24)
        assert get_dustjacket_spine_width(1) == 6.0
        assert get_dustjacket_spine_width(10) == 6.0
        assert get_dustjacket_spine_width(23) == 6.0

        # Above maximum (> 800)
        assert get_dustjacket_spine_width(801) == 6.0
        assert get_dustjacket_spine_width(999) == 6.0
        assert get_dustjacket_spine_width(1000) == 6.0

    def test_boundary_values(self):
        """Test boundary values between ranges."""
        # 84/85 boundary
        assert get_dustjacket_spine_width(84) == 6.0
        assert get_dustjacket_spine_width(85) == 13.0

        # 140/141 boundary
        assert get_dustjacket_spine_width(140) == 13.0
        assert get_dustjacket_spine_width(141) == 16.0

        # 499/500/501 boundaries
        assert get_dustjacket_spine_width(499) == 35.0
        assert get_dustjacket_spine_width(500) == 35.0
        assert get_dustjacket_spine_width(501) == 37.0


class TestSpineWidthCalculatorDialog:
    """Test the spine width calculator dialog functionality."""

    @pytest.fixture
    def app(self, qtbot):
        """Create QApplication for testing."""
        return QApplication.instance() or QApplication([])

    @pytest.fixture
    def dialog(self, qtbot, app):
        """Create a dialog instance for testing."""
        dialog = SpineWidthCalculatorDialog(initial_pages=100)
        qtbot.addWidget(dialog)
        return dialog

    def test_dialog_creation(self, dialog):
        """Test that dialog is created properly."""
        assert dialog.windowTitle() == "Spine Width Calculator"
        assert dialog.isModal()
        assert dialog.page_spinbox.minimum() == 1
        assert dialog.page_spinbox.maximum() == 999
        assert dialog.page_spinbox.value() == 100

    def test_initial_pages_parameter(self, qtbot, app):
        """Test that initial pages parameter works correctly."""
        # Test with different initial values
        dialog1 = SpineWidthCalculatorDialog(initial_pages=250)
        qtbot.addWidget(dialog1)
        assert dialog1.page_spinbox.value() == 250

        dialog2 = SpineWidthCalculatorDialog(initial_pages=500)
        qtbot.addWidget(dialog2)
        assert dialog2.page_spinbox.value() == 500

    def test_default_selection(self, dialog):
        """Test default document type selection."""
        assert dialog.cover_radio.isChecked()
        assert not dialog.dustjacket_radio.isChecked()

    def test_cover_calculation_in_dialog(self, dialog, qtbot):
        """Test cover spine width calculation through dialog."""
        # Set page count
        dialog.page_spinbox.setValue(200)

        # Ensure cover is selected
        dialog.cover_radio.setChecked(True)

        # Check result (trailing zeros removed)
        assert "11.44mm" in dialog.result_label.text()
        # Info label should be empty for normal calculations
        assert dialog.info_label.text() == ""

    def test_dustjacket_calculation_in_dialog(self, dialog, qtbot):
        """Test dustjacket spine width calculation through dialog."""
        # Set page count
        dialog.page_spinbox.setValue(350)

        # Select dustjacket
        dialog.dustjacket_radio.setChecked(True)

        # Check result (dustjacket shows as integer when whole number)
        assert "27mm" in dialog.result_label.text()
        # Info label should be empty for normal range
        assert dialog.info_label.text() == ""

    def test_minimum_spine_display(self, dialog, qtbot):
        """Test minimum spine width display in dialog."""
        # Set page count that meets minimum but has minimum spine width
        dialog.page_spinbox.setValue(100)

        # Ensure cover is selected
        dialog.cover_radio.setChecked(True)

        # Check result shows minimum (trailing zero removed)
        assert "6.35mm" in dialog.result_label.text()
        # Info label should be empty for normal calculations
        assert dialog.info_label.text() == ""

    def test_cover_minimum_pages(self, dialog, qtbot):
        """Test minimum page requirement for covers."""
        # Set page count below minimum
        dialog.page_spinbox.setValue(10)

        # Ensure cover is selected
        dialog.cover_radio.setChecked(True)

        # Check no width is shown
        assert dialog.result_label.text() == "Spine Width: --"
        assert "Minimum 32 pages required for covers" in dialog.info_label.text()

        # Test at exactly 32 pages
        dialog.page_spinbox.setValue(32)
        assert "Spine Width: --" not in dialog.result_label.text()
        assert "6.35mm" in dialog.result_label.text()  # Should show minimum spine width

    def test_out_of_range_dustjacket_display(self, dialog, qtbot):
        """Test out of range message for dustjacket."""
        # Set page count outside table range
        dialog.page_spinbox.setValue(999)

        # Select dustjacket
        dialog.dustjacket_radio.setChecked(True)

        # Check result shows no width for out of range
        assert dialog.result_label.text() == "Spine Width: --"
        assert "Note: Page count outside standard range" in dialog.info_label.text()

    def test_dynamic_update(self, dialog, qtbot):
        """Test that changing inputs updates the result dynamically."""
        # Initial state
        dialog.page_spinbox.setValue(100)
        dialog.cover_radio.setChecked(True)
        initial_result = dialog.result_label.text()

        # Change page count
        dialog.page_spinbox.setValue(500)
        assert dialog.result_label.text() != initial_result
        assert "28.6mm" in dialog.result_label.text()  # Trailing zero removed

        # Switch to dustjacket
        dialog.dustjacket_radio.setChecked(True)
        assert "35mm" in dialog.result_label.text()  # Whole number

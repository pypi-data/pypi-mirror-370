"""Test that the spinbox step size is correctly set to 2 in side-by-side mode."""

from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from momovu.views.main_window import MainWindow


class TestSpinboxStepFix:
    """Test the spinbox step=2 fix for side-by-side mode."""

    def test_spinbox_step_on_startup_single_mode(self, qapp):
        """Test spinbox has step=1 when starting in single page mode."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=False)

            # Spinbox should have step=1 in single page mode
            assert window.page_number_spinbox.singleStep() == 1

            window.close()

    def test_spinbox_step_on_startup_side_by_side_mode(self, qapp):
        """Test spinbox has step=2 when starting in side-by-side mode."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=True)

            # Spinbox should have step=2 in side-by-side mode
            assert window.page_number_spinbox.singleStep() == 2

            window.close()

    def test_spinbox_step_changes_when_toggling_mode(self, qapp):
        """Test spinbox step changes when toggling between modes."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=False)

            # Start in single page mode
            assert window.page_number_spinbox.singleStep() == 1

            # Toggle to side-by-side mode
            window.side_by_side_action.trigger()  # This toggles the checked state

            # Process events to ensure the toggle completes
            QApplication.processEvents()

            # Should now have step=2
            assert window.page_number_spinbox.singleStep() == 2

            # Toggle back to single page mode
            window.side_by_side_action.trigger()  # This toggles back

            # Process events to ensure the toggle completes
            QApplication.processEvents()

            # Should be back to step=1
            assert window.page_number_spinbox.singleStep() == 1

            window.close()

    def test_spinbox_arrow_works_in_side_by_side_mode(self, qapp):
        """Test that UP/DOWN arrows work correctly with step=2."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=True)
            window.navigation_presenter.set_total_pages(100)
            window.page_number_spinbox.setMaximum(100)

            # Navigate to page 10 (even page)
            window.navigation_presenter.go_to_page(9)  # 0-based
            window.update_page_label()

            # Spinbox should show 9 (1-based) because go_to_page(9) adjusts to 8
            assert window.page_number_spinbox.value() == 9

            # Click UP arrow - should increment by 2
            old_value = window.page_number_spinbox.value()
            window.page_number_spinbox.stepUp()
            new_value = window.page_number_spinbox.value()

            # Should have increased by 2
            assert new_value == old_value + 2
            assert new_value == 11

            # Trigger navigation
            window.on_page_number_changed(new_value)

            # Should navigate to page 10 (0-based) which stays at 10
            assert window.navigation_presenter.get_current_page() == 10

            window.close()

    def test_user_scenario_page_600_with_fix(self, qapp):
        """Test the original bug scenario with the fix applied."""
        with patch.object(MainWindow, "showMaximized"):
            window = MainWindow(side_by_side=True)
            window.navigation_presenter.set_total_pages(688)
            window.page_number_spinbox.setMaximum(688)

            # Navigate to page 598 (0-based) = 599 (1-based)
            window.navigation_presenter.go_to_page(598)
            window.update_page_label()
            assert window.page_number_spinbox.value() == 599

            # User types 600 (but we'll simulate being on 600)
            # In reality, go_to_page(599) would keep us at 598
            # But let's test from page 600 as the user expects
            window.navigation_presenter.go_to_page(600)  # Even page, no adjustment
            window.update_page_label()
            assert window.page_number_spinbox.value() == 601

            # Click UP arrow - with step=2, should go to 603
            window.page_number_spinbox.stepUp()
            assert window.page_number_spinbox.value() == 603

            # Navigate to 603 (0-based: 602)
            window.on_page_number_changed(603)

            # Should be on page 602 (0-based) which is even
            assert window.navigation_presenter.get_current_page() == 602

            # This is much better than before - the user sees clear movement
            # from 601 to 603, navigating by page pairs as expected

            window.close()

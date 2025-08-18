"""Unit tests for the AboutDialog component."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from momovu._version import __version__
from momovu.views.components.about_dialog import AboutDialog


class TestAboutDialog:
    """Test the AboutDialog component."""

    def test_about_dialog_creation(self, qtbot):
        """Test that AboutDialog can be created."""
        dialog = AboutDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert dialog.windowTitle() == "About Momovu"
        assert dialog.isModal()

    def test_about_dialog_displays_correct_version(self, qtbot):
        """Test that AboutDialog displays the correct version from _version.py."""
        dialog = AboutDialog()
        qtbot.addWidget(dialog)

        # Find all QLabel widgets in the dialog
        labels = dialog.findChildren(QLabel)

        # Check that at least one label contains the version
        version_found = False
        version_text = f"Version {__version__}"

        for label in labels:
            if version_text in label.text():
                version_found = True
                break

        assert version_found, f"Version '{version_text}' not found in dialog labels"

    def test_about_dialog_contains_expected_content(self, qtbot):
        """Test that AboutDialog contains all expected content."""
        dialog = AboutDialog()
        qtbot.addWidget(dialog)

        # Get all text content from labels
        labels = dialog.findChildren(QLabel)
        all_text = " ".join(label.text() for label in labels)

        # Check for expected content
        expected_content = [
            "Momovu",
            f"Version {__version__}",
            "A PDF viewer for book publishing workflows",
            "margin visualization",
            "Features:",
            "Interior, Cover, and Dustjacket viewing modes",
            "Links:",
            "https://momovu.org",
            "https://spacecruft.org/books/momovu",
            "Copyright © 2025 Jeff Moe",
            "Apache License, Version 2.0",
            "Python version:",
            "PySide6 version:",
        ]

        for content in expected_content:
            assert (
                content in all_text
            ), f"Expected content '{content}' not found in dialog"

    def test_about_dialog_has_ok_button(self, qtbot):
        """Test that AboutDialog has an OK button."""
        dialog = AboutDialog()
        qtbot.addWidget(dialog)

        # Check for OK button in button box
        from PySide6.QtWidgets import QDialogButtonBox

        button_boxes = dialog.findChildren(QDialogButtonBox)
        assert len(button_boxes) > 0, "No QDialogButtonBox found"

        button_box = button_boxes[0]
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        assert ok_button is not None, "OK button not found"
        assert ok_button.text() in [
            "OK",
            "&OK",
        ], f"Unexpected button text: {ok_button.text()}"

    def test_about_dialog_closes_on_ok(self, qtbot):
        """Test that AboutDialog closes when OK is clicked."""
        dialog = AboutDialog()
        qtbot.addWidget(dialog)

        # Show the dialog
        dialog.show()
        qtbot.waitExposed(dialog)

        # Find and click OK button
        from PySide6.QtWidgets import QDialogButtonBox

        button_box = dialog.findChild(QDialogButtonBox)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)

        # Click OK
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)

        # Dialog should be accepted
        assert dialog.result() == dialog.DialogCode.Accepted

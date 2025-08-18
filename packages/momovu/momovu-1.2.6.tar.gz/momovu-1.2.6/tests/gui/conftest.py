"""Fixtures and utilities for GUI testing with pytest-qt.

This module provides specialized fixtures for testing the Momovu application
with real Qt widgets and interactions using the qtbot fixture.
"""

from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from momovu.views.main_window import MainWindow

# Get the samples directory path
SAMPLES_DIR = Path(__file__).parent.parent.parent / "samples"


@pytest.fixture(autouse=True)
def qt_cleanup(qtbot):
    """Ensure Qt event loop is clean between tests."""
    yield
    # Process all pending events after each test
    QCoreApplication.processEvents()
    qtbot.wait(10)
    QCoreApplication.sendPostedEvents()
    QCoreApplication.processEvents()


@pytest.fixture
def sample_pdf_paths():
    """Provide paths to sample PDF files for testing.

    Returns:
        dict: Dictionary of sample PDF paths categorized by type
    """
    return {
        "interior": [
            SAMPLES_DIR / "bovary-interior.pdf",
            SAMPLES_DIR / "pingouins-interior.pdf",
        ],
        "cover": [
            SAMPLES_DIR / "bovary-cover.pdf",
            SAMPLES_DIR / "lovecraft-cover.pdf",
            SAMPLES_DIR / "pingouins-cover.pdf",
            SAMPLES_DIR / "quixote-cover.pdf",
            SAMPLES_DIR / "siddhartha-cover.pdf",
            SAMPLES_DIR / "vatican-cover.pdf",
        ],
        "dustjacket": [
            SAMPLES_DIR / "bovary-dustjacket.pdf",
            SAMPLES_DIR / "pingouins-dustjacket.pdf",
            SAMPLES_DIR / "vatican-dustjacket.pdf",
        ],
    }


@pytest.fixture
def main_window(qtbot):
    """Create a MainWindow instance for GUI testing.

    Args:
        qtbot: pytest-qt fixture for Qt testing

    Returns:
        MainWindow: A MainWindow instance registered with qtbot
    """
    # Create the main window
    window = MainWindow()

    # Register with qtbot for proper cleanup
    qtbot.addWidget(window)

    # Show the window and wait for it to be exposed
    window.show()
    qtbot.waitExposed(window)

    return window


@pytest.fixture
def main_window_with_pdf(qtbot, sample_pdf_paths):
    """Create a MainWindow with a PDF loaded.

    Args:
        qtbot: pytest-qt fixture for Qt testing
        sample_pdf_paths: Dictionary of sample PDF paths

    Returns:
        MainWindow: A MainWindow instance with a PDF loaded
    """
    # Create the main window
    window = MainWindow()
    qtbot.addWidget(window)

    # Load a sample interior PDF
    pdf_path = sample_pdf_paths["interior"][0]

    # Ensure the file exists
    assert pdf_path.exists(), f"Sample PDF not found: {pdf_path}"

    # Show the window
    window.show()
    qtbot.waitExposed(window)

    # Load the PDF
    window.load_pdf(str(pdf_path))

    # Wait for the document to be loaded
    qtbot.waitUntil(
        lambda: window.document_presenter is not None
        and window.document_presenter.is_document_loaded(),
        timeout=5000,
    )

    # Wait a bit for initial rendering to complete
    qtbot.wait(500)

    # Process any pending events before yielding
    QCoreApplication.processEvents()

    yield window

    # Proper cleanup to prevent Qt event loop issues
    try:
        # Process any pending events first
        QCoreApplication.processEvents()
        qtbot.wait(10)

        # Close any open documents first
        if (
            hasattr(window, "document_presenter")
            and window.document_presenter
            and hasattr(window.document_presenter, "is_document_loaded")
            and window.document_presenter.is_document_loaded()
        ):
            window.close_pdf()
            qtbot.wait(50)
            QCoreApplication.processEvents()

        # Hide the window before closing
        if window.isVisible():
            window.hide()
            qtbot.wait(10)

        # Close the window properly
        window.close()
        qtbot.wait(50)

        # Final event processing and cleanup
        QCoreApplication.sendPostedEvents()
        QCoreApplication.processEvents()
    except (RuntimeError, AttributeError):
        # Widget already deleted or attribute error, that's fine
        pass


@pytest.fixture
def main_window_with_cover(qtbot, sample_pdf_paths):
    """Create a MainWindow with a cover PDF loaded.

    Args:
        qtbot: pytest-qt fixture for Qt testing
        sample_pdf_paths: Dictionary of sample PDF paths

    Returns:
        MainWindow: A MainWindow instance with a cover PDF loaded
    """
    # Create the main window
    window = MainWindow()
    qtbot.addWidget(window)

    # Load a sample cover PDF
    pdf_path = sample_pdf_paths["cover"][0]

    # Ensure the file exists
    assert pdf_path.exists(), f"Sample PDF not found: {pdf_path}"

    # Show the window
    window.show()
    qtbot.waitExposed(window)

    # Load the PDF
    window.load_pdf(str(pdf_path))

    # Wait for the document to be loaded
    qtbot.waitUntil(
        lambda: window.document_presenter is not None
        and window.document_presenter.is_document_loaded(),
        timeout=5000,
    )

    # Set document type to cover
    window.set_document_type("cover")

    # Wait for re-rendering
    qtbot.wait(500)

    # Process any pending events before yielding
    QCoreApplication.processEvents()

    yield window

    # Proper cleanup
    try:
        # Process any pending events first
        QCoreApplication.processEvents()
        qtbot.wait(10)

        # Close any open documents first
        if (
            hasattr(window, "document_presenter")
            and window.document_presenter
            and hasattr(window.document_presenter, "is_document_loaded")
            and window.document_presenter.is_document_loaded()
        ):
            window.close_pdf()
            qtbot.wait(50)
            QCoreApplication.processEvents()

        # Hide the window before closing
        if window.isVisible():
            window.hide()
            qtbot.wait(10)

        # Close the window properly
        window.close()
        qtbot.wait(50)

        # Final event processing and cleanup
        QCoreApplication.sendPostedEvents()
        QCoreApplication.processEvents()
    except (RuntimeError, AttributeError):
        # Widget already deleted or attribute error, that's fine
        pass


@pytest.fixture
def main_window_with_dustjacket(qtbot, sample_pdf_paths):
    """Create a MainWindow with a dustjacket PDF loaded.

    Args:
        qtbot: pytest-qt fixture for Qt testing
        sample_pdf_paths: Dictionary of sample PDF paths

    Returns:
        MainWindow: A MainWindow instance with a dustjacket PDF loaded
    """
    # Create the main window
    window = MainWindow()
    qtbot.addWidget(window)

    # Load a sample dustjacket PDF
    pdf_path = sample_pdf_paths["dustjacket"][0]

    # Ensure the file exists
    assert pdf_path.exists(), f"Sample PDF not found: {pdf_path}"

    # Show the window
    window.show()
    qtbot.waitExposed(window)

    # Load the PDF
    window.load_pdf(str(pdf_path))

    # Wait for the document to be loaded
    qtbot.waitUntil(
        lambda: window.document_presenter is not None
        and window.document_presenter.is_document_loaded(),
        timeout=5000,
    )

    # Set document type to dustjacket
    window.set_document_type("dustjacket")

    # Wait for re-rendering
    qtbot.wait(500)

    # Process any pending events before yielding
    QCoreApplication.processEvents()

    yield window

    # Proper cleanup
    try:
        # Process any pending events first
        QCoreApplication.processEvents()
        qtbot.wait(10)

        # Close any open documents first
        if (
            hasattr(window, "document_presenter")
            and window.document_presenter
            and hasattr(window.document_presenter, "is_document_loaded")
            and window.document_presenter.is_document_loaded()
        ):
            window.close_pdf()
            qtbot.wait(50)
            QCoreApplication.processEvents()

        # Hide the window before closing
        if window.isVisible():
            window.hide()
            qtbot.wait(10)

        # Close the window properly
        window.close()
        qtbot.wait(50)

        # Final event processing and cleanup
        QCoreApplication.sendPostedEvents()
        QCoreApplication.processEvents()
    except (RuntimeError, AttributeError):
        # Widget already deleted or attribute error, that's fine
        pass


class GUITestHelper:
    """Helper class for common GUI testing operations."""

    @staticmethod
    def wait_for_render(qtbot, window, timeout=2000):
        """Wait for the current page to be rendered.

        Args:
            qtbot: pytest-qt fixture
            window: MainWindow instance
            timeout: Maximum time to wait in milliseconds
        """
        qtbot.waitUntil(lambda: len(window.graphics_scene.items()) > 0, timeout=timeout)

    @staticmethod
    def get_current_page(window) -> int:
        """Get the current page number (0-based).

        Args:
            window: MainWindow instance

        Returns:
            int: Current page number
        """
        if window.navigation_presenter:
            return window.navigation_presenter.get_current_page()
        return -1

    @staticmethod
    def get_total_pages(window) -> int:
        """Get the total number of pages.

        Args:
            window: MainWindow instance

        Returns:
            int: Total number of pages
        """
        if window.navigation_presenter:
            return window.navigation_presenter.get_total_pages()
        return 0

    @staticmethod
    def get_zoom_level(window) -> float:
        """Get the current zoom level.

        Args:
            window: MainWindow instance

        Returns:
            float: Current zoom level
        """
        if window.zoom_controller:
            return window.zoom_controller.get_current_zoom()
        return 1.0

    @staticmethod
    def get_document_type(window) -> str:
        """Get the current document type.

        Args:
            window: MainWindow instance

        Returns:
            str: Document type ('interior', 'cover', or 'dustjacket')
        """
        if window.margin_presenter:
            return window.margin_presenter.get_document_type()
        return "interior"

    @staticmethod
    def is_side_by_side(window) -> bool:
        """Check if side-by-side view is active.

        Args:
            window: MainWindow instance

        Returns:
            bool: True if side-by-side view is active
        """
        if window.navigation_presenter:
            return window.navigation_presenter.model.view_mode == "side_by_side"
        return False

    @staticmethod
    def is_presentation_mode(window) -> bool:
        """Check if presentation mode is active.

        Args:
            window: MainWindow instance

        Returns:
            bool: True if presentation mode is active
        """
        if window.ui_state_manager:
            return window.ui_state_manager.is_presentation_mode
        return False


@pytest.fixture
def gui_helper():
    """Provide the GUI test helper.

    Returns:
        GUITestHelper: Helper instance for GUI testing
    """
    return GUITestHelper()

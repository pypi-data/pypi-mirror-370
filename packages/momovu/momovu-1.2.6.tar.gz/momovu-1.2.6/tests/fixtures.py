"""Shared test fixtures and utilities for the test suite.

This module provides reusable fixtures, mock factories, and helper functions
to reduce code duplication and make tests more maintainable.
"""

from typing import Any, Optional
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter

# ============================================================================
# Mock Factories
# ============================================================================


class MockFactory:
    """Factory for creating commonly used mock objects."""

    @staticmethod
    def create_pdf_document(
        page_count: int = 10,
        page_width: float = 612.0,
        page_height: float = 792.0,
        status: QPdfDocument.Status = QPdfDocument.Status.Ready,
    ) -> Mock:
        """Create a mock PDF document."""
        mock_pdf = Mock(spec=QPdfDocument)
        mock_pdf.pageCount = Mock(return_value=page_count)
        mock_pdf.status = Mock(return_value=status)
        mock_pdf.close = Mock()

        # Mock page size
        mock_size = Mock()
        mock_size.width = Mock(return_value=page_width)
        mock_size.height = Mock(return_value=page_height)
        mock_pdf.pageSize = Mock(return_value=mock_size)

        # Mock load method
        mock_pdf.load = Mock(return_value=QPdfDocument.Error.None_)

        # Mock render method
        mock_image = QImage(100, 100, QImage.Format.Format_RGB32)
        mock_pdf.render = Mock(return_value=mock_image)

        return mock_pdf

    @staticmethod
    def create_graphics_scene() -> Mock:
        """Create a mock graphics scene."""
        mock_scene = Mock(spec=QGraphicsScene)
        mock_scene.clear = Mock()
        mock_scene.addItem = Mock()
        mock_scene.addRect = Mock(return_value=Mock())
        mock_scene.addLine = Mock(return_value=Mock())
        mock_scene.setSceneRect = Mock()
        mock_scene.items = Mock(return_value=[])
        mock_scene.itemsBoundingRect = Mock(return_value=QRectF(0, 0, 612, 792))
        mock_scene.views = Mock(return_value=[])
        return mock_scene

    @staticmethod
    def create_graphics_view() -> Mock:
        """Create a mock graphics view."""
        mock_view = Mock(spec=QGraphicsView)
        mock_view.scale = Mock()
        mock_view.resetTransform = Mock()
        mock_view.fitInView = Mock()
        mock_view.mapToScene = Mock(return_value=QPointF(0, 0))
        mock_view.viewport = Mock(
            return_value=Mock(rect=Mock(return_value=QRectF(0, 0, 800, 600)))
        )
        mock_view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        return mock_view

    @staticmethod
    def create_main_window() -> Mock:
        """Create a mock main window."""
        mock_window = Mock()
        mock_window.graphics_scene = MockFactory.create_graphics_scene()
        mock_window.graphics_view = MockFactory.create_graphics_view()
        mock_window.pdf_document = MockFactory.create_pdf_document()
        mock_window.setWindowTitle = Mock()
        mock_window.update_page_label = Mock()
        mock_window.render_current_page = Mock()
        mock_window.menuBar = Mock(return_value=Mock())
        mock_window.toolbar = Mock()
        mock_window.status_bar = Mock()
        mock_window.isFullScreen = Mock(return_value=False)
        mock_window.showFullScreen = Mock()
        mock_window.showNormal = Mock()
        return mock_window

    @staticmethod
    def create_page_item(page_number: int = 0) -> Mock:
        """Create a mock page item."""
        mock_item = Mock()
        mock_item.page_number = page_number
        mock_item.cleanup = Mock()
        mock_item.setPos = Mock()
        mock_item.pos = Mock(return_value=QPointF(0, 0))
        mock_item.boundingRect = Mock(return_value=QRectF(0, 0, 612, 792))
        mock_item.mapRectToScene = Mock(return_value=QRectF(0, 0, 612, 792))
        return mock_item


# ============================================================================
# Model/Presenter Fixtures
# ============================================================================


@pytest.fixture
def document_model():
    """Create a Document model instance."""
    return Document()


@pytest.fixture
def margin_model():
    """Create a MarginSettingsModel instance."""
    return MarginSettingsModel()


@pytest.fixture
def view_model():
    """Create a ViewStateModel instance."""
    return ViewStateModel()


@pytest.fixture
def document_presenter(document_model):
    """Create a DocumentPresenter with model."""
    return DocumentPresenter(document_model)


@pytest.fixture
def margin_presenter(margin_model):
    """Create a MarginPresenter with model."""
    return MarginPresenter(margin_model)


@pytest.fixture
def navigation_presenter(view_model):
    """Create a NavigationPresenter with model."""
    return NavigationPresenter(view_model)


# ============================================================================
# Mock Object Fixtures
# ============================================================================


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document."""
    return MockFactory.create_pdf_document()


@pytest.fixture
def mock_graphics_scene():
    """Create a mock graphics scene."""
    return MockFactory.create_graphics_scene()


@pytest.fixture
def mock_graphics_view():
    """Create a mock graphics view."""
    return MockFactory.create_graphics_view()


@pytest.fixture
def mock_main_window():
    """Create a mock main window."""
    return MockFactory.create_main_window()


# ============================================================================
# Parameterized Fixtures
# ============================================================================


@pytest.fixture(params=["interior", "cover", "dustjacket"])
def document_type(request):
    """Parameterized fixture for document types."""
    return request.param


@pytest.fixture(params=[0, 5, 10, 50, 100])
def page_count(request):
    """Parameterized fixture for different page counts."""
    return request.param


@pytest.fixture(params=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
def zoom_level(request):
    """Parameterized fixture for zoom levels."""
    return request.param


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_image(width: int = 100, height: int = 100) -> QImage:
    """Create a test QImage."""
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(255, 255, 255))
    return image


def create_test_rect(
    x: float = 0, y: float = 0, width: float = 612, height: float = 792
) -> QRectF:
    """Create a test QRectF."""
    return QRectF(x, y, width, height)


def create_test_point(x: float = 0, y: float = 0) -> QPointF:
    """Create a test QPointF."""
    return QPointF(x, y)


def assert_rect_equal(rect1: QRectF, rect2: QRectF, tolerance: float = 0.01) -> None:
    """Assert two QRectF objects are equal within tolerance."""
    assert abs(rect1.x() - rect2.x()) < tolerance
    assert abs(rect1.y() - rect2.y()) < tolerance
    assert abs(rect1.width() - rect2.width()) < tolerance
    assert abs(rect1.height() - rect2.height()) < tolerance


def assert_point_equal(
    point1: QPointF, point2: QPointF, tolerance: float = 0.01
) -> None:
    """Assert two QPointF objects are equal within tolerance."""
    assert abs(point1.x() - point2.x()) < tolerance
    assert abs(point1.y() - point2.y()) < tolerance


# ============================================================================
# Test Data
# ============================================================================


class TestData:
    """Common test data values."""

    # Page dimensions
    LETTER_WIDTH = 612.0  # 8.5 inches in points
    LETTER_HEIGHT = 792.0  # 11 inches in points
    A4_WIDTH = 595.0  # A4 width in points
    A4_HEIGHT = 842.0  # A4 height in points

    # Margin sizes
    DEFAULT_MARGIN_MM = 12.7  # 0.5 inches
    DEFAULT_MARGIN_POINTS = 36.0

    # Spine widths
    THIN_SPINE = 10.0
    MEDIUM_SPINE = 50.0
    THICK_SPINE = 100.0

    # Flap dimensions
    SMALL_FLAP_WIDTH = 75.0
    MEDIUM_FLAP_WIDTH = 100.0
    LARGE_FLAP_WIDTH = 150.0

    # Sample file paths
    SAMPLE_PDF_PATH = "/test/sample.pdf"
    INVALID_PDF_PATH = "/test/invalid.pdf"
    MISSING_PDF_PATH = "/test/missing.pdf"


# ============================================================================
# Composite Fixtures
# ============================================================================


@pytest.fixture
def complete_test_setup(mock_main_window, document_model, margin_model, view_model):
    """Create a complete test setup with all components."""
    # Create presenters
    doc_presenter = DocumentPresenter(document_model)
    margin_presenter = MarginPresenter(margin_model)
    nav_presenter = NavigationPresenter(view_model)

    # Wire up main window
    mock_main_window.document_presenter = doc_presenter
    mock_main_window.margin_presenter = margin_presenter
    mock_main_window.navigation_presenter = nav_presenter

    return {
        "window": mock_main_window,
        "doc_presenter": doc_presenter,
        "margin_presenter": margin_presenter,
        "nav_presenter": nav_presenter,
        "doc_model": document_model,
        "margin_model": margin_model,
        "view_model": view_model,
    }


# ============================================================================
# Performance Testing Utilities
# ============================================================================


class PerformanceTimer:
    """Context manager for timing test execution."""

    def __init__(self, name: str = "Test"):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        import time

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time

        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"\n{self.name} took {duration:.3f} seconds")

    @property
    def duration(self) -> Optional[float]:
        """Get the duration if timing is complete."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


# ============================================================================
# Assertion Helpers
# ============================================================================


class AssertHelpers:
    """Additional assertion helpers for common test patterns."""

    @staticmethod
    def assert_called_with_any_of(mock_obj: Mock, *expected_calls: Any) -> None:
        """Assert mock was called with any of the expected calls."""
        actual_calls = mock_obj.call_args_list
        for expected in expected_calls:
            if expected in actual_calls:
                return
        raise AssertionError(
            f"Expected one of {expected_calls}, but got {actual_calls}"
        )

    @staticmethod
    def assert_not_called_with(mock_obj: Mock, *unexpected_args: Any) -> None:
        """Assert mock was never called with specific arguments."""
        actual_calls = mock_obj.call_args_list
        for args in unexpected_args:
            if args in actual_calls:
                raise AssertionError(f"Unexpected call {args} found in {actual_calls}")

    @staticmethod
    def assert_in_range(value: float, min_val: float, max_val: float) -> None:
        """Assert value is within range."""
        assert (
            min_val <= value <= max_val
        ), f"Value {value} not in range [{min_val}, {max_val}]"

"""Global pytest configuration and fixtures.

This file is automatically loaded by pytest and provides fixtures
and configuration for all tests.
"""

from unittest.mock import Mock, patch

import pytest

# Import all fixtures from our fixtures module
from tests.fixtures import *  # noqa: F403

# Import Hypothesis settings
from tests.hypothesis_settings import *  # noqa: F403
from tests.test_config import TestConfig, TestMarkers
from tests.test_utils import mock_qt_application

# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    for marker in TestMarkers.get_all_markers():
        config.addinivalue_line("markers", marker)

    # Set up test environment
    import os

    os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Run Qt tests headless


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and skip tests."""
    for item in items:
        # Add markers based on test location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_perf" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        # Skip slow tests if requested
        if TestConfig.should_skip_slow_tests() and item.get_closest_marker("slow"):
            item.add_marker(pytest.mark.skip(reason="Slow tests disabled"))

        # Skip GUI tests if requested
        if TestConfig.should_skip_gui_tests() and item.get_closest_marker("gui"):
            item.add_marker(pytest.mark.skip(reason="GUI tests disabled"))


# ============================================================================
# Session Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def qt_app():
    """Ensure Qt application exists for the entire test session."""
    with mock_qt_application() as app:
        yield app


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the test data directory."""
    data_dir = TestConfig.TEST_DATA_DIR
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(scope="session")
def test_output_dir():
    """Get the test output directory."""
    return TestConfig.get_test_output_dir()


# ============================================================================
# Function Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singletons between tests."""
    # Add any singleton resets here if needed
    yield


@pytest.fixture
def temp_pdf_file(tmp_path):
    """Create a temporary PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    # Create a minimal valid PDF
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n203\n%%EOF"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


# ============================================================================
# Logging Configuration
# ============================================================================


@pytest.fixture(autouse=True)
def configure_test_logging(caplog):
    """Configure logging for tests."""
    import logging

    caplog.set_level(TestConfig.TEST_LOG_LEVEL)

    # Disable verbose Qt logging
    logging.getLogger("PySide6").setLevel(logging.WARNING)

    yield


# ============================================================================
# Performance Monitoring
# ============================================================================


@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.operations = {}

        def start(self, operation: str):
            self.start_time = time.time()
            self.current_operation = operation

        def stop(self):
            if self.start_time:
                duration = time.time() - self.start_time
                self.operations[self.current_operation] = duration
                self.start_time = None
                return duration
            return 0

        def get_report(self):
            return self.operations

    return PerformanceMonitor()


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture
def auto_cleanup():
    """Automatically cleanup resources after test."""
    resources = []

    def register(resource):
        resources.append(resource)

    yield register

    # Cleanup all registered resources
    for resource in resources:
        if hasattr(resource, "cleanup"):
            try:
                resource.cleanup()
            except Exception:
                pass
        elif hasattr(resource, "deleteLater"):
            try:
                resource.deleteLater()
            except Exception:
                pass


# ============================================================================
# Test Helpers
# ============================================================================


@pytest.fixture
def assert_no_warnings(recwarn):
    """Fixture to assert no warnings were issued."""
    yield
    assert (
        len(recwarn) == 0
    ), f"Unexpected warnings: {[str(w.message) for w in recwarn]}"


@pytest.fixture
def mock_timer():
    """Mock QTimer for testing."""
    with patch("PySide6.QtCore.QTimer") as mock:
        timer_instance = Mock()
        timer_instance.timeout = Mock()
        timer_instance.start = Mock()
        timer_instance.stop = Mock()
        timer_instance.isActive = Mock(return_value=False)
        mock.return_value = timer_instance
        mock.singleShot = Mock()
        yield mock


# ============================================================================
# Report Generation
# ============================================================================


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom information to test report."""
    if TestConfig.CI_MODE:
        return  # Skip in CI

    # Add test categories summary
    terminalreporter.section("Test Categories")

    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))

    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")

    # Add performance summary if enabled
    if TestConfig.PERFORMANCE_TEST_ENABLED:
        terminalreporter.section("Performance Summary")
        # Add performance metrics here


# ============================================================================
# Custom Assertions
# ============================================================================


def pytest_assertrepr_compare(op, left, right):
    """Provide custom assertion messages."""
    from PySide6.QtCore import QRectF

    if isinstance(left, QRectF) and isinstance(right, QRectF) and op == "==":
        return [
            "QRectF comparison failed:",
            f"  Left:  x={left.x()}, y={left.y()}, w={left.width()}, h={left.height()}",
            f"  Right: x={right.x()}, y={right.y()}, w={right.width()}, h={right.height()}",
        ]

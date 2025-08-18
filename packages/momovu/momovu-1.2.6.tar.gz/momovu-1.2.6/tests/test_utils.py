"""Test utilities and helper functions.

This module provides utility functions to simplify common testing patterns
and reduce boilerplate code.
"""

import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

# ============================================================================
# Qt Test Utilities
# ============================================================================


def process_qt_events(max_time: float = 0.1) -> None:
    """Process Qt events for a short time to allow UI updates."""
    app = QApplication.instance()
    if app:
        end_time = time.time() + max_time
        while time.time() < end_time:
            app.processEvents()
            time.sleep(0.001)


def wait_for_signal(signal: Any, timeout: float = 1.0) -> bool:
    """Wait for a Qt signal to be emitted.

    Args:
        signal: The Qt signal to wait for
        timeout: Maximum time to wait in seconds

    Returns:
        True if signal was emitted, False if timeout
    """
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)

    signal.connect(loop.quit)
    timer.timeout.connect(loop.quit)

    timer.start(int(timeout * 1000))
    loop.exec()

    return timer.isActive()


@contextmanager
def qt_wait(duration: float = 0.1):
    """Context manager that waits for Qt events after the block."""
    yield
    process_qt_events(duration)


# ============================================================================
# Mock Utilities
# ============================================================================


def create_autospec_mock(spec_class: type, **kwargs) -> Mock:
    """Create a mock with autospec and additional attributes.

    Args:
        spec_class: The class to create an autospec mock of
        **kwargs: Additional attributes to set on the mock

    Returns:
        Mock object with autospec
    """
    mock = Mock(spec=spec_class)
    for key, value in kwargs.items():
        setattr(mock, key, value)
    return mock


def patch_multiple_methods(target: str, methods: dict) -> Any:
    """Patch multiple methods on a target class.

    Args:
        target: The target class path to patch
        methods: Dict of method_name: return_value or Mock

    Returns:
        Patch object that can be used as decorator or context manager
    """
    patches = {}
    for method, value in methods.items():
        if isinstance(value, Mock):
            patches[method] = value
        else:
            patches[method] = Mock(return_value=value)

    return patch.multiple(target, **patches)


@contextmanager
def mock_qt_application():
    """Context manager that ensures a Qt application exists for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    yield app

    # Don't quit the app as other tests might need it


# ============================================================================
# Assertion Utilities
# ============================================================================


def assert_called_once_with_subset(mock: Mock, **expected_kwargs) -> None:
    """Assert mock was called once with at least the expected kwargs.

    This is useful when you only care about certain arguments.
    """
    assert mock.call_count == 1, f"Expected 1 call, got {mock.call_count}"

    actual_kwargs = mock.call_args.kwargs
    for key, expected_value in expected_kwargs.items():
        assert key in actual_kwargs, f"Missing expected kwarg: {key}"
        assert (
            actual_kwargs[key] == expected_value
        ), f"Kwarg {key}: expected {expected_value}, got {actual_kwargs[key]}"


def assert_signal_emitted(signal_mock: Mock, times: int = 1) -> None:
    """Assert a Qt signal was emitted the expected number of times."""
    emit_calls = [call for call in signal_mock.method_calls if call[0] == "emit"]
    assert (
        len(emit_calls) == times
    ), f"Expected signal emitted {times} times, got {len(emit_calls)}"


def assert_no_exceptions(func: Callable) -> Callable:
    """Decorator that ensures a test function doesn't raise exceptions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")

    return wrapper


# ============================================================================
# Test Data Generators
# ============================================================================


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def create_page_sizes(
        count: int, width: float = 612.0, height: float = 792.0
    ) -> list[tuple[float, float]]:
        """Create a list of page sizes."""
        return [(width, height) for _ in range(count)]

    @staticmethod
    def create_margin_combinations() -> list[dict]:
        """Create various margin setting combinations."""
        return [
            {"margin_mm": 12.7, "show_margins": True, "show_trim": True},
            {"margin_mm": 25.4, "show_margins": True, "show_trim": False},
            {"margin_mm": 6.35, "show_margins": False, "show_trim": True},
            {"margin_mm": 0, "show_margins": False, "show_trim": False},
        ]

    @staticmethod
    def create_zoom_levels() -> list[float]:
        """Create a range of zoom levels for testing."""
        return [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]

    @staticmethod
    def create_document_types() -> list[tuple[str, dict]]:
        """Create document type configurations."""
        return [
            ("interior", {"supports_barcode": False, "supports_fold": False}),
            ("cover", {"supports_barcode": True, "supports_fold": True}),
            ("dustjacket", {"supports_barcode": True, "supports_fold": True}),
        ]


# ============================================================================
# Performance Testing
# ============================================================================


def measure_performance(func: Callable) -> Callable:
    """Decorator that measures and reports function execution time."""
    # Store durations on the function itself
    func.durations = []

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        # Store duration on the original function
        func.durations.append(duration)

        return result

    return wrapper


def assert_performance(
    operation: str, duration: float, max_duration: Optional[float] = None
) -> None:
    """Assert that an operation completed within acceptable time."""
    from .test_config import PerformanceBenchmarks

    if max_duration is None:
        # Use default benchmark
        is_acceptable = PerformanceBenchmarks.check_performance(operation, duration)
        assert is_acceptable, f"{operation} took {duration:.3f}s, " f"exceeds benchmark"
    else:
        assert duration <= max_duration, (
            f"{operation} took {duration:.3f}s, "
            f"exceeds limit of {max_duration:.3f}s"
        )


# ============================================================================
# Parameterization Helpers
# ============================================================================


def parametrize_document_types():
    """Parametrize test with all document types."""
    return pytest.mark.parametrize(
        "doc_type,expected", TestDataGenerator.create_document_types()
    )


def parametrize_zoom_levels():
    """Parametrize test with various zoom levels."""
    return pytest.mark.parametrize("zoom_level", TestDataGenerator.create_zoom_levels())


def parametrize_page_counts():
    """Parametrize test with various page counts."""
    return pytest.mark.parametrize("page_count", [0, 1, 2, 5, 10, 50, 100, 500])


# ============================================================================
# Error Testing Utilities
# ============================================================================


@contextmanager
def should_not_raise():
    """Context manager that fails if an exception is raised."""
    try:
        yield
    except Exception as e:
        pytest.fail(f"Unexpected exception: {type(e).__name__}: {e}")


def assert_error_handled(
    func: Callable, error_type: type[Exception], *args, **kwargs
) -> None:
    """Assert that a function handles a specific error type gracefully."""
    with patch("momovu.lib.logger.get_logger") as mock_logger:
        # Function should not raise the exception
        with should_not_raise():
            func(*args, **kwargs)

        # But it should log the error
        logger = mock_logger.return_value
        assert (
            logger.error.called or logger.warning.called
        ), "Expected error to be logged"


# ============================================================================
# State Verification
# ============================================================================


class StateVerifier:
    """Helper for verifying object state in tests."""

    def __init__(self, obj: Any):
        self.obj = obj
        self.initial_state = self._capture_state()

    def _capture_state(self) -> dict:
        """Capture current state of the object."""
        state = {}
        for attr in dir(self.obj):
            if not attr.startswith("_") and not callable(getattr(self.obj, attr)):
                try:
                    state[attr] = getattr(self.obj, attr)
                except Exception:
                    pass
        return state

    def assert_changed(self, *attributes: str) -> None:
        """Assert that specific attributes have changed."""
        current_state = self._capture_state()
        for attr in attributes:
            assert attr in self.initial_state, f"Unknown attribute: {attr}"
            assert (
                current_state[attr] != self.initial_state[attr]
            ), f"Expected {attr} to change"

    def assert_unchanged(self, *attributes: str) -> None:
        """Assert that specific attributes have not changed."""
        current_state = self._capture_state()
        for attr in attributes:
            assert attr in self.initial_state, f"Unknown attribute: {attr}"
            assert (
                current_state[attr] == self.initial_state[attr]
            ), f"Expected {attr} to remain unchanged"


# ============================================================================
# Cleanup Utilities
# ============================================================================


@contextmanager
def ensure_cleanup(*objects: Any):
    """Ensure cleanup methods are called on objects."""
    try:
        yield
    finally:
        for obj in objects:
            if hasattr(obj, "cleanup") and callable(obj.cleanup):
                try:
                    obj.cleanup()
                except Exception:
                    pass  # Best effort cleanup


def cleanup_qt_widgets(*widgets: Any) -> None:
    """Clean up Qt widgets after tests."""
    for widget in widgets:
        if widget and hasattr(widget, "deleteLater"):
            widget.deleteLater()

    # Process events to ensure deletion
    process_qt_events(0.01)

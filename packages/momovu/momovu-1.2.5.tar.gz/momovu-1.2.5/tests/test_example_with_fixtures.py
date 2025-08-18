"""Example test file demonstrating the use of improved test infrastructure.

This shows how to use the fixtures, utilities, and helpers we've created.
"""

from unittest.mock import Mock

import pytest

from tests.fixtures import (
    AssertHelpers,
    MockFactory,
    PerformanceTimer,
    TestData,
)
from tests.test_config import TestConfig
from tests.test_utils import (
    StateVerifier,
    assert_signal_emitted,
    parametrize_document_types,
    parametrize_zoom_levels,
    should_not_raise,
)


# Use the test markers
@pytest.mark.unit
class TestExampleWithFixtures:
    """Example tests using the improved infrastructure."""

    def test_using_mock_factory(self):
        """Example of using MockFactory."""
        # Create mocks easily
        pdf = MockFactory.create_pdf_document(page_count=20)
        scene = MockFactory.create_graphics_scene()
        view = MockFactory.create_graphics_view()

        # Use the mocks
        assert pdf.pageCount() == 20
        scene.clear()
        scene.clear.assert_called_once()

        view.scale(2.0, 2.0)
        view.scale.assert_called_with(2.0, 2.0)

    def test_using_test_data(self):
        """Example of using TestData constants."""
        # Use predefined test data
        assert TestData.LETTER_WIDTH == 612.0
        assert TestData.DEFAULT_MARGIN_MM == 12.7

        # Use for creating test scenarios
        _ = {"spine_width": TestData.THIN_SPINE, "page_count": 50}  # thin_book
        _ = {"spine_width": TestData.THICK_SPINE, "page_count": 500}  # thick_book

    def test_using_complete_setup(self, complete_test_setup):
        """Example of using the complete test setup fixture."""
        setup = complete_test_setup

        # Access all components
        _ = setup["window"]  # window
        doc_presenter = setup["doc_presenter"]
        _ = setup["margin_presenter"]  # margin_presenter
        nav_presenter = setup["nav_presenter"]

        # Test interaction between components
        doc_presenter.model.page_count = 10
        nav_presenter.set_total_pages(10)

        assert nav_presenter.get_total_pages() == 10

    @parametrize_document_types()
    def test_with_document_types(self, doc_type, expected):
        """Example of using parameterized document types."""
        # This test runs once for each document type
        if doc_type == "interior":
            assert not expected["supports_barcode"]
        else:
            assert expected["supports_barcode"]

    @parametrize_zoom_levels()
    def test_with_zoom_levels(self, zoom_level):
        """Example of using parameterized zoom levels."""
        # This test runs once for each zoom level
        view = MockFactory.create_graphics_view()

        # Test zoom operation
        view.scale(zoom_level, zoom_level)
        view.scale.assert_called_with(zoom_level, zoom_level)


@pytest.mark.integration
class TestExampleIntegration:
    """Example integration tests using utilities."""

    def test_state_verification(self, margin_model):
        """Example of using StateVerifier."""
        verifier = StateVerifier(margin_model)

        # Change some state
        margin_model.document_type = "cover"
        margin_model.spine_width = 50.0

        # Verify what changed and what didn't
        verifier.assert_changed("document_type", "spine_width")
        verifier.assert_unchanged("safety_margin_mm", "show_margins")

    def test_signal_assertions(self):
        """Example of asserting signal emissions."""
        mock_signal = Mock()
        mock_signal.emit = Mock()

        # Emit signal twice
        mock_signal.emit("data1")
        mock_signal.emit("data2")

        # Assert it was emitted twice
        assert_signal_emitted(mock_signal, times=2)

    def test_error_handling(self):
        """Example of testing error handling."""

        def risky_operation():
            # This would normally raise an exception
            # but we're testing that it's handled
            pass

        # Assert no exception is raised
        with should_not_raise():
            risky_operation()


@pytest.mark.performance
class TestExamplePerformance:
    """Example performance tests."""

    def test_render_performance(self):
        """Example of measuring performance."""
        # Simple performance measurement without decorator
        import time

        start = time.time()

        # Simulate some operation
        time.sleep(0.01)  # 10ms operation

        duration = time.time() - start

        # Assert performance
        assert duration < 0.1  # Should be under 100ms
        assert duration >= 0.01  # Should be at least 10ms

    def test_with_performance_timer(self):
        """Example of using PerformanceTimer."""
        with PerformanceTimer("Complex Operation") as timer:
            # Do some work
            import time

            time.sleep(0.05)

        # Check duration
        assert timer.duration is not None
        assert timer.duration < 0.1  # Should be under 100ms


@pytest.mark.slow
@pytest.mark.gui
class TestExampleGUI:
    """Example GUI tests (would be skipped in CI)."""

    @pytest.mark.skipif(TestConfig.should_skip_gui_tests(), reason="GUI tests disabled")
    def test_gui_operation(self):
        """Example of a GUI test that can be skipped."""
        # This would contain actual GUI testing code
        pass

    @pytest.mark.skipif(
        TestConfig.should_skip_slow_tests(), reason="Slow tests disabled"
    )
    def test_slow_operation(self):
        """Example of a slow test that can be skipped."""
        # This would contain a slow operation
        pass


class TestExampleHelpers:
    """Example of using assertion helpers."""

    def test_assertion_helpers(self):
        """Example of using custom assertion helpers."""
        mock = Mock()

        # Call with different arguments
        mock(1, 2)
        mock(3, 4)
        mock(5, 6)

        # Use custom assertion helper
        AssertHelpers.assert_called_with_any_of(
            mock, ((3, 4),), ((7, 8),)  # This one should match  # This one won't
        )

        # Assert NOT called with specific args
        AssertHelpers.assert_not_called_with(mock, ((9, 10),), ((11, 12),))

    def test_range_assertions(self):
        """Example of range assertions."""
        zoom_level = 1.5

        # Assert value is in valid range
        AssertHelpers.assert_in_range(zoom_level, 0.1, 10.0)

        # This would fail:
        # AssertHelpers.assert_in_range(zoom_level, 2.0, 10.0)


# Example of using test configuration
def test_using_config():
    """Example of using TestConfig."""
    # Get sample PDF path
    _ = TestConfig.get_sample_pdf_path()  # pdf_path

    # Get output directory for test artifacts
    _ = TestConfig.get_test_output_dir()  # output_dir

    # Check environment
    if TestConfig.CI_MODE:
        # Running in CI, adjust behavior
        pass

    # Check if performance tests are enabled
    if TestConfig.PERFORMANCE_TEST_ENABLED:
        # Run additional performance checks
        pass

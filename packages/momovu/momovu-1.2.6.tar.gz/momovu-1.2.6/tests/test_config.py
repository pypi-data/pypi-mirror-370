"""Test configuration and settings.

This module centralizes test configuration to make it easy to adjust
test behavior across the entire test suite.
"""

import os
from pathlib import Path
from typing import Any


class TestConfig:
    """Centralized test configuration."""

    # Test environment
    TEST_ENV = os.environ.get("TEST_ENV", "local")
    CI_MODE = os.environ.get("CI", "false").lower() == "true"

    # Test paths
    TEST_DIR = Path(__file__).parent
    PROJECT_ROOT = TEST_DIR.parent
    FIXTURES_DIR = TEST_DIR / "fixtures"
    TEST_DATA_DIR = TEST_DIR / "test_data"

    # Performance settings
    PERFORMANCE_TEST_ENABLED = os.environ.get("PERF_TEST", "false").lower() == "true"
    MAX_TEST_DURATION = 5.0  # seconds

    # Coverage settings
    MIN_COVERAGE_PERCENT = 75
    COVERAGE_FAIL_UNDER = MIN_COVERAGE_PERCENT if CI_MODE else 0

    # Mock settings
    MOCK_RENDER_DELAY = 0.001  # Simulated render delay for performance tests
    MOCK_PDF_LOAD_DELAY = 0.01  # Simulated PDF load delay

    # Qt settings
    QT_API = "pyside6"
    QT_OFFSCREEN = True  # Run Qt tests without display

    # Logging
    TEST_LOG_LEVEL = os.environ.get("TEST_LOG_LEVEL", "WARNING")
    CAPTURE_LOGS = True

    # Timeouts
    DEFAULT_TIMEOUT = 5.0
    RENDER_TIMEOUT = 2.0
    LOAD_TIMEOUT = 3.0

    @classmethod
    def get_sample_pdf_path(cls) -> Path:
        """Get path to a sample PDF for testing."""
        # Try to find a sample PDF in the project
        sample_paths = [
            cls.PROJECT_ROOT / "samples" / "bovary-interior.pdf",
            cls.PROJECT_ROOT / "samples" / "bovary-cover.pdf",
            cls.TEST_DATA_DIR / "sample.pdf",
        ]

        for path in sample_paths:
            if path.exists():
                return path

        # Return a dummy path if no sample found
        return Path("/tmp/test_sample.pdf")

    @classmethod
    def get_test_output_dir(cls) -> Path:
        """Get directory for test output files."""
        output_dir = cls.TEST_DIR / "test_output"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    @classmethod
    def should_skip_slow_tests(cls) -> bool:
        """Check if slow tests should be skipped."""
        return os.environ.get("SKIP_SLOW", "false").lower() == "true"

    @classmethod
    def should_skip_gui_tests(cls) -> bool:
        """Check if GUI tests should be skipped."""
        return os.environ.get("SKIP_GUI", "false").lower() == "true"

    @classmethod
    def get_pytest_args(cls) -> dict[str, Any]:
        """Get pytest configuration arguments."""
        args = {
            "tb": "short",  # Traceback format
            "strict": True,  # Strict marker checking
            "verbose": 1 if not cls.CI_MODE else 0,
        }

        if cls.CI_MODE:
            args["quiet"] = True
            args["no_header"] = True

        return args


# Test markers
class TestMarkers:
    """Pytest markers for categorizing tests."""

    SLOW = "slow: marks tests as slow running"
    GUI = "gui: marks tests that require GUI"
    INTEGRATION = "integration: marks integration tests"
    UNIT = "unit: marks unit tests"
    PERFORMANCE = "performance: marks performance tests"
    SMOKE = "smoke: marks smoke tests for quick validation"

    @classmethod
    def get_all_markers(cls) -> list[str]:
        """Get all defined markers."""
        return [
            cls.SLOW,
            cls.GUI,
            cls.INTEGRATION,
            cls.UNIT,
            cls.PERFORMANCE,
            cls.SMOKE,
        ]


# Test categories for organization
class TestCategories:
    """Test categories for better organization."""

    RENDERING = "rendering"
    NAVIGATION = "navigation"
    DOCUMENT = "document"
    UI_STATE = "ui_state"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"

    @classmethod
    def get_category_patterns(cls) -> dict[str, str]:
        """Get file patterns for each category."""
        return {
            cls.RENDERING: "test_*render*.py",
            cls.NAVIGATION: "test_*nav*.py",
            cls.DOCUMENT: "test_*doc*.py",
            cls.UI_STATE: "test_*ui*.py",
            cls.ERROR_HANDLING: "test_*error*.py",
            cls.INTEGRATION: "test_integration*.py",
            cls.PERFORMANCE: "test_perf*.py",
        }


# Performance benchmarks
class PerformanceBenchmarks:
    """Performance benchmarks for tests."""

    # Maximum acceptable durations in seconds
    PAGE_RENDER_MAX = 0.1
    DOCUMENT_LOAD_MAX = 0.5
    VIEW_UPDATE_MAX = 0.05
    ZOOM_OPERATION_MAX = 0.02
    NAVIGATION_MAX = 0.01

    @classmethod
    def check_performance(cls, operation: str, duration: float) -> bool:
        """Check if performance meets benchmark."""
        benchmarks = {
            "page_render": cls.PAGE_RENDER_MAX,
            "document_load": cls.DOCUMENT_LOAD_MAX,
            "view_update": cls.VIEW_UPDATE_MAX,
            "zoom": cls.ZOOM_OPERATION_MAX,
            "navigation": cls.NAVIGATION_MAX,
        }

        max_duration = benchmarks.get(operation, 1.0)
        return duration <= max_duration

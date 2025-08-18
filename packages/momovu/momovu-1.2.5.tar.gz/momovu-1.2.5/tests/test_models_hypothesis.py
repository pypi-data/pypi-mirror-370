"""Property-based tests for Momovu models using Hypothesis.

This module demonstrates how to use Hypothesis for testing model
invariants, validations, and state transitions.
"""

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel

# Import our custom strategies
from tests.hypothesis_strategies import (
    any_page_count,
    document_types,
    margin_settings,
    margin_sizes_mm,
    page_dimensions,
    pdf_file_paths,
    view_states,
    zoom_levels,
)


class TestDocumentModelProperties:
    """Property-based tests for the Document model."""

    @given(
        page_count=st.integers(min_value=0, max_value=10000),
        page_sizes=st.lists(page_dimensions, min_size=0, max_size=100),
    )
    def test_document_consistency(self, page_count, page_sizes):
        """Property: Document state remains internally consistent."""
        doc = Document()

        # Set properties
        doc.page_count = page_count
        doc.page_sizes = page_sizes

        # Properties to verify:
        # 1. Page count is always non-negative
        assert doc.page_count >= 0

        # 2. Page sizes list length matches what was set
        assert len(doc.page_sizes) == len(page_sizes)

        # 3. get_page_size returns None for out-of-bounds indices
        assert doc.get_page_size(-1) is None
        assert doc.get_page_size(len(page_sizes)) is None
        assert doc.get_page_size(page_count + 100) is None

    @given(
        file_path=pdf_file_paths(),
        page_count=any_page_count,
        page_sizes=st.lists(page_dimensions, min_size=1, max_size=100),
    )
    def test_document_update_from_info(self, file_path, page_count, page_sizes):
        """Property: update_from_document_info correctly updates all fields."""
        doc = Document()

        # Ensure page_sizes matches page_count
        if len(page_sizes) > page_count:
            page_sizes = page_sizes[:page_count]
        elif len(page_sizes) < page_count:
            page_sizes = page_sizes * (page_count // len(page_sizes) + 1)
            page_sizes = page_sizes[:page_count]

        doc.update_from_document_info(
            file_path=file_path, page_count=page_count, page_sizes=page_sizes
        )

        # Verify all properties were set correctly
        assert doc.file_path == file_path
        assert doc.page_count == page_count
        assert doc.page_sizes == page_sizes
        assert doc.is_loaded is True
        assert doc.error_message is None

    @given(page_count=st.integers(min_value=-100, max_value=-1))
    def test_document_negative_page_count_validation(self, page_count):
        """Property: Document rejects negative page counts."""
        doc = Document()
        doc.page_count = 10  # Set a valid initial value

        # Should reject negative values
        result = doc.set_property("page_count", page_count)
        assert result is False
        assert doc.page_count == 10  # Value unchanged

    @given(error_message=st.text(min_size=1, max_size=200))
    def test_document_error_state(self, error_message):
        """Property: Setting error always sets is_loaded to False."""
        doc = Document()
        doc.is_loaded = True

        doc.set_error(error_message)

        assert doc.is_loaded is False
        assert doc.error_message == error_message

    def test_document_clear_resets_all(self):
        """Property: clear() always resets document to initial state."""
        doc = Document()

        # Set various properties
        doc.file_path = "/test/path.pdf"
        doc.page_count = 100
        doc.page_sizes = [(612, 792)] * 100
        doc.is_loaded = True
        doc.error_message = "Some error"

        # Clear should reset everything
        doc.clear()

        assert doc.file_path is None
        assert doc.page_count == 0
        assert doc.page_sizes == []
        assert doc.is_loaded is False
        assert doc.error_message is None


class TestMarginSettingsModelProperties:
    """Property-based tests for MarginSettingsModel."""

    @given(settings=margin_settings())
    def test_margin_settings_validation(self, settings):
        """Property: All valid margin settings are accepted."""
        model = MarginSettingsModel()

        # Apply all settings
        for key, value in settings.items():
            if hasattr(model, key):
                setattr(model, key, value)

        # Verify settings were applied
        for key, value in settings.items():
            if hasattr(model, key):
                assert getattr(model, key) == value

    @given(margin_mm=st.floats(min_value=-100.0, max_value=-0.1))
    def test_negative_margin_validation(self, margin_mm):
        """Property: Negative margins are always rejected."""
        model = MarginSettingsModel()
        original = model.safety_margin_mm

        result = model.set_property("safety_margin_mm", margin_mm)

        assert result is False
        assert model.safety_margin_mm == original

    @given(num_pages=st.integers(min_value=1, max_value=10000))
    def test_num_pages_always_positive(self, num_pages):
        """Property: Valid page counts are always accepted."""
        model = MarginSettingsModel()

        result = model.set_property("num_pages", num_pages)

        assert result is True
        assert model.num_pages == num_pages

    @given(
        doc_type=st.text(min_size=1).filter(
            lambda x: x not in ["interior", "cover", "dustjacket"]
        )
    )
    def test_invalid_document_type_rejected(self, doc_type):
        """Property: Invalid document types are always rejected."""
        model = MarginSettingsModel()
        original = model.document_type

        result = model.set_property("document_type", doc_type)

        assert result is False
        assert model.document_type == original

    @given(
        doc_type=document_types, spine_width=st.floats(min_value=0.1, max_value=200.0)
    )
    def test_spine_width_consistency(self, doc_type, spine_width):
        """Property: Spine width is relevant only for covers and dustjackets."""
        model = MarginSettingsModel()
        model.document_type = doc_type
        model.spine_width = spine_width

        if doc_type == "interior":
            # Interior documents might ignore spine width in rendering
            pass  # No assertion needed, just checking it doesn't crash
        else:
            # Covers and dustjackets should maintain spine width
            assert model.spine_width == spine_width


class TestViewStateModelProperties:
    """Property-based tests for ViewStateModel."""

    @given(
        current_page=st.integers(min_value=0, max_value=10000),
        total_pages=st.integers(min_value=1, max_value=10000),
    )
    def test_current_page_validation(self, current_page, total_pages):
        """Property: Current page must be non-negative."""
        model = ViewStateModel()

        # Set current page
        result = model.set_property("current_page", current_page)

        if current_page >= 0:
            assert result is True
            assert model.current_page == current_page
        else:
            assert result is False
            assert model.current_page == 0  # Default value

    @given(zoom=zoom_levels)
    def test_zoom_level_bounds(self, zoom):
        """Property: Zoom levels are constrained to valid range."""
        model = ViewStateModel()

        result = model.set_property("zoom_level", zoom)

        if 0.1 <= zoom <= 10.0:
            assert result is True
            assert model.zoom_level == zoom
        else:
            assert result is False

    @given(
        zoom_too_small=st.floats(max_value=0.09, min_value=0.0, exclude_min=True),
        zoom_too_large=st.floats(min_value=10.01, max_value=100.0),
    )
    def test_zoom_level_out_of_bounds(self, zoom_too_small, zoom_too_large):
        """Property: Out-of-bounds zoom levels are rejected."""
        model = ViewStateModel()
        original = model.zoom_level

        # Test too small
        result = model.set_property("zoom_level", zoom_too_small)
        assert result is False
        assert model.zoom_level == original

        # Test too large
        result = model.set_property("zoom_level", zoom_too_large)
        assert result is False
        assert model.zoom_level == original

    def test_view_mode_toggle_is_involutive(self):
        """Property: Toggling view mode twice returns to original state."""
        model = ViewStateModel()

        original_mode = model.view_mode

        # Toggle twice
        model.toggle_view_mode()
        model.toggle_view_mode()

        assert model.view_mode == original_mode

    @given(
        flags=st.fixed_dictionaries(
            {
                "show_margins": st.booleans(),
                "show_trim_lines": st.booleans(),
                "show_spine_line": st.booleans(),
                "show_fold_lines": st.booleans(),
                "show_barcode": st.booleans(),
                "is_fullscreen": st.booleans(),
                "is_presentation": st.booleans(),
            }
        )
    )
    def test_boolean_flags_independence(self, flags):
        """Property: Boolean flags can be set independently."""
        model = ViewStateModel()

        # Set all flags
        for flag, value in flags.items():
            setattr(model, flag, value)

        # Verify all flags maintained their values
        for flag, value in flags.items():
            assert getattr(model, flag) == value


class MarginSettingsStateMachine(RuleBasedStateMachine):
    """Stateful testing for MarginSettingsModel.

    This tests that the model maintains consistency through
    various sequences of operations.
    """

    def __init__(self):
        super().__init__()
        self.model = MarginSettingsModel()

    @initialize()
    def setup(self):
        """Initialize with a known state."""
        self.model = MarginSettingsModel()

    @rule(doc_type=document_types)
    def change_document_type(self, doc_type):
        """Rule: Can change document type."""
        self.model.document_type = doc_type

    @rule(margin=margin_sizes_mm)
    def set_margin(self, margin):
        """Rule: Can set valid margins."""
        self.model.set_property("safety_margin_mm", margin)

    @rule(pages=st.integers(min_value=1, max_value=5000))
    def set_page_count(self, pages):
        """Rule: Can set page count."""
        self.model.num_pages = pages

    @rule(show=st.booleans())
    def toggle_visibility(self, show):
        """Rule: Can toggle visibility flags."""
        self.model.show_margins = show
        self.model.show_trim_lines = show

    @invariant()
    def margins_non_negative(self):
        """Invariant: Margins are never negative."""
        assert self.model.safety_margin_mm >= 0
        assert self.model.safety_margin_points >= 0

    @invariant()
    def page_count_positive(self):
        """Invariant: Page count is always positive."""
        assert self.model.num_pages > 0

    @invariant()
    def document_type_valid(self):
        """Invariant: Document type is always valid."""
        assert self.model.document_type in ["interior", "cover", "dustjacket"]

    @invariant()
    def spine_width_consistency(self):
        """Invariant: Spine width rules are maintained."""
        if self.model.document_type == "interior":
            # Interior can have None spine width
            pass
        elif self.model.spine_width is not None:
            # If set, spine width should be positive
            assert self.model.spine_width >= 0


# Create test case from state machine
TestMarginSettingsStateMachine = MarginSettingsStateMachine.TestCase


class ViewStateStateMachine(RuleBasedStateMachine):
    """Stateful testing for ViewStateModel navigation."""

    def __init__(self):
        super().__init__()
        self.model = ViewStateModel()
        self.total_pages = 100  # Fixed for this test

    @rule(page=st.integers(min_value=0, max_value=99))
    def go_to_page(self, page):
        """Rule: Can navigate to any valid page."""
        self.model.current_page = page

    @rule()
    def toggle_view_mode(self):
        """Rule: Can toggle view mode."""
        self.model.toggle_view_mode()

    @rule(zoom=zoom_levels)
    def set_zoom(self, zoom):
        """Rule: Can set zoom level."""
        self.model.set_property("zoom_level", zoom)

    @rule()
    def toggle_fullscreen(self):
        """Rule: Can toggle fullscreen."""
        self.model.is_fullscreen = not self.model.is_fullscreen

    @invariant()
    def current_page_in_bounds(self):
        """Invariant: Current page is always valid."""
        assert 0 <= self.model.current_page < self.total_pages

    @invariant()
    def zoom_in_valid_range(self):
        """Invariant: Zoom is always in valid range."""
        assert 0.1 <= self.model.zoom_level <= 10.0

    @invariant()
    def view_mode_valid(self):
        """Invariant: View mode is always valid."""
        assert self.model.view_mode in ["single", "side_by_side"]


# Create test case from state machine
TestViewStateStateMachine = ViewStateStateMachine.TestCase


# Example of combining property-based tests with fixtures
class TestModelIntegration:
    """Integration tests combining multiple models with property-based testing."""

    @given(doc_settings=margin_settings(), view_settings=view_states())
    def test_model_independence(self, doc_settings, view_settings):
        """Property: Models can be updated independently without interference."""
        # Create models
        margin_model = MarginSettingsModel()
        view_model = ViewStateModel()

        # Apply settings to margin model
        for key, value in doc_settings.items():
            if hasattr(margin_model, key):
                setattr(margin_model, key, value)

        # Apply settings to view model
        for key, value in view_settings.items():
            if hasattr(view_model, key):
                setattr(view_model, key, value)

        # Verify settings don't interfere
        for key, value in doc_settings.items():
            if hasattr(margin_model, key):
                assert getattr(margin_model, key) == value

        for key, value in view_settings.items():
            if hasattr(view_model, key):
                assert getattr(view_model, key) == value


# Performance-related property tests
class TestModelPerformance:
    """Property tests focused on performance characteristics."""

    @settings(deadline=100)  # 100ms deadline
    @given(
        updates=st.lists(
            st.tuples(
                st.sampled_from(["safety_margin_mm", "num_pages", "show_margins"]),
                st.one_of(margin_sizes_mm, any_page_count, st.booleans()),
            ),
            min_size=100,
            max_size=1000,
        )
    )
    def test_bulk_updates_performance(self, updates):
        """Property: Bulk updates complete within reasonable time."""
        model = MarginSettingsModel()

        # This should complete quickly even with many updates
        for prop_name, value in updates:
            if prop_name in ["safety_margin_mm", "num_pages"]:
                model.set_property(
                    prop_name, abs(value) if isinstance(value, (int, float)) else value
                )
            else:
                model.set_property(prop_name, value)

    @settings(deadline=50, suppress_health_check=[HealthCheck.large_base_example])
    @given(page_sizes=st.lists(page_dimensions, min_size=100, max_size=500))
    def test_large_document_handling(self, page_sizes):
        """Property: Large documents are handled efficiently."""
        doc = Document()

        # This should handle large page lists efficiently
        doc.page_count = len(page_sizes)
        doc.page_sizes = page_sizes

        # Random access should be fast
        for _ in range(10):
            idx = len(page_sizes) // 2
            size = doc.get_page_size(idx)
            if idx < len(page_sizes):
                assert size == page_sizes[idx]

"""Property-based tests for presenters using Hypothesis."""

from unittest.mock import Mock

import hypothesis.strategies as st
from hypothesis import given
from PySide6.QtCore import QSizeF
from PySide6.QtPdf import QPdfDocument

from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter

# Import custom strategies
from tests.hypothesis_strategies import margin_settings


class TestNavigationPresenterExtended:
    """Extended property-based tests for NavigationPresenter."""

    @given(
        pages=st.integers(min_value=1, max_value=10000),
        view_mode=st.sampled_from(["single", "side_by_side"]),
    )
    def test_view_mode_page_adjustment(self, pages, view_mode):
        """Property: Side-by-side mode adjusts to even pages."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)
        presenter.set_total_pages(pages)
        presenter.set_view_mode(view_mode)

        # Navigate to odd page
        if pages > 1:
            presenter.go_to_page(1)  # Page 2 (0-indexed)
            current = presenter.get_current_page()

            if view_mode == "side_by_side":
                # Should adjust to even page (0-indexed)
                assert current % 2 == 0
            else:
                # Should stay on requested page
                assert current == 1

    @given(
        total_pages=st.integers(min_value=1, max_value=1000),
        actions=st.lists(
            st.sampled_from(["next", "previous", "first", "last", "goto"]),
            min_size=1,
            max_size=10,
        ),
    )
    def test_navigation_state_consistency(self, total_pages, actions):
        """Property: Navigation state remains consistent."""
        model = ViewStateModel()
        presenter = NavigationPresenter(model)

        # Set up initial state
        presenter.set_total_pages(total_pages)

        # Execute navigation sequence
        for action in actions:
            if action == "next":
                presenter.next_page()
            elif action == "previous":
                presenter.previous_page()
            elif action == "first":
                presenter.go_to_first_page()
            elif action == "last":
                presenter.go_to_last_page()
            elif action == "goto":
                # Go to a random valid page
                target = min(total_pages - 1, max(0, presenter.get_current_page()))
                presenter.go_to_page(target)

        # Verify invariants
        current = presenter.get_current_page()
        assert 0 <= current < total_pages
        assert presenter.get_total_pages() == total_pages


class TestMarginPresenterExtended:
    """Extended property-based tests for MarginPresenter."""

    @given(
        margin_mm=st.floats(min_value=0.0, max_value=100.0),
        margin_points=st.floats(min_value=0.0, max_value=288.0),
    )
    def test_margin_unit_independence(self, margin_mm, margin_points):
        """Property: Margin units can be set independently through model."""
        model = MarginSettingsModel()
        _ = MarginPresenter(model)  # Create presenter to ensure model is initialized

        # Set margins through model (presenter doesn't expose these methods)
        model.safety_margin_mm = margin_mm
        assert model.safety_margin_mm == margin_mm

        # Setting points doesn't affect mm (they're independent in the model)
        model.safety_margin_points = margin_points
        assert model.safety_margin_points == margin_points

    @given(
        pages=st.integers(min_value=1, max_value=5000),
        spine_calc=st.sampled_from([6.0, 8.0, 10.0]),  # Common calculations
        doc_type=st.sampled_from(
            ["cover", "dustjacket"]
        ),  # Only these types have spine width
    )
    def test_spine_width_calculation(self, pages, spine_calc, doc_type):
        """Property: Spine width calculations are reasonable."""
        model = MarginSettingsModel()
        presenter = MarginPresenter(model)

        # Set document type first - spine width is only calculated for cover/dustjacket
        presenter.set_document_type(doc_type)
        presenter.set_num_pages(pages)

        # Spine width should be positive and reasonable
        assert model.spine_width is not None
        assert model.spine_width > 0
        # Very rough check - actual calculation is more complex
        # For dustjackets, even 1-page books have a minimum spine width
        # For covers, spine width is calculated differently
        if doc_type == "dustjacket":
            # Dustjackets have a minimum spine width even for thin books
            assert model.spine_width < max(pages * 2, 100)  # More reasonable limit
        else:
            # Covers use a formula-based calculation
            assert model.spine_width < pages + 50  # Account for offset in formula


class TestDocumentPresenterExtended:
    """Extended property-based tests for DocumentPresenter."""

    @given(
        page_sizes=st.lists(
            st.tuples(
                st.floats(min_value=100.0, max_value=2000.0),
                st.floats(min_value=100.0, max_value=2000.0),
            ),
            min_size=1,
            max_size=10,
        )
    )
    def test_page_size_retrieval(self, page_sizes):
        """Property: Page sizes are correctly retrieved."""
        model = Document()
        presenter = DocumentPresenter(model)

        # Create mock PDF document
        mock_pdf = Mock(spec=QPdfDocument)
        mock_pdf.pageCount.return_value = len(page_sizes)

        # Create all mock size objects first
        mock_sizes = []
        for width, height in page_sizes:
            mock_size = Mock(spec=QSizeF)
            mock_size.width.return_value = width
            mock_size.height.return_value = height
            mock_sizes.append(mock_size)

        # Configure pagePointSize to return the correct mock for each index
        def get_page_size(idx):
            if 0 <= idx < len(mock_sizes):
                return mock_sizes[idx]
            return None

        mock_pdf.pagePointSize.side_effect = get_page_size

        presenter.set_qt_document(mock_pdf)

        # Verify each page size
        for i, (expected_width, expected_height) in enumerate(page_sizes):
            size = presenter.get_page_size(i)
            assert size is not None
            assert abs(size[0] - expected_width) < 0.01
            assert abs(size[1] - expected_height) < 0.01

    @given(
        total_pages=st.integers(min_value=1, max_value=1000),
        start_page=st.integers(min_value=0),
        end_page=st.integers(min_value=0),
    )
    def test_page_range_validation(self, total_pages, start_page, end_page):
        """Property: Page ranges are properly validated."""
        model = Document()
        presenter = DocumentPresenter(model)

        # Set up document with known page count
        mock_pdf = Mock(spec=QPdfDocument)
        mock_pdf.pageCount.return_value = total_pages
        presenter.set_qt_document(mock_pdf)

        # Test range validation
        # Valid ranges should work
        if 0 <= start_page < total_pages and start_page <= end_page < total_pages:
            # Should not raise exception
            size = presenter.get_page_size(start_page)
            assert size is not None or start_page >= total_pages


class TestPresenterIntegration:
    """Integration tests for presenter interactions."""

    @given(
        settings=margin_settings(),
        pages=st.integers(min_value=1, max_value=1000),
    )
    def test_presenter_coordination(self, settings, pages):
        """Property: Presenters coordinate correctly."""
        # Create models
        doc_model = Document()
        margin_model = MarginSettingsModel()
        nav_model = ViewStateModel()

        # Create presenters
        doc_presenter = DocumentPresenter(doc_model)
        margin_presenter = MarginPresenter(margin_model)
        nav_presenter = NavigationPresenter(nav_model)

        # Set up document
        mock_pdf = Mock(spec=QPdfDocument)
        mock_pdf.pageCount.return_value = pages
        doc_presenter.set_qt_document(mock_pdf)

        # Configure navigation
        nav_presenter.set_total_pages(pages)

        # Configure margins
        margin_presenter.set_document_type(settings["document_type"])
        margin_presenter.set_num_pages(settings["num_pages"])

        # Verify coordination
        assert nav_presenter.get_total_pages() == pages
        assert margin_presenter.get_document_type() == settings["document_type"]
        assert 0 <= nav_presenter.get_current_page() < pages

    @given(
        invalid_pages=st.integers(max_value=0),
        invalid_margins=st.floats(max_value=-0.1),
    )
    def test_presenter_validation(self, invalid_pages, invalid_margins):
        """Property: Presenters handle invalid inputs gracefully."""
        margin_model = MarginSettingsModel()
        _ = MarginPresenter(margin_model)  # Create presenter to ensure initialization

        # Store original values
        original_pages = margin_model.num_pages
        original_margin = margin_model.safety_margin_mm

        # Try to set invalid values through model
        result = margin_model.set_property("num_pages", invalid_pages)
        assert result is False  # Should reject

        result = margin_model.set_property("safety_margin_mm", invalid_margins)
        assert result is False  # Should reject

        # Values should remain unchanged
        assert margin_model.num_pages == original_pages
        assert margin_model.safety_margin_mm == original_margin

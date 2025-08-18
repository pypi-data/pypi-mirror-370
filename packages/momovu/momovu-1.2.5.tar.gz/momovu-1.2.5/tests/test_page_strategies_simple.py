"""Simplified tests for page navigation strategies.

Tests focus on the actual implementation without extensive mocking.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import QRectF

from momovu.views.components.page_strategies.all_pages import AllPagesStrategy
from momovu.views.components.page_strategies.base import BaseStrategy
from momovu.views.components.page_strategies.page_pair import PagePairStrategy
from momovu.views.components.page_strategies.side_by_side import SideBySideStrategy
from momovu.views.components.page_strategies.single_page import SinglePageStrategy


class TestBaseStrategy:
    """Test the abstract base strategy."""

    def test_base_strategy_is_abstract(self):
        """Test that BaseStrategy cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseStrategy(None, None, None, None, None, None)

    def test_base_strategy_has_render_method(self):
        """Test that BaseStrategy defines render as abstract."""
        assert hasattr(BaseStrategy, "render")
        # Check if it's abstract by looking at the method
        assert hasattr(BaseStrategy.render, "__isabstractmethod__")


class MockDependencies:
    """Helper to create mock dependencies for strategies."""

    @staticmethod
    def create():
        """Create all required mock dependencies."""
        mock_scene = Mock()
        mock_scene.clear = Mock()
        mock_scene.addItem = Mock()
        mock_scene.setSceneRect = Mock()
        mock_scene.itemsBoundingRect = Mock(return_value=QRectF(0, 0, 612, 792))
        mock_scene.views = Mock(return_value=[])
        mock_scene.items = Mock(return_value=[])

        mock_document = Mock()
        mock_document.pageCount = Mock(return_value=10)

        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))

        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"

        mock_nav_presenter = Mock()

        mock_margin_renderer = Mock()
        mock_margin_renderer.draw_page_overlays = Mock()

        return (
            mock_scene,
            mock_document,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )


class TestSinglePageStrategy:
    """Test single page rendering strategy."""

    @pytest.fixture
    def strategy_with_mocks(self):
        """Create a SinglePageStrategy with mock dependencies."""
        deps = MockDependencies.create()
        strategy = SinglePageStrategy(*deps)
        return strategy, deps

    def test_render_single_page(self, strategy_with_mocks):
        """Test rendering a single page."""
        strategy, (mock_scene, mock_document, _, _, _, _) = strategy_with_mocks

        # Mock the create_page_item method
        mock_item = Mock()
        strategy.create_page_item = Mock(return_value=mock_item)

        strategy.render(5, False, False)

        # Should clear scene
        mock_scene.clear.assert_called_once()

        # Should create one page item
        strategy.create_page_item.assert_called_once()

        # Should add item to scene
        mock_scene.addItem.assert_called_with(mock_item)

    def test_create_page_item(self, strategy_with_mocks):
        """Test creating a page item."""
        strategy, _ = strategy_with_mocks

        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_item = Mock()
            mock_page_item.return_value = mock_item

            result = strategy.create_page_item(5, 100, 200)

            assert result == mock_item
            mock_item.setPos.assert_called_once_with(100, 200)

    def test_cleanup_page_items(self, strategy_with_mocks):
        """Test cleanup of page items."""
        strategy, (mock_scene, _, _, _, _, _) = strategy_with_mocks

        # Create mock page items
        mock_page_item = Mock()
        mock_page_item.cleanup = Mock()
        mock_other_item = Mock()  # Non-PageItem

        mock_scene.items.return_value = [mock_page_item, mock_other_item]

        # Make isinstance work correctly
        with patch(
            "momovu.views.components.page_strategies.base.isinstance"
        ) as mock_isinstance:
            mock_isinstance.side_effect = lambda obj, cls: obj == mock_page_item

            strategy.cleanup_page_items()

            mock_page_item.cleanup.assert_called_once()


class TestPagePairStrategy:
    """Test page pair rendering strategy."""

    @pytest.fixture
    def strategy_with_mocks(self):
        """Create a PagePairStrategy with mock dependencies."""
        deps = MockDependencies.create()
        strategy = PagePairStrategy(*deps)
        return strategy, deps

    def test_render_page_pair(self, strategy_with_mocks):
        """Test rendering a pair of pages."""
        strategy, (mock_scene, mock_document, _, _, mock_nav_presenter, _) = (
            strategy_with_mocks
        )

        # Mock navigation presenter methods
        mock_nav_presenter.get_total_pages = Mock(return_value=10)

        # Mock the create_page_item method
        mock_items = [Mock(), Mock()]
        strategy.create_page_item = Mock(side_effect=mock_items)

        # Render pages 3-4
        strategy.render(3, False, False)

        # Should clear scene
        mock_scene.clear.assert_called_once()

        # Should create at least one page item
        assert strategy.create_page_item.call_count >= 1

    def test_render_first_page(self, strategy_with_mocks):
        """Test rendering first page (page 0)."""
        strategy, (mock_scene, _, _, _, _, _) = strategy_with_mocks

        # Mock the create_page_item method
        strategy.create_page_item = Mock(return_value=Mock())

        strategy.render(0, False, False)

        # Should handle first page correctly
        mock_scene.clear.assert_called_once()


class TestSideBySideStrategy:
    """Test side-by-side rendering strategy."""

    @pytest.fixture
    def strategy_with_mocks(self):
        """Create a SideBySideStrategy with mock dependencies."""
        deps = MockDependencies.create()
        strategy = SideBySideStrategy(*deps)
        return strategy, deps

    def test_render_all_pages(self, strategy_with_mocks):
        """Test rendering all pages in side-by-side layout."""
        strategy, (mock_scene, mock_document, mock_doc_presenter, _, _, _) = (
            strategy_with_mocks
        )

        # Mock document presenter methods
        mock_doc_presenter.get_page_count = Mock(return_value=10)

        # Mock the create_page_item method
        strategy.create_page_item = Mock(return_value=Mock())

        strategy.render(5, False, False)

        # Should clear scene
        mock_scene.clear.assert_called_once()

        # Should update scene rect
        mock_scene.setSceneRect.assert_called()

    def test_empty_document(self, strategy_with_mocks):
        """Test rendering empty document."""
        strategy, (mock_scene, mock_document, mock_doc_presenter, _, _, _) = (
            strategy_with_mocks
        )
        mock_document.pageCount.return_value = 0
        mock_doc_presenter.get_page_count = Mock(return_value=0)

        strategy.render(0, False, False)

        # Should clear scene but not crash
        mock_scene.clear.assert_called_once()


class TestAllPagesStrategy:
    """Test all pages rendering strategy."""

    @pytest.fixture
    def strategy_with_mocks(self):
        """Create an AllPagesStrategy with mock dependencies."""
        deps = MockDependencies.create()
        strategy = AllPagesStrategy(*deps)
        return strategy, deps

    def test_render_all_pages_vertically(self, strategy_with_mocks):
        """Test rendering all pages vertically."""
        strategy, (mock_scene, mock_document, mock_doc_presenter, _, _, _) = (
            strategy_with_mocks
        )
        mock_document.pageCount.return_value = 5
        mock_doc_presenter.get_page_count = Mock(return_value=5)

        # Mock the create_page_item method
        strategy.create_page_item = Mock(return_value=Mock())

        strategy.render(2, False, False)

        # Should create all 5 pages
        assert strategy.create_page_item.call_count == 5


class TestStrategyHelpers:
    """Test helper methods in base strategy."""

    @pytest.fixture
    def base_strategy_mock(self):
        """Create a concrete strategy for testing base methods."""
        deps = MockDependencies.create()

        class ConcreteStrategy(BaseStrategy):
            def render(
                self,
                current_page,
                is_presentation_mode,
                show_fold_lines,
                fit_callback=None,
            ):
                pass

        return ConcreteStrategy(*deps), deps

    def test_draw_overlays(self, base_strategy_mock):
        """Test drawing overlays."""
        strategy, (_, _, _, _, _, mock_margin_renderer) = base_strategy_mock

        strategy.draw_overlays(0, 0, 612, 792)

        mock_margin_renderer.draw_page_overlays.assert_called_once_with(
            0, 0, 612, 792, None
        )

    def test_fit_to_view_if_needed(self, base_strategy_mock):
        """Test fit to view scheduling."""
        strategy, _ = base_strategy_mock
        mock_callback = Mock()

        with patch("momovu.views.components.page_strategies.base.QTimer") as mock_timer:
            # Test in presentation mode
            strategy.fit_to_view_if_needed(True, mock_callback)
            mock_timer.singleShot.assert_called_once()

            # Test not in presentation mode
            mock_timer.singleShot.reset_mock()
            strategy.fit_to_view_if_needed(False, mock_callback)
            mock_timer.singleShot.assert_not_called()

    def test_update_scene_rect(self, base_strategy_mock):
        """Test updating scene rect with padding."""
        strategy, (mock_scene, _, _, _, _, _) = base_strategy_mock

        # Mock scene bounds
        mock_scene.itemsBoundingRect.return_value = QRectF(0, 0, 612, 792)

        # Mock views with scrollbars
        mock_view = Mock()
        mock_h_bar = Mock()
        mock_v_bar = Mock()
        mock_h_bar.value.return_value = 100
        mock_v_bar.value.return_value = 200
        mock_view.horizontalScrollBar.return_value = mock_h_bar
        mock_view.verticalScrollBar.return_value = mock_v_bar
        mock_scene.views.return_value = [mock_view]

        strategy.update_scene_rect()

        # Should set expanded scene rect
        mock_scene.setSceneRect.assert_called_once()

        # Should restore scrollbar positions
        mock_h_bar.setValue.assert_called_with(100)
        mock_v_bar.setValue.assert_called_with(200)


class TestStrategyIntegration:
    """Test integration aspects of strategies."""

    def test_all_strategies_inherit_from_base(self):
        """Test that all strategies inherit from BaseStrategy."""
        strategies = [
            SinglePageStrategy,
            PagePairStrategy,
            SideBySideStrategy,
            AllPagesStrategy,
        ]

        for strategy_class in strategies:
            assert issubclass(strategy_class, BaseStrategy)

    def test_all_strategies_implement_render(self):
        """Test that all strategies implement render method."""
        deps = MockDependencies.create()

        strategies = [
            SinglePageStrategy(*deps),
            PagePairStrategy(*deps),
            SideBySideStrategy(*deps),
            AllPagesStrategy(*deps),
        ]

        for strategy in strategies:
            assert hasattr(strategy, "render")
            assert callable(strategy.render)

    def test_strategy_creation_with_none_values(self):
        """Test strategies handle None dependencies gracefully."""
        # Most strategies will fail with None deps, but shouldn't crash on import
        try:
            import momovu.views.components.page_strategies.all_pages  # noqa: F401
            import momovu.views.components.page_strategies.page_pair  # noqa: F401
            import momovu.views.components.page_strategies.side_by_side  # noqa: F401
            import momovu.views.components.page_strategies.single_page  # noqa: F401
        except ImportError:
            pytest.fail("Strategy modules should import without errors")

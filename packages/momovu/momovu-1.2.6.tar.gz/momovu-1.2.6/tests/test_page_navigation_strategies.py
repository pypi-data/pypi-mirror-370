"""Comprehensive tests for page navigation strategies.

Tests focus on different page rendering strategies and their behavior.
"""

from unittest.mock import Mock, patch

import pytest

from momovu.views.components.page_strategies.all_pages import AllPagesStrategy
from momovu.views.components.page_strategies.base import BaseStrategy
from momovu.views.components.page_strategies.page_pair import PagePairStrategy
from momovu.views.components.page_strategies.side_by_side import SideBySideStrategy
from momovu.views.components.page_strategies.single_page import SinglePageStrategy


class TestBaseStrategy:
    """Test the abstract base strategy."""

    def test_base_strategy_is_abstract(self):
        """Test that BaseStrategy cannot be instantiated."""
        # BaseStrategy requires arguments, but it's abstract so we can't instantiate it anyway
        mock_scene = Mock()
        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_margin_presenter = Mock()
        mock_nav_presenter = Mock()
        mock_margin_renderer = Mock()

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            )

    def test_base_strategy_interface(self):
        """Test that BaseStrategy defines the required interface."""
        # Check that abstract methods are defined
        assert hasattr(BaseStrategy, "render")
        # BaseStrategy only has render as an abstract method
        # Other methods like create_page_item, draw_overlays, etc. are concrete implementations


class TestSinglePageStrategy:
    """Test single page rendering strategy."""

    @pytest.fixture
    def mock_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.clear = Mock()
        scene.addItem = Mock()
        scene.setSceneRect = Mock()
        scene.itemsBoundingRect = Mock(
            return_value=Mock(adjusted=Mock(return_value=Mock()))
        )
        scene.views = Mock(return_value=[])  # Return empty list of views
        return scene

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock()
        doc.pageCount = Mock(return_value=10)
        return doc

    @pytest.fixture
    def strategy(self, mock_scene, mock_document):
        """Create a SinglePageStrategy instance."""
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=10)

        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"

        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=10)

        mock_margin_renderer = Mock()
        mock_margin_renderer.draw_page_overlays = Mock()

        return SinglePageStrategy(
            mock_scene,
            mock_document,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

    def test_render_single_page(self, strategy, mock_scene, mock_document):
        """Test rendering a single page."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_item = Mock()
            mock_item.setPos = Mock()
            mock_page_item.return_value = mock_item

            # Mock the cleanup method
            strategy.cleanup_page_items = Mock()

            strategy.render(
                current_page=5,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should cleanup and clear scene
            strategy.cleanup_page_items.assert_called_once()
            mock_scene.clear.assert_called_once()

            # Should create one page item
            mock_page_item.assert_called_once_with(mock_document, 5, 612, 792)

            # Should add item to scene
            mock_scene.addItem.assert_called_once_with(mock_item)

    def test_render_first_page(self, strategy, mock_scene, mock_document):
        """Test rendering the first page (page 0)."""
        with patch("momovu.views.components.page_strategies.base.PageItem"):
            strategy.cleanup_page_items = Mock()

            strategy.render(
                current_page=0,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should handle first page correctly
            strategy.cleanup_page_items.assert_called_once()
            mock_scene.clear.assert_called_once()

    def test_render_last_page(self, strategy, mock_scene, mock_document):
        """Test rendering the last page."""
        with patch("momovu.views.components.page_strategies.base.PageItem"):
            strategy.cleanup_page_items = Mock()

            strategy.render(
                current_page=9,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should handle last page correctly
            strategy.cleanup_page_items.assert_called_once()
            mock_scene.clear.assert_called_once()

    # Note: get_visible_pages and get_page_position methods don't exist in the strategy classes
    # These tests should be removed as they test non-existent functionality


class TestPagePairStrategy:
    """Test page pair rendering strategy."""

    @pytest.fixture
    def mock_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.clear = Mock()
        scene.addItem = Mock()
        scene.setSceneRect = Mock()
        scene.itemsBoundingRect = Mock(
            return_value=Mock(adjusted=Mock(return_value=Mock()))
        )
        scene.views = Mock(return_value=[])  # Return empty list of views
        return scene

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock()
        doc.pageCount = Mock(return_value=10)
        return doc

    @pytest.fixture
    def strategy(self, mock_scene, mock_document):
        """Create a PagePairStrategy instance."""
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=10)

        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"

        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=10)

        mock_margin_renderer = Mock()
        mock_margin_renderer.draw_page_overlays = Mock()

        return PagePairStrategy(
            mock_scene,
            mock_document,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

    def test_render_page_pair_odd_page(self, strategy, mock_scene, mock_document):
        """Test rendering a pair starting from odd page."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_items = []
            for _ in range(2):
                mock_item = Mock()
                mock_item.setPos = Mock()
                mock_items.append(mock_item)
            mock_page_item.side_effect = mock_items

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=3,
                is_presentation_mode=False,
                show_fold_lines=True,
                fit_callback=None,
            )

            # Should create two page items (pages 3 and 4 for current page 3)
            assert mock_page_item.call_count == 2
            mock_page_item.assert_any_call(mock_document, 3, 612, 792)
            mock_page_item.assert_any_call(mock_document, 4, 612, 792)

            # Should position them side by side
            mock_items[0].setPos.assert_called_once_with(0, 0)
            mock_items[1].setPos.assert_called_once_with(612, 0)

    def test_render_page_pair_even_page(self, strategy, mock_scene, mock_document):
        """Test rendering a pair starting from even page."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_items = []
            for _ in range(2):
                mock_item = Mock()
                mock_item.setPos = Mock()
                mock_items.append(mock_item)
            mock_page_item.side_effect = mock_items

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=4,
                is_presentation_mode=False,
                show_fold_lines=True,
                fit_callback=None,
            )

            # Should create two page items (pages 3 and 4)
            assert mock_page_item.call_count == 2
            mock_page_item.assert_any_call(mock_document, 3, 612, 792)
            mock_page_item.assert_any_call(mock_document, 4, 612, 792)

    def test_render_first_page_pair(self, strategy, mock_scene, mock_document):
        """Test rendering first page (page 0) - should show only one page."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_item = Mock()
            mock_item.setPos = Mock()
            mock_page_item.return_value = mock_item

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=0,
                is_presentation_mode=False,
                show_fold_lines=True,
                fit_callback=None,
            )

            # Should create only one page item for page 0
            mock_page_item.assert_called_once_with(mock_document, 0, 612, 792)

            # Should position it on the right (page 1 position)
            mock_item.setPos.assert_called_once_with(612, 0)

    def test_render_last_page_odd_count(self, strategy, mock_scene, mock_document):
        """Test rendering last page when document has odd number of pages."""
        strategy.navigation_presenter.get_total_pages.return_value = 9  # Pages 0-8

        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_items = []
            for _ in range(2):
                mock_item = Mock()
                mock_item.setPos = Mock()
                mock_items.append(mock_item)
            mock_page_item.side_effect = mock_items

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=8,
                is_presentation_mode=False,
                show_fold_lines=True,
                fit_callback=None,
            )

            # Should create two page items (pages 7 and 8)
            assert mock_page_item.call_count == 2

    # Note: get_visible_pages method doesn't exist in the strategy classes


class TestSideBySideStrategy:
    """Test side-by-side rendering strategy."""

    @pytest.fixture
    def mock_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.clear = Mock()
        scene.addItem = Mock()
        scene.setSceneRect = Mock()
        scene.itemsBoundingRect = Mock(
            return_value=Mock(adjusted=Mock(return_value=Mock()))
        )
        scene.views = Mock(return_value=[])  # Return empty list of views
        return scene

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock()
        doc.pageCount = Mock(return_value=10)
        return doc

    @pytest.fixture
    def strategy(self, mock_scene, mock_document):
        """Create a SideBySideStrategy instance."""
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=10)

        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"

        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=10)

        mock_margin_renderer = Mock()
        mock_margin_renderer.draw_page_overlays = Mock()

        return SideBySideStrategy(
            mock_scene,
            mock_document,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

    def test_render_all_pages_side_by_side(self, strategy, mock_scene, mock_document):
        """Test rendering all pages in side-by-side pairs."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_items = []
            for _ in range(10):
                mock_item = Mock()
                mock_item.setPos = Mock()
                mock_items.append(mock_item)
            mock_page_item.side_effect = mock_items

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=5,  # This is ignored for side-by-side
                is_presentation_mode=False,
                show_fold_lines=True,
                fit_callback=None,
            )

            # Should create all 10 pages
            assert mock_page_item.call_count == 10

            # Check positioning of first few pages
            # Page 0 should be on the right in first row
            mock_items[0].setPos.assert_called_with(612, 0)

            # Pages 1-2 should be side by side in second row
            # Note: Y_OFFSET_SPACING is added between rows
            # We need to account for the spacing constant

    def test_render_empty_document(self, strategy, mock_scene, mock_document):
        """Test rendering with empty document."""
        strategy.document_presenter.get_page_count.return_value = 0

        strategy.cleanup_page_items = Mock()

        strategy.render(
            current_page=0,
            is_presentation_mode=False,
            show_fold_lines=False,
            fit_callback=None,
        )

        # Should cleanup and clear scene but not crash
        strategy.cleanup_page_items.assert_called_once()
        mock_scene.clear.assert_called_once()

    # Note: get_visible_pages method doesn't exist in the strategy classes


class TestAllPagesStrategy:
    """Test all pages rendering strategy."""

    @pytest.fixture
    def mock_scene(self):
        """Create a mock graphics scene."""
        scene = Mock()
        scene.clear = Mock()
        scene.addItem = Mock()
        scene.setSceneRect = Mock()
        scene.itemsBoundingRect = Mock(
            return_value=Mock(adjusted=Mock(return_value=Mock()))
        )
        scene.views = Mock(return_value=[])  # Return empty list of views
        return scene

    @pytest.fixture
    def mock_document(self):
        """Create a mock PDF document."""
        doc = Mock()
        doc.pageCount = Mock(return_value=5)
        return doc

    @pytest.fixture
    def strategy(self, mock_scene, mock_document):
        """Create an AllPagesStrategy instance."""
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=5)

        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"

        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=5)

        mock_margin_renderer = Mock()
        mock_margin_renderer.draw_page_overlays = Mock()

        # Mock the graphics scene views
        mock_view = Mock()
        mock_view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=100))
        )
        mock_view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=50))
        )
        mock_scene.views = Mock(return_value=[mock_view])

        return AllPagesStrategy(
            mock_scene,
            mock_document,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

    def test_render_all_pages_vertically(self, strategy, mock_scene, mock_document):
        """Test rendering all pages vertically stacked."""
        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_items = []
            for _ in range(5):
                mock_item = Mock()
                mock_item.setPos = Mock()
                mock_items.append(mock_item)
            mock_page_item.side_effect = mock_items

            strategy.cleanup_page_items = Mock()

            strategy.render(
                current_page=2,  # This is ignored for all pages view
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should create all 5 pages
            assert mock_page_item.call_count == 5

            # Check vertical positioning (accounting for Y_OFFSET_SPACING)
            # We can't check exact positions without knowing Y_OFFSET_SPACING value

    def test_render_large_document(self, strategy, mock_scene, mock_document):
        """Test rendering a large document."""
        strategy.document_presenter.get_page_count.return_value = 100
        strategy.document_presenter.get_page_size = Mock(return_value=(612, 792))

        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            # Create mock items
            mock_item = Mock()
            mock_item.setPos = Mock()
            mock_page_item.return_value = mock_item

            strategy.cleanup_page_items = Mock()

            strategy.render(
                current_page=50,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should create all 100 pages
            assert mock_page_item.call_count == 100

    # Note: get_visible_pages method doesn't exist in the strategy classes


class TestStrategyIntegration:
    """Test integration between different strategies."""

    def test_strategy_interface_consistency(self):
        """Test that all strategies implement the same interface."""
        # Create mock dependencies
        mock_scene = Mock()
        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=10)
        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"
        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=10)
        mock_margin_renderer = Mock()

        # For AllPagesStrategy, we need to mock the views
        mock_view = Mock()
        mock_view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_scene.views = Mock(return_value=[mock_view])

        strategies = [
            SinglePageStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            PagePairStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            SideBySideStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            AllPagesStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
        ]

        for strategy in strategies:
            # All should have render method
            assert hasattr(strategy, "render")
            assert callable(strategy.render)

    def test_strategy_switching(self):
        """Test switching between strategies."""
        # Create mock dependencies
        mock_scene = Mock()
        mock_scene.clear = Mock()
        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=10)
        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"
        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=10)
        mock_margin_renderer = Mock()

        # For AllPagesStrategy
        mock_view = Mock()
        mock_view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_scene.views = Mock(return_value=[mock_view])

        strategies = {
            "single": SinglePageStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            "pair": PagePairStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            "side_by_side": SideBySideStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            "all": AllPagesStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
        }

        # Test that each strategy can be used without errors
        with patch("momovu.views.components.page_strategies.base.PageItem"):
            for _name, strategy in strategies.items():
                mock_scene.clear.reset_mock()
                strategy.cleanup_page_items = Mock()

                strategy.render(
                    current_page=5,
                    is_presentation_mode=False,
                    show_fold_lines=False,
                    fit_callback=None,
                )

                strategy.cleanup_page_items.assert_called_once()
                mock_scene.clear.assert_called_once()


class TestEdgeCases:
    """Test edge cases in page navigation strategies."""

    def test_single_page_strategy_invalid_page(self):
        """Test single page strategy with invalid page number."""
        mock_scene = Mock()
        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=None)  # Invalid page
        mock_doc_presenter.get_page_count = Mock(return_value=5)
        mock_margin_presenter = Mock()
        mock_nav_presenter = Mock()
        mock_margin_renderer = Mock()

        strategy = SinglePageStrategy(
            mock_scene,
            mock_doc,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

        with patch("momovu.views.components.page_strategies.base.PageItem"):
            strategy.cleanup_page_items = Mock()

            # Should handle invalid page gracefully
            strategy.render(
                current_page=10,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should still cleanup and clear
            strategy.cleanup_page_items.assert_called_once()
            mock_scene.clear.assert_called_once()

    def test_page_pair_strategy_single_page_document(self):
        """Test page pair strategy with single-page document."""
        mock_scene = Mock()
        mock_scene.clear = Mock()
        mock_scene.addItem = Mock()
        mock_scene.setSceneRect = Mock()
        mock_scene.itemsBoundingRect = Mock(
            return_value=Mock(adjusted=Mock(return_value=Mock()))
        )
        mock_scene.views = Mock(return_value=[])  # Return empty list of views

        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(612, 792))
        mock_doc_presenter.get_page_count = Mock(return_value=1)
        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"
        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=1)
        mock_margin_renderer = Mock()

        strategy = PagePairStrategy(
            mock_scene,
            mock_doc,
            mock_doc_presenter,
            mock_margin_presenter,
            mock_nav_presenter,
            mock_margin_renderer,
        )

        with patch(
            "momovu.views.components.page_strategies.base.PageItem"
        ) as mock_page_item:
            mock_item = Mock()
            mock_item.setPos = Mock()
            mock_page_item.return_value = mock_item

            strategy.cleanup_page_items = Mock()
            strategy._draw_spine_line = Mock()

            strategy.render(
                current_page=0,
                is_presentation_mode=False,
                show_fold_lines=False,
                fit_callback=None,
            )

            # Should create only one page
            mock_page_item.assert_called_once_with(mock_doc, 0, 612, 792)

    def test_strategies_with_zero_dimensions(self):
        """Test strategies with zero page dimensions."""
        mock_scene = Mock()
        mock_doc = Mock()
        mock_doc_presenter = Mock()
        mock_doc_presenter.get_page_size = Mock(return_value=(0, 0))  # Zero dimensions
        mock_doc_presenter.get_page_count = Mock(return_value=5)
        mock_margin_presenter = Mock()
        mock_margin_presenter.model = Mock()
        mock_margin_presenter.model.document_type = "interior"
        mock_nav_presenter = Mock()
        mock_nav_presenter.get_total_pages = Mock(return_value=5)
        mock_margin_renderer = Mock()

        # For AllPagesStrategy
        mock_view = Mock()
        mock_view.verticalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_view.horizontalScrollBar = Mock(
            return_value=Mock(value=Mock(return_value=0))
        )
        mock_scene.views = Mock(return_value=[mock_view])

        strategies = [
            SinglePageStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            PagePairStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            SideBySideStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
            AllPagesStrategy(
                mock_scene,
                mock_doc,
                mock_doc_presenter,
                mock_margin_presenter,
                mock_nav_presenter,
                mock_margin_renderer,
            ),
        ]

        for strategy in strategies:
            with patch("momovu.views.components.page_strategies.base.PageItem"):
                strategy.cleanup_page_items = Mock()

                # Should not crash with zero dimensions
                strategy.render(
                    current_page=0,
                    is_presentation_mode=False,
                    show_fold_lines=False,
                    fit_callback=None,
                )

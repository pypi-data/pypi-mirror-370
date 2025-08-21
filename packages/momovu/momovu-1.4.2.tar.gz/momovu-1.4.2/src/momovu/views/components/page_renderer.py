"""Page rendering component for the PDF viewer.

This refactored version uses the Strategy pattern to delegate rendering
to specialized strategies based on the view mode and document type.
"""

from typing import TYPE_CHECKING, Callable, Optional, Union

if TYPE_CHECKING:
    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter

from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.logger import get_logger

if not TYPE_CHECKING:
    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter
from momovu.views.components.margin_renderer import MarginRenderer
from momovu.views.components.page_strategies.all_pages import AllPagesStrategy
from momovu.views.components.page_strategies.page_pair import PagePairStrategy
from momovu.views.components.page_strategies.side_by_side import SideBySideStrategy
from momovu.views.components.page_strategies.single_page import SinglePageStrategy

logger = get_logger(__name__)


class PageRenderer:
    """Component responsible for coordinating page rendering.

    This class uses the Strategy pattern to delegate actual rendering
    to specialized strategies based on the current view mode.
    """

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        pdf_document: QPdfDocument,
        document_presenter: DocumentPresenter,
        margin_presenter: MarginPresenter,
        navigation_presenter: NavigationPresenter,
        config_manager: Optional[ConfigurationManager] = None,
    ):
        """Initialize the page renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
            pdf_document: The Qt PDF document
            document_presenter: Presenter for document operations
            margin_presenter: Presenter for margin operations
            navigation_presenter: Presenter for navigation operations
            config_manager: Optional configuration manager for reading user preferences
        """
        self.graphics_scene = graphics_scene
        self.pdf_document = pdf_document
        self.document_presenter = document_presenter
        self.margin_presenter = margin_presenter
        self.navigation_presenter = navigation_presenter
        self.config_manager = config_manager

        # Pass config manager to margin renderer
        self.margin_renderer = MarginRenderer(
            graphics_scene, margin_presenter, config_manager
        )

        self._init_strategies()

        self.is_presentation_mode = False
        self.show_fold_lines = True

        self._cleaned_up = False

    def _init_strategies(self) -> None:
        """Create strategy instances for each rendering mode."""
        strategy_args = (
            self.graphics_scene,
            self.pdf_document,
            self.document_presenter,
            self.margin_presenter,
            self.navigation_presenter,
            self.margin_renderer,
        )

        self.single_page_strategy = SinglePageStrategy(*strategy_args)
        self.page_pair_strategy = PagePairStrategy(*strategy_args)
        self.all_pages_strategy = AllPagesStrategy(*strategy_args)
        self.side_by_side_strategy = SideBySideStrategy(*strategy_args)

    def render_current_page(
        self, fit_callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Select and execute the appropriate rendering strategy.

        Strategy selection based on:
        - Presentation mode → single/pair only
        - Interior + side-by-side → all pairs stacked
        - Interior + single → all pages stacked
        - Cover/dustjacket → single page only

        Args:
            fit_callback: Optional zoom adjustment after rendering
        """
        # Check if navigation presenter exists before using it
        if not self.navigation_presenter:
            logger.error("Navigation presenter not available for rendering")
            return

        current_page = self.navigation_presenter.get_current_page()

        strategy = self._select_strategy()
        strategy.render(
            current_page, self.is_presentation_mode, self.show_fold_lines, fit_callback
        )

    def _select_strategy(
        self,
    ) -> Union[
        SinglePageStrategy, PagePairStrategy, AllPagesStrategy, SideBySideStrategy
    ]:
        """Choose rendering strategy based on mode and document type.

        Returns:
            Strategy instance matching current viewing configuration
        """
        if self.is_presentation_mode:
            if self.navigation_presenter.model.view_mode == "side_by_side":
                return self.page_pair_strategy
            else:
                return self.single_page_strategy

        elif self.navigation_presenter.model.view_mode == "side_by_side":
            # Side-by-side mode for interior should show ALL page pairs stacked
            if self.margin_presenter.model.document_type == "interior":
                return self.side_by_side_strategy
            else:
                return self.page_pair_strategy

        elif self.margin_presenter.model.document_type == "interior":
            # For interior documents in normal single-page mode, render ALL pages
            return self.all_pages_strategy
        else:
            return self.single_page_strategy

    def set_presentation_mode(self, enabled: bool) -> None:
        """Enable/disable presentation mode rendering.

        Args:
            enabled: True for single page/pair only, False for stacked pages
        """
        self.is_presentation_mode = enabled
        logger.debug(f"Presentation mode set to: {enabled}")

    def set_show_fold_lines(self, show: bool) -> None:
        """Control spine/flap fold line visibility.

        Args:
            show: True to display fold indicators on covers/dustjackets
        """
        self.show_fold_lines = show
        self.margin_renderer.set_show_fold_lines(show)
        logger.debug(f"Show fold lines set to: {show}")

    def set_show_gutter(self, show: bool) -> None:
        """Control gutter margin visibility.

        Args:
            show: True to display gutter margins on interior documents
        """
        # The actual show_gutter state is managed by margin_presenter
        # This just triggers a re-render if needed
        self.margin_renderer.set_show_gutter(show)
        logger.debug(f"Show gutter set to: {show}")

    def clear_renderer_caches(self) -> None:
        """Clear cached configuration values in renderers.

        This should be called when configuration changes to ensure
        new values are loaded.
        """
        if self.margin_renderer:
            self.margin_renderer.clear_renderer_caches()

    def cleanup(self) -> None:
        """Release all strategy instances and clear references (idempotent)."""
        if self._cleaned_up:
            return  # Already cleaned up

        logger.debug("Cleaning up PageRenderer")

        strategies = [
            "single_page_strategy",
            "page_pair_strategy",
            "all_pages_strategy",
            "side_by_side_strategy",
        ]

        for strategy_name in strategies:
            if hasattr(self, strategy_name):
                try:
                    setattr(self, strategy_name, None)
                except Exception as e:
                    logger.warning(f"Error clearing strategy {strategy_name}: {e}")

        if hasattr(self, "margin_renderer"):
            try:
                # MarginRenderer doesn't need cleanup - it only holds references
                # to objects that are cleaned up elsewhere (scene, presenter)
                self.margin_renderer = None  # type: ignore[assignment]
            except Exception as e:
                logger.warning(f"Error clearing margin renderer: {e}")

        self.graphics_scene = None  # type: ignore[assignment]
        self.pdf_document = None  # type: ignore[assignment]
        self.document_presenter = None  # type: ignore[assignment]
        self.margin_presenter = None  # type: ignore[assignment]
        self.navigation_presenter = None  # type: ignore[assignment]
        self.config_manager = None

        self._cleaned_up = True
        logger.info("PageRenderer cleanup completed")

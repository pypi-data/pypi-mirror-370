"""Base strategy for page rendering."""

from abc import ABC, abstractmethod
from typing import Callable, Optional

from PySide6.QtCore import QTimer
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.constants import IMMEDIATE_DELAY, Y_OFFSET_SPACING, ZOOM_SCENE_PADDING
from momovu.lib.logger import get_logger
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter
from momovu.views.components.margin_renderer import MarginRenderer
from momovu.views.page_item import PageItem

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for page rendering strategies."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        pdf_document: QPdfDocument,
        document_presenter: DocumentPresenter,
        margin_presenter: MarginPresenter,
        navigation_presenter: NavigationPresenter,
        margin_renderer: MarginRenderer,
    ):
        """Initialize the render strategy.

        Args:
            graphics_scene: The Qt graphics scene to render to
            pdf_document: The Qt PDF document
            document_presenter: Presenter for document operations
            margin_presenter: Presenter for margin operations
            navigation_presenter: Presenter for navigation operations
            margin_renderer: Renderer for margins and overlays
        """
        self.graphics_scene = graphics_scene
        self.pdf_document = pdf_document
        self.document_presenter = document_presenter
        self.margin_presenter = margin_presenter
        self.navigation_presenter = navigation_presenter
        self.margin_renderer = margin_renderer

        self.Y_OFFSET_SPACING = Y_OFFSET_SPACING  # Points between pages/pairs

    @abstractmethod
    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Render pages according to the strategy.

        Args:
            current_page: Current page index (0-based)
            is_presentation_mode: Whether in presentation mode
            show_fold_lines: Whether to show fold lines
            fit_callback: Optional callback to fit page to view
        """
        pass

    def create_page_item(
        self, page_index: int, x: float, y: float
    ) -> Optional[PageItem]:
        """Instantiate and position a page widget for rendering.

        Args:
            page_index: Zero-based page index
            x: Left edge position in scene coordinates
            y: Top edge position in scene coordinates

        Returns:
            Positioned PageItem ready for scene insertion, None if page invalid
        """
        page_size = self.document_presenter.get_page_size(page_index)
        if not page_size:
            return None

        page_width, page_height = page_size
        page_item = PageItem(
            self.pdf_document,
            page_index,
            page_width,
            page_height,
        )
        page_item.setPos(x, y)
        return page_item

    def draw_overlays(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skip_trim_edge: Optional[str] = None,
        page_position: Optional[str] = None,
    ) -> None:
        """Render safety margins and trim indicators on top of page.

        Args:
            x: Page left edge in scene coordinates
            y: Page top edge in scene coordinates
            width: Page width in points
            height: Page height in points
            skip_trim_edge: Optional edge to skip when drawing trim lines ("left" or "right")
            page_position: Optional page position for gutter ("left", "right", "first_alone", "last_alone", "single")
        """
        self.margin_renderer.draw_page_overlays(
            x, y, width, height, skip_trim_edge, page_position
        )

    def fit_to_view_if_needed(
        self, is_presentation_mode: bool, fit_callback: Optional[Callable[[], None]]
    ) -> None:
        """Schedule zoom adjustment for presentation mode.

        Args:
            is_presentation_mode: True triggers fit callback
            fit_callback: Function to scale view to page bounds
        """
        if is_presentation_mode and fit_callback:
            QTimer.singleShot(IMMEDIATE_DELAY, fit_callback)

    def update_scene_rect(self) -> None:
        """Expand scene boundaries to include all rendered pages with padding for zoom.

        The padding allows proper mouse-centered zoom at document edges by giving
        Qt room to position the viewport beyond the actual content bounds.
        Only adds padding when zoomed in to avoid scrollbar issues.
        """
        # CRITICAL: Save scrollbar positions before changing scene rect
        # This prevents the 1-pixel shift by preserving exact pixel positions
        scrollbar_positions = []
        for view in self.graphics_scene.views():
            if hasattr(view, "horizontalScrollBar") and hasattr(
                view, "verticalScrollBar"
            ):
                h_bar = view.horizontalScrollBar()
                v_bar = view.verticalScrollBar()
                if h_bar and v_bar:
                    h_pos = h_bar.value()
                    v_pos = v_bar.value()
                    scrollbar_positions.append((view, h_pos, v_pos))

        # Get the actual content bounds
        content_bounds = self.graphics_scene.itemsBoundingRect()

        # Always add padding for zoom operations to work properly
        # This is critical for corner zoom to function
        # Calculate padding based on potential zoom levels
        # This ensures we have enough room for zoom operations at edges
        padding = ZOOM_SCENE_PADDING  # Configurable in constants

        # Expand the scene rect with padding on all sides
        expanded_bounds = content_bounds.adjusted(-padding, -padding, padding, padding)
        self.graphics_scene.setSceneRect(expanded_bounds)

        logger.debug(
            f"Scene rect expanded from {content_bounds} to {expanded_bounds} "
            f"(added {padding}px padding for zoom)"
        )

        # CRITICAL: Restore scrollbar positions after changing scene rect
        # This prevents the view from jumping by maintaining exact pixel positions
        for view, h_pos, v_pos in scrollbar_positions:
            if hasattr(view, "horizontalScrollBar") and hasattr(
                view, "verticalScrollBar"
            ):
                h_bar = view.horizontalScrollBar()
                v_bar = view.verticalScrollBar()
                if h_bar and v_bar:
                    h_bar.setValue(h_pos)
                    v_bar.setValue(v_pos)

    def cleanup_page_items(self) -> None:
        """Clean up all PageItem instances before clearing the scene.

        This ensures timers are stopped and resources are freed properly.
        """
        for item in self.graphics_scene.items():
            if isinstance(item, PageItem) and hasattr(item, "cleanup"):
                try:
                    item.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up PageItem: {e}")

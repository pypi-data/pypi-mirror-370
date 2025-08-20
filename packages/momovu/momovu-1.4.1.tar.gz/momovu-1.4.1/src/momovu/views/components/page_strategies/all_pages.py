"""All pages rendering strategy."""

from typing import Callable, Optional

from momovu.lib.logger import get_logger
from momovu.views.components.page_strategies.base import BaseStrategy

logger = get_logger(__name__)


class AllPagesStrategy(BaseStrategy):
    """Strategy for rendering all pages vertically stacked."""

    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Stack all document pages vertically with preserved scroll position.

        Args:
            current_page: Ignored - all pages shown regardless
            is_presentation_mode: Ignored - not applicable for all pages
            show_fold_lines: Whether to display fold indicators
            fit_callback: Ignored - no fitting for multi-page view
        """
        # Preserve scroll position before clearing scene
        # This fixes the bug where re-rendering resets to page 1
        views = self.graphics_scene.views()
        old_scroll_v = None
        old_scroll_h = None
        if views:
            graphics_view = views[0]
            old_scroll_v = graphics_view.verticalScrollBar().value()
            old_scroll_h = graphics_view.horizontalScrollBar().value()

        # Clean up PageItems before clearing to ensure timers are stopped
        self.cleanup_page_items()
        self.graphics_scene.clear()

        y_offset = 0.0

        page_count = self.document_presenter.get_page_count()

        for page_index in range(page_count):
            page_size = self.document_presenter.get_page_size(page_index)
            if not page_size:
                continue

            page_width, page_height = page_size

            page_item = self.create_page_item(page_index, 0, y_offset)
            if page_item:
                self.graphics_scene.addItem(page_item)

                # Draw overlays - all pages view shows as single pages (no gutter)
                self.draw_overlays(
                    0, y_offset, page_width, page_height, page_position="single"
                )

                y_offset += page_height + self.Y_OFFSET_SPACING

        self.update_scene_rect()

        # Restore scroll position after rendering
        # This preserves the view position when switching modes
        if old_scroll_v is not None and views:
            graphics_view = views[0]
            graphics_view.verticalScrollBar().setValue(old_scroll_v)
            if old_scroll_h is not None:
                graphics_view.horizontalScrollBar().setValue(old_scroll_h)
            logger.debug(
                f"Restored scroll position: V={old_scroll_v}, H={old_scroll_h}"
            )

        logger.info(f"Rendered all {page_count} pages vertically")

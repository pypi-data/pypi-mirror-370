"""Side-by-side rendering strategy for all pages."""

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen

from momovu.lib.constants import (
    FOLD_LINE_COLOR,
    FOLD_LINE_PEN_WIDTH,
    Y_OFFSET_SPACING,
)
from momovu.lib.logger import get_logger
from momovu.views.components.page_strategies.base import BaseStrategy

logger = get_logger(__name__)


class SideBySideStrategy(BaseStrategy):
    """Strategy for rendering all pages in side-by-side pairs vertically stacked."""

    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Stack all page pairs vertically (page 1 alone, then 2-3, 4-5, etc).

        Book layout: page 1 on right, then even pages left/odd pages right.

        Args:
            current_page: Ignored - all pairs shown regardless
            is_presentation_mode: Ignored - not applicable for all pairs
            show_fold_lines: Display spine lines between pages
            fit_callback: Ignored - no fitting for multi-pair view
        """
        # Clean up PageItems before clearing to ensure timers are stopped
        self.cleanup_page_items()
        self.graphics_scene.clear()

        y_offset = 0.0

        page_count = self.document_presenter.get_page_count()
        if page_count == 0:
            return

        # FIRST: Page 1 (index 0) alone on the right
        y_offset = self._render_first_page_alone(y_offset, show_fold_lines)

        # THEN: Render remaining pages in pairs (2-3, 4-5, 6-7, etc.)
        self._render_remaining_pairs(page_count, y_offset, show_fold_lines)

        self.update_scene_rect()

        logger.info(f"Rendered all {page_count} pages in side-by-side layout")

    def _render_first_page_alone(self, y_offset: float, show_fold_lines: bool) -> float:
        """Place page 1 on right side with empty left page space.

        Args:
            y_offset: Vertical position to start
            show_fold_lines: Draw spine line if True

        Returns:
            New Y position after page 1 height + spacing
        """
        first_size = self.document_presenter.get_page_size(0)
        if not first_size:
            return y_offset

        first_width, first_height = first_size

        # Render page 1 on the RIGHT side (offset by page width)
        first_item = self.create_page_item(0, first_width, y_offset)
        if first_item:
            self.graphics_scene.addItem(first_item)

            # Page 1 is alone on the right - draw all trim lines
            # Gutter goes on the left side for first page
            self.draw_overlays(
                first_width,
                y_offset,
                first_width,
                first_height,
                page_position="first_alone",
            )

            if show_fold_lines:
                self._draw_spine_line(first_width, y_offset, first_height)

        return y_offset + first_height + Y_OFFSET_SPACING

    def _render_remaining_pairs(
        self, page_count: int, y_offset: float, show_fold_lines: bool
    ) -> None:
        """Stack page pairs (2-3, 4-5, etc) vertically below page 1.

        Args:
            page_count: Total pages in document
            y_offset: Starting Y position after page 1
            show_fold_lines: Draw spine lines between pairs
        """
        for page_index in range(1, page_count, 2):
            # Even page number (2, 4, 6...) goes on LEFT
            left_page = page_index
            # Odd page number (3, 5, 7...) goes on RIGHT
            right_page = page_index + 1 if page_index + 1 < page_count else None

            left_size = self.document_presenter.get_page_size(left_page)
            if not left_size:
                continue
            left_width, left_height = left_size

            right_width = 0.0
            right_height = 0.0
            if right_page is not None:
                right_size = self.document_presenter.get_page_size(right_page)
                if right_size:
                    right_width, right_height = right_size

            pair_height = max(left_height, right_height) if right_page else left_height

            left_item = self.create_page_item(left_page, 0, y_offset)
            if left_item:
                self.graphics_scene.addItem(left_item)
                # Only skip right edge if there's actually a right page
                if right_page is not None:
                    self.draw_overlays(
                        0,
                        y_offset,
                        left_width,
                        left_height,
                        skip_trim_edge="right",
                        page_position="left",
                    )
                else:
                    # Left page alone (last page) - draw all edges
                    # This is the last page if it's alone on the left
                    self.draw_overlays(
                        0, y_offset, left_width, left_height, page_position="last_alone"
                    )

            if show_fold_lines:
                self._draw_spine_line(left_width, y_offset, pair_height)

            if right_page is not None:
                right_item = self.create_page_item(right_page, left_width, y_offset)
                if right_item:
                    self.graphics_scene.addItem(right_item)
                    # Right page in a pair - skip left edge
                    self.draw_overlays(
                        left_width,
                        y_offset,
                        right_width,
                        right_height,
                        skip_trim_edge="left",
                        page_position="right",
                    )

            y_offset += pair_height + Y_OFFSET_SPACING

    def _draw_spine_line(self, x: float, y: float, height: float) -> None:
        """Add purple dashed line to indicate book spine location.

        Args:
            x: Horizontal position between pages
            y: Top of spine line
            height: Length of spine line
        """
        # Get fold line color and width from configuration if available
        if self.margin_renderer and hasattr(self.margin_renderer, "cover_renderer"):
            # Use the cover renderer's method to get configured fold pen
            pen = self.margin_renderer.cover_renderer.get_fold_pen()
        else:
            # Fallback to hardcoded values if config not available
            pen = QPen(FOLD_LINE_COLOR)
            pen.setWidth(FOLD_LINE_PEN_WIDTH)
            pen.setStyle(Qt.PenStyle.DashLine)

        self.graphics_scene.addLine(x, y, x, y + height, pen)

"""Page pair rendering strategy."""

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen

from momovu.lib.constants import FOLD_LINE_COLOR, FOLD_LINE_PEN_WIDTH
from momovu.lib.logger import get_logger
from momovu.views.components.page_strategies.base import BaseStrategy

logger = get_logger(__name__)


class PagePairStrategy(BaseStrategy):
    """Strategy for rendering a pair of pages side by side."""

    def render(
        self,
        current_page: int,
        is_presentation_mode: bool,
        show_fold_lines: bool,
        fit_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Display current page with its pair (page 1 alone, then 2-3, 4-5, etc).

        Args:
            current_page: Page to display with its pair
            is_presentation_mode: Triggers fit_callback if True
            show_fold_lines: Display spine line between pages
            fit_callback: Function to scale pair to viewport
        """
        # Clear scene
        # Clean up PageItems before clearing to ensure timers are stopped
        self.cleanup_page_items()
        self.graphics_scene.clear()

        # For cover/dustjacket, delegate to single page
        if self.margin_presenter.model.document_type in ["cover", "dustjacket"]:
            from momovu.views.components.page_strategies.single_page import (
                SinglePageStrategy,
            )

            single_strategy = SinglePageStrategy(
                self.graphics_scene,
                self.pdf_document,
                self.document_presenter,
                self.margin_presenter,
                self.navigation_presenter,
                self.margin_renderer,
            )
            single_strategy.render(
                current_page, is_presentation_mode, show_fold_lines, fit_callback
            )
            return

        # Interior documents follow book conventions
        if current_page == 0:
            self._render_first_page(show_fold_lines)
        else:
            self._render_page_pair(current_page, show_fold_lines)

        # Update scene rect
        self.update_scene_rect()

        # Fit to view if needed
        self.fit_to_view_if_needed(is_presentation_mode, fit_callback)

    def _render_first_page(self, show_fold_lines: bool) -> None:
        """Position page 1 on right side following book convention."""
        page_size = self.document_presenter.get_page_size(0)
        if not page_size:
            return

        page_width, page_height = page_size

        # Render page 1 on the RIGHT side
        page_item = self.create_page_item(0, page_width, 0)
        if page_item:
            self.graphics_scene.addItem(page_item)

            # Draw overlays for page 1 - it's alone, so draw all trim lines
            # Page 1 is on the right side, so gutter goes on left
            self.draw_overlays(
                page_width, 0, page_width, page_height, page_position="first_alone"
            )

            # Draw spine line on the left edge if interior
            if (
                self.margin_presenter.model.document_type == "interior"
                and show_fold_lines
            ):
                self._draw_spine_line(page_width, 0, page_height)

            logger.info("Rendered page 1 alone on right")

    def _render_page_pair(self, current_page: int, show_fold_lines: bool) -> None:
        """Display even page on left, odd page on right with spine between."""
        # Determine the pair
        if current_page % 2 == 0:
            # Even page index (odd page number) - show previous even/odd pair
            left_page_index = current_page - 1
            right_page_index = current_page
        else:
            # Odd page index (even page number) - this is the left page
            left_page_index = current_page
            right_page_index = current_page + 1

        # Get page dimensions
        left_page_size = self.document_presenter.get_page_size(left_page_index)
        if not left_page_size:
            return
        left_width, left_height = left_page_size

        right_width = 0.0
        right_height = 0.0
        if right_page_index < self.navigation_presenter.get_total_pages():
            right_page_size = self.document_presenter.get_page_size(right_page_index)
            if right_page_size:
                right_width, right_height = right_page_size

        # Check if we have a complete pair
        has_right_page = right_page_index < self.navigation_presenter.get_total_pages()

        # Render left page
        left_item = self.create_page_item(left_page_index, 0, 0)
        if left_item:
            self.graphics_scene.addItem(left_item)
            # For interior documents, skip right edge only if there's a right page
            if (
                self.margin_presenter.model.document_type == "interior"
                and has_right_page
            ):
                self.draw_overlays(
                    0,
                    0,
                    left_width,
                    left_height,
                    skip_trim_edge="right",
                    page_position="left",
                )
            else:
                # Left page alone or non-interior - draw all edges
                # Check if this is the last page alone
                is_last_alone = (
                    not has_right_page
                    and left_page_index
                    == self.navigation_presenter.get_total_pages() - 1
                )
                page_pos = "last_alone" if is_last_alone else "left"
                self.draw_overlays(
                    0, 0, left_width, left_height, page_position=page_pos
                )

        # Draw spine line between pages if interior
        if self.margin_presenter.model.document_type == "interior" and show_fold_lines:
            max_height = (
                max(left_height, right_height) if has_right_page else left_height
            )
            self._draw_spine_line(left_width, 0, max_height)

        # Render right page if it exists
        if has_right_page:
            right_item = self.create_page_item(right_page_index, left_width, 0)
            if right_item:
                self.graphics_scene.addItem(right_item)
                # For interior documents in a pair, skip left edge
                if self.margin_presenter.model.document_type == "interior":
                    self.draw_overlays(
                        left_width,
                        0,
                        right_width,
                        right_height,
                        skip_trim_edge="left",
                        page_position="right",
                    )
                else:
                    # Non-interior - draw all edges
                    self.draw_overlays(left_width, 0, right_width, right_height)

        logger.info(
            f"Rendered pages {left_page_index + 1}-"
            f"{right_page_index + 1 if right_page_index < self.navigation_presenter.get_total_pages() else left_page_index + 1}"
        )

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

"""Renderer for interior document margins and overlays."""

from typing import Optional

from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.views.components.renderers.base import BaseRenderer


class InteriorRenderer(BaseRenderer):
    """Handles rendering for interior documents."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        config_manager: Optional[ConfigurationManager] = None,
    ) -> None:
        """Initialize the interior renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
            config_manager: Optional configuration manager for reading user preferences
        """
        super().__init__(graphics_scene, config_manager)

    def draw_margins(
        self, x: float, y: float, width: float, height: float, margin: float
    ) -> None:
        """Render safety margin overlays on all four edges.

        Args:
            x: Page left edge
            y: Page top edge
            width: Page width
            height: Page height
            margin: Safety margin size
        """
        margin_brush = self.get_margin_brush()

        self.add_margin_rect(x, y, width, margin, margin_brush)

        self.add_margin_rect(x, y + height - margin, width, margin, margin_brush)

        self.add_margin_rect(
            x,
            y + margin,
            margin,
            height - 2 * margin,
            margin_brush,
        )

        self.add_margin_rect(
            x + width - margin,
            y + margin,
            margin,
            height - 2 * margin,
            margin_brush,
        )

    def draw_gutter(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        margin: float,
        gutter_width: float,
        page_position: str,
    ) -> None:
        """Draw gutter margin extension on the spine side of the page.

        The gutter extends inward from the safety margin toward the spine.

        Args:
            x: Page left edge
            y: Page top edge
            width: Page width
            height: Page height
            margin: Safety margin size
            gutter_width: Gutter width in points
            page_position: Position of page ("left", "right", "first_alone", "last_alone", "single")
        """
        if gutter_width <= 0:
            return

        # Determine which side gets the gutter based on page position
        # For single page view, default to left side (like a right page)
        if page_position in ["left", "last_alone"]:
            # Gutter on RIGHT side (extending from right margin toward spine)
            gutter_x = x + width - margin - gutter_width
            self.add_gutter_rect(
                gutter_x, y + margin, gutter_width, height - 2 * margin
            )
        elif page_position in ["right", "first_alone", "single"]:
            # Gutter on LEFT side (extending from left margin toward spine)
            # Single pages are treated like right pages (gutter on left)
            gutter_x = x + margin
            self.add_gutter_rect(
                gutter_x, y + margin, gutter_width, height - 2 * margin
            )

    def draw_trim_lines(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skip_trim_edge: Optional[str] = None,
    ) -> None:
        """Add trim marks exactly at page boundaries.

        Args:
            x: Page left edge
            y: Page top edge
            width: Page width
            height: Page height
            skip_trim_edge: Optional edge to skip when drawing trim lines ("left" or "right")
        """
        pen = self.get_trim_pen()

        # Always draw horizontal trim lines
        self.graphics_scene.addLine(x, y, x + width, y, pen)
        self.graphics_scene.addLine(x, y + height, x + width, y + height, pen)

        # Conditionally draw vertical trim lines
        if skip_trim_edge != "left":
            self.graphics_scene.addLine(x, y, x, y + height, pen)
        if skip_trim_edge != "right":
            self.graphics_scene.addLine(x + width, y, x + width, y + height, pen)

    def draw_bleed_lines(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skip_trim_edge: Optional[str] = None,
    ) -> None:
        """Interior documents don't have bleed lines.

        Args:
            x: Page left edge
            y: Page top edge
            width: Page width
            height: Page height
            skip_trim_edge: Ignored for interior documents
        """
        # No-op: Interior documents don't have bleeds
        pass

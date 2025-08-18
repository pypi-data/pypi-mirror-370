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

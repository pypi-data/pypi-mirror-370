"""Renderer for cover document margins and overlays."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.constants import (
    BARCODE_AREA_COLOR,
    BARCODE_HEIGHT,
    BARCODE_RECT_OPACITY,
    BARCODE_WIDTH,
    COVER_BLEED,
    POINTS_PER_MM,
)
from momovu.views.components.renderers.base import BaseRenderer


class CoverRenderer(BaseRenderer):
    """Handles rendering for cover documents."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        config_manager: Optional[ConfigurationManager] = None,
    ) -> None:
        """Initialize the cover renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
            config_manager: Optional configuration manager for reading user preferences
        """
        super().__init__(graphics_scene, config_manager)

    def draw_margins(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        margin: float,
        spine_width: float,
    ) -> None:
        """Render safety margins on front/back covers, excluding spine area.

        Cover layout: [back cover][spine][front cover]

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            margin: Safety margin size
            spine_width: Book spine thickness
        """
        margin_brush = self.get_margin_brush()
        bleed_offset = COVER_BLEED * POINTS_PER_MM

        center_x = width / 2
        spine_left = center_x - spine_width / 2
        spine_right = center_x + spine_width / 2

        # BACK COVER MARGINS
        self.add_margin_rect(
            x + bleed_offset,
            y + bleed_offset,
            spine_left - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + bleed_offset,
            y + height - margin - bleed_offset,
            spine_left - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + bleed_offset,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_left - margin,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )

        # NO SPINE MARGINS - spine area should be clear

        # FRONT COVER MARGINS
        self.add_margin_rect(
            x + spine_right,
            y + bleed_offset,
            width - spine_right - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_right,
            y + height - margin - bleed_offset,
            width - spine_right - bleed_offset,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + spine_right,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )
        self.add_margin_rect(
            x + width - margin - bleed_offset,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )

    def draw_trim_lines(self, x: float, y: float, width: float, height: float) -> None:
        """Add trim marks at cover edges accounting for bleed.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
        """
        pen = self.get_trim_pen()
        bleed = COVER_BLEED * POINTS_PER_MM

        self.graphics_scene.addLine(
            x + bleed, y + bleed, x + width - bleed, y + bleed, pen
        )
        self.graphics_scene.addLine(
            x + bleed,
            y + height - bleed,
            x + width - bleed,
            y + height - bleed,
            pen,
        )

        self.graphics_scene.addLine(
            x + bleed, y + bleed, x + bleed, y + height - bleed, pen
        )
        self.graphics_scene.addLine(
            x + width - bleed, y + bleed, x + width - bleed, y + height - bleed, pen
        )

    def draw_spine_fold_lines(
        self, x: float, y: float, width: float, height: float, spine_width: float
    ) -> None:
        """Mark spine boundaries with dashed purple lines.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            spine_width: Book spine thickness
        """
        if not spine_width:
            return

        center_x = width / 2
        fold_pen = self.get_fold_pen()

        self.graphics_scene.addLine(
            x + center_x - spine_width / 2,
            y,
            x + center_x - spine_width / 2,
            y + height,
            fold_pen,
        )

        self.graphics_scene.addLine(
            x + center_x + spine_width / 2,
            y,
            x + center_x + spine_width / 2,
            y + height,
            fold_pen,
        )

    def draw_barcode(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        spine_width: float,
        safety_margin: float,
    ) -> None:
        """Highlight barcode placement area on back cover bottom-right.

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
            spine_width: Book spine thickness
            safety_margin: Distance from edges
        """
        barcode_width = BARCODE_WIDTH * POINTS_PER_MM
        barcode_height = BARCODE_HEIGHT * POINTS_PER_MM
        bleed_offset = COVER_BLEED * POINTS_PER_MM

        back_cover_width = (width - spine_width) / 2

        barcode_x = x + back_cover_width - safety_margin - barcode_width
        barcode_y = y + height - safety_margin - barcode_height - bleed_offset

        # Get barcode color from configuration
        barcode_color = self.get_color_from_config("barcode_area", BARCODE_AREA_COLOR)
        barcode_opacity = self.get_opacity_from_config(
            "barcode_area", BARCODE_RECT_OPACITY
        )

        pen = QPen(Qt.PenStyle.NoPen)
        brush = QBrush(barcode_color)

        barcode_rect = self.graphics_scene.addRect(
            barcode_x, barcode_y, barcode_width, barcode_height, pen, brush
        )
        barcode_rect.setOpacity(barcode_opacity)

    def draw_bleed_lines(self, x: float, y: float, width: float, height: float) -> None:
        """Add bleed marks at actual page edges (outside trim lines).

        Args:
            x: Page left edge
            y: Page top edge
            width: Total cover width
            height: Cover height
        """
        pen = self.get_bleed_pen()

        # Draw bleed lines at actual page edges
        # Top edge
        self.graphics_scene.addLine(x, y, x + width, y, pen)
        # Bottom edge
        self.graphics_scene.addLine(x, y + height, x + width, y + height, pen)
        # Left edge
        self.graphics_scene.addLine(x, y, x, y + height, pen)
        # Right edge
        self.graphics_scene.addLine(x + width, y, x + width, y + height, pen)

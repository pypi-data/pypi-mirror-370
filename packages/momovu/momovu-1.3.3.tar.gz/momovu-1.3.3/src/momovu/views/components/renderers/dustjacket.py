"""Renderer for dustjacket document margins and overlays."""

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
    DUSTJACKET_BLEED,
    DUSTJACKET_FOLD_SAFETY_MARGIN,
    POINTS_PER_MM,
)
from momovu.views.components.renderers.base import BaseRenderer


class DustjacketRenderer(BaseRenderer):
    """Handles rendering for dustjacket documents."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        config_manager: Optional[ConfigurationManager] = None,
    ) -> None:
        """Initialize the dustjacket renderer.

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
        flap_width: float,
    ) -> None:
        """Render safety margins on all dustjacket sections including flaps.

        Layout: [left flap][back cover][spine][front cover][right flap]

        Args:
            x: Page left edge
            y: Page top edge
            width: Total dustjacket width
            height: Dustjacket height
            margin: Safety margin size
            spine_width: Book spine thickness
            flap_width: Width of each flap
        """
        margin_brush = self.get_margin_brush()
        bleed_offset = DUSTJACKET_BLEED * POINTS_PER_MM
        fold_safety_margin = DUSTJACKET_FOLD_SAFETY_MARGIN * POINTS_PER_MM

        center_x = width / 2
        spine_left = center_x - spine_width / 2
        spine_right = center_x + spine_width / 2

        main_left = flap_width + fold_safety_margin + bleed_offset
        main_right = width - flap_width - fold_safety_margin - bleed_offset

        back_cover_left = main_left
        back_cover_right = spine_left
        back_cover_width = back_cover_right - back_cover_left

        front_cover_left = spine_right
        front_cover_right = main_right
        front_cover_width = front_cover_right - front_cover_left

        self._draw_flap_margins(
            x, y, width, height, margin, flap_width, bleed_offset, True
        )
        self._draw_cover_margins(
            x,
            y,
            height,
            margin,
            back_cover_left,
            back_cover_width,
            back_cover_right,
            bleed_offset,
            margin_brush,
        )
        self._draw_cover_margins(
            x,
            y,
            height,
            margin,
            front_cover_left,
            front_cover_width,
            front_cover_right,
            bleed_offset,
            margin_brush,
        )
        self._draw_flap_margins(
            x, y, width, height, margin, flap_width, bleed_offset, False
        )

    def _draw_flap_margins(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        margin: float,
        flap_width: float,
        bleed_offset: float,
        is_left: bool,
    ) -> None:
        """Render safety margins within a single flap area."""
        margin_brush = self.get_margin_brush()

        flap_x = bleed_offset if is_left else width - flap_width - bleed_offset

        self.add_margin_rect(
            x + flap_x, y + bleed_offset, flap_width, margin, margin_brush
        )
        self.add_margin_rect(
            x + flap_x,
            y + height - margin - bleed_offset,
            flap_width,
            margin,
            margin_brush,
        )

        if is_left:
            self.add_margin_rect(
                x + flap_x,
                y + margin + bleed_offset,
                margin,
                height - 2 * margin - 2 * bleed_offset,
                margin_brush,
            )
            self.add_margin_rect(
                x + flap_x + flap_width - margin,
                y + margin + bleed_offset,
                margin,
                height - 2 * margin - 2 * bleed_offset,
                margin_brush,
            )
        else:
            self.add_margin_rect(
                x + flap_x,
                y + margin + bleed_offset,
                margin,
                height - 2 * margin - 2 * bleed_offset,
                margin_brush,
            )
            self.add_margin_rect(
                x + flap_x + flap_width - margin,
                y + margin + bleed_offset,
                margin,
                height - 2 * margin - 2 * bleed_offset,
                margin_brush,
            )

    def _draw_cover_margins(
        self,
        x: float,
        y: float,
        height: float,
        margin: float,
        cover_left: float,
        cover_width: float,
        cover_right: float,
        bleed_offset: float,
        margin_brush: QBrush,
    ) -> None:
        """Render safety margins within front or back cover area."""
        self.add_margin_rect(
            x + cover_left,
            y + bleed_offset,
            cover_width,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + cover_left,
            y + height - margin - bleed_offset,
            cover_width,
            margin,
            margin_brush,
        )
        self.add_margin_rect(
            x + cover_left,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )
        self.add_margin_rect(
            x + cover_right - margin,
            y + margin + bleed_offset,
            margin,
            height - 2 * margin - 2 * bleed_offset,
            margin_brush,
        )

    def draw_trim_lines(self, x: float, y: float, width: float, height: float) -> None:
        """Add trim marks at dustjacket edges accounting for bleed."""
        pen = self.get_trim_pen()
        bleed = DUSTJACKET_BLEED * POINTS_PER_MM

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

    def draw_fold_lines(
        self, x: float, y: float, width: float, height: float, flap_width: float
    ) -> None:
        """Mark flap fold positions with dashed purple lines."""
        bleed_offset = DUSTJACKET_BLEED * POINTS_PER_MM
        fold_safety_margin = DUSTJACKET_FOLD_SAFETY_MARGIN * POINTS_PER_MM
        pen = self.get_fold_pen()

        back_fold_x = flap_width + fold_safety_margin / 2 - 1 + bleed_offset
        self.graphics_scene.addLine(
            x + back_fold_x,
            y + bleed_offset,
            x + back_fold_x,
            y + height - bleed_offset,
            pen,
        )

        front_fold_x = width - flap_width - fold_safety_margin / 2 - 1 - bleed_offset
        self.graphics_scene.addLine(
            x + front_fold_x,
            y + bleed_offset,
            x + front_fold_x,
            y + height - bleed_offset,
            pen,
        )

    def draw_barcode(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        spine_width: float,
        flap_width: float,
        safety_margin: float,
    ) -> None:
        """Highlight barcode placement area on back cover section."""
        barcode_width = BARCODE_WIDTH * POINTS_PER_MM
        barcode_height = BARCODE_HEIGHT * POINTS_PER_MM
        bleed_offset = DUSTJACKET_BLEED * POINTS_PER_MM

        back_cover_start = flap_width
        cover_area_width = width - 2 * flap_width
        back_cover_width = (cover_area_width - spine_width) / 2

        barcode_x = (
            x + back_cover_start + back_cover_width - safety_margin - barcode_width
        )
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
            width: Total dustjacket width
            height: Dustjacket height
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

"""Base renderer class for margin and overlay drawing."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.constants import (
    BLEED_LINE_COLOR,
    BLEED_LINE_PEN_WIDTH,
    FOLD_LINE_COLOR,
    FOLD_LINE_PEN_WIDTH,
    GUTTER_COLOR,
    MARGIN_OVERLAY_COLOR,
    MARGIN_RECT_OPACITY,
    TRIM_LINE_COLOR,
    TRIM_LINE_PEN_WIDTH,
)
from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class BaseRenderer:
    """Base class for all margin renderers."""

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        config_manager: Optional[ConfigurationManager] = None,
    ) -> None:
        """Initialize the base renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
            config_manager: Optional configuration manager for reading user preferences
        """
        self.graphics_scene = graphics_scene
        self.config_manager = config_manager
        self._color_cache: dict[str, QColor] = (
            {}
        )  # Cache colors to avoid repeated config lookups
        self._opacity_cache: dict[str, float] = {}  # Cache opacity values
        self._line_width_cache: dict[str, int] = {}  # Cache line widths

    def get_color_from_config(self, color_key: str, default_color: QColor) -> QColor:
        """Get color from configuration or use default.

        Args:
            color_key: Configuration key for the color (e.g., "margin_overlay", "barcode_area")
            default_color: Default color to use if config not available

        Returns:
            QColor from configuration or default
        """
        if not self.config_manager:
            return default_color

        # Check cache first
        if color_key in self._color_cache:
            return self._color_cache[color_key]

        # Get from config
        color_value = self.config_manager.get_value(
            f"colors/{color_key}/color", default_color.name()
        )

        # Handle different types that might be returned
        if isinstance(color_value, QColor):
            color = color_value
        elif isinstance(color_value, str):
            color = QColor(color_value)
        else:
            logger.warning(
                f"Unexpected color type for {color_key}: {type(color_value)}, using default"
            )
            color = default_color

        # Cache it
        self._color_cache[color_key] = color
        return color

    def get_opacity_from_config(
        self, opacity_key: str, default_opacity: float
    ) -> float:
        """Get opacity from configuration or use default.

        Args:
            opacity_key: Configuration key for the opacity (e.g., "margin_overlay", "barcode_area")
            default_opacity: Default opacity to use if config not available

        Returns:
            Opacity value from configuration or default
        """
        if not self.config_manager:
            return default_opacity

        # Check cache first
        if opacity_key in self._opacity_cache:
            return self._opacity_cache[opacity_key]

        # Get from config
        opacity = self.config_manager.get_value(
            f"colors/{opacity_key}/opacity", default_opacity, type=float
        )

        # Cache it
        self._opacity_cache[opacity_key] = opacity
        return float(opacity)

    def get_line_width_from_config(self, width_key: str, default_width: int) -> int:
        """Get line width from configuration or use default.

        Args:
            width_key: Configuration key for the line width (e.g., "fold_lines", "trim_lines")
            default_width: Default width to use if config not available

        Returns:
            Line width from configuration or default
        """
        if not self.config_manager:
            return default_width

        # Check cache first
        if width_key in self._line_width_cache:
            return self._line_width_cache[width_key]

        # Get from config
        width = self.config_manager.get_value(
            f"line_widths/{width_key}", default_width, type=int
        )

        # Cache it
        self._line_width_cache[width_key] = width
        return int(width)

    def clear_caches(self) -> None:
        """Clear all cached configuration values.

        This should be called when configuration changes to ensure
        new values are loaded.
        """
        self._color_cache.clear()
        self._opacity_cache.clear()
        self._line_width_cache.clear()

    def add_margin_rect(
        self, x: float, y: float, w: float, h: float, brush: QBrush
    ) -> None:
        """Draw semi-transparent colored rectangle for margin visualization.

        Args:
            x: Rectangle left edge
            y: Rectangle top edge
            w: Rectangle width
            h: Rectangle height
            brush: Fill color/pattern
        """
        rect = self.graphics_scene.addRect(x, y, w, h, QPen(Qt.PenStyle.NoPen), brush)
        # Get opacity from config for margin overlays
        opacity = self.get_opacity_from_config("margin_overlay", MARGIN_RECT_OPACITY)
        rect.setOpacity(opacity)

    def get_margin_brush(self) -> QBrush:
        """Create brush for safety margin overlay rendering.

        Returns:
            Semi-transparent blue/purple brush
        """
        color = self.get_color_from_config("margin_overlay", MARGIN_OVERLAY_COLOR)
        return QBrush(color)

    def get_fold_pen(self) -> QPen:
        """Create pen for spine/flap fold indicators.

        Returns:
            2px purple dashed line pen
        """
        color = self.get_color_from_config("fold_lines", FOLD_LINE_COLOR)
        width = self.get_line_width_from_config("fold_lines", FOLD_LINE_PEN_WIDTH)
        pen = QPen(color)
        pen.setWidth(width)
        pen.setStyle(Qt.PenStyle.DashLine)
        return pen

    def get_trim_pen(self) -> QPen:
        """Create pen for page edge trim marks.

        Returns:
            1px solid black line pen
        """
        color = self.get_color_from_config("trim_lines", TRIM_LINE_COLOR)
        width = self.get_line_width_from_config("trim_lines", TRIM_LINE_PEN_WIDTH)
        pen = QPen(color)
        pen.setWidth(width)
        pen.setStyle(Qt.PenStyle.SolidLine)
        return pen

    def get_bleed_pen(self) -> QPen:
        """Create pen for bleed line marks.

        Returns:
            1px solid light blue line pen
        """
        color = self.get_color_from_config("bleed_lines", BLEED_LINE_COLOR)
        width = self.get_line_width_from_config("bleed_lines", BLEED_LINE_PEN_WIDTH)
        pen = QPen(color)
        pen.setWidth(width)
        pen.setStyle(Qt.PenStyle.SolidLine)
        return pen

    def get_gutter_brush(self) -> QBrush:
        """Create brush for gutter margin rendering.

        Returns:
            Brush with gutter color (#79c196)
        """
        color = self.get_color_from_config("gutter", GUTTER_COLOR)
        return QBrush(color)

    def add_gutter_rect(self, x: float, y: float, w: float, h: float) -> None:
        """Draw gutter margin rectangle.

        Args:
            x: Rectangle left edge
            y: Rectangle top edge
            w: Rectangle width
            h: Rectangle height
        """
        brush = self.get_gutter_brush()
        rect = self.graphics_scene.addRect(x, y, w, h, QPen(Qt.PenStyle.NoPen), brush)
        # Get opacity from config for gutter (default 0.3)
        opacity = self.get_opacity_from_config("gutter", 0.3)
        rect.setOpacity(opacity)

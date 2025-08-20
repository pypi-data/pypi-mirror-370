"""Margin rendering component for the PDF viewer.

This refactored version delegates to specialized renderers for each document type,
following the Single Responsibility Principle and keeping the file under 400 lines.
"""

from typing import Optional

from PySide6.QtWidgets import QGraphicsScene

from momovu.lib.configuration_manager import ConfigurationManager
from momovu.lib.constants import DUSTJACKET_FLAP_WIDTH, POINTS_PER_MM
from momovu.lib.logger import get_logger
from momovu.presenters.margin import MarginPresenter
from momovu.views.components.renderers.cover import CoverRenderer
from momovu.views.components.renderers.dustjacket import DustjacketRenderer
from momovu.views.components.renderers.interior import InteriorRenderer

logger = get_logger(__name__)


class MarginRenderer:
    """Component responsible for coordinating margin, trim line, and overlay rendering.

    This class delegates actual rendering to specialized renderers based on document type,
    following the Single Responsibility Principle.
    """

    def __init__(
        self,
        graphics_scene: QGraphicsScene,
        margin_presenter: MarginPresenter,
        config_manager: Optional[ConfigurationManager] = None,
    ):
        """Initialize the margin renderer.

        Args:
            graphics_scene: The Qt graphics scene to render to
            margin_presenter: Presenter for margin operations
            config_manager: Optional configuration manager for reading user preferences
        """
        self.graphics_scene = graphics_scene
        self.margin_presenter = margin_presenter
        self.config_manager = config_manager

        # Pass config manager to all child renderers
        self.interior_renderer = InteriorRenderer(graphics_scene, config_manager)
        self.cover_renderer = CoverRenderer(graphics_scene, config_manager)
        self.dustjacket_renderer = DustjacketRenderer(graphics_scene, config_manager)

        self.show_fold_lines = True

    def draw_page_overlays(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skip_trim_edge: Optional[str] = None,
        page_position: Optional[str] = None,
    ) -> None:
        """Render all enabled overlays on top of page content.

        Args:
            x: Page left edge in scene coordinates
            y: Page top edge in scene coordinates
            width: Page width in points
            height: Page height in points
            skip_trim_edge: Optional edge to skip when drawing trim lines ("left" or "right")
            page_position: Optional page position for gutter ("left", "right", "first_alone", "last_alone", "single")
        """
        doc_type = self.margin_presenter.model.document_type

        if self.margin_presenter.model.show_margins:
            self._draw_margins(x, y, width, height, doc_type)

        # Draw gutter AFTER margins but BEFORE other overlays (for interior documents only)
        if (
            doc_type == "interior"
            and self.margin_presenter.model.show_gutter
            and page_position is not None
        ):
            self._draw_gutter(x, y, width, height, page_position)

        # Draw bleed lines BEFORE trim lines so they appear behind
        if self.margin_presenter.model.show_bleed_lines:
            self._draw_bleed_lines(x, y, width, height, doc_type, skip_trim_edge)

        if self.margin_presenter.model.show_trim_lines:
            self._draw_trim_lines(x, y, width, height, doc_type, skip_trim_edge)

        if doc_type in ["cover", "dustjacket"]:
            self._draw_special_overlays(x, y, width, height, doc_type)

    def _draw_margins(
        self, x: float, y: float, width: float, height: float, doc_type: str
    ) -> None:
        """Draw margins based on document type.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            doc_type: Document type (interior, cover, or dustjacket)
        """
        margin = self.margin_presenter.model.safety_margin_points

        if doc_type == "dustjacket":
            spine_width = self.margin_presenter.model.spine_width or 0
            flap_width = self.margin_presenter.model.flap_width or (
                DUSTJACKET_FLAP_WIDTH * POINTS_PER_MM
            )
            self.dustjacket_renderer.draw_margins(
                x, y, width, height, margin, spine_width, flap_width
            )
        elif doc_type == "cover":
            spine_width = self.margin_presenter.model.spine_width or 0
            self.cover_renderer.draw_margins(x, y, width, height, margin, spine_width)
        else:
            self.interior_renderer.draw_margins(x, y, width, height, margin)

    def _draw_trim_lines(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        doc_type: str,
        skip_trim_edge: Optional[str] = None,
    ) -> None:
        """Draw trim lines based on document type.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            doc_type: Document type (interior, cover, or dustjacket)
            skip_trim_edge: Optional edge to skip when drawing trim lines ("left" or "right")
        """
        if doc_type == "dustjacket":
            self.dustjacket_renderer.draw_trim_lines(x, y, width, height)
        elif doc_type == "cover":
            self.cover_renderer.draw_trim_lines(x, y, width, height)
        else:
            self.interior_renderer.draw_trim_lines(x, y, width, height, skip_trim_edge)

    def _draw_special_overlays(
        self, x: float, y: float, width: float, height: float, doc_type: str
    ) -> None:
        """Draw special overlays for cover and dustjacket documents.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            doc_type: Document type (cover or dustjacket)
        """
        if self.show_fold_lines:
            spine_width = self.margin_presenter.model.spine_width or 0
            if spine_width and doc_type == "cover":
                self.cover_renderer.draw_spine_fold_lines(
                    x, y, width, height, spine_width
                )
            elif spine_width and doc_type == "dustjacket":
                # Dustjacket has both spine and flap fold lines
                self.cover_renderer.draw_spine_fold_lines(
                    x, y, width, height, spine_width
                )
                flap_width = self.margin_presenter.model.flap_width or (
                    DUSTJACKET_FLAP_WIDTH * POINTS_PER_MM
                )
                self.dustjacket_renderer.draw_fold_lines(
                    x, y, width, height, flap_width
                )

        if self.margin_presenter.model.show_barcode:
            self._draw_barcode(x, y, width, height, doc_type)

    def _draw_barcode(
        self, x: float, y: float, width: float, height: float, doc_type: str
    ) -> None:
        """Draw barcode for cover and dustjacket documents.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            doc_type: Document type (cover or dustjacket)
        """
        spine_width = self.margin_presenter.model.spine_width or 0
        safety_margin = self.margin_presenter.model.safety_margin_points

        if doc_type == "cover":
            self.cover_renderer.draw_barcode(
                x, y, width, height, spine_width, safety_margin
            )
        elif doc_type == "dustjacket":
            flap_width = self.margin_presenter.model.flap_width or (
                DUSTJACKET_FLAP_WIDTH * POINTS_PER_MM
            )
            self.dustjacket_renderer.draw_barcode(
                x, y, width, height, spine_width, flap_width, safety_margin
            )

    def _draw_bleed_lines(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        doc_type: str,
        skip_trim_edge: Optional[str] = None,
    ) -> None:
        """Draw bleed lines based on document type.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            doc_type: Document type (interior, cover, or dustjacket)
            skip_trim_edge: Optional edge to skip when drawing bleed lines
        """
        if doc_type == "dustjacket":
            self.dustjacket_renderer.draw_bleed_lines(x, y, width, height)
        elif doc_type == "cover":
            self.cover_renderer.draw_bleed_lines(x, y, width, height)
        else:
            # Interior documents don't have bleed lines
            self.interior_renderer.draw_bleed_lines(x, y, width, height, skip_trim_edge)

    def _draw_gutter(
        self, x: float, y: float, width: float, height: float, page_position: str
    ) -> None:
        """Draw gutter margin extension for interior documents.

        Args:
            x: X position of the page
            y: Y position of the page
            width: Page width
            height: Page height
            page_position: Position of page ("left", "right", "first_alone", "last_alone", "single")
        """
        margin = self.margin_presenter.model.safety_margin_points
        gutter_width = self.margin_presenter.model.gutter_width or 0.0

        if gutter_width > 0:
            self.interior_renderer.draw_gutter(
                x, y, width, height, margin, gutter_width, page_position
            )
            logger.debug(
                f"Drew gutter with width {gutter_width} for {page_position} page"
            )

    def set_show_fold_lines(self, show: bool) -> None:
        """Enable/disable spine and flap fold indicators.

        Args:
            show: True to display fold lines on covers/dustjackets
        """
        self.show_fold_lines = show
        logger.debug(f"Fold lines visibility set to: {show}")

    def set_show_gutter(self, show: bool) -> None:
        """Enable/disable gutter margin display.

        Args:
            show: True to display gutter margins on interior documents
        """
        # This is handled by the margin_presenter
        logger.debug(f"Gutter visibility set to: {show}")

    def clear_renderer_caches(self) -> None:
        """Clear cached configuration values in all renderers.

        This should be called when configuration changes to ensure
        new values are loaded.
        """
        if self.interior_renderer:
            self.interior_renderer.clear_caches()
        if self.cover_renderer:
            self.cover_renderer.clear_caches()
        if self.dustjacket_renderer:
            self.dustjacket_renderer.clear_caches()

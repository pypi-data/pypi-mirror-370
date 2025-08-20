"""Zoom controller component for managing view zoom operations.

This component encapsulates all zoom-related functionality, providing a clean
interface for zoom operations while maintaining separation of concerns.
"""

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QObject, QRectF, Qt, Signal
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from momovu.lib.constants import (
    SCENE_FIT_HEIGHT,
    SCENE_FIT_HEIGHT_OFFSET,
    VIEWPORT_FIT_MARGIN,
    ZOOM_IN_FACTOR,
    ZOOM_OUT_FACTOR,
)
from momovu.lib.logger import get_logger

if TYPE_CHECKING:
    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter

logger = get_logger(__name__)


class ZoomController(QObject):
    """Controls all zoom operations for the PDF viewer.

    This class manages zoom in/out operations and fit-to-page functionality,
    handling the complex logic for different document types and view modes.
    It follows the Single Responsibility Principle by focusing solely on
    zoom-related operations.
    """

    zoom_changed = Signal(float)  # Emitted when zoom level changes

    def __init__(
        self,
        graphics_view: QGraphicsView,
        graphics_scene: QGraphicsScene,
        parent: Optional[QObject] = None,
    ) -> None:
        """Initialize the zoom controller.

        Args:
            graphics_view: The graphics view to control zoom for
            graphics_scene: The graphics scene containing the content
            parent: Optional parent QObject for proper cleanup
        """
        super().__init__(parent)
        self.graphics_view = graphics_view
        self.graphics_scene = graphics_scene

        self._current_zoom: float = 1.0

        self._get_margin_presenter: Optional[
            Callable[[], Optional[MarginPresenter]]
        ] = None
        self._get_navigation_presenter: Optional[
            Callable[[], Optional[NavigationPresenter]]
        ] = None
        self._get_document_presenter: Optional[
            Callable[[], Optional[DocumentPresenter]]
        ] = None
        self._update_page_label: Optional[Callable[[], None]] = None

    def set_presenter_callbacks(
        self,
        get_margin_presenter: Callable[[], Optional["MarginPresenter"]],
        get_navigation_presenter: Callable[[], Optional["NavigationPresenter"]],
        get_document_presenter: Callable[[], Optional["DocumentPresenter"]],
    ) -> None:
        """Set callbacks for accessing presenters.

        This allows the controller to access presenter state without
        creating tight coupling.

        Args:
            get_margin_presenter: Callback to get margin presenter
            get_navigation_presenter: Callback to get navigation presenter
            get_document_presenter: Callback to get document presenter
        """
        self._get_margin_presenter = get_margin_presenter
        self._get_navigation_presenter = get_navigation_presenter
        self._get_document_presenter = get_document_presenter

    def set_update_callback(self, update_page_label: Callable[[], None]) -> None:
        """Set callback for updating UI after zoom operations.

        Args:
            update_page_label: Callback to update page label
        """
        self._update_page_label = update_page_label

    def zoom_in(self) -> None:
        """Increase zoom level by the standard zoom factor from viewport center."""
        self.graphics_view.scale(ZOOM_IN_FACTOR, ZOOM_IN_FACTOR)
        self._current_zoom *= ZOOM_IN_FACTOR
        self.zoom_changed.emit(self._current_zoom)
        logger.debug(f"Zoomed in to {self._current_zoom:.1%}")
        # Don't update scene rect here - it causes view jumps

    def zoom_out(self) -> None:
        """Decrease zoom level by the standard zoom factor from viewport center."""
        self.graphics_view.scale(ZOOM_OUT_FACTOR, ZOOM_OUT_FACTOR)
        self._current_zoom *= ZOOM_OUT_FACTOR
        self.zoom_changed.emit(self._current_zoom)
        logger.debug(f"Zoomed out to {self._current_zoom:.1%}")
        # Don't update scene rect here - it causes view jumps

    def get_current_zoom(self) -> float:
        """Get the current zoom level.

        Returns:
            Current zoom level (1.0 = 100%)
        """
        return self._current_zoom

    def set_zoom_level(self, zoom_level: float, emit_signal: bool = True) -> None:
        """Set the internal zoom level without applying scale.

        Used by GraphicsView after it performs mouse-centered zoom.
        This method only updates the tracking value.

        Args:
            zoom_level: The new zoom level (1.0 = 100%)
            emit_signal: Whether to emit the zoom_changed signal
        """
        self._current_zoom = zoom_level
        if emit_signal:
            self.zoom_changed.emit(self._current_zoom)

    def fit_to_page(self) -> None:
        """Fit the current page(s) to the view.

        This method handles different fitting strategies based on:
        - Document type (interior/cover/dustjacket)
        - View mode (single/side-by-side)

        For interior documents with all pages rendered, this fits
        only the current page in view, not all pages.
        """
        margin_presenter = (
            self._get_margin_presenter() if self._get_margin_presenter else None
        )
        navigation_presenter = (
            self._get_navigation_presenter() if self._get_navigation_presenter else None
        )

        if not margin_presenter or not navigation_presenter:
            logger.warning("Presenters not available for fit_to_page")
            self._fit_entire_scene()
            return

        document_type = margin_presenter.model.document_type
        view_mode = navigation_presenter.model.view_mode

        if document_type == "interior" and view_mode == "single":
            self._fit_interior_single_page(navigation_presenter)
        elif document_type == "interior" and view_mode == "side_by_side":
            self._fit_interior_side_by_side(navigation_presenter)
        else:
            self._fit_entire_scene()

        if self._update_page_label:
            try:
                self._update_page_label()
            except RuntimeError as e:
                # The main window or its widgets may have been deleted
                logger.debug(f"Error updating page label during fit_to_page: {e}")

    def _fit_interior_single_page(
        self, navigation_presenter: "NavigationPresenter"
    ) -> None:
        """Fit a single interior page to the view.

        Args:
            navigation_presenter: Navigation presenter for current page info
        """
        from momovu.views.page_item import PageItem

        current_page = navigation_presenter.get_current_page()

        page_items = [
            item
            for item in self.graphics_scene.items()
            if isinstance(item, PageItem) and item.page_number == current_page
        ]

        if page_items:
            page_rect = page_items[0].boundingRect()
            page_rect = page_items[0].mapRectToScene(page_rect)

            if not page_rect.isEmpty():
                self._fit_rect_to_view(page_rect)
                logger.debug(f"Fitted to page {current_page + 1}")
        else:
            logger.debug(
                f"No PageItem found for page {current_page}, fitting scene width"
            )
            self._fit_scene_width()

    def _fit_interior_side_by_side(
        self, navigation_presenter: "NavigationPresenter"
    ) -> None:
        """Fit interior pages in side-by-side mode.

        Args:
            navigation_presenter: Navigation presenter for current page info
        """
        from momovu.views.page_item import PageItem

        current_page = navigation_presenter.get_current_page()

        target_pages = self._calculate_side_by_side_pages(
            current_page, navigation_presenter
        )

        page_items = [
            item
            for item in self.graphics_scene.items()
            if isinstance(item, PageItem)
            and hasattr(item, "page_number")
            and item.page_number in target_pages
        ]

        if not page_items:
            logger.debug("No PageItems found for current page pair, skipping fit")
            return

        bounds = QRectF()
        for item in page_items:
            item_rect = item.mapRectToScene(item.boundingRect())
            bounds = bounds.united(item_rect)

        if self._is_valid_rect(bounds):
            self._fit_rect_to_view(bounds)
            logger.debug("Fitted to current page pair in side-by-side mode")

    def _calculate_side_by_side_pages(
        self, current_page: int, navigation_presenter: "NavigationPresenter"
    ) -> list[int]:
        """Calculate which pages to show in side-by-side mode.

        Args:
            current_page: Current page index (0-based)
            navigation_presenter: Navigation presenter for total pages

        Returns:
            List of page indices to display
        """
        # Page 0 is alone, then pairs are (1,2), (3,4), (5,6), etc.
        if current_page == 0:
            return [0]

        if current_page % 2 == 0:
            return [current_page - 1, current_page]
        else:
            document_presenter = (
                self._get_document_presenter() if self._get_document_presenter else None
            )
            if document_presenter:
                # Check page count safely
                page_count = document_presenter.get_page_count()
                if current_page + 1 < page_count:
                    return [current_page, current_page + 1]

            # Fallback to single page
            return [current_page]

    def _fit_entire_scene(self) -> None:
        """Fit all scene content to the view (used for cover/dustjacket)."""
        scene_rect = self.graphics_scene.itemsBoundingRect()

        if self._is_valid_rect(scene_rect):
            self._fit_rect_to_view(scene_rect)
            logger.debug(f"Fitted to entire scene: {scene_rect}")

    def _fit_scene_width(self) -> None:
        """Fit scene width to view width (fallback when page items not found)."""
        scene_rect = self.graphics_scene.itemsBoundingRect()
        if not scene_rect.isEmpty():
            view_center = self.graphics_view.mapToScene(
                self.graphics_view.viewport().rect().center()
            )
            fit_rect = QRectF(
                scene_rect.left(),
                view_center.y() - SCENE_FIT_HEIGHT_OFFSET,
                scene_rect.width(),
                SCENE_FIT_HEIGHT,
            )
            self._fit_rect_to_view(fit_rect)

    def _fit_rect_to_view(self, rect: QRectF) -> None:
        """Scale view to fit the given rectangle with margins.

        Args:
            rect: Scene rectangle to fit within the viewport
        """
        viewport_rect = self.graphics_view.viewport().rect()
        viewport_rect.adjust(
            VIEWPORT_FIT_MARGIN,
            VIEWPORT_FIT_MARGIN,
            -VIEWPORT_FIT_MARGIN,
            -VIEWPORT_FIT_MARGIN,
        )

        try:
            # Store the old transform to calculate zoom change
            old_transform = self.graphics_view.transform()
            old_scale = old_transform.m11()

            # Perform the fit operation
            self.graphics_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

            # Calculate the actual zoom level by comparing transforms
            new_transform = self.graphics_view.transform()
            new_scale = new_transform.m11()

            # Handle edge cases for zoom calculation
            if isinstance(old_scale, (int, float)) and isinstance(
                new_scale, (int, float)
            ):
                if old_scale > 0 and new_scale > 0:
                    # Normal case: calculate relative change
                    scale_factor = new_scale / old_scale
                    self._current_zoom *= scale_factor
                elif new_scale > 0:
                    # Initial case or reset: use absolute scale
                    # The new scale IS the zoom level relative to identity transform
                    self._current_zoom = new_scale
                else:
                    # Fallback: something went wrong, assume no zoom
                    logger.warning(
                        "Invalid transform scale detected, defaulting zoom to 1.0"
                    )
                    self._current_zoom = 1.0
            else:
                # Mock or test case - just perform the fit without zoom calculation
                logger.debug(  # type: ignore[unreachable]
                    "Non-numeric scale detected (likely mock), skipping zoom calculation"
                )
                # Keep current zoom level unchanged

            # Emit the actual zoom level
            self.zoom_changed.emit(self._current_zoom)
            logger.debug(f"Fit to page - actual zoom: {self._current_zoom:.2f}")
        except (AttributeError, TypeError) as e:
            # Handle mock objects or other test scenarios
            logger.debug(f"Error calculating zoom during fit: {e}")
            # Still perform the fit operation
            self.graphics_view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            # Emit current zoom level
            self.zoom_changed.emit(self._current_zoom)

    def _is_valid_rect(self, rect: QRectF) -> bool:
        """Check if rectangle has positive dimensions.

        Args:
            rect: Rectangle to validate

        Returns:
            True if width and height are both positive
        """
        return not rect.isEmpty() and rect.width() > 0 and rect.height() > 0

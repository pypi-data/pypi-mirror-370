"""Window initializer component for handling complex initialization."""

from typing import Any, Optional

from PySide6.QtPdf import QPdfDocument

from momovu.lib.logger import get_logger
from momovu.models.document import Document
from momovu.models.margin_settings import MarginSettingsModel
from momovu.models.view_state import ViewStateModel
from momovu.presenters.document import DocumentPresenter
from momovu.presenters.margin import MarginPresenter
from momovu.presenters.navigation import NavigationPresenter

logger = get_logger(__name__)


class WindowSetup:
    """Handles complex initialization for the main window."""

    def __init__(self, main_window: Any) -> None:
        """Initialize the window initializer.

        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window

    def init_models_and_presenters(self) -> None:
        """Create MVP components and wire them together."""
        self.main_window.pdf_document = QPdfDocument()

        self.main_window.document_model = Document()
        self.main_window.margin_model = MarginSettingsModel()
        self.main_window.view_model = ViewStateModel()

        self.main_window.document_presenter = DocumentPresenter(
            self.main_window.document_model
        )
        self.main_window.document_presenter.set_qt_document(
            self.main_window.pdf_document
        )
        self.main_window.margin_presenter = MarginPresenter(
            self.main_window.margin_model
        )
        self.main_window.navigation_presenter = NavigationPresenter(
            self.main_window.view_model, total_pages=0
        )

        logger.debug("Models and presenters initialized")

    def store_init_params(
        self,
        pdf_path: Optional[str],
        num_pages: Optional[int],
        book_type: Optional[str],
        side_by_side: bool,
        show_margins: Optional[bool],
        show_trim_lines: Optional[bool],
        show_barcode: Optional[bool],
        show_fold_lines: Optional[bool],
        show_bleed_lines: Optional[bool],
        show_gutter: Optional[bool],
        start_presentation: bool,
        start_fullscreen: bool,
    ) -> None:
        """Cache constructor parameters for deferred initialization.

        Args:
            pdf_path: Initial PDF to load
            num_pages: Page count for spine width calculation
            book_type: One of 'interior', 'cover', 'dustjacket'
            side_by_side: Enable page pair view
            show_margins: Display safety margins
            show_trim_lines: Display trim indicators
            show_barcode: Display barcode area
            show_fold_lines: Display spine/flap folds
            show_bleed_lines: Display bleed lines
            show_gutter: Display gutter margin
            start_presentation: Launch in presentation mode
            start_fullscreen: Launch fullscreen
        """
        self.main_window._pdf_path = pdf_path
        self.main_window._num_pages = num_pages or 100
        self.main_window._book_type = book_type or "interior"
        self.main_window._side_by_side = side_by_side
        self.main_window._show_margins = (
            show_margins if show_margins is not None else True
        )
        self.main_window._show_trim_lines = (
            show_trim_lines if show_trim_lines is not None else True
        )
        self.main_window._show_barcode = (
            show_barcode if show_barcode is not None else True
        )
        self.main_window._show_fold_lines = (
            show_fold_lines if show_fold_lines is not None else True
        )
        self.main_window._show_bleed_lines = (
            show_bleed_lines if show_bleed_lines is not None else True
        )
        self.main_window._show_gutter = show_gutter if show_gutter is not None else True
        self.main_window._start_presentation = start_presentation
        self.main_window._start_fullscreen = start_fullscreen

        logger.debug("Initialization parameters stored")

    def apply_initial_settings(self) -> None:
        """Configure UI state from stored initialization parameters."""
        self.main_window.toggle_manager.set_document_type(self.main_window._book_type)

        if self.main_window._side_by_side and self.main_window._book_type == "interior":
            self.main_window.side_by_side_action.setChecked(True)
            self.main_window.navigation_presenter.set_view_mode("side_by_side")
            # Set spinbox to increment by 2 in side-by-side mode
            if self.main_window.page_number_spinbox:
                self.main_window.page_number_spinbox.setSingleStep(2)

        self.main_window.margin_presenter.set_num_pages(self.main_window._num_pages)
        self.main_window.margin_presenter.set_show_margins(
            self.main_window._show_margins
        )
        self.main_window.margin_presenter.set_show_trim_lines(
            self.main_window._show_trim_lines
        )
        self.main_window.margin_presenter.set_show_barcode(
            self.main_window._show_barcode
        )
        self.main_window.margin_presenter.set_show_fold_lines(
            self.main_window._show_fold_lines
        )
        self.main_window.margin_presenter.set_show_bleed_lines(
            self.main_window._show_bleed_lines
        )
        self.main_window.margin_presenter.set_show_gutter(self.main_window._show_gutter)

        self.main_window.num_pages_spinbox.setValue(self.main_window._num_pages)

        logger.debug("Initial settings applied")

    def initialize_document(self) -> None:
        """Load initial PDF and apply window display mode."""
        if self.main_window._pdf_path:
            self.main_window.load_pdf(self.main_window._pdf_path)

        self.main_window.ui_state_manager.apply_window_state(
            self.main_window._start_fullscreen, self.main_window._start_presentation
        )

        logger.info("Document and window state initialized")

    def create_action_aliases(self) -> None:
        """Map builder-created actions to main window attributes for easy access."""
        for name, action in self.main_window.menu_builder.actions.items():
            setattr(self.main_window, f"{name}_action", action)

        for name, action in self.main_window.toolbar_builder.actions.items():
            setattr(self.main_window, f"{name}_action", action)

        self.main_window.page_number_spinbox = (
            self.main_window.toolbar_builder.get_widget("page_spinbox")
        )
        self.main_window.num_pages_spinbox = (
            self.main_window.toolbar_builder.get_widget("num_pages_spinbox")
        )
        self.main_window.toolbar = self.main_window.toolbar_builder.toolbar

        logger.debug("Action aliases created")

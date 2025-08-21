"""Dialog manager component for handling all dialog operations.

This component follows the Single Responsibility Principle by centralizing
all dialog-related functionality, making the main window cleaner and more focused.
"""

from typing import TYPE_CHECKING, Callable, Optional

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QFileDialog, QInputDialog, QWidget

from momovu.lib.logger import get_logger
from momovu.lib.shortcuts_dialog import ShortcutsDialog
from momovu.views.components.about_dialog import AboutDialog

if TYPE_CHECKING:
    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.navigation import NavigationPresenter

logger = get_logger(__name__)


class DialogManager:
    """Manages all dialog operations for the application.

    This class encapsulates dialog creation, display, and result handling,
    providing a clean interface for the main window to use dialogs without
    dealing with implementation details.
    """

    def __init__(self, parent: QWidget) -> None:
        """Initialize the dialog manager.

        Args:
            parent: The parent widget (typically MainWindow) for dialogs
        """
        self.parent = parent
        self._file_load_callback: Optional[Callable[[str], None]] = None
        self._page_navigation_callback: Optional[Callable[[int], None]] = None

    def set_file_load_callback(self, callback: Callable[[str], None]) -> None:
        """Register handler for file selection from open dialog.

        Args:
            callback: Function that receives the selected PDF file path
        """
        self._file_load_callback = callback

    def set_page_navigation_callback(self, callback: Callable[[int], None]) -> None:
        """Register handler for go-to-page dialog results.

        Args:
            callback: Function that receives the target page number (1-based)
        """
        self._page_navigation_callback = callback

    def show_open_file_dialog(self) -> None:
        """Display PDF file selection dialog and trigger callback on selection."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent,
                QCoreApplication.translate("DialogManager", "Open PDF"),
                "",
                QCoreApplication.translate("DialogManager", "PDF Files (*.pdf)"),
            )

            if file_path and self._file_load_callback:
                logger.debug(f"File selected: {file_path}")
                self._file_load_callback(file_path)
            elif file_path:
                logger.warning("File selected but no callback registered")

        except Exception as e:
            logger.error(f"Error in file dialog: {e}", exc_info=True)
            raise

    def show_shortcuts_dialog(self) -> None:
        """Display the keyboard shortcuts reference dialog."""
        dialog = ShortcutsDialog(self.parent)
        dialog.exec()
        logger.debug("Shortcuts dialog shown")

    def show_about_dialog(self) -> None:
        """Display application information and credits dialog."""
        dialog = AboutDialog(self.parent)
        dialog.exec()
        logger.debug("About dialog shown")

    def show_go_to_page_dialog(
        self, current_page: int, total_pages: int, document_loaded: bool
    ) -> None:
        """Display page number input dialog and trigger navigation callback.

        Args:
            current_page: Currently displayed page (1-based)
            total_pages: Maximum page number allowed
            document_loaded: False prevents dialog display
        """
        if not document_loaded:
            logger.debug("Go to page dialog requested but no document loaded")
            return

        if total_pages <= 0:
            logger.warning(f"Invalid total pages: {total_pages}")
            return

        page_num, ok = QInputDialog.getInt(
            self.parent,
            QCoreApplication.translate("DialogManager", "Go to Page"),
            QCoreApplication.translate(
                "DialogManager", "Enter page number (1-{total_pages}):"
            ).format(total_pages=total_pages),
            value=current_page,
            minValue=1,
            maxValue=total_pages,
        )

        if ok and self._page_navigation_callback:
            logger.debug(f"Go to page: {page_num}")
            self._page_navigation_callback(page_num)
        elif ok:
            logger.warning("Page selected but no navigation callback registered")

    def show_go_to_page_dialog_with_presenters(
        self,
        document_presenter: Optional["DocumentPresenter"],
        navigation_presenter: Optional["NavigationPresenter"],
    ) -> None:
        """Extract page info from presenters and show go-to-page dialog.

        Args:
            document_presenter: Source for document loaded state
            navigation_presenter: Source for current/total page counts
        """
        if not document_presenter or not navigation_presenter:
            logger.debug("Go to page dialog requested but presenters not available")
            return

        if not document_presenter.is_document_loaded():
            logger.debug("Go to page dialog requested but no document loaded")
            return

        # Check if we have access to margin presenter to determine document type
        if hasattr(self.parent, "margin_presenter") and self.parent.margin_presenter:
            doc_type = self.parent.margin_presenter.model.document_type
            if doc_type != "interior":
                logger.debug(
                    f"Go to page dialog requested for {doc_type} document - not applicable"
                )
                return

        total_pages = navigation_presenter.get_total_pages()
        current_page = navigation_presenter.get_current_page() + 1  # Convert to 1-based

        self.show_go_to_page_dialog(
            current_page=current_page, total_pages=total_pages, document_loaded=True
        )

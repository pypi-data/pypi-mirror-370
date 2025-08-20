"""Toolbar builder component for the main window.

This component handles toolbar creation and setup.
"""

from typing import TYPE_CHECKING, Any, Optional, Union

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QLabel, QMainWindow, QSpinBox, QStyle, QToolBar, QWidget

from momovu.lib.constants import DEFAULT_PAGE_COUNT, PAGE_SPINBOX_MAX, PAGE_SPINBOX_MIN
from momovu.lib.logger import get_logger
from momovu.views.components.page_spinbox import PageSpinBox

if TYPE_CHECKING:
    from momovu.presenters.margin import MarginPresenter

logger = get_logger(__name__)


class ToolbarBuilder:
    """Component responsible for building and managing the toolbar."""

    def __init__(self, main_window: QMainWindow) -> None:
        """Initialize the toolbar builder.

        Args:
            main_window: The main window to add toolbar to
        """
        self.main_window = main_window
        self.toolbar: Optional[QToolBar] = None
        self.margin_presenter: Optional[MarginPresenter] = None

        self.widgets: dict[str, Union[QSpinBox, QWidget]] = {}
        self.actions: dict[str, QAction] = {}

        self.page_label: Optional[QLabel] = None
        self.pages_label: Optional[QLabel] = None
        self.page_label_action: Optional[QAction] = None
        self.page_spinbox_action: Optional[QAction] = None
        self.pages_label_action: Optional[QAction] = None
        self.pages_spinbox_action: Optional[QAction] = None

    def _try_icons(self, icon_names: list[str], action_name: str) -> Optional[QIcon]:
        """Attempt to load theme icons in priority order.

        Args:
            icon_names: Icon names to try (first match wins)
            action_name: Action description for debug logging

        Returns:
            First available theme icon, or None if none found
        """
        for icon_name in icon_names:
            if QIcon.hasThemeIcon(icon_name):
                logger.debug(f"Using theme icon '{icon_name}' for {action_name}")
                return QIcon.fromTheme(icon_name)

        logger.debug(
            f"Theme icons not available for {action_name}: {', '.join(icon_names)}"
        )
        return None

    def build_toolbar(
        self,
        menu_actions: dict[str, Any],
        margin_presenter: Optional["MarginPresenter"] = None,
    ) -> None:
        """Create main toolbar with navigation, page controls, and zoom actions.

        Args:
            menu_actions: Menu actions to reuse in toolbar (e.g., 'open')
            margin_presenter: Presenter for determining document-specific controls
        """
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setObjectName(
            "MainToolbar"
        )  # Set object name for saveState/restoreState
        self.main_window.addToolBar(self.toolbar)
        self.margin_presenter = margin_presenter

        if self.toolbar:
            open_action = menu_actions.get("open")
            if open_action:
                self.toolbar.addAction(open_action)
            self.toolbar.addSeparator()

            self._add_navigation_actions()
            self._add_page_spinbox()
            self.toolbar.addSeparator()

            self._add_num_pages_spinbox()
            self.toolbar.addSeparator()

            self._add_zoom_actions()

        logger.info("Toolbar built successfully")

    def _add_navigation_actions(self) -> None:
        """Add first/previous/next/last page navigation buttons."""
        if self.toolbar:
            style = self.main_window.style()

            self.actions["first_page"] = QAction(
                QCoreApplication.translate("MainWindow", "First"), self.main_window
            )
            icon = self._try_icons(["go-first-symbolic", "go-first"], "First Page")
            if icon:
                self.actions["first_page"].setIcon(icon)
            else:
                icon = style.standardIcon(QStyle.SP_MediaSkipBackward)  # type: ignore[attr-defined]
                if not icon.isNull():
                    self.actions["first_page"].setIcon(icon)
                    logger.debug(
                        "Using standard icon SP_MediaSkipBackward for First Page"
                    )
                else:
                    logger.debug(
                        "No suitable icon found for First Page, using text only"
                    )
            self.actions["first_page"].setToolTip(
                QCoreApplication.translate("MainWindow", "Go to first page (Home)")
            )
            self.actions["first_page"].setShortcut("Home")
            self.toolbar.addAction(self.actions["first_page"])

            self.actions["prev_page"] = QAction(
                QCoreApplication.translate("MainWindow", "Previous"), self.main_window
            )
            icon = self._try_icons(
                ["go-previous-symbolic", "go-previous"], "Previous Page"
            )
            if icon:
                self.actions["prev_page"].setIcon(icon)
            else:
                icon = style.standardIcon(QStyle.SP_MediaSeekBackward)  # type: ignore[attr-defined]
                if not icon.isNull():
                    self.actions["prev_page"].setIcon(icon)
                    logger.debug(
                        "Using standard icon SP_MediaSeekBackward for Previous Page"
                    )
                else:
                    logger.debug(
                        "No suitable icon found for Previous Page, using text only"
                    )
            self.actions["prev_page"].setToolTip(
                QCoreApplication.translate("MainWindow", "Go to previous page")
            )
            # Arrow key shortcuts removed - handled by zoom-aware logic in GraphicsView
            self.toolbar.addAction(self.actions["prev_page"])

            self.actions["next_page"] = QAction(
                QCoreApplication.translate("MainWindow", "Next"), self.main_window
            )
            icon = self._try_icons(["go-next-symbolic", "go-next"], "Next Page")
            if icon:
                self.actions["next_page"].setIcon(icon)
            else:
                icon = style.standardIcon(QStyle.SP_MediaSeekForward)  # type: ignore[attr-defined]
                if not icon.isNull():
                    self.actions["next_page"].setIcon(icon)
                    logger.debug(
                        "Using standard icon SP_MediaSeekForward for Next Page"
                    )
                else:
                    logger.debug(
                        "No suitable icon found for Next Page, using text only"
                    )
            self.actions["next_page"].setToolTip(
                QCoreApplication.translate("MainWindow", "Go to next page")
            )
            # Arrow key shortcuts removed - handled by zoom-aware logic in GraphicsView
            self.toolbar.addAction(self.actions["next_page"])

            self.actions["last_page"] = QAction(
                QCoreApplication.translate("MainWindow", "Last"), self.main_window
            )
            icon = self._try_icons(["go-last-symbolic", "go-last"], "Last Page")
            if icon:
                self.actions["last_page"].setIcon(icon)
            else:
                icon = style.standardIcon(QStyle.SP_MediaSkipForward)  # type: ignore[attr-defined]
                if not icon.isNull():
                    self.actions["last_page"].setIcon(icon)
                    logger.debug(
                        "Using standard icon SP_MediaSkipForward for Last Page"
                    )
                else:
                    logger.debug(
                        "No suitable icon found for Last Page, using text only"
                    )
            self.actions["last_page"].setToolTip(
                QCoreApplication.translate("MainWindow", "Go to last page (End)")
            )
            self.actions["last_page"].setShortcut("End")
            self.toolbar.addAction(self.actions["last_page"])

    def _add_page_spinbox(self) -> None:
        """Add current page number input control for interior documents."""
        if self.toolbar:
            self.page_label = QLabel(QCoreApplication.translate("MainWindow", "Page:"))
            self.page_label_action = self.toolbar.addWidget(self.page_label)

            spinbox = PageSpinBox()
            spinbox.setMinimum(PAGE_SPINBOX_MIN)
            spinbox.setMaximum(PAGE_SPINBOX_MIN)  # Will be updated when document loads
            spinbox.setValue(PAGE_SPINBOX_MIN)
            spinbox.setToolTip(
                QCoreApplication.translate("MainWindow", "Current page number")
            )
            spinbox.set_main_window(self.main_window)
            self.widgets["page_spinbox"] = spinbox
            self.page_spinbox_action = self.toolbar.addWidget(spinbox)

    def _add_num_pages_spinbox(self) -> None:
        """Add page count input for spine width calculation on covers/dustjackets."""
        if self.toolbar:
            self.pages_label = QLabel(
                QCoreApplication.translate("MainWindow", "Pages:")
            )
            self.pages_label_action = self.toolbar.addWidget(self.pages_label)

            spinbox = QSpinBox()
            spinbox.setMinimum(PAGE_SPINBOX_MIN)
            spinbox.setMaximum(PAGE_SPINBOX_MAX)
            spinbox.setValue(DEFAULT_PAGE_COUNT)
            spinbox.setToolTip(
                QCoreApplication.translate(
                    "MainWindow", "Number of pages for spine width calculation"
                )
            )
            self.widgets["num_pages_spinbox"] = spinbox
            self.pages_spinbox_action = self.toolbar.addWidget(spinbox)

    def _add_zoom_actions(self) -> None:
        """Add zoom in/out and fit-to-page buttons."""
        if self.toolbar:
            style = self.main_window.style()

            self.actions["zoom_in"] = QAction(
                QCoreApplication.translate("MainWindow", "Zoom In"), self.main_window
            )
            icon = self._try_icons(["zoom-in-symbolic", "zoom-in"], "Zoom In")
            if icon:
                self.actions["zoom_in"].setIcon(icon)
            else:
                logger.debug("No suitable icon found for Zoom In, using text only")
            self.actions["zoom_in"].setToolTip(
                QCoreApplication.translate("MainWindow", "Zoom in (Ctrl++)")
            )
            self.actions["zoom_in"].setShortcut("Ctrl++")
            self.toolbar.addAction(self.actions["zoom_in"])

            self.actions["zoom_out"] = QAction(
                QCoreApplication.translate("MainWindow", "Zoom Out"), self.main_window
            )
            icon = self._try_icons(["zoom-out-symbolic", "zoom-out"], "Zoom Out")
            if icon:
                self.actions["zoom_out"].setIcon(icon)
            else:
                logger.debug("No suitable icon found for Zoom Out, using text only")
            self.actions["zoom_out"].setToolTip(
                QCoreApplication.translate("MainWindow", "Zoom out (Ctrl+-)")
            )
            self.actions["zoom_out"].setShortcut("Ctrl+-")
            self.toolbar.addAction(self.actions["zoom_out"])

            self.actions["fit_page"] = QAction(
                QCoreApplication.translate("MainWindow", "Fit Page"), self.main_window
            )
            icon = self._try_icons(
                ["zoom-fit-best-symbolic", "zoom-fit-best"], "Fit Page"
            )
            if icon:
                self.actions["fit_page"].setIcon(icon)
            else:
                icon = style.standardIcon(QStyle.SP_TitleBarNormalButton)  # type: ignore[attr-defined]
                if not icon.isNull():
                    self.actions["fit_page"].setIcon(icon)
                    logger.debug(
                        "Using standard icon SP_TitleBarNormalButton for Fit Page"
                    )
                else:
                    logger.debug("No suitable icon found for Fit Page, using text only")
            self.actions["fit_page"].setToolTip(
                QCoreApplication.translate("MainWindow", "Fit page to window (Ctrl+0)")
            )
            self.actions["fit_page"].setShortcut("Ctrl+0")
            self.toolbar.addAction(self.actions["fit_page"])

    def get_widget(self, name: str) -> Optional[Union[QSpinBox, QWidget]]:
        """Retrieve a toolbar widget by its identifier.

        Args:
            name: Widget identifier (e.g., 'page_spinbox', 'num_pages_spinbox')

        Returns:
            The widget if found, None otherwise
        """
        return self.widgets.get(name)

    def update_toolbar_visibility(self, is_viewing_all_pages: bool = False) -> None:
        """Show/hide toolbar controls based on document type.

        Visibility rules:
        - Interior: Shows page navigation and current page spinbox
        - Cover/Dustjacket: Shows page count spinbox for spine calculation
        - Navigation buttons only appear for multi-page interior documents

        Args:
            is_viewing_all_pages: Deprecated parameter, kept for compatibility
        """
        if not self.margin_presenter:
            return

        doc_type = self.margin_presenter.get_document_type()

        show_page = doc_type == "interior"
        show_pages = doc_type in ["cover", "dustjacket"]
        show_navigation = doc_type == "interior"

        if self.page_label_action and self.page_spinbox_action:
            self.page_label_action.setVisible(show_page)
            self.page_spinbox_action.setVisible(show_page)
            logger.debug(f"Set page actions visible={show_page}")

        if self.pages_label_action and self.pages_spinbox_action:
            self.pages_label_action.setVisible(show_pages)
            self.pages_spinbox_action.setVisible(show_pages)
            logger.debug(f"Set pages actions visible={show_pages}")

        navigation_actions = ["first_page", "prev_page", "next_page", "last_page"]
        for action_name in navigation_actions:
            action = self.actions.get(action_name)
            if action:
                action.setVisible(show_navigation)
                logger.debug(f"Set {action_name} visible={show_navigation}")

        logger.debug(
            f"Toolbar visibility updated - doc_type: {doc_type}, viewing_all: {is_viewing_all_pages}, "
            f"show_page: {show_page}, show_pages: {show_pages}, show_navigation: {show_navigation}"
        )

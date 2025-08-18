"""Custom QSpinBox that properly handles navigation keys."""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QSpinBox

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


class PageSpinBox(QSpinBox):
    """Custom spinbox for page navigation that doesn't interfere with document navigation keys."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize the page spinbox.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.main_window: Optional[Any] = None
        # Disable keyboard tracking so valueChanged only fires on Enter/focus lost/arrows
        self.setKeyboardTracking(False)

    def set_main_window(self, main_window: Any) -> None:
        """Connect to main window for delegating navigation keys.

        Args:
            main_window: MainWindow instance with graphics_view
        """
        self.main_window = main_window

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Intercept navigation keys and delegate to graphics view.

        Allows arrow keys, page up/down, etc. to navigate document
        instead of changing spinbox value.

        Args:
            event: Qt keyboard event
        """
        key = event.key()

        navigation_keys = {
            Qt.Key.Key_PageUp,
            Qt.Key.Key_PageDown,
            Qt.Key.Key_Home,
            Qt.Key.Key_End,
            Qt.Key.Key_Space,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
        }

        if key in navigation_keys:
            if self.main_window is not None and hasattr(
                self.main_window, "graphics_view"
            ):
                logger.debug(f"Passing navigation key {key} to graphics view")
                self.main_window.graphics_view.keyPressEvent(event)
            return

        super().keyPressEvent(event)

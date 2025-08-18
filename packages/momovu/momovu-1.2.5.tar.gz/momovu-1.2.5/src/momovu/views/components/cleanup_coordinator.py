"""Cleanup coordinator for managing resource cleanup during shutdown.

This component handles the orderly cleanup of all resources when the main window
closes or encounters an error during initialization. It ensures components are
cleaned up in the correct order to prevent crashes from dangling references.
"""

from typing import TYPE_CHECKING

from momovu.lib.logger import get_logger

if TYPE_CHECKING:
    from momovu.views.main_window import MainWindow

logger = get_logger(__name__)


class CleanupCoordinator:
    """Coordinates cleanup of all components during shutdown.

    This class manages the cleanup process in phases to ensure proper ordering
    and prevent crashes from dangling signal connections or references.
    """

    def __init__(self, main_window: "MainWindow") -> None:
        """Initialize the cleanup coordinator.

        Args:
            main_window: Reference to the main window containing components to clean up
        """
        self.main_window = main_window

    def cleanup_resources(self) -> None:
        """Execute phased shutdown sequence to safely release all resources.

        Cleanup phases:
        1. Disconnect signals (prevents crashes from dangling connections)
        2. Clean up view components (they reference other components)
        3. Clear graphics scene
        4. Clean up PDF document
        5. Clean up presenters
        """
        try:
            if not self.main_window._resources_initialized:
                return

            logger.info("Starting resource cleanup")

            if not hasattr(self.main_window, "_shutting_down"):
                self.main_window._shutting_down = True  # type: ignore[attr-defined]

            # Phase 1: Disconnect signals first (prevents crashes from dangling connections)
            if (
                hasattr(self.main_window, "signal_connector")
                and self.main_window.signal_connector
            ):
                try:
                    self.main_window.signal_connector.cleanup()
                    logger.debug("SignalConnections cleaned up")
                except Exception as e:
                    logger.warning(f"Error cleaning up SignalConnections: {e}")

            # Phase 2: Clean up view components (they reference other components)
            if (
                hasattr(self.main_window, "page_renderer")
                and self.main_window.page_renderer
            ):
                try:
                    self.main_window.page_renderer.cleanup()
                    logger.debug("PageRenderer cleaned up")
                except Exception as e:
                    logger.warning(f"Error cleaning up PageRenderer: {e}")

            if (
                hasattr(self.main_window, "graphics_view")
                and self.main_window.graphics_view
            ):
                try:
                    self.main_window.graphics_view.cleanup()
                    logger.debug("GraphicsView cleaned up")
                except Exception as e:
                    logger.warning(f"Error cleaning up GraphicsView: {e}")

            # Phase 3: Clear the graphics scene
            if (
                hasattr(self.main_window, "graphics_scene")
                and self.main_window.graphics_scene
            ):
                try:
                    self.main_window.graphics_scene.clear()
                    logger.debug("Graphics scene cleared")
                except Exception as e:
                    logger.warning(f"Error clearing graphics scene: {e}")

            # Phase 4: Clean up PDF document
            if (
                hasattr(self.main_window, "pdf_document")
                and self.main_window.pdf_document
            ):
                try:
                    # Actually close the PDF document to release file handles
                    self.main_window.pdf_document.close()
                    logger.debug("PDF document closed and cleaned up")
                except Exception as e:
                    logger.warning(f"Error cleaning up PDF document: {e}")

            # Phase 5: Clean up presenters (they have their own cleanup)
            for presenter_name in [
                "document_presenter",
                "margin_presenter",
                "navigation_presenter",
            ]:
                if hasattr(self.main_window, presenter_name):
                    presenter = getattr(self.main_window, presenter_name)
                    if presenter and hasattr(presenter, "cleanup"):
                        try:
                            presenter.cleanup()
                            logger.debug(f"{presenter_name} cleaned up")
                        except Exception as e:
                            logger.warning(f"Error cleaning up {presenter_name}: {e}")

            self.main_window._resources_initialized = False
            logger.info("Resource cleanup completed successfully")

        except Exception as e:
            logger.error(
                f"Unexpected error during resource cleanup: {e}", exc_info=True
            )

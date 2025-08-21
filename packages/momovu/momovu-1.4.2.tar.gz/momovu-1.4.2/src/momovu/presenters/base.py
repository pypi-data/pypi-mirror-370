"""Base presenter class for MVP architecture.

This module provides the foundation for all presenters.
Presenters handle business logic and coordinate between models and views.
"""

from typing import Any, Optional, Protocol


class IView(Protocol):
    """Interface that all views must implement for presenter interaction."""

    def update_display(self, **kwargs: Any) -> None:
        """Receive property updates from presenter.

        Args:
            **kwargs: Changed properties as key-value pairs
        """
        ...


class BasePresenter:
    """Base class for all presenters in the MVP architecture.

    This class provides:
    - View reference management
    - Model coordination
    - Common presenter functionality
    """

    def __init__(self, view: Optional[IView] = None) -> None:
        """Initialize the base presenter.

        Args:
            view: Optional view to attach to this presenter
        """
        self._view = view

    @property
    def view(self) -> Optional[IView]:
        """Access the currently attached view instance."""
        return self._view

    @property
    def has_view(self) -> bool:
        """Check if presenter has an active view connection."""
        return self._view is not None

    def update_view(self, **kwargs: Any) -> None:
        """Push property changes to attached view if present.

        Args:
            **kwargs: Property updates to send
        """
        if self._view:
            self._view.update_display(**kwargs)

    def cleanup(self) -> None:  # noqa: B027
        """Release resources and remove model observers.

        Subclasses override to disconnect from models and clear state.
        """

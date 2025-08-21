"""Base model class with property change notification support.

This module provides the foundation for all models in the MVP architecture.
It implements property change notifications without Qt dependencies.
"""

import threading
from typing import Any, Callable


class PropertyChangedEvent:
    """Event fired when a model property changes."""

    def __init__(self, property_name: str, old_value: Any, new_value: Any) -> None:
        """Initialize a property changed event.

        Args:
            property_name: Name of the property that changed
            old_value: Previous value of the property
            new_value: New value of the property
        """
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return (
            f"PropertyChangedEvent(property_name={self.property_name!r}, "
            f"old_value={self.old_value!r}, new_value={self.new_value!r})"
        )


class BaseModel:
    """Base class for all models with property change notification.

    This class provides:
    - Property change notification mechanism
    - Property validation framework
    - Observer pattern implementation (no Qt dependencies)
    """

    def __init__(self) -> None:
        """Initialize the base model with empty observers and properties."""
        self._observers: list[Callable[[PropertyChangedEvent], None]] = []
        self._properties: dict[str, Any] = {}
        self._validators: dict[str, Callable[[Any], bool]] = {}
        self._is_batch_updating = False
        self._pending_events: list[PropertyChangedEvent] = []
        self._observer_lock = threading.RLock()  # Reentrant lock for thread safety

    def add_observer(self, observer: Callable[[PropertyChangedEvent], None]) -> None:
        """Add an observer for property changes.

        Args:
            observer: Callback function to be called on property changes
        """
        with self._observer_lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def remove_observer(self, observer: Callable[[PropertyChangedEvent], None]) -> None:
        """Remove an observer from the notification list.

        Args:
            observer: Callback function to remove (no-op if not registered)
        """
        with self._observer_lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def _notify_observers(self, event: PropertyChangedEvent) -> None:
        """Notify all observers of a property change.

        Args:
            event: The property changed event
        """
        if self._is_batch_updating:
            self._pending_events.append(event)
        else:
            # Create a copy of observers while holding the lock
            with self._observer_lock:
                observers_copy = self._observers.copy()

            # Notify observers without holding the lock to avoid deadlocks
            for observer in observers_copy:
                try:
                    observer(event)
                except Exception as e:
                    # Log but don't crash on observer errors
                    from momovu.lib.logger import get_logger

                    logger = get_logger(__name__)
                    logger.error(f"Observer error: {e}")

    def set_property(self, name: str, value: Any, validate: bool = True) -> bool:
        """Set a property value with optional validation.

        Args:
            name: Property name
            value: New value
            validate: Whether to validate the value

        Returns:
            True if the property was set, False if validation failed
        """
        old_value = self._properties.get(name)
        if old_value == value:
            return True  # No change needed

        if validate and name in self._validators and not self._validators[name](value):
            return False

        self._properties[name] = value
        event = PropertyChangedEvent(name, old_value, value)
        self._notify_observers(event)
        return True

    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property value.

        Args:
            name: Property name
            default: Default value if property doesn't exist

        Returns:
            The property value or default
        """
        return self._properties.get(name, default)

    def add_validator(
        self, property_name: str, validator: Callable[[Any], bool]
    ) -> None:
        """Add a validator for a property.

        Args:
            property_name: Name of the property to validate
            validator: Function that returns True if value is valid
        """
        self._validators[property_name] = validator

    def begin_batch_update(self) -> None:
        """Start batching property changes to reduce notification overhead."""
        self._is_batch_updating = True
        self._pending_events.clear()

    def end_batch_update(self) -> None:
        """Flush all pending property change notifications at once."""
        self._is_batch_updating = False

        # Create a copy of observers while holding the lock
        with self._observer_lock:
            observers_copy = self._observers.copy()

        # Notify observers without holding the lock
        for event in self._pending_events:
            for observer in observers_copy:
                try:
                    observer(event)
                except Exception as e:
                    from momovu.lib.logger import get_logger

                    logger = get_logger(__name__)
                    logger.error(f"Observer error during batch: {e}")
        self._pending_events.clear()

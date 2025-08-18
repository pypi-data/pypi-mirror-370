"""Configuration model for MVP architecture."""

import re
from typing import Any

from momovu.models.base import BaseModel


class ConfigurationModel(BaseModel):
    """Model for configuration data following MVP pattern."""

    def __init__(self) -> None:
        """Initialize configuration model with validators and defaults."""
        super().__init__()
        self._setup_validators()
        self._load_defaults()

    def _setup_validators(self) -> None:
        """Set up value validators."""
        # Color validation
        self.add_validator("color", lambda x: self._validate_color(x))
        # Opacity validation (0.0-1.0)
        self.add_validator(
            "opacity", lambda x: isinstance(x, (int, float)) and 0.0 <= x <= 1.0
        )
        # Line width validation (positive integers)
        self.add_validator("line_width", lambda x: isinstance(x, int) and x > 0)
        # Zoom level validation
        self.add_validator(
            "zoom_level", lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 10.0
        )
        # Boolean validation
        self.add_validator("boolean", lambda x: isinstance(x, bool))

    def _validate_color(self, color: Any) -> bool:
        """Validate color format (#RRGGBB).

        Args:
            color: Color string to validate

        Returns:
            True if valid color format
        """
        if not isinstance(color, str):
            return False
        return bool(re.match(r"^#[0-9A-Fa-f]{6}$", color))

    def _load_defaults(self) -> None:
        """Load default configuration values."""
        # Default colors
        self.set_property(
            "colors",
            {
                "margin_overlay": {"color": "#7F7FC1", "opacity": 0.3},
                "barcode_area": {"color": "#FFFF00", "opacity": 0.5},
                "fold_lines": {"color": "#A41CAD", "opacity": 1.0},
                "trim_lines": {"color": "#000000", "opacity": 1.0},
                "bleed_lines": {"color": "#22B5F0", "opacity": 1.0},
            },
            validate=False,
        )

        # Default line widths
        self.set_property(
            "line_widths",
            {
                "fold_lines": 2,
                "trim_lines": 1,
                "bleed_lines": 1,
            },
            validate=False,
        )

        # Default preferences
        self.set_property(
            "preferences",
            {
                "auto_fit_on_load": True,
                "auto_fit_on_resize": False,
                "remember_zoom_per_document": True,
                "smooth_scrolling": True,
                "scroll_speed": 50,
                "zoom_increment": 1.1,
                "cache_max_pages": 20,
                "cache_max_memory_mb": 300,
                "high_contrast_mode": False,
            },
            validate=False,
        )

        # Default document settings
        self.set_property(
            "document_defaults",
            {
                "interior": {
                    "show_margins": True,
                    "show_trim_lines": True,
                    "show_barcode": False,
                    "show_fold_lines": False,
                    "show_bleed_lines": False,
                },
                "cover": {
                    "show_margins": True,
                    "show_trim_lines": True,
                    "show_barcode": True,
                    "show_fold_lines": True,
                    "show_bleed_lines": True,
                    "default_num_pages": 100,
                },
                "dustjacket": {
                    "show_margins": True,
                    "show_trim_lines": True,
                    "show_barcode": True,
                    "show_fold_lines": True,
                    "show_bleed_lines": True,
                    "default_num_pages": 100,
                },
            },
            validate=False,
        )

    def get_defaults(self) -> dict[str, Any]:
        """Get default configuration values.

        Returns:
            Dictionary of all default values
        """
        return {
            "colors": self.get_property("colors"),
            "line_widths": self.get_property("line_widths"),
            "preferences": self.get_property("preferences"),
            "document_defaults": self.get_property("document_defaults"),
        }

    def get_color(self, overlay_type: str) -> dict[str, Any]:
        """Get color configuration for an overlay type.

        Args:
            overlay_type: Type of overlay (margin_overlay, barcode_area, etc.)

        Returns:
            Dictionary with color and opacity
        """
        colors = dict(self.get_property("colors", {}))
        return dict(colors.get(overlay_type, {"color": "#000000", "opacity": 1.0}))

    def set_color(self, overlay_type: str, color: str, opacity: float) -> None:
        """Set color configuration for an overlay type.

        Args:
            overlay_type: Type of overlay
            color: Color in #RRGGBB format
            opacity: Opacity value (0.0-1.0)
        """
        if not self._validate_color(color):
            raise ValueError(f"Invalid color format: {color}")
        if not (0.0 <= opacity <= 1.0):
            raise ValueError(f"Invalid opacity value: {opacity}")

        colors = self.get_property("colors", {})
        colors[overlay_type] = {"color": color, "opacity": opacity}
        self.set_property("colors", colors)

    def get_line_width(self, line_type: str) -> int:
        """Get line width for a line type.

        Args:
            line_type: Type of line (fold_lines, trim_lines, etc.)

        Returns:
            Line width in pixels
        """
        line_widths = dict(self.get_property("line_widths", {}))
        return int(line_widths.get(line_type, 1))

    def set_line_width(self, line_type: str, width: int) -> None:
        """Set line width for a line type.

        Args:
            line_type: Type of line
            width: Width in pixels (must be positive)
        """
        if not isinstance(width, int) or width <= 0:
            raise ValueError(f"Invalid line width: {width}")

        line_widths = self.get_property("line_widths", {})
        line_widths[line_type] = width
        self.set_property("line_widths", line_widths)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value.

        Args:
            key: Preference key
            default: Default value if key doesn't exist

        Returns:
            Preference value or default
        """
        preferences = self.get_property("preferences", {})
        return preferences.get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference value.

        Args:
            key: Preference key
            value: Value to set
        """
        preferences = self.get_property("preferences", {})
        preferences[key] = value
        self.set_property("preferences", preferences)

    def get_document_defaults(self, doc_type: str) -> dict[str, Any]:
        """Get default settings for a document type.

        Args:
            doc_type: Document type (interior, cover, dustjacket)

        Returns:
            Dictionary of default settings
        """
        defaults = dict(self.get_property("document_defaults", {}))
        return dict(defaults.get(doc_type, {}))

    def set_document_defaults(self, doc_type: str, settings: dict[str, Any]) -> None:
        """Set default settings for a document type.

        Args:
            doc_type: Document type
            settings: Dictionary of settings
        """
        defaults = self.get_property("document_defaults", {})
        defaults[doc_type] = settings
        self.set_property("document_defaults", defaults)

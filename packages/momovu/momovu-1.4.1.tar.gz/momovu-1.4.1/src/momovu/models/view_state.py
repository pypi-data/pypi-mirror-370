"""View state model for MVP architecture.

This model handles view state without any UI dependencies.
"""

from typing import cast

from momovu.lib.constants import MAX_ZOOM_LEVEL, MIN_ZOOM_LEVEL
from momovu.models.base import BaseModel


class ViewStateModel(BaseModel):
    """Model for view state data.

    This model stores:
    - Current page/page pair
    - View mode (single/side-by-side)
    - Zoom level
    - Visibility flags

    It does NOT handle:
    - View rendering (that's a view concern)
    - Navigation logic (that's a presenter concern)
    """

    # View mode constants
    VIEW_MODE_SINGLE = "single"
    VIEW_MODE_SIDE_BY_SIDE = "side_by_side"

    def __init__(self) -> None:
        """Initialize view state with default single-page mode and all overlays visible."""
        super().__init__()

        # Define validation rules
        self.add_validator("current_page", lambda x: isinstance(x, int) and x >= 0)
        self.add_validator(
            "view_mode",
            lambda x: x in [self.VIEW_MODE_SINGLE, self.VIEW_MODE_SIDE_BY_SIDE],
        )
        self.add_validator(
            "zoom_level",
            lambda x: isinstance(x, (int, float))
            and MIN_ZOOM_LEVEL <= x <= MAX_ZOOM_LEVEL,
        )
        self.add_validator("show_margins", lambda x: isinstance(x, bool))
        self.add_validator("show_trim_lines", lambda x: isinstance(x, bool))
        self.add_validator("show_spine_line", lambda x: isinstance(x, bool))
        self.add_validator("show_fold_lines", lambda x: isinstance(x, bool))
        self.add_validator("show_barcode", lambda x: isinstance(x, bool))
        self.add_validator("show_gutter", lambda x: isinstance(x, bool))
        self.add_validator("is_fullscreen", lambda x: isinstance(x, bool))
        self.add_validator("is_presentation", lambda x: isinstance(x, bool))

        # Initialize properties with defaults
        self.set_property("current_page", 0, validate=True)
        self.set_property("view_mode", self.VIEW_MODE_SINGLE, validate=True)
        self.set_property("zoom_level", 1.0, validate=True)
        self.set_property("show_margins", True, validate=True)
        self.set_property("show_trim_lines", True, validate=True)
        self.set_property("show_spine_line", True, validate=True)
        self.set_property("show_fold_lines", True, validate=True)
        self.set_property("show_barcode", True, validate=True)
        self.set_property("show_gutter", True, validate=True)
        self.set_property("is_fullscreen", False, validate=True)
        self.set_property("is_presentation", False, validate=True)

    @property
    def current_page(self) -> int:
        """Zero-based index of the currently displayed page."""
        return cast("int", self.get_property("current_page", 0))

    @current_page.setter
    def current_page(self, value: int) -> None:
        """Update the current page index."""
        self.set_property("current_page", value)

    @property
    def view_mode(self) -> str:
        """Current viewing mode: 'single' or 'side_by_side'."""
        return cast("str", self.get_property("view_mode", self.VIEW_MODE_SINGLE))

    @view_mode.setter
    def view_mode(self, value: str) -> None:
        """Switch between single page and side-by-side viewing."""
        self.set_property("view_mode", value)

    @property
    def zoom_level(self) -> float:
        """Current zoom factor where 1.0 = 100%, 2.0 = 200%, etc."""
        return cast("float", self.get_property("zoom_level", 1.0))

    @zoom_level.setter
    def zoom_level(self, value: float) -> None:
        """Update zoom level (clamped to 0.1-10.0 range)."""
        self.set_property("zoom_level", value)

    @property
    def show_margins(self) -> bool:
        """Get show margins flag."""
        return cast("bool", self.get_property("show_margins", True))

    @show_margins.setter
    def show_margins(self, value: bool) -> None:
        """Set show margins flag."""
        self.set_property("show_margins", value)

    @property
    def show_trim_lines(self) -> bool:
        """Get show trim lines flag."""
        return cast("bool", self.get_property("show_trim_lines", True))

    @show_trim_lines.setter
    def show_trim_lines(self, value: bool) -> None:
        """Set show trim lines flag."""
        self.set_property("show_trim_lines", value)

    @property
    def show_spine_line(self) -> bool:
        """Get show spine line flag."""
        return cast("bool", self.get_property("show_spine_line", True))

    @show_spine_line.setter
    def show_spine_line(self, value: bool) -> None:
        """Set show spine line flag."""
        self.set_property("show_spine_line", value)

    @property
    def show_fold_lines(self) -> bool:
        """Get show fold lines flag."""
        return cast("bool", self.get_property("show_fold_lines", True))

    @show_fold_lines.setter
    def show_fold_lines(self, value: bool) -> None:
        """Set show fold lines flag."""
        self.set_property("show_fold_lines", value)

    @property
    def show_barcode(self) -> bool:
        """Get show barcode flag."""
        return cast("bool", self.get_property("show_barcode", True))

    @show_barcode.setter
    def show_barcode(self, value: bool) -> None:
        """Set show barcode flag."""
        self.set_property("show_barcode", value)

    @property
    def show_gutter(self) -> bool:
        """Get show gutter flag."""
        return cast("bool", self.get_property("show_gutter", True))

    @show_gutter.setter
    def show_gutter(self, value: bool) -> None:
        """Set show gutter flag."""
        self.set_property("show_gutter", value)

    @property
    def is_fullscreen(self) -> bool:
        """Get fullscreen state."""
        return cast("bool", self.get_property("is_fullscreen", False))

    @is_fullscreen.setter
    def is_fullscreen(self, value: bool) -> None:
        """Set fullscreen state."""
        self.set_property("is_fullscreen", value)

    @property
    def is_presentation(self) -> bool:
        """Get presentation mode state."""
        return cast("bool", self.get_property("is_presentation", False))

    @is_presentation.setter
    def is_presentation(self, value: bool) -> None:
        """Set presentation mode state."""
        self.set_property("is_presentation", value)

    def is_single_page_mode(self) -> bool:
        """True if displaying one page at a time."""
        return self.view_mode == self.VIEW_MODE_SINGLE

    def is_side_by_side_mode(self) -> bool:
        """True if displaying page pairs side-by-side."""
        return self.view_mode == self.VIEW_MODE_SIDE_BY_SIDE

    def toggle_view_mode(self) -> None:
        """Switch between single page and side-by-side page pair display."""
        if self.is_single_page_mode():
            self.view_mode = self.VIEW_MODE_SIDE_BY_SIDE
        else:
            self.view_mode = self.VIEW_MODE_SINGLE

    def __repr__(self) -> str:
        """Developer-friendly string representation of view state."""
        return (
            f"ViewStateModel(current_page={self.current_page}, "
            f"view_mode={self.view_mode!r}, zoom_level={self.zoom_level})"
        )

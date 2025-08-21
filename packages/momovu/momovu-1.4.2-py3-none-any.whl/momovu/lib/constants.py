"""Constants used throughout the Momovu application.

This module defines all the constants used in the Momovu application including:
- Window dimensions and UI elements
- Presentation settings
- Measurement conversions (points, mm, inches)
- Cache and performance settings
- Zoom factors
- Default margins and safety areas
- Barcode dimensions for covers
- Spine and flap calculations
- Graphics item colors and styles
- Z-order layering values
"""

from typing import Final

from PySide6.QtGui import QColor

# Window dimensions
DEFAULT_WINDOW_WIDTH: Final[int] = 1024
DEFAULT_WINDOW_HEIGHT: Final[int] = 768
MIN_WINDOW_WIDTH: Final[int] = 800
MIN_WINDOW_HEIGHT: Final[int] = 600

# UI elements

# Dialog dimensions
SHORTCUTS_DIALOG_WIDTH: Final[int] = 600
SHORTCUTS_DIALOG_HEIGHT: Final[int] = 500
ABOUT_DIALOG_MIN_WIDTH: Final[int] = 500

# Table settings
SHORTCUTS_TABLE_COLUMNS: Final[int] = 3

# Spinbox limits
PAGE_SPINBOX_MIN: Final[int] = 1
PAGE_SPINBOX_MAX: Final[int] = 10000
DEFAULT_PAGE_COUNT: Final[int] = 100

# Scrolling
DEFAULT_SCROLL_AMOUNT: Final[int] = 50  # Pixels for manual scrolling

# Font sizes
TITLE_FONT_SIZE: Final[int] = 16
VERSION_FONT_SIZE: Final[int] = 10

# Presentation settings
Y_OFFSET_SPACING: Final[int] = 50  # points

# Measurement conversions
POINTS_PER_INCH: Final[float] = 72.0
MM_PER_INCH: Final[float] = 25.4

# Zoom factors
# Smaller zoom increments for smoother zoom experience
ZOOM_IN_FACTOR: Final[float] = 1.1  # 10% increase - smoother zoom steps
ZOOM_OUT_FACTOR: Final[float] = 1.0 / ZOOM_IN_FACTOR  # Exact inverse for symmetric zoom

# Default margins
DEFAULT_SAFETY_MARGIN_MM: Final[float] = 12.7  # 0.5 inches

# ISBN barcode dimensions (EAN-13 with 5-digit price addon)
BARCODE_WIDTH: Final[float] = 92.075  # mm (3.625 inches)
BARCODE_HEIGHT: Final[float] = 31.75  # mm (1.25 inches)

# Spine width calculation constants
# Formula from Lulu's Book Creation Guide for calculating spine width:
# spine_width_mm = (page_count / 17.48) + 1.524
# This accounts for standard paper thickness and perfect binding requirements
SPINE_WIDTH_DIVISOR: Final[float] = 17.48  # Lulu's divisor for page count
SPINE_WIDTH_OFFSET: Final[float] = 1.524  # Lulu's base spine width in mm

# Minimum page requirements
MINIMUM_COVER_PAGES: Final[int] = (
    32  # Minimum pages for paperback covers per Lulu requirements
)

# Dustjacket flap dimensions
# Standard US Trade (6" x 9") dustjacket flap measurements
DUSTJACKET_FLAP_WIDTH: Final[float] = 82.55  # mm (3.25 inches) - standard flap width
DUSTJACKET_FLAP_HEIGHT: Final[float] = 228.6  # mm (9 inches) - matches book height

# Fold safety margin
DUSTJACKET_FOLD_SAFETY_MARGIN: Final[float] = 6.35  # mm

# Bleed areas for different document types
DUSTJACKET_BLEED: Final[float] = 6.35  # mm (0.25 inches) - bleed area for dustjackets
COVER_BLEED: Final[float] = (
    3.175  # mm (0.125 inches) - bleed area for covers (half of dustjacket bleed)
)

# Line widths
FOLD_LINE_PEN_WIDTH: Final[int] = 2  # pixels - width for fold/spine line indicators
TRIM_LINE_PEN_WIDTH: Final[int] = 1  # pixels - width for trim mark lines
BLEED_LINE_PEN_WIDTH: Final[int] = 1  # pixels - width for bleed line marks
GUTTER_LINE_PEN_WIDTH: Final[int] = 1  # pixels - width for gutter line indicators

# Gutter size thresholds based on page count (in mm)
# The gutter extends the safety margin toward the spine
# Note: These values are per page (half of the total gutter for both pages)
GUTTER_SIZE_THRESHOLDS: Final[list[tuple[int, float]]] = [
    (60, 0.0),  # Less than 60 pages: 0 mm
    (150, 1.5875),  # 61 to 150 pages: 0.125 in / 2 ; 1.5875 mm
    (400, 6.35),  # 151 to 400 pages: 0.5 in / 2 ; 6.35 mm
    (600, 7.9375),  # 401 to 600 pages: 0.625 in / 2 ; 7.9375 mm
    (9999, 9.525),  # Over 601 pages: 0.75 in / 2 ; 9.525 mm
]

# UI transition delays (milliseconds)
IMMEDIATE_DELAY: Final[int] = 0  # Next event loop
STANDARD_TRANSITION_DELAY: Final[int] = 100  # Normal UI updates
COMPLETE_TRANSITION_DELAY: Final[int] = 200  # Full transition completion

# Specific operation delays
PRESENTATION_ENTER_DELAY: Final[int] = 50
PRESENTATION_EXIT_DELAY: Final[int] = 50
FIT_TO_PAGE_DELAY: Final[int] = 100

# Exit codes
# Following Unix/POSIX conventions for process exit status
EXIT_CODE_SUCCESS: Final[int] = 0  # Normal termination
EXIT_CODE_WINDOW_ERROR: Final[int] = 2  # Window creation errors
EXIT_CODE_APP_ERROR: Final[int] = 3  # Application initialization errors
EXIT_CODE_UNEXPECTED: Final[int] = 4  # Unexpected errors
EXIT_CODE_SIGINT: Final[int] = (
    130  # Standard Unix exit code for SIGINT (128 + signal 2)
)

# UI Zoom limits (separate from render scale)
MIN_ZOOM_LEVEL: Final[float] = 0.1  # Minimum UI zoom (10%)
MAX_ZOOM_LEVEL: Final[float] = 10.0  # Maximum UI zoom (1000%)

# Zoom thresholds
ZOOM_THRESHOLD_FOR_PAN: Final[float] = (
    1.05  # Zoom level above which arrow keys pan instead of navigate
)

# Conversion factors
POINTS_PER_MM: Final[float] = POINTS_PER_INCH / MM_PER_INCH  # 2.834645669...
MM_TO_POINTS: Final[float] = POINTS_PER_MM  # Alias for conversion factor

# Viewport fit margin for page fitting
VIEWPORT_FIT_MARGIN: Final[int] = 10  # Margin in pixels when fitting page to viewport

# Scene fitting constants
SCENE_FIT_HEIGHT_OFFSET: Final[int] = 100  # Pixels above/below center for scene fitting
SCENE_FIT_HEIGHT: Final[int] = 200  # Total height for scene fitting rectangle

# Spine and flap calculation ratios
FLAP_WIDTH_RATIO: Final[float] = DUSTJACKET_FLAP_WIDTH  # Flap width in mm
FLAP_HEIGHT_RATIO: Final[float] = DUSTJACKET_FLAP_HEIGHT  # Flap height in mm

# Additional graphics colors
FOLD_LINE_COLOR: Final[QColor] = QColor(
    164, 28, 173
)  # Purple for fold line indicators (spine, flap, etc.)
MARGIN_OVERLAY_COLOR: Final[QColor] = QColor(127, 127, 193)  # Blue for margin overlays
BARCODE_AREA_COLOR: Final[QColor] = QColor(255, 255, 0)  # Yellow for barcode areas
TRIM_LINE_COLOR: Final[QColor] = QColor(0, 0, 0, 255)  # Black for trim line marks
BLEED_LINE_COLOR: Final[QColor] = QColor(
    34, 181, 240
)  # Light blue (#22b5f0) for bleed lines
GUTTER_COLOR: Final[QColor] = QColor(121, 193, 150)  # #79c196 for gutter margins

# Opacity constants
BARCODE_RECT_OPACITY: Final[float] = 0.5
MARGIN_RECT_OPACITY: Final[float] = 0.3

# Zoom rendering constants
# Quality threshold - below this uses full-page rendering for best quality
ZOOM_QUALITY_THRESHOLD: Final[float] = 10.0  # 10x zoom

# Safe fallback scale when rendering fails
ZOOM_SAFE_FALLBACK_SCALE: Final[float] = 4.0  # 4x zoom

# Scene padding for edge zoom operations
ZOOM_SCENE_PADDING: Final[int] = 5000  # pixels

# Buffer factor for rendering extra area around visible region
ZOOM_BUFFER_FACTOR: Final[float] = 0.5  # 50% extra

# Buffer reduction at high zoom (formula: min(reduction_max, buffer_factor / (scale / threshold)))
ZOOM_BUFFER_REDUCTION_MAX: Final[float] = 0.2  # 20% max buffer at high zoom
ZOOM_BUFFER_REDUCTION_THRESHOLD: Final[float] = 10.0  # Start reducing after 10x

# Memory limits for rendering
ZOOM_MAX_RENDER_PIXELS: Final[int] = 200_000_000  # 200 megapixels
ZOOM_MAX_DIMENSION: Final[int] = 30000  # 30k pixels per dimension

# Progressive rendering delay
ZOOM_PROGRESSIVE_RENDER_DELAY: Final[int] = 150  # milliseconds

# Maximum useful render scale (beyond this, no visual improvement)
ZOOM_MAX_USEFUL_SCALE: Final[float] = 100.0  # 100x zoom

# Cache settings
ZOOM_CACHE_MAX_ENTRIES: Final[int] = 20  # Number of cached regions
ZOOM_CACHE_MAX_MEMORY_MB: Final[int] = 300  # MB of cache memory

# Zoom level snapping for better cache hits
ZOOM_CACHE_LEVELS: Final[list[float]] = [
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    5.0,
    8.0,
    10.0,
    15.0,
    20.0,
    30.0,
    50.0,
    75.0,
    100.0,
    150.0,
    200.0,
]

# Active zoom detection threshold
ZOOM_ACTIVE_THRESHOLD: Final[float] = (
    0.1  # seconds - time between paints to detect active zooming
)

"""Custom Hypothesis strategies for Momovu types.

This module provides reusable strategies for generating test data
that matches the domain model of the Momovu application.
"""

import hypothesis.strategies as st

# Document-related strategies

# Page dimensions strategy (in points)
# Standard page sizes range from small (A6) to large (A0)
page_dimensions = st.tuples(
    st.floats(
        min_value=72.0, max_value=7200.0, allow_nan=False, allow_infinity=False
    ),  # Width: 1-100 inches
    st.floats(
        min_value=72.0, max_value=7200.0, allow_nan=False, allow_infinity=False
    ),  # Height: 1-100 inches
)

# Common paper sizes in points
common_page_sizes = st.sampled_from(
    [
        (612.0, 792.0),  # Letter (8.5 x 11 inches)
        (595.0, 842.0),  # A4
        (420.0, 595.0),  # A5
        (297.0, 420.0),  # A6
        (842.0, 1191.0),  # A3
        (1191.0, 1684.0),  # A2
    ]
)

# Document type strategy
document_types = st.sampled_from(["interior", "cover", "dustjacket"])


# Valid file paths for PDFs
@st.composite
def pdf_file_paths(draw):
    """Generate valid PDF file paths."""
    # Generate safe filename characters
    name = draw(
        st.text(
            alphabet=st.characters(
                whitelist_categories=["Ll", "Lu", "Nd"],  # Letters and digits
                whitelist_characters="-_",
            ),
            min_size=1,
            max_size=50,
        )
    )
    # Optionally add directory structure
    depth = draw(st.integers(min_value=0, max_value=3))
    path_parts = []
    for _ in range(depth):
        dir_name = draw(
            st.text(
                alphabet=st.characters(
                    whitelist_categories=["Ll", "Lu"], whitelist_characters="-_"
                ),
                min_size=1,
                max_size=20,
            )
        )
        path_parts.append(dir_name)
    path_parts.append(f"{name}.pdf")
    return "/".join(path_parts)


# Page count strategies
small_page_counts = st.integers(min_value=1, max_value=50)
medium_page_counts = st.integers(min_value=50, max_value=500)
large_page_counts = st.integers(min_value=500, max_value=5000)
any_page_count = st.integers(min_value=1, max_value=10000)


# Page ranges for navigation
@st.composite
def page_ranges(draw, max_pages=1000):
    """Generate valid (current_page, total_pages) tuples."""
    total = draw(st.integers(min_value=1, max_value=max_pages))
    current = draw(st.integers(min_value=0, max_value=total - 1))
    return current, total


# Margin-related strategies

# Margin sizes in millimeters
margin_sizes_mm = st.floats(
    min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
)

# Margin sizes in points
margin_sizes_points = st.floats(
    min_value=0.0, max_value=288.0, allow_nan=False, allow_infinity=False  # 4 inches
)

# Spine width strategy (can be None for interior documents)
spine_widths = st.one_of(
    st.none(),
    st.floats(min_value=0.0, max_value=200.0, allow_nan=False, allow_infinity=False),
)

# Flap dimensions
flap_widths = st.one_of(
    st.none(),
    st.floats(min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False),
)

flap_heights = st.one_of(
    st.none(),
    st.floats(min_value=100.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
)


# Complete margin settings
@st.composite
def margin_settings(draw, document_type=None):
    """Generate valid margin settings for a given document type."""
    doc_type = document_type or draw(document_types)

    settings = {
        "document_type": doc_type,
        "num_pages": draw(st.integers(min_value=1, max_value=5000)),
        "safety_margin_mm": draw(margin_sizes_mm),
        "safety_margin_points": draw(margin_sizes_points),
        "show_margins": draw(st.booleans()),
        "show_trim_lines": draw(st.booleans()),
        "show_barcode": draw(st.booleans()),
        "show_fold_lines": draw(st.booleans()),
    }

    # Add spine width for covers and dustjackets
    if doc_type in ["cover", "dustjacket"]:
        settings["spine_width"] = draw(st.floats(min_value=0.1, max_value=100.0))
    else:
        settings["spine_width"] = None

    # Add flap dimensions for dustjackets
    if doc_type == "dustjacket":
        settings["flap_width"] = draw(st.floats(min_value=50.0, max_value=200.0))
        settings["flap_height"] = draw(st.floats(min_value=100.0, max_value=500.0))
    else:
        settings["flap_width"] = None
        settings["flap_height"] = None

    return settings


# View state strategies

# View modes
view_modes = st.sampled_from(["single", "side_by_side"])

# Zoom levels
zoom_levels = st.floats(
    min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False
)

# Reasonable zoom levels for UI testing
reasonable_zoom_levels = st.sampled_from(
    [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
)


# Complete view state
@st.composite
def view_states(draw, total_pages=None):
    """Generate valid view states."""
    if total_pages is None:
        total_pages = draw(st.integers(min_value=1, max_value=1000))

    return {
        "current_page": draw(
            st.integers(min_value=0, max_value=max(0, total_pages - 1))
        ),
        "view_mode": draw(view_modes),
        "zoom_level": draw(zoom_levels),
        "show_margins": draw(st.booleans()),
        "show_trim_lines": draw(st.booleans()),
        "show_spine_line": draw(st.booleans()),
        "show_fold_lines": draw(st.booleans()),
        "show_barcode": draw(st.booleans()),
        "is_fullscreen": draw(st.booleans()),
        "is_presentation": draw(st.booleans()),
    }


# Qt-specific strategies


# QRectF-like rectangles
@st.composite
def qrect_like(draw, max_size=5000.0):
    """Generate QRectF-compatible rectangle data."""
    x = draw(st.floats(min_value=-max_size, max_value=max_size, allow_nan=False))
    y = draw(st.floats(min_value=-max_size, max_value=max_size, allow_nan=False))
    width = draw(st.floats(min_value=0.1, max_value=max_size, allow_nan=False))
    height = draw(st.floats(min_value=0.1, max_value=max_size, allow_nan=False))
    return (x, y, width, height)


# QPointF-like points
@st.composite
def qpoint_like(draw, max_coord=5000.0):
    """Generate QPointF-compatible point data."""
    x = draw(st.floats(min_value=-max_coord, max_value=max_coord, allow_nan=False))
    y = draw(st.floats(min_value=-max_coord, max_value=max_coord, allow_nan=False))
    return (x, y)


# Document loading scenarios
@st.composite
def document_load_scenario(draw):
    """Generate a complete document loading scenario."""
    file_path = draw(pdf_file_paths())
    page_count = draw(any_page_count)

    # Generate page sizes - either all the same or varied
    if draw(st.booleans()):
        # All pages same size
        size = draw(common_page_sizes)
        page_sizes = [size] * page_count
    else:
        # Mixed page sizes
        page_sizes = [draw(common_page_sizes) for _ in range(page_count)]

    return {
        "file_path": file_path,
        "page_count": page_count,
        "page_sizes": page_sizes,
    }


# Navigation scenarios
@st.composite
def navigation_scenario(draw, total_pages):
    """Generate navigation test scenarios."""
    action = draw(st.sampled_from(["next", "previous", "first", "last", "goto"]))

    if action == "goto":
        target_page = draw(st.integers(min_value=0, max_value=total_pages - 1))
        return {"action": action, "target": target_page}
    else:
        return {"action": action}


# Rendering scenarios
@st.composite
def rendering_scenario(draw):
    """Generate rendering test scenarios."""
    return {
        "document_type": draw(document_types),
        "page_count": draw(small_page_counts),
        "view_mode": draw(view_modes),
        "zoom_level": draw(reasonable_zoom_levels),
        "show_overlays": draw(st.booleans()),
        "presentation_mode": draw(st.booleans()),
    }


# State transition scenarios
@st.composite
def state_transition(draw):
    """Generate valid state transitions for testing."""
    transitions = [
        ("toggle_fullscreen", {}),
        ("toggle_presentation", {}),
        ("toggle_view_mode", {}),
        ("zoom_in", {}),
        ("zoom_out", {}),
        ("fit_to_page", {}),
        ("toggle_margins", {}),
        ("toggle_trim_lines", {}),
        ("set_document_type", {"type": draw(document_types)}),
        (
            "navigate",
            {"direction": draw(st.sampled_from(["next", "previous", "first", "last"]))},
        ),
    ]

    return draw(st.sampled_from(transitions))


# Batch operation scenarios
@st.composite
def batch_property_updates(draw):
    """Generate batch property update scenarios."""
    num_updates = draw(st.integers(min_value=1, max_value=10))
    updates = {}

    possible_properties = [
        ("safety_margin_mm", margin_sizes_mm),
        ("num_pages", any_page_count),
        ("show_margins", st.booleans()),
        ("show_trim_lines", st.booleans()),
        ("spine_width", spine_widths),
    ]

    selected = draw(
        st.lists(
            st.sampled_from(possible_properties),
            min_size=num_updates,
            max_size=num_updates,
            unique_by=lambda x: x[0],
        )
    )

    for prop_name, strategy in selected:
        updates[prop_name] = draw(strategy)

    return updates

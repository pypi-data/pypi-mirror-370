import sys
from pathlib import Path
from typing import Any

import sphinx.util.logging

# Add the src directory to the path for autodoc
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

logger = sphinx.util.logging.getLogger(__name__)

# Dynamically read version from _version.py
try:
    from momovu._version import __version__

    version = __version__.split("+")[0]  # Get base version without git info
    release = f"v{__version__}"
except ImportError:
    # Fallback version if _version.py doesn't exist
    version = "0.3.0"
    release = "v0.3.0"

# Project information
project = "Momovu"
copyright = "2025, Jeff Moe"
author = "Jeff Moe"

# Extensions
extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
]

# Configuration for autodoc
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyside6": ("https://doc.qt.io/qtforpython-6/", None),
}

# General configuration
templates_path = ["_templates"]
exclude_patterns: list[str] = []
source_suffix = ".rst"
master_doc = "index"
pygments_style = "sphinx"
python_display_short_literal_types = True
todo_include_todos = True
add_module_names = False

# HTML output options
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "style_nav_header_background": "#4fb31f",
    "prev_next_buttons_location": "bottom",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    "logo_only": False,
}

html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_logo = "_static/logo.png"
html_last_updated_fmt = None
html_show_sphinx = False
html_show_sourcelink = False  # Disable "View page source" link
html_show_copyright = False  # Disable copyright in footer
html_link_suffix = ".html"
html_use_index = True
html_split_index = False
html_copy_source = True

# Custom CSS
html_css_files = [
    "custom.css",
]

# HTML context for additional template variables
html_context = {
    "display_lower_left": True,
}

# Internationalization
locale_dirs = ["locale/"]
gettext_compact = False
language = "en"
html_search_language = "en"

# LaTeX output options
latex_engine = "xelatex"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "extraclassoptions": "openany,oneside",
    "sphinxsetup": "hmargin={1in,1in}, vmargin={1in,1in}",
    "inputenc": "",
    "utf8extra": "",
    "preamble": r"""
\usepackage{xcolor}
\usepackage{polyglossia}
\setdefaultlanguage{english}
\usepackage{fontspec}
\setmainfont{DejaVu Sans}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
    """,
}

latex_documents = [
    (master_doc, "Momovu.tex", "Momovu Documentation", "Jeff Moe", "manual"),
]

# Man page output
man_pages = [(master_doc, "momovu", "Momovu Documentation", [author], 1)]

# Texinfo output
texinfo_documents = [
    (
        master_doc,
        "Momovu",
        "Momovu Documentation",
        author,
        "Momovu",
        "Preview margins on book PDFs before publication.",
        "Miscellaneous",
    ),
]

# EPUB output
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ["search.html"]

# Extension configuration
# notfound.extension
notfound_urls_prefix = "/en/"
notfound_default_language = "en"
notfound_default_version = ""

# Coverage extension
coverage_show_missing_items = True

# Todo extension
todo_emit_warnings = True

# Suppress specific warnings
suppress_warnings = ["autosummary", "autodoc.import_object"]


# Custom setup function
def setup(app: Any) -> None:
    app.add_css_file("custom.css")
    app.add_config_value(
        "recommonmark_config",
        {
            "auto_toc_tree_section": "Contents",
        },
        True,
    )

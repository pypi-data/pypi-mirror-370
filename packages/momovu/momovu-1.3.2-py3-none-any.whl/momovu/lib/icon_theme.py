"""Icon theme configuration for Qt applications.

This module handles Qt icon theme configuration using Qt's built-in
theme support, including fallback themes and search paths.
"""

import os

from PySide6.QtGui import QIcon

from momovu.lib.logger import get_logger

logger = get_logger(__name__)


def configure_icon_theme() -> None:
    """Configure Qt icon theme with proper fallbacks.

    Uses Qt's built-in theme support:
    1. Ensures standard search paths are available
    2. Sets up fallback theme if main theme is missing icons
    3. Adds fallback search paths for standalone icons
    """
    # Ensure standard icon paths are available
    _ensure_theme_search_paths()

    # Set up fallback theme
    _configure_fallback_theme()

    # Set up fallback search paths for standalone icons
    _configure_fallback_search_paths()

    # Log current configuration
    current_theme = QIcon.themeName()
    fallback_theme = QIcon.fallbackThemeName()
    logger.debug(f"Icon theme: '{current_theme}', fallback: '{fallback_theme}'")

    # Check if we can find icons
    if not QIcon.hasThemeIcon("document-open"):
        logger.warning(
            "Qt cannot find standard icons. Consider installing an icon theme or setting QT_QPA_PLATFORMTHEME"
        )


def _ensure_theme_search_paths() -> None:
    """Ensure Qt knows about standard icon theme directories."""
    search_paths = list(QIcon.themeSearchPaths())
    standard_paths = [
        "/usr/share/icons",
        "/usr/local/share/icons",
        os.path.expanduser("~/.local/share/icons"),
        os.path.expanduser("~/.icons"),
    ]

    # Add XDG_DATA_DIRS paths
    xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    for data_dir in xdg_data_dirs.split(":"):
        if data_dir:
            icon_dir = os.path.join(data_dir, "icons")
            if icon_dir not in standard_paths:
                standard_paths.append(icon_dir)

    added = []
    for path in standard_paths:
        if path not in search_paths and os.path.exists(path):
            search_paths.append(path)
            added.append(path)

    if added:
        QIcon.setThemeSearchPaths(search_paths)
        logger.debug(f"Added theme search paths: {', '.join(added)}")


def _configure_fallback_theme() -> None:
    """Set up a fallback theme if the current theme is insufficient."""
    current_theme = QIcon.themeName()

    # If no theme or only hicolor, try to find a better one
    if not current_theme or current_theme == "hicolor":
        # Check for platform integration
        platform_theme = os.environ.get("QT_QPA_PLATFORMTHEME", "")
        if not platform_theme:
            logger.debug("No QT_QPA_PLATFORMTHEME set")

            # Find and set a usable theme
            installed_themes = _find_installed_themes()
            for theme in ["Adwaita", "breeze", "gnome", "oxygen"]:
                if theme in installed_themes:
                    QIcon.setThemeName(theme)
                    logger.info(f"Set icon theme to '{theme}'")
                    break

    # Always set a fallback theme
    if not QIcon.fallbackThemeName():
        # Find a different theme as fallback
        current = QIcon.themeName()
        fallback_order = ["Adwaita", "breeze", "gnome", "oxygen", "hicolor"]

        for theme in fallback_order:
            if theme != current and _theme_exists(theme):
                QIcon.setFallbackThemeName(theme)
                logger.debug(f"Set fallback theme to '{theme}'")
                break


def _configure_fallback_search_paths() -> None:
    """Set up fallback search paths for standalone icon files."""
    fallback_paths = QIcon.fallbackSearchPaths()

    # Add paths that might contain standalone icons
    additional_paths = [
        "/usr/share/pixmaps",
        "/usr/local/share/pixmaps",
        os.path.expanduser("~/.local/share/pixmaps"),
    ]

    added = []
    for path in additional_paths:
        if path not in fallback_paths and os.path.exists(path):
            fallback_paths.append(path)
            added.append(path)

    if added:
        QIcon.setFallbackSearchPaths(fallback_paths)
        logger.debug(f"Added fallback search paths: {', '.join(added)}")


def _find_installed_themes() -> list[str]:
    """Find all installed icon themes.

    Returns:
        List of theme names
    """
    themes = []
    for search_path in QIcon.themeSearchPaths():
        if os.path.exists(search_path):
            try:
                for item in os.listdir(search_path):
                    theme_dir = os.path.join(search_path, item)
                    if os.path.isdir(theme_dir) and os.path.exists(
                        os.path.join(theme_dir, "index.theme")
                    ):
                        themes.append(item)
            except OSError:
                pass  # Skip inaccessible directories
    return list(set(themes))  # Remove duplicates


def _theme_exists(theme_name: str) -> bool:
    """Check if a theme exists in any search path.

    Args:
        theme_name: Name of the theme to check

    Returns:
        True if theme exists, False otherwise
    """
    for search_path in QIcon.themeSearchPaths():
        theme_dir = os.path.join(search_path, theme_name)
        if os.path.exists(theme_dir) and os.path.exists(
            os.path.join(theme_dir, "index.theme")
        ):
            return True
    return False

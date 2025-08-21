"""CLI internationalization support using gettext."""

import gettext
import locale
from pathlib import Path
from typing import Optional, Union


def setup_cli_translations(
    language_code: Optional[str] = None,
) -> Union[gettext.GNUTranslations, gettext.NullTranslations]:
    """Initialize gettext for CLI translations.

    Args:
        language_code: Two-letter language code (e.g., 'es', 'fr').
                      If None, uses standard locale environment variables.

    Returns:
        Translation object for the selected language.
    """
    # locale/ directory is inside the momovu package
    locale_dir = Path(__file__).parent.parent / "locale"

    # Determine language to use
    if not language_code:
        import os

        # Check locale environment variables in order of precedence
        # 1. LC_ALL overrides everything
        # 2. LC_MESSAGES for message translations specifically
        # 3. LANG for general locale
        # 4. LANGUAGE for GNU gettext fallback chain
        for env_var in ["LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"]:
            locale_str = os.environ.get(env_var, "")
            if locale_str:
                # Extract language code from locale string
                # Handle formats like: es_ES.UTF-8, es_ES, es:en, es
                language_code = locale_str.split(":")[0].split(".")[0].split("_")[0]
                if language_code and language_code != "C":  # 'C' means no localization
                    break

        # If still no language code, try system locale
        if not language_code or language_code == "C":
            try:
                system_locale = locale.getdefaultlocale()[0]
                language_code = system_locale[:2] if system_locale else "en"
            except Exception:
                language_code = "en"

    # Setup gettext with fallback
    translation = gettext.translation(
        "momovu-cli",
        localedir=locale_dir,
        languages=[language_code],
        fallback=True,  # Returns NullTranslations if file not found
    )

    # Install _() function globally
    translation.install()

    return translation

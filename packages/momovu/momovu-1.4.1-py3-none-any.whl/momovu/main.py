"""Main entry point for the Momovu application."""

import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import NoReturn, Optional

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

# Handle version import with fallback for development/uninstalled usage
try:
    from momovu._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

from momovu.lib.constants import (
    EXIT_CODE_APP_ERROR,
    EXIT_CODE_SIGINT,
    EXIT_CODE_SUCCESS,
    EXIT_CODE_UNEXPECTED,
    EXIT_CODE_WINDOW_ERROR,
)
from momovu.lib.icon_theme import configure_icon_theme
from momovu.lib.logger import configure_logging, get_logger
from momovu.views.main_window import MainWindow


def parse_arguments() -> argparse.Namespace:
    """Process CLI arguments with validation and help text.

    Returns:
        Namespace with all command options

    Example:
        >>> import sys
        >>> sys.argv = ['momovu', '--help']
        >>> parse_arguments()  # doctest: +ELLIPSIS
        usage: momovu ...
    """
    # Use the global _ function installed by setup_cli_translations
    # If it's not available (e.g., in tests), use a no-op function
    import builtins

    def _fallback(x: str) -> str:
        """Fallback function when translations are not initialized."""
        return x

    _ = builtins._ if hasattr(builtins, "_") else _fallback

    parser = argparse.ArgumentParser(
        description=_("Preview margins on book PDFs before publication."),
        epilog=_("Example: momovu --num-pages 300 --document cover book.pdf"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-D",
        "--debug",
        help=_("Enable debug logging"),
        action="store_true",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help=_("Increase output verbosity (can be used multiple times)"),
        action="count",
        default=0,
    )

    parser.add_argument(
        "-V",
        "--version",
        help=_("Show version and exit"),
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-n",
        "--num-pages",
        help=_("Set number of pages for spine calculations (must be positive)"),
        type=int,
        metavar="N",
    )

    parser.add_argument(
        "-d",
        "--document",
        help=_(
            "Set document type for margin calculations (interior, cover, dustjacket)"
        ),
        choices=["interior", "cover", "dustjacket"],
        metavar="TYPE",
    )

    parser.add_argument(
        "-s",
        "--side-by-side",
        help=_("Enable side-by-side dual page view mode"),
        action="store_true",
    )

    parser.add_argument(
        "-m",
        "--safety-margins",
        help=_("Show safety margins (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-t",
        "--trim-lines",
        help=_("Show trim lines (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-b",
        "--barcode",
        help=_("Show barcode area for cover/dustjacket (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-l",
        "--fold-lines",
        help=_("Show fold lines for cover/dustjacket (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-r",
        "--bleed-lines",
        help=_("Show bleed lines for cover/dustjacket (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-u",
        "--gutter",
        help=_("Show gutter margin for interior documents (default: enabled)"),
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "-p",
        "--presentation",
        help=_("Start in presentation mode"),
        action="store_true",
    )

    parser.add_argument(
        "-f",
        "--fullscreen",
        help=_("Start in fullscreen mode"),
        action="store_true",
    )

    parser.add_argument(
        "pdf_path",
        help=_("Path to the PDF file to preview margins for"),
        metavar="PDF_FILE",
        nargs="?",
        default=None,
    )

    args = parser.parse_args()

    if args.num_pages is not None and args.num_pages <= 0:
        parser.error(_("--num-pages must be a positive integer"))

    if args.pdf_path:
        # Just normalize the path without validation
        # The document presenter will handle validation when loading
        args.pdf_path = str(Path(args.pdf_path))

    return args


def setup_logging(args: argparse.Namespace) -> None:
    """Configure log levels from debug/verbose CLI flags.

    Args:
        args: Namespace with debug and verbose attributes

    Example:
        >>> import argparse
        >>> args = argparse.Namespace(debug=False, verbose=0)
        >>> setup_logging(args)
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.level  # doctest: +ELLIPSIS
        30
    """
    configure_logging(verbose=args.verbose, debug=args.debug)

    if args.verbose > 0 or args.debug:
        logger = get_logger(__name__)
        log_level = (
            logging.DEBUG
            if (args.debug or args.verbose >= 2)
            else (logging.INFO if args.verbose == 1 else logging.WARNING)
        )
        logger.info(f"Logging configured at level: {logging.getLevelName(log_level)}")


def _setup_application() -> QApplication:
    """Initialize Qt app with metadata and signal handling.

    Returns:
        Ready-to-run QApplication

    Raises:
        RuntimeError: If Qt initialization fails

    Example:
        >>> app = _setup_application()
        >>> app.applicationName()
        'Momovu'
    """
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Momovu")
        app.setApplicationVersion(__version__)
        app.setOrganizationName("Momovu")
        app.setOrganizationDomain("momovu.org")

        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        app.setQuitOnLastWindowClosed(True)

        configure_icon_theme()

        return app
    except Exception as e:
        raise RuntimeError(f"Failed to initialize application: {e}") from e


def _load_translations(app: QApplication, language: Optional[str] = None) -> None:
    """Load translations for the application.

    Args:
        app: The QApplication instance
        language: Language code (e.g., 'en', 'es', 'fr'). If None, uses system locale.
    """
    logger = get_logger(__name__)

    # Create translator instances
    translator = QTranslator(app)
    qt_translator = QTranslator(app)

    # Determine locale to use
    if language:
        locale_name = language
    else:
        # Use system locale
        locale = QLocale.system()
        locale_name = locale.name()[
            :2
        ]  # Get just the language code (e.g., 'en' from 'en_US')

    logger.debug(f"Loading translations for locale: {locale_name}")

    # Load application translations
    translations_dir = Path(__file__).parent / "translations"
    translation_file = f"momovu_{locale_name}"

    if translator.load(translation_file, str(translations_dir)):
        app.installTranslator(translator)
        logger.info(f"Loaded application translations for {locale_name}")
    else:
        logger.debug(
            f"No application translations found for {locale_name}, using default"
        )

    # Load Qt's built-in translations for standard dialogs
    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if qt_translator.load(f"qtbase_{locale_name}", qt_translations_path):
        app.installTranslator(qt_translator)
        logger.debug(f"Loaded Qt translations for {locale_name}")


def main() -> NoReturn:
    """Launch Momovu with error handling and proper exit codes.

    Raises:
        SystemExit: Always exits with appropriate code

    Example:
        >>> import sys
        >>> sys.argv = ['momovu', '--help']
        >>> main()  # doctest: +ELLIPSIS
        usage: momovu ...
    """
    logger = get_logger(__name__)
    exit_code = EXIT_CODE_SUCCESS

    try:
        # Setup CLI translations early, before parsing arguments
        from momovu.lib.cli_i18n import setup_cli_translations

        # Try to get saved language preference, but don't fail if Qt isn't available yet
        saved_language = None
        try:
            from momovu.lib.configuration_manager import ConfigurationManager

            config_manager = ConfigurationManager()
            saved_language = config_manager.get_current_language()
        except Exception:
            # ConfigurationManager requires QApplication, which isn't created yet
            # Will use environment variable or system locale instead
            pass

        # Initialize CLI translations (will use LANGUAGE env var if saved_language is None)
        setup_cli_translations(saved_language)

        # Now parse arguments (will use translations)
        args = parse_arguments()
        setup_logging(args)

        logger.info(f"Starting Momovu v{__version__}")
        logger.debug(f"Arguments: {vars(args)}")

        app = _setup_application()

        # Load GUI translations based on user preference or system locale
        _load_translations(app, saved_language if saved_language else None)

        try:
            window = MainWindow(
                pdf_path=args.pdf_path,
                num_pages=args.num_pages,
                book_type=args.document,
                side_by_side=args.side_by_side,
                show_margins=args.safety_margins,
                show_trim_lines=args.trim_lines,
                show_barcode=args.barcode,
                show_fold_lines=args.fold_lines,
                show_bleed_lines=args.bleed_lines,
                show_gutter=args.gutter,
                start_presentation=args.presentation,
                start_fullscreen=args.fullscreen,
            )

            window.show()
            logger.info("Application window created and shown")

            exit_code = app.exec()
            logger.info(f"Application exited with code: {exit_code}")

        except Exception as e:
            logger.error(f"Error creating or running main window: {e}", exc_info=True)
            exit_code = EXIT_CODE_WINDOW_ERROR

    except RuntimeError as e:
        print(f"Application Error: {e}", file=sys.stderr)
        exit_code = EXIT_CODE_APP_ERROR

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        exit_code = EXIT_CODE_SIGINT

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print("An unexpected error occurred. Check logs for details.", file=sys.stderr)
        exit_code = EXIT_CODE_UNEXPECTED

    finally:
        logger.info("Application shutdown complete")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()

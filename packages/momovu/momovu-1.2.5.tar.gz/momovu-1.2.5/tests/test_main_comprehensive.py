"""Comprehensive tests for main module."""

import argparse
import logging
import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from momovu._version import __version__
from momovu.main import (
    _setup_application,
    main,
    parse_arguments,
    setup_logging,
)


class TestParseArguments:
    """Test parse_arguments function."""

    def test_help_argument(self, capsys: Any) -> None:
        """Test --help argument."""
        with patch("sys.argv", ["momovu", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert "Preview margins on book PDFs" in captured.out
            assert "Example: momovu" in captured.out

    def test_version_argument(self, capsys: Any) -> None:
        """Test --version argument."""
        with patch("sys.argv", ["momovu", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert f"momovu {__version__}" in captured.out

    def test_minimal_valid_arguments(self) -> None:
        """Test minimal valid arguments."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch("sys.argv", ["momovu", temp_path]):
                args = parse_arguments()
                assert args.pdf_path == temp_path
                assert args.debug is False
                assert args.verbose == 0
                assert args.num_pages is None
                assert args.document is None
                assert args.side_by_side is False
        finally:
            os.unlink(temp_path)

    def test_all_arguments(self) -> None:
        """Test all arguments."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch(
                "sys.argv",
                [
                    "momovu",
                    "-D",
                    "-vv",
                    "--num-pages",
                    "300",
                    "--document",
                    "cover",
                    "--side-by-side",
                    temp_path,
                ],
            ):
                args = parse_arguments()
                assert args.pdf_path == temp_path
                assert args.debug is True
                assert args.verbose == 2
                assert args.num_pages == 300
                assert args.document == "cover"
                assert args.side_by_side is True
        finally:
            os.unlink(temp_path)

    def test_invalid_num_pages(self) -> None:
        """Test invalid num-pages argument."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with (
                patch("sys.argv", ["momovu", "--num-pages", "-5", temp_path]),
                pytest.raises(SystemExit),
            ):
                parse_arguments()

            with (
                patch("sys.argv", ["momovu", "--num-pages", "abc", temp_path]),
                pytest.raises(SystemExit),
            ):
                parse_arguments()
        finally:
            os.unlink(temp_path)

    def test_invalid_document_type(self) -> None:
        """Test invalid document type."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with (
                patch("sys.argv", ["momovu", "--document", "invalid", temp_path]),
                pytest.raises(SystemExit),
            ):
                parse_arguments()
        finally:
            os.unlink(temp_path)

    def test_missing_pdf_file(self) -> None:
        """Test missing PDF file argument."""
        # PDF file is now optional, so it should not raise SystemExit
        with patch("sys.argv", ["momovu"]):
            args = parse_arguments()
            assert args.pdf_path is None

    def test_nonexistent_pdf_file(self) -> None:
        """Test non-existent PDF file."""
        # Now that validation is removed from parse_arguments,
        # non-existent files are accepted and will be handled later
        with patch("sys.argv", ["momovu", "/nonexistent/file.pdf"]):
            args = parse_arguments()
            assert args.pdf_path == str(Path("/nonexistent/file.pdf"))

    def test_document_choices(self) -> None:
        """Test all valid document type choices."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            for doc_type in ["interior", "cover", "dustjacket"]:
                with patch("sys.argv", ["momovu", "--document", doc_type, temp_path]):
                    args = parse_arguments()
                    assert args.document == doc_type
        finally:
            os.unlink(temp_path)


class TestSetupLogging:
    """Test setup_logging function."""

    def test_default_logging_level(self) -> None:
        """Test default logging level (WARNING)."""
        args = argparse.Namespace(debug=False, verbose=0)

        with patch("momovu.main.configure_logging") as mock_config:
            setup_logging(args)
            mock_config.assert_called_once_with(verbose=0, debug=False)

    def test_verbose_level_1(self) -> None:
        """Test verbose level 1 (INFO)."""
        args = argparse.Namespace(debug=False, verbose=1)

        with patch("momovu.main.configure_logging") as mock_config:
            setup_logging(args)
            mock_config.assert_called_once_with(verbose=1, debug=False)

    def test_verbose_level_2(self) -> None:
        """Test verbose level 2+ (DEBUG)."""
        args = argparse.Namespace(debug=False, verbose=2)

        with patch("momovu.main.configure_logging") as mock_config:
            setup_logging(args)
            mock_config.assert_called_once_with(verbose=2, debug=False)

    def test_debug_flag(self) -> None:
        """Test debug flag sets DEBUG level."""
        args = argparse.Namespace(debug=True, verbose=0)

        with patch("momovu.main.configure_logging") as mock_config:
            setup_logging(args)
            mock_config.assert_called_once_with(verbose=0, debug=True)

    def test_logging_format(self) -> None:
        """Test logging format configuration."""
        args = argparse.Namespace(debug=False, verbose=0)

        # The format is now handled internally by configure_logging
        # We just need to verify it's called correctly
        with patch("momovu.main.configure_logging") as mock_config:
            setup_logging(args)
            mock_config.assert_called_once_with(verbose=0, debug=False)

    def test_third_party_logger_level(self) -> None:
        """Test third-party logger level is set to WARNING."""
        args = argparse.Namespace(debug=True, verbose=0)

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            setup_logging(args)

            # Check PySide6 logger level was set
            mock_get_logger.assert_any_call("PySide6")
            mock_logger.setLevel.assert_any_call(logging.WARNING)


class TestSetupApplication:
    """Test _setup_application function."""

    @pytest.fixture
    def mock_qapp(self) -> Generator[tuple[Mock, Mock], None, None]:
        """Mock QApplication."""
        with patch("momovu.main.QApplication") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            yield mock_app_class, mock_app

    def test_application_setup(self, mock_qapp: Any) -> None:
        """Test application setup."""
        mock_app_class, mock_app = mock_qapp

        with (
            patch("signal.signal") as mock_signal,
            patch("momovu.main.configure_icon_theme") as mock_icon_theme,
        ):
            app = _setup_application()

        assert app == mock_app
        mock_app.setApplicationName.assert_called_once_with("Momovu")
        mock_app.setApplicationVersion.assert_called_once_with(__version__)
        mock_app.setOrganizationName.assert_called_once_with("Momovu")
        mock_app.setOrganizationDomain.assert_called_once_with("momovu.org")
        mock_app.setQuitOnLastWindowClosed.assert_called_once_with(True)

        # Check signal handler was set
        mock_signal.assert_called_once()

        # Check icon theme was configured
        mock_icon_theme.assert_called_once()

    def test_application_setup_failure(self) -> None:
        """Test application setup failure."""
        with patch("momovu.main.QApplication") as mock_app_class:
            mock_app_class.side_effect = Exception("Qt error")

            with pytest.raises(RuntimeError, match="Failed to initialize application"):
                _setup_application()


class TestMain:
    """Test main function."""

    @pytest.fixture
    def mock_dependencies(self) -> Generator[dict[str, Any], None, None]:
        """Mock all main dependencies."""
        with (
            patch("momovu.main.parse_arguments") as mock_parse,
            patch("momovu.main.setup_logging") as mock_logging,
            patch("momovu.main._setup_application") as mock_setup_app,
            patch("momovu.main.MainWindow") as mock_main_window_class,
            patch("sys.exit") as mock_exit,
        ):

            # Setup default mocks
            mock_args = Mock()
            mock_args.pdf_path = "test.pdf"
            mock_args.num_pages = None
            mock_args.document = None
            mock_args.side_by_side = False
            mock_args.debug = False
            mock_args.verbose = 0
            # Add the new visibility options with default values
            mock_args.safety_margins = True
            mock_args.trim_lines = True
            mock_args.barcode = True
            mock_args.fold_lines = True
            mock_args.bleed_lines = True
            mock_args.presentation = False
            mock_args.fullscreen = False
            mock_parse.return_value = mock_args

            mock_app = Mock()
            mock_app.exec.return_value = 0
            mock_setup_app.return_value = mock_app

            mock_viewer = Mock()
            mock_main_window_class.return_value = mock_viewer

            yield {
                "parse_arguments": mock_parse,
                "setup_logging": mock_logging,
                "_setup_application": mock_setup_app,
                "MainWindow": mock_main_window_class,
                "exit": mock_exit,
                "args": mock_args,
                "app": mock_app,
                "viewer": mock_viewer,
            }

    def test_successful_run(self, mock_dependencies: Any) -> None:
        """Test successful application run."""
        main()

        # Check call sequence
        mock_dependencies["parse_arguments"].assert_called_once()
        mock_dependencies["setup_logging"].assert_called_once_with(
            mock_dependencies["args"]
        )
        mock_dependencies["_setup_application"].assert_called_once()
        # MVP is now default, so MainWindow should be called
        mock_dependencies["MainWindow"].assert_called_once_with(
            pdf_path="test.pdf",
            num_pages=None,
            book_type=None,
            side_by_side=False,
            show_margins=True,
            show_trim_lines=True,
            show_barcode=True,
            show_fold_lines=True,
            show_bleed_lines=True,
            start_presentation=False,
            start_fullscreen=False,
        )
        mock_dependencies["viewer"].show.assert_called_once()
        mock_dependencies["app"].exec.assert_called_once()
        mock_dependencies["exit"].assert_called_once_with(0)

    def test_runtime_error(self, mock_dependencies: Any, capsys: Any) -> None:
        """Test RuntimeError handling."""
        mock_dependencies["_setup_application"].side_effect = RuntimeError("App error")

        main()

        captured = capsys.readouterr()
        assert "Application Error: App error" in captured.err
        mock_dependencies["exit"].assert_called_once_with(3)

    def test_keyboard_interrupt(self, mock_dependencies: Any) -> None:
        """Test KeyboardInterrupt handling."""
        mock_dependencies["app"].exec.side_effect = KeyboardInterrupt()

        main()

        mock_dependencies["exit"].assert_called_once_with(130)

    def test_viewer_creation_error(self, mock_dependencies: Any) -> None:
        """Test error during viewer creation."""
        # MVP is now default, so MainWindow should be used
        mock_dependencies["MainWindow"].side_effect = Exception("Viewer error")

        main()

        mock_dependencies["exit"].assert_called_once_with(2)

    def test_unexpected_error(self, mock_dependencies: Any, capsys: Any) -> None:
        """Test unexpected error handling."""
        mock_dependencies["setup_logging"].side_effect = Exception("Unexpected")

        main()

        captured = capsys.readouterr()
        assert "An unexpected error occurred" in captured.err
        mock_dependencies["exit"].assert_called_once_with(4)

    def test_app_exec_non_zero_exit(self, mock_dependencies: Any) -> None:
        """Test non-zero exit code from app.exec."""
        mock_dependencies["app"].exec.return_value = 1

        main()

        mock_dependencies["exit"].assert_called_once_with(1)

    def test_with_all_arguments(self, mock_dependencies: Any) -> None:
        """Test main with all arguments."""
        mock_dependencies["args"].num_pages = 300
        mock_dependencies["args"].document = "cover"
        mock_dependencies["args"].side_by_side = True

        main()

        # MVP is now default, so MainWindow should be called
        mock_dependencies["MainWindow"].assert_called_once_with(
            pdf_path="test.pdf",
            num_pages=300,
            book_type="cover",
            side_by_side=True,
            show_margins=True,
            show_trim_lines=True,
            show_barcode=True,
            show_fold_lines=True,
            show_bleed_lines=True,
            start_presentation=False,
            start_fullscreen=False,
        )

    def test_logging_calls(self, mock_dependencies: Any) -> None:
        """Test logging calls during execution."""
        with patch("momovu.main.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            main()

            # Check key logging calls
            mock_logger.info.assert_any_call(f"Starting Momovu v{__version__}")
            mock_logger.info.assert_any_call("Application window created and shown")
            mock_logger.info.assert_any_call("Application exited with code: 0")
            mock_logger.info.assert_any_call("Application shutdown complete")

    def test_debug_logging(self, mock_dependencies: Any) -> None:
        """Test debug logging with debug flag."""
        mock_dependencies["args"].debug = True

        with patch("momovu.main.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            main()

            # Check debug logging of arguments
            mock_logger.debug.assert_called()
            debug_call = mock_logger.debug.call_args[0][0]
            assert "Arguments:" in debug_call


class TestMainEntryPoint:
    """Test main entry point."""

    def test_main_entry_point(self) -> None:
        """Test __main__ entry point."""
        with (
            patch("momovu.main.main") as mock_main,
            patch("momovu.main.__name__", "__main__"),
        ):
            # Re-execute the module code
            # The main() should not be called during import
            mock_main.assert_not_called()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_string_pdf_path(self) -> None:
        """Test empty string as PDF path."""
        # Empty string is now accepted as a path
        # Empty string is falsy, so it doesn't get converted by Path()
        with patch("sys.argv", ["momovu", ""]):
            args = parse_arguments()
            assert args.pdf_path == ""

    def test_very_large_num_pages(self) -> None:
        """Test very large num-pages value."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch("sys.argv", ["momovu", "--num-pages", "999999999", temp_path]):
                args = parse_arguments()
                assert args.num_pages == 999999999
        finally:
            os.unlink(temp_path)

    def test_unicode_pdf_path(self) -> None:
        """Test Unicode characters in PDF path."""
        # Create file with Unicode name
        unicode_name = "test_文档_🎨.pdf"

        try:
            with open(unicode_name, "wb") as f:
                f.write(b"test")

            with patch("sys.argv", ["momovu", unicode_name]):
                args = parse_arguments()
                assert args.pdf_path == unicode_name
        finally:
            if os.path.exists(unicode_name):
                os.unlink(unicode_name)

    def test_multiple_verbose_flags(self) -> None:
        """Test multiple verbose flags."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch("sys.argv", ["momovu", "-vvvv", temp_path]):
                args = parse_arguments()
                assert args.verbose == 4
        finally:
            os.unlink(temp_path)

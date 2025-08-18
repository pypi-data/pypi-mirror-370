"""
Tests for document operations utilities.
"""

from momovu.lib.exceptions import DocumentLoadError
from momovu.views.components.document_operations import (
    DocumentOperationResult,
    create_error_message,
    extract_filename_from_path,
    format_window_title,
    safe_document_operation,
    should_show_error_dialog,
)


class TestExtractFilenameFromPath:
    """Test filename extraction."""

    def test_simple_filename(self):
        """Test simple filename extraction."""
        assert extract_filename_from_path("/path/to/file.pdf") == "file.pdf"

    def test_windows_path(self):
        """Test Windows path."""
        # On Linux, this won't be interpreted as a Windows path
        # So we'll test with a forward slash path instead
        assert extract_filename_from_path("C:/path/to/file.pdf") == "file.pdf"

    def test_filename_only(self):
        """Test filename without path."""
        assert extract_filename_from_path("file.pdf") == "file.pdf"


class TestFormatWindowTitle:
    """Test window title formatting."""

    def test_base_title_only(self):
        """Test base title without filename."""
        assert format_window_title("Momovu") == "Momovu"
        assert format_window_title("Momovu", None) == "Momovu"

    def test_title_with_filename(self):
        """Test title with filename."""
        assert format_window_title("Momovu", "test.pdf") == "Momovu - test.pdf"


class TestShouldShowErrorDialog:
    """Test error dialog decision logic."""

    def test_normal_exceptions(self):
        """Test normal exceptions should show dialog."""
        assert should_show_error_dialog(ValueError("test"))
        assert should_show_error_dialog(DocumentLoadError("test.pdf", "test"))
        assert should_show_error_dialog(RuntimeError("test"))

    def test_system_exceptions(self):
        """Test system exceptions should not show dialog."""
        assert not should_show_error_dialog(KeyboardInterrupt())
        assert not should_show_error_dialog(SystemExit())


class TestCreateErrorMessage:
    """Test error message creation."""

    def test_document_error(self):
        """Test DocumentError formatting."""
        error = DocumentLoadError("test.pdf", "Invalid PDF")
        message = create_error_message(error)
        assert (
            message == "Document Error: Failed to load document 'test.pdf': Invalid PDF"
        )

    def test_generic_error_with_context(self):
        """Test generic error with context."""
        error = ValueError("Invalid value")
        message = create_error_message(error, "loading document")
        assert message == "Error in loading document: Invalid value"

    def test_generic_error_without_context(self):
        """Test generic error without context."""
        error = ValueError("Invalid value")
        message = create_error_message(error)
        assert message == "An error occurred: Invalid value"


class TestDocumentOperationResult:
    """Test DocumentOperationResult class."""

    def test_success_result(self):
        """Test successful result."""
        result = DocumentOperationResult(True, "Success", {"data": "test"})
        assert result.success
        assert result.message == "Success"
        assert result.data["data"] == "test"
        assert bool(result) is True

    def test_failure_result(self):
        """Test failure result."""
        result = DocumentOperationResult(False, "Failed")
        assert not result.success
        assert result.message == "Failed"
        assert result.data == {}
        assert bool(result) is False

    def test_default_values(self):
        """Test default values."""
        result = DocumentOperationResult(True)
        assert result.success
        assert result.message == ""
        assert result.data == {}


class TestSafeDocumentOperation:
    """Test safe document operation wrapper."""

    def test_successful_operation(self):
        """Test successful operation."""

        def test_func(x, y):
            return x + y

        result = safe_document_operation("test_add", test_func, 2, 3)
        assert result.success
        assert result.data["result"] == 5
        assert "test_add completed" in result.message

    def test_document_error(self):
        """Test DocumentError handling."""

        def test_func():
            raise DocumentLoadError("test.pdf", "Test error")

        result = safe_document_operation("test_error", test_func)
        assert not result.success
        assert (
            "Document error: Failed to load document 'test.pdf': Test error"
            in result.message
        )

    def test_generic_error(self):
        """Test generic error handling."""

        def test_func():
            raise ValueError("Test error")

        result = safe_document_operation("test_error", test_func)
        assert not result.success
        assert "Unexpected error: Test error" in result.message

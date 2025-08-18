"""GUI tests for PDF loading and rendering functionality.

These tests use pytest-qt to test actual PDF loading and rendering
with real Qt widgets and sample PDF files.
"""

import pytest


@pytest.mark.gui
class TestPDFLoading:
    """Test PDF loading functionality with real widgets."""

    def test_load_interior_pdf(self, qtbot, main_window, sample_pdf_paths, gui_helper):
        """Test loading an interior PDF document."""
        # Get a sample interior PDF
        pdf_path = sample_pdf_paths["interior"][0]
        assert pdf_path.exists()

        # Load the PDF
        main_window.load_pdf(str(pdf_path))

        # Wait for document to be loaded
        qtbot.waitUntil(
            lambda: main_window.document_presenter is not None
            and main_window.document_presenter.is_document_loaded(),
            timeout=5000,
        )

        # Wait for rendering
        gui_helper.wait_for_render(qtbot, main_window)

        # Verify document is loaded
        assert main_window.document_presenter.is_document_loaded()

        # Verify page count is correct
        assert gui_helper.get_total_pages(main_window) > 0

        # Verify current page is 0 (first page)
        assert gui_helper.get_current_page(main_window) == 0

        # Verify scene has items (page is rendered)
        assert len(main_window.graphics_scene.items()) > 0

        # Verify window title contains filename
        assert "bovary" in main_window.windowTitle().lower()

    def test_load_cover_pdf(self, qtbot, main_window, sample_pdf_paths, gui_helper):
        """Test loading a cover PDF document."""
        # Get a sample cover PDF
        pdf_path = sample_pdf_paths["cover"][0]
        assert pdf_path.exists()

        # Load the PDF
        main_window.load_pdf(str(pdf_path))

        # Wait for document to be loaded
        qtbot.waitUntil(
            lambda: main_window.document_presenter is not None
            and main_window.document_presenter.is_document_loaded(),
            timeout=5000,
        )

        # Wait for rendering
        gui_helper.wait_for_render(qtbot, main_window)

        # Verify document is loaded
        assert main_window.document_presenter.is_document_loaded()

        # Verify scene has items
        assert len(main_window.graphics_scene.items()) > 0

        # Verify window title contains filename
        assert "bovary" in main_window.windowTitle().lower()

    def test_load_dustjacket_pdf(
        self, qtbot, main_window, sample_pdf_paths, gui_helper
    ):
        """Test loading a dustjacket PDF document."""
        # Get a sample dustjacket PDF
        pdf_path = sample_pdf_paths["dustjacket"][0]
        assert pdf_path.exists()

        # Load the PDF
        main_window.load_pdf(str(pdf_path))

        # Wait for document to be loaded
        qtbot.waitUntil(
            lambda: main_window.document_presenter is not None
            and main_window.document_presenter.is_document_loaded(),
            timeout=5000,
        )

        # Wait for rendering
        gui_helper.wait_for_render(qtbot, main_window)

        # Verify document is loaded
        assert main_window.document_presenter.is_document_loaded()

        # Verify scene has items
        assert len(main_window.graphics_scene.items()) > 0

    def test_load_multiple_pdfs_sequentially(
        self, qtbot, main_window, sample_pdf_paths, gui_helper
    ):
        """Test loading multiple PDFs one after another."""
        pdf_types = ["interior", "cover", "dustjacket"]

        for pdf_type in pdf_types:
            pdf_path = sample_pdf_paths[pdf_type][0]
            assert pdf_path.exists()

            # Load the PDF
            main_window.load_pdf(str(pdf_path))

            # Wait for document to be loaded
            qtbot.waitUntil(
                lambda: main_window.document_presenter is not None
                and main_window.document_presenter.is_document_loaded(),
                timeout=5000,
            )

            # Wait for rendering
            gui_helper.wait_for_render(qtbot, main_window)

            # Verify document is loaded
            assert main_window.document_presenter.is_document_loaded()

            # Verify scene has items
            assert len(main_window.graphics_scene.items()) > 0

    def test_close_and_reload_pdf(
        self, qtbot, main_window_with_pdf, sample_pdf_paths, gui_helper
    ):
        """Test closing a PDF and loading another one."""
        # Verify initial PDF is loaded
        assert main_window_with_pdf.document_presenter.is_document_loaded()

        # Load a different PDF (should replace the current one)
        new_pdf_path = sample_pdf_paths["cover"][0]
        assert new_pdf_path.exists()

        main_window_with_pdf.load_pdf(str(new_pdf_path))

        # Wait for new document to be loaded
        qtbot.waitUntil(
            lambda: main_window_with_pdf.document_presenter.is_document_loaded(),
            timeout=5000,
        )

        # Wait for rendering
        gui_helper.wait_for_render(qtbot, main_window_with_pdf)

        # Verify new document is loaded
        assert main_window_with_pdf.document_presenter.is_document_loaded()
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        assert gui_helper.get_total_pages(main_window_with_pdf) > 0


@pytest.mark.gui
class TestPDFRendering:
    """Test PDF rendering functionality with real widgets."""

    def test_initial_rendering(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that PDF is rendered correctly on initial load."""
        # Verify document is loaded
        assert main_window_with_pdf.document_presenter.is_document_loaded()

        # Verify scene has items
        scene_items = main_window_with_pdf.graphics_scene.items()
        assert len(scene_items) > 0

        # Verify current page is 0
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Verify page label is updated
        page_label_text = main_window_with_pdf.page_label.text()
        assert "Page: 1/" in page_label_text

    def test_rendering_after_navigation(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that pages are rendered correctly after navigation."""
        # Navigate to next page
        main_window_with_pdf.next_page()

        # Wait for rendering
        qtbot.wait(300)

        # Verify page changed
        assert gui_helper.get_current_page(main_window_with_pdf) == 1

        # Verify scene still has items
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        # Navigate back
        main_window_with_pdf.previous_page()

        # Wait for rendering
        qtbot.wait(300)

        # Verify page changed back
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Verify scene still has items
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

    def test_rendering_with_margins(self, qtbot, main_window_with_pdf, gui_helper):
        """Test rendering with margins enabled/disabled."""
        # Ensure margins are initially shown
        if not main_window_with_pdf.show_margins_action.isChecked():
            main_window_with_pdf.toggle_margins()

        qtbot.wait(200)

        # Verify scene has items with margins
        items_with_margins = len(main_window_with_pdf.graphics_scene.items())
        assert items_with_margins > 0

        # Toggle margins off
        main_window_with_pdf.toggle_margins()
        qtbot.wait(200)

        # Verify scene still has items (but possibly fewer without margin overlays)
        items_without_margins = len(main_window_with_pdf.graphics_scene.items())
        assert items_without_margins > 0

        # Toggle margins back on
        main_window_with_pdf.toggle_margins()
        qtbot.wait(200)

        # Verify margins are rendered again
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

    def test_rendering_cover_with_overlays(
        self, qtbot, main_window_with_cover, gui_helper
    ):
        """Test rendering cover document with various overlays."""
        # Verify initial rendering
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Toggle trim lines
        main_window_with_cover.toggle_trim_lines()
        qtbot.wait(200)
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Toggle barcode (only for cover/dustjacket)
        main_window_with_cover.toggle_barcode()
        qtbot.wait(200)
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Toggle bleed lines (only for cover/dustjacket)
        main_window_with_cover.toggle_bleed_lines()
        qtbot.wait(200)
        assert len(main_window_with_cover.graphics_scene.items()) > 0

    def test_rendering_dustjacket_with_fold_lines(
        self, qtbot, main_window_with_dustjacket, gui_helper
    ):
        """Test rendering dustjacket with fold lines."""
        # Verify initial rendering
        assert len(main_window_with_dustjacket.graphics_scene.items()) > 0

        # Toggle fold lines (only for dustjacket)
        main_window_with_dustjacket.toggle_fold_lines()
        qtbot.wait(200)
        assert len(main_window_with_dustjacket.graphics_scene.items()) > 0

        # Toggle fold lines off
        main_window_with_dustjacket.toggle_fold_lines()
        qtbot.wait(200)
        assert len(main_window_with_dustjacket.graphics_scene.items()) > 0

    def test_fit_to_page_after_load(self, qtbot, main_window_with_pdf, gui_helper):
        """Test that fit to page works correctly after loading."""
        # Get initial zoom level
        initial_zoom = gui_helper.get_zoom_level(main_window_with_pdf)

        # Zoom in first
        main_window_with_pdf.zoom_in()
        qtbot.wait(200)

        # Verify zoom changed
        zoomed_level = gui_helper.get_zoom_level(main_window_with_pdf)
        assert zoomed_level > initial_zoom

        # Fit to page
        main_window_with_pdf.fit_to_page()
        qtbot.wait(200)

        # Verify scene is still rendered
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        # Zoom level should be different from zoomed level
        fit_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert fit_zoom != zoomed_level

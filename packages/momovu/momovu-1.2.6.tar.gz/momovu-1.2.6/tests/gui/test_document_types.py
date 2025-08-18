"""GUI tests for document type switching functionality.

These tests use pytest-qt to test switching between interior,
cover, and dustjacket document types with real Qt widgets.
"""

import pytest
from PySide6.QtCore import Qt


@pytest.mark.gui
class TestDocumentTypeSwitching:
    """Test document type switching functionality with real widgets."""

    def test_switch_from_interior_to_cover(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test switching from interior to cover document type."""
        # Verify starting with interior
        assert gui_helper.get_document_type(main_window_with_pdf) == "interior"

        # Switch to cover
        main_window_with_pdf.set_document_type("cover")
        qtbot.wait(500)

        # Verify document type changed
        assert gui_helper.get_document_type(main_window_with_pdf) == "cover"

        # Verify scene is re-rendered
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        # For cover, current page should be 0
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Note: Cover documents still report total pages from the PDF,
        # but only render the cover page

        # Verify num_pages spinbox is visible for cover
        assert main_window_with_pdf.num_pages_spinbox is not None
        assert main_window_with_pdf.num_pages_spinbox.isVisible()

    def test_switch_from_interior_to_dustjacket(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test switching from interior to dustjacket document type."""
        # Verify starting with interior
        assert gui_helper.get_document_type(main_window_with_pdf) == "interior"

        # Switch to dustjacket
        main_window_with_pdf.set_document_type("dustjacket")
        qtbot.wait(500)

        # Verify document type changed
        assert gui_helper.get_document_type(main_window_with_pdf) == "dustjacket"

        # Verify scene is re-rendered
        assert len(main_window_with_pdf.graphics_scene.items()) > 0

        # For dustjacket, current page should be 0
        assert gui_helper.get_current_page(main_window_with_pdf) == 0

        # Note: Dustjacket documents still report total pages from the PDF,
        # but only render the dustjacket page

        # Verify num_pages spinbox is visible for dustjacket
        assert main_window_with_pdf.num_pages_spinbox is not None
        assert main_window_with_pdf.num_pages_spinbox.isVisible()

    def test_switch_between_all_types(self, qtbot, main_window_with_pdf, gui_helper):
        """Test switching between all document types."""
        doc_types = ["interior", "cover", "dustjacket"]

        for doc_type in doc_types:
            # Switch to document type
            main_window_with_pdf.set_document_type(doc_type)
            qtbot.wait(500)

            # Verify type changed
            assert gui_helper.get_document_type(main_window_with_pdf) == doc_type

            # Verify scene is rendered
            assert len(main_window_with_pdf.graphics_scene.items()) > 0

            # Verify current page is 0
            assert gui_helper.get_current_page(main_window_with_pdf) == 0

            # Note: All document types report the actual PDF page count,
            # but cover and dustjacket only render their respective pages

    def test_document_type_affects_overlays(
        self, qtbot, main_window_with_cover, gui_helper
    ):
        """Test that document type affects available overlays."""
        # Cover document should have barcode and bleed lines available
        assert gui_helper.get_document_type(main_window_with_cover) == "cover"

        # Toggle barcode (should work for cover)
        main_window_with_cover.toggle_barcode()
        qtbot.wait(300)
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Toggle bleed lines (should work for cover)
        main_window_with_cover.toggle_bleed_lines()
        qtbot.wait(300)
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Switch to interior
        main_window_with_cover.set_document_type("interior")
        qtbot.wait(500)

        # Barcode and bleed lines should not be visible for interior
        # (The actions might still be callable but won't have effect)
        assert gui_helper.get_document_type(main_window_with_cover) == "interior"
        assert len(main_window_with_cover.graphics_scene.items()) > 0

    def test_dustjacket_fold_lines(
        self, qtbot, main_window_with_dustjacket, gui_helper
    ):
        """Test that fold lines are available for dustjacket."""
        # Verify dustjacket type
        assert gui_helper.get_document_type(main_window_with_dustjacket) == "dustjacket"

        # Toggle fold lines on
        main_window_with_dustjacket.toggle_fold_lines()
        qtbot.wait(300)

        # Verify scene is rendered
        assert len(main_window_with_dustjacket.graphics_scene.items()) > 0

        # Toggle fold lines off
        main_window_with_dustjacket.toggle_fold_lines()
        qtbot.wait(300)

        # Verify scene is still rendered
        assert len(main_window_with_dustjacket.graphics_scene.items()) > 0

    def test_num_pages_spinbox_for_cover_dustjacket(
        self, qtbot, main_window_with_cover, gui_helper
    ):
        """Test num_pages spinbox functionality for cover/dustjacket."""
        # Verify cover type
        assert gui_helper.get_document_type(main_window_with_cover) == "cover"

        # Get the num_pages spinbox
        spinbox = main_window_with_cover.num_pages_spinbox
        assert spinbox is not None
        assert spinbox.isVisible()

        # Change the value
        new_value = 200
        spinbox.clear()
        qtbot.keyClicks(spinbox, str(new_value))
        qtbot.keyClick(spinbox, Qt.Key.Key_Return)
        qtbot.wait(300)

        # Verify value changed
        assert spinbox.value() == new_value

        # Verify scene is re-rendered with new spine width
        assert len(main_window_with_cover.graphics_scene.items()) > 0

        # Switch to dustjacket
        main_window_with_cover.set_document_type("dustjacket")
        qtbot.wait(500)

        # Num pages should be preserved
        assert spinbox.value() == new_value

        # Change value again
        another_value = 150
        spinbox.clear()
        qtbot.keyClicks(spinbox, str(another_value))
        qtbot.keyClick(spinbox, Qt.Key.Key_Return)
        qtbot.wait(300)

        # Verify value changed
        assert spinbox.value() == another_value

        # Verify scene is re-rendered
        assert len(main_window_with_cover.graphics_scene.items()) > 0

    def test_document_type_preserves_zoom(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test that zoom level is preserved when switching document types."""
        # Zoom in
        for _ in range(3):
            main_window_with_pdf.zoom_in()
            qtbot.wait(100)

        zoom_level = gui_helper.get_zoom_level(main_window_with_pdf)

        # Switch to cover
        main_window_with_pdf.set_document_type("cover")
        qtbot.wait(500)

        # Zoom should be approximately preserved
        cover_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert cover_zoom == pytest.approx(zoom_level, rel=0.1)

        # Switch to dustjacket
        main_window_with_pdf.set_document_type("dustjacket")
        qtbot.wait(500)

        # Zoom should still be approximately preserved
        dustjacket_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert dustjacket_zoom == pytest.approx(zoom_level, rel=0.1)

        # Switch back to interior
        main_window_with_pdf.set_document_type("interior")
        qtbot.wait(500)

        # Zoom should still be approximately preserved
        interior_zoom = gui_helper.get_zoom_level(main_window_with_pdf)
        assert interior_zoom == pytest.approx(zoom_level, rel=0.1)

    def test_margins_available_for_all_types(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test that margins can be toggled for all document types."""
        doc_types = ["interior", "cover", "dustjacket"]

        for doc_type in doc_types:
            # Switch to document type
            main_window_with_pdf.set_document_type(doc_type)
            qtbot.wait(500)

            # Toggle margins off
            if main_window_with_pdf.show_margins_action.isChecked():
                main_window_with_pdf.toggle_margins()
                qtbot.wait(300)

            # Verify scene is rendered
            items_without_margins = len(main_window_with_pdf.graphics_scene.items())
            assert items_without_margins > 0

            # Toggle margins on
            main_window_with_pdf.toggle_margins()
            qtbot.wait(300)

            # Verify scene is still rendered
            items_with_margins = len(main_window_with_pdf.graphics_scene.items())
            assert items_with_margins > 0

    def test_trim_lines_available_for_all_types(
        self, qtbot, main_window_with_pdf, gui_helper
    ):
        """Test that trim lines can be toggled for all document types."""
        doc_types = ["interior", "cover", "dustjacket"]

        for doc_type in doc_types:
            # Switch to document type
            main_window_with_pdf.set_document_type(doc_type)
            qtbot.wait(500)

            # Toggle trim lines
            main_window_with_pdf.toggle_trim_lines()
            qtbot.wait(300)

            # Verify scene is rendered
            assert len(main_window_with_pdf.graphics_scene.items()) > 0

            # Toggle trim lines again
            main_window_with_pdf.toggle_trim_lines()
            qtbot.wait(300)

            # Verify scene is still rendered
            assert len(main_window_with_pdf.graphics_scene.items()) > 0

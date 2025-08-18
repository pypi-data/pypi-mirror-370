"""Test navigation icon visibility in toolbar based on document type."""

import pytest
from PySide6.QtWidgets import QMainWindow

from momovu.models.margin_settings import MarginSettingsModel
from momovu.presenters.margin import MarginPresenter
from momovu.views.components.toolbar_builder import ToolbarBuilder


class TestToolbarNavigationVisibility:
    """Test navigation icon visibility based on document type."""

    @pytest.fixture
    def setup_toolbar(self, qtbot):
        """Set up toolbar with margin presenter."""
        main_window = QMainWindow()
        qtbot.addWidget(main_window)

        margin_model = MarginSettingsModel()
        margin_presenter = MarginPresenter(margin_model)

        toolbar_builder = ToolbarBuilder(main_window)
        toolbar_builder.build_toolbar({}, margin_presenter)

        return toolbar_builder, margin_presenter

    def test_navigation_visible_for_interior(self, setup_toolbar):
        """Navigation icons should be visible for interior documents."""
        toolbar_builder, margin_presenter = setup_toolbar

        # Set document type to interior
        margin_presenter.set_document_type("interior")
        toolbar_builder.update_toolbar_visibility()

        # Check all navigation actions are visible
        for action_name in ["first_page", "prev_page", "next_page", "last_page"]:
            action = toolbar_builder.actions.get(action_name)
            assert action is not None, f"Action {action_name} not found"
            assert (
                action.isVisible()
            ), f"Action {action_name} should be visible for interior"

    def test_navigation_hidden_for_cover(self, setup_toolbar):
        """Navigation icons should be hidden for cover documents."""
        toolbar_builder, margin_presenter = setup_toolbar

        # Set document type to cover
        margin_presenter.set_document_type("cover")
        toolbar_builder.update_toolbar_visibility()

        # Check all navigation actions are hidden
        for action_name in ["first_page", "prev_page", "next_page", "last_page"]:
            action = toolbar_builder.actions.get(action_name)
            assert action is not None, f"Action {action_name} not found"
            assert (
                not action.isVisible()
            ), f"Action {action_name} should be hidden for cover"

    def test_navigation_hidden_for_dustjacket(self, setup_toolbar):
        """Navigation icons should be hidden for dustjacket documents."""
        toolbar_builder, margin_presenter = setup_toolbar

        # Set document type to dustjacket
        margin_presenter.set_document_type("dustjacket")
        toolbar_builder.update_toolbar_visibility()

        # Check all navigation actions are hidden
        for action_name in ["first_page", "prev_page", "next_page", "last_page"]:
            action = toolbar_builder.actions.get(action_name)
            assert action is not None, f"Action {action_name} not found"
            assert (
                not action.isVisible()
            ), f"Action {action_name} should be hidden for dustjacket"

    def test_navigation_visibility_toggle(self, setup_toolbar):
        """Navigation visibility should toggle when document type changes."""
        toolbar_builder, margin_presenter = setup_toolbar

        # Start with interior - navigation should be visible
        margin_presenter.set_document_type("interior")
        toolbar_builder.update_toolbar_visibility()
        assert toolbar_builder.actions["first_page"].isVisible()

        # Change to cover - navigation should be hidden
        margin_presenter.set_document_type("cover")
        toolbar_builder.update_toolbar_visibility()
        assert not toolbar_builder.actions["first_page"].isVisible()

        # Change back to interior - navigation should be visible again
        margin_presenter.set_document_type("interior")
        toolbar_builder.update_toolbar_visibility()
        assert toolbar_builder.actions["first_page"].isVisible()

    def test_spinbox_visibility_remains_correct(self, setup_toolbar):
        """Page/Pages spinbox visibility should work correctly alongside navigation."""
        toolbar_builder, margin_presenter = setup_toolbar

        # Interior: page spinbox visible, pages spinbox hidden
        margin_presenter.set_document_type("interior")
        toolbar_builder.update_toolbar_visibility()
        assert toolbar_builder.page_spinbox_action.isVisible()
        assert not toolbar_builder.pages_spinbox_action.isVisible()

        # Cover: page spinbox hidden, pages spinbox visible
        margin_presenter.set_document_type("cover")
        toolbar_builder.update_toolbar_visibility()
        assert not toolbar_builder.page_spinbox_action.isVisible()
        assert toolbar_builder.pages_spinbox_action.isVisible()

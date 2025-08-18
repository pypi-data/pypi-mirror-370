=============
API Reference
=============

This document provides a comprehensive API reference for the Momovu library. All public classes,
methods, and functions are documented here using automatic documentation generation from the source code.

.. contents:: Table of Contents
   :local:
   :depth: 3

Core Module
===========

Main Entry Point
----------------

.. automodule:: momovu.main
   :members:
   :undoc-members:
   :show-inheritance:

Models
======

The models implement the Model component of the MVP (Model-View-Presenter) architecture pattern.
They handle data storage and business logic.

Base Model
----------

.. automodule:: momovu.models.base
   :members:
   :undoc-members:
   :show-inheritance:

Document Model
--------------

.. automodule:: momovu.models.document
   :members:
   :undoc-members:
   :show-inheritance:

Margin Settings Model
---------------------

.. automodule:: momovu.models.margin_settings
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Model
-------------------

.. automodule:: momovu.models.configuration
   :members:
   :undoc-members:
   :show-inheritance:

View State Model
----------------

.. automodule:: momovu.models.view_state
   :members:
   :undoc-members:
   :show-inheritance:

Presenters
==========

The presenters implement the Presenter component of the MVP architecture pattern.
They handle the business logic and coordinate between models and views.

Base Presenter
--------------

.. automodule:: momovu.presenters.base
   :members:
   :undoc-members:
   :show-inheritance:

Configuration Presenter
-----------------------

.. automodule:: momovu.presenters.configuration
   :members:
   :undoc-members:
   :show-inheritance:

Document Presenter
------------------

.. automodule:: momovu.presenters.document
   :members:
   :undoc-members:
   :show-inheritance:

Margin Presenter
----------------

.. automodule:: momovu.presenters.margin
   :members:
   :undoc-members:
   :show-inheritance:

Navigation Presenter
--------------------

.. automodule:: momovu.presenters.navigation
   :members:
   :undoc-members:
   :show-inheritance:

Views
=====

The views implement the View component of the MVP architecture pattern.
They handle the user interface and display logic.

Main Window
-----------

.. automodule:: momovu.views.main_window
   :members:
   :undoc-members:
   :show-inheritance:

Page Item
---------

.. automodule:: momovu.views.page_item
   :members:
   :undoc-members:
   :show-inheritance:

View Components
===============

These components handle specific aspects of the view layer.

About Dialog
------------

.. automodule:: momovu.views.components.about_dialog
   :members:
   :undoc-members:
   :show-inheritance:

Cleanup Coordinator
-------------------

.. automodule:: momovu.views.components.cleanup_coordinator
   :members:
   :undoc-members:
   :show-inheritance:

Dialog Manager
--------------

.. automodule:: momovu.views.components.dialog_manager
   :members:
   :undoc-members:
   :show-inheritance:

Document Operations
-------------------

.. automodule:: momovu.views.components.document_operations
   :members:
   :undoc-members:
   :show-inheritance:

Graphics View
-------------

.. automodule:: momovu.views.components.graphics_view
   :members:
   :undoc-members:
   :show-inheritance:

Margin Renderer
---------------

.. automodule:: momovu.views.components.margin_renderer
   :members:
   :undoc-members:
   :show-inheritance:

Menu Builder
------------

.. automodule:: momovu.views.components.menu_builder
   :members:
   :undoc-members:
   :show-inheritance:

Navigation Controller
---------------------

.. automodule:: momovu.views.components.navigation_controller
   :members:
   :undoc-members:
   :show-inheritance:

Page Positions
--------------

.. automodule:: momovu.views.components.page_positions
   :members:
   :undoc-members:
   :show-inheritance:

Page Renderer
-------------

.. automodule:: momovu.views.components.page_renderer
   :members:
   :undoc-members:
   :show-inheritance:

Page SpinBox
------------

.. automodule:: momovu.views.components.page_spinbox
   :members:
   :undoc-members:
   :show-inheritance:

Preferences Dialog
------------------

.. automodule:: momovu.views.components.preferences_dialog
   :members:
   :undoc-members:
   :show-inheritance:

Scroll Manager
--------------

.. automodule:: momovu.views.components.scroll_manager
   :members:
   :undoc-members:
   :show-inheritance:

Signal Connections
------------------

.. automodule:: momovu.views.components.signal_connections
   :members:
   :undoc-members:
   :show-inheritance:

Spine Width Calculator Dialog
------------------------------

.. automodule:: momovu.views.components.spine_width_calculator_dialog
   :members:
   :undoc-members:
   :show-inheritance:

State Saver
-----------

.. automodule:: momovu.views.components.state_saver
   :members:
   :undoc-members:
   :show-inheritance:

Toggle Manager
--------------

.. automodule:: momovu.views.components.toggle_manager
   :members:
   :undoc-members:
   :show-inheritance:

Toolbar Builder
---------------

.. automodule:: momovu.views.components.toolbar_builder
   :members:
   :undoc-members:
   :show-inheritance:

UI State Manager
----------------

.. automodule:: momovu.views.components.ui_state_manager
   :members:
   :undoc-members:
   :show-inheritance:

Window Setup
------------

.. automodule:: momovu.views.components.window_setup
   :members:
   :undoc-members:
   :show-inheritance:

Zoom Controller
---------------

.. automodule:: momovu.views.components.zoom_controller
   :members:
   :undoc-members:
   :show-inheritance:

Page Rendering Strategies
=========================

These strategies implement different page rendering approaches.

Base Strategy
-------------

.. automodule:: momovu.views.components.page_strategies.base
   :members:
   :undoc-members:
   :show-inheritance:

All Pages Strategy
------------------

.. automodule:: momovu.views.components.page_strategies.all_pages
   :members:
   :undoc-members:
   :show-inheritance:

Page Pair Strategy
------------------

.. automodule:: momovu.views.components.page_strategies.page_pair
   :members:
   :undoc-members:
   :show-inheritance:

Side by Side Strategy
---------------------

.. automodule:: momovu.views.components.page_strategies.side_by_side
   :members:
   :undoc-members:
   :show-inheritance:

Single Page Strategy
--------------------

.. automodule:: momovu.views.components.page_strategies.single_page
   :members:
   :undoc-members:
   :show-inheritance:

Margin Renderers
================

These renderers handle margin and overlay drawing for different document types.

Base Renderer
-------------

.. automodule:: momovu.views.components.renderers.base
   :members:
   :undoc-members:
   :show-inheritance:

Cover Renderer
--------------

.. automodule:: momovu.views.components.renderers.cover
   :members:
   :undoc-members:
   :show-inheritance:

Dustjacket Renderer
-------------------

.. automodule:: momovu.views.components.renderers.dustjacket
   :members:
   :undoc-members:
   :show-inheritance:

Interior Renderer
-----------------

.. automodule:: momovu.views.components.renderers.interior
   :members:
   :undoc-members:
   :show-inheritance:

Library Modules
===============

These modules provide utility functions and shared functionality.

Configuration Manager
---------------------

.. automodule:: momovu.lib.configuration_manager
   :members:
   :undoc-members:
   :show-inheritance:

Constants
---------

.. automodule:: momovu.lib.constants
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. automodule:: momovu.lib.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Icon Theme
----------

.. automodule:: momovu.lib.icon_theme
   :members:
   :undoc-members:
   :show-inheritance:

Logger
------

.. automodule:: momovu.lib.logger
   :members:
   :undoc-members:
   :show-inheritance:

Shortcuts Dialog
----------------

.. automodule:: momovu.lib.shortcuts_dialog
   :members:
   :undoc-members:
   :show-inheritance:

Dustjacket Spine Widths
------------------------

.. automodule:: momovu.lib.sizes.dustjacket_spine_widths
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
==============

Basic Usage
-----------

.. code-block:: python

    import sys
    from PySide6.QtWidgets import QApplication
    from momovu.main import main

    # Run the application
    if __name__ == "__main__":
        main()

Command Line Usage
------------------

.. code-block:: bash

    # Open a PDF file
    momovu document.pdf

    # Specify document type and page count
    momovu --type cover --pages 300 cover.pdf

    # Enable verbose logging
    momovu -v document.pdf

    # Show version
    momovu --version

Programmatic Usage
------------------

.. code-block:: python

    from PySide6.QtWidgets import QApplication
    from momovu.views.main_window import MainWindow
    from momovu.models.document import Document
    from momovu.models.margin_settings import MarginSettingsModel
    from momovu.models.view_state import ViewStateModel
    from momovu.presenters.document import DocumentPresenter
    from momovu.presenters.margin import MarginPresenter
    from momovu.presenters.navigation import NavigationPresenter

    # Create application
    app = QApplication([])

    # Create models
    document_model = Document()
    margin_model = MarginSettingsModel()
    view_model = ViewStateModel()

    # Create presenters
    doc_presenter = DocumentPresenter(document_model)
    margin_presenter = MarginPresenter(margin_model)
    nav_presenter = NavigationPresenter(view_model, document_model)

    # Create main window
    window = MainWindow(
        pdf_path="document.pdf",
        num_pages=300,
        book_type="interior",
        side_by_side=False,
        document_presenter=doc_presenter,
        margin_presenter=margin_presenter,
        navigation_presenter=nav_presenter
    )

    # Show window and run
    window.show()
    app.exec()

Working with Document Types
---------------------------

.. code-block:: python

    # Set document type to interior
    margin_presenter.set_document_type("interior")

    # Set document type to cover with spine calculation
    margin_presenter.set_document_type("cover")
    margin_presenter.set_num_pages(300)  # Automatically calculates spine width

    # Set document type to dustjacket
    margin_presenter.set_document_type("dustjacket")
    margin_presenter.set_flap_dimensions(
        flap_width=82.55,  # 3.25 inches
        flap_height=228.6  # 9 inches
    )

Navigation Examples
-------------------

.. code-block:: python

    # Navigate to specific page
    nav_presenter.go_to_page(10)

    # Navigate relatively
    nav_presenter.next_page()
    nav_presenter.previous_page()

    # Jump to boundaries
    nav_presenter.go_to_first_page()
    nav_presenter.go_to_last_page()

    # Toggle view modes
    nav_presenter.toggle_view_mode()  # Switch between single and side-by-side

Margin Configuration
--------------------

.. code-block:: python

    # Set safety margins
    margin_presenter.set_safety_margin(5.0)  # 5mm

    # Toggle overlay visibility
    margin_presenter.set_show_margins(True)
    margin_presenter.set_show_trim_lines(True)
    margin_presenter.set_show_barcode(True)
    margin_presenter.set_show_fold_lines(True)

    # Get calculated margins for rendering
    margin_rect = margin_presenter.calculate_margin_rect(
        x=0, y=0, width=612, height=792
    )

Error Handling
--------------

.. code-block:: python

    from momovu.lib.exceptions import DocumentLoadError
    from momovu.views.components.dialog_manager import DialogManager

    try:
        # Attempt to load document
        success = doc_presenter.load_document("document.pdf")
        if not success:
            raise DocumentLoadError("document.pdf", "Failed to load")
    except DocumentLoadError as e:
        dialog_manager = DialogManager(window)
        dialog_manager.show_error("Error Loading PDF", str(e))

Extending Momovu
================

Creating Custom Strategies
--------------------------

.. code-block:: python

    from momovu.views.components.page_strategies.base import BaseStrategy

    class CustomStrategy(BaseStrategy):
        def render(
            self,
            current_page: int,
            total_pages: int,
            show_fold_lines: bool = False
        ) -> None:
            # Custom rendering logic
            page_item = self.create_page_item(
                page_index=current_page,
                x=0,
                y=0
            )
            # Add custom overlays
            self.draw_overlays(0, 0, width, height)

Creating Custom Renderers
-------------------------

.. code-block:: python

    from momovu.views.components.renderers.base import BaseRenderer

    class CustomRenderer(BaseRenderer):
        def draw_margins(
            self,
            x: float,
            y: float,
            width: float,
            height: float,
            margin_size: float
        ) -> None:
            # Custom margin drawing
            self.add_margin_rect(
                x + margin_size,
                y + margin_size,
                width - 2 * margin_size,
                height - 2 * margin_size
            )

        def draw_trim_lines(
            self,
            x: float,
            y: float,
            width: float,
            height: float
        ) -> None:
            # Custom trim line drawing
            pen = self.get_trim_pen()
            # Draw custom trim lines

Adding Custom Validators
------------------------

.. code-block:: python

    from momovu.lib.exceptions import ValidationError

    def validate_custom_parameter(value: Any, param_name: str) -> None:
        """Validate a custom parameter."""
        if not isinstance(value, CustomType):
            raise ValidationError(
                f"{param_name} must be a CustomType instance"
            )
        # Additional validation logic

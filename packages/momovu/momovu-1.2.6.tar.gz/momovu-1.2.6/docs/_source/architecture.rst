============
Architecture
============

This document describes the software architecture of Momovu, including its design patterns,
component structure, and technical decisions.

Overview
========

Momovu follows the **Model-View-Presenter (MVP)** architectural pattern with clear separation of concerns:

* **Model Layer**: Data storage and business state management
* **View Layer**: Qt-based GUI components and user interface
* **Presenter Layer**: Business logic and coordination between models and views
* **Component Layer**: Specialized UI components for specific functionality

Technology Stack
================

Core Technologies
-----------------

* **Python 3.9+**: Modern Python with type hints
* **PySide6/Qt6**: Cross-platform GUI framework
* **QPdfDocument**: Native PDF rendering
* **QGraphicsView**: Scene-based rendering system

Design Principles
-----------------

* **MVP Pattern**: Clear separation between data, logic, and presentation
* **Single Responsibility**: Each class has one well-defined purpose
* **Dependency Injection**: Loose coupling between components
* **Observer Pattern**: Event-driven updates via property change notifications
* **Strategy Pattern**: Different rendering strategies for various view modes
* **Component-Based Architecture**: Modular UI components

MVP Architecture
================

The application follows a strict MVP pattern where:

1. **Models** hold data and notify observers of changes
2. **Views** display data and handle user input
3. **Presenters** contain business logic and coordinate between models and views

Model Layer
-----------

**Base Model**

All models inherit from ``BaseModel`` which provides:

.. code-block:: text

    BaseModel
    ├── Property change notification
    ├── Observer management
    ├── Batch update support
    ├── Property validation
    └── State management

**Document Model**

Manages PDF document data:

.. code-block:: python

    class Document(BaseModel):
        - file_path: Path to PDF file
        - page_count: Total number of pages
        - page_sizes: Dictionary of page dimensions
        - is_loaded: Loading state
        - error_message: Error details if failed

**Margin Settings Model**

Stores margin and overlay configuration:

.. code-block:: python

    class MarginSettingsModel(BaseModel):
        - document_type: interior/cover/dustjacket
        - safety_margin_mm: Margin size in millimeters
        - spine_width: Calculated spine width
        - flap_width/height: Dustjacket flap dimensions
        - show_margins/trim_lines/barcode/fold_lines: Visibility flags

**View State Model**

Maintains view-related state:

.. code-block:: python

    class ViewStateModel(BaseModel):
        - current_page: Active page index
        - view_mode: single/side_by_side
        - zoom_level: Current zoom factor
        - is_fullscreen: Fullscreen state
        - is_presentation: Presentation mode state

Presenter Layer
---------------

**Base Presenter**

Abstract base class for all presenters:

.. code-block:: text

    BasePresenter
    ├── View attachment
    ├── Model management
    ├── Update coordination
    └── Cleanup handling

**Document Presenter**

Handles PDF document operations:

* Document loading and validation
* Page rendering coordination
* Error handling and reporting
* Qt PDF document management

**Margin Presenter**

Manages margin calculations:

* Document type-specific margins
* Spine width calculations
* Overlay visibility control
* Margin geometry calculations

**Navigation Presenter**

Controls page navigation:

* Page movement logic
* View mode management
* Navigation bounds checking
* Page pair calculations

View Layer
----------

**Main Window**

Central application window:

.. code-block:: text

    MainWindow (QMainWindow)
    ├── Component initialization
    ├── Presenter coordination
    ├── Event handling
    └── Resource management

**Page Item**

Individual PDF page rendering with advanced zoom support:

.. code-block:: text

    PageItem (QGraphicsItem)
    ├── Dynamic rendering based on zoom level
    ├── Progressive rendering (instant preview + delayed high quality)
    ├── Intelligent render caching with LRU eviction
    ├── Viewport-based partial rendering
    ├── High-quality rendering up to 200x zoom
    └── Memory-efficient buffer management

Component Architecture
======================

UI Components
-------------

The view layer is composed of specialized components, each handling a specific aspect:

**Window Components:**

* ``WindowSetup``: Initialization and configuration
* ``MenuBuilder``: Menu bar construction
* ``ToolbarBuilder``: Toolbar creation and management
* ``SignalConnections``: Signal-slot connection management

**Navigation Components:**

* ``NavigationController``: Centralized navigation control
* ``ScrollManager``: View scrolling coordination
* ``PagePositions``: Page position calculations
* ``PageSpinBox``: Custom page number input

**Rendering Components:**

* ``PageRenderer``: Page rendering coordination
* ``MarginRenderer``: Margin and overlay rendering
* ``GraphicsView``: Custom QGraphicsView with enhanced zoom/pan
* ``ZoomController``: Advanced zoom operations with mouse-centered zoom

**State Management:**

* ``UIStateManager``: Presentation and fullscreen modes
* ``ToggleManager``: UI toggle operations
* ``DialogManager``: Dialog handling
* ``CleanupCoordinator``: Resource cleanup

Rendering Strategies
--------------------

Different strategies for various view modes:

.. code-block:: text

    BaseStrategy (Abstract)
    ├── SinglePageStrategy: One page at a time
    ├── PagePairStrategy: Two pages side-by-side
    ├── SideBySideStrategy: All pages in pairs
    └── AllPagesStrategy: All pages vertically

Margin Renderers
----------------

Document type-specific rendering:

.. code-block:: text

    BaseRenderer (Abstract)
    ├── InteriorRenderer: Simple margins
    ├── CoverRenderer: Spine and barcode
    └── DustjacketRenderer: Complex fold lines

Data Flow
=========

Model Update Flow
-----------------

.. code-block:: text

    1. User action triggers presenter method
    2. Presenter validates and updates model
    3. Model fires PropertyChangedEvent
    4. Observers (presenters) receive notification
    5. Presenters update their views
    6. Views refresh display

Document Loading Flow
---------------------

.. code-block:: text

    1. User opens PDF file
    2. DocumentPresenter validates file
    3. QPdfDocument loads PDF
    4. Document model updated with info
    5. Navigation presenter sets page bounds
    6. Page renderer creates page items
    7. Margin presenter calculates overlays
    8. View displays rendered content

View Mode Change Flow
---------------------

.. code-block:: text

    1. User toggles view mode
    2. Navigation presenter updates model
    3. View state model notifies observers
    4. Page renderer selects new strategy
    5. Strategy repositions pages
    6. Margin renderer updates overlays
    7. Scroll manager adjusts view

State Management
================

Property Change Notification
----------------------------

Models use property change events:

.. code-block:: python

    # Model notifies observers
    model.set_property("current_page", 5)
    
    # Presenter receives event
    def _on_model_changed(self, event: PropertyChangedEvent):
        if event.property_name == "current_page":
            self.update_view(page=event.new_value)

Batch Updates
-------------

For multiple related changes:

.. code-block:: python

    model.begin_batch_update()
    model.set_property("width", 100)
    model.set_property("height", 200)
    model.end_batch_update()  # Single notification

View Updates
------------

Views are updated through presenter calls:

.. code-block:: python

    # Presenter updates view
    if self._view:
        self._view.update_display(
            current_page=self._model.current_page,
            total_pages=self._model.page_count
        )

Performance Optimization
========================

Rendering Pipeline
------------------

Advanced multi-stage rendering approach:

1. **Zoom-Aware Rendering**:
   - Below 10x zoom: Full page rendering for best quality
   - Above 10x zoom: Viewport-based partial rendering
   - Progressive rendering: Low-quality preview during zoom, high-quality after

2. **Intelligent Caching**:
   - LRU cache for rendered regions
   - Configurable memory limits (300MB default)
   - Cache key includes scale and viewport coordinates
   - Predictive pre-rendering of adjacent areas

3. **Viewport Optimization**:
   - Only render visible area plus configurable buffer
   - Buffer size reduces at high zoom to maintain quality
   - Scene padding ensures smooth edge panning

4. **Quality Management**:
   - Snap to predefined zoom levels for better cache hits
   - Maximum useful scale capping (100x)
   - Presentation mode always uses full quality

Memory Management
-----------------

Enhanced resource optimization:

* **Render Cache Management**:
  - Maximum 20 cached regions per page
  - Automatic eviction when memory limit reached
  - Proper cleanup of QImage resources

* **Timer Management**:
  - QTimer cleanup with deleteLater()
  - Scene validity checks before rendering
  - Prevents memory leaks from orphaned timers

* **Progressive Rendering**:
  - Deferred high-quality renders (150ms delay)
  - Cancellable render queue
  - Memory-safe image scaling

* **Buffer Optimization**:
  - Dynamic buffer sizing based on zoom level
  - Reduces memory usage at extreme zoom levels
  - Maintains visual quality during panning

Scene Graph Efficiency
----------------------

Qt's scene graph automatically provides:

* Efficient bounding box queries
* Fast viewport intersection tests
* Optimized item selection
* Automatic culling of invisible items

Error Handling
==============

Exception Hierarchy
-------------------

.. code-block:: text

    Exception
    └── MomovuError
        ├── DocumentError
        │   ├── DocumentLoadError
        │   ├── DocumentNotLoadedError
        │   └── InvalidPageError
        ├── RenderingError
        │   ├── PageRenderError
        │   └── ViewModeError
        ├── ConfigurationError
        │   ├── InvalidConfigError
        │   └── MissingConfigError
        ├── FileOperationError
        │   ├── FileNotFoundError
        │   └── FileAccessError
        └── ValidationError
            ├── InvalidDocumentTypeError
            └── InvalidDimensionError

Error Recovery
--------------

Graceful error handling:

* User-friendly error dialogs
* Detailed logging for debugging
* Fallback to safe defaults
* State preservation on errors

Threading Model
===============

Main Thread Only
----------------

Momovu uses a single-threaded model:

* All operations on main/GUI thread
* Qt event loop handles responsiveness
* No threading complexity
* Predictable execution order

Benefits:

* Simplified debugging
* No synchronization issues
* Direct UI updates
* Qt signal/slot safety

Testing Architecture
====================

Test Structure
--------------

Comprehensive test coverage:

.. code-block:: text

    tests/
    ├── Unit Tests
    │   ├── test_models.py
    │   ├── test_presenters.py
    │   ├── test_validators.py
    │   └── test_utils.py
    ├── Integration Tests
    │   ├── test_integration_document_loading.py
    │   ├── test_integration_navigation_flow.py
    │   └── test_integration_rendering_pipeline.py
    └── Component Tests
        ├── test_main_window_refactoring.py
        ├── test_navigation_refactoring.py
        └── test_document_operations.py

Test Approach
-------------

* **Unit Tests**: Individual class functionality
* **Integration Tests**: Component interaction
* **UI Tests**: User interface behavior
* **Fixtures**: Reusable test components

Code Organization
=================

Directory Structure
-------------------

.. note::
   For the most current project structure, run ``tree src/momovu/`` in the project root.

The project follows an MVP (Model-View-Presenter) architecture:

.. code-block:: text

    src/momovu/
    ├── __init__.py
    ├── main.py                    # Application entry point
    ├── models/                    # Data models (MVP Model layer)
    │   ├── __init__.py
    │   ├── base.py               # Base model with property notifications
    │   ├── document.py           # PDF document model
    │   ├── margin_settings.py    # Margin configuration model
    │   └── view_state.py         # View state model
    ├── presenters/                # Business logic (MVP Presenter layer)
    │   ├── __init__.py
    │   ├── base.py               # Base presenter interface
    │   ├── document.py           # Document operations presenter
    │   ├── margin.py             # Margin calculations presenter
    │   └── navigation.py         # Navigation logic presenter
    ├── views/                     # UI components (MVP View layer)
    │   ├── __init__.py
    │   ├── main_window.py        # Main application window
    │   ├── page_item.py          # PDF page graphics item
    │   └── components/           # Specialized UI components
    │       ├── __init__.py
    │       ├── page_strategies/  # Rendering strategy patterns
    │       │   ├── base.py
    │       │   ├── single_page.py
    │       │   ├── page_pair.py
    │       │   ├── side_by_side.py
    │       │   └── all_pages.py
    │       ├── renderers/        # Document-specific margin renderers
    │       │   ├── base.py
    │       │   ├── interior.py
    │       │   ├── cover.py
    │       │   └── dustjacket.py
    │       └── [20+ component files for specific UI functionality]
    └── lib/                       # Shared utilities and helpers
        ├── __init__.py
        ├── config.py             # Configuration management
        ├── constants.py          # Application constants
        ├── error_dialog.py       # Error handling UI
        ├── exceptions.py         # Custom exception hierarchy
        ├── icon_theme.py         # Icon theme configuration
        ├── logger.py             # Logging configuration
        ├── shortcuts_dialog.py   # Keyboard shortcuts dialog
        ├── types.py              # Type definitions
        ├── utils.py              # Utility functions
        └── validators.py         # Input validation

Module Responsibilities
-----------------------

* **models/**: Pure data storage with property change notifications, no UI dependencies
* **presenters/**: Business logic and coordination between models and views, no Qt widgets
* **views/**: Qt UI components with minimal logic, delegates to presenters
* **views/components/**: Specialized UI components with single responsibilities
* **lib/**: Shared utilities, constants, and helper functions

Design Decisions
================

MVP Over MVC
------------

Chose MVP pattern because:

* Better testability (presenters are UI-agnostic)
* Clear separation of concerns
* Easier to mock views for testing
* More suitable for desktop applications

Component-Based UI
------------------

Benefits of component architecture:

* Single responsibility per component
* Easy to test individual components
* Reusable across different contexts
* Simplified maintenance

Strategy Pattern for Rendering
------------------------------

Advantages:

* Easy to add new view modes
* Clean separation of rendering logic
* Runtime strategy selection
* Consistent interface


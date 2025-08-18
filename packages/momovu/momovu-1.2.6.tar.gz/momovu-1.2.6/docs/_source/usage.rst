=====
Usage
=====

Momovu provides a comprehensive set of tools for previewing and analyzing PDF margins. This guide covers
all features, command-line options, and keyboard shortcuts.

Quick Start
===========

Basic usage:

.. code-block:: bash

    # Open a PDF file
    momovu document.pdf


.. figure:: _static/screenshots/basic-usage.png
   :align: center
   :alt: Basic momovu window with interior PDF
   :width: 80%

   Basic momovu window with interior PDF

.. code-block:: bash

    # Specify document type and page count
    momovu -d cover -n 300 book.pdf

    # Enable side-by-side view for interior documents
    momovu -s interior.pdf

Command Line Interface
======================

Synopsis
--------

.. code-block:: bash

    momovu [-h] [-D] [-v] [-V] [-n N] [-d TYPE] [-s] [-m | --safety-margins | --no-safety-margins]
           [-t | --trim-lines | --no-trim-lines] [-b | --barcode | --no-barcode]
           [-l | --fold-lines | --no-fold-lines] [-r | --bleed-lines | --no-bleed-lines]
           [-p] [-f]
           [PDF_FILE]

Arguments
---------

**Positional Arguments:**

* ``PDF_FILE`` - Path to the PDF file to preview (optional)

**Optional Arguments:**

* ``-h, --help`` - Show help message and exit
* ``-D, --debug`` - Enable debug logging for troubleshooting
* ``-v, --verbose`` - Increase output verbosity (can be used multiple times: -v, -vv, -vvv)
* ``-V, --version`` - Show version information and exit
* ``-n N, --num-pages N`` - Number of pages for spine width calculation
* ``-d TYPE, --document TYPE`` - Document type: interior, cover, or dustjacket (default: interior)
* ``-s, --side-by-side`` - Start in side-by-side view mode (interior documents only)
* ``-m, --safety-margins, --no-safety-margins`` - Show safety margins (default: enabled)
* ``-t, --trim-lines, --no-trim-lines`` - Show trim lines (default: enabled)
* ``-b, --barcode, --no-barcode`` - Show barcode area for cover/dustjacket (default: enabled)
* ``-l, --fold-lines, --no-fold-lines`` - Show fold lines for cover/dustjacket (default: enabled)
* ``-r, --bleed-lines, --no-bleed-lines`` - Show bleed lines for cover/dustjacket (default: enabled)
* ``-p, --presentation`` - Start in presentation mode
* ``-f, --fullscreen`` - Start in fullscreen mode

Examples
--------

.. code-block:: bash

    # Preview an interior PDF with default settings
    momovu book-interior.pdf

    # Preview a cover with 300 pages (affects spine width)
    momovu -d cover -n 300 book-cover.pdf

    # Preview a dustjacket with specific page count
    momovu -d dustjacket -n 442 book-dustjacket.pdf

    # View interior pages in side-by-side mode
    momovu -s book-interior.pdf

    # Enable debug logging for troubleshooting
    momovu --debug problematic-file.pdf

    # Increase verbosity for more detailed output
    momovu -vv document.pdf

Keyboard Shortcuts
==================

Navigation
----------

* ``Page Up`` - Go to previous page
* ``Page Down`` - Go to next page
* ``Home`` - Go to first page (interior documents only)
* ``End`` - Go to last page (interior documents only)
* ``Arrow Keys`` - Pan the view when zoomed in
* ``Mouse Wheel`` - Scroll vertically when zoomed in (or navigate pages when zoomed out)
* ``Shift+Mouse Wheel`` - Scroll horizontally when zoomed in
* ``Space`` - Next page (in presentation mode)
* ``Backspace`` - Previous page (in presentation mode)

View Controls
-------------

* ``Ctrl+Plus/=`` - Zoom in (10% increment)
* ``Ctrl+Minus`` - Zoom out (10% decrement)
* ``Ctrl+0`` - Fit page to window
* ``Ctrl+Mouse Wheel`` - Zoom in/out at mouse cursor position

.. figure:: _static/screenshots/zoomed-in.png
   :align: center
   :alt: Zoomed in view
   :width: 80%

   Zoomed in view showing detail of the page content with high-quality rendering

* ``F11`` - Toggle fullscreen mode
* ``F5`` - Toggle presentation mode
* ``Escape`` - Exit presentation mode

Zoom and Pan Behavior
---------------------

**When zoomed out (fit to page):**

* ``Mouse Wheel`` - Navigate between pages
* ``Ctrl+Mouse Wheel`` - Zoom in/out at cursor position

**When zoomed in:**

* ``Mouse Wheel`` - Pan vertically (scroll up/down)
* ``Shift+Mouse Wheel`` - Pan horizontally (scroll left/right)
* ``Ctrl+Mouse Wheel`` - Zoom in/out at cursor position
* ``Arrow Keys`` - Pan in any direction

The zoom system features:

* **High-quality rendering** at all zoom levels (up to 200x)
* **Progressive rendering** for smooth zoom experience
* **Intelligent caching** for instant panning
* **Mouse-centered zoom** for precise control

Display Options
---------------

* ``Ctrl+D`` - Toggle side-by-side view (interior documents only)
* ``Ctrl+T`` - Toggle trim lines visibility
* ``Ctrl+M`` - Toggle safety margins visibility
* ``Ctrl+L`` - Toggle spine/fold lines visibility
* ``Ctrl+B`` - Toggle barcode area (cover/dustjacket only)
* ``Ctrl+R`` - Toggle bleed lines (cover/dustjacket only)

File Operations
---------------

* ``Ctrl+O`` - Open a new PDF file
* ``Ctrl+W`` - Close current document
* ``Ctrl+G`` - Go to page dialog
* ``Ctrl+Q`` - Quit application

Menu System
===========

File Menu
---------

* **Open** (Ctrl+O) - Open a new PDF file
* **Close** (Ctrl+W) - Close the current document
* **Quit** (Ctrl+Q) - Exit the application

View Menu
---------

**Zoom Controls:**

* **Zoom In** (Ctrl+Plus) - Increase zoom level by 10%
* **Zoom Out** (Ctrl+Minus) - Decrease zoom level by 10%
* **Fit to Page** (Ctrl+0) - Fit entire page in window
* **Mouse Wheel Zoom** (Ctrl+Mouse Wheel) - Smooth zoom at cursor position

**Display Modes:**

* **Fullscreen** (F11) - Toggle fullscreen mode
* **Presentation Mode** (F5) - Enter/exit presentation mode
* **Side-by-Side View** (Ctrl+D) - Toggle dual page view (interior only)

**Overlays:**

* **Show Trim Lines** (Ctrl+T) - Toggle trim line visibility
* **Show Safety Margins** (Ctrl+M) - Toggle margin visibility
* **Show Spine Line** (Ctrl+L) - Toggle spine/fold lines
* **Show Barcode Area** (Ctrl+B) - Toggle barcode area (cover/dustjacket)
* **Show Bleed Lines** (Ctrl+R) - Toggle bleed lines (cover/dustjacket)

**Navigation:**

* **Go to Page...** (Ctrl+G) - Open page navigation dialog

Document Menu
-------------

* **Interior Document** - Set margins for interior pages
* **Cover Document** - Set margins for book covers
* **Dustjacket Document** - Set margins for dustjackets

Help Menu
---------

* **Keyboard Shortcuts** - Display all keyboard shortcuts in a dialog
* **About Momovu** - Show application information and version

Document Types
==============

Interior Documents
------------------

Interior documents represent the content pages of a book:

* Simple rectangular safety margins
* Side-by-side view available for spread preview
* Spine line visible in dual-page mode
* Navigation to first/last page enabled

.. code-block:: bash

    momovu -d interior book-content.pdf
    
    # With side-by-side view
    momovu -d interior -s book-content.pdf


.. figure:: _static/screenshots/interior-single.png
   :align: center
   :alt: Interior document in single page view
   :width: 80%

   Interior document displayed in single page view mode

Cover Documents
---------------

Cover documents include front and back covers with spine:

* Spine width automatically calculated from page count
* Barcode placement area in lower right of back cover
* Fold lines at spine edges (green dashed lines)
* Safety margins with bleed areas

.. code-block:: bash

    momovu -d cover -n 300 book-cover.pdf


.. figure:: _static/screenshots/cover-spine.png
   :align: center
   :alt: Cover document showing spine width calculation
   :width: 80%

   Cover document with automatically calculated spine width based on page count

.. figure:: _static/screenshots/cover-margins.png
  :align: center
  :alt: Cover document with safety margins
  :width: 80%

  Cover document showing safety margins and bleed areas

**Spine Width Calculation:**

* Formula: (pages / 17.48) + 1.524 mm
* Converted to points for display
* Example: 300 pages = 18.69 mm spine width

Dustjacket Documents
--------------------

Dustjackets include covers, spine, and flaps:

* Complete dustjacket layout visualization
* Fixed flap dimensions: 3.25" x 9" (82.55mm x 228.6mm)
* Multiple fold lines for all edges
* Separate margins for flaps and covers

.. code-block:: bash

    momovu -d dustjacket -n 500 book-dustjacket.pdf


.. figure:: _static/screenshots/dustjacket.png
   :align: center
   :alt: Dustjacket with flaps and fold lines
   :width: 80%

   Complete dustjacket layout with flaps, spine, fold lines, and bleed lines visible

.. figure:: _static/screenshots/dustjacket-bleed-lines.png
  :align: center
  :alt: Dustjacket with bleed lines
  :width: 80%

  Dustjacket showing bleed lines that extend beyond trim lines for print production

Presentation Mode
=================

Presentation mode provides a distraction-free view:

* Full-screen display without UI elements
* Maintains current view mode and overlays
* Smooth page-by-page navigation
* Exit with F5 or Escape

Navigation in presentation mode:

* ``Page Down`` or ``Space`` - Next page
* ``Page Up`` or ``Backspace`` - Previous page  
* ``Arrow Keys`` - Pan view if zoomed
* ``F5`` or ``Escape`` - Exit presentation mode


.. figure:: _static/screenshots/presentation-mode.png
   :align: center
   :alt: Presentation mode (fullscreen, no UI)
   :width: 80%

   Presentation mode showing pages in fullscreen without any UI elements

Starting presentation mode:

* Press ``F5`` while viewing a document
* All overlay toggles remain functional

Fullscreen Mode
===============

Fullscreen mode maximizes the window:

* Window fills entire screen
* Menus and toolbars remain accessible
* Different from presentation mode
* Toggle with ``F11``


.. figure:: _static/screenshots/fullscreen-mode.png
   :align: center
   :alt: Fullscreen mode (maximized window)
   :width: 80%

   Fullscreen mode with maximized window while keeping menus and toolbars visible

Side-by-Side View
=================

Side-by-side view displays interior pages as spreads:

* First page displayed alone (right side)
* Subsequent pages in proper left/right pairs
* Spine line visualization between pages
* Maintains reading order

Toggle with ``Ctrl+D`` or via View menu (interior documents only).

.. figure:: _static/screenshots/side-by-side.png
   :align: center
   :alt: Interior pages in side-by-side view
   :width: 80%

   Interior pages displayed as a book spread in side-by-side view


Visual Overlays
===============

.. figure:: _static/screenshots/overlay-all.png
   :align: center
   :alt: All overlays enabled simultaneously
   :width: 80%

   All visual overlays enabled together showing trim lines, safety margins, fold lines, barcode area, and bleed lines

Safety Margins
--------------

Safety margins indicate the safe content area:

* **Appearance**: Semi-transparent blue/purple overlay (#7F7FC1)
* **Default Size**: 12.7mm (0.5 inches)
* **Purpose**: Show printable area safe from trimming
* **Toggle**: ``Ctrl+M``


.. figure:: _static/screenshots/overlay-safety-margins.png
   :align: center
   :alt: Safety margins overlay enabled
   :width: 80%

   Safety margins overlay showing the safe content area

Trim Lines
----------

Trim lines show where pages will be cut:

* **Appearance**: Black solid lines at edges
* **Purpose**: Indicate final page dimensions
* **Essential for**: Bleed verification
* **Toggle**: ``Ctrl+T``


.. figure:: _static/screenshots/overlay-trim-lines.png
   :align: center
   :alt: Trim lines overlay enabled
   :width: 80%

   Trim lines showing where the page will be cut

Spine/Fold Lines
----------------

Document-specific spine indicators:

**Interior Documents:**
* Center spine line in side-by-side view
* Purple solid line between page pairs
* Toggle: ``Ctrl+L``

**Cover Documents:**
* Fold lines at spine edges
* Purple dashed lines
* Based on calculated spine width
* Toggle: ``Ctrl+L``

**Dustjacket Documents:**
* Multiple fold lines for all edges
* Purple dashed lines for all folds
* Separate margins for flaps (teal) and spine (olive)
* Toggle: ``Ctrl+L``

.. figure:: _static/screenshots/overlay-spine-lines.png
   :align: center
   :alt: Spine/fold lines overlay enabled
   :width: 80%

   Spine and fold lines indicating where the cover will be folded


Barcode Area
------------

Barcode placement indicator:

* **Location**: Lower right of back cover
* **Appearance**: Orange dash-dot rectangle with "BARCODE" label
* **Documents**: Cover and dustjacket only
* **Toggle**: ``Ctrl+B``


.. figure:: _static/screenshots/overlay-barcode.png
   :align: center
   :alt: Barcode area overlay enabled
   :width: 80%

   Barcode placement area on the back cover

Bleed Lines
-----------

Bleed lines show the actual page edges for cover and dustjacket documents:

* **Appearance**: Light blue solid lines (#22b5f0) at page edges
* **Purpose**: Show actual page boundaries (outside trim lines)
* **Documents**: Cover and dustjacket only
* **Toggle**: ``Ctrl+R``

Bleed lines appear at the actual page edges, while trim lines appear inside at the bleed offset:
* Cover documents: 3.18mm (1/8") bleed
* Dustjacket documents: 6.35mm (1/4") bleed

.. figure:: _static/screenshots/overlay-bleed-lines.png
   :align: center
   :alt: Bleed lines overlay enabled
   :width: 80%

   Bleed lines showing the actual page edges for print production

Go to Page Dialog
=================

Quick page navigation:

* **Open**: Ctrl+G or View → Go to Page...
* **Features**:
  - Shows current page and total pages
  - Input validation
  - Enter key navigates
  - Escape key cancels

Sample Files
============

The repository includes sample PDFs for testing:

* https://spacecruft.org/books/momovu/src/branch/main/samples

.. code-block:: bash

    # Interior document examples
    momovu -d interior samples/bovary-interior.pdf
    momovu -d interior -s samples/pingouins-interior.pdf

    # Cover examples with different page counts
    momovu -d cover -n 688 samples/bovary-cover.pdf
    momovu -d cover -n 126 samples/lovecraft-cover.pdf
    momovu -d cover -n 574 samples/pingouins-cover.pdf
    momovu -d cover -n 180 samples/quixote-cover.pdf
    momovu -d cover -n 100 samples/siddhartha-cover.pdf
    momovu -d cover -n 442 samples/vatican-cover.pdf

    # Dustjacket examples
    momovu -d dustjacket -n 688 samples/bovary-dustjacket.pdf
    momovu -d dustjacket -n 574 samples/pingouins-dustjacket.pdf
    momovu -d dustjacket -n 442 samples/vatican-dustjacket.pdf


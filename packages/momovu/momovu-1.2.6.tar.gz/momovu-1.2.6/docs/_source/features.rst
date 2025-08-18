========
Features
========

Momovu provides specialized tools for book publishers and designers to preview PDFs with professional margin visualization.

Document Type Support
=====================

Interior Pages
--------------

Preview your book's content pages with:

* **Safety margin visualization** - See exactly where content is safe from trimming
* **Spread view** - View pages side-by-side as readers will see them
* **Spine line indicator** - Visualize the book's center fold in spread view
* **Page navigation** - Jump to any page instantly

Cover Documents
---------------

Verify your book covers with:

* **Automatic spine width calculation** - Enter page count, see exact spine dimensions
* **Fold line indicators** - Know exactly where the spine edges will be
* **Barcode placement guide** - Standard barcode area visualization
* **Full cover preview** - See front, spine, and back as one unit

Dustjacket Documents
--------------------

Complete dustjacket visualization:

* **Flap dimensions** - Standard 3.25" x 9" flaps with safety margins
* **Multiple fold lines** - All fold positions clearly marked
* **Complete layout view** - See the entire dustjacket spread
* **Separate margin zones** - Different margins for flaps, covers, and spine

Visual Overlays
===============

.. figure:: _static/screenshots/cover-clean.png
   :align: center
   :alt: Cover document without overlays
   :width: 80%

   Cover document showing clean view without any overlays

Safety Margins
--------------

* **Blue/purple overlay** shows the safe content area (12.7mm / 0.5 inches)
* **Toggle on/off** with Ctrl+M to compare with and without margins
* **Semi-transparent** so you can see your content underneath

Trim Lines
----------

* **Black edge lines** show exactly where pages will be cut
* **Essential for bleed verification** - ensure images extend past trim
* **Toggle** with Ctrl+T

Fold Lines
----------

* **Purple dashed lines** indicate all fold positions
* **Document-specific** - spine folds for covers, all folds for dustjackets
* **Toggle** with Ctrl+L

Barcode Area
------------

* **Orange indicator** shows standard barcode placement (covers/dustjackets only)
* **Lower-right back cover** positioning
* **Toggle** with Ctrl+B

Bleed Lines
-----------

* **Light blue lines** show actual page edges (covers/dustjackets only)
* **Outside trim lines** - indicate full page boundaries for print production
* **Document-specific offsets** - 3.18mm for covers, 6.35mm for dustjackets
* **Toggle** with Ctrl+R

View Modes
==========

Single Page View
----------------

* **Detailed inspection** - Focus on one page at a time
* **Full zoom range** - From 10% to 1000%
* **Smooth navigation** - Page Up/Down to move through document

Side-by-Side View
-----------------

* **Book spread simulation** - See pages as they appear in print
* **Proper page pairing** - First page alone, then left/right spreads
* **Interior documents only** - Toggle with Ctrl+D

Presentation Mode
-----------------

* **Distraction-free review** - Full screen with no UI elements
* **Maintains overlays** - All margin visualizations remain active
* **Quick navigation** - Page Down/Space for next, Page Up for previous
* **Exit anytime** - Press F5 or Escape

Navigation
==========

Keyboard Shortcuts
------------------

**Essential shortcuts for efficient work:**

* **Ctrl+O** - Open a new PDF
* **Ctrl+G** - Go to specific page
* **Ctrl+Plus/Minus** - Zoom in/out
* **Ctrl+0** - Fit page to window
* **Ctrl+R** - Toggle bleed lines (cover/dustjacket)
* **Ctrl+K** - Open spine width calculator
* **F11** - Fullscreen mode
* **F5** - Presentation mode

Page Navigation
---------------

* **Page spinbox** in toolbar for direct page access
* **Home/End keys** for first/last page (interior documents)
* **Mouse wheel** for scrolling through pages
* **Go to Page dialog** (Ctrl+G) with validation

Zoom Control
------------

* **Mouse-centered zoom** - Zooms at cursor position for precise control
* **High-quality rendering** - No pixelation even at extreme zoom levels (up to 200x)
* **Progressive rendering** - Smooth zoom experience with instant preview
* **Ctrl+Mouse wheel** for smooth zoom with 10% increments
* **Smart panning when zoomed** - Mouse wheel scrolls vertically, Shift+wheel scrolls horizontally
* **Fit to page** automatically sizes content to window
* **Zoom persists** when navigating pages
* **Optimized performance** - Intelligent caching for smooth panning at any zoom level

.. figure:: _static/screenshots/zoomed-margin-detail.png
   :align: center
   :alt: Zoomed view showing margin detail
   :width: 80%

   Zoomed in view showing fine detail of safety margins on a cover

Professional Publishing Features
================================

Spine Width Calculation
-----------------------

* **Automatic calculation** from page count
* **Industry-standard** spine dimensions
* **Real-time updates** when page count changes
* **Dedicated calculator tool** - Access via Document → Spine Width Calculator (Ctrl+K)
* **Support for both covers and dustjackets**
* **Minimum spine width** - 6.35mm (0.25") for covers

Multiple Document Support
-------------------------

* **Quick document type switching** via Document menu
* **Preserves settings** when changing between interior/cover/dustjacket
* **Optimized layouts** for each document type


.. figure:: _static/screenshots/dustjacket-trim-fold.png
   :align: center
   :alt: Dustjacket showing trim lines and fold lines
   :width: 80%

   Dustjacket with trim lines and fold lines visible for precise cutting and folding

Quality Control Tools
=====================

Visual Verification
-------------------

* **Toggle overlays independently** - Compare with/without each overlay
* **High contrast indicators** - Clear visibility of all guides
* **Zoom to details** - Inspect specific areas closely

Print Preparation
-----------------

* **Bleed verification** - Ensure images extend past trim lines
* **Margin compliance** - Confirm all text is within safe areas
* **Spine text check** - Verify spine content fits within width
* **Barcode clearance** - Ensure barcode area is unobstructed

Performance
===========

* **Handles large PDFs** smoothly regardless of page count
* **Efficient rendering** - Only visible pages are processed
* **Fast navigation** - No lag when jumping between pages
* **Advanced zoom rendering** - High-quality display at all zoom levels
* **Intelligent caching** - Recently viewed areas cached for instant panning
* **Progressive rendering** - Low-quality preview during zoom, high-quality after
* **Memory-efficient** - Smart cache management prevents excessive memory use
* **Presentation mode optimization** - Always uses full quality rendering

.. figure:: _static/screenshots/interior-margins.png
   :align: center
   :alt: Interior pages showing safety margins
   :width: 80%

   Interior pages in side-by-side view with safety margins visible
===========================
Preferences & Configuration
===========================

Momovu provides a comprehensive preferences system that allows you to customize the application's behavior and appearance to suit your workflow.

Accessing Preferences
=====================

The Preferences dialog can be accessed in two ways:

1. From the menu: **File** → **Preferences...**
2. Using the keyboard shortcut: ``Ctrl+,`` (Ctrl+comma)

.. image:: _static/screenshots/preferences-dialog.png
   :alt: Preferences dialog showing configuration options
   :align: center
   :width: 500px

Configuration Options
=====================

The Preferences dialog is organized into three tabs for easy navigation:

General Tab
-----------

The General tab contains the main application settings:

.. image:: _static/screenshots/preferences-dialog.png
   :alt: Preferences dialog General tab
   :align: center
   :width: 500px

**Fit Options**
   - **Auto-fit on document load**: Automatically fit the page to the window when opening a PDF
   - **Auto-fit on window resize**: Maintain page fit when resizing the application window

**Zoom Settings**
   - **Zoom Increment**: Control how much the zoom changes with each Ctrl+Plus/Minus press (1.05x to 2.00x)

**Scrolling**
   - **Enable smooth scrolling**: Use animated transitions when scrolling through pages
   - **Scroll Speed**: Adjust the scrolling speed in pixels (10-200)

**Performance**
   - **Max Cached Pages**: Number of pages to keep in memory for faster navigation (5-100)
   - **Max Cache Memory**: Maximum memory allocation for page cache in MB (50-1000)

Colors Tab
----------

The Colors tab allows customization of all overlay colors and line widths:

.. image:: _static/screenshots/preferences-colors.png
   :alt: Preferences dialog Colors tab
   :align: center
   :width: 500px

**Overlay Colors and Opacity**
   - **Margin Overlay**: Color and transparency for safety margin areas
   - **Barcode Area**: Color and transparency for barcode placement guide
   - **Fold Lines**: Color and transparency for spine/fold line indicators
   - **Trim Lines**: Color and transparency for page trim boundaries
   - **Bleed Lines**: Color and transparency for bleed area indicators

**Line Widths**
   - Adjust the thickness of fold, trim, and bleed lines (1-10 pixels)

**Colorblind Presets**
   Three preset buttons provide optimized color schemes:
   - **Protanopia**: Optimized for red-blind vision
   - **Deuteranopia**: Optimized for green-blind vision
   - **Tritanopia**: Optimized for blue-blind vision

Recent Files Tab
----------------

The Recent Files tab manages your file history:

.. image:: _static/screenshots/preferences-recent-files.png
   :alt: Preferences dialog Recent Files tab
   :align: center
   :width: 500px

**File Management**
   - View all recently opened PDF files with their document types
   - **Remove Selected**: Remove individual files from the history
   - **Clear All Recent Files**: Clear the entire recent files list

Configuration File Location
===========================

Momovu stores its configuration using Qt's QSettings system:

- **Linux**: ``~/.config/Momovu/Momovu.conf``
- **Windows**: Registry under ``HKEY_CURRENT_USER\Software\Momovu\Momovu``
- **macOS**: ``~/Library/Preferences/com.momovu.Momovu.plist``

The configuration is managed automatically by the application.

Resetting to Defaults
=====================

To reset all preferences to their default values:

1. Open the Preferences dialog (``Ctrl+,``)
2. Click the **Restore Defaults** button at the bottom (shown in red)
3. Confirm the reset when prompted
4. A message will confirm that settings have been reset

Command-Line Overrides
=======================

Many preferences can be overridden via command-line arguments, which take precedence over saved preferences:

.. code-block:: bash

   # Override default visibility of overlays
   momovu --no-safety-margins document.pdf
   momovu --no-trim-lines document.pdf
   
   # Override document type
   momovu --document cover book.pdf
   
   # Start in specific modes
   momovu --presentation document.pdf
   momovu --fullscreen document.pdf

Per-Document Settings
=====================

The following settings are remembered for each document in the recent files list:

- Last viewed page
- Zoom level
- View mode (single/side-by-side)
- Document type
- Overlay visibility states
- Presentation mode state

These are restored when you reopen the same document from the recent files list.
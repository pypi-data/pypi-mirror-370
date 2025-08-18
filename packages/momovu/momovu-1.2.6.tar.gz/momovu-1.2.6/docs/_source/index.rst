======
Momovu
======

**Preview book PDFs before print and publication**

Momovu is a PDF margin visualization tool designed for publishers and book designers.
It provides real-time preview of safety margins, spine widths, and dustjacket layouts to ensure
proper formatting before sending books to print.

* **Website**: https://momovu.org
* **Source Code**: https://spacecruft.org/books/momovu

.. raw:: html

   <div style="text-align: center; margin: 20px 0;">
     <p><strong>Watch Momovu in action:</strong></p>
     <video width="90%" controls>
       <source src="_static/momovu_demo.webm" type="video/webm">
       Your browser does not support the video tag.
     </video>
     <p><em>Video showcasing document types and features</em></p>
   </div>

.. figure:: _static/screenshots/showcase-index.png
   :align: center
   :alt: Momovu showcasing dustjacket with all features
   :width: 90%

   Momovu displaying a dustjacket with all visual overlays

Key Features
============

* **Multiple Document Types**: Support for interior pages, covers, and dustjackets
* **Interactive Navigation**: Zoom, pan, and navigate through pages with ease
* **Presentation Mode**: Full-screen presentation for reviewing layouts
* **Side-by-Side View**: View pages in spreads as they would appear in print
* **Configurable Margins**: Customizable safety margins and spine dimensions
* **Visual Overlays**: Toggle trim lines, safety margins, fold lines, barcode areas, and bleed lines
* **Performance Optimized**: Efficient rendering with viewport culling and scene management

Document Types
==============

Interior Pages
--------------
* Preview safety margins for book content
* Side-by-side spread view
* Spine line visualization in dual-page mode

Covers
------
* Front and back cover visualization
* Spine width calculation based on page count
* Barcode area placement
* Fold line indicators

Dustjackets
-----------
* Complete dustjacket layout preview
* Flap dimensions and safety margins
* Spine width with bleed areas
* Fold lines for all edges

.. toctree::
   :maxdepth: 1
   :caption: User Guide:

   about
   features
   install
   usage
   preferences
   spine_width_calculator

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide:

   development
   architecture
   api

.. toctree::
   :maxdepth: 1
   :caption: Reference:

   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

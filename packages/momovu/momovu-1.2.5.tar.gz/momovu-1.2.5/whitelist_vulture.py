"""
Vulture whitelist for momovu project.

This file contains false positives that vulture reports as dead code
but are actually used by the Qt framework or other external systems.
"""

# ruff: noqa: F821, B018

# Qt method overrides that are called by the framework
_.wheelEvent  # unused method (src/momovu/views/components/graphics_view.py:226)
_.paint  # unused method (src/momovu/views/page_item.py:93)
widget  # unused variable (src/momovu/views/page_item.py:97)

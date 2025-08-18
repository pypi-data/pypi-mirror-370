===========
Development
===========

This guide covers setting up a development environment for Momovu, coding standards, testing procedures,
and contribution guidelines.

Development Setup
=================

Prerequisites
-------------

* Python 3.9 or higher
* Git
* A code editor
* Basic knowledge of Python and Qt/PySide6

Setting Up the Environment
--------------------------

1. Clone the repository:

.. code-block:: bash

    git clone https://spacecruft.org/books/momovu
    cd momovu/

2. Create a virtual environment:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate

3. Install in development mode with all dependencies:

.. code-block:: bash

    pip install -U setuptools pip wheel
    pip install -e .
    pip install -e .[dev,test,docs]

This installs:

* Core application dependencies
* Development tools (formatters, linters)
* Testing frameworks
* Documentation builders

Project Structure
=================

The project follows an MVP (Model-View-Presenter) architecture. For the detailed project structure and module organization, see the :doc:`architecture` documentation.

Key directories:

* ``src/momovu/`` - Main application source code
* ``tests/`` - Test suite with unit and integration tests
* ``docs/`` - Sphinx documentation source and build
* ``samples/`` - Sample PDF files for testing

Code Style
==========

Formatting
----------

We use **black** for consistent code formatting:

.. code-block:: bash

    # Format all Python files
    black src/momovu/

    # Check formatting without changes
    black --check src/momovu/

Black configuration in ``pyproject.toml``:

* Line length: 88 characters
* Target Python version: 3.9+

Linting
-------

We use **ruff** for fast, comprehensive linting:

.. code-block:: bash

    # Run linter
    ruff check src/momovu/

    # Fix auto-fixable issues
    ruff check --fix src/momovu/

Ruff checks for:

* Pycodestyle errors (E) and warnings (W)
* Pyflakes issues (F)
* Import sorting (I)
* Bugbear patterns (B)
* Comprehension improvements (C4)
* Code upgrades (UP)
* Unused arguments (ARG)
* Simplifications (SIM)

Type Checking
-------------

We use **mypy** for static type checking:

.. code-block:: bash

    # Run type checker
    mypy src/momovu/

Type hints should be used for:

* Function parameters and return values
* Class attributes
* Complex data structures

Example:

.. code-block:: python

    from typing import Optional, List, Tuple

    def calculate_margin(
        page_size: Tuple[float, float],
        margin_mm: float = 3.175
    ) -> Optional[List[float]]:
        """Calculate margins for a page."""
        ...

Testing
=======

Running Tests
-------------

We use **pytest** for testing:

.. code-block:: bash

    # Run all tests
    pytest

    # Run with coverage
    pytest --cov=src/momovu --cov-report=html

    # Run specific test file
    pytest tests/test_viewer.py

    # Run tests matching pattern
    pytest -k "margin"

    # Run with verbose output
    pytest -v

Test Categories
---------------

Tests are organized by type:

* **Unit tests** - Test individual functions and classes
* **Integration tests** - Test component interactions
* **UI tests** - Test Qt/PySide6 interfaces using pytest-qt

Writing Tests
-------------

Example test structure:

.. code-block:: python

    import pytest
    from momovu.lib.margin_manager import MarginManager

    class TestMarginManager:
        """Test margin calculations."""

        @pytest.fixture
        def manager(self):
            """Create a margin manager instance."""
            return MarginManager()

        def test_safety_margin_default(self, manager):
            """Test default safety margin value."""
            assert manager.safety_margin_mm == 3.175

        def test_calculate_spine_width(self, manager):
            """Test spine width calculation."""
            width = manager.calculate_spine_width(300)
            assert width > 0

Test Coverage
-------------

Maintain high test coverage:

.. code-block:: bash

    # Generate coverage report
    pytest --cov=src/momovu --cov-report=term-missing

    # Generate HTML coverage report
    pytest --cov=src/momovu --cov-report=html
    # Open htmlcov/index.html in browser

Building
========

Building Wheels
---------------

Create distribution packages:

.. code-block:: bash

    # Install build tools
    pip install build

    # Build wheel and source distribution
    python -m build

    # Output in dist/ directory
    ls dist/
    # momovu-*.whl
    # momovu-*.tar.gz

Version Management
------------------

Version is managed by ``setuptools_scm`` from git tags:

.. code-block:: bash

    # Create a new version
    git tag v1.2.3
    git push origin v1.2.3

    # Build with version
    python -m build

Documentation
=============

Building Documentation
----------------------

Documentation uses Sphinx:

.. code-block:: bash

    # Install documentation dependencies
    pip install -e .[docs]

    # Build HTML documentation
    make clean
    make html

    # View documentation
    xdg-open docs/_build/html/index.html  # Linux

Writing Documentation
---------------------

Documentation is written in reStructuredText:

* User guides in ``docs/_source/``
* API docs auto-generated from docstrings

Example docstring:

.. code-block:: python

    def load_pdf(self, path: str) -> bool:
        """Load a PDF file for viewing.
        
        Args:
            path: Path to the PDF file
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            PDFError: If the PDF is corrupted or invalid
            
        Example:
            >>> viewer = PDFViewer()
            >>> viewer.load_pdf("document.pdf")
            True
        """

Debugging
=========

Debug Mode
----------

Run with debug logging:

.. code-block:: bash

    # Command line
    momovu --debug document.pdf

    # Environment variable
    export MOMOVU_DEBUG=1
    momovu document.pdf

Resources
=========

* **Source Code**: https://spacecruft.org/books/momovu
* **Documentation**: https://momovu.org
* **PyPI Package**: https://pypi.org/project/momovu/
============
Installation
============

This guide covers installation of Momovu on Linux systems.

System Requirements
===================

Minimum Requirements
--------------------

* **Operating System**: Linux
* **Python**: 3.9 or higher
* **RAM**: 4 GB minimum, 8 GB recommended
* **Disk Space**: 500 MB for installation
* **Display**: 1280x720 minimum resolution

Recommended Requirements
------------------------

* **Operating System**: Latest stable release of your Linux distribution
* **Python**: 3.10 or higher
* **RAM**: 8 GB or more
* **Disk Space**: 1 GB for installation and cache
* **Display**: 1920x1080 or higher resolution

Quick Install
=============

Using pip (Recommended)
------------------------

The simplest way to install Momovu:

.. code-block:: bash

    pip install momovu

To upgrade to the latest version:

.. code-block:: bash

    pip install --upgrade momovu

Installation Instructions
=========================

Linux (Debian)
--------------

1. Install system dependencies:

.. code-block:: bash

    sudo apt update
    sudo apt install python3-pip python3-venv python-is-python3
    sudo apt install libxcb-xinerama0 libxcb-cursor0  # Qt dependencies

2. Create a virtual environment (recommended):

.. code-block:: bash

    python3 -m venv ~/momovu-env
    source ~/momovu-env/bin/activate

3. Install Momovu:

.. code-block:: bash

    pip install --upgrade pip wheel setuptools
    pip install momovu

Install from Source
===================

For users who want the latest development version:

Clone the Repository
--------------------

.. code-block:: bash

    git clone https://spacecruft.org/books/momovu
    cd momovu/

Install the Application
------------------------

1. Create and activate a virtual environment:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate

2. Install in user mode:

.. code-block:: bash

    pip install --upgrade pip wheel setuptools
    pip install -e .

Verification
============

After installation, verify Momovu is working:

.. code-block:: bash

    # Check version
    momovu --version

    # Show help
    momovu --help

    # Test with a sample PDF (if available)
    momovu sample.pdf

Uninstallation
==============

To remove Momovu:

Using pip
---------

.. code-block:: bash

    pip uninstall momovu

Complete Removal
----------------

1. Uninstall the package:

.. code-block:: bash

    pip uninstall momovu

2. Remove virtual environment (if used):

.. code-block:: bash

    rm -rf ~/momovu-env

3. Remove configuration files (if any):

.. code-block:: bash

    rm -rf ~/.config/momovu

Next Steps
==========

After successful installation:

1. Read the :doc:`usage` guide to learn about features
2. Try the sample PDFs in the repository
3. Configure your preferred document types
4. Explore keyboard shortcuts for efficient workflow

For development setup, see :doc:`development`.
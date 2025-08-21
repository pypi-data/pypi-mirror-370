:sd_hide_title:
.. grid:: 1

    .. grid-item-card:: PyXMake as a poetry plugin

        Learn how to use PyXMake together with poetry
-----------------
Usage with poetry
-----------------

Installation
------------
You can install `PyXMake`_ and `poetry`_ directly by using pip:

.. code-block:: console

    $ pip install poetry pyxmake[poetry,lint]

.. important::

	PyXMake installs a backwards-compatible version of poetry and replaces the original executable. 
	If PyXMake is uninstalled, poetry must be reinstalled.

Usage
-----
To verify that the installation was successful, use

.. code-block:: console

	$ poetry debug info
	==================================
	Running poetry with PyXMake plugin
	==================================

	Poetry
	Version: 1.8.3
	Python:  3.10.14

	Virtualenv
	Python:         3.10.14
	Implementation: CPython
	Valid:          True

	Base
	Platform:   win32
	OS:         nt
	Python:     3.10.14

A reference to the use of `PyXMake`_ with `poetry`_ as well as a summary of the current system information should appear.

.. _PyXMake: https://pypi.org/project/pyxmake
.. _poetry: https://python-poetry.org/docs/
.. toctree::
   :hidden:
   
   self
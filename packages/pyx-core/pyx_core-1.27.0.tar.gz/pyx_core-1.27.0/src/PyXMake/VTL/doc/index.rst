.. Custom link to in-house GitLab repository.
   :gitlab_url: https://gitlab.com/dlr-sy/pyxmake

.. toctree::
   :maxdepth: 2
   :hidden:

   pyx_core/catalog
   pyx_poetry/plugin
   pyx_webservice/api
   pyxmake/contributing
   pyxmake/changelog
	
Harmonized interfaces and workflows to selected software development tools
==========================================================================
.. include:: ../../README.md
	:end-line: 4
	:parser: myst_parser.docutils_

.. admonition:: Summary

	`PyXMake`_ supports the software development process in Python by providing harmonized interfaces to widely used third-party tools. 
	Strict default values are specified, which lower the barrier to entry and shorten the initial training period. 
	These interfaces can be used either from the command line, via a pyproject.toml file or directly via Python scripts.
	More experienced developers can also transfer the existing class structure into their own build scripts through inheritance and modify them as required.

Scope
-----
This software project arose from the need to consolidate a wide variety of local build configurations for software projects developed by heterogeneous development teams with different individual skills.   
The result is a support tool that defines a standardized command interface with stricter default settings for widespread developer tools, largely independent of platform. 
By setting stricter default values and configuration settings in a `pyproject.toml`_ file, workflows can be easily shared with inexperienced developers as well. 
Platform-dependent tasks are adapted for the user in the background. Missing dependencies are automatically installed using the platform-specific package 
manager or by using chocolatey after user confirmation. Experienced developers can extend all predefined build classes with their own scripts or deactivate them completely 
in order to interact directly with the underlying background tool while retaining the `pyproject.toml`_ support.

Installation
------------
You can install `PyXMake`_ directly with pip:

.. code-block:: console

    $ pip install pyxmake[lint]

Usage
-----
To display all available interface commands, use

.. code-block:: console

	$ pyxmake run --help
	usage: PyXMake run [-h] ...

	positional arguments:
	  namespace   An option identifier. Unknown arguments are ignored. Allowed values are: abaqus, api, pyinstaller,
				  archive, bundle, chocolatey, cmake, coverage, cxx, docker, doxygen, gfortran, gitlab, ifort, java,
				  latex, openapi, portainer, f2py, pyreq, sphinx, ssh_f2py, ssh_ifort, ssh_make

	options:
	  -h, --help  show this help message and exit

By default, all configuration settings are read directly from a `pyproject.toml`_ file and transferred to the respective background process as command line parameters.
Supported interfaces in the `pyproject.toml`_ file are defined as follows, e.g.:

.. include:: ../../pyproject.toml
   :start-line: 159
   :literal:

The dash operator
-----------------
Each entry in a `pyproject.toml`_ file can be overwritten with the -- operator and the corresponding keyword. Additional command line parameters can also be added in this way.
The following command illustrates the workflow. A locally available version of `doxygen`_ is used to create a HTML documentation with a custom tag (e.g. a repository revision number). 
All other configuration settings are taken directly from the `pyproject.toml`_.

.. code-block:: console

	$ pyxmake run doxygen -- --version=1.0.0dev

Citation
--------
.. include:: ../../CITATION.cff
   :literal:

Legal notice
------------
.. include:: ../../LICENSE
   :literal:

Further readings
----------------
* `Developer Reference Guide`_

.. _pyproject.toml: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
.. _doxygen: https://www.doxygen.nl/index.html
.. _PyXMake: https://pypi.org/project/pyxmake
.. _Developer Reference Guide: _static/html/index.html
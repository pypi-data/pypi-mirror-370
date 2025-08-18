******************
Python Terminology
******************

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+---------------------------------------------+
   |Name                 |Definition                                   |
   +=====================+=============================================+
   |Python package       |Python packages are directories that contains|
   |                     |the special module ``__init__.py`` and other |
   |                     |modules, packages, files or directories.     |
   +---------------------+---------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which|
   |                     |are contained in another python package.     |
   +---------------------+---------------------------------------------+
   |Python package       |directory contained in a python package.     |
   |sub-directory        |                                             |
   +---------------------+---------------------------------------------+
   |Python package       |Python package sub-directories with a special|
   |special sub-directory|meaning like data or cfg                     |
   +---------------------+---------------------------------------------+

Special python package sub-directories
--------------------------------------

  .. Special-python-package-sub-directory-Examples-label:
  .. table:: *Special python package sub-directories*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

Python package files
====================

Overview
--------

  .. Python-package-files-overview-label:
  .. table:: *Python package overview files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python        |Files within a python package.                           |
   |package files |                                                         |
   +--------------+---------------------------------------------------------+
   |Python dunder |Package files which are name with leading and trailing   |
   |files         |double underscores.                                      |
   +--------------+---------------------------------------------------------+
   |special       |Package files which are not modules and used as python   |
   |Python files  |marker files like ``py.typed``.                          |
   +--------------+---------------------------------------------------------+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

Python package special files
----------------------------

  .. Python-package-special-files-label:
  .. table:: *Python package special files*

   +--------+--------+--------------------------------------------------------------+
   |Name    |Type    |Description                                                   |
   +========+========+==============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages|
   |        |checking|to indicate that the package supports type checking. This is a|
   |        |marker  |part of the PEP 561 standard, which provides a standardized   |
   |        |file    |way to package and distribute type information in Python.     |
   +--------+--------+--------------------------------------------------------------+

Python package special modules
------------------------------

  .. Python-package-special-modules-label:
  .. table:: *Python package special modules*

   +--------------+-----------+----------------------------------------------------------------+
   |Name          |Type       |Description                                                     |
   +==============+===========+================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to|
   |              |directory  |execute initialisation code or mark the directory it contains   |
   |              |marker     |as a package. The Module enforces explicit imports and thus     |
   |              |file       |clear namespace use and call them with the dot notation.        |
   +--------------+-----------+----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as package entry point |
   |              |for the    |point. The module is executed when the package is called by the |
   |              |package    |interpreter with the command **python -m <package name>**.      |
   +--------------+-----------+----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment      |
   |              |file       |statements used in Versioning.                                  |
   +--------------+-----------+----------------------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +-------------------+-------------------------------------------+
   |Name               |Description                                |
   +===================+===========================================+
   |Python method      |Python functions defined in python modules.|
   +-------------------+-------------------------------------------+
   |special Python     |Python functions with special names and    |
   |method             |functionalities.                           |
   +-------------------+-------------------------------------------+
   |Python class       |Classes defined in python modules.         |
   +-------------------+-------------------------------------------+
   |Python class method|Python methods defined in python classes   |
   +-------------------+-------------------------------------------+
   |special Python     |Python class functions with special names  |
   |class method       |and functionalities.                       |
   +-------------------+-------------------------------------------+

Special python class methods
----------------------------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+------------+-------------------------------------------------------+
   |Name    |Type        |Description                                            |
   +========+============+=======================================================+
   |__init__|class object|The special method ``__init__`` is called when an      |
   |        |constructor |instance (object) of a class is created; instance      |
   |        |method      |attributes can be defined and initalized in the method.|
   +--------+------------+-------------------------------------------------------+

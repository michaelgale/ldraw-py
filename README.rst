ldraw-py
========

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://github.com/fx-bricks/pfx-brick-py/blob/master/LICENSE.md

.. image:: https://travis-ci.com/michaelgale/ldraw-py.png
   :target: https://travis-ci.com/michaelgale/ldraw-py
   :alt: Latest Travis CI build status

A utility package for creating, modifying, and reading LDraw files and data structures.

Installation
------------

The **ldraw-py** package can be installed directly from the source code:

.. code-block:: shell

    $ git clone https://github.com/michaelgale/ldraw-py.git
    $ cd ldraw-py
    $ python setup.py install

Usage
-----

After installation, the package can imported:

.. code-block:: shell

    $ python
    >>> import ldrawpy
    >>> ldrawpy.__version__

An example of the package can be seen below

.. code-block:: python

    from ldrawpy import LDRColour

    # Open a PFx Brick session instance
    mycolour = LDRColour(15)
    print(mycolour)

.. code-block:: shell

    White


Requirements
^^^^^^^^^^^^

* Python 3.6+
* fxgeometry

Authors
-------

`ldraw-py` was written by `Michael Gale <michael@fxbricks.com>`_.

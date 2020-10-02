# ldraw-py

![python version](https://img.shields.io/static/v1?label=python&message=3.6%2B&color=blue&style=flat&logo=python)
![https://github.com/michaelgale/toolbox-py/blob/master/LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>  

![https://travis-ci.org/michaelgale/ldraw-py](https://travis-ci.com/michaelgale/ldraw-py.svg?branch=master)

A utility package for creating, modifying, and reading LDraw files and data structures.

## Installation

The **ldraw-py** package can be installed directly from the source code:

```shell
    $ git clone https://github.com/michaelgale/ldraw-py.git
    $ cd ldraw-py
    $ python setup.py install
```

## Usage

After installation, the package can imported:

```shell
    $ python
    >>> import ldrawpy
    >>> ldrawpy.__version__
```

An example of the package can be seen below

```python
    from ldrawpy import LDRColour

    # Create a white colour using LDraw colour code 15 for white
    mycolour = LDRColour(15)
    print(mycolour)
```

```shell
    White
```

## Requirements

* Python 3.6+
* toolbox-py

## Authors

`ldraw-py` was written by [Michael Gale](https://github.com/michaelgale)

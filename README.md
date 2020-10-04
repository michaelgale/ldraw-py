# ldraw-py

![python version](https://img.shields.io/static/v1?label=python&message=3.6%2B&color=blue&style=flat&logo=python)
![https://github.com/michaelgale/toolbox-py/blob/master/LICENSE](https://img.shields.io/badge/license-MIT-blue.svg)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>  

![https://travis-ci.org/michaelgale/ldraw-py](https://travis-ci.com/michaelgale/ldraw-py.svg?branch=master)

A utility package for creating, modifying, and reading LDraw files and data structures.

LDraw is an open standard for LEGO® CAD software.  It is based on a hierarchy of elements describing primitive shapes up to complex LEGO models and scenes. 

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

## References

- [LDraw.org](https://www.ldraw.org) - Official maintainer of the LDraw file format specification and the LDraw official part library.
- [ldraw-vscode](https://github.com/michaelgale/ldraw-vscode) - Visual Studio Code language extension plug-in for LDraw files

### Lego CAD Tools

- [Bricklink stud.io](https://www.bricklink.com/v3/studio/download.page) new and modern design tool designed and maintained by Bricklink
- [LeoCAD](https://www.leocad.org) cross platform tool
- [MLCAD](http://mlcad.lm-software.com) for Windows
- [Bricksmith](http://bricksmith.sourceforge.net) for macOS by Allen Smith (no longer maintained)
- [LDView](http://ldview.sourceforge.net) real-time 3D viewer for LDraw models

### LPub Instructions Tools

- Original [LPub](http://lpub.binarybricks.nl) publishing tool by Kevin Clague
- [LPub3D](https://trevorsandy.github.io/lpub3d/) successor to LPub by Trevor Sandy
- [Manual](https://sites.google.com/site/workingwithlpub/lpub-4) for Legacy LPub 4 tool (last version by Kevin Clague)

## Authors

`ldraw-py` was written by [Michael Gale](https://github.com/michaelgale)

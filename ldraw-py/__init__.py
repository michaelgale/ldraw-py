"""ldraw-py - A utility package for creating, modifying, and reading LDraw files and data structures."""

import os

__project__ = 'ldraw'
__version__ = '0.1.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .ldraw import *

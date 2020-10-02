"""ldrawpy - A utility package for creating, modifying, and reading LDraw files and data structures."""

import os

__project__ = 'ldrawpy'
__version__ = '0.5.0'

VERSION = __project__ + '-' + __version__

script_dir = os.path.dirname(__file__)

from .constants import *
from .ldrawpy import *
from .ldrcolour import LDRColour
from .ldrprimitives import LDRAttrib, LDRHeader, LDRLine, LDRTriangle, LDRQuad, LDRPart
from .ldrshapes import *
from .ldrmodel import LDRModel, parse_special_tokens
from .ldrdocument import LDRDocument
from .ldrdochelpers import get_centroids_of_colour, CalloutArrows, RotationIcon
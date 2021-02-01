"""ldrawpy - A utility package for creating, modifying, and reading LDraw files and data structures."""

import os

# fmt: off
__project__ = 'ldrawpy'
__version__ = '0.5.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .constants import *
from .ldrawpy import *
from .ldrcolourdict import *
from .ldrhelpers import *
from .ldrcolour import LDRColour
from .ldrprimitives import LDRAttrib, LDRHeader, LDRLine, LDRTriangle, LDRQuad, LDRPart
from .ldrshapes import *
from .ldrmodel import LDRModel, parse_special_tokens
from .ldvrender import LDViewRender
from .ldrarrows import ArrowContext, arrows_for_step, remove_offset_parts

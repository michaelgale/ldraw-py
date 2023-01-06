"""ldrawpy - A utility package for creating, modifying, and reading LDraw files and data structures."""

import os

# fmt: off
__project__ = 'ldrawpy'
__version__ = '0.6.0'
# fmt: on

VERSION = __project__ + "-" + __version__

script_dir = os.path.dirname(__file__)

from .constants import *
from .ldrawpy import brick_name_strip, xyz_to_ldr, mesh_to_ldr
from .ldrcolourdict import *
from .ldrhelpers import *
from .ldrcolour import LDRColour
from .ldrprimitives import LDRAttrib, LDRHeader, LDRLine, LDRTriangle, LDRQuad, LDRPart
from .ldrshapes import *
from .ldrmodel import LDRModel, parse_special_tokens, sort_parts, get_sha1_hash
from .ldvrender import LDViewRender
from .ldrarrows import ArrowContext, arrows_for_step, remove_offset_parts
from .ldrpprint import pprint_line

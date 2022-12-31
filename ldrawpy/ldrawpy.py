#! /usr/bin/env python3
#
# Copyright (C) 2020  Michael Gale
# This file is part of the legocad python module.
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# LDraw python module

from toolbox import *

from .constants import *
from .ldrprimitives import LDRTriangle, LDRLine


def xyz_to_ldr(point, as_tuple=False):
    """Converts a typical x,y,z 3D coordinate to the somewhat unconventional
    LDraw representations of x, -z, y, i.e. the vertical axis extends in
    the -y direction as opposed to +z."""
    if isinstance(point, (tuple, list)):
        v = Vector(point[0], -point[2], point[1])
    else:
        v = Vector(point.x, -point.z, point.y)
    if as_tuple:
        return v.as_tuple()
    return v


def mesh_to_ldr(
    faces, vertices, mesh_colour=LDR_DEF_COLOUR, edges=None, edge_colour=None
):
    """Converts a triangular mesh into a LDraw formatted string of triangles
    and optionally specified edge lines.
      faces - list of triangle vertex indices into the vertices list
      vertices - list of mesh 3D vertices (x, y, z)
      mesh_colour - LDraw colour code for mesh triangles
      edges - list of ((x0, y0, z0), (x1, y1, z1)) line tuples
      edge_colour - LDraw colour code for edge lines
    """
    s = []
    triangles = []
    for face in faces:
        tri = LDRTriangle(mesh_colour, "mm")
        tri.p1 = xyz_to_ldr(vertices[face[0]])
        tri.p2 = xyz_to_ldr(vertices[face[1]])
        tri.p3 = xyz_to_ldr(vertices[face[2]])
        triangles.append(tri)
    for triangle in triangles:
        s.append(str(triangle))
    if edges is not None:
        lines = []
        ec = edge_colour if edge_colour is not None else LDR_OPT_COLOUR
        for edge in edges:
            line = LDRLine(ec, "mm")
            line.p1 = xyz_to_ldr(edge[0])
            line.p2 = xyz_to_ldr(edge[1])
            lines.append(line)
        for line in lines:
            s.append(str(line))
    return "".join(s)


def brick_name_strip(s, level=0):
    """Progressively strips (with increasing levels) a part description
    by making substitutions with abreviations, removing spaces, etc.
    This can be useful for labelling or BOM part lists where space is limited."""
    sn = s
    if level == 0:
        sn = sn.replace("  ", " ")
        sn = sn.replace(
            "Plate 1 x 2 with Groove with 1 Centre Stud, without Understud",
            "Plate 1 x 2  Jumper",
        )
        sn = sn.replace(
            "Plate 1 x 2 without Groove with 1 Centre Stud", "Plate 1 x 2  Jumper"
        )
        sn = sn.replace(
            "Plate 1 x 2 with Groove with 1 Centre Stud", "Plate 1 x 2  Jumper"
        )
        sn = sn.replace("Brick 1 x 1 with Headlight", "Brick 1 x 1 Erling")
        sn = sn.replace("with Groove", "")
        sn = sn.replace("Bluish ", "Bl ")
        sn = sn.replace("Slope Brick", "Slope")
        sn = sn.replace("0.667", "2/3")
        sn = sn.replace("1.667", "1-2/3")
        sn = sn.replace("1.333", "1-1/3")
        sn = sn.replace("1 And 1/3", "1-1/3")
        sn = sn.replace("1 and 1/3", "1-1/3")
        sn = sn.replace("1 & 1/3", "1-1/3")
        sn = sn.replace("with Headlight", "Erling")
        sn = sn.replace("Angle Connector", "Conn")
        sn = sn.replace("~Plate", "Plate")
    elif level == 1:
        sn = sn.replace("with ", "w/")
        sn = sn.replace("With ", "w/")
        sn = sn.replace("Ribbed", "ribbed")
        sn = sn.replace("without ", "wo/")
        sn = sn.replace("Without ", "wo/")
        sn = sn.replace("One", "1")
        sn = sn.replace("Two", "2")
        sn = sn.replace("Three", "3 ")
        sn = sn.replace("Four", "4")
        sn = sn.replace(" and ", " & ")
        sn = sn.replace(" And ", " & ")
        sn = sn.replace("Dark", "Dk")
        sn = sn.replace("Light", "Lt")
        sn = sn.replace("Bright", "Br")
        sn = sn.replace("Reddish Brown", "Red Brown")
        sn = sn.replace("Reddish", "Red")
        sn = sn.replace("Yellowish", "Ylwish")
        sn = sn.replace("Medium", "Med")
        sn = sn.replace("Offset", "offs")
        sn = sn.replace("Adjacent", "adj")
        sn = sn.replace(" degree", "°")
    elif level == 2:
        sn = sn.replace("Trans", "Tr")
        sn = sn.replace(" x ", "x")
        sn = sn.replace("Bl ", " ")
    elif level == 3:
        sn = sn.replace("Orange", "Org")
        sn = sn.replace("Yellow", "Ylw")
        sn = sn.replace("Black", "Blk")
        sn = sn.replace("White", "Wht")
        sn = sn.replace("Green", "Grn")
        sn = sn.replace("Brown", "Brn")
        sn = sn.replace("Purple", "Prpl")
        sn = sn.replace("Violet", "Vlt")
        sn = sn.replace("Gray", "Gry")
        sn = sn.replace("Grey", "Gry")
        sn = sn.replace("Axlehole", "axle")
        sn = sn.replace("Cylinder", "Cyl")
        sn = sn.replace("cylinder", "cyl")
        sn = sn.replace("Inverted", "Inv")
        sn = sn.replace("inverted", "inv")
        sn = sn.replace("Centre", "Ctr")
        sn = sn.replace("centre", "ctr")
        sn = sn.replace("Center", "Ctr")
        sn = sn.replace("center", "ctr")
        sn = sn.replace("Figure", "Fig")
        sn = sn.replace("figure", "fig")
        sn = sn.replace("Rounded", "Round")
        sn = sn.replace("rounded", "round")
        sn = sn.replace("Underside", "under")
        sn = sn.replace("Vertical", "vert")
        sn = sn.replace("Horizontal", "horz")
        sn = sn.replace("vertical", "vert")
        sn = sn.replace("horizontal", "horz")
        sn = sn.replace("Flex-System", "Flex")
        sn = sn.replace("Flanges", "Flange")
        sn = sn.replace("Joiner", "joiner")
        sn = sn.replace("Joint", "joint")
        sn = sn.replace("Type 1", "")
        sn = sn.replace("Type 2", "")
    elif level == 4:
        sn = sn.replace("Technic", "")
        sn = sn.replace("Single", "1")
        sn = sn.replace("Dual", "2")
        sn = sn.replace("Double", "Dbl")
        sn = sn.replace("Stud on", "stud")
        sn = sn.replace("Studs on Sides", "stud sides")
        sn = sn.replace("Studs on Side", "side studs")
        sn = sn.replace("Hinge Plate", "Hinge")
    elif level == 5:
        sn = sn.replace(" on ", " ")
        sn = sn.replace(" On ", " ")
        sn = sn.replace("Round", "Rnd")
        sn = sn.replace("round", "rnd")
        sn = sn.replace("Side", "Sd")
        sn = sn.replace("Groove", "Grv")
        sn = sn.replace("Minifig", "")
        sn = sn.replace("Curved", "Curv")
        sn = sn.replace("curved", "curv")
        sn = sn.replace("Notched", "notch")
        sn = sn.replace("Friction", "fric")
        sn = sn.replace("(Complete)", "")
        sn = sn.replace("Cross", "X")
        sn = sn.replace("Embossed", "Emb")
        sn = sn.replace("Extension", "Ext")
        sn = sn.replace("Bottom", "Bot")
        sn = sn.replace("bottom", "bot")
        sn = sn.replace("Inside", "Insd")
        sn = sn.replace("inside", "insd")
        sn = sn.replace("Locking", "click")
        sn = sn.replace("Axleholder", "axle")
        sn = sn.replace("axleholder", "axle")
        sn = sn.replace("End", "end")
        sn = sn.replace("Open", "open")
        sn = sn.replace("Rod", "rod")
        sn = sn.replace("Hole", "hole")
        sn = sn.replace("Ball", "ball")
        sn = sn.replace("Thin", "thin")
        sn = sn.replace("Thick", "thick")
        sn = sn.replace(" - ", "-")
    elif level == 6:
        sn = sn.replace("Up", "up")
        sn = sn.replace("Down", "dn")
        sn = sn.replace("Bot", "bot")
        sn = sn.replace("Rnd", "rnd")
        sn = sn.replace("Studs", "St")
        sn = sn.replace("studs", "St")
        sn = sn.replace("Stud", "St")
        sn = sn.replace("stud", "St")
        sn = sn.replace("Corners", "edge")
        sn = sn.replace("w/Curv Top", "curved")
        sn = sn.replace("Domed", "dome")
        sn = sn.replace("Clip", "clip")
        sn = sn.replace("Clips", "clip")
        sn = sn.replace("Convex", "cvx")
    sn = sn[0].upper() + sn[1:]
    return sn

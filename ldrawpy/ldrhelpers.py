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
# LDraw related helper functions

import os, tempfile
from toolbox import *
from ldrawpy import *


def mm2LDU(x):
    return x * 2.5


def LDU2mm(x):
    return x * 0.4


def PUnits(point, units="ldu"):
    """
    Writes a floating point value in units of either mm or ldu.
    It restricts the number of decimal places to 4 and minimizes
    redundant trailing zeros (as recommended by ldraw.org)
    """
    x = 0.0
    if units == "mm":
        x = point * 2.5
    else:
        x = point
    s = "%.4f" % (x)
    y = float(s)
    ns = str(y).rstrip("0")
    zs = ns.rstrip(".")
    if zs == "-0":
        return "0 "
    return zs + " "


def MatStr(m):
    """
    Writes the values of a matrix formatted by PUnits.
    """
    s = []
    for v in m:
        s.append(PUnits(v, "ldu"))
    return "".join(s)


def VectorStr(p, attrib):
    return (
        PUnits(p.x, attrib.units)
        + PUnits(p.y, attrib.units)
        + PUnits(p.z, attrib.units)
    )


def GetCircleSegments(radius, segments, attrib):
    from .ldrprimitives import LDRLine

    lines = []
    for seg in range(segments):
        p1 = Vector(0, 0, 0)
        p2 = Vector(0, 0, 0)
        a1 = seg / segments * 2.0 * pi
        a2 = (seg + 1) / segments * 2.0 * pi
        p1.x = radius * cos(a1)
        p1.z = radius * sin(a1)
        p2.x = radius * cos(a2)
        p2.z = radius * sin(a2)
        l = LDRLine(attrib.colour, attrib.units)
        l.p1 = p1
        l.p2 = p2
        lines.append(l)
    return lines


def ldrlist_from_parts(parts):
    """Returns a list of LDRPart objects from either a list of LDRParts,
    a list of strings representing parts or a string with line feed
    delimited parts."""
    from .ldrprimitives import LDRPart

    p = []
    if isinstance(parts, list):
        if len(parts) < 1:
            return []
        if isinstance(parts[0], LDRPart):
            p.extend(parts)
        else:
            for e in parts:
                lp = LDRPart()
                if lp.from_str(e) is not None:
                    p.append(lp)
    else:
        # build from a string of LDraw text
        for e in parts.splitlines():
            lp = LDRPart()
            if lp.from_str(e) is not None:
                p.append(lp)
    return p


def ldrstring_from_list(parts):
    """Returns a LDraw formatted string from a list of parts.  Each part
    is represented in a line feed terminated string concatenated together."""
    from .ldrprimitives import LDRPart

    s = []
    for p in parts:
        if isinstance(p, LDRPart):
            s.append(str(p))
        else:
            if p[-1] != "\n":
                s.append(p + "\n")
            else:
                s.append(p)
    return "".join(s)


def merge_same_parts(parts, other, ignore_colour=False, as_str=False):
    """ Merges parts + other where the the parts in other take precedence."""
    from .ldrprimitives import LDRPart

    op = ldrlist_from_parts(other)
    p = ldrlist_from_parts(other)
    np = ldrlist_from_parts(parts)
    for n in np:
        if not any(
            [
                n.is_same(o, ignore_location=True, ignore_colour=ignore_colour)
                for o in op
            ]
        ):
            p.append(n)
    if as_str:
        return ldrstring_from_list(p)
    return p


def remove_parts_from_list(parts, other):
    """ Returns a list based on removing the parts from other from parts. """
    pp = ldrlist_from_parts(parts)
    op = ldrlist_from_parts(other)
    np = []
    for p in pp:
        if not any([o.name == p.name for o in op]):
            np.append(p)
    return np

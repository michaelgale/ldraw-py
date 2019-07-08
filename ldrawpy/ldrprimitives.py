#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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
# LDraw primitives

import os
import tempfile
from functools import reduce

from fxgeometry import Identity, Vector, Vector2D, Matrix
from .ldrawpy import *
from ldrawpy.ldrhelpers import VectorStr, MatStr


class LDRAttrib:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.colour = colour
        self.units = units
        self.loc = Vector(0, 0, 0)
        self.matrix = Identity()


class LDRLine:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.p1 = Vector(0, 0, 0)
        self.p2 = Vector(0, 0, 0)

    def __str__(self):
        return (
            ("2 %d " % self.attrib.colour)
            + VectorStr(self.p1, self.attrib)
            + VectorStr(self.p2, self.attrib)
            + "\n"
        )

    def translate(self, offset):
        self.p1 += offset
        self.p2 += offset

    def transform(self, matrix):
        self.p1 = self.p1 * matrix
        self.p2 = self.p2 * matrix


class LDRTriangle:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.p1 = Vector(0, 0, 0)
        self.p2 = Vector(0, 0, 0)
        self.p3 = Vector(0, 0, 0)

    def __str__(self):
        return (
            ("3 %d " % self.attrib.colour)
            + VectorStr(self.p1, self.attrib)
            + VectorStr(self.p2, self.attrib)
            + VectorStr(self.p3, self.attrib)
            + "\n"
        )

    def translate(self, offset):
        self.p1 += offset
        self.p2 += offset
        self.p3 += offset

    def transform(self, matrix):
        self.p1 *= matrix
        self.p2 *= matrix
        self.p3 *= matrix


class LDRQuad:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.p1 = Vector(0, 0, 0)
        self.p2 = Vector(0, 0, 0)
        self.p3 = Vector(0, 0, 0)
        self.p4 = Vector(0, 0, 0)

    def __str__(self):
        return (
            ("4 %d " % self.attrib.colour)
            + VectorStr(self.p1, self.attrib)
            + VectorStr(self.p2, self.attrib)
            + VectorStr(self.p3, self.attrib)
            + VectorStr(self.p4, self.attrib)
            + "\n"
        )

    def translate(self, offset):
        self.p1 += offset
        self.p2 += offset
        self.p3 += offset
        self.p4 += offset

    def transform(self, matrix):
        self.p1 *= matrix
        self.p2 *= matrix
        self.p3 *= matrix
        self.p4 *= matrix


class LDRPart:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.name = ""
        self.wrapcallout = True

    def from_str(self, s):
        splitLine = s.lower().split()
        if (len(splitLine) >= 15):
            self.attrib.colour = int(splitLine[1])
            self.attrib.loc.x = float(splitLine[2])
            self.attrib.loc.y = float(splitLine[3])
            self.attrib.loc.z = float(splitLine[4])
            self.attrib.matrix = Matrix(
                [[float(splitLine[5]), float(splitLine[6]), float(splitLine[7])], \
                 [float(splitLine[8]), float(splitLine[9]), float(splitLine[10])], \
                 [float(splitLine[11]), float(splitLine[12]), float(splitLine[13])]] \
            )
            pname = splitLine[14]
            if pname[-4 :] == ".dat":
                self.name = str(pname[0:len(pname)-4])
            else:
                self.name = str(splitLine[14])

    def __str__(self):
        tup = tuple(reduce(lambda row1, row2: row1 + row2, self.attrib.matrix.rows))
        name = self.name
        ext = name[-4:].lower()
        if len(name) > 4:
            if ext == ".ldr" or ext == ".dat":
                name = self.name
            else:
                name = self.name + ".dat"
        else:
            name = self.name + ".dat"
        s = (
            ("1 %i " % self.attrib.colour)
            + VectorStr(self.attrib.loc, self.attrib)
            + MatStr(tup)
            + ("%s\n" % name)
        )
        if self.wrapcallout and ext == ".ldr":
            return "0 !LPUB CALLOUT BEGIN\n" + s + "0 !LPUB CALLOUT END\n"
        return s


def GeneratePartImage(
    name, colour=LDR_DEF_COLOUR, size=512, outpath="./", filename=""
):

    p = LDRPart(colour, "mm")
    p.name = name
    LDR_TEMP_PATH = tempfile.gettempdir() + os.sep + "temp.ldr"
    f = open(LDR_TEMP_PATH, "w")
    f.write(str(p))
    f.close()

    if filename is not None:
        fn = filename
    else:
        fn = outpath + name + "_" + str(colour) + ".png"

    ldvsize = "-SaveWidth=%d -SaveHeight=%d -SaveSnapShot=%s" % (size, size, fn)
    ldv = []
    ldv.append(LDVIEW_BIN)
    ldv.append(LDVIEW_ARG)
    ldv.append(ldvsize)
    ldv.append(LDR_TEMP_PATH)
    s = " ".join(ldv)
    os.system(s)


class LDRHeader:
    def __init__(self):
        self.title = ""
        self.file = ""
        self.name = ""
        self.author = ""

    def __str__(self):
        return (
            ("0 %s\n" % self.title)
            + ("0 FILE %s\n" % self.file)
            + ("0 Name: %s\n" % self.name)
            + ("0 Author: %s\n" % self.author)
        )

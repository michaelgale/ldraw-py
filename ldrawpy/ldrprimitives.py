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
# LDraw primitives

import os
import tempfile
import hashlib

from functools import reduce

from toolbox import *
from ldrawpy import *
from .ldrhelpers import VectorStr, MatStr


class LDRAttrib:
    __slots__ = ["colour", "units", "loc", "matrix"]

    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.colour = colour
        self.units = units
        self.loc = Vector(0, 0, 0)
        self.matrix = Identity()

    def __eq__(self, other):
        if self.colour != other.colour:
            return False
        if not self.loc.almost_same_as(other.loc):
            return False
        if not self.matrix.is_almost_same_as(other.matrix):
            return False
        return True

    def copy(self):
        a = LDRAttrib()
        a.colour = self.colour
        a.units = self.units
        a.loc = self.loc.copy()
        a.matrix = self.matrix.copy()
        return a


class LDRLine:
    __slots__ = ["attrib", "p1", "p2"]

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
    __slots__ = ["attrib", "p1", "p2", "p3"]

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
    __slots__ = ["attrib", "p1", "p2", "p3", "p4"]

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
    __slots__ = ["attrib", "name", "wrapcallout"]

    def __init__(self, colour=LDR_DEF_COLOUR, name=None, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.name = name if name is not None else ""
        self.wrapcallout = True

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

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.attrib.colour != other.attrib.colour:
            return False
        return True

    def copy(self):
        p = LDRPart()
        p.name = self.name
        p.wrapcallout = self.wrapcallout
        p.attrib = self.attrib.copy()
        return p

    def sha1hash(self):
        shash = hashlib.sha1()
        shash.update(bytes(str(self), encoding="utf8"))
        return shash.hexdigest()

    def is_identical(self, other):
        if self.name != other.name:
            return False
        if self.attrib != other.attrib:
            return False
        return True

    def is_same(self, other, ignore_location=False, ignore_colour=False):
        if not self.name == other.name:
            return False
        if not ignore_colour:
            if not self.attrib.colour == other.attrib.colour:
                return False
        if not ignore_location:
            if not self.attrib.loc.almost_same_as(other.attrib.loc):
                return False
        if not ignore_colour and not ignore_location:
            if not self.sha1hash() == other.sha1hash():
                return False
        return True

    def is_coaligned(self, other):
        v1 = self.attrib.loc * self.attrib.matrix
        v2 = other.attrib.loc * other.attrib.matrix
        naxis = v1.is_colinear_with(v2)
        if naxis == 2:
            return True
        return False

    def change_colour(self, to_colour):
        self.attrib.colour = to_colour

    def set_rotation(self, angle):
        rm = euler_to_rot_matrix(angle)
        self.attrib.matrix = rm

    def move_to(self, pos):
        o = safe_vector(pos)
        self.attrib.loc = o

    def move_by(self, offset):
        o = safe_vector(offset)
        self.attrib.loc += o

    def rotate_by(self, angle):
        rm = euler_to_rot_matrix(angle)
        rt = rm.transpose()
        self.attrib.matrix = rm * self.attrib.matrix
        self.attrib.loc *= rt

    def transform(self, matrix=Identity(), offset=Vector(0, 0, 0)):
        mt = matrix.transpose()
        self.attrib.matrix = matrix * self.attrib.matrix
        self.attrib.loc *= mt
        self.attrib.loc += offset

    def from_str(self, s):
        splitLine = s.lower().split()
        if len(splitLine) >= 15:
            line_type = int(splitLine[0].lstrip())
            if line_type == 1:
                self.attrib.colour = int(splitLine[1])
                self.attrib.loc.x = float(splitLine[2])
                self.attrib.loc.y = float(splitLine[3])
                self.attrib.loc.z = float(splitLine[4])
                self.attrib.matrix = Matrix(
                    [
                        [float(splitLine[5]), float(splitLine[6]), float(splitLine[7])],
                        [
                            float(splitLine[8]),
                            float(splitLine[9]),
                            float(splitLine[10]),
                        ],
                        [
                            float(splitLine[11]),
                            float(splitLine[12]),
                            float(splitLine[13]),
                        ],
                    ]
                )
                pname = " ".join(splitLine[14:])
                self.name = pname.replace(".dat", "")
                return self
        return None

    @staticmethod
    def translate_from_str(s, offset):
        offset = safe_vector(offset)
        p = LDRPart()
        p.from_str(s)
        p.attrib.loc += offset
        p.wrapcallout = False
        return str(p)

    @staticmethod
    def transform_from_str(s, matrix=Identity(), offset=Vector(0, 0, 0), colour=None):
        offset = safe_vector(offset)
        p = LDRPart()
        p.from_str(s)
        mt = matrix.transpose()
        p.attrib.matrix = matrix * p.attrib.matrix
        p.attrib.loc *= mt
        p.attrib.loc += offset
        p.wrapcallout = False
        if colour is not None:
            p.attrib.colour = colour
        return str(p)


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

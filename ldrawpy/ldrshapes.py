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
# LDraw helper functions to generate complicated shapes and solids
# from LDraw primitives

import os
import copy

from toolbox import *
from ldrawpy import *


class LDRPolyWall:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.height = 1

    def __str__(self):

        s = []
        nPoints = len(self.points)
        for i in range(nPoints):
            q = LDRQuad(self.attrib.colour, self.attrib.units)
            q.p1.x = self.points[i].x
            q.p1.y = self.height
            q.p1.z = self.points[i].z
            thePoint = self.points[0]
            if i < nPoints - 1:
                thePoint = self.points[i + 1]
            q.p2.x = thePoint.x
            q.p2.y = self.height
            q.p2.z = thePoint.z
            q.p3.x = thePoint.x
            q.p3.y = 0
            q.p3.z = thePoint.z
            q.p4.x = self.points[i].x
            q.p4.y = 0
            q.p4.z = self.points[i].z
            q.transform(self.attrib.matrix)
            q.translate(self.attrib.loc)
            s.append(str(q))
        return "".join(s)


class LDRRect:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.length = 1
        self.width = 1

    def __str__(self):
        s = []
        q = LDRQuad(self.attrib.colour, self.attrib.units)
        q.p1.x
        q.p1.x = -self.length / 2
        q.p1.y = 0
        q.p1.z = self.width / 2
        q.p2.x = -self.length / 2
        q.p2.y = 0
        q.p2.z = -self.width / 2
        q.p3.x = self.length / 2
        q.p3.y = 0
        q.p3.z = -self.width / 2
        q.p4.x = self.length / 2
        q.p4.y = 0
        q.p4.z = self.width / 2
        q.transform(self.attrib.matrix)
        q.translate(self.attrib.loc)
        l = LDRLine(self.attrib.colour, self.attrib.units)
        l.p1 = q.p1
        l.p2 = q.p2
        s.append(str(l))
        l.p1 = q.p2
        l.p2 = q.p3
        s.append(str(l))
        l.p1 = q.p3
        l.p2 = q.p4
        s.append(str(l))
        l.p1 = q.p4
        l.p2 = q.p1
        s.append(str(l))
        s.append(str(q))
        return "".join(s)


class LDRCircle:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.radius = 1
        self.segments = 24
        self.fill = False

    def __str__(self):
        s = []
        lines = GetCircleSegments(self.radius, self.segments, self.attrib)
        for line in lines:
            l = LDRLine(self.attrib.colour, self.attrib.units)
            l.transform(self.attrib.matrix)
            l.translate(self.attrib.loc)
            s.append(str(l))
        if self.fill == True:
            for line in lines:
                t = LDRTriangle(self.attrib.colour, self.attrib.units)
                t.p2 = line.p1
                t.p3 = line.p2
                t.transform(self.attrib.matrix)
                t.translate(self.attrib.loc)
                s.append(str(t))
        return "".join(s)


class LDRDisc:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.radius = 1
        self.border = 2
        self.segments = 24

    def __str__(self):
        s = []
        lines = GetCircleSegments(self.radius, self.segments, self.attrib)
        for line in lines:
            l = LDRLine(self.attrib.colour, self.attrib.units)
            l = copy.deepcopy(line)
            l.transform(self.attrib.matrix)
            l.translate(self.attrib.loc)
            s.append(str(l))

        olines = GetCircleSegments(
            self.radius + self.border, self.segments, self.attrib
        )

        for i, line in enumerate(lines):
            q = LDRQuad(self.attrib.colour, self.attrib.units)
            q.p1.x = line.p1.x
            q.p1.z = line.p1.z
            q.p2.x = line.p2.x
            q.p2.z = line.p2.z
            q.p3.x = olines[i].p2.x
            q.p3.z = olines[i].p2.z
            q.p4.x = olines[i].p1.x
            q.p4.z = olines[i].p1.z
            q.transform(self.attrib.matrix)
            q.translate(self.attrib.loc)
            s.append(str(q))
        return "".join(s)


class LDRHole:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.radius = 1
        self.segments = 24

    def __str__(self):
        s = []
        for seg in range(self.segments):
            t = LDRTriangle(self.attrib.colour, self.attrib.units)
            a1 = seg / self.segments * 2.0 * pi
            a2 = (seg + 1) / self.segments * 2.0 * pi
            t.p1.x = self.radius * cos(a1)
            t.p1.z = self.radius * sin(a1)
            t.p2.x = self.radius * cos(a2)
            t.p2.z = self.radius * sin(a2)
            if (a1 >= 0.0) and (a1 < pi / 2.0):
                t.p3.x = self.radius
                t.p3.z = self.radius
            elif (a1 >= pi / 2.0) and (a1 < pi):
                t.p3.x = -self.radius
                t.p3.z = self.radius
            elif (a1 >= pi) and (a1 < 3 * pi / 2):
                t.p3.x = -self.radius
                t.p3.z = -self.radius
            else:
                t.p3.x = self.radius
                t.p3.z = -self.radius
            t.transform(self.attrib.matrix)
            t.translate(self.attrib.loc)
            l = LDRLine(OPT_COLOUR, self.attrib.units)
            l.p1 = t.p1
            l.p2 = t.p2
            s.append(str(t))
            s.append(str(l))
        return "".join(s)


class LDRCylinder:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.radius = 1
        self.height = 1
        self.segments = 24

    def __str__(self):
        s = []
        lines = GetCircleSegments(self.radius, self.segments, self.attrib)
        for line in lines:
            l = LDRLine(self.attrib.colour, self.attrib.units)
            l = copy.deepcopy(line)
            l.transform(self.attrib.matrix)
            l.translate(self.attrib.loc)
            s.append(str(l))
        for line in lines:
            l = LDRLine(self.attrib.colour, self.attrib.units)
            l = copy.deepcopy(line)
            l.translate(Vector(0, self.height, 0))
            l.transform(self.attrib.matrix)
            l.translate(self.attrib.loc)
            s.append(str(l))
        for line in lines:
            q = LDRQuad(self.attrib.colour, self.attrib.units)
            q.p1.x = line.p1.x
            q.p1.z = line.p1.z
            q.p2.x = line.p2.x
            q.p2.z = line.p2.z
            q.p3.x = line.p2.x
            q.p3.z = line.p2.z
            q.p4.x = line.p1.x
            q.p4.z = line.p1.z
            q.p1.y = self.height
            q.p2.y = self.height
            q.p3.y = 0
            q.p4.y = 0
            q.transform(self.attrib.matrix)
            q.translate(self.attrib.loc)
            s.append(str(q))
        return "".join(s)


class LDRBox:
    def __init__(self, colour=LDR_DEF_COLOUR, units="ldu"):
        self.attrib = LDRAttrib(colour, units)
        self.length = 1
        self.width = 1
        self.height = 1

    def __str__(self):
        s = []
        l = LDRLine(OPT_COLOUR, self.attrib.units)
        p = []
        p.append(Vector(self.length / 2, self.height / 2, self.width / 2))
        p.append(Vector(-self.length / 2, self.height / 2, self.width / 2))
        p.append(Vector(-self.length / 2, self.height / 2, -self.width / 2))
        p.append(Vector(self.length / 2, self.height / 2, -self.width / 2))
        p.append(Vector(self.length / 2, -self.height / 2, self.width / 2))
        p.append(Vector(-self.length / 2, -self.height / 2, self.width / 2))
        p.append(Vector(-self.length / 2, -self.height / 2, -self.width / 2))
        p.append(Vector(self.length / 2, -self.height / 2, -self.width / 2))
        coords = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 0],
            [4, 5],
            [5, 6],
            [6, 7],
            [7, 4],
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
        ]
        for coord in coords:
            l.p1 = p[coord[0]]
            l.p2 = p[coord[1]]
            l.transform(self.attrib.matrix)
            l.translate(self.attrib.loc)
            s.append(str(l))
        q = LDRQuad(self.attrib.colour, self.attrib.units)
        coords = [
            [0, 3, 2, 1],
            [6, 7, 4, 5],
            [5, 4, 0, 1],
            [6, 5, 1, 2],
            [7, 6, 2, 3],
            [4, 7, 3, 0],
        ]
        for coord in coords:
            q.p1 = p[coord[0]]
            q.p2 = p[coord[1]]
            q.p3 = p[coord[2]]
            q.p4 = p[coord[3]]
            q.transform(self.attrib.matrix)
            q.translate(self.attrib.loc)
            s.append(str(q))
        return "".join(s)

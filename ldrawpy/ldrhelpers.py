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
# LDraw related helper functions

import os
from fxgeometry import Vector

def LineHasAllTokens(line, tokenlist):
    for t in tokenlist:
        tokens = t.split()
        tcount = 0
        tlen = len(tokens)
        for te in tokens:
            if te in line.split():
                tcount += 1
        if tcount == tlen:
            return True
    return False

def mm2LDU(x):
    return(x * 2.5)

def LDU2mm(x):
    return(x * 0.4)

def PUnits(point, units='ldu'):
    """
    Writes a floating point value in units of either mm or ldu.
    It restricts the number of decimal places to 4 and minimizes
    redundant trailing zeros (as recommended by ldraw.org)
    """
    x = 0.0
    if units=='mm':
        x = point * 2.5
    else:
        x = point
    s = "%.4f" % (x)
    y = float(s)
    ns = str(y).rstrip('0')
    zs = ns.rstrip('.')
    if zs == '-0':
        return '0 '
    return (zs + ' ')

def MatStr(m):
    """
    Writes the values of a matrix formatted by PUnits.
    """
    s = []
    for v in m:
        s.append(PUnits(v, 'ldu'))
    return ''.join(s)

def VectorStr(p, attrib):
    return PUnits(p.x, attrib.units) + PUnits(p.y, attrib.units) + PUnits(p.z, attrib.units)

def GetCircleSegments(radius, segments, attrib):
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

START_TOKENS = ['PLI BEGIN IGN', 'BUFEXCHG STORE', 'SYNTH BEGIN']
END_TOKENS = ['PLI END', 'BUFEXCHG RETRIEVE', 'SYNTH END']

def GetPartsFromModel(ldr_string):
    parts = []
    lines = ldr_string.splitlines()
    mask_depth = 0
    for line in lines:
        pd = {}
        if LineHasAllTokens(line, START_TOKENS):
            mask_depth += 1
        if LineHasAllTokens(line, END_TOKENS):
            if mask_depth > 0:
                mask_depth -= 1

        lineType = int(line.lstrip()[0] if line.lstrip() else -1)
        if lineType == -1:
            continue
        if lineType == 1 and mask_depth == 0:
            splitLine = line.lower().split()
            pd['color'] = splitLine[1]
            pd['partId'] = ' '.join([str(i) for i in splitLine[14:]])
            parts.append(pd)
    return parts

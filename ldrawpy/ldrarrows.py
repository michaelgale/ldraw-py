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
# LDraw arrow callout utilties

import os
import copy
from math import sin, cos, pi
from functools import reduce

from toolbox import *
from ldrawpy import *

ARROW_PREFIX = """0 BUFEXCHG A STORE"""
ARROW_PLI = """0 !LPUB PLI BEGIN IGN"""
ARROW_SUFFIX = """0 !LPUB PLI END
0 STEP
0 BUFEXCHG A RETRIEVE"""
ARROW_PLI_SUFFIX = """0 !LPUB PLI END"""

ARROW_PARTS = ["hashl2", "hashl3", "hashl4", "hashl5", "hashl6"]

# ARROW_MZ = Matrix([[0, -1.25, 0], [1.25, 0, 0], [0, 0, 1.25]])
# ARROW_PZ = Matrix([[0, -1.25, 0], [-1.25, 0, 0], [0, 0, -1.25]])
# ARROW_MX = Matrix([[0, 0, 1.25], [1.25, 0, 0], [0, 1.25, 0]])
# ARROW_PX = Matrix([[0, 0, -1.25], [-1.25, 0, 0], [0, 1.25, 0]])
# ARROW_MY = Matrix([[0, -1.25, 0], [0, 0, -1.25], [1.25, 0, 0]])
# ARROW_PY = Matrix([[0, -1.25, 0], [0, 0, 1.25], [-1.25, 0, 0]])

ARROW_MZ = Matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
ARROW_PZ = Matrix([[0, -1, 0], [-1, 0, 0], [0, 0, -1]])
ARROW_MX = Matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
ARROW_PX = Matrix([[0, 0, -1], [-1, 0, 0], [0, 1, 0]])
ARROW_MY = Matrix([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
ARROW_PY = Matrix([[0, -1, 0], [0, 0, 1], [-1, 0, 0]])


def value_after_token(tokens, value_token):
    for i, token in enumerate(tokens):
        if token == value_token:
            if (i + 1) < len(tokens):
                return tokens[i + 1]


def norm_angle(angle):
    return angle % 90


class ArrowContext:
    def __init__(self, colour=4, length=2):
        self.colour = colour
        self.length = length
        self.scale = 10
        self.yscale = 10
        self.offset = Vector(0, 0, 0)
        self.rotstep = Vector(0, 0, 0)

    def part_for_length(self, length):
        if length <= 2:
            return "hashl2"
        if length <= 3:
            return "hashl3"
        if length <= 4:
            return "hashl4"
        if length <= 5:
            return "hashl5"
        return "hashl2"

    def matrix_for_offset(self, offset, mask=""):
        rotxy = norm_angle(self.rotstep.x) + norm_angle(self.rotstep.y)
        rotxz = norm_angle(self.rotstep.x) + norm_angle(self.rotstep.z)
        rotyz = norm_angle(self.rotstep.y) + norm_angle(self.rotstep.z)
        if (offset.x > 0) and mask != "x":
            return ARROW_MX.rotate(-rotyz, ZAxis)
        elif (offset.x < 0) and mask != "x":
            return ARROW_PX.rotate(rotyz, ZAxis)
        elif (offset.y > 0) and mask != "y":
            return ARROW_PY.rotate(rotxz, ZAxis)
        elif (offset.y < 0) and mask != "y":
            return ARROW_MY.rotate(-rotxz, ZAxis)
        elif (offset.z > 0) and mask != "z":
            return ARROW_MZ.rotate(-rotxy, ZAxis)
        elif (offset.z < 0) and mask != "z":
            return ARROW_PZ.rotate(rotxy, ZAxis)
        return Identity()

    def loc_for_offset(self, offset, length, mask=""):
        loc_offset = Vector(0, 0, 0)
        if (offset.x > 0) and mask != "x":
            loc_offset.x = -1.5 * length * self.scale
        elif (offset.x < 0) and mask != "x":
            loc_offset.x = 1.5 * length * self.scale
        elif (offset.y > 0) and mask != "y":
            loc_offset.y = -length * self.yscale
        elif (offset.y < 0) and mask != "y":
            loc_offset.y = 1.5 * length * self.yscale
        elif (offset.z > 0) and mask != "z":
            loc_offset.z = -1.5 * length * self.scale
        elif (offset.z < 0) and mask != "z":
            loc_offset.z = length * self.scale
        if mask == "x":
            loc_offset += Vector(offset.x, 0.5 * offset.y, 0.5 * offset.z)
        elif mask == "y":
            loc_offset += Vector(0.5 * offset.x, offset.y, 0.5 * offset.z)
        elif mask == "z":
            loc_offset += Vector(0.5 * offset.x, 0.5 * offset.y, offset.z)
        else:
            loc_offset += 0.5 * offset
        return loc_offset

    def part_loc_for_offset(self, offset, mask=""):
        loc_offset = Vector(0, 0, 0)
        if (offset.x != 0) and mask != "x":
            loc_offset.x = offset.x
        elif (offset.y != 0) and mask != "y":
            loc_offset.y = offset.y
        elif (offset.z != 0) and mask != "z":
            loc_offset.z = offset.z
        else:
            loc_offset = offset
        return loc_offset

    def _mask_axis(self, offsets):
        """ Determines which axis has a changing value and is not consistent in a list """
        if len(offsets) == 1:
            return ""
        mx, my, mz = 0, 0, 0
        nx, ny, nz = 0, 0, 0
        for o in offsets:
            mx, my, mz = min(mx, o.x), min(my, o.y), min(mz, o.z)
            nx, ny, nz = max(nx, o.x), max(ny, o.y), max(nz, o.z)
        if abs(nx - mx) > 0:
            return "x"
        elif abs(ny - my) > 0:
            return "y"
        elif abs(nz - mz) > 0:
            return "z"
        return ""

    def arrow_from_dict(self, dict):
        arrows = []
        mask = self._mask_axis(dict["offset"])
        for i, o in enumerate(dict["offset"]):
            ldrpart = LDRPart()
            ldrpart.wrapcallout = False
            ldrpart.from_str(dict["line"])
            arrpart = LDRPart()
            arrpart.name = self.part_for_length(dict["length"])
            arrpart.attrib.loc = copy.copy(ldrpart.attrib.loc)
            arrpart.attrib.loc += self.loc_for_offset(o, dict["length"], mask)
            arrpart.attrib.matrix = self.matrix_for_offset(o, mask)
            arrpart.attrib.colour = dict["colour"]
            arrows.append(str(arrpart))
        return "".join(arrows)

    def dict_for_line(self, line):
        item = {}
        item["line"] = line
        item["colour"] = self.colour
        item["length"] = self.length
        item["offset"] = copy.copy(self.offset)
        return item


def arrows_for_step(arrow_ctx, step, as_lpub=True):
    step_lines = []
    arrow_parts = []
    lines = step.splitlines()
    in_arrow = False
    offset = Vector(0, 0, 0)
    for line in lines:
        lineType = int(line.lstrip()[0] if line.lstrip() else -1)
        if lineType == 0:
            ls = line.upper().split()
            if "!PY ARROW" in line:
                if in_arrow == False and "BEGIN" in line:
                    in_arrow = True
                    arrow_ctx.offset = []
                    arrow_ctx.offset.append(
                        Vector(float(ls[4]), float(ls[5]), float(ls[6]))
                    )
                    if len(ls) > 7:
                        arrow_ctx.offset.append(
                            Vector(float(ls[7]), float(ls[8]), float(ls[9]))
                        )
                    if len(ls) > 10:
                        arrow_ctx.offset.append(
                            Vector(float(ls[10]), float(ls[11]), float(ls[12]))
                        )
                elif in_arrow and "END" in line:
                    in_arrow = False
                    continue
                if "COLOUR" in line:
                    try:
                        arrow_ctx.colour = int(value_after_token(ls, "COLOUR"))
                    except:
                        pass
                    if not in_arrow:
                        continue
                if "LENGTH" in line:
                    try:
                        arrow_ctx.length = int(value_after_token(ls, "LENGTH"))
                    except:
                        pass
                    if not in_arrow:
                        continue

        if in_arrow and lineType == 1:
            item = arrow_ctx.dict_for_line(line)
            arrow_parts.append(item)
        elif in_arrow == False:
            step_lines.append(line)

    if len(arrow_parts) > 0:
        if as_lpub:
            step_lines.append(ARROW_PREFIX)
            for part in arrow_parts:
                ldrpart = LDRPart()
                ldrpart.wrapcallout = False
                ldrpart.from_str(part["line"])
                mask = arrow_ctx._mask_axis(part["offset"])
                ldrpart.attrib.loc += arrow_ctx.part_loc_for_offset(
                    part["offset"][0], mask
                )
                step_lines.append(str(ldrpart).strip("\n"))
            step_lines.append(ARROW_PLI)
            for part in arrow_parts:
                arrow_part = arrow_ctx.arrow_from_dict(part)
                step_lines.append(arrow_part.strip("\n"))
            step_lines.append(ARROW_SUFFIX)
            step_lines.append(ARROW_PLI)
            for part in arrow_parts:
                step_lines.append(part["line"])
            step_lines.append(ARROW_PLI_SUFFIX)
        else:
            for part in arrow_parts:
                ldrpart = LDRPart()
                ldrpart.wrapcallout = False
                ldrpart.from_str(part["line"])
                mask = arrow_ctx._mask_axis(part["offset"])
                ldrpart.attrib.loc += arrow_ctx.part_loc_for_offset(
                    part["offset"][0], mask
                )
                step_lines.append(str(ldrpart).strip("\n"))
            for part in arrow_parts:
                arrow_part = arrow_ctx.arrow_from_dict(part)
                step_lines.append(arrow_part.strip("\n"))

    else:
        if "NOFILE" not in step:
            if len(step_lines) > 0:
                step_lines.append("0 STEP")
    if len(step_lines) > 0:
        return "\n".join(step_lines)
    return ""


def arrows_for_lpub_file(filename, outfile):
    arrow_ctx = ArrowContext()
    with open(filename, "rt") as fp:
        with open(outfile, "w") as fpo:
            files = fp.read().split("0 FILE")
            for i, file in enumerate(files):
                if i == 0:
                    mfile = file
                else:
                    mfile = "0 FILE " + file.strip()
                steps = mfile.split("0 STEP")
                for j, step in enumerate(steps):
                    new_step = arrows_for_step(arrow_ctx, step)
                    fpo.write(new_step)
                if len(steps) > 1:
                    fpo.write("\n")

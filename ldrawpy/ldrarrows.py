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
    return angle % 45


class ArrowContext:
    def __init__(self, colour=804, length=2):
        self.colour = colour
        self.length = length
        self.scale = 25
        self.yscale = 20
        self.offset = Vector(0, 0, 0)
        self.rotstep = Vector(0, 0, 0)
        self.ratio = 0.5

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

    def matrix_for_offset(self, offset, mask="", invert=False, tilt=0):
        rotxy = norm_angle(self.rotstep.x + self.rotstep.y)
        rotxz = norm_angle(self.rotstep.x + self.rotstep.z)
        rotyz = norm_angle(self.rotstep.y + self.rotstep.z)

        if invert:
            rotxy = rotxy + 180
            rotxz = rotxz + 180
            rotyz = rotyz + 180
        if (offset.x > 0) and "x" not in mask:
            return ARROW_MX.rotate(-rotyz + tilt, ZAxis)
        elif (offset.x < 0) and "x" not in mask:
            return ARROW_PX.rotate(rotyz + tilt, ZAxis)

        if (offset.y > 0) and "y" not in mask:
            return ARROW_PY.rotate(rotxz + tilt, ZAxis)
        elif (offset.y < 0) and "y" not in mask:
            return ARROW_MY.rotate(-rotxz + tilt, ZAxis)

        if (offset.z > 0) and "z" not in mask:
            return ARROW_MZ.rotate(-rotxy + tilt, ZAxis)
        elif (offset.z < 0) and "z" not in mask:
            return ARROW_PZ.rotate(rotxy + tilt, ZAxis)
        return Identity()

    def loc_for_offset(self, offset, length, mask="", ratio=0.5):
        loc_offset = Vector(0, 0, 0)
        ratio1 = 1.0 + ratio
        if (offset.x > 0) and "x" not in mask:
            loc_offset.x = offset.x / 2 - float(length) * ratio * self.scale
        elif (offset.x < 0) and "x" not in mask:
            loc_offset.x = offset.x / 2 + float(length) * ratio * self.scale
        if (offset.y > 0) and "y" not in mask:
            loc_offset.y = offset.y / 2 - float(length) * ratio * self.yscale
        elif (offset.y < 0) and "y" not in mask:
            loc_offset.y = offset.y / 2 + float(length) * ratio * self.yscale
        if (offset.z > 0) and "z" not in mask:
            loc_offset.z = offset.z / 2 - float(length) * ratio * self.scale
        elif (offset.z < 0) and "z" not in mask:
            loc_offset.z = offset.z / 2 + float(length) * ratio * self.scale
        if "x" in mask:
            loc_offset += Vector(offset.x, 0, 0)
        if "y" in mask:
            loc_offset += Vector(0, offset.y, 0)
        if "z" in mask:
            loc_offset += Vector(0, 0, offset.z)
        # else:
        #     loc_offset += ratio * offset
        # if "x" in mask:
        #     loc_offset += Vector(offset.x, ratio * offset.y, ratio * offset.z)
        # elif "y" in mask:
        #     loc_offset += Vector(ratio * offset.x, offset.y, ratio * offset.z)
        # elif "z" in mask:
        #     loc_offset += Vector(ratio * offset.x, ratio * offset.y, offset.z)
        # else:
        #     loc_offset += ratio * offset
        # print("len: %s offset: %s  mask: %s ratio: %.1f loc_off: %s" %(length, str(offset), mask, ratio, str(loc_offset)))
        return loc_offset

    def part_loc_for_offset(self, offset, mask=""):
        loc_offset = Vector(0, 0, 0)
        if abs(offset.x) > 0.1 and "x" not in mask:
            loc_offset.x = offset.x
        if abs(offset.y) > 0.1 and "y" not in mask:
            loc_offset.y = offset.y
        if abs(offset.z) > 0.1 and "z" not in mask:
            loc_offset.z = offset.z
        return loc_offset

    def _mask_axis(self, offsets):
        """Determines which axis has a changing value and is not consistent in a list"""
        if len(offsets) == 1:
            return ""
        mx, my, mz = 1e18, 1e18, 1e18
        nx, ny, nz = -1e18, -1e18, -1e18
        mask = ""
        for o in offsets:
            mx, my, mz = min(mx, o.x), min(my, o.y), min(mz, o.z)
            nx, ny, nz = max(nx, o.x), max(ny, o.y), max(nz, o.z)
        if abs(nx - mx) > 0:
            mask = mask + "x"
        if abs(ny - my) > 0:
            mask = mask + "y"
        if abs(nz - mz) > 0:
            mask = mask + "z"
        return mask

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
            arrpart.attrib.loc += self.loc_for_offset(
                o, dict["length"], mask, ratio=dict["ratio"]
            )
            arrpart.attrib.matrix = self.matrix_for_offset(
                o, mask, invert=dict["invert"], tilt=dict["tilt"]
            )
            arrpart.attrib.colour = dict["colour"]
            arrows.append(str(arrpart))
        return "".join(arrows)

    def dict_for_line(self, line, invert, ratio, colour=None, tilt=0):
        item = {}
        item["line"] = line
        c = colour if colour is not None else self.colour
        item["colour"] = c
        item["length"] = self.length
        item["offset"] = copy.copy(self.offset)
        item["invert"] = invert
        item["ratio"] = ratio
        item["tilt"] = tilt
        return item


def arrows_for_step(arrow_ctx, step, as_lpub=True, only_arrows=False, as_dict=False):
    step_lines = []
    arrow_parts = []
    arrow_dict = []
    lines = step.splitlines()
    in_arrow = False
    offset = Vector(0, 0, 0)
    arrow_ratio = 0.5
    arrow_tilt = 0
    arrow_colour = arrow_ctx.colour
    for line in lines:
        lineType = int(line.lstrip()[0] if line.lstrip() else -1)
        if lineType == 0:
            ls = line.upper().split()
            if "!PY ARROW" in line:
                if in_arrow == False and "BEGIN" in line:
                    in_arrow = True
                    arrow_ctx.offset = []
                    idx = 0
                    try:
                        arrow_ctx.offset.append(
                            Vector(
                                float(ls[4 + idx]),
                                float(ls[5 + idx]),
                                float(ls[6 + idx]),
                            )
                        )
                    except:
                        pass
                    if len(ls) > 7 + idx:
                        try:
                            arrow_ctx.offset.append(
                                Vector(
                                    float(ls[7 + idx]),
                                    float(ls[8 + idx]),
                                    float(ls[9 + idx]),
                                )
                            )
                        except:
                            pass
                    if len(ls) > 10 + idx:
                        try:
                            arrow_ctx.offset.append(
                                Vector(
                                    float(ls[10 + idx]),
                                    float(ls[11 + idx]),
                                    float(ls[12 + idx]),
                                )
                            )
                        except:
                            pass
                elif in_arrow and "END" in line:
                    in_arrow = False
                    continue
                if "COLOUR" in line:
                    try:
                        arrow_colour = int(value_after_token(ls, "COLOUR"))
                    except:
                        pass
                    if not in_arrow:
                        arrow_ctx.colour = arrow_colour
                        continue
                if "LENGTH" in line:
                    try:
                        arrow_ctx.length = int(value_after_token(ls, "LENGTH"))
                    except:
                        pass
                    if not in_arrow:
                        continue
                if "RATIO" in line:
                    try:
                        arrow_ratio = float(value_after_token(ls, "RATIO"))
                    except:
                        pass
                    if not in_arrow:
                        continue
                if "TILT" in line:
                    try:
                        arrow_tilt = float(value_after_token(ls, "TILT"))
                    except:
                        pass
                    if not in_arrow:
                        continue

        if in_arrow and lineType == 1:
            item = arrow_ctx.dict_for_line(
                line,
                invert=False,
                ratio=arrow_ratio,
                colour=arrow_colour,
                tilt=arrow_tilt,
            )
            arrow_parts.append(item)
            item = arrow_ctx.dict_for_line(
                line,
                invert=True,
                ratio=arrow_ratio,
                colour=arrow_colour,
                tilt=arrow_tilt,
            )
            arrow_parts.append(item)
        elif in_arrow == False:
            if not only_arrows:
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
            for i, part in enumerate(arrow_parts):
                ad = {}
                ldrpart = LDRPart()
                ldrpart.wrapcallout = False
                ldrpart.from_str(part["line"])
                mask = arrow_ctx._mask_axis(part["offset"])
                offset = arrow_ctx.part_loc_for_offset(part["offset"][0], mask)
                ldrpart.attrib.loc += offset
                ad["offset"] = offset
                if i % 2 == 0:
                    step_lines.append(str(ldrpart).strip("\n"))
                ad["part"] = str(ldrpart)
                arrow_part = arrow_ctx.arrow_from_dict(part)
                step_lines.append(arrow_part.strip("\n"))
                ad["arrow"] = arrow_part
                arrow_dict.append(ad)

    else:
        if "NOFILE" not in step:
            if len(step_lines) > 0:
                step_lines.append("0 STEP")
    if as_dict:
        return arrow_dict
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


def remove_offset_parts(parts, oparts, arrow_dict, as_str=False):
    """Removes parts which are offset versions of the same part."""
    pp = ldrlist_from_parts(parts)
    op = ldrlist_from_parts(oparts)
    offsets = []
    arrows = []
    # aparts = []
    for ad in arrow_dict:
        p = LDRPart().from_str(ad["part"])
        offset = ad["offset"] * p.attrib.matrix
        offsets.append(offset)
        a = LDRPart().from_str(ad["arrow"])
        arrows.append(a.name)
        # aparts.append(a)
    np = []
    for p in pp:
        matched = False
        for o in op:
            if not o.name == p.name or not o.attrib.colour == p.attrib.colour:
                continue
            elif p.name in arrows:
                continue
            else:
                v1 = p.attrib.loc * p.attrib.matrix
                v2 = o.attrib.loc * o.attrib.matrix
                for offset in offsets:
                    # va = offset * arrow.attrib.matrix
                    # vm = v2.copy() + va
                    # print("part1: %s / %s" % (str(p), str(v1)))
                    # print("part2: %s / %s" % (str(o), str(v2)))
                    vd = abs(v2.copy() - v1.copy())
                    vo = abs(offset)
                    # print("offset: %s  vm: %s  vd: %s vo: %s\n" % (str(offset), str(vm), str(vd), str(vo)))
                    # if v1.almost_same_as(vm, tolerance=0.1):
                    if abs(vd - vo) < 0.1:
                        matched = True

        if not matched:
            np.append(p)
    if as_str:
        return ldrstring_from_list(np)
    return np

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
# LDraw colour class

import os
import string

from ldrawpy import *


class LDRColour(object):
    """LDraw colour helper class.  This class can be used to store a
    colour and to perform conversions among:
      LDraw colour code, Bricklink colour code, colour name,
      RGB floating point, RGB hex"""

    def __init__(self, colour=LDR_DEF_COLOUR):
        self.code = LDR_DEF_COLOUR
        self.r = 0.8
        self.g = 0.8
        self.b = 0.8
        if isinstance(colour, (tuple, list)):
            if (colour[0] > 1.0) or (colour[1] > 1.0) or (colour[2] > 1.0):
                self.r = colour[0] / 255.0
                self.g = colour[1] / 255.0
                self.b = colour[2] / 255.0
                if self.r > 1.0:
                    self.r = 1.0
                if self.g > 1.0:
                    self.g = 1.0
                if self.b > 1.0:
                    self.b = 1.0
            else:
                self.r = colour[0]
                self.g = colour[1]
                self.b = colour[2]
            rgbstr = self.as_hex().lower()
            newCode = LDR_DEF_COLOUR
            for code, hexrgb in LDR_COLOUR_RGB.items():
                if rgbstr == hexrgb.lower():
                    newCode = code
            if newCode != LDR_DEF_COLOUR:
                self.code = newCode

        else:
            if isinstance(colour, str):
                self.code = LDRColour.ColourCodeFromString(colour)
                if self.code == LDR_DEF_COLOUR:
                    self.r, self.g, self.b = LDRColour.RGBFromHex(colour)
            elif isinstance(colour, LDRColour):
                self.code = colour.code
            else:
                self.code = colour
        self.code_to_rgb()

    def __repr__(self):
        return "%s(%s, r: %.2f g: %.2f b: %.2f, #%s)" % (
            self.__class__.__name__,
            self.code,
            self.r,
            self.g,
            self.b,
            self.as_hex(),
        )

    def __str__(self):
        return LDRColour.SafeLDRColourName(self.code)

    def __eq__(self, other):
        if isinstance(other, int):
            if self.code == other:
                return True
        if isinstance(other, LDRColour):
            if self.code == other.code and self.code != LDR_DEF_COLOUR:
                return True
            if self.r == other.r and self.g == other.g and self.b == other.b:
                return True
        return False

    def code_to_rgb(self):
        if self.code == LDR_DEF_COLOUR:
            self.r = 0.62
            self.g = 0.62
            self.b = 0.62
            return
        if self.code in LDR_COLOUR_RGB:
            rgb = LDR_COLOUR_RGB[self.code]
            [rd, gd, bd] = tuple(int(rgb[i : i + 2], 16) for i in (0, 2, 4))
            self.r = float(rd) / 255.0
            self.g = float(gd) / 255.0
            self.b = float(bd) / 255.0

    def as_tuple(self):
        return (self.r, self.g, self.b)

    def as_hex(self):
        return "%02X%02X%02X" % (
            int(self.r * 255.0),
            int(self.g * 255.0),
            int(self.b * 255.0),
        )

    def ldvcode(self):
        pc = self.code
        if self.code >= 1000:
            pc = LDR_DEF_COLOUR
        return pc

    def name(self):
        theName = LDRColour.SafeLDRColourName(self.code)
        if theName == "":
            return self.as_hex()
        return theName

    def high_contrast_complement(self):
        level = self.r * self.r + self.g * self.g + self.b * self.b
        if level < 1.25:
            return (1.0, 1.0, 1.0)
        return (0.0, 0.0, 0.0)

    def to_bricklink(self):
        for blcode, ldrcode in BL_TO_LDR_COLOUR.items():
            if ldrcode == self.code:
                return blcode
        return 0

    @staticmethod
    def SafeLDRColourName(ldrCode):
        if ldrCode in LDR_COLOUR_NAME:
            return LDR_COLOUR_NAME[ldrCode]
        elif ldrCode in LDR_COLOUR_TITLE:
            return LDR_COLOUR_TITLE[ldrCode]
        return ""

    @staticmethod
    def SafeLDRColourRGB(ldrCode):
        if ldrCode in LDR_COLOUR_RGB:
            return LDR_COLOUR_RGB[ldrCode]
        return "FFFFFF"

    @staticmethod
    def BLColourCodeFromLDR(colour):
        for blcode, ldrcode in BL_TO_LDR_COLOUR.items():
            if ldrcode == colour:
                return blcode
        return 0

    @staticmethod
    def ColourCodeFromString(colourStr):
        for code, label in LDR_COLOUR_NAME.items():
            if label.lower() == colourStr.lower():
                return code
        if len(colourStr) == 6 or len(colourStr) == 7:
            hs = colourStr.lstrip("#").lower()
            if not all(c in string.hexdigits for c in hs):
                return LDR_DEF_COLOUR
            for code, rgbhex in LDR_COLOUR_RGB.items():
                if hs == rgbhex.lower():
                    return code
        return LDR_DEF_COLOUR

    @staticmethod
    def RGBFromHex(hexStr):
        if len(hexStr) < 6:
            return 0, 0, 0
        hs = hexStr.lstrip("#")
        if not all(c in string.hexdigits for c in hs):
            return 0, 0, 0
        [rd, gd, bd] = tuple(int(hs[i : i + 2], 16) for i in (0, 2, 4))
        r = float(rd) / 255.0
        g = float(gd) / 255.0
        b = float(bd) / 255.0
        return r, g, b


def FillColoursFromLDRCode(ldrCode):
    fillColours = []
    if ldrCode in LDR_COLOUR_RGB:
        fillColours.append(LDR_COLOUR_RGB[ldrCode])
    elif ldrCode in LDR_FILL_CODES:
        fillColours = LDR_FILL_CODES[ldrCode]
    return [LDRColour.RGBFromHex(x) for x in fillColours]


def FillTitlesFromLDRCode(ldrCode):
    fillTitles = []
    if ldrCode in LDR_COLOUR_RGB:
        fillTitles.append(LDR_COLOUR_NAME[ldrCode])
    elif ldrCode in LDR_FILL_TITLES:
        fillTitles = LDR_FILL_TITLES[ldrCode]
    return fillTitles

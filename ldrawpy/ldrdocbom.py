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
# LDRDocBOM class

import os, tempfile
import copy
import datetime
import crayons
from collections import defaultdict

from reportlab.pdfgen import canvas

from datetime import datetime
from PIL import Image, ImageOps, ImageChops, ImageFilter, ImageEnhance
from toolbox import *
from .constants import *
from .ldrprimitives import LDRPart
from .ldrmodel import LDRModel
from .ldrarrows import *
from .ldrdocstyles import *
from .ldrdochelpers import CalloutArrows, get_centroids_of_colour

from pdfdoc import *


class LDRDocBOM(TableGrid):
    """ A subclass of TableGrid used to draw a bill of materials. """
    PARAMS = {
        "dpi": 300,
    }

    def __init__(self, width=0, height=0, style=None, **kwargs):
        super().__init__(width, height)
        apply_params(self, kwargs)
        self.stylesheet = self.stylesheet
        if style is not None:
            self.style.set_with_dict(style)
        self.fill_dir = "column-wise"
        # self.fill_dir = "row-wise"
        self.auto_adjust = True

    def set_bom_parts(self, bom):
        self.clear()
        for i, p in enumerate(bom):
            pc = TableColumn(0, 0, self.stylesheet["STEP_PLI_ITEM_STYLE"])
            fn = p["filename"]
            pimage = ImageRect(
                0, 0, fn, self.stylesheet["STEP_PLI_IMAGE_STYLE"], dpi=self.dpi
            )
            pimage.auto_size = False
            pqty = TextRect(
                0, 0, str(p["qty"]) + "x", self.stylesheet["STEP_PLI_TEXT_STYLE"]
            )
            pc.add_row("Image", pimage)
            pc.add_row("Qty", pqty)
            pc.set_row_height("Image", CONTENT_SIZE)
            pc.set_row_height("Qty", CONTENT_SIZE)
            self.add_cell("BOM%d" % (i + 1), pc)

    def set_size_constraints(self, w, h):
        self.width_constraint = w
        self.height_constraint = h
        self.rect.set_size(w, h)

    def set_position(self, pos):
        self.rect.move_top_left_to(pos)


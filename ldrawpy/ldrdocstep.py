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
# LDRDocStep class

import os, tempfile
import copy
import datetime
import crayons
from collections import defaultdict

from reportlab.pdfgen import canvas

from datetime import datetime
from PIL import Image, ImageOps, ImageChops, ImageFilter, ImageEnhance
from toolbox import *
from .ldrprimitives import LDRPart
from .ldrmodel import LDRModel
from .ldrarrows import *
from .ldrdocstyles import *
from .constants import *
from .ldrdochelpers import CalloutArrows, get_centroids_of_colour, RotationIcon

from pdfdoc import *


class LDRDocStep(LayoutCell):
    PARAMS = {
        "show_pli": True,
        "pli_vert_align": "top",
        "pli_horz_align": "left",
        "assem_vert_align": "bottom",
        "assem_horz_align": "centre",
        "callout_location": "top",
        "dpi": 300,
    }

    def __init__(self, width=0, height=0, style=None, **kwargs):
        super().__init__(width, height)
        apply_params(self, kwargs)
        self.stylesh = self.stylesheet
        # define the cells in a step
        self.step_num = TextRect(0, 0, "", self.stylesh["STEP_NUM_STYLE"])
        self.pli = TableGrid(2.75 * inch, 4 * inch, self.stylesh["STEP_PLI_STYLE"])
        self.pli.fill_dir = "row-wise"
        self.assem = ImageRect(
            0, 0, "", dpi=self.dpi, style=self.stylesh["STEP_ASSEM_IMAGE_STYLE"]
        )
        self.assem.auto_size = False
        self.roticon = RotationIcon(
            style=self.stylesh["ROTATE_ICON_STYLE"],
            arrow_style=self.stylesh["ROTATE_ARROW_STYLE"],
        )
        self.callout = TableGrid(
            4.35 * inch, 1 * inch, style=self.stylesh["CALLOUT_STYLE_L1"]
        )
        self.callout.fill_dir = "row-wise"
        self.qty = TextRect(0, 0, "", style=self.stylesh["CALLOUT_QTY_STYLE"])
        # add the cells to a LayoutCell
        self.add_cell("StepNum", self.step_num, constraints=["top left"])
        self.add_cell("PLI", self.pli, constraints=["top left to StepNum top right"])
        self.add_cell("Callout", self.callout, constraints=["top right to top right"])
        self.add_cell(
            "StepModel", self.assem, constraints=["centre", "below PLI Callout StepNum"]
        )
        self.add_cell(
            "Qty", self.qty, constraints=["bottom left to StepModel bottom right"]
        )
        self.add_cell(
            "RotateIcon",
            self.roticon,
            constraints=["rightof StepNum", "bottom to bottom"],
        )
        self.set_cell_visible("Callout", False)
        self.set_cell_visible("Qty", False)
        self.set_cell_visible("RotateIcon", False)
        self.set_layout()

    def set_layout(self):
        if self.callout_location == "top":
            self.set_top_side_callout()
        elif self.callout_location == "right":
            self.set_right_side_callout()
        elif self.callout_location == "bottom":
            self.set_bottom_side_callout()
        elif self.callout_location == "preview":
            self.set_top_side_preview()

    def set_top_side_preview(self):
        self.callout.fill_dir = "row-wise"
        self.set_cell_constraints("StepNum", constraints=["top left"], order=0)
        self.set_cell_constraints(
            "PLI", constraints=["top left to StepNum top right"], order=3
        )
        self.set_cell_order("RotateIcon", 2)
        self.set_cell_constraints(
            "Callout", constraints=["top centre to top centre"], order=2
        )
        self.set_cell_constraints(
            "StepModel",
            constraints=[
                "between_horz parent_left and parent_right",
                "below PLI Callout StepNum",
            ],
            order=4,
        )
        self.set_cell_constraints(
            "Qty", constraints=["bottom left to StepModel bottom right"], order=5
        )
        self.assem.style.set_tb_margins(0.5 * inch)

    def set_top_side_callout(self):
        self.callout.fill_dir = "row-wise"
        self.set_cell_constraints("StepNum", constraints=["top left"], order=0)
        self.set_cell_constraints(
            "PLI", constraints=["top left to StepNum top right"], order=1
        )
        self.set_cell_order("RotateIcon", 2)
        self.set_cell_constraints(
            "Callout", constraints=["top right to top right"], order=3
        )
        self.set_cell_constraints(
            "StepModel",
            constraints=[
                "between_horz parent_left and parent_right",
                "below PLI Callout StepNum",
            ],
            order=4,
        )
        self.set_cell_constraints(
            "Qty", constraints=["bottom left to StepModel bottom right"], order=5
        )
        self.assem.style.set_tb_margins(0.5 * inch)

    def set_right_side_callout(self):
        self.callout.fill_dir = "column-wise"
        self.set_cell_constraints("StepNum", constraints=["top left"], order=0)
        self.set_cell_constraints(
            "PLI", constraints=["top left to StepNum top right"], order=1
        )
        self.set_cell_order("RotateIcon", 2)
        self.set_cell_constraints(
            "Callout", constraints=["top right to top right"], order=3
        )
        self.set_cell_constraints(
            "StepModel",
            constraints=[
                "between_horz parent_left and Callout parent_right",
                "below PLI StepNum",
            ],
            order=4,
        )
        self.set_cell_constraints(
            "Qty", constraints=["bottom left to StepModel bottom right"], order=5
        )
        self.assem.style.set_tb_margins(0.5 * inch)
        self.callout.height_constraint = 6 * inch

    def set_bottom_side_callout(self):
        self.callout.fill_dir = "row-wise"
        self.set_cell_constraints("StepNum", constraints=["top left"], order=0)
        self.set_cell_constraints(
            "PLI", constraints=["top left to StepNum top right"], order=1
        )
        self.set_cell_order("RotateIcon", 2)
        self.set_cell_constraints(
            "StepModel",
            constraints=[
                "between_horz parent_left and parent_right",
                "below PLI StepNum",
            ],
            order=3,
        )
        self.set_cell_constraints(
            "Callout", constraints=["centre", "below StepModel"], order=4
        )
        self.set_cell_constraints(
            "Qty", constraints=["bottom left to StepModel bottom right"], order=5
        )
        self.assem.style.set_tb_margins(0.5 * inch)

    def set_size_constraints(self, w, h):
        self.width_constraint = w
        self.height_constraint = h
        self.rect.set_size(w, h)
        self.fixed_rect.set_size(w, h)

    def set_debug_rects(self, show=False):
        self.step_num.show_debug_rects = show
        self.pli.show_debug_rects = show
        self.assem.show_debug_rects = show
        self.callout.show_debug_rects = show

    def set_style_from_level(self, level):
        if level == 1:
            self.style.set_with_dict(self.stylesh["STEP_L1_STYLE"])
        elif level == 2:
            self.style.set_with_dict(self.stylesh["STEP_L2_STYLE"])
        elif level == 3:
            self.style.set_with_dict(self.stylesh["STEP_L3_STYLE"])
        else:
            self.style.set_with_dict(self.stylesh["STEP_L0_STYLE"])

    def set_callout_style_from_level(self, level):
        if level == 1:
            self.callout.style.set_with_dict(self.stylesh["CALLOUT_STYLE_L1"])
        elif level == 2:
            self.callout.style.set_with_dict(self.stylesh["CALLOUT_STYLE_L2"])
        elif level == 3:
            self.callout.style.set_with_dict(self.stylesh["CALLOUT_STYLE_L3"])
        else:
            self.callout.style.set_with_dict(self.stylesh["CALLOUT_STYLE_L0"])

    def set_step_item_style(self, callout_level=0):
        if callout_level:
            if callout_level == 1:
                s = "CALLOUT_STYLE_L1"
            elif callout_level == 2:
                s = "CALLOUT_STYLE_L2"
            elif callout_level == 3:
                s = "CALLOUT_STYLE_L3"
            font = self.stylesh[s]["font"]
            font_colour = self.stylesh[s]["font-colour"]
            font_size = self.stylesh[s]["font-size"]
            backgnd = self.stylesh[s]["background-colour"]
            self.step_num.style.set_attr("font", font)
            self.step_num.style.set_attr("font-colour", font_colour)
            self.step_num.style.set_attr("font-size", font_size)
            self.step_num.style.set_attr("background-colour", backgnd)
            self.assem.style.set_attr("background-colour", backgnd)
            self.assem.style.set_with_dict(self.stylesh["CALLOUT_ASSEM_IMAGE_STYLE"])
        else:
            self.step_num.style.set_with_dict(self.stylesh["STEP_NUM_STYLE"])
            self.assem.style.set_with_dict(self.stylesh["STEP_ASSEM_IMAGE_STYLE"])

    def show_pli(self):
        self.set_cell_visible("PLI", True)

    def hide_pli(self):
        self.set_cell_visible("PLI", False)

    def show_callout(self):
        self.set_cell_visible("Callout", True)

    def hide_callout(self):
        self.set_cell_visible("Callout", False)

    def show_step_num(self):
        self.set_cell_visible("StepNum", True)

    def hide_step_num(self):
        self.set_cell_visible("StepNum", False)

    def show_qty(self):
        self.set_cell_visible("Qty", True)

    def hide_qty(self):
        self.set_cell_visible("Qty", False)

    def show_rotate_icon(self):
        self.set_cell_visible("RotSpacer", True)
        self.set_cell_visible("RotateIcon", True)

    def hide_rotate_icon(self):
        self.set_cell_visible("RotSpacer", False)
        self.set_cell_visible("RotateIcon", False)

    def set_assem_image(self, image):
        self.assem.dpi = self.dpi
        self.assem.filename = image

    def set_step_num(self, stepnum):
        self.step_num.text = str(stepnum)

    def set_pli(self, pli):
        """ PLI must be a list of dictionaries. Each dictionary must have keys 
        "qty" and "filename". """
        if self.show_pli:
            self.pli.clear()
            if not self.is_cell_visible("Callout"):
                self.pli.width_constraint = 4.25 * inch
            for i, p in enumerate(pli):
                pc = TableColumn(0, 0, self.stylesh["STEP_PLI_ITEM_STYLE"])
                fn = p["filename"]
                pimage = ImageRect(
                    0, 0, fn, self.stylesh["STEP_PLI_IMAGE_STYLE"], dpi=self.dpi
                )
                pimage.auto_size = False
                pqty = TextRect(
                    0, 0, str(p["qty"]) + "x", self.stylesh["STEP_PLI_TEXT_STYLE"]
                )
                pc.add_row("Image", pimage)
                pc.add_row("Qty", pqty)
                pc.set_row_height("Image", CONTENT_SIZE)
                pc.set_row_height("Qty", CONTENT_SIZE)
                self.pli.add_cell("PLI%d" % (i + 1), pc)

    def set_position(self, pos):
        self.rect.move_top_left_to(pos)

    def optimize_layout(self, tpw):
        """ Optimize the layout of cells in the document step. 
        The goal is to minimize the height of the document step container and 
        minimize the wasted space between the PLI and Callout cells for a more
        balanced appearance """

        self.set_layout()
        if not self.is_cell_visible("Callout") or not self.is_cell_visible("PLI"):
            # trigger auto-sizing and layout of cells, but reset the width since
            # it will be reduced by the fact there is no callout
            self.set_size_constraints(tpw, 5 * inch)
            w, h = self.get_content_size()
            self.is_fixed_width = True
            self.fixed_rect.width = tpw
            return

        self.set_size_constraints(tpw, 5 * inch)
        sw, sh = self.step_num.get_content_size()
        pw = tpw - sw
        gutter = 0.04
        self.pli.auto_adjust = True
        self.callout.auto_adjust = True

        def get_score_for_layout():
            self.set_size_constraints(tpw, 5 * inch)
            score, best_score, best_ratio = 0, -1000, 0.1
            for ratio in [x * 0.05 for x in range(3, 16)]:
                gw = ratio - gutter / 2
                wpli = (ratio - gutter / 2) * pw
                wcallout = (1 - (ratio + gutter / 2)) * pw
                self.pli.width_constraint = wpli
                if self.pli.min_width:
                    self.pli.width_constraint = max(wpli, self.pli.min_width)
                self.callout.width_constraint = wcallout
                w, h = self.get_content_size()
                wp = self.pli.rect.width
                wc = self.callout.rect.width
                margin = pw - wp - wc
                overlap = self.has_overlapped_cells()
                clipped = self.has_clipped_cells()
                if not clipped and not overlap:
                    score = (wp + wc) / pw
                    score *= 1.0 - self.get_whitespace_ratio()
                    if score > best_score:
                        best_score = score
                        best_ratio = ratio
            return best_score, best_ratio

        self.callout_location = "top"
        self.set_top_side_callout()
        top_score, top_ratio = get_score_for_layout()
        self.callout_location = "right"
        self.set_right_side_callout()
        right_score, right_ratio = get_score_for_layout()
        if top_score > right_score and top_score > -1000:
            self.callout_location = "top"
            self.set_top_side_callout()
            best_ratio = top_ratio
            best_score = top_score
        elif right_score > top_score and right_score > -1000:
            self.callout_location = "right"
            self.set_right_side_callout()
            best_ratio = right_ratio
            best_score = right_score
        else:
            self.callout_location = "bottom"
            self.set_bottom_side_callout()
            self.pli.width_constraint = pw
            self.callout.width_constraint = pw
            w, h = self.get_content_size()
            return
        gw = best_ratio - gutter / 2
        wpli = (best_ratio - gutter / 2) * pw
        wcallout = (1 - (best_ratio + gutter / 2)) * pw
        self.pli.width_constraint = wpli
        self.callout.width_constraint = wcallout
        w, h = self.get_content_size()
        if w > tpw:
            print("ERROR: exceeded width limit %.1f > %.1f" % (w, tpw))
            wpli = 0.48 * pw
            wcallout = 0.48 * pw
            self.set_size_constraints(tpw, 7 * inch)
            self.pli.width_constraint = wpli
            self.callout.width_constraint = wcallout
            w, h = self.get_content_size()
            print("RESET: to %.1f" % (w))


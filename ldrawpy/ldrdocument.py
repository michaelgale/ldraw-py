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
# LDraw Instructions Document generator

import os, tempfile
import copy
import datetime
import crayons as cr
from collections import defaultdict

from reportlab.pdfgen import canvas

from datetime import datetime
from PIL import Image, ImageOps, ImageChops, ImageFilter, ImageEnhance
from toolbox import *
from .constants import *
from .ldrprimitives import LDRPart
from .ldrhelpers import *
from .ldrmodel import LDRModel
from .ldrdocstep import LDRDocStep
from .ldvrender import LDViewRender
from .ldrarrows import *
from .ldrdocstyles import *
from .ldrdochelpers import CalloutArrows, get_centroids_of_colour, RotationIcon
from .ldrdocbom import LDRDocBOM

from pdfdoc import *


def _coord_str(x, y=None, sep=", "):
    c = None
    if isinstance(x, (tuple, list)):
        a, b = float(x[0]), float(x[1])
        if len(x) == 3:
            c = float(x[2])
            sc = ("%f" % (c)).rstrip("0").rstrip(".")
    else:
        a, b = float(x), float(y)
    sa = ("%f" % (a)).rstrip("0").rstrip(".")
    sb = ("%f" % (b)).rstrip("0").rstrip(".")
    s = []
    s.append(str(cr.green("%s" % (sa))))
    s.append(sep)
    s.append(str(cr.green("%s" % (sb))))
    if c is not None:
        s.append(sep)
        s.append(str(cr.green("%s" % (sc))))
    return "".join(s)


class LDRDocument(Document):
    PARAMS = {
        "dpi": 200,
        "default_aspect": (-40, 60, 0),
        "pli_aspect": (-25, -40, 0),
        "pli_scale": 0.60,
        "assem_scale": 0.75,
        "callout_scale": 0.75,
        "preview_assem_scale": 0.65,
        "callout_arrow_offset": 0.1 * inch,
        "show_page_number": True,
        "cache_path": "~/tmp/imagecache",
        "stylesheet_path": "~/tmp/imagecache/stylesheet.yml",
    }

    def __init__(self, ldrfile, **kwargs):
        # self.filename = ldrfile.replace(".ldr", ".pdf")
        super().__init__(filename=ldrfile.replace(".ldr", ".pdf"))
        _, self.title = split_path(ldrfile)
        self.title = self.title.lower().replace(".ldr", "")
        apply_params(self, kwargs)
        self.model = LDRModel(ldrfile)
        self.ldv = LDViewRender(output_path=self.cache_path, dpi=self.dpi)
        self.ldv.log_output = False
        self.stylesheet = DocStyleSheet(filename=full_path(self.stylesheet_path))
        self.model.pli_aspect = self.pli_aspect
        self.model.global_aspect = self.default_aspect
        self.docstep_stack = []
        self.section_list = ["0", "1", "2", "3"]
        self.arrowctx = ArrowContext()
        self.background_colours = []

    def set_stylesheet(self, stylesheet_file):
        self.stylesheet = DocStyleSheet(filename=full_path(stylesheet_file))

    def _init_callbacks(self):
        st = self.stylesheet
        # page background callbacks
        l0 = PageBackgroundCallback(style=st["STEP_L0_STYLE"])
        l0.sections_active = ["0"]
        l1 = PageBackgroundCallback(style=st["STEP_L1_STYLE"])
        l1.sections_active = ["1"]
        l2 = PageBackgroundCallback(style=st["STEP_L2_STYLE"])
        l2.sections_active = ["2"]
        l3 = PageBackgroundCallback(style=st["STEP_L3_STYLE"])
        l3.sections_active = ["3"]
        # conveniently store the background colours for use elsewhere
        self.background_colours = []
        self.background_colours.append(st["STEP_L0_STYLE"]["background-colour"])
        self.background_colours.append(st["STEP_L1_STYLE"]["background-colour"])
        self.background_colours.append(st["STEP_L2_STYLE"]["background-colour"])
        self.background_colours.append(st["STEP_L3_STYLE"]["background-colour"])

        # page number callback
        pn = PageNumberCallback(
            show_in_footer=True, style=self.stylesheet["PAGE_NUM_STYLE"]
        )
        self.page_start_callbacks = [l0, l1, l2, l3, pn]
        
        # column divider callback
        cl = ColumnLineCallback(style=st["COLUMN_STYLE"])
        self.column_end_callbacks = [cl]

    def _init_model(self):
        self.model.global_scale = self.assem_scale
        print("DOC: Parsing model file %s..." % (cr.blue(self.title)))
        self.model.parse_file()
        print("DOC: Rendering PLI images...")
        self.render_pli_images()

    def init_document(self):
        self._init_callbacks()
        self._init_model()
        gw = self.stylesheet["COLUMN_STYLE"].get_attr("gutter-width")
        self.style["gutter-width"] = gw

    def _pprint_step(self, idx, s):
        stn = cr.yellow(s["step"]) if s["model"] != "root" else cr.cyan(s["step"])
        stc = (
            cr.yellow(s["num_steps"])
            if s["model"] != "root"
            else cr.cyan(s["num_steps"])
        )
        print(
            "DOC: idx=%s Processing step %s of %s in model %-16s (level %s) page: %s column: %s"
            % (
                str(cr.cyan(str(idx))),
                str(stn),
                str(stc),
                str(cr.red(s["model"])),
                str(cr.yellow(s["level"])),
                str(cr.cyan(str(self.page_number))),
                str(cr.cyan(str(self.column))),
            )
        )

    def _pprint_assem(self, fn, scale, aspect):
        print(
            "DOC:   Assembly image: %s scale %s / aspect (%s)"
            % (str(cr.blue(fn)), str(cr.yellow(str(scale))), _coord_str(aspect))
        )

    def _create_callout_cell(self):
        ds = LDRDocStep(3 * inch, 2 * inch, dpi=self.dpi, stylesheet=self.stylesheet)
        ds.set_cell_constraints("StepNum", ["top left"])
        ds.set_cell_constraints("StepModel", ["top left to StepNum top right"])
        ds.set_cell_visible("PLI", False)
        return ds

    def fn_pli(self, part, with_path=False):
        """ Returns the filename of rendered PLI image. It constructs the filename
        from either a LDRPart instance or BOMPart instance."""
        from brickbom import BOM, BOMPart

        if isinstance(part, LDRPart):
            name = part.id
            colour = part.attrib.colour
        elif isinstance(part, BOMPart):
            name = part.id
            colour = part.colour.code
        elif isinstance(part, str):
            p = LDRPart.from_str(part)
            name = p.name
            colour = part.attrib.colour
        fn = "pli_%s_%s_%d_%.2f.png" % (name, str(colour), self.dpi, self.pli_scale)
        if with_path:
            return full_path(self.cache_path + os.sep + fn)
        return fn

    def render_pli_images(self):
        """ Renders all of parts in the model as individual image files for use
        with either PLI blocks or BOM pages."""
        self.ldv.set_scale(self.pli_scale)
        for part in self.model.bom.parts:
            if part.id in self.model.pli_exceptions:
                rm = euler_to_rot_matrix(self.model.pli_exceptions[part.id])
            else:
                rm = euler_to_rot_matrix(self.pli_aspect)
            fn = self.fn_pli(part, with_path=True)
            p = LDRPart(part.colour.code, name=part.id)
            p.attrib.matrix = rm
            self.ldv.render_from_str(str(p), fn)

    def fn_assem(self, step_dict, other=None, with_path=False, scale=None):
        """ Returns the filename of a rendered assembly image.  It constructs the
        filename based on a passed in dictionary with keys "model", "step", "scale",
        "aspect".  If other is specified, then it appends the text of other to the
        title part of the filename. The dictionary is typically supplied from the
        unwrapped model. step_dict can also be supplied as an integer index for
        convenient access to the step dictionary in the unwrapped model."""
        if isinstance(step_dict, int):
            sd = self.model[step_dict]
        else:
            sd = step_dict
        scale = scale if scale is not None else sd["scale"]
        rx, ry, rz = sd["aspect"]
        if other is not None:
            title = self.title + other
        else:
            title = self.title
        if sd["model"] != "root":
            subname = sd["model"]
            subname = subname.replace(".ldr", "")
            subname = subname.replace(" ", "_")
            title = "%s_%s" % (title, subname)
        fn = "%s_assem_%s_%d_%.2f_%.0f_%.0f_%.0f.png" % (
            title,
            str(sd["step"]),
            self.dpi,
            scale,
            rx,
            ry,
            rz,
        )
        if with_path:
            return full_path(self.cache_path + os.sep + fn)
        return fn

    def render_bom(self, pos=None):
        bom = LDRDocBOM(
            self.inset_rect.width,
            self.inset_rect.height,
            dpi=self.dpi,
            stylesheet=self.stylesheet,
        )
        bom.style.set_attr("horz-align", "left")
        bom.style.set_attr("vert-align", "bottom")
        bom_parts = []
        self.model.bom.sort_description()
        self.model.bom.sort_category()
        self.model.bom.sort_colour()
        for p in self.model.bom.parts:
            fn = self.fn_pli(p, with_path=True)
            bom_parts.append({"qty": p.qty, "filename": fn})
        bstart = 0
        blen = len(self.model.bom.parts)
        bstep = 8
        bstop = bstep
        done = False
        # progressively add segments until we spill over a page/column
        # boundary and need to force a draw in canvas and a page break
        while not done:
            bom.set_bom_parts(bom_parts[bstart:bstop])
            w, h = bom.get_content_size()
            if w < self.inset_rect.width and h < self.inset_rect.height:
                if bstop >= blen:
                    bstop = blen
                    done = True
                else:
                    bstop += bstep
                    if bstop >= blen:
                        bstop = blen
            else:
                self._render_bom_segment(pos, bom, bom_parts[bstart : bstop - bstep])
                bstart = bstop - bstep
                bstop = bstart + bstep
                if bstop >= blen:
                    bstop = blen
                    done = True
        bom.set_bom_parts(bom_parts[bstart:bstop])
        self._render_bom_segment(pos, bom, bom_parts[bstart:bstop])

    def _render_bom_segment(self, pos, bom, bom_parts):
        bom.set_bom_parts(bom_parts)
        if pos is None:
            pos = self.get_top_left()
        w, h = bom.get_content_size()
        bom.rect.move_top_left_to(pos)
        bom.draw_in_canvas(self.c)
        self.page_break()

    def render_assem_preview_image(self, idx, pos=None, as_cell=False):
        """ Renders a preview image of a sub-assembly on the current page canvas."""
        level = self.model[idx + 1]["level"]
        if level > 0:
            subidx = self.model.get_sub_model_assem(self.model[idx + 1]["model"])
        else:
            subidx = self.model.get_sub_model_assem(self.model[idx]["model"])
        subparts = self.model[subidx]["parts"]
        fn = self.fn_assem(subidx, with_path=True, scale=self.preview_assem_scale)
        self.ldv.set_scale(self.preview_assem_scale)
        self.ldv.render_from_parts(subparts, fn)
        tc = TableColumn(0, 0, style=self.stylesheet["PREVIEW_ASSEM_STYLE"])
        # remove the bottom margin if used as a cell within a step
        if as_cell:
            tc.style.set_attr("bottom-margin", 0.0)
        im = ImageRect(
            0,
            0,
            filename=fn,
            dpi=self.dpi,
            style=self.stylesheet["PREVIEW_IMAGE_STYLE"],
        )
        subqty = self.model[subidx]["qty"]
        qty = TextRect(
            0, 0, str(subqty) + "x", style=self.stylesheet["PREVIEW_QTY_STYLE"]
        )
        qty.is_fixed_height = True
        qty.fixed_rect.height = 0.35 * inch
        tc.add_row("Image", im)
        tc.add_row("Qty", qty)
        tc.set_row_height("Image", CONTENT_SIZE)
        tc.set_row_height("Qty", CONTENT_SIZE)
        if subqty > 1:
            tc.set_cell_visible("Qty", True)
        else:
            tc.set_cell_visible("Qty", False)
        if as_cell:
            return tc

        if pos is None:
            pos = self.get_top_left(in_column=True)
        tc.rect.move_top_left_to(pos)
        tc.draw_in_canvas(self.c, auto_size=True, auto_size_anchor="top left")
        border = 2 * tc.style.get_attr("border-width")
        self.cursor_shift_down(tc.total_height + border)

    def render_arrows(self, s, step_image_file):
        """ Inserts arrow proxy parts into the LDraw model to show assembly helper
        arrows.  It interprets custom !PY ARROW meta commands and computes where to
        insert the proxy arrows and temporary location offsets for the parts delimited
        with the !PY ARROW tags."""
        if "!PY ARROW" in s["raw_ldraw"]:
            new_step = arrows_for_step(self.arrowctx, s["raw_ldraw"], as_lpub=False)
            a = self.model.transform_parts(new_step.splitlines(), aspect=s["aspect"])
            ax = self.model.ad_hoc_parse("\n".join(a))
            np = merge_same_parts(s["parts"], ax, as_str=True)
            self.ldv.render_from_str(np, step_image_file)
        else:
            self.ldv.render_from_parts(s["parts"], step_image_file)

    def get_new_part_centroids(self, idx, s, scale):
        """ Renders a special high constrast version of the model at a step location.
        This special render is used to highlight only parts or subassemblies which have
        been added to the step.  All other parts are rendered almost invisible with a 
        special colour code 502 (in LDConfig.ldr).  Image processing is used to find
        the centroids of the new parts marked with colour code 26.  These centroid locations
        can then be used to compute coordinates for items like callout arrows."""
        fncent = self.fn_assem(self.model[idx], with_path=True, scale=scale, other="_x")
        other_parts = self.model.transform_colour(s["parts"], 502)
        if "!PY ARROW" in s["raw_ldraw"]:
            new_step = arrows_for_step(self.arrowctx, s["raw_ldraw"], as_lpub=False)
            a = self.model.transform_parts(new_step.splitlines(), aspect=s["aspect"])
            ax = self.model.ad_hoc_parse("".join(a))
            ay = remove_parts_from_list(ax, [LDRPart(name=x) for x in ARROW_PARTS])
            new_parts = self.model.transform_colour(ay, 26)
            cent_parts = merge_same_parts(other_parts, new_parts, as_str=True)
        else:
            new_parts = self.model.transform_colour(s["step_parts"], 26)
            cent_parts = merge_same_parts(other_parts, new_parts, ignore_colour=True, as_str=True)
        self.ldv.no_lines = True
        self.ldv.render_from_str(cent_parts, fncent)
        centroids = get_centroids_of_colour(fncent, 150, dpi=self.dpi)
        self.ldv.no_lines = False
        return centroids

    def render_callout_arrows(self, s, centroids, ds):
        """ Draws callout arrows from the callout block to the centroid location
        of the part/subassembly in the assembly image block.  The centroids 
        are pre-computed with the get_new_part_centroids methods."""
        if centroids is not None:
            arect = ds.assem.style.get_inset_rect(ds.assem.rect)
            crect = ds.get_cell_rect("Callout")
            if ds.callout_location == "top" or ds.callout_location == "preview":
                x0 = crect.left + crect.width / 2
                y0 = crect.bottom
            elif ds.callout_location == "right":
                x0 = crect.left
                y0 = crect.bottom + crect.height / 2
            elif ds.callout_location == "bottom":
                x0 = crect.left + crect.width / 2
                y0 = crect.top
            ca = CalloutArrows(
                style=self.stylesheet["CALLOUT_ARROW_STYLE"],
                callout_location=ds.callout_location,
                callout_rect=crect,
            )
            ca.style.set_attr("border-colour", self.background_colours[s["level"]])
            ca.origin = (x0, y0)
            if len(centroids):
                for cent in centroids:
                    xc, yc = arect.left + cent[0], arect.top - cent[1]
                    yc += self.callout_arrow_offset
                    ca.endpoints.append((xc, yc))
                ca.draw_in_canvas(self.c)

    def is_layout_changing(self, s):
        return True if "!TWOCOL" in s["raw_ldraw"] or "!ONECOL" in s["raw_ldraw"] else False

    def change_layout(self, s):
        if "!TWOCOL" in s["raw_ldraw"]:
            if self.num_columns != 2:
                self.page_break()
                self.set_columns(2)
        elif "!ONECOL" in s["raw_ldraw"]:
            if self.num_columns != 1:
                self.page_break()
                self.set_columns(1)

    def render_step(self, idx):
        """ Render a single step. Step is specified as an index
        into the unwrapped model. """
        s = self.model[idx]
        parent_level = self.model.callout_parent(idx)
        scale = self.callout_scale if s["callout"] else s["scale"] 
        step_assem_image = self.fn_assem(self.model[idx], with_path=True, scale=scale)
        centroids = None
        
        sw = self.get_column_width()
        cw = self.get_column_width()
        pli_dict = self.docstep_pli(idx)
        self.ldv.set_scale(scale)

        self.render_arrows(s, step_assem_image)
        self._pprint_step(idx, s)
        fn = self.fn_assem(self.model[idx], with_path=False, scale=scale)
        self._pprint_assem(fn, scale, s["aspect"])

        centroids = self.get_new_part_centroids(idx, s, scale)
        # Create a new LDRDocStep and determine which type we need based
        # on callout state
        if idx in self.model.callouts:
            print(
                "DOC:   Callout starting on level %s with parent level %s"
                % (str(cr.green(str(s["callout"]))), str(cr.cyan(str(parent_level))))
            )
            # create a LDRDocStep for future use with a callout container cell enabled
            # push a reference to this LDRDocStep onto a stack
            # no PLI if we're already inside a callout
            callout_before = self.model[idx - 1]["callout"] > 0 if idx > 0 else False
            if callout_before:
                dc = LDRDocStep(cw, 3 * inch, dpi=self.dpi, stylesheet=self.stylesheet)
                dc.set_cell_constraints("StepNum", ["top left"])
                dc.set_cell_constraints("StepModel", ["top left to StepNum top right"])
                dc.set_cell_constraints("Callout", ["rightof StepModel StepNum"])
                dc.set_cell_visible("PLI", False)
            else:
                dc = LDRDocStep(
                    sw,
                    5 * inch,
                    dpi=self.dpi,
                    stylesheet=self.stylesheet,
                )
                dc.set_cell_visible("PLI", True)
            dc.set_callout_style_from_level(s["callout"])
            dc.set_cell_visible("Callout", True)
            print(
                "DOC:   Pushing reference to callout docstep %s to stack"
                % (str(cr.magenta(str("%r" % (dc)))))
            )
            self.docstep_stack.append(dc)

        if s["callout"]:
            ds = self._create_callout_cell()
        else:
            print("DOC:   Normal step at level %s" % (str(cr.white(str(s["level"])))))
            # if there is a pending LDRDocStep on the stack, use that
            # instead of creating a new instance
            if len(self.docstep_stack):
                ds = self.docstep_stack[len(self.docstep_stack) - 1]
                print(
                    "DOC:   Using docstep %s pending on the stack"
                    % (str(cr.magenta(str("%r" % (ds)))))
                )
            else:
                print("DOC:   Creating a new docstep")
                ds = LDRDocStep(sw, 6 * inch, dpi=self.dpi, stylesheet=self.stylesheet)

            ds.set_pli(pli_dict)
            if s["no_pli"]:
                ds.hide_pli()
                ds.show_callout()
                preview_image = self.render_assem_preview_image(idx - 1, as_cell=True)
                ds.set_cell_content("Callout", preview_image)
                ds.callout_location = "preview"
                ds.set_top_side_preview()
        # add the assembly image and step number
        ds.set_assem_image(step_assem_image)
        # if there is only 1 step for this model (usually in a trivial callout)
        # then hide the step number
        if s["callout"]:
            ds.set_style_from_level(s["callout"])
            ds.set_step_item_style(s["callout"])
        else:
            ds.set_style_from_level(s["level"])
            ds.set_step_item_style(s["callout"])
        if s["num_steps"] == 1:
            ds.hide_step_num()
            ds.set_cell_constraints("StepModel", ["top left"])
            ds.assem.style.set_attr("left-padding", 0.1 * inch)
        else:
            ds.set_step_num(s["step"])

        if s["callout"]:
            # if a previous step in the callout ended a child level callout or
            # if we happen to initiate a callout at the very start of the document
            # then pop the stack to pick up the correct reference to the parent step
            callout_idx = idx - 1 if idx > 0 else idx
            if self.model.is_callout_end(callout_idx):
                if len(self.docstep_stack):
                    dc = self.docstep_stack[len(self.docstep_stack) - 1]
                    parent = self.docstep_stack[len(self.docstep_stack) - 2]
                    # before we pop the reference, add the cell to the parent
                    # and set all of content cells and layout constraints
                    print(
                        "DOC:   Retrieving parent docstep %s from stack before popping stack"
                        % (str(cr.magenta(str("%r" % (parent)))))
                    )
                    dc.set_step_num(s["step"])
                    dc.set_assem_image(step_assem_image)
                    dc.set_style_from_level(s["callout"])
                    dc.set_step_item_style(s["callout"])
                    dc.set_cell_constraints("StepNum", ["top left"], order=1)
                    dc.set_cell_constraints(
                        "Callout", ["top left to StepNum top right"], order=2
                    )
                    dc.set_cell_constraints(
                        "StepModel", ["top left to Callout bottom left"], order=3
                    )
                    dc.set_cell_order("PLI", 4)
                    if self.model[idx]["qty"] > 1:
                        dc.qty.text = str(self.model[idx]["qty"]) + "x"
                        dc.show_qty()
                    else:
                        dc.hide_qty()
                    parent.callout.width_constraint = sw
                    parent.callout.height_constraint = 5 * inch
                    parent.callout.auto_adjust = True
                    parent.callout.add_cell("Step%d" % (idx), dc)
                    print(
                        "DOC:   Popping docstep reference %s from stack because callout ended previous"
                        % (str(cr.magenta(str("%r" % (dc)))))
                    )
                    self.docstep_stack.pop()
            else:
                dc = self.docstep_stack[len(self.docstep_stack) - 1]
                # enable a sub assembly qty label if applicable
                if self.model.is_callout_end(idx):
                    print(
                        "DOC:   Pushing last docstep of callout to %s"
                        % (str(cr.magenta(str("%r" % (dc)))))
                    )
                    if self.model[idx]["qty"] > 1:
                        ds.qty.text = str(self.model[idx]["qty"]) + "x"
                        ds.show_qty()
                    else:
                        ds.hide_qty()
                else:
                    print(
                        "DOC:   Pushing docstep of callout to %s"
                        % (str(cr.magenta(str("%r" % (dc)))))
                    )
                dc.callout.add_cell("Step%d" % (idx), ds)

        # if we're rendering a root model step, draw it on the canvas
        else:
            ds.optimize_layout(sw)
            print(
                "DOC:   Rendering step at (%s) with width %s height %s"
                % (
                    _coord_str(self.cursor),
                    str(cr.cyan(str("%.1f" % (ds.total_width)))),
                    str(cr.cyan(str("%.1f" % (ds.total_height)))),
                )
            )
            space = ds.total_height
            if not self.is_enough_space(space) and s["step"] > 1:
                print(
                    "DOC: Column break from page %s, not enough space %s"
                    % (
                        str(cr.magenta(str(self.page_number))),
                        str(cr.cyan(str("%.1f" % (space)))),
                    )
                )
                self.column_break()
            ds.set_position(self.cursor)
            if s["aspect_change"]:
                ds.show_rotate_icon()
            ds.draw_in_canvas(self.c)
            if ds.is_cell_visible("Callout"):
                self.render_callout_arrows(s, centroids, ds)
            self.cursor_auto_shift(space)

            # if the previous step was the last of a callout, we should release
            # the reference to a LDRDocStep from the stack and pop it from the stack
            if idx > 0 and len(self.docstep_stack):
                if self.model.is_callout_end(idx - 1):
                    dc = self.docstep_stack[len(self.docstep_stack) - 1]
                    print(
                        "DOC:   Popping docstep reference %s from stack due to previous callout end"
                        % (str(cr.magenta(str("%r" % (dc)))))
                    )
                    self.docstep_stack.pop()

    def docstep_pli(self, idx):
        """ Returns a dictionary of PLI parts which can be used with the LDRDocStep class."""
        s = self.model[idx]
        pli = s["pli_bom"]
        docstep_pli = []
        for p in pli.parts:
            fn = self.fn_pli(p, with_path=True)
            docstep_pli.append({"qty": p.qty, "filename": fn})
        return docstep_pli

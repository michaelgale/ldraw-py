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
# LDView render class and helper functions

import os, tempfile
import datetime
import crayons
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageOps, ImageChops, ImageFilter, ImageEnhance

from toolbox import *
from ldrawpy import *

LDVIEW_BIN = "/Applications/LDView.app/Contents/MacOS/LDView"
LDVIEW_DICT = {
    "DefaultMatrix": "1,0,0,0,1,0,0,0,1",
    "SnapshotSuffix": ".png",
    "BlackHighlights": 0,
    "ProcessLDConfig": 1,
    "EdgeThickness": 3,
    "EdgesOnly": 0,
    "ShowHighlightLines": 1,
    "ConditionalHighlights": 1,
    "SaveZoomToFit": 0,
    "SubduedLighting": 1,
    "UseSpecular": 1,
    "UseFlatShading": 0,
    "LightVector": "0,1,1",
    "AllowPrimitiveSubstitution": 0,
    "HiResPrimitives": 1,
    "UseQualityLighting": 1,
    "UseQualityStuds": 1,
    "TextureStuds": 0,
    "SaveActualSize": 0,
    "SaveAlpha": 1,
    "AutoCrop": 0,
    "LineSmoothing": 1,
}
# 10.0 / tan(0.005 deg)
LDU_DISTANCE = 114591


def camera_distance(scale=1.0, dpi=300, page_width=8.5):
    one = 20 * 1 / 64 * dpi * scale
    sz = page_width * dpi / one * LDU_DISTANCE * 0.775
    sz *= 1700 / 1000
    return sz


def _coord_str(x, y=None, sep=", "):
    if isinstance(x, (tuple, list)):
        a, b = float(x[0]), float(x[1])
    else:
        a, b = float(x), float(y)
    sa = ("%f" % (a)).rstrip("0").rstrip(".")
    sb = ("%f" % (b)).rstrip("0").rstrip(".")
    s = []
    s.append(str(crayons.yellow("%s" % (sa))))
    s.append(sep)
    s.append(str(crayons.yellow("%s" % (sb))))
    return "".join(s)


class LDViewRender:
    """LDView render session helper class."""

    PARAMS = {
        "dpi": 300,
        "page_width": 8.5,
        "page_height": 11.0,
        "auto_crop": True,
        "image_smooth": False,
        "no_lines": False,
        "wireframe": False,
        "line_thickness": 3,
        "scale": 1.0,
        "output_path": None,
        "log_output": True,
        "log_level": 0,
        "overwrite": False,
    }

    def __init__(self, **kwargs):
        self.ldr_temp_path = tempfile.gettempdir() + os.sep + "temp.ldr"
        apply_params(self, kwargs)
        self.set_page_size(self.page_width, self.page_height)
        self.set_scale(self.scale)

    def __str__(self):
        s = []
        s.append("LDViewRender: ")
        s.append(" DPI: %d  Scale: %.2f" % (self.dpi, self.scale))
        s.append(
            " Page size: %s in (%s pixels)"
            % (
                _coord_str(self.page_width, self.page_height, " x "),
                _coord_str(self.pix_width, self.pix_height, " x "),
            )
        )
        s.append(
            " Auto crop: %s  Image smooth: %s" % (self.auto_crop, self.image_smooth)
        )
        s.append(" Camera distance: %d" % (self.cam_dist))
        return "\n".join(s)

    def set_page_size(self, width, height):
        self.page_width = width
        self.page_height = height
        self.pix_width = self.page_width * self.dpi
        self.pix_height = self.page_height * self.dpi
        self.args_size = "-SaveWidth=%d -SaveHeight=%d" % (
            self.pix_width,
            self.pix_height,
        )

    def set_scale(self, scale):
        self.scale = scale
        self.cam_dist = int(camera_distance(self.scale, self.dpi, self.page_width))
        self.args_cam = "-ca0.01 -cg0.0,0.0,%d" % (self.cam_dist)

    def _logoutput(self, msg, tstart=None, level=2):
        logmsg(msg, level=level, prefix="LDR", log_level=self.log_level)

    def render_from_str(self, ldrstr, outfile):
        """Render from a LDraw text string."""
        if self.log_output:
            s = ldrstr.splitlines()[0]
            self._logoutput(
                "rendering string (%s)..." % (crayons.green(s[: min(len(s), 80)]))
            )
        with open(self.ldr_temp_path, "w") as f:
            f.write(ldrstr)
        self.render_from_file(self.ldr_temp_path, outfile)

    def render_from_parts(self, parts, outfile):
        """Render using a list of LDRPart objects."""
        if self.log_output:
            self._logoutput("rendering parts (%s)..." % (crayons.green(len(parts))))
        ldrstr = []
        for p in parts:
            ldrstr.append(str(p))
        ldrstr = "".join(ldrstr)
        self.render_from_str(ldrstr, outfile)

    def render_from_file(self, ldrfile, outfile):
        """Render from an LDraw file."""
        tstart = datetime.now()
        if self.output_path is not None:
            path, name = split_path(outfile)
            oppath = full_path(self.output_path)
            if not oppath in path:
                filename = os.path.normpath(self.output_path + os.sep + outfile)
            else:
                filename = outfile
        else:
            filename = full_path(outfile)
        _, fno = split_path(filename)
        if not self.overwrite and os.path.isfile(full_path(filename)):
            if self.log_output:
                _, fno = split_path(filename)
                fno = colour_path_str(fno)
                self._logoutput("rendered file %s already exists, skipping" % fno)
            return
        ldv = []
        ldv.append(LDVIEW_BIN)
        ldv.append("-SaveSnapShot=%s" % filename)
        ldv.append(self.args_size)
        ldv.append(self.args_cam)
        for key, value in LDVIEW_DICT.items():
            if key == "EdgeThickness":
                value = self.line_thickness
            if self.no_lines:
                if key == "EdgeThickness":
                    value = 0
                elif key == "ShowHighlightLines":
                    value = 0
                elif key == "ConditionalHighlights":
                    value = 0
                elif key == "UseQualityStuds":
                    value = 0
            if self.wireframe:
                if key == "EdgesOnly":
                    value = 1
            ldv.append("-%s=%s" % (key, value))
        ldv.append(ldrfile)
        s = " ".join(ldv)
        os.system(s)
        if self.log_output:
            _, fni = split_path(ldrfile)
            _, fno = split_path(filename)
            fni = colour_path_str(fni)
            fno = colour_path_str(fno)
            self._logoutput("rendered file %s to %s..." % (fni, fno), tstart, level=0)

        if self.auto_crop:
            self.crop(filename)
        if self.image_smooth:
            self.smooth(filename)

    def crop(self, filename):
        """Crop image file."""
        tstart = datetime.now()
        im = Image.open(filename)
        bg = Image.new(im.mode, im.size, im.getpixel((1, 1)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, 0)
        bbox = diff.getbbox()
        if bbox:
            im2 = im.crop(bbox)
        else:
            im2 = im
        im2.save(filename)
        if self.log_output:
            _, fn = split_path(filename)
            fn = colour_path_str(fn)
            self._logoutput(
                "> cropped %s from (%s) to (%s)"
                % (fn, _coord_str(im.size), _coord_str(im2.size)),
                tstart,
            )

    def smooth(self, filename):
        """Apply a smoothing filter to image file."""
        tstart = datetime.now()
        im = Image.open(filename)
        im = im.filter(ImageFilter.SMOOTH)
        im.save(filename)
        if self.log_output:
            _, fn = split_path(filename)
            fn = colour_path_str(fn)
            self._logoutput("> smoothed %s (%s)" % (fn, _coord_str(im.size)), tstart)


def GeneratePartImage(name, colour=LDR_DEF_COLOUR, size=512, outpath="./", filename=""):

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

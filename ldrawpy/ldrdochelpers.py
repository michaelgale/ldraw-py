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
# LDraw related helper functions

import os, tempfile
from math import sin, cos, radians
from PIL import Image, ImageChops
import cv2
from toolbox import *
from reportlab.lib.units import inch, mm
from pdfdoc import *
from .ldrdocstyles import *


def get_centroids_of_colour(fn, colour, dpi=None):
    """ Returns a list of pixel coordinates of the centroids of detected regions
    of a specified colour. """
    img = cv2.imread(fn)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img_hsv, (colour - 12, 50, 50), (colour + 12, 255, 255))
    region = cv2.bitwise_and(img, img, mask=mask)
    gray_image = cv2.cvtColor(region, cv2.COLOR_BGRA2GRAY)
    ret, thresh = cv2.threshold(gray_image, 50, 255, 0)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    centroids = []
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(img, (cX, cY), 5, (255, 128, 255), -1)
            if dpi is not None:
                cX = cX / dpi * 72
                cY = cY / dpi * 72
            centroids.append((cX, cY))
    cv2.imwrite(fn, img)
    return centroids


class RotationIcon(ContentRect):
    """ A class which represents a boxed rotation icon.  It is a subclass of
    ContentRect and can be used by any TableVector class or rendered
    directly on to a ReportLab canvas object. """

    def __init__(self, style, size=None, arrow_style=None):
        super().__init__(style=style)
        self.arrow_style = DocStyle()
        self.arrow_style.set_with_dict(arrow_style)
        self.size = 0.7 * inch if size is None else size
        self.top_arrow = True
        self.bottom_arrow = True
        self.top_arrow_lr = True
        self.bottom_arrow_lr = False
        self.arrow_sep = 0.65
        self.arrow_tip = -0.65
        self.c = None
        self.set_fixed_size(self.size, self.size)
        self.rect.set_size(self.size, self.size)

    def draw_in_canvas(self, c):
        super().draw_in_canvas(c)
        r = self.rect
        x0, y0 = r.get_centre()
        ys = self.arrow_sep * r.height / 2
        yt = self.arrow_tip * r.height / 2
        at = 0.35 * r.height / 2
        ang = 45
        ytop = y0 + ys
        atop = y0 + at
        ttop = y0 + yt
        ybot = y0 - ys
        abot = y0 - at
        tbot = y0 - yt
        xl = x0 - ys
        xr = x0 + ys
        fc = self.arrow_style.get_attr("line-colour")
        c.setLineWidth(self.arrow_style.get_attr("line-width"))
        ax = self.arrow_style.get_attr("length") * cos(radians(ang)) / 4
        c.setStrokeColor(fc)
        c.setLineCap(0)
        if self.top_arrow:
            p = c.beginPath()
            p.arc(xl, ytop, xr, ttop, startAng=30, extent=120)
            c.drawPath(p, stroke=1, fill=0)
            ah = ArrowHead(style=self.arrow_style)
            if self.top_arrow_lr:
                ah.draw_in_canvas(c, (xr - ax, atop), -ang)
            else:
                ah.draw_in_canvas(c, (xl + ax, atop), -180 + ang)
        if self.bottom_arrow:
            p = c.beginPath()
            p.arc(xl, tbot, xr, ybot, startAng=-30, extent=-120)
            c.drawPath(p, stroke=1, fill=0)
            if self.bottom_arrow_lr:
                ah.draw_in_canvas(c, (xr - ax, abot), ang)
            else:
                ah.draw_in_canvas(c, (xl + ax, abot), 180 - ang)


class CalloutArrows:
    """ A class which represents one or more callout arrows.  Callout
    arrows are drawn from a callout rectangle border to an endpoint 
    somewhere else in the canvas. """

    def __init__(self, style, callout_location=None, callout_rect=None):
        self.style = DocStyle()
        self.style.set_with_dict(style)
        self.origin = (0, 0)
        self.endpoints = []
        self.offset = 0.2 * inch
        self.head_offset = -0.05 * inch
        self.point_offset = 0.25 * inch
        self.callout_rect = callout_rect
        self.callout_location = (
            callout_location if callout_location is not None else "top"
        )
        self.c = None

    def draw_in_canvas(self, c):
        self.c = c
        ep = []
        epa = []
        total_offset = self.head_offset + self.point_offset
        for e in self.endpoints:
            if self.callout_location == "top" or self.callout_location == "preview":
                ep.append((e[0], e[1] + total_offset))
                epa.append((e[0], e[1] + self.point_offset))
            elif self.callout_location == "right":
                ep.append((e[0] + total_offset, e[1]))
                epa.append((e[0] + self.point_offset, e[1]))
            elif self.callout_location == "bottom":
                ep.append((e[0], e[1] - total_offset))
                epa.append((e[0], e[1] - self.point_offset))
        for e in ep:
            # line backgrounds
            self.draw_line(*self.origin, *e, outline=True)
        for e in epa:
            # arrow heads
            if self.callout_location == "top" or self.callout_location == "preview":
                self.draw_arrow_head(*e, dir="down")
            elif self.callout_location == "right":
                self.draw_arrow_head(*e, dir="left")
            elif self.callout_location == "bottom":
                self.draw_arrow_head(*e, dir="up")
        for e in ep:
            # redraw lines
            self.draw_line(*self.origin, *e, outline=False)

    def draw_arrow_head(self, x, y, dir="down"):
        ah = ArrowHead(style=self.style)
        if dir == "down":
            rot = -90
        elif dir == "up":
            rot = 90
        elif dir == "left":
            rot = -180
        else:
            rot = 0
        ah.draw_in_canvas(self.c, (x, y), rot)

    def draw_line(self, x0, y0, x1, y1, outline=True):
        al = self.style.get_attr("length")
        bc = self.style.get_attr("border-colour")
        lw = 2 * self.style.get_attr("border-width") + self.style.get_attr("line-width")
        bw = self.style.get_attr("border-width") / 2
        self.c.setLineCap(0)
        in_rect = False
        if self.callout_rect is not None:
            if self.callout_location == "right":
                in_rect = (
                    True
                    if y1 > self.callout_rect.bottom and y1 < self.callout_rect.top
                    else False
                )
            else:
                in_rect = (
                    True
                    if x1 > self.callout_rect.left and x1 < self.callout_rect.right
                    else False
                )
        pts = []
        if self.callout_location == "top" or self.callout_location == "preview":
            if len(self.endpoints) == 1 and in_rect:
                pts.append((x1, y0 - bw))
                pts.append((x1, y1 + al / 2))
            else:
                pts.append((x0, y0 - bw))
                pts.append((x0, y0 - self.offset))
                pts.append((x1, y0 - self.offset))
                pts.append((x1, y1 + al / 2))
        elif self.callout_location == "right":
            if len(self.endpoints) == 1 and in_rect:
                pts.append((x0 - bw, y1))
                pts.append((x0 - self.offset, y1))
                pts.append((x1 + al / 2, y1))
            else:
                pts.append((x0 - bw, y0))
                pts.append((x0 - self.offset, y0))
                pts.append((x0 - self.offset, y1))
                pts.append((x1 + al / 2, y1))
        elif self.callout_location == "bottom":
            if len(self.endpoints) == 1 and in_rect:
                pts.append((x1, y0 + bw))
                pts.append((x1, y1 - al / 2))
            else:
                pts.append((x0, y0 + bw))
                pts.append((x0, y0 + self.offset))
                pts.append((x1, y0 + self.offset))
                pts.append((x1, y1 - al / 2))
        if outline:
            self.c.setLineWidth(lw)
            self.c.setStrokeColor(bc)
            p = self.c.beginPath()
            p.moveTo(*pts[0])
            for pt in pts:
                p.lineTo(*pt)
            self.c.drawPath(p, stroke=1, fill=0)
        fc = self.style.get_attr("line-colour")
        self.c.setLineWidth(self.style.get_attr("line-width"))
        self.c.setStrokeColor(fc)
        self.c.setLineCap(0)
        p = self.c.beginPath()
        p.moveTo(*pts[0])
        for pt in pts:
            p.lineTo(*pt)
        self.c.drawPath(p, stroke=1, fill=0)

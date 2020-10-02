# Sample Test passing with nose and pytest

import os
import sys
import pytest

from math import sqrt
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from fxgeometry import Vector, Point
from ldrawpy import *
from pdfdoc import *

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
pdfmetrics.registerFont(TTFont("IKEA-Sans-Regular", "IKEA-Sans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("IKEA-Sans-Heavy", "IKEA-Sans-Heavy.ttf"))
pdfmetrics.registerFont(TTFont("British-Rail-Light", "britrln_.ttf"))
pdfmetrics.registerFont(TTFont("British-Rail-Dark", "britrdn_.ttf"))


def test_ldrdocument():
    return
    doc = LDRDocument(ldrfile="./test_files/test_model.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/Polybulk.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/HEAHopperRev1.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/HEAHopperRev1.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/7763OBA.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/ZDAWagon.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/7762VDA.ldr", dpi=200)
    # doc = LDRDocument(ldrfile="./test_files/PGA.ldr", dpi=200)
    doc.set_stylesheet("./test_files/stylesheet.yml")
    doc.set_page_size(PAGE_LETTER, orientation="portrait")
    doc.init_document()
    doc.set_columns(1)
    start_idx, stop_idx = doc.model.idx_range_from_steps(range(1, 20))
    # print(start_idx, stop_idx)
    for idx, ctx in doc.iter_doc(range(start_idx, stop_idx + 1)):
        if idx == start_idx:
            doc.render_bom()
        s = doc.model[idx]
        doc.change_layout(s)
        doc.render_step(idx)
        if s["page_break"]:
            doc.section_break(new_section=str(s["next_level"]), page_break=True, column_break=False)
            if not doc.model[idx + 1]["no_pli"]:
                doc.render_assem_preview_image(idx)
        else:
            doc.change_layout(s)
        # elif lc:
        #     doc.change_layout(s, with_break=True)
    doc.model.print_unwrapped()


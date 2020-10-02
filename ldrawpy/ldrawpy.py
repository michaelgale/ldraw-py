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
# LDraw python module

SPECIAL_TOKENS = {
    "scale": ["!LPUB ASSEM MODEL_SCALE %-1", "!PY SCALE %-1"],
    "rotation_abs": ["ROTSTEP %2 %3 %4 ABS"],
    "rotation_rel": ["ROTSTEP %2 %3 %4 REL"],
    "page_break": ["!LPUB INSERT PAGE", "!PY PAGE_BREAK"],
    "columns": ["!PY COLUMNS %-1"],
    "column_break": ["!PY COLUMN_BREAK"],
    "arrow_begin": ["!PY ARROW BEGIN %4 %5 %6 %7 %8 %9 %10 %11 %12"],
    "arrow_colour": ["!PY ARROW COLOUR %-1"],
    "arrow_length": ["!PY ARROW LENGTH %-1"],
    "arrow_end": ["!PY ARROW END"],
    "callout": ["!PY CALLOUT"],
    "bom": ["!LPUB INSERT BOM", "!PY BOM"],
}


def BrickNameStrip(s, level=0):
    """ Progressively strips (with increasing levels) a part description
    by making substitutions with abreviations, removing spaces, etc. 
    This can be useful for labelling or BOM part lists where space is limited."""
    sn = s
    if level == 0:
        sn = sn.replace("  ", " ")
        sn = sn.replace(
            "Plate 1 x 2 with Groove with 1 Centre Stud, without Understud",
            "Plate 1 x 2  Jumper",
        )
        sn = sn.replace(
            "Plate 1 x 2 without Groove with 1 Centre Stud", "Plate 1 x 2  Jumper"
        )
        sn = sn.replace(
            "Plate 1 x 2 with Groove with 1 Centre Stud", "Plate 1 x 2  Jumper"
        )
        sn = sn.replace("Brick 1 x 1 with Headlight", "Brick 1 x 1 Erling")
        sn = sn.replace("with Groove", "")
        sn = sn.replace("Bluish ", "Bl ")
        sn = sn.replace("Slope Brick", "Slope")
        sn = sn.replace("0.667", "2/3")
        sn = sn.replace("1.667", "1-2/3")
        sn = sn.replace("1 And 1/3", "1-1/3")
        sn = sn.replace("1 and 1/3", "1-1/3")
        sn = sn.replace("1 & 1/3", "1-1/3")
        sn = sn.replace("with Headlight", "Erling")
    elif level == 1:
        sn = sn.replace("with ", "w/")
        sn = sn.replace("With ", "w/")
        sn = sn.replace("without ", "wo/")
        sn = sn.replace("Without ", "wo/")
        sn = sn.replace("One", "1")
        sn = sn.replace("Two", "2")
        sn = sn.replace("Three", "3 ")
        sn = sn.replace("Four", "4")
        sn = sn.replace(" and ", " & ")
        sn = sn.replace(" And ", " & ")
        sn = sn.replace("Dark", "Dk")
        sn = sn.replace("Light", "Lt")
        sn = sn.replace("Bright", "Br")
        sn = sn.replace("Reddish Brown", "Red Brown")
        sn = sn.replace("Reddish", "Red")
        sn = sn.replace("Yellowish", "Ylwish")
        sn = sn.replace("Medium", "Med")
        sn = sn.replace("Offset", "offs")
        sn = sn.replace("Adjacent", "adj")
    elif level == 2:
        sn = sn.replace("Trans", "Tr")
        sn = sn.replace(" x ", "x")
    elif level == 3:
        sn = sn.replace("Orange", "Org")
        sn = sn.replace("Yellow", "Ylw")
        sn = sn.replace("Black", "Blk")
        sn = sn.replace("White", "Wht")
        sn = sn.replace("Green", "Grn")
        sn = sn.replace("Brown", "Brn")
        sn = sn.replace("Purple", "Prpl")
        sn = sn.replace("Violet", "Vlt")
        sn = sn.replace("Gray", "Gry")
        sn = sn.replace("Grey", "Gry")
        sn = sn.replace("Axlehole", "axle")
        sn = sn.replace("Cylinder", "cyl")
        sn = sn.replace("Inverted", "inv")
        sn = sn.replace("Centre", "Ctr")
        sn = sn.replace("Center", "Ctr")
        sn = sn.replace("Rounded", "round")
        sn = sn.replace("Underside", "under")
        sn = sn.replace("Vertical", "vert")
        sn = sn.replace("Horizontal", "horz")
        sn = sn.replace("Flex-System", "Flex")
        sn = sn.replace("Flanges", "Flange")
        sn = sn.replace("Type 1", "")
        sn = sn.replace("Type 2", "")
    elif level == 4:
        sn = sn.replace("Technic", "")
        sn = sn.replace("Single", "1")
        sn = sn.replace("Dual", "2")
        sn = sn.replace("Double", "Dbl")
        sn = sn.replace("Stud on", "stud")
        sn = sn.replace("Studs on Sides", "stud sides")
        sn = sn.replace("Studs on Side", "side studs")
        sn = sn.replace("Hinge Plate", "Hinge")
    elif level == 5:
        sn = sn.replace(" on ", " ")
        sn = sn.replace(" On ", " ")
        sn = sn.replace("Rounded", "Rnd")
        sn = sn.replace("Round", "Rnd")
        sn = sn.replace("Side", "Sd")
        sn = sn.replace("Groove", "Grv")
        sn = sn.replace("Minifig", "")
        sn = sn.replace("Curved", "curv")
        sn = sn.replace("Notched", "notch")
        sn = sn.replace("Friction", "fric")
        sn = sn.replace("(Complete)", "")
        sn = sn.replace("Cross", "X")
        sn = sn.replace("Embossed", "Emb")
        sn = sn.replace("Extension", "Ext")
        sn = sn.replace("Bottom", "Bot")
        sn = sn.replace("Inside", "Insd")
        sn = sn.replace("Locking", "click")
        sn = sn.replace("Axleholder", "axle")
    elif level == 6:
        sn = sn.replace("Studs", "St")
        sn = sn.replace("Stud", "St")
        sn = sn.replace("Corners", "edge")
        sn = sn.replace("w/Curv Top", "curved")
        sn = sn.replace("Domed", "dome")
        sn = sn.replace("Clips", "clip")
        sn = sn.replace("Convex", "cvx")
    return sn

#! /usr/bin/env python3
#
# Copyright (C) 2018  Fx Bricks Inc.
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

LDR_OPT_COLOUR = 24
LDR_DEF_COLOUR = 16
LDR_ALL_COLOUR = 1000
LDR_ANY_COLOUR = 1001
LDR_OTHER_COLOUR = 1002
LDR_MONO_COLOUR = 1003
LDR_BLKWHT_COLOUR = 1004
LDR_GRAY_COLOUR = 1005
LDR_REDYLW_COLOUR = 1006
LDR_BLUYLW_COLOUR = 1007
LDR_REDBLUYLW_COLOUR = 1008
LDR_GRNBRN_COLOUR = 1009
LDR_BLUBRN_COLOUR = 1010
LDR_BRGREEN_COLOUR = 1011
LDR_LAVENDER_COLOUR = 1012
LDR_PINK_COLOUR = 1013
LDR_LTYLW_COLOUR = 1014


def BrickNameStrip(s, level=0):
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
        sn = sn.replace("Plate 1 x 2 with Groove with 1 Centre Stud", "Plate 1 x 2  Jumper")
        sn = sn.replace("with Groove", "")
        sn = sn.replace("Bluish ", "")
        sn = sn.replace("Slope Brick", "Slope")
        sn = sn.replace("0.667", "2/3")
        sn = sn.replace("1.667", "1-2/3")
        sn = sn.replace("1 And 1/3", "1-1/3")
        sn = sn.replace("1 and 1/3", "1-1/3")
        sn = sn.replace("1 & 1/3", "1-1/3")
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
        sn = sn.replace("Reddish Brown", "Brown")
        sn = sn.replace("Reddish", "Red")
        sn = sn.replace("Yellowish", "Ylwish")
        sn = sn.replace("Medium", "Med")
        sn = sn.replace("Offset", "Offs")
        sn = sn.replace("Adjacent", "Adj")
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
        sn = sn.replace("Axlehole", "Axle")
        sn = sn.replace("Cylinder", "Cyl")
        sn = sn.replace("Inverted", "Inv")
        sn = sn.replace("Centre", "Ctr")
        sn = sn.replace("Center", "Ctr")
        sn = sn.replace("Rounded", "Round")
        sn = sn.replace("Underside", "Under")
        sn = sn.replace("Vertical", "Vert")
        sn = sn.replace("Horizontal", "Horz")
        sn = sn.replace("Flex-System", "Flex")
        sn = sn.replace("Flanges", "Flange ")
        sn = sn.replace("Type 1", "")
        sn = sn.replace("Type 2", "")
    elif level == 4:
        sn = sn.replace("Technic", "")
        sn = sn.replace("Single", "1")
        sn = sn.replace("Dual", "2")
        sn = sn.replace("Double", "Dbl")
        sn = sn.replace("Stud on", "Stud")
        sn = sn.replace("Studs on Sides", "Stud Sides")
        sn = sn.replace("Studs on Side", "Side Studs")
        sn = sn.replace("Hinge Plate", "Hinge")
    elif level == 5:
        sn = sn.replace(" on ", " ")
        sn = sn.replace(" On ", " ")
        sn = sn.replace("Rounded", "Rnd")
        sn = sn.replace("Round", "Rnd")
        sn = sn.replace("Side", "Sd")
        sn = sn.replace("Groove", "Grv")
        sn = sn.replace("Minifig", "")
        sn = sn.replace("Curved", "Curv")
        sn = sn.replace("Notched", "Notch")
        sn = sn.replace("Friction", "Frctn")
        sn = sn.replace("(Complete)", "")
        sn = sn.replace("Cross", "X")
        sn = sn.replace("Embossed", "Emb")
        sn = sn.replace("Extension", "Ext")
        sn = sn.replace("Bottom", "Bot")
        sn = sn.replace("Inside", "Insd")
        sn = sn.replace("Locking", "Click")
        sn = sn.replace("Axleholder", "Axle")
    elif level == 6:
        sn = sn.replace("Studs", "St")
        sn = sn.replace("Stud", "St")
        sn = sn.replace("Corners", "Edge")
        sn = sn.replace("w/Curv Top", "Curved")
        sn = sn.replace("Domed", "Dome")
        sn = sn.replace("Clips", "Clip")
        sn = sn.replace("Convex", "Cvx")
    return sn

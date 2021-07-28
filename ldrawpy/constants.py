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
# Constants

LDR_OPT_COLOUR = 24
LDR_DEF_COLOUR = 16

#
# special colour codes for use with labels
#
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
LDR_BLUBLU_COLOUR = 1015
LDR_DKREDBLU_COLOUR = 1016
LDR_ORGYLW_COLOUR = 1017
LDR_ORGBRN_COLOUR = 1018
LDR_BLUES_COLOUR = 1019
LDR_GREENS_COLOUR = 1020
LDR_YELLOWS_COLOUR = 1021
LDR_REDORG_COLOUR = 1022
LDR_TANBRN_COLOUR = 1023
LDR_REDORGYLW_COLOUR = 1024
LDR_BLUGRN_COLOUR = 1025
LDR_TAN_COLOUR = 1026
LDR_PINKPURP_COLOUR = 1027

LDR_ANY_COLOUR_FILL = ["E6E6E6", "8EDAFF", "FFFF66", "FD908F"]


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
    "no_callout": ["!PY NO_CALLOUT"],
    "rotation_pre": ["!PY ROT %3 %4 %5"],
    "no_preview": ["!PY NO_PREVIEW"],
    "model_scale": ["!PY MODEL_SCALE %-1"],
    "preview_aspect": ["!PY PREVIEW_ASPECT %3 %4 %5"],
}

LDR_DEFAULT_SCALE = 1.0
LDR_DEFAULT_ASPECT = (40, -55, 0)

ASPECT_DICT = {
    "front": (0, 0, 0),
    "back": (0, 180, 0),
    "right": (0, 90, 0),
    "left": (0, -90, 0),
    "top": (90, 0, 0),
    "bottom": (-90, 0, 0),
    "iso35": (35, 35, 0),
    "iso45": (35, 45, 0),
    "iso55": (35, 55, 0),
    "iso90": (35, 90, 0),
    "iso125": (35, 125, 0),
    "iso135": (35, 135, 0),
    "iso145": (35, 145, 0),
    "iso-35": (35, -35, 0),
    "iso-45": (35, -45, 0),
    "iso-55": (35, -55, 0),
    "iso-90": (35, -90, 0),
    "iso-125": (35, -125, 0),
    "iso-135": (35, -135, 0),
    "iso-145": (35, -145, 0),
    "iso180": (35, 180, 0),
    "iso-180": (35, 180, 0),
    "n": (35, 0, 0),
    "nnw": (35, 35, 0),
    "nw": (35, 45, 0),
    "wnw": (35, 55, 0),
    "w": (35, 90, 0),
    "wsw": (35, 125, 0),
    "sw": (35, 135, 0),
    "ssw": (35, 145, 0),
    "s": (35, 180, 0),
    "sse": (35, -145, 0),
    "se": (35, -135, 0),
    "ese": (35, -125, 0),
    "e": (35, -90, 0),
    "ene": (35, -55, 0),
    "ne": (35, -45, 0),
    "nne": (35, -35, 0),
}

FLIP_DICT = {
    "flip-x": (180, 0, 0),
    "flip-y": (0, 180, 0),
    "flip-z": (0, 0, 180),
    "flipx": (180, 0, 0),
    "flipy": (0, 180, 0),
    "flipz": (0, 0, 180),
    "rot90": (0, 90, 0),
    "rot-90": (0, -90, 0),
}

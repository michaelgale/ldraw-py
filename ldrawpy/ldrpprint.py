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
# LDraw pretty printer helper functions

import string

from rich import print
from ldrawpy import *


def is_hex_colour(text):
    text = text.strip('"')
    if not len(text) == 7:
        return False
    if not text[0] == "#":
        return False
    hs = text.lstrip("#")
    if not all(c in string.hexdigits for c in hs):
        return False
    return True


def pprint_ldr_colour(code):
    if code == "16" or code == "24":
        return "[bold navajo_white1]%s" % (code)
    if code == "0":
        return "[bold]0"
        # return "[bold yellow reverse]%s[not reverse]" % (code)
    colour = LDRColour(int(code))
    return "[#%s reverse]%s[not reverse]" % (colour.as_hex(), code)


def pprint_coord_str(v, colour="[white]"):
    return "[not bold]%s%s %s %s" % (colour, v[0], v[1], v[2])


def pprint_line1(line):
    s = []
    line = line.rstrip()
    ls = line.split()
    s.append("[bold white]%s" % (ls[0]))
    s.append("%s" % (pprint_ldr_colour(ls[1])))
    s.append(pprint_coord_str(ls[2:5]))
    s.append(pprint_coord_str(ls[5:8], colour="[#91E3FF]"))
    s.append(pprint_coord_str(ls[8:11], colour="[#FFF3AF]"))
    s.append(pprint_coord_str(ls[11:14], colour="[#91E3FF]"))
    if line.lower().endswith(".ldr"):
        s.append("[bold #B7E67A]%s" % (" ".join(ls[14:])))
    else:
        s.append("[bold #F27759]%s" % (" ".join(ls[14:])))
    return " ".join(s)


def pprint_line2345(line):
    s = []
    line = line.rstrip()
    ls = line.split()
    s.append("[bold white]%s" % (ls[0]))
    s.append("%s" % (pprint_ldr_colour(ls[1])))
    s.append(pprint_coord_str(ls[2:5]))
    s.append(pprint_coord_str(ls[5:8], colour="[#91E3FF]"))
    if len(ls) > 8:
        s.append(pprint_coord_str(ls[8:11], colour="[#FFF3AF]"))
    if len(ls) > 11:
        s.append(pprint_coord_str(ls[8:11], colour="[#91E3FF]"))
    return " ".join(s)


def pprint_line0(line):
    s = []
    line = line.rstrip()
    ls = line.split()
    if ls[1] in LDRAW_TOKENS or ls[1] in META_TOKENS or ls[1].startswith("!"):
        s.append("[bold white]%s[not bold]" % (ls[0]))
        if "FILE" in ls[1]:
            s.append("[bold #B7E67A]%s[not bold]" % (ls[1]))
        elif ls[1].startswith("!"):
            s.append("[bold #78D4FE]%s[not bold]" % (ls[1]))
        elif ls[1] in META_TOKENS:
            s.append("[bold #BA7AE4]%s[not bold]" % (ls[1]))
        else:
            s.append("[bold #7096FF]%s[not bold]" % (ls[1]))
        if len(ls) > 2:
            if line.lower().endswith(".ldr"):
                for e in ls[2:]:
                    s.append("[bold #B7E67A]%s" % (e))
            elif line.lower().endswith(".dat"):
                for e in ls[2:]:
                    s.append("[bold #F27759]%s" % (e))
            else:
                for e in ls[2:]:
                    if e in META_TOKENS:
                        s.append("[bold #BA7AE4]%s[not bold]" % (e))
                    elif is_hex_colour(e):
                        s.append("[%s reverse]%s[not reverse]" % (e.strip('"'), e))
                    else:
                        s.append("[white]%s" % (e))
    else:
        s.append("[bold black]%s" % (line.rstrip()))
    return " ".join(s)


def pprint_line(line, lineno=None, nocolour=False):
    ls = line.split()
    s = []
    if lineno is not None:
        s.append("[#404040]%4d | " % (lineno))
    if len(ls) > 1 and not nocolour:
        if ls[0] == "1":
            s.append(pprint_line1(line))
        elif ls[0] == "0":
            s.append(pprint_line0(line))
        elif any([ls[0] in "2345"]):
            s.append(pprint_line2345(line))
        else:
            s.append("[white]%s" % (line.rstrip()))
    else:
        s.append("[white][not bold]%s" % (line.rstrip()))
    print("".join(s))

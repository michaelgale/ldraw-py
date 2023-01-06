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

from rich import print
from ldrawpy import *


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
    s.append(pprint_coord_str(ls[5:8], colour="[steel_blue1]"))
    s.append(pprint_coord_str(ls[8:11], colour="[khaki1]"))
    s.append(pprint_coord_str(ls[11:14], colour="[steel_blue1]"))
    if line.lower().endswith(".ldr"):
        s.append("[bold sea_green3]%s" % (" ".join(ls[14:])))
    else:
        s.append("[bold dark_orange]%s" % (" ".join(ls[14:])))
    return " ".join(s)


def pprint_line2345(line):
    s = []
    line = line.rstrip()
    ls = line.split()
    s.append("[bold white]%s" % (ls[0]))
    s.append("%s" % (pprint_ldr_colour(ls[1])))
    s.append(pprint_coord_str(ls[2:5]))
    s.append(pprint_coord_str(ls[5:8], colour="[steel_blue1]"))
    if len(ls) > 8:
        s.append(pprint_coord_str(ls[8:11], colour="[khaki1]"))
    if len(ls) > 11:
        s.append(pprint_coord_str(ls[8:11], colour="[steel_blue1]"))
    return " ".join(s)


def pprint_line0(line):
    s = []
    line = line.rstrip()
    ls = line.split()
    if ls[1] in LDRAW_TOKENS or ls[1] in META_TOKENS or ls[1].startswith("!"):
        s.append("[bold white]%s[not bold]" % (ls[0]))
        if "FILE" in ls[1]:
            s.append("[bold sea_green3]%s[not bold]" % (ls[1]))
        elif ls[1].startswith("!"):
            s.append("[bold cyan]%s[not bold]" % (ls[1]))
        elif ls[1] in META_TOKENS:
            s.append("[bold medium_orchid]%s[not bold]" % (ls[1]))
        else:
            s.append("[bold blue]%s[not bold]" % (ls[1]))
        if len(ls) > 2:
            if line.lower().endswith(".ldr"):
                for e in ls[2:]:
                    s.append("[bold sea_green3]%s" % (e))
            elif line.lower().endswith(".dat"):
                for e in ls[2:]:
                    s.append("[bold dark_orange]%s" % (e))
            else:
                for e in ls[2:]:
                    if e in META_TOKENS:
                        s.append("[bold medium_orchid]%s[not bold]" % (e))
                    else:
                        s.append("[white]%s" % (e))
    else:
        s.append("[bold black]%s" % (line.rstrip()))
    return " ".join(s)


def pprint_line(line):
    if len(line) < 1:
        print("")
        return
    ls = line.split()
    if len(ls) > 1:
        if ls[0] == "1":
            print(pprint_line1(line))
        elif ls[0] == "0":
            print(pprint_line0(line))
        elif any([ls[0] in "2345"]):
            print(pprint_line2345(line))
        else:
            print("[white]%s" % (line.rstrip()))
        return
    print("[white]%s" % (line.rstrip()))

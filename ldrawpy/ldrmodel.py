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
# LDraw model classes and helper functions

import os, tempfile
import datetime
import hashlib

import crayons
from datetime import datetime
from collections import defaultdict

from toolbox import *
from ldrawpy import *

# import brickbom if available, otherwise don't raise since it is not
# necessary for testing.
try:
    from brickbom import BOM, BOMPart
except:
    pass
try:
    from rich import print

    has_rich = True
except:
    has_rich = False

START_TOKENS = ["PLI BEGIN IGN", "BUFEXCHG STORE", "SYNTH BEGIN"]
END_TOKENS = ["PLI END", "BUFEXCHG RETRIEVE", "SYNTH END"]
EXCEPTION_LIST = ["2429c01.dat"]

COMMON_SUBSTITUTIONS = [
    ("3070a", "3070b"),  # 1 x 1 tile
    ("3069a", "3069b"),  # 1 x 2 tile
    ("3068a", "3068b"),  # 2 x 2 tile
    ("x224", "41751"),  # windscreen
    ("4864a", "87552"),  # 1 x 2 x 2 panel with side supports
    ("4864b", "87552"),  # 1 x 2 x 2 panel with side supports
    ("2362a", "87544"),  # 1 x 2 x 3 panel with side supports
    ("2362b", "87544"),  # 1 x 2 x 3 panel with side supports
    ("60583", "60583b"),  # 1 x 1 x 3 brick with clips
    ("60583a", "60583b"),
    ("3245a", "3245c"),  # 1 x 2 x 2 brick
    ("3245b", "3245c"),
    ("3794", "15573"),  # 1 x 2 jumper plate
    ("3794a", "15573"),
    ("3794b", "15573"),
    ("4215a", "60581"),  # 1 x 4 x 3 panel with side supports
    ("4215b", "60581"),
    ("4215", "60581"),
    # ["2429c01", "73983"],  # 1 x 4 hinge plate complete
    ["73983", "2429c01"],  # 1 x 4 hinge plate complete
]


def substitute_part(part):
    for e in COMMON_SUBSTITUTIONS:
        if part.name == e[0]:
            part.name = e[1]
    return part


def line_has_all_tokens(line, tokenlist):
    for t in tokenlist:
        tokens = t.split()
        tcount = 0
        tlen = len(tokens)
        for te in tokens:
            if te in line.split():
                tcount += 1
        if tcount == tlen:
            return True
    return False


def parse_special_tokens(line):
    ls = line.split()
    metas = []
    for k, v in SPECIAL_TOKENS.items():
        for t in v:
            tokens = t.split()
            tcount = 0
            tlen = len([x for x in tokens if x[0] != "%"])
            for token in tokens:
                if token in ls:
                    tcount += 1
            if tcount == tlen:
                linelen = len(ls)
                captures = [int(x[1:]) for x in tokens if x[0] == "%"]
                if len(captures) > 0:
                    values = [ls[x] for x in captures if x < linelen]
                    meta = {k: {"values": values, "text": line}}
                else:
                    meta = {k: {"text": line}}
                metas.append(meta)
    return metas


def get_meta_commands(ldr_string):
    """Parses an LDraw string looking for known meta commands. Identified meta
    commands are returned in a dictionary."""
    cmd = []
    lines = ldr_string.splitlines()
    for line in lines:
        lineType = int(line.lstrip()[0] if line.lstrip() else -1)
        if lineType == -1:
            continue
        if lineType == 0:
            meta = parse_special_tokens(line)
            if meta is not None:
                cmd.extend(meta)
    return cmd


def get_parts_from_model(ldr_string):
    """Extracts a list of parts representing LDraw parts (line type 1) from a
    string of LDraw text. The returned list is contains dictionary for each part
    with the keys "partname" and "ldrtext"."""
    parts = []
    lines = ldr_string.splitlines()
    mask_depth = 0
    bufex = False
    for line in lines:
        pd = {}
        if line_has_all_tokens(line, ["BUFEXCHG STORE"]):
            bufex = True
        if line_has_all_tokens(line, ["BUFEXCHG RETRIEVE"]):
            bufex = False
        if line_has_all_tokens(line, START_TOKENS):
            mask_depth += 1
        if line_has_all_tokens(line, END_TOKENS):
            if mask_depth > 0:
                mask_depth -= 1

        lineType = int(line.lstrip()[0] if line.lstrip() else -1)
        if lineType == -1:
            continue
        if lineType == 1:
            splitLine = line.lower().split()
            pd["ldrtext"] = line
            pd["partname"] = " ".join([str(i) for i in splitLine[14:]])
            if mask_depth == 0:
                parts.append(pd)
            else:
                if pd["partname"] in EXCEPTION_LIST:
                    parts.append(pd)
                elif not bufex and pd["partname"].endswith(".ldr"):
                    parts.append(pd)
    return parts


def recursive_parse_model(
    model,
    submodels,
    parts,
    offset=None,
    matrix=None,
    reset_parts=False,
    inv=False,
    only_submodel=None,
):
    """Recursively parses an LDraw model dictionary plus any submodels and
    populates a parts list representing that model.  To support selective
    parsing of only one submodel, only_submodel can be set to the desired
    submodel."""
    o = offset if offset is not None else Vector(0, 0, 0)
    m = matrix if matrix is not None else Identity()
    if reset_parts:
        parts.clear()
    for e in model:
        if only_submodel is not None:
            if not e["partname"] == only_submodel:
                continue
        if e["partname"] in submodels:
            submodel = submodels[e["partname"]]
            p = LDRPart()
            p.from_str(e["ldrtext"])
            # as we progress deeper in the recursive search, we need to
            # transpose the rotation matrix every other level to maintain
            # consistent geometry for the entire aggregate model
            if inv:
                new_matrix = m * p.attrib.matrix
                new_loc = p.attrib.loc * m.transpose()
            else:
                new_matrix = m * p.attrib.matrix
                new_loc = p.attrib.loc * m
            new_loc += o
            recursive_parse_model(
                submodel,
                submodels,
                parts,
                offset=new_loc,
                matrix=new_matrix,
                inv=not inv,
            )
        else:
            if only_submodel is None:
                part = LDRPart()
                part.from_str(e["ldrtext"])
                part = substitute_part(part)
                part.transform(matrix=m, offset=o)
                parts.append(part)


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


def unique_set(items):
    udict = {}
    if len(items) > 0:
        udict = defaultdict(int)
        for e in items:
            udict[e] += 1
    return udict


def key_name(elem):
    return elem.name


def key_colour(elem):
    return elem.attrib.colour


def key_colour(elem):
    return elem.attrib.colour


def get_sha1_hash(parts):
    """Gets a normalized sha1 hash LDRPart objects"""
    sp = []
    for p in parts:
        sp.append((p, p.sha1hash()))
    sp.sort(key=lambda x: x[1])
    shash = hashlib.sha1()
    for p in sp:
        shash.update(bytes(p[1], encoding="utf8"))
    return shash.hexdigest()


def sort_parts(parts, key="name", order="ascending"):
    """Sorts a list of LDRPart objects by key"""
    sp = []
    if key.lower() == "sha1":
        for p in parts:
            sp.append((p, p.sha1hash()))
        sp.sort(key=lambda x: x[1])
        xp = []
        for p in sp:
            xp.append(sp[0])
        return xp
    if key.lower() == "name":
        sp.sort(key=key_name, reverse=True if order.lower() == "descending" else False)
    elif key.lower() == "colour":
        sp.sort(
            key=key_colour, reverse=True if order.lower() == "descending" else False
        )
    return sp


class LDRModel:
    PARAMS = {
        "global_origin": (0, 0, 0),
        "global_aspect": (-40, 55, 0),
        "global_scale": 1.0,
        "pli_aspect": (-25, -40, 0),
        "pli_exceptions": {
            "32001": (-50, -25, 0),
            "3676": (-25, 50, 0),
            "3045": (-25, 50, 0),
        },
        "callout_step_thr": 6,
        "continuous_step_numbers": False,
    }

    def __init__(self, filename, **kwargs):
        from brickbom import BOM, BOMPart

        self.filename = filename
        apply_params(self, kwargs, locals())
        _, self.title = split_path(filename)
        self.bom = BOM()
        self.steps = {}
        self.pli = {}
        self.sub_models = {}
        self.sub_model_str = {}
        self.unwrapped = None
        self.callouts = {}
        self.continuous_step_count = 0

    def __str__(self):
        s = []
        s.append("LDRModel:")
        s.append(
            " Global origin: %s Global aspect: %s"
            % (self.global_origin, self.global_aspect)
        )
        s.append(" Number of steps: %d" % (len(self.steps)))
        s.append(" Number of sub-models: %d" % (len(self.sub_models)))
        return "\n".join(s)

    def __getitem__(self, key):
        return self.unwrapped[key]

    def print_step_dict(self, key):
        if key in self.steps:
            s = self.steps[key]
            for k, v in s.items():
                if k == "sub_parts":
                    for ks, vs in v.items():
                        print("%s: " % (ks))
                        for e in vs:
                            print("  %s" % (str(e).rstrip()))
                elif isinstance(v, list):
                    print("%s: " % (k))
                    for vx in v:
                        print("  %s" % (str(vx).rstrip()))
                else:
                    print("%s: %s" % (k, v))

    def print_unwrapped_dict(self, idx):
        s = self.unwrapped[idx]
        for k, v in s.items():
            if isinstance(v, list):
                print("%s: " % (k))
                for vx in v:
                    print("  %s" % (str(vx).rstrip()))
            else:
                print("%s: %s" % (k, v))

    def print_unwrapped_verbose(self):
        for i, v in enumerate(self.unwrapped):
            print(
                "%3d. idx:%3d [pl:%d l:%d nl:%d] [s:%2d ns:%2d sc:%2d] %-16s q:%d sc:%.2f (%3.0f,%4.0f,%3.0f)"
                % (
                    i,
                    v["idx"],
                    v["prev_level"],
                    v["level"],
                    v["next_level"],
                    v["step"],
                    v["next_step"],
                    v["num_steps"],
                    v["model"],
                    v["qty"],
                    v["scale"],
                    v["aspect"][0],
                    v["aspect"][1],
                    v["aspect"][2],
                )
            )

    def print_unwrapped(self):
        for v in self.unwrapped:
            self.print_step(v)

    def print_step(self, v):
        pb = "break" if v["page_break"] else ""
        co = str(v["callout"])
        model_name = v["model"].replace(".ldr", "")
        model_name = model_name[:16]
        qty = "(%2dx)" % (v["qty"]) if v["qty"] > 0 else "     "
        level = " " * v["level"] + "Level %d" % (v["level"])
        level = "%-11s" % (level)
        parts = "(%2dx pcs)" % (len(v["pli_bom"]))
        meta = [v.keys() for v in v["meta"]]
        meta = [list(x) for x in meta if "columns" not in x]
        for e in v["meta"]:
            if "columns" in e:
                meta.append("[green]COL%s[/]" % (e["columns"]["values"][0]))
        meta = ["".join(x) for x in meta]
        meta = " ".join(meta)
        meta = meta.replace("arrow_begin", ":arrow_down:")
        meta = meta.replace(" arrow_end", "")
        meta = meta.replace(" arrow_length", "")
        meta = meta.replace("rotation_rel", ":arrows_counterclockwise:REL")
        meta = meta.replace("rotation_abs", ":arrows_counterclockwise:ABS")
        meta = meta.replace("rotation_pre", ":arrows_counterclockwise:PRE")
        meta = meta.replace("scale", ":triangular_ruler:")
        meta = meta.replace("page_break", ":page_facing_up:")
        meta = meta.replace("no_callout", ":prohibited:CA")
        if has_rich:
            if not co == "0":
                fmt = "%3d. %s Step [yellow]%3d/%3d[/] Model: [red]%-16s[/]"
            else:
                if model_name == "root":
                    fmt = "%3d. %s Step [green]%3d/%3d[/] Model: [green]%-16s[/]"
                else:
                    fmt = "%3d. %s Step [green]%3d/%3d[/] Model: [red]%-16s[/]"
        else:
            fmt = "%3d. %s Step %3d/%3d Model: %-16s"
        fmt += " %s %s scale: %.2f (%3.0f,%4.0f,%3.0f)"
        if co == "0":
            fmt += " [bright_black]%1s[/]"
        else:
            fmt += " [yellow]%1s[/]"
        if pb == "break":
            fmt += " [magenta]BR[/] %s"
        else:
            fmt += " %s"
        print(
            fmt
            % (
                v["idx"],
                level,
                v["step"],
                v["num_steps"],
                model_name,
                qty,
                parts,
                v["scale"],
                v["aspect"][0],
                v["aspect"][1],
                v["aspect"][2],
                co,
                meta,
            )
        )

    def idx_range_from_steps(self, steps):
        """Returns a start and stop index into the unwrapped model from
        either a list or range."""
        if isinstance(steps, list):
            start_idx = self.idx_from_step(steps[0], as_start_idx=True)
            stop_idx = self.idx_from_step(steps[len(steps) - 1])
        elif isinstance(steps, range):
            start_idx = self.idx_from_step(steps.start, as_start_idx=True)
            stop_idx = self.idx_from_step(steps.stop)
        return start_idx, stop_idx

    def idx_from_step(self, step, as_start_idx=False):
        """Returns the index from the unwrapped model corresponding to a specified
        step in the root model."""
        if step == 1:  # and as_start_idx:
            return 0
        if step < 0:
            return len(self.unwrapped) + step
        if step < 1:
            return 0
        if as_start_idx:
            if self.continuous_step_numbers:
                for s in self.unwrapped:
                    if s["step"] == step - 1 and s["callout"] == 0:
                        return s["idx"] + 1
            else:
                for s in self.unwrapped:
                    if s["step"] == step - 1 and s["level"] == 0:
                        return s["idx"] + 1
        else:
            if self.continuous_step_numbers:
                for s in self.unwrapped:
                    if s["step"] == step and s["callout"] == 0:
                        return s["idx"]
            else:
                for s in self.unwrapped:
                    if s["step"] == step and s["level"] == 0:
                        return s["idx"]

        return len(self.unwrapped) - 1

    def print_callouts(self):
        for k, v in self.callouts.items():
            print(
                "Callout: level %d: %d -> %d parent: %d"
                % (v["level"], k, v["end"], v["parent"])
            )

    def is_callout_start(self, idx):
        """Returns True if the index to the unwrapped model points to a
        the beginning of a callout sequence."""
        return idx in self.callouts

    def prev_step_was_callout(self, idx):
        """Returns True if the previous step was in a callout."""
        callout_before = self[idx - 1]["callout"] > 0 if idx > 0 else False
        return callout_before

    def prev_step_was_callout_end(self, idx):
        """Returns True if the previous step ended a callout."""
        did_end = self.is_callout_end(idx - 1) if idx > 0 else False
        return did_end

    def is_callout_end(self, idx):
        """Returns True if the index to the unwrapped model points to a
        step at the end of a callout sequence."""
        for k, v in self.callouts.items():
            if v["end"] == idx:
                return True
        return False

    def callout_parent(self, idx):
        """Returns the level into the model hierarchy of a callout's
        parent level at the specified index into the unwrapped model."""
        level = 0
        for k, v in self.callouts.items():
            if idx >= k and idx <= v["end"]:
                level = max(level, v["parent"])
        return level

    def is_parent_a_callout(self, idx):
        """Returns True if at the index into the unwrapped model
        a callout step is contained in another callout."""
        my_parent = self.callout_parent(idx)
        if my_parent > 0:
            for k, v in self.callouts.items():
                if v["level"] == my_parent and idx >= k and idx <= v["end"]:
                    return True
        return False

    def has_assembly_arrows(self, idx):
        meta = self.unwrapped[idx]["meta"]
        for m in meta:
            if "arrow_begin" in m:
                return True
        return False

    def is_no_callout_meta(self, meta):
        for m in meta:
            if "no_callout" in m:
                return True
        return False

    def has_fixed_scale(self, idx):
        meta = self.unwrapped[idx]["meta"]
        for m in meta:
            if "scale" in m:
                return True
        return False

    def print_parts_at_idx(self, idx):
        parts = self.unwrapped[idx]["step_parts"]
        for p in parts:
            print(str(p).rstrip())

    def print_model_at_idx(self, idx):
        parts = self.unwrapped[idx]["parts"]
        for p in parts:
            print(str(p).rstrip())

    def print_pli_at_idx(self, idx):
        parts = self.unwrapped[idx]["pli_bom"]
        print(parts)

    def print_bom_at_idx(self, idx):
        print(self.unwrapped[idx]["pli_bom"])

    def get_sub_model_assem(self, submodel):
        """Returns the index into the unwrapped model of a specified
        sub-model assembly."""
        last_idx = 0
        submodel = submodel if ".ldr" in submodel else submodel + ".ldr"
        for s in self.unwrapped:
            if s["model"] == submodel:
                last_idx = max(last_idx, s["idx"])
        return last_idx

    def unwrap(self):
        self.unwrapped = self.unwrap_model()

    def unwrap_model(
        self,
        root=None,
        idx=None,
        level=None,
        model_name=None,
        model_qty=None,
        unwrapped=None,
    ):
        """This recursive function unwraps the entire sequence of building steps
        for a LDraw model.  This sequence unwraps nested building steps implied in
        the hierarchy of a model consisting of sub-models and the sub-model's
        children.  Unwrapping the model also allows pre-computation of transitions
        to nested sub-steps which can either be represented as callouts or inline
        build instructions.  The unwrapped model is represented as a list of
        dictionaries with a rich representation of the model at each step.
        The unwrapped model can then be traversed easily in a linear fashion
        by an iterator."""

        if root is None:
            idx = 0
            level = 0
            unwrapped = []
            model = self.steps
            model_name = "root"
            model_qty = 0
            self.continuous_step_count = 0
        else:
            idx = idx
            level = level
            model = root
            unwrapped = unwrapped
            model_name = model_name
            model_qty = model_qty
        for k, v in model.items():
            if len(v["sub_models"]) > 0:
                subs = unique_set(v["sub_models"])
                for name, qty in subs.items():
                    pli, steps = self.parse_model(name, is_top_level=False)
                    _, newidx = self.unwrap_model(
                        root=steps,
                        idx=idx,
                        level=level + 1,
                        model_name=name,
                        model_qty=qty,
                        unwrapped=unwrapped,
                    )
                    idx = newidx
            sd = {
                "idx": idx,
                "level": level,
                "step": k,
                "next_step": k + 1 if k < len(model.items()) else k,
                "num_steps": len(model.items()),
                "model": model_name,
                "qty": model_qty,
                "scale": v["scale"],
                "aspect": v["aspect"],
                "parts": v["parts"],
                "step_parts": v["step_parts"],
                "pli_bom": v["pli_bom"],
                "meta": v["meta"],
                "aspect_change": v["aspect_change"],
                "raw_ldraw": v["raw_ldraw"],
                "sub_parts": v["sub_parts"],
            }
            unwrapped.append(sd)
            idx += 1
        if level == 0:
            # when finished unwrapping the model, loop through the model
            # to add new keys for next and prev level changes and automatic
            # callout detection and page breaks across changes in level which
            # do not result in a callout.  Also apply step numbering scheme.
            umodel = []
            step_num = 1
            prev_level = 0
            next_level = 0
            prev_break = False
            callout = []
            callout_start = []
            callout_end = []
            callout_parent = []
            dont_callout_models = []
            for i, e in enumerate(unwrapped):
                level = e["level"]
                next_level = (
                    unwrapped[i + 1]["level"] if i < len(unwrapped) - 1 else level
                )
                level_up = True if next_level > level else False
                level_down = True if next_level < level else False
                levelled_up = True if level > prev_level else False
                levelled_down = True if level < prev_level else False
                next_steps = (
                    unwrapped[i + 1]["num_steps"]
                    if i < len(unwrapped) - 1
                    else e["num_steps"]
                )
                prev_steps = e["num_steps"] if i == 0 else unwrapped[i - 1]["num_steps"]
                dont_callout = (
                    self.is_no_callout_meta(unwrapped[i]["meta"])
                    if i < len(unwrapped)
                    else False
                )
                dont_callout_next = (
                    self.is_no_callout_meta(unwrapped[i + 1]["meta"])
                    if i < len(unwrapped) - 1
                    else False
                )
                if dont_callout:
                    dont_callout_models.append(e["model"])
                page_break = (
                    True if level_up and next_steps >= self.callout_step_thr else False
                )
                page_break = (
                    True
                    if level_down and e["num_steps"] >= self.callout_step_thr
                    else page_break
                )
                page_break = True if level_up and dont_callout_next else page_break
                page_break = (
                    True
                    if level_down and e["model"] in dont_callout_models
                    else page_break
                )
                pb = False
                for x in unwrapped[i]["meta"]:
                    if "page_break" in x:
                        pb = True
                page_break = True if pb else page_break
                no_pli = True if levelled_down and prev_break else False
                if (
                    levelled_up
                    and (e["num_steps"] < self.callout_step_thr)
                    and not dont_callout
                ):
                    callout.append(level)
                    callout_start.append(i)
                    callout_parent.append(prev_level)
                elif levelled_down:
                    if len(callout) > 0:
                        callout.pop()
                        callout_end.append(i - 1)
                if len(callout) > 0:
                    callout_level = callout[len(callout) - 1]
                else:
                    callout_level = 0
                if self.continuous_step_numbers:
                    if callout_level == 0:
                        e["step"] = step_num
                        step_num += 1
                        self.continuous_step_count += 1
                x = {
                    **e,
                    "prev_level": prev_level,
                    "next_level": next_level,
                    "page_break": page_break,
                    "no_pli": no_pli,
                    "callout": callout_level,
                }
                umodel.append(x)
                prev_level = level
                prev_break = page_break
            if self.continuous_step_numbers:
                for e in umodel:
                    if e["callout"] == 0:
                        e["num_steps"] = self.continuous_step_count
            # pair up the callout boundaries in dictionary with the start
            # index as the key and the end index and parent level as values
            self.callouts = {}
            for x0, p in zip(callout_start, callout_parent):
                level = umodel[x0]["callout"]
                for x1 in callout_end:
                    endlevel = umodel[x1]["callout"]
                    if x1 >= x0 and level == endlevel:
                        self.callouts[x0] = {"level": level, "end": x1, "parent": p}
                        break

            return umodel
        return unwrapped, idx

    def transform_parts_to(self, parts, origin=None, aspect=None, use_exceptions=False):
        """Transforms the location and/or aspect angle of all the parts in
        a list to a fixed position and/or aspect angle."""
        origin = origin if origin is not None else self.global_origin
        aspect = aspect if aspect is not None else self.global_aspect
        if not isinstance(origin, Vector):
            origin = Vector(origin[0], origin[1], origin[2])
        tparts = []
        for p in parts:
            np = p.copy()
            angle = aspect
            # override the aspect angle for any parts which need a special
            # orientation for clarity
            if use_exceptions:
                if p.name in self.pli_exceptions:
                    angle = self.pli_exceptions[p.name]
            np.set_rotation(angle)
            np.move_to(origin)
            tparts.append(np)
        return tparts

    def transform_parts(self, parts, offset=None, aspect=None):
        """Transforms the geometry (location and or aspect angle) of all
        the parts in a list.  The transform is applied as an offset to
        the existing part geometry."""
        offset = offset if offset is not None else self.global_origin
        aspect = aspect if aspect is not None else self.global_aspect
        if not isinstance(offset, Vector):
            offset = Vector(offset[0], offset[1], offset[2])
        tparts = []
        if len(parts) < 1:
            return []
        if isinstance(parts[0], LDRPart):
            for p in parts:
                np = p.copy()
                np.rotate_by(aspect)
                np.move_by(offset)
                tparts.append(np)
            return tparts
        else:
            for p in parts:
                np = LDRPart()
                if np.from_str(p) is not None:
                    np.rotate_by(aspect)
                    np.move_by(offset)
                    tparts.append(str(np))
                else:
                    # print("part is None ", p)
                    tparts.append(p)
            return tparts

    def transform_colour(self, parts, to_colour, from_colour=None, as_str=False):
        """Transforms the colour of a provided list of parts."""
        tparts = []
        if len(parts) < 1:
            return
        if isinstance(parts[0], LDRPart):
            for p in parts:
                np = p.copy()
                np.change_colour(to_colour)
                tparts.append(np)
        else:
            for p in parts:
                np = LDRPart()
                if np.from_str(p) is not None:
                    np.change_colour(to_colour)
                    tparts.append(np)
        if as_str:
            return [str(p) for p in tparts]
        return tparts

    def parse_file(self):
        """Parses an LDraw file and determines the root model and any included
        submodels."""
        self.sub_models = {}
        with open(self.filename, "rt") as fp:
            files = fp.read().split("0 FILE")
            root = None
            if len(files) == 1:
                root = files[0]
            else:
                root = "0 FILE " + files[1]
                for sub_file in files[2:]:
                    sub_name = sub_file.splitlines()[0].lower().strip()
                    sub_str = "0 FILE" + sub_file
                    self.sub_model_str[sub_name] = sub_str
                    self.sub_models[sub_name] = get_parts_from_model(sub_str)
            self.pli, self.steps = self.parse_model(root, is_top_level=True)
        self.unwrap()

    def ad_hoc_parse(self, ldrstring, only_submodel=None):
        """Performs an adhoc parsing operation on a provided LDraw formatted text
        string. If any references are made to submodels, then it recursively un packs
        the parts for the submodels based on a previous call to parse_model.
        Optionally, the parsing can be confined to only one submodel identified
        by only_submodel."""
        model_parts = []
        step_parts = get_parts_from_model(ldrstring)
        recursive_parse_model(
            step_parts,
            self.sub_models,
            model_parts,
            reset_parts=False,
            only_submodel=only_submodel,
        )
        return model_parts

    def parse_model(self, root, is_top_level=True, mask_submodels=False):
        """Generic parser for LDraw text. It parses a model provided either as a string
        of the entire LDR file at root level or as a key to a submodel in the LDR file.
        In either case, it recursively traverses the LDraw tree including all the
        children of the desired model and returns two lists: one for the parts
        at each step and one representing the model at each step.

        To parse at the root:
           self.pli, self.steps = self.parse_model(root, is_top_level=True)
        To parse a submodel:
           pli, steps = self.parse_model("submodel.ldr", is_top_level=False)

        The PLI list is a list of LDRPart objects for each step.
        The steps list is list of dictionaries with the following data for each step:
            parts - the aggregate parts that form the model at the step
            step_parts - only the parts that have been added at the step
            sub_models - a list of submodels referred to in this step
            scale - the current model scale
            aspect - the current euler viewing aspect angle
            pli_bom - a BOM object containing the parts in this step
            meta - a list of dictionaries representing any meta commands
                   found in this step
            raw_ldraw - the raw LDraw text in the step
            aspect_change - a flag indicating the aspect angle has changed
            sub_parts - parts added to this step that come from sub-models
                        indexed by submodel name in a dictionary
        """
        is_masked = False
        if not is_top_level:
            if root in self.sub_model_str:
                root = self.sub_model_str[root]
            else:
                key = root + ".ldr"
                if key in self.sub_model_str:
                    root = self.sub_model_str[key]
                    is_masked = True if mask_submodels else False

        model_pli = {}
        model_steps = {}
        steps = root.split("0 STEP")
        model_parts = []

        current_aspect = self.global_aspect
        current_scale = self.global_scale
        callout_style = "top"

        step_num = 1
        progress_bar(0, len(steps), "Parsing:", length=50)
        for i, step in enumerate(steps):
            aspect_change = False
            step_parts = get_parts_from_model(step)
            meta_cmd = get_meta_commands(step)
            for cmd in meta_cmd:
                if "scale" in cmd:
                    current_scale = float(cmd["scale"]["values"][0])
                elif "callout" in cmd:
                    callout_style = cmd["callout"]["values"][0].lower()
                elif "rotation_abs" in cmd:
                    current_aspect = [float(x) for x in cmd["rotation_abs"]["values"]]
                    current_aspect[0] = -current_aspect[0]
                    current_aspect = tuple(current_aspect)
                    aspect_change = True if step_num > 1 else False
                elif "rotation_rel" in cmd:
                    aspect_change = True if step_num > 1 else False
                    ar = tuple([float(x) for x in cmd["rotation_rel"]["values"]])
                    current_aspect = (
                        (current_aspect[0] + ar[0]),
                        (current_aspect[1] + ar[1]),
                        (current_aspect[2] + ar[2]),
                    )
                    current_aspect = norm_aspect(current_aspect)
                elif "rotation_pre" in cmd:
                    current_aspect = preset_aspect(
                        current_aspect, cmd["rotation_pre"]["values"]
                    )
                    aspect_change = True if step_num > 1 else False

            # capture submodel references in this step
            subs = []
            for p in step_parts:
                if p["partname"] in self.sub_models:
                    subs.append(p["partname"])
            # capture the parts that have been added in this step
            # and store a transformed/normalized version for a PLI
            parts_in_step = []
            recursive_parse_model(
                step_parts, self.sub_models, parts_in_step, reset_parts=True
            )
            pli = self.transform_parts_to(
                parts_in_step,
                origin=(0, 0, 0),
                aspect=self.pli_aspect,
                use_exceptions=True,
            )
            # submodel parts stored in separate dictionaries for convenient
            # access if required
            sub_dict = {}
            for sub in subs:
                sub_parts = []
                recursive_parse_model(
                    step_parts,
                    self.sub_models,
                    sub_parts,
                    reset_parts=True,
                    only_submodel=sub,
                )
                pn = self.transform_parts(sub_parts, aspect=current_aspect)
                sub_dict[sub] = pn

            if len(pli) > 0:
                model_pli[step_num] = pli
                # Store a BOM object representation of the parts for convenience
                pli_bom = BOM()
                for p in pli:
                    pli_bom.add_part(BOMPart(1, p.name, p.attrib.colour))
                    if is_top_level:
                        self.bom.add_part(BOMPart(1, p.name, p.attrib.colour))
                # store the model representation
                recursive_parse_model(
                    step_parts, self.sub_models, model_parts, reset_parts=False
                )
                p = self.transform_parts(model_parts, aspect=current_aspect)
                # store only the parts added in this step
                pn = self.transform_parts(parts_in_step, aspect=current_aspect)
                # put all the collection info into a dictionary
                step_dict = {}
                step_dict["parts"] = p
                step_dict["sub_models"] = subs
                step_dict["aspect"] = current_aspect
                step_dict["scale"] = current_scale
                step_dict["raw_ldraw"] = step
                step_dict["step_parts"] = pn
                step_dict["pli_bom"] = pli_bom
                step_dict["meta"] = meta_cmd
                step_dict["aspect_change"] = aspect_change
                step_dict["sub_parts"] = sub_dict
                model_steps[step_num] = step_dict
                step_num += 1

            progress_bar(i, len(steps), "Parsing:", length=50)

        return model_pli, model_steps

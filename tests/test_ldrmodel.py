# Sample Test passing with nose and pytest

import os
import sys
import pytest

from math import sqrt

from fxgeometry import Vector
from pdfdoc import *
from ldrawpy import *

def test_parse_meta():
    line = "0 ROTSTEP 20 -45 0 ABS"
    meta = parse_special_tokens(line)
    assert "rotation_abs" in meta
    assert "values" in meta["rotation_abs"] 
    assert ["20", "-45", "0"] ==  meta["rotation_abs"]["values"]
    line = "0 !LPUB ASSEM MODEL_SCALE GLOBAL 0.5"
    meta = parse_special_tokens(line)
    assert "scale" in meta
    line = "0 !PY COLUMNS 2"
    meta = parse_special_tokens(line)
    assert "columns" in meta
    line = "0 !LPUB INSERT BOM"
    meta = parse_special_tokens(line)
    assert "bom" in meta
    line = "0 !PY ARROW BEGIN 0 50 0 20 50 0"
    meta = parse_special_tokens(line)
    assert "arrow_begin" in meta
    line = "0 !PY ARROW COLOUR 14"
    meta = parse_special_tokens(line)
    assert "arrow_colour" in meta
    line = "0 !PY ARROW LENGTH 3"
    meta = parse_special_tokens(line)
    assert "arrow_length" in meta


# def test_model_at_step():
#     m = model_at_step("./test_files/test_model.ldr", 9, origin=(0, -100,0), aspect=(-40, 55, 0))
#     ms = "".join(m)
#     ldview_render(ms, "./test_files/render_test_2.png")

# def test_parts_at_step():
#     m = model_at_step("./test_files/test_model.ldr", 3, parts_only=True)
#     ms = "".join(m)
#     ldview_render(ms, "./test_files/render_test_3.png")
#     m = model_at_step("./test_files/test_model.ldr", 4, origin=(0, -100,0), aspect=(-40, 55, 0), parts_only=True)
#     ms = "".join(m)
#     ldview_render(ms, "./test_files/render_test_4.png")

# def test_ldview_render():
#     p = parts_for_step("./test_files/test_model.ldr", 1)
#     ldview_render(p, "./test_files/render_test_1.png")

# def test_render_class():
#     fn = "./test_files/Polybulk.ldr"
#     ldv = LDViewRender(output_path="./test_files", dpi=150)
#     print(ldv)
#     for i in range(15):
#         m = model_at_step(fn, i+1, aspect=(-40,55,0))
#         ms = "".join(m)
#         fnr = "model_step_%d.png" % (i+1)
#         ldv.render_from_str(ms, fnr)

# def test_bound_box():
#     m = model_at_step("./test_files/test_model.ldr", 2)
#     bb_min, bb_max = ldr_bound_box(m)
#     assert bb_min == (-60.0, 0.0, 0.0)
#     assert bb_max == (60.0, 24.0, 50.0)
#     bb = ldr_bound_box(m, as_size=True)
#     assert bb == (120.0, 24.0, 50.0)
#     pix = ldu_to_pixels(bb, 300)

def test_model_class():
    # m = LDRModel(filename="./test_files/BallastR40Curve.ldr")
    m = LDRModel(filename="./test_files/test_model.ldr")
    # m = LDRModel(filename="./test_files/HEAHopperRev1.ldr")
    # m = LDRModel(filename="./test_files/Polybulk.ldr")

    m.parse_file()
    m.print_unwrapped()
    # print(m.sub_models)
    # print(m.get_sub_model_assem("submodel1"))
    # print(m.get_sub_model_assem("submodel2.ldr"))

    # m.print_unwrapped_verbose()
    # for i in range(len(m.unwrapped)):
    #     print("Parts at Idx: %d" % (i))
    #     m.print_parts_at_idx(i)
    # for i in range(len(m.unwrapped)):
    #     print("Model at Idx: %d" % (i))
    #     m.print_model_at_idx(i)
    # for i in range(len(m.unwrapped)):
    #     print("PLI at Idx: %d" % (i))
    #     m.print_pli_at_idx(i)
    # for i in range(len(m.unwrapped)):
    #     print("PLI BOM at Idx: %d" % (i))
    #     m.print_bom_at_idx(i)
    # for i in range(len(m.unwrapped)):
    #     print("PLI Ldraw at Idx: %d" % (i))
    #     x = m.get_ldraw_pli_at_idx(i)
    #     print(x)

    # print("BOM")
    # print(m.bom)
#     ldv = LDViewRender(output_path="./test_files", dpi=150)
#     m.parse_file()
#     print(m)
#     print("BOM")
#     print(m.get_bom(as_str=True))
#     print("PLI")
#     m.print_pli()
#     print("Model at step 4:")
#     p = m.get_model_at_step(4, as_str=True)
#     ldv.render_from_str(p, "model_test_step_4.png")
#     print(p)
#     print("PLI at step 8:")
#     p = m.get_parts_at_step(8, as_str=True)
#     ldv.render_from_str(p, "pli_test_step_8.png")
#     print(p)
#     pli = m.get_pli_at_step(8)
#     print(pli)

# _sytle_dict = {
#     "top-padding": 0.05 * inch,
#     "bottom-padding": 0.05 * inch,
#     "left-padding": 0.05 * inch,
#     "right-padding": 0.05 * inch,
# }


# def test_render_dpi():
#     for dpi in [150, 200, 300]:
#         fn = "./test_files/test_dpi.ldr"
#         ldv = LDViewRender(output_path="./test_files", dpi=dpi)
#         m = model_at_step(fn, 1, aspect=(-40,55,0))
#         ms = "".join(m)
#         fnr = "model_dpi_%d.png" % (dpi)
#         ldv.render_from_str(ms, fnr)
#         fno = "./test_files/model_dpi_%d.pdf" % (dpi)
#         c = canvas.Canvas(
#             fno,
#             pagesize=(8.5 * inch, 11 * inch)
#         )
#         c.saveState()
#         fni = os.path.normpath("./test_files" + os.sep + fnr)

#         tl = LayoutCell(6 * inch, 1 * inch)
#         tl.style.set_with_dict(
#             {
#                 "top-margin": 0.05 * inch,
#                 "bottom-margin": 0.1 * inch,
#                 "left-margin": 0.1 * inch,
#                 "right-margin": 0.05 * inch,
#             }
#         )
#         tl.style.set_tb_padding(0.1 * inch)

#         r = ImageRect(0, 0, fni, dpi=dpi, style=_sytle_dict)
#         r.auto_size = True
#         # w, h = r.get_content_size()
#         # r.rect.set_size(w, h)
#         # r.rect.move_top_left_to((1 * inch, 9 * inch))
#         tl.add_cell("Cell1", r, constraints=["top left"])
#         tl.rect.move_top_left_to((1 * inch, 9 * inch))
#         tl.draw_in_canvas(c)
#         c.showPage()
#         c.save()

# def test_render_grid_dpi():
#     for dpi in [150, 200, 300]:
#         fn = "./test_files/test_dpi.ldr"
#         ldv = LDViewRender(output_path="./test_files", dpi=dpi)
#         m = model_at_step(fn, 1, aspect=(-40,55,0))
#         ms = "".join(m)
#         fnr = "model_dpi_%d.png" % (dpi)
#         ldv.render_from_str(ms, fnr)
#         fno = "./test_files/model_grid_dpi_%d.pdf" % (dpi)
#         c = canvas.Canvas(
#             fno,
#             pagesize=(8.5 * inch, 11 * inch)
#         )
#         c.saveState()
#         fni = os.path.normpath("./test_files" + os.sep + fnr)

#         tr = TableGrid(5 * inch, 3 * inch)
#         tr.fill_dir = "row-wise"
#         tr.style.set_attr("vert-align", "bottom")
#         tr.style.set_with_dict(
#             {
#                 "top-margin": 0.05 * inch,
#                 "bottom-margin": 0.1 * inch,
#                 "left-margin": 0.1 * inch,
#                 "right-margin": 0.05 * inch,
#             }
#         )
#         tr.style.set_tb_padding(0.1 * inch)

#         r = ImageRect(0, 0, fni, dpi=dpi, style=_sytle_dict)
#         r.auto_size = True
#         # w, h = r.get_content_size()
#         # r.rect.set_size(w, h)
#         # r.rect.move_top_left_to((1 * inch, 9 * inch))
#         tr.add_cell("Cell1", r)
#         tr.rect.move_top_left_to((1 * inch, 9 * inch))
#         tr.draw_in_canvas(c)
#         c.showPage()
#         c.save()


# def test_render_grid_dpi():
#     tr = TableGrid(5 * inch, 3 * inch)
#     tr.fill_dir = "row-wise"
#     tr.style.set_attr("vert-align", "bottom")
#     tr.style.set_with_dict(
#         {
#             "top-margin": 0.05 * inch,
#             "bottom-margin": 0.1 * inch,
#             "left-margin": 0.1 * inch,
#             "right-margin": 0.05 * inch,
#         }
#     )
#     tr.style.set_tb_padding(0.1 * inch)

#     for x in range(15):
#         cl = "TableCell-%d" % (x) if x % 2 == 0 else "%d" % (x) * random.randint(1, 10) 
#         tc = TextRect(0, 0, cl, _text_dict)
#         tp = random.randint(1, 10) * 0.025 * inch
#         bp = random.randint(1, 10) * 0.025 * inch
#         tc.style.set_attr("top-padding", tp)
#         tc.style.set_attr("bottom-padding", bp)
#         tc.show_debug_rects = True
#         tr.add_cell(cl, tc)

#     assert len(tr) == 15
#     # assert tr.cells[0].label == "TableCell-0"
#     # assert tr.cells[1].label == "Grid 1"
#     # assert tr.cells[2].label == "TableCell-2"
#     c = canvas.Canvas("test_tablegrid_rows.pdf", pagesize=(8.5 * inch, 11.0 * inch))
#     c.saveState()

#     tr.rect.move_top_left_to(Point(1 * inch, 9 * inch))
#     tr.draw_in_canvas(c)
#     r = ContentRect(5 * inch, 3 * inch)
#     r.show_debug_rects = True
#     r.rect.move_top_left_to(Point(1 * inch, 9 * inch))
#     r.draw_in_canvas(c)

#     c.showPage()
#     c.save()

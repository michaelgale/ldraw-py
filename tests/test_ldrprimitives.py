# Sample Test passing with nose and pytest

import os
import sys
import pytest

from ldrawpy.ldrprimitives import *
from fxgeometry import Vector

def test_ldrline():
    l1 = LDRLine(0)
    l1.p2 = Vector(1, 2, 3)
    l1.translate(Vector(5, 10, 20))
    assert l1.p2.x == 6
    assert l1.p2.y == 12
    assert l1.p2.z == 23
    ls = str(l1).rstrip()
    assert ls == "2 0 5 10 20 6 12 23"


def test_ldrtriangle():
    t1 = LDRTriangle(0)
    t1.p2 = Vector(5, 10, 0)
    t1.p3 = Vector(10, 0, 0)
    t1.translate(Vector(2, 3, -7))
    assert t1.p3.x == 12
    assert t1.p3.y == 3
    assert t1.p3.z == -7
    ts = str(t1).rstrip()
    assert ts == "3 0 2 3 -7 7 13 -7 12 3 -7"

def test_ldrquad():
    q1 = LDRQuad(0)
    q1.p2 = Vector(0, 5, 0)
    q1.p3 = Vector(20, 5, 0)
    q1.p4 = Vector(20, 0, 0)
    q1.translate(Vector(7, 3, 8))
    assert q1.p4.x == 27
    assert q1.p4.y == 3
    assert q1.p4.z == 8
    qs = str(q1).rstrip()
    assert qs == "4 0 7 3 8 7 8 8 27 8 8 27 3 8"

def test_ldrpart():
    p1 = LDRPart(0)
    p1.attrib.loc = Vector(5, 7, 8)
    p1.name = '3002'
    assert p1.attrib.loc.x == 5
    assert p1.attrib.loc.y == 7
    assert p1.attrib.loc.z == 8
    ps = str(p1).rstrip()
    assert ps == "1 0 5 7 8 1 0 0 0 1 0 0 0 1 3002.dat"

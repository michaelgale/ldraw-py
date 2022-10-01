# Sample Test passing with nose and pytest

import os
import sys
import pytest

from ldrawpy import *
from ldrawpy.ldrcolour import FillColoursFromLDRCode, FillTitlesFromLDRCode


def test_init_colour():
    c1 = LDRColour(15)
    c2 = LDRColour("White")
    c3 = LDRColour([1.0, 1.0, 1.0])
    c4 = LDRColour([255, 255, 255])
    c5 = LDRColour("#FFFFFF")
    assert c1 == c2
    assert c1 == c3
    assert c1 == c4
    assert c1 == c5


def test_equality():
    c1 = LDRColour([0.4, 0.2, 0.6])
    c2 = LDRColour("#663399")
    assert c1 == c2
    c3 = LDRColour([102, 51, 153])
    assert c2 == c3


def test_dict_lookup():
    c1 = LDRColour(LDR_ORGYLW_COLOUR)
    assert c1.name() == "Orange/Yellow"
    c2 = LDRColour.SafeLDRColourName(LDR_ORGYLW_COLOUR)
    assert c2 == "Orange/Yellow"
    c3 = FillColoursFromLDRCode(LDR_BLKWHT_COLOUR)
    assert (1.0, 1.0, 1.0) in c3
    c4 = FillTitlesFromLDRCode(LDR_BLKWHT_COLOUR)
    assert "Black" in c4
    assert "White" in c4
    assert len(c4) == 2

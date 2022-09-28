# Sample Test passing with nose and pytest

import os
import sys
import pytest

from toolbox import *
from ldrawpy import *

fin = "./test_files/testfile2.ldr"

def test_cleanup():
    fno = fin.replace(".ldr", "_clean.ldr")
    clean_file(fin, fno)
    with open(fin, "r") as f:
        fl = f.read()
        assert len(fl) == 1284
        assert "-59.999975" in fl
    with open(fno, "r") as f:
        fl = f.read()
        assert len(fl) == 1101
        assert "-60" in fl
    
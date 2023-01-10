import pytest
from moms_apriltag import *
import numpy as np


def test_invalid_family():
    with pytest.raises(Exception):
        board((6,8), "tag25h19", 1)


def test_too_big():
    with pytest.raises(Exception):
        board((6,8), "tag25h9", 1)

    with pytest.raises(Exception):
        board((6,8), "tag16h5", 1)


# def test_size():
#     x = board((2,2), "tag25h9", 1)
#     print(x.shape)
#     assert x.shape == (2*3+2*7,20,)

#     x = board((2,2), "tag36h10", 1)
#     assert x.shape == (2*3+2*8,22,)

#     x = board((2,2), "tag36h10", 10)
#     assert x.shape == (220,220,)

def test_wrong_marker():

    with pytest.raises(ValueError):
        for fam in apriltags_v2:
            tg = TagGenerator3(fam)

        for fam in apriltags_v3:
            tg = TagGenerator2(fam)

def test_marker_size():
    for fam in apriltags_v2:
        tg = TagGenerator2(fam)
        im = tg.generate(0)
        s = tg.size + 2 # fix +2 buffer dimension
        # assert tg.area == s*s
        assert im.shape == (s,s)

    for fam in apriltags_v3:
        tg = TagGenerator3(fam)
        im = tg.generate(0)
        s = tg.template.size
        assert im.shape == (s,s)

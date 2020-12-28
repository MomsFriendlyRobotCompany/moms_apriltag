import pytest
import moms_apriltag as apt
import numpy as np


def test_invalid_family():
    with pytest.raises(Exception):
        apt.board((6,8), "tag25h19", 1)


def test_too_big():
    with pytest.raises(Exception):
        apt.board((6,8), "tag25h9", 1)

    with pytest.raises(Exception):
        apt.board((6,8), "tag16h5", 1)


def test_size():
    x = apt.board((2,2), "tag25h9", 1)
    print(x.shape)
    assert x.shape == (2*3+2*7,20,)

    x = apt.board((2,2), "tag36h10", 1)
    assert x.shape == (2*3+2*8,22,)

    x = apt.board((2,2), "tag36h10", 10)
    assert x.shape == (220,220,)

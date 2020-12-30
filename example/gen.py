#!/usr/bin/env python3
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import moms_apriltag as apt
import numpy as np
import imageio


if __name__ == '__main__':
    # family = "tag36h11"
    family = "tag36h11"
    # family = "tag25h9"
    shape = (6,9)
    filename = "apriltag_target.png"
    size = 50

    tgt = apt.board(shape, family, size)
    imageio.imwrite(filename, tgt)

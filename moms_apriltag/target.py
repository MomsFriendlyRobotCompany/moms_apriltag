# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################

import numpy as np
# from .tag_generate import generate
# import sys
# import math
# import numpy as np
# from PIL import Image
from collections import namedtuple
# from sys import exit

from .tags import tag16h5
from .tags import tag25h9
from .tags import tag36h10
from .tags import tag36h11

# so I have to do padding and change my code below to
# make these tag formats work.
# from .tags import tag41h12
# from .tags import tagCircle21h7

flip = lambda a: a^1

Tag = namedtuple("Tag", "family id array")

apriltags = {
    "tag16h5": tag16h5,
    "tag25h9": tag25h9,
    "tag36h10": tag36h10,
    "tag36h11": tag36h11,
    # "tag41h12": tag41h12,
    # "tagCircle21h7": tagCircle21h7
}

def gen_tag(tag, val):
    """
    Generate a tag with the given value, return a numpy array
    """
    d = np.frombuffer(np.array(tag.codes[val], ">i8"), np.uint8)
    bits = np.unpackbits(d)[-tag.area:].reshape((-1,tag.dim))
    bits = np.pad(bits, 1, 'constant', constant_values=0)
    # bits = np.pad(bits, 2, 'constant', constant_values=1)
    return bits


def generate(family, nums):
    """
    Given a tag family and list of IDs, return an array of numpy arrays
    corresponding to those IDs.

    family: tag16h5, tag25h9, tag36h10, tag36h11
    nums: an array of id, ex [1,2,3, ... 45,46,47]
    """
    try:
        tagdata = apriltags[family]
    except:
        raise Exception(f"*** Invalid family: {family} ***")
        # exit(1)

    tags = [Tag(family, n, gen_tag(tagdata, n)) for n in nums]
    return tags


def check_size(r, size):
    if r >= size:
        raise Exception(f"family board size exceeded: {r} != {size}")

def board(marker_size, family, scale=10, ofw=2, span=None):
    """
    marker_size: dimensions of board, tuple(rows, cols)
    family: family of the tag, string
    scale: scale image by a factor, default: 10
    ofw: offset between tags, this is affected by scale size,
         default: 2 (2*scale is what is really is)
    span: tag numbers to use, default: None
    """
    if span:
        r = span
        if len(span) != marker_size[0]*marker_size[1]:
            raise Exception("len(span) != marker_size[0]*marker_size[1]")
    else:
        r = marker_size[0]*marker_size[1]

    if family == "tag36h10":
        check_size(r, len(tag36h10.codes))
        tag_size = 8
    elif family == "tag36h11":
        check_size(r, len(tag36h11.codes))
        tag_size = 8
    elif family == "tag25h9":
        check_size(r, len(tag25h9.codes))
        tag_size = 7
    elif family == "tag16h5":
        check_size(r, len(tag16h5.codes))
        tag_size = 6
    else:
        raise Exception(f"Invalid tag family: {family}")

    tags = generate(family, range(r))

    ofr = tag_size+ofw
    ofc = tag_size+ofw
    r = marker_size[0]*(ofr)
    c = marker_size[1]*(ofc)
    b = np.ones((r,c))
    box = np.zeros((ofw,ofw))

    for i in range(marker_size[0]):     # rows
        for j in range(marker_size[1]): # cols
            r = i*(ofr)
            c = j*(ofc)
            x = i*marker_size[1]+j
            tag = tags[x].array
            b[r:r+tag_size,c:c+tag_size] = tag

    # border
    r,c = b.shape
    mm = np.ones((r+ofw, c+ofw), dtype=np.uint8)
    mm[ofw:,ofw:] = b


    for i in range(marker_size[0]+1):     # rows
        for j in range(marker_size[1]+1): # cols
            r = i*(ofr)
            c = j*(ofc)
            mm[r:r+ofw,c:c+ofw] = box

    # mm = 255*flip(mm)
    mm = 255*mm

    # scale image
    xx = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)

    return xx

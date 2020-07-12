# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import sys
import math
import numpy as np
from PIL import Image
from collections import namedtuple

from .tags import tag16h5
from .tags import tag25h9
from .tags import tag36h10
from .tags import tag36h11

Tag = namedtuple("Tag", "family id array")

apriltags = {
    "tag16h5": tag16h5,
    "tag25h9": tag25h9,
    "tag36h10": tag36h10,
    "tag36h11": tag36h11
}

# Generate a tag with the given value, return a numpy array
def gen_tag(tag, val):
    d = np.frombuffer(np.array(tag.codes[val], ">i8"), np.uint8)
    bits = np.unpackbits(d)[-tag.area:].reshape((-1,tag.dim))
    bits = np.pad(bits, 1, 'constant', constant_values=0)
    # bits = np.pad(bits, 2, 'constant', constant_values=1)
    return bits


def save(ext, arrays, pixels=1):
    """
    Save the tag to an image file of size (pixel, pixel)

    ext: jpg, png, bmp, tif
    array: list of numpy tag arrays
    pixel: pixel dimension of the image
    """
    for family, id, a in arrays:
        # (h,w) = a.shape
        img = Image.fromarray(a * 255)
        # img = img.resize((w*scale, h*scale), resample=Image.NEAREST)
        img = img.resize((pixels, pixels), resample=Image.NEAREST)
        img.save(f"{family}-{id:0>4d}.{ext}", ext)

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
        print(f"*** Invalid family: {family} ***")
        exit(1)

    tags = [Tag(family, n, gen_tag(tagdata, n)) for n in nums]
    return tags


flip = lambda a: a^1

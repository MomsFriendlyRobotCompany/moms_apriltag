# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import numpy as np

class TagGenerator2:
    """
    Generator for tags.

    tag_gen = TagGenerator("tag16h5")
    tag_im22 = tag_gen.generate(22)           # this is 9x9 px
    tag_im42 = tag_gen.generate(42, scale=50) # this is 50x50 px
    """
    def __init__(self, name):
        fmt = None
        if name == "tag16h5":
            from .tags import tag16h5 as MYTAG
        elif name == "tag25h9":
            from .tags import tag25h9 as MYTAG
        elif name == "tag36h10":
            from .tags import tag36h10 as MYTAG
        elif name == "tag36h11":
            from .tags import tag36h11 as MYTAG
        else:
            raise ValueError(name)

        self.codes = MYTAG.codes
        self.area = MYTAG.area
        self.size = MYTAG.dim
        self.max_id = len(MYTAG.codes)

    def generate(self, val, scale=None):
        """
        Generate a tag with the given value, return a numpy array
        """
        if val > self.max_id:
            raise Exception(f"*** tag id {val} exceeded max id value {self.max_id} ***")
        d = np.frombuffer(np.array(self.codes[val], ">i8"), np.uint8)
        bits = np.unpackbits(d)[-self.area:].reshape((-1,self.size))
        tag = np.pad(bits, 1, 'constant', constant_values=0)
        # bits = np.pad(bits, 2, 'constant', constant_values=1)

        if scale:
            tag = np.repeat(np.repeat(tag, scale, axis=0), scale, axis=1)

        return tag
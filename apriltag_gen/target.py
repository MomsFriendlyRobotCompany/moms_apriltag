# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################


def board(self, marker_size, family, scale=10, ofw=2):
    r = marker_size[0]*marker_size[1]
    # family = self.detector.params["families"][0]
    tags = apt.generate(family, range(r))

    ofr = 8+ofw
    ofc = 8+ofw
    r = marker_size[0]*(ofr)
    c = marker_size[1]*(ofc)
    b = np.ones((r,c))

    for i in range(marker_size[0]):     # rows
        for j in range(marker_size[1]): # cols
            r = i*(ofr)
            c = j*(ofc)
            x = i*marker_size[1]+j
            tag = tags[x].array
            b[r:r+8,c:c+8] = tag

    # border
    r,c = b.shape
    mm = np.ones((r+ofw, c+ofw), dtype=np.uint8)
    mm[ofw:,ofw:] = b
    mm = 255*mm

    # scale image
    xx = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)

    return xx

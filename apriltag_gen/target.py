# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
from .apr import generate
import numpy as np


def board(marker_size, family, scale=10, ofw=2, span=None):
    """
    marker_size: dimensions of board, tuple(rows, cols)
    family: family of the tag, string
    scale: scale image by a factor, default: 10
    ofw: offset between tags, this is affected by scale size, default: 2 (2*scale is what is really is)
    span: tag numbers to use, default: None
    """
    if span:
        r = span
        if len(span) != marker_size[0]*marker_size[1]:
            raise Exception("Span doesn't fit inside marker_size; len(span) != marker_size[0]*marker_size[1]")
    else:
        r = marker_size[0]*marker_size[1]

    tag_size = 8 # families 36h11/10
    if family == "tag25h9":
        tag_size = 7
    elif family == "tag16h5":
        tag_size = 6

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

    mm = 255*mm

    # scale image
    xx = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)

    return xx

# def board3():
#     family = "tag36h11"
#     a = 12
#     b = 22
#     tags = apt.generate(family, range(a,b))
#     print(tags[0])
#     # print(apt.flip(tags[0].array))
#     # apt.save("png", tags, 30)
#
#     t = tags[0].array
#     tt = np.array(t^1, dtype=np.uint8)
#     # print(t)
#     # print(tt)
#     # tt = apt.Tag(t.family + "-w",t.id,t.array^1)
#     # apt.save("png", [tt],300)
#     a = np.hstack((t,tt,t,tt))
#     aa = np.hstack((tt,t,tt,t))
#     a = np.vstack((a,aa,a,aa))
#     img = Image.fromarray(a * 255)
#     h,w = a.shape
#     s = w*30
#     img = img.resize((s, s), resample=Image.NEAREST)
#     # img = img.resize((pixels, pixels), resample=Image.NEAREST)

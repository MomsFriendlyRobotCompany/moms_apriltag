#!/usr/bin/env python3
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import apriltag_gen as apt
import numpy as np
from PIL import Image

def main():
    family = "tag36h11"
    a = 12
    b = 22
    tags = apt.generate(family, range(a,b))
    print(tags[0])
    # print(apt.flip(tags[0].array))
    apt.save("png", tags, 30)

    t = tags[0].array
    tt = np.array(t^1, dtype=np.uint8)
    # print(t)
    # print(tt)
    # tt = apt.Tag(t.family + "-w",t.id,t.array^1)
    # apt.save("png", [tt],300)
    a = np.hstack((t,tt,t,tt))
    aa = np.hstack((tt,t,tt,t))
    a = np.vstack((a,aa,a,aa))
    img = Image.fromarray(a * 255)
    h,w = a.shape
    s = w*30
    img = img.resize((s, s), resample=Image.NEAREST)
    # img = img.resize((pixels, pixels), resample=Image.NEAREST)
    img.save("bob.png")



if __name__ == '__main__':
    main()

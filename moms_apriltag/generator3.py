# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import numpy as np

NOTHING   = 0
WHITE     = 1
BLACK     = 2
DATA      = 3
RECURSIVE = 4

class ImageLayout:
    """
    ImageLayout holds the template for the tag
    generation.

    size: number pixels per side
    numBits: number of encoded bits in tag
    pixels: 2D numpy array template of DATA, BLACK, WHITE
            which marks how the tag should be filled out
            with information.
    """
    # value for these????
    # WHITE = 0xffffffff
    # BLACK = 0xff000000
    # TRANSPARENT = 0x00000000
    # name
    # dataString
    # borderWidth
    # borderStart
    # reverseBorder

    def __init__(self,size, numBits, pixels):
        self.size = size
        self.numBits = numBits
        self.pixels = pixels

    @classmethod
    def createFromString(cls, fmt):
        """
        This is a factory function that returns a new
        ImageLayout object from the formatting string.

        fmt: formatting string
        """

        def getPixelTypeForChar(c):
            if   c == 'x': return NOTHING
            elif c == 'd': return DATA
            elif c == 'w': return WHITE
            elif c == 'b': return BLACK
            elif c == 'r': raise NotImplementedError()
            else: raise ValueError(c)

        # layout = ImageLayout()
        size = int(np.sqrt(len(fmt)))
        pixels = np.zeros((size, size))
        numBits = 0
        loc = 0
        for c in fmt:
            pixelType = getPixelTypeForChar(c)
            if pixelType == DATA:
                numBits += 1
            row = loc // size
            col = loc % size
            pixels[row, col] = pixelType
            loc += 1
        layout = cls(size, numBits, pixels)
        return layout


class TagGenerator3:
    """
    Generator for tags.

    tag_gen = TagGenerator("tagStandard41h12")
    tag_im22 = tag_gen.generate(22)           # this is 9x9 px
    tag_im42 = tag_gen.generate(42, scale=50) # this is 50x50 px
    """
    def __init__(self, name):
        if name == "tagStandard41h12":
            from .tags import tagStandard41h12 as MYTAG
        elif name == "tagStandard52h13":
            from .tags import tagStandard52h13 as MYTAG
        elif name == "tagCircle21h7":
            from .tags import tagCircle21h7 as MYTAG
        elif name == "tagCircle49h12":
            from .tags import tagCircle49h12 as MYTAG
        elif name == "tagCustom48h12":
            from .tags import tagCustom48h12 as MYTAG
        else:
            raise ValueError(name)

        self.codes = MYTAG.codes
        self.max_id = len(MYTAG.codes)
        fmt = MYTAG.fmt
        self.template = ImageLayout.createFromString(fmt)

    def generate(self, tag_id, scale=None):
        if tag_id > self.max_id:
            raise Exception(f"*** tag id {tag_id} exceeded max id value {self.max_id} ***")

        code = self.codes[tag_id]
        pixels = self.template.pixels.copy()
        tag = self.renderToImage(pixels, code)

        if scale:
            tag = np.repeat(np.repeat(tag, scale, axis=0), scale, axis=1)

        return tag

    def setPixel(self, pix, code):
        numBits = self.template.numBits

        if pix == DATA:
            bits = (code & (1 << (numBits -1)))
            code = code << 1
            value = 0xff if bits != 0 else 0x00
        elif pix == BLACK:
            value = 0x00
        elif pix == WHITE:
            value = 0xff
        elif pix == NOTHING:
            value = 127
        return value, code

    def renderToImage(self, p, code):
        size = self.template.size

        for i in range(4):
            p = np.rot90(p)

            # render 1/4 of image
            for r in range(size//2 + 1):
                for c in range(r, size - 1 - r):
                    pix = p[r,c]
                    value, code = self.setPixel(pix, code)
                    p[r,c] = value
        p = np.rot90(p)

        # set middle pixel
        if (size % 2) == 1:
            r = size//2
            c = r
            pix = p[r,c]
            value, code = self.setPixel(pix, code)
            p[r,c] = value

        return p

    def toRGBA(self, im):
        """
        Circular tags have a translucent value which is
        carried as 127. However, when saving to a file,
        which has to png, we need to add an alpha layer
        and then you can save it using cv2.imwrite() or
        something.
        """
        a = np.where(im == 127, 0, 255)
        png = np.dstack((im, im, im, a))
        return png

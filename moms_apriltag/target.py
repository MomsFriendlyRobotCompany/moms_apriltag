# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import numpy as np
import cv2
import cv2.aruco as aruco
from dataclasses import dataclass
from .generator2 import apriltags_v2
from .generator2 import tag_sizes_v2 as tag_sizes
# from .generator3 import apriltags_v3
# from collections import namedtuple
# from matplotlib import pyplot as plt
# from .color_space import bgr2gray, gray2bgr

# tag_sizes_v2 = {
#     "tag16h5": 6,
#     "tag25h9": 7,
#     "tag36h10": 8,
#     "tag36h11": 8,
# }

arucoTags = {
    "tag16h5": cv2.aruco.DICT_APRILTAG_16H5,
    "tag25h9": cv2.aruco.DICT_APRILTAG_25H9,
    "tag36h10": cv2.aruco.DICT_APRILTAG_36H10,
    "tag36h11": cv2.aruco.DICT_APRILTAG_36H11,
}

@dataclass
class TextWriter:
    """
    Simple class to hold info for writing text on an image
    """
    fontScale: int
    color: tuple
    thickness: int = 2
    font: int = cv2.FONT_HERSHEY_SIMPLEX

    def write(self, img, text, org, color=None):
        if color is None:
            color = self.color
        return cv2.putText(
            img,
            text, org,
            self.font,
            self.fontScale,
            color,
            self.thickness,
            cv2.LINE_AA)

@dataclass
class ApriltagBoard:
    """

    Board
    - objectPoints: dict, 3D corner points of tag
    - board: np.array grayscale image of shape (x,y)
    """
    boardSize:tuple # (rows, cols)
    family:str
    tagEdgeLength:float # meters

    scale:int = 40 # image pixel scale
    squareSize:int = 2 # in pixels
    ids:list = None # marker ids on board
    __objpts:dict = None # small unscaled 3d board corners
    objPoints:dict = None # scaled 3d board corners
    generator = None # value?
    __target: np.ndarray = None # numpy image

    def __post_init__(self):
        """
        Automatically called when created to build board image and
        3D object points
        """
        #FIXME: clean up these variable names

        r,c = self.boardSize
        self.ids = list(range(r*c))

        if self.family in apriltags_v2:
            from moms_apriltag.generator2 import TagGenerator2 as TagGenerator
        # elif self.family in apriltags_v3:
        #     from moms_apriltag.generator3 import TagGenerator3 as TagGenerator
        else:
            raise Exception(f"*** Invalid family: {self.family} ***")

        tg = TagGenerator(self.family)
        self.generator = tg
        tags = {n:tg.generate(n) for n in self.ids}

        ofw = self.squareSize # small black square size

        tag_size = tag_sizes[self.family]

        ofr = tag_size+ofw # offset row
        ofc = tag_size+ofw # offset col
        boardRows = self.boardSize[0]*(ofr)
        boardCols = self.boardSize[1]*(ofc)

        box = np.zeros((ofw,ofw), dtype=np.uint8) # small black box
        canvas = 255*np.ones((boardRows+ofw, boardCols+ofw), dtype=np.uint8)

        self.__objpts = {}
        self.objPoints = {}

        tagScale = self.tagEdgeLength/tag_size

        # draw tags ----------------------------------------------------
        for i in range(self.boardSize[0]):     # rows
            for j in range(self.boardSize[1]): # cols
                r = ofw+i*(ofr)
                c = ofw+j*(ofc)
                rr = r+tag_size
                cc = c+tag_size
                id = i*self.boardSize[1]+j # self.boardSize => board_size

                tag = tags[id]

                canvas[r:rr,c:cc] = tag # already 0-255
                self.__objpts[id] = np.array((
                    (rr,cc,0.0),
                    (rr,c,0.0),
                    (r,c,0.0),
                    (r,cc,0.0))) # ccw - best
                self.objPoints[id] = tagScale* self.__objpts[id]
                # print("tag", np.min(tag), np.max(tag))

        # draw little black square ------------------------------------
        for i in range(self.boardSize[0]+1):     # rows
            for j in range(self.boardSize[1]+1): # cols
                r = i*(ofr)
                c = j*(ofc)
                canvas[r:r+ofw,c:c+ofw] = box

        # scale image
        scale = self.scale
        canvas = np.repeat(np.repeat(canvas, scale, axis=0), scale, axis=1)

        # write info to target: family, size -------------------------
        # canvas = gray2bgr(canvas)

        w = TextWriter(2,(0,0,0), thickness=5)
        col = int(scale*ofw*1.2)
        row = int(scale*ofw*0.7)
        # canvas = w.write(canvas, f"{self.family}, {self.boardSize}", (col, row))
        canvas = w.write(canvas, f"{self.family}", (col, row))

        col = int(scale*(2*ofw + tag_size + 0.5))
        canvas = w.write(canvas, f"{self.boardSize}", (col, row))

        # write the first couple tag numbers -------------------------
        col = scale*ofw//4
        row = 3*scale*ofw//4
        numcolor = (255,255,255)
        w.fontScale = self.squareSize
        canvas = w.write(canvas, "0", (col, row), color=numcolor)

        col = int(scale*(ofw/4 + tag_size + ofw))
        w.fontScale = self.squareSize
        canvas = w.write(canvas, "1", (col, row), color=numcolor)

        col = int(scale*(ofw/4 + 2*(tag_size + ofw)))
        w.fontScale = self.squareSize
        canvas = w.write(canvas, "2", (col, row), color=numcolor)

        self.__target = canvas
        # print("generate", np.min(canvas), np.max(canvas))


    def find(self, gray):
        """
        Given an image, this will return tag corners. The input flags are not
        used.

        return:
            success: (True, [corner points],[object points])
            failure: (False, None, None)
        """
        if len(gray[0].shape) > 2:
            raise Exception(f"Images must be grayscale, not shape: {gray[0].shape}")

        # additionally, I do a binary thresholding which greatly reduces
        # the apriltag's bad corner finding which resulted in non-square
        # tags which gave horrible calibration results.
        # ok, gray = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
        # if not ok:
        #     return False, None, None

        # use cv2.aruco to find tags
        # corners: tuple of numpy array (1,4,2), length N ... why?
        # ids: numpy array shape (N,1)
        arucoTagName = arucoTags[self.family]
        corners, ids, rejectedImgPts = aruco.detectMarkers(
            gray,
            aruco.Dictionary_get(arucoTagName),
            parameters=aruco.DetectorParameters_create(),
        )
        if corners is None or ids is None:
            return False, None, None
        elif len(corners) == 0:
            return False, None, None

        ids = ids.ravel() # flatten in an array

        corners = [c.reshape(-1,2) for c in corners] # make (4,2)
        # print("apriltagfinder corners",np.array(corners).shape)

        # get complete listing of objpoints in a target
        opdict = self.objPoints

        ob = []
        tt = []
        # for each tag, get corners and obj point corners:
        # for tag in tags:
        for tag_id, corner in zip(ids, corners):
            # add found objpoint to list IF tag id found in image
            try:
                # obcorners = opdict[tag_id]
                obcorners = self.objPoints[tag_id]
            except KeyError as e:
                print(f"*** {e} ***")
                continue

            for oc in obcorners:
                ob.append(oc)
            for c in corner:
                tt.append([c])

        corners = np.array(tt, dtype=np.float32)
        objpts = np.array(ob, dtype=np.float32)

        return True, corners, objpts, ids

    @classmethod
    def create(cls, rows, columns, family, tagEdgeLength):
        """
        Useful?
        """
        board = cls((rows, columns), family, tagEdgeLength)
        return board

    def objPointsScale(self, scale):
        """
        Rescale the object 3D object points. Useful?

        scale: edge size of a tag
        """
        return {x:scale*self.__objpts[x] for x in self.__objpts.keys()}
        # return self.objpts

    def getTag(self, id, scale=None):
        """
        Generate individual tags. Does not check if id number exceeds
        apriltag family max id value.

        Not sure value, could do Generator2/3.generate(id) instead.
        """
        if scale is None:
            scale = self.scale
        tag = self.generator.generate(id)
        return np.repeat(np.repeat(tag, scale, axis=0), scale, axis=1)

    @property
    def board(self):
        return self.__target

    # def imagePoints(self):
    #     """
    #     Returns a set of the target's ideal 3D feature points.
    #     sz: size of board, ex: (6,9)
    #     ofw: offset width, ex: 2px
    #     """
    #     ofw = self.squareSize
    #     # family = self.detector.params["families"][0]
    #     pix = tag_sizes[self.family]
    #     sz = self.boardSize
    #     scale = self.scale #/8
    #     ofr = pix+ofw
    #     ofc = pix+ofw
    #     r = sz[0]*(ofr)
    #     c = sz[1]*(ofc)
    #     # b = np.ones((r,c))
    #     objpts = {}
    #     tags = []

    #     for i in range(sz[0]):     # rows
    #         for j in range(sz[1]): # cols
    #             r = i*(ofr)+ofw
    #             c = j*(ofc)+ofw
    #             x = i*sz[1]+j

    #             rr = r+pix
    #             cc = c+pix
    #             corners = (
    #                 (scale*rr,scale*c,0),
    #                 (scale*rr,scale*cc,0),
    #                 (scale*r,scale*cc,0),
    #                 (scale*r,scale*c,0)) # ccw - best


    #             corners2d = (
    #                 (rr,c),
    #                 (rr,cc),
    #                 (r,cc),
    #                 (r,c)) # ccw - best

    #             corners2d = scale*np.array(corners2d)

    #             # objpts[x] = corners

    #             tags.append(Tag2(x, corners2d))
    #     # return objpts
    #     return tags



def draw_tag(color_img, corners, tag_id=None, mark=False):
    """
    color_img: image to draw on, must be color
    corners: corner points from apriltag detector, v[0] is the
                lower left of the tag and the point move CCW.
    tag_id [string]: write tag id number
    mark [bool]: draw a circle in the middle of the tag to see detection easier
    """
    v = corners.astype('int32')
    pts = corners.reshape((-1,1,2)).astype('int32')
    t = int(abs(v[0][0] - v[1][0])/20)
    cv2.polylines(color_img,[pts],True,(0,255,0),thickness=t)

    if mark:
        # center = (
        #     v[0][0]+abs(v[2][0]-v[0][0])//2,
        #     v[0][1]-abs(v[2][1]-v[0][1])//2
        # )
        # r = abs(v[0][0] - v[1][0])//2//2
        # r = 5
        # cv2.circle(color_img,center, r, (200,0,255), -1)

        # [tr, br,bl,tl]

        r,c = v[1,:] - v[3,:]
        center = (
            v[3,0] + r//2,
            v[3,1] + c//2
        )
        rad = r//10
        # r = 5
        # print(corners.shape, center, r, corners)
        cv2.circle(color_img,center, rad, (200,0,255), -1)

    # r = 15
    y = color_img.shape[0]
    # r = max(int(y/200),1)
    c = (255,0,0)
    oc = (0,0,255)
    # v = corners.astype('int32')
    # r = int(abs(v[0][0] - v[1][0])/15)
    # r,_ = v[1,:] - v[3,:]
    r = (v[1,0] - v[3,0]) // 20
    # r = 10
    # print(r)
    # cv2.circle(color_img, tuple(v[0,:]),r,oc,thickness=-1)
    # cv2.circle(color_img, tuple(v[1,:]),r,c,thickness=-1)
    # cv2.circle(color_img, tuple(v[2,:]),r,c,thickness=-1)
    cv2.circle(color_img, tuple(v[3,:]),r,c,thickness=-1)

    if tag_id is not None:
        offset = (v[1][0]-v[0][0])//4
        fs = r//3
        cv2.putText(
            color_img, str(tag_id),
            org=(v[0][0]+offset,v[0][1]-offset,),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=fs,
            thickness=2*fs,
            color=(255, 0, 255))

    return color_img



# import numpy as np
# from collections import namedtuple

# flip = lambda a: a^1

# Tag = namedtuple("Tag", "family id array")

# apriltags_v2 = [
#     "tag16h5",
#     "tag25h9",
#     "tag36h10",
#     "tag36h11",
# ]

# apriltags_v3 = [
#     "tagCircle21h7",
#     "tagCircle49h12",
#     "tagCustom48h12",
#     "tagStandard41h12",
#     "tagStandard52h13",
# ]


# # def gen_tag(tag, val):
# #     """
# #     Generate a tag with the given value, return a numpy array
# #     """
# #     d = np.frombuffer(np.array(tag.codes[val], ">i8"), np.uint8)
# #     bits = np.unpackbits(d)[-tag.area:].reshape((-1,tag.dim))
# #     bits = np.pad(bits, 1, 'constant', constant_values=0)
# #     # bits = np.pad(bits, 2, 'constant', constant_values=1)
# #     return bits


# def generate(family, nums):
#     """
#     Given a tag family and list of IDs, return an array of numpy arrays
#     corresponding to those IDs.

#     family: tag16h5, tag25h9, tag36h10, tag36h11
#     nums: an array of id, ex [1,2,3, ... 45,46,47]
#     """
#     if isinstance(nums, range):
#         nums = list(nums)
#     if not isinstance(nums, list):
#         nums = [nums]

#     if family in apriltags_v2:
#         from .generator2 import TagGenerator2 as TagGenerator
#     elif family in apriltags_v3:
#         from .generator3 import TagGenerator3 as TagGenerator
#     else:
#         raise Exception(f"*** Invalid family: {family} ***")

#     tg = TagGenerator(family)
#     tags = [Tag(family, n, tg.generate(n)) for n in nums]
#     return tags


# # def check_size(r, size):
# #     if r >= size:
# #         raise Exception(f"family board size exceeded: {r} != {size}")

# def board(marker_size, family, scale=10, ofw=2, span=None):
#     """
#     marker_size: dimensions of board, tuple(rows, cols)
#     family: family of the tag, string
#     scale: scale image by a factor, default: 10
#     ofw: offset between tags, this is affected by scale size,
#          default: 2 (2*scale is what is really is)
#     span: tag numbers to use, default: None
#     """
#     if span:
#         r = span
#         if len(span) != marker_size[0]*marker_size[1]:
#             raise Exception("len(span) != marker_size[0]*marker_size[1]")
#     else:
#         r = marker_size[0]*marker_size[1]

#     if family == "tag36h10":
#         # check_size(r, len(tag36h10.codes))
#         tag_size = 8
#     elif family == "tag36h11":
#         # check_size(r, len(tag36h11.codes))
#         tag_size = 8
#     elif family == "tag25h9":
#         # check_size(r, len(tag25h9.codes))
#         tag_size = 7
#     elif family == "tag16h5":
#         # check_size(r, len(tag16h5.codes))
#         tag_size = 6
#     else:
#         raise Exception(f"Invalid tag family: {family}")

#     tags = generate(family, range(r))

#     ofr = tag_size+ofw
#     ofc = tag_size+ofw
#     r = marker_size[0]*(ofr)
#     c = marker_size[1]*(ofc)
#     b = np.ones((r,c))
#     box = np.zeros((ofw,ofw))

#     for i in range(marker_size[0]):     # rows
#         for j in range(marker_size[1]): # cols
#             r = i*(ofr)
#             c = j*(ofc)
#             x = i*marker_size[1]+j
#             tag = tags[x].array
#             b[r:r+tag_size,c:c+tag_size] = 255*tag

#     # border
#     r,c = b.shape
#     mm = 255*np.ones((r+ofw, c+ofw), dtype=np.uint8)
#     mm[ofw:,ofw:] = 255*b


#     for i in range(marker_size[0]+1):     # rows
#         for j in range(marker_size[1]+1): # cols
#             r = i*(ofr)
#             c = j*(ofc)
#             mm[r:r+ofw,c:c+ofw] = box

#     # mm = 255*flip(mm)
#     # mm = 255*mm

#     # scale image
#     xx = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)

#     return xx.astype(np.uint8)

#!/usr/bin/env python3
import numpy as np
from dataclasses import dataclass
from moms_apriltag import apriltags_v2, apriltags_v3
from opencv_camera import ApriltagMarker
# from moms_apriltag import TagGenerator2, TagGenerator3
from collections import namedtuple
from matplotlib import pyplot as plt
import cv2
from opencv_camera.color_space import bgr2gray, gray2bgr


Tag = namedtuple("Tag", "family id array")
Tag2 = namedtuple("Tag","tag_id corners") #FIXME: why 2???

tag_sizes = {
    "tag16h5": 6,
    "tag25h9": 7,
    "tag36h10": 8,
    "tag36h11": 8,
}

@dataclass
class ApriltagBoard:
    # markerSize:int
    squareSize:int
    boardSize:tuple
    scale:int
    family:str

    ids:list = None
    objPoints:list = None
    generator = None
    # rightBottomCorner:
    __target: np.ndarray = None

    def gen(self):
        r,c = self.boardSize
        self.ids = list(range(r*c))

        family = self.family
        if family in apriltags_v2:
            from moms_apriltag.generator2 import TagGenerator2 as TagGenerator
        elif family in apriltags_v3:
            from moms_apriltag.generator3 import TagGenerator3 as TagGenerator
        else:
            raise Exception(f"*** Invalid family: {family} ***")

        tg = TagGenerator(family)
        tags = [Tag(family, n, tg.generate(n)) for n in self.ids]

        ofw = self.squareSize

        # FIXME
        if family == "tag36h10":
            # check_size(r, len(tag36h10.codes))
            tag_size = 8
        elif family == "tag36h11":
            # check_size(r, len(tag36h11.codes))
            tag_size = 8
        elif family == "tag25h9":
            # check_size(r, len(tag25h9.codes))
            tag_size = 7
        elif family == "tag16h5":
            # check_size(r, len(tag16h5.codes))
            tag_size = 6
        else:
            raise Exception(f"Invalid tag family: {family}")
        #---------------------------

        ofr = tag_size+ofw
        ofc = tag_size+ofw
        marker_size = self.boardSize

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
        scale = self.scale
        if scale > 1:
            self.__target = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)
        else:
            self.__target = mm

    @classmethod
    def create(cls, squaresX, squaresY, family, scale=1, squareSize=2):
        board = cls(squareSize, (squaresX, squaresY), scale, family)
        board.gen()
        return board

    def imagePoints(self):
        """
        Returns a set of the target's ideal 3D feature points.
        sz: size of board, ex: (6,9)
        ofw: offset width, ex: 2px
        """
        ofw = self.squareSize
        # family = self.detector.params["families"][0]
        pix = tag_sizes[self.family]
        sz = self.boardSize
        scale = self.scale #/8
        ofr = pix+ofw
        ofc = pix+ofw
        r = sz[0]*(ofr)
        c = sz[1]*(ofc)
        # b = np.ones((r,c))
        objpts = {}
        tags = []

        for i in range(sz[0]):     # rows
            for j in range(sz[1]): # cols
                r = i*(ofr)+ofw
                c = j*(ofc)+ofw
                x = i*sz[1]+j

                rr = r+pix
                cc = c+pix
                corners = (
                    (scale*rr,scale*c,0),
                    (scale*rr,scale*cc,0),
                    (scale*r,scale*cc,0),
                    (scale*r,scale*c,0)) # ccw - best


                corners2d = (
                    (rr,c),
                    (rr,cc),
                    (r,cc),
                    (r,c)) # ccw - best

                corners2d = scale*np.array(corners2d)

                # objpts[x] = corners

                tags.append(Tag2(x, corners2d))
        # return objpts
        return tags

    # @property
    def draw(self):
        return self.__target



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
        cv2.putText(color_img, str(tag_id),
                    org=(v[0][0]+offset,v[0][1]-offset,),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=fs,
                    thickness=2*fs,
                    color=(255, 0, 255))

    return color_img


board = ApriltagBoard.create(4,4,"tag36h11",scale=50,squareSize=1)
# print(board.draw)
tgt = board.draw()
print("target shape:", tgt.shape)
tags = board.imagePoints()
print(len(tags))
# tm = ApriltagMarker()
# tgt = tm.draw(tgt, tags, id=True, mark=True)

tgt = gray2bgr(tgt)

for tag in tags:
    draw_tag(tgt, tag.corners,mark=True)


# plt.imshow(tgt, cmap="gray")
plt.imshow(tgt)
plt.title(f"{board.family} {board.boardSize}")
# plt.axis("off")
plt.show()
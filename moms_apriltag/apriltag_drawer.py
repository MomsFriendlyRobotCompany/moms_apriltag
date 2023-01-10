##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
from .color_space import bgr2gray, gray2bgr
import numpy as np
import cv2
from collections import namedtuple

Tag = namedtuple("Tag","id corners")


class ApriltagDrawer:
    def draw(self, img, ids, corners, mark=False):
        """
        Given a list of Tags (create with tagArray), this will draw
        the markers on an image.

        Return: color image with tags drawn on it
        """
        if len(img.shape) == 2:
            color_img = gray2bgr(img)
        else:
            color_img = img.copy()

        tags = []
        for ident, corner in zip(ids.flatten(), corners):
            tags.append(Tag(ident, corner[0]))

        if not isinstance(tags, list):
            tags = [tags]

        for tag in tags:
            # num = tag.tag_id if id else None
            color_img = self.__draw_tag(color_img, tag.corners, mark=mark)

        return color_img

    def __draw_tag(self, color_img, corners, mark=False):
        """
        color_img: image to draw on, must be color
        corners: corner points from apriltag detector, v[0] is the
                 lower left of the tag and the point move CCW.
        tag_id [int]: write tag id number
        mark [bool]: draw a circle in the middle of the tag to see detection easier
        """
        v = corners.astype('int32')
        pts = corners.reshape((-1,1,2)).astype('int32')

        # base thickness off of image size, not tag size!!
        thick = int(color_img.shape[1]/100)
        cv2.polylines(color_img,[pts],True,(0,255,0),thickness=thick)

        if mark:
            center = (
                v[0][0]+abs(v[2][0]-v[0][0])//2,
                v[0][1]-abs(v[2][1]-v[0][1])//2
            )
            radius = abs(v[0][0] - v[1][0])//2//2
            cv2.circle(color_img,center, radius, (200,0,255), -1)

        color = (255,0,0)  # color
        ocolor = (0,0,255) # other color
        radius = thick
        cv2.circle(color_img, tuple(v[0]),radius,ocolor,thickness=-1)
        # cv2.circle(color_img, tuple(v[1]),r,c,thickness=-1)
        cv2.circle(color_img, tuple(v[2]),radius,color,thickness=-1)
        # cv2.circle(color_img, tuple(v[3]),r,c,thickness=-1)

        # if tag_id is not None:
        #     offset = (v[1][0]-v[0][0])//4
        #     fs = r//3
        #     cv2.putText(color_img, str(tag_id),
        #                 org=(v[0][0]+offset,v[0][1]-offset,),
        #                 fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        #                 fontScale=fs,
        #                 thickness=2*fs,
        #                 color=(255, 0, 255))

        return color_img

    # @staticmethod
    # def tagArray(ids, corners):
    #     """
    #     value?
    #     """
    #     if len(ids) != len(corners):
    #         return None

    #     tags = []
    #     for ident, corner in zip(ids.flatten(), corners):
    #         tags.append(Tag(ident, corner[0]))

    #     return tags

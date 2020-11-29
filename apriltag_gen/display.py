# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
# import cv2
# import numpy as np
#
#
# def draw_ids(img, tags):
#     """
#     Draws the tag IDs on the found tags
#
#     img: single color image
#     tags: array of tags found in image
#     """
#     if len(img.shape) == 2:
#         color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#     else:
#         color_img = img.copy()
#
#     for tag in tags:
#         color_img = draw_tag(color_img, tag.corners, tag.tag_id)
#     return color_img


# def tip_sheet(imgs, width=5):
#     """
#     Creates a single image (tip sheet) with thumb nails of
#     the input images.
#
#     imgs: array of grayscale images
#     width: number of thumbnail images across the tip sheet
#            will be"""
#     tip = None
#     num = len(imgs)
#     r,c = imgs[0].shape[:2]
#     wid = width
#     rr = int(np.floor(r/wid))
#     cc = int(c*rr/r)
#     row = None
#
#     for i in range(num):
#         im = cv2.resize(imgs[i],(cc,rr,),interpolation=cv2.INTER_NEAREST)
#
#         if i == 0:
#             row = im.copy()
#         elif i == (num-1):
#             blk = np.zeros((row.shape[0], tip.shape[1]))
#             blk[:row.shape[0],:row.shape[1]] = row
#             row = blk
#             tip = np.vstack((tip, row))
#         elif i%wid == 0:
#             if tip is None:
#                 tip = row.copy()
#             else:
#                 tip = np.vstack((tip, row))
#             row = im.copy()
#         else:
#             row = np.hstack((row, im))
#
#     return tip

# def draw_tag(color_img, corners, tag_id=None):
#     """
#     color_img: image to draw on, must be color
#     corners: corner points from apriltag detector, v[0] is the
#              lower left of the tag and the point move CCW.
#     """
#     pts = corners.reshape((-1,1,2)).astype('int32')
#     cv2.polylines(color_img,[pts],True,(0,255,0),thickness=4)
#
#     # r = 15
#     y = color_img.shape[0]
#     r = max(int(y/200),1)
#     c = (255,0,0)
#     oc = (0,0,255)
#     v = corners.astype('int32')
#     cv2.circle(color_img, tuple(v[0]),r,oc,thickness=-1)
#     cv2.circle(color_img, tuple(v[1]),r,c,thickness=-1)
#     cv2.circle(color_img, tuple(v[2]),r,c,thickness=-1)
#     cv2.circle(color_img, tuple(v[3]),r,c,thickness=-1)
#
#     if tag_id is not None:
#         offset = int((v[1][0]-v[0][0])/4)
#         cv2.putText(color_img, str(tag_id),
#                     org=(v[0][0]+offset,v[0][1]-offset,),
#                     fontFace=cv2.FONT_HERSHEY_SIMPLEX,
#                     fontScale=1,
#                     thickness=4,
#                     color=(255, 0, 255))
#
#     return color_img
#
#
# def draw_imgpts(img, tags):
#     if len(img.shape) == 2:
#         color_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#     else:
#         color_img = img.copy()
#
#     for t in tags:
#             color_img = draw_tag(color_img, t.corners)
#
#     return color_img
#
#
# def coverage(self, size, imgpoints):
#     """
#     size: a tuple of (rows, columns)
#     imgpoints: points found on an image (from tag.corners)
#     """
#     y,x = size #imgs[0].shape[:2]
#     tgt = np.zeros((y,x,3),dtype=np.uint8)
#
#     rad = 5*max(int(y/1000),1)
#     c = (0,0,255)
#     for f in imgpoints:
#         for x in f:
#             cv2.circle(tgt, tuple(x.astype('int32')),rad,c,thickness=-1)
#
#     return tgt

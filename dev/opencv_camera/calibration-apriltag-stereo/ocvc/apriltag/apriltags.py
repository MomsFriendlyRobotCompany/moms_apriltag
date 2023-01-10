##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
# import cv2
# from opencv_camera.color_space import bgr2gray, gray2bgr
# import numpy as np
# from colorama import Fore
# import cv2.aruco as aruco

# from .apriltag_marker import Tag
# from .apriltag_marker import ApriltagMarker

# # pixel size of marker on one side
# # 16h5 is 6x6 px
# tag_sizes = {
#     cv2.aruco.DICT_APRILTAG_16H5: 6,
#     cv2.aruco.DICT_APRILTAG_25H9: 7,
#     cv2.aruco.DICT_APRILTAG_36H10: 8,
#     cv2.aruco.DICT_APRILTAG_36H11: 8,
# }


# class ApriltagTargetFinder:
#     def __init__(self, size, scale, family):
#         """
#         Uses the built-in apriltag finder in OpenCV contrib library to find
#         apriltags.

#         size: pattern of chess board, tuple(rows, columns)
#         scale: real-world dimension of square side, example, 2 cm (0.02 m)
#         family: example, cv2.aruco.DICT_APRILTAG_16H5
#         """
#         # self.detector = detector
#         self.marker_size = size
#         self.marker_scale = scale
#         self.type = "Apriltag"
#         self.family = family
#         self.bitsPerPixel = 5
#         self.markerSizePx = 8 # 36h10
#         self.has_ids = True

#         self.generatePoints()

#     # def aruco2opencv(corners):
#     #     """
#     #     Takes corners found from cv2.aruco.detectMarkers() which is a list
#     #     of markers size (1,4,2) each and returns
#     #     a numpy array of (4*markers,1,2) where each marker has 4 corners
#     #     and if there are 6 markers in the image, then the first number
#     #     is 4*6 = 24 or (24,1,2). This is what is passed to cv2.cornerSubPix
#     #     or cv2.calibrateCamera() / cv2.calibrateStereo()
#     #     """
#     #     c = [x.reshape((4,1,2)) for x in corners]
#     #     c = np.vstack(c)
#     #     return c

#     def find(self, gray, flags=None):
#         """
#         Given an image, this will return tag corners. The input flags are not
#         used.

#         return:
#             success: (True, [corner points],[object points])
#             failure: (False, None, None)
#         """
#         if len(gray[0].shape) > 2:
#             raise Exception(f"Images must be grayscale, not shape: {gray[0].shape}")

#         # additionally, I do a binary thresholding which greatly reduces
#         # the apriltag's bad corner finding which resulted in non-square
#         # tags which gave horrible calibration results.
#         # ok, gray = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
#         # if not ok:
#         #     return False, None, None

#         # use cv2.aruco to find tags
#         # corners: tuple of numpy array (1,4,2), length N ... why?
#         # ids: numpy array shape (N,1)
#         corners, ids, rejectedImgPts = aruco.detectMarkers(
#             gray,
#             aruco.Dictionary_get(self.family),
#             parameters=aruco.DetectorParameters_create(),
#         )
#         if corners is None or ids is None:
#             return False, None, None
#         elif len(corners) == 0:
#             return False, None, None

#         ids = ids.ravel() # flatten in an array

#         corners = [c.reshape(-1,2) for c in corners] # make (4,2)
#         # print("apriltagfinder corners",np.array(corners).shape)

#         # get complete listing of objpoints in a target
#         opdict = self.objectPoints

#         ob = []
#         tt = []
#         # for each tag, get corners and obj point corners:
#         # for tag in tags:
#         for tag_id, corner in zip(ids, corners):
#             # add found objpoint to list IF tag id found in image
#             try:
#                 obcorners = opdict[tag_id]
#             except KeyError as e:
#                 print(f"*** {e} ***")
#                 continue

#             for oc in obcorners:
#                 ob.append(oc)
#             for c in corner:
#                 tt.append([c])

#         corners = np.array(tt, dtype=np.float32)
#         objpts = np.array(ob, dtype=np.float32)

#         return True, corners, objpts, ids

#     def generatePoints(self):
#         """
#         Returns a set of the target's ideal 3D feature points.

#         aruco pt order:
#         3     4
#         +-----+
#         |     |
#         |     |
#         +-----+
#         2     1

#         pupil labs pt order:
#         4     3
#         +-----+
#         |     |
#         |     |
#         +-----+
#         1     2

#         sz: size of board, ex: (6,9)
#         ofw: offset width, ex: 2px
#         """
#         ofw = 2 #self.squareSize
#         pix = tag_sizes[self.family]
#         sz = (4,5) #self.boardSize
#         scale = self.marker_scale #/8
#         ofr = pix+ofw
#         ofc = pix+ofw
#         r = sz[0]*(ofr)
#         c = sz[1]*(ofc)

#         objpts = {}
#         imgpts = {}

#         # print("pix", pix)
#         pxscale = scale / pix

#         for i in range(sz[0]):     # rows
#             for j in range(sz[1]): # cols
#                 r = i*(ofr)+ofw
#                 c = j*(ofc)+ofw
#                 x = i*sz[1]+j

#                 rr = r+pix
#                 cc = c+pix

#                 # corners2d = (
#                 #     (r,c),
#                 #     (rr,c),
#                 #     (rr,cc),
#                 #     (r,cc))
#                 corners2d = (
#                     (rr,cc),
#                     (r,cc),
#                     (r,c),
#                     (rr,c))

#                 imgpts[x] = np.array(corners2d, dtype=int)

#                 # corners3d = (
#                 #     (r,c,0),
#                 #     (rr,c,0),
#                 #     (rr,cc,0),
#                 #     (r,cc,0))
#                 corners3d = (
#                     (rr,cc,0),
#                     (r,cc,0),
#                     (r,c,0),
#                     (rr,c,0))

#                 corners3d = pxscale * np.array(corners3d)

#                 objpts[x] = corners3d

#         self.imgpts = imgpts
#         self.objpts = objpts

#     @property
#     def objectPoints(self):
#         return self.objpts

#     @property
#     def imagePoints(self):
#         return self.imgpts

#     def draw(self, img, tags):
#         """
#         Draws corners on an image for viewing/debugging
#         """
#         if len(img.shape) == 2:
#             color = gray2bgr(img) #cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#         else:
#             color = img.copy()

#         tm = ApriltagMarker()
#         return tm.draw(color, tags)

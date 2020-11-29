# # -*- coding: utf-8 -*
# ##############################################
# # The MIT License (MIT)
# # Copyright (c) 2020 Kevin Walchko
# # see LICENSE for full details
# ##############################################
# import numpy as np
# import time
# import cv2
#
#
# class ApriltagCameraCalibrator:
#     def __init__(self, detector):
#         self.detector = detector
#
#     def find_markers(self, images):
#         tags = []
#         num = 0
#         if len(images[0].shape) > 2:
#             raise Exception(f"Images must be grayscale, not shape: {images[0].shape}")
#
#         for img in images:
#             t = self.detector.detect(
#                 img,
#                 estimate_tag_pose=False,
#                 camera_params=None,
#                 tag_size=0.0235)
#
#             tags.append(t)
#             num += len(t)
#
#         print(f">> Found {num} points across {len(tags)} images")
#         return tags
#
#     def calibrate(self, images, marker_size, tag_size):
#         """
#         images: array of graysccale images
#         marker_size: tuple size, ex: (6,9)
#         tag_size: size of tag in meters, ex: 0.0235 (or 23.5mm)"""
#         tags = self.find_markers(images)
#
#         objpts = self.obj_points(marker_size)
#
#         # list of tags found by detector for each image
#         img_ids = [[t.tag_id for t in f] for f in tags]
#
#         # list of searchable tag coordinates found by detector for each image
#         stags = [{t.tag_id: t.corners for t in tag} for tag in tags]
#
#         # points found in image from detector
#         imgpoints = []
#
#         # point locations on an ideal target array
#         objpoints = []
#
#         for stag,ids in zip(stags, img_ids):
#             op = [] # objpoints
#             ip = [] # imgpoints
#
#             # putting the ids in order
#             ids.sort()
#             #s=0.0235/8 # fixme
#             s=tag_size/8 # fixme
#             for id in ids:
#                 for x in objpts[id]:
#                     op.append((s*x[0],s*x[1], 0,))
#
#                 for x in stag[id]:
#                     ip.append(x)
#
#             x = np.array(ip, dtype=np.float32)
#             imgpoints.append(x)
#
#             x = np.array(op, dtype=np.float32)
#             objpoints.append(x)
#
#         h,w = imgs[0].shape[:2]
#         K = None
#         rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
#             objpoints, imgpoints, (w, h), K, None)
#
#         print(f"RMS error: {rms}")
#         print(f"distortion coefficients: {dist}")
#         print(f"camera matrix:\n{mtx}")
#
#         data = {
#             'date': time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
# #             'markerType': self.marker_type,
#             'markerSize': marker_size,
#             'imageSize': images[0].shape,
#             'cameraMatrix': mtx,
#             'distCoeffs': DistortionCoefficients(*dist[0]),
#             'rms': rms,
#             'rvecs': rvecs,
#             'tvecs': tvecs,
#             'imgpoints': imgpoints,
#             'objpoints': objpoints
#         }
#         return data
#
#     def obj_points(self, sz, ofw=2):
#         ofr = 8+ofw
#         ofc = 8+ofw
#         r = sz[0]*(ofr)
#         c = sz[1]*(ofc)
#         b = np.ones((r,c))
#         objpts = {}
#
#         for i in range(sz[0]):     # rows
#             for j in range(sz[1]): # cols
#                 r = i*(ofr)+ofw
#                 c = j*(ofc)+ofw
#                 x = i*sz[1]+j
#
#                 rr = r+8
#                 cc = c+8
#                 objpts[x] = ((rr,c),(rr,cc),(r,cc),(r,c)) # ccw - best
#         return objpts
#
#     # def coverage(self, size, imgpoints):
#     #     y,x = size #imgs[0].shape[:2]
#     #     tgt = np.zeros((y,x,3),dtype=np.uint8)
#     #
#     #     rad = 5*max(int(y/1000),1)
#     #     c = (0,0,255)
#     #     for f in imgpoints:
#     #         for x in f:
#     #             cv2.circle(tgt, tuple(x.astype(int)),rad,c,thickness=-1)
#     #
#     #     return tgt
#     #
#     # def board(self, marker_size, scale=10, ofw=2):
#     #     r = marker_size[0]*marker_size[1]
#     #     family = self.detector.params["families"][0]
#     #     tags = apt.generate(family, range(r))
#     #
#     #     ofr = 8+ofw
#     #     ofc = 8+ofw
#     #     r = marker_size[0]*(ofr)
#     #     c = marker_size[1]*(ofc)
#     #     b = np.ones((r,c))
#     #
#     #     for i in range(marker_size[0]):     # rows
#     #         for j in range(marker_size[1]): # cols
#     #             r = i*(ofr)
#     #             c = j*(ofc)
#     #             x = i*marker_size[1]+j
#     #             tag = tags[x].array
#     #             b[r:r+8,c:c+8] = tag
#     #
#     #     # border
#     #     r,c = b.shape
#     #     mm = np.ones((r+ofw, c+ofw), dtype=np.uint8)
#     #     mm[ofw:,ofw:] = b
#     #     mm = 255*mm
#     #
#     #     # scale image
#     #     xx = np.repeat(np.repeat(mm, scale, axis=0), scale, axis=1)
#     #
#     #     return xx

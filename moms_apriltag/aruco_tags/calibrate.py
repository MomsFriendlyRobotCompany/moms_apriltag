# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
import numpy as np
# np.set_printoptions(precision=3)
# np.set_printoptions(suppress=True)
import cv2
import time # save date in results
from ..color_space import bgr2gray, gray2bgr
from collections import OrderedDict # need?

# def tagsorted(tags):
#     def func(x):
#             return x.id

#     # ensure ids are ordered from low to high
#     return sorted(tags, key=func)

class ApriltagCameraCalibration:
    '''
    Simple calibration class.
    '''

    def findPoints(self, images, board):
        """
        images: array of M numpy images
        board: target board

        Return
            M: number of images
            N: number of tags found
            tagids: list of list of ids, (M,N)
            objpoints: list of list of 3D corner points, (M,N*4,3)
            imgpoints: list of list of 2D corner points, (M,N*4,2)
        """

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
        # bad_images = [] # keep track of what images failed
        tagids = []

        # max_corners = board.marker_size[0]*board.marker_size[1]
        max_corners = np.multiply(*board.boardSize)

        for cnt, gray in enumerate(images):
            if len(gray.shape) > 2:
                gray = bgr2gray(gray)

            ok, corners, objp, ids = board.find(gray)
            if not ok:
                # bad_images.append(cnt)
                continue

            # print("board.find",ok, type(corners), len(corners), corners[0].shape, type(objp),len(objp), objp[0].shape)

            objpoints.append(objp)
            tagids.append(ids)

            term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), term)
            imgpoints.append(corners.reshape(-1, 2))

        # M: number of images
        # N: number of tags found
        # tagids: list of list of ids, (M,N)
        # imgpoints: list of list of 2D corner points, (M,N*4,2)
        # objpoints: list of list of 3D corner points, (M,N*4,3)
        return tagids, imgpoints, objpoints

    def calibrate(self, images, board, flags=None):
        """
        images: an array of grayscale images, all assumed to be the same size.
            If images are not grayscale, then assumed to be in BGR format.
        board: an object that represents your target, i.e., Chessboard
        marker_scale: how big are your markers in the real world, example:
            checkerboard with sides 2 cm, set marker_scale=0.02 so your T matrix
            comes out in meters
        """
        ids, imgpoints, objpoints = self.findPoints(images, board)

        # images size here is backwards: w,h
        h, w = images[0].shape[:2]

        # initial guess for camera matrix
        # K = None # FIXME
        f = 0.8*w
        cx, cy = w//2, h//2
        K = np.array([
            [ f,  0, cx],
            [ 0,  f, cy],
            [ 0,  0,  1]
        ])

        # not sure how much these really help
        if flags is None:
            flags = 0
            # flags |= cv2.CALIB_THIN_PRISM_MODEL
            # flags |= cv2.CALIB_TILTED_MODEL
            # flags |= cv2.CALIB_RATIONAL_MODEL

        rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, (w, h), K, None)

        tags = []
        for id, ipts, opts in zip(ids, imgpoints, objpoints):
            # group the 4 corners of each marker together with
            # its respective tagID
            ipts = np.array(ipts)
            opts = np.array(opts)
            ipts = ipts.reshape((-1,4,2)) # 4 x 2d
            opts = opts.reshape((-1,4,3)) # 4 x 3d

            img_tags = OrderedDict() # need ordered?

            for i,im, ob in zip(id,ipts,opts):
                img_tags[i] = (im,ob,)
            tags.append(img_tags)

        # tags = tagsorted(tags)

        data = {
            'date': time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
            'markerFamily': board.family,
            'boardSize': board.boardSize,
            'K': K,
            'd': dist,
            'rms': rms,
            'rvecs': rvecs,
            'tvecs': tvecs,
            "tags": tags,
            "height": images[0].shape[0],
            "width": images[0].shape[1]
        }

        # print(tags[0]))
        # for k,v in tags[0].items():
        #     print("-------")
        #     print(v[0])
        #     print(v[1])

        return data



class ApriltagStereoCalibration:
    save_cal_imgs = None

    # def aruco2opencv(corners):
    #     """
    #     Takes corners found from cv2.aruco.detectMarkers() which is a list
    #     of markers size (1,4,2) each and returns
    #     a numpy array of (4*markers,1,2) where each marker has 4 corners
    #     and if there are 6 markers in the image, then the first number
    #     is 4*6 = 24 or (24,1,2). This is what is passed to cv2.cornerSubPix
    #     or cv2.calibrateCamera() / cv2.calibrateStereo()
    #     """
    #     c = [x.reshape((4,1,2)) for x in corners]
    #     c = np.vstack(c)
    #     return c

    def calibrate(self, imgs_l, imgs_r, board, flags=None):
        """
        This will save the found markers for camera_2 (right) only in
        self.save_cal_imgs array
        """
        # so we know a little bit about the camera, so
        # start off the algorithm with a simple guess
        # h,w = imgs_l[0].shape[:2]
        # f = max(h,w)*0.8  # focal length is a function of image size in pixels
        # K = np.array([
        #     [f,0,w//2],
        #     [0,f,h//2],
        #     [0,0,1]
        # ])

        cc = ApriltagCameraCalibration()

        data = cc.calibrate(imgs_l, board)
        K1 = data["K"]
        d1 = data["d"]
        rvecs1 = data["rvecs"]
        tvecs1 = data["tvecs"]
        tagsL = data["tags"]

        data = cc.calibrate(imgs_r, board)
        K2 = data["K"]
        d2 = data["d"]
        rvecs2 = data["rvecs"]
        tvecs2 = data["tvecs"]
        tagsR = data["tags"]

        # objpoints,imgpoints_r,imgpoints_l = self.match2(objpts, idsL, imgptsL, idsR, imgptsR)
        objpoints = []
        imgpoints_l = []
        imgpoints_r = []


        for imgtagsL, imgtagsR in zip(tagsL, tagsR):
            # print(imgtagsL)
            # print("-"*40)
            # for k,v in imgtagsL.items():
            #     print(f"ID: {k}:")
            #     print(f"  imgpts: {v[0]}")
            #     print(f"  objpts: {v[1]}")

            obj = []
            ipts_l = []
            ipts_r = []
            for k,v in imgtagsL.items():
                try:
                    vright = imgtagsR[k]
                except KeyError:
                    continue
                obj.append(v[1]) # reshape?
                ipts_l.append(v[0])
                ipts_r.append(vright[0])

            if len(obj) > 0:
                objpoints.append(np.vstack(obj).reshape((-1,1,3)))
                imgpoints_l.append(np.vstack(ipts_l).reshape((-1,1,2)))
                imgpoints_r.append(np.vstack(ipts_r).reshape((-1,1,2)))

        # for o in objpoints:
        #     print(o.shape)
        #     # print(o)
        #     # print("-------")

        # print("objpoints",type(objpoints),len(objpoints),objpoints[0].shape)
        # print("imgpoints_l",type(imgpoints_l),len(imgpoints_l),imgpoints_l[0].shape)
        # print("imgpoints_r",type(imgpoints_r),len(imgpoints_r),imgpoints_r[0].shape)

        # cv2.utils.dumpInputArrayOfArrays(objpoints)
        # cv2.utils.dumpInputArrayOfArrays(imgpoints_l)
        # cv2.utils.dumpInputArrayOfArrays(imgpoints_r)

        """
        CALIB_ZERO_DISPARITY: horizontal shift, cx1 == cx2
        """
        if flags is None:
            flags = 0
            # flags |= cv2.CALIB_FIX_INTRINSIC
            flags |= cv2.CALIB_ZERO_DISPARITY
            # flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
            flags |= cv2.CALIB_USE_INTRINSIC_GUESS
            # flags |= cv2.CALIB_FIX_FOCAL_LENGTH
            # flags |= cv2.CALIB_FIX_ASPECT_RATIO
            # flags |= cv2.CALIB_ZERO_TANGENT_DIST
            # flags |= cv2.CALIB_RATIONAL_MODEL
            # flags |= cv2.CALIB_SAME_FOCAL_LENGTH
            # flags |= cv2.CALIB_FIX_K3
            # flags |= cv2.CALIB_FIX_K4
            # flags |= cv2.CALIB_FIX_K5
            # flags |= cv2.CALIB_USE_EXTRINSIC_GUESS

        stereocalib_criteria = (
            cv2.TERM_CRITERIA_MAX_ITER +
            cv2.TERM_CRITERIA_EPS,
            100,
            1e-5)

        h,w = imgs_l[0].shape[:2]

        ret, K1, d1, K2, d2, R, T, E, F = cv2.stereoCalibrate(
            objpoints,
            imgpoints_l,
            imgpoints_r,
            K1, d1,
            K2, d2,
            (w,h),
            # (h,w),
            # R=self.R,
            # T=self.t,
            # R=np.eye(3,3),
            # T=np.array([[0.031],[0],[0]]), # FIXME
            criteria=stereocalib_criteria,
            flags=flags)

        if ret is False:
            return ret, None

        camera_model = {
            'date': time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
            'markerFamily': board.family,
            'boardSize': board.boardSize,
            'height': imgs_l[0].shape[0],
            'width': imgs_l[0].shape[1],
            'K1': K1, # camera matrix
            'K2': K2,
            'd1': d1, # distortion coefficients
            'd2': d2,
            'rvecsL': rvecs1, # rotations
            "tvecsL": tvecs1, # translations
            'rvecsR': rvecs2,
            "tvecsR": tvecs2,
            'R': R, # rotation between left/right camera
            'T': T, # translation between left/right camera
            'E': E, # essential matrix
            'F': F, # functional matrix
            "objpoints": objpoints, # 3d corners on the target board
            "imgpointsL": imgpoints_l, # 2d image points detected from the image
            "imgpointsR": imgpoints_r,
        }

        return ret, camera_model

















    # def match(self,objpts, idsL, imgptsL, idsR, imgptsR):
    #     """
    #     idsL: list(np.array(N, ids))
    #     imgptsL: list(np.array(N, 2d points))
    #     """

    #     objpoints = []
    #     imgpoints_r = []
    #     imgpoints_l = []

    #     # trying to be efficient in the serach instead of using
    #     # find() on the list
    #     # print("Removing markers not seen in both frames:")
    #     totalMarkers = 0
    #     for img_num, (ob, idL, ipL, idR, ipR) in enumerate(zip(objpts, idsL, imgptsL, idsR, imgptsR)):
    #         reject = 0
    #         leftInfo = dict(zip(idL,tuple(zip(ipL, ob))))
    #         rightInfo = dict(zip(idR, ipR))
    #         top = []
    #         timl = []
    #         timr = []

    #         print("ob idL imgL",ob.shape,idL.shape,ipL.shape)

    #         # for each id found in left camera, see if the marker id
    #         # was found in the right camera. If yes, save, if no,
    #         # reject the marker
    #         for id,(ipt,opt) in leftInfo.items():
    #             print("id,ipt,opt",id,ipt, opt)
    #             try:
    #                 iptr = rightInfo[id]
    #                 top.append(opt)
    #                 timl.append(ipt)
    #                 timr.append(iptr)
    #             except KeyError:
    #                 # id not found in right camera
    #                 reject += 1
    #                 continue
    #         objpoints.append(np.array(top))
    #         imgpoints_l.append(np.array(timl))
    #         imgpoints_r.append(np.array(timr))
    #         # if reject > 0:
    #         #     total = max(len(idL), len(idR))
    #         #     print(f"  Image {img_num}: rejected {reject} tags of {total} tags")

    #         totalMarkers += len(top)

    #     print(f"Total markers found in BOTH cameras: {totalMarkers}")

    #     return objpoints,imgpoints_r,imgpoints_l


    # def match2(self,objpts, idsL, imgptsL, idsR, imgptsR):
    #     """
    #     M: images
    #     N: found markers
    #     all lists are length M

    #     idsL/R:    list(np.array(N*4, 1))
    #     imgptsL/R: list(np.array(N*4, 2))
    #     objpts:    list(np.array(N*4, 3))
    #     """

    #     objpoints = []
    #     imgpoints_r = []
    #     imgpoints_l = []

    #     # set(a).intersection(b)

    #     # trying to be efficient in the serach instead of using
    #     # find() on the list
    #     # print("Removing markers not seen in both frames:")
    #     totalMarkers = 0
    #     for img_num, (ob, idL, ipL, idR, ipR) in enumerate(zip(objpts, idsL, imgptsL, idsR, imgptsR)):
    #         reject = 0
    #         top = []
    #         timl = []
    #         timr = []

    #         # group the 4 corners of each marker together with
    #         # its respective tagID
    #         ipL = ipL.reshape((-1,4,2)) # 4 x 2d
    #         ipR = ipR.reshape((-1,4,2)) # 4 x 2d
    #         ob = ob.reshape((-1,4,3))   # 4 x 3d

    #         leftInfo = dict(zip(idL,zip(ipL,ob)))
    #         rightInfo = dict(zip(idR, ipR))

    #         # for each id found in left camera, see if the marker id
    #         # was found in the right camera. If yes, save, if no,
    #         # reject the marker
    #         for id,(ipt,opt) in leftInfo.items():
    #             # print("id,ipt,opt",id,ipt, opt)
    #             try:
    #                 iptr = rightInfo[id]
    #                 for i in range(4):
    #                     top.append(opt[i])
    #                     timl.append(ipt[i])
    #                     timr.append(iptr[i])
    #             except KeyError:
    #                 # id not found in right camera
    #                 reject += 1
    #                 continue
    #         objpoints.append(np.array(top))
    #         imgpoints_l.append(np.array(timl))
    #         imgpoints_r.append(np.array(timr))
    #         # if reject > 0:
    #         #     total = max(len(idL), len(idR))
    #         #     print(f"  Image {img_num}: rejected {reject} tags of {total} tags")

    #         totalMarkers += len(top)

    #     print(f"Total markers found in BOTH cameras: {totalMarkers/4} marker or {totalMarkers} corners")

    #     return objpoints,imgpoints_r,imgpoints_l
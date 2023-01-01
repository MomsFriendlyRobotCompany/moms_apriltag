##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
import cv2
from opencv_camera.color_space import bgr2gray, gray2bgr
import numpy as np
# from ..apriltag.apriltag_marker import ApriltagMarker
from colorama import Fore
from moms_apriltag import apriltags_v2
from opencv_camera import bgr2gray, gray2bgr
from opencv_camera import CameraCalibration, Camera, StereoCamera
# import cv2.aruco as aruco

# cv2.aruco.DICT_APRILTAG_16H5 = 17
# cv2.aruco.DICT_APRILTAG_25h9 = 18
# cv2.aruco.DICT_APRILTAG_36H10 = 19
# cv2.aruco.DICT_APRILTAG_36H11 = 20

# pixel size of marker on one side
# 16h5 is 6x6 px
tag_sizes = {
    'tag16h5' : 6,
    'tag25h9' : 7,
    'tag36h10': 8,
    'tag36h11': 8,
}

# pixel size of marker on one side
# 16h5 is 6x6 px
# tag_sizes = {
#     cv2.aruco.DICT_APRILTAG_16H5: 6,
#     cv2.aruco.DICT_APRILTAG_25H9: 7,
#     cv2.aruco.DICT_APRILTAG_36H10: 8,
#     cv2.aruco.DICT_APRILTAG_36H11: 8,
# }


class ApriltagTargetFinder:
    def __init__(self, size, scale, detector):
        """
        Uses the pupil labs detector:

        detector = Detector(
            families="tag16h5",
            nthreads=1,
            quad_decimate=1.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0
        )

        size: pattern of chess board, tuple(rows, columns)
        scale: real-world dimension of square side, example, 2 cm (0.02 m)
        family: example, tag16h5
        detector: pupil labs detector, only gen 3 tags
        """
        if family not in apriltags_v2:
            raise ValueError(f"Invalid generation 2 apriltag: {family}")

        # self.detector = detector
        self.marker_size = size
        self.marker_scale = scale
        self.type = "Apriltag"
        self.family = family
        self.detector = detector

    def find(self, gray, flags=None):
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

        tags = self.detector.detect(
            gray,
            estimate_tag_pose=False,
            camera_params=None,
            tag_size=self.marker_scale)

        # corners, ids, rejectedImgPts = aruco.detectMarkers(
        #     gray,
        #     aruco.Dictionary_get(self.family),
        #     parameters=aruco.DetectorParameters_create(),
        # )
        # if corners is None or ids is None:
        #     return False, None, None

        # tags = ApriltagMarker.tagArray(ids, corners)

        if len(tags) == 0:
            return False, None, None
        #---
        # get complete listing of objpoints in a target
        opdict = self.objectPoints()

        invalid_id = False

        ob = []
        tt = []
        # for each tag, get corners and obj point corners:
        for tag in tags:
            # add found objpoint to list IF tag id found in image
            try:
                obcorners = opdict[tag.tag_id]
            except KeyError as e:
                # print(f"*** {e} ***")
                # invalid_id = True
                continue

            for oc in obcorners:
                ob.append(oc)
            cs = tag.corners
            for c in cs:
                tt.append(c)

        corners = np.array(tt, dtype=np.float32)
        objpts = np.array(ob, dtype=np.float32)
        # print("corners", corners.shape, corners.dtype)
        # print(corners)
        # if invalid_id:
        #     print(f"{Fore.RED}*** Invalid tag ID's found ***{Fore.RESET}")

        return True, corners, objpts

    def objectPoints(self, ofw=2):
        """
        Returns a set of the target's ideal 3D feature points.

        sz: size of board, ex: (6,9)
        ofw: offset width, ex: 2px
        """
        # family = self.detector.params["families"][0]
        pix = tag_sizes[self.family]
        sz = self.marker_size
        scale = self.marker_scale/8
        ofr = pix+ofw
        ofc = pix+ofw
        r = sz[0]*(ofr)
        c = sz[1]*(ofc)
        b = np.ones((r,c))
        objpts = {}

        for i in range(sz[0]):     # rows
            for j in range(sz[1]): # cols
                r = i*(ofr)+ofw
                c = j*(ofc)+ofw
                x = i*sz[1]+j

                rr = r+pix
                cc = c+pix
                objpts[x] = (
                    (scale*rr,scale*c,0),
                    (scale*rr,scale*cc,0),
                    (scale*r,scale*cc,0),
                    (scale*r,scale*c,0)) # ccw - best
        return objpts

    def draw(self, img, tags):
        """
        Draws corners on an image for viewing/debugging
        """
        if len(img.shape) == 2:
            color = gray2bgr(img) #cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            color = img.copy()

        tm = ApriltagMarker()
        return tm.draw(color, tags)




class StereoCalibration(object):
    save_cal_imgs = None

    # def __init__(self, R=None, t=None):
    #     """
    #     The frame from left to right camera is [R|t]
    #     """
    #     # self.camera_model = None
    #     self.save_cal_imgs = None

    #     # if R is None:
    #     #     R = np.eye(3) # no rotation between left/right camera
    #     # self.R = R
    #     #
    #     # if t is None:
    #     #     t = np.array([0.1,0,0]) # 100mm baseline
    #     #     t.reshape((3,1))
    #     # self.t = t

    # def save(self, filename, handler=pickle):
    #     if self.camera_model is None:
    #         print("no camera model to save")
    #         return
    #     with open(filename, 'wb') as f:
    #         handler.dump(self.camera_model, f)

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

        cc = CameraCalibration()
        # rms1, M1, d1, r1, t1, objpoints, imgpoints_l = cc.calibrate(imgs_l, board)
        # rms2, M2, d2, r2, t2, objpoints, imgpoints_r = cc.calibrate(imgs_r, board)

        cam, data = cc.calibrate(imgs_l, board)
        K1 = cam.K
        d1 = cam.d
        rvecs1 = data["rvecs"]
        tvecs1 = data["tvecs"]
        objpts = data["objpoints"]
        imgptsL = data["imgpoints"]

        # print(objpoints)

        # time.sleep(1)

        cam, data = cc.calibrate(imgs_r, board)
        K2 = cam.K
        d2 = cam.d
        rvecs2 = data["rvecs"]
        tvecs2 = data["tvecs"]
        imgptsR = data["imgpoints"]

        # print(d1,d2)

        # self.save_cal_imgs = cc.save_cal_imgs
        objpoints = []
        imgpoints_r = []
        imgpoints_l = []
        for o,l,r in zip(objpts,imgptsL,imgptsR):
            # must have all the same number of points for calibration
            if o.shape[0] == l.shape[0] == r.shape[0]:
                objpoints.append(o)
                imgpoints_r.append(r)
                imgpoints_l.append(l)
            else:
                print("bad points:", o.shape, l.shape, r.shape)

        print(f"Object Pts: {len(objpoints)}")
        print(f"Left Image Pts: {len(imgpoints_l)}")
        print(f"Right Image Pts: {len(imgpoints_r)}")

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
            criteria=stereocalib_criteria,
            flags=flags)

        # d1 = d1.T[0]
        # d2 = d2.T[0]

        # print('')
        camera_model = {
            'date': time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
            'markerType': board.type,
            'markerSize': board.marker_size,
            'imageSize': imgs_l[0].shape[:2],
            # 'cameraMatrix1': K1,
            # 'cameraMatrix2': K2,
            # 'distCoeffs1': d1,
            # 'distCoeffs2': d2,
            'rvecsL': rvecs1,
            "tvecsL": tvecs1,
            'rvecsR': rvecs2,
            "tvecsR": tvecs2,
            # 'R': R,
            # 'T': T,
            # 'E': E,
            # 'F': F,
            "objpoints": objpoints,
            "imgpointsL": imgpoints_l,
            "imgpointsR": imgpoints_r,
        }

        sc = StereoCamera(
            K1,d1,
            K2,d2,
            R,T,
            F,
            E
        )
        # sc.R = R
        # sc.E = E
        # sc.F = F
        # sc.T = T
        # sc.K1 = K1
        # sc.K2 = K2
        # sc.d1 = d1
        # sc.d2 = d2

        return ret, camera_model, sc

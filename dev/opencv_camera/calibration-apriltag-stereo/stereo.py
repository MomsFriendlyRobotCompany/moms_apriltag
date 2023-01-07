##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
import numpy as np
# np.set_printoptions(precision=3)
# np.set_printoptions(suppress=True)
import cv2
from colorama import Fore
# import time
# from collections import namedtuple
from ..undistort import DistortionCoefficients
from ..color_space import bgr2gray, gray2bgr
from ..mono.calibrate import CameraCalibration
from ..mono.camera import Camera
from .camera import StereoCamera



class CameraCalibration:
    '''
    Simple calibration class.
    '''

    def calibrate(self, images, board, flags=None):
        """
        images: an array of grayscale images, all assumed to be the same size.
            If images are not grayscale, then assumed to be in BGR format.
        board: an object that represents your target, i.e., Chessboard
        marker_scale: how big are your markers in the real world, example:
            checkerboard with sides 2 cm, set marker_scale=0.02 so your T matrix
            comes out in meters
        """
        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        max_corners = board.marker_size[0]*board.marker_size[1]
        # print(max_corners)

        bad_images = []
        # for cnt, gray in enumerate(tqdm(images)):
        for cnt, gray in enumerate(images):
            if len(gray.shape) > 2:
                gray = bgr2gray(gray)

            # ret, corners = self.findMarkers(gray)
            ok, corners, objp = board.find(gray)
            # if not ok:
            #     continue
            # print(len(corners))
            # print(corners)
            # raise Exception()
            # if len(corners) // 4 != max_corners:
            #     continue

            # If found, add object points, image points (after refining them)
            if ok:
                if len(corners) // 4 != max_corners:
                    bad_images.append(cnt)
                    continue
                # imgpoints.append(corners.reshape(-1, 2))

                # get the real-world pattern of points
                # objp = board.objectPoints()
                objpoints.append(objp)

                # print('[{}] + found {} of {} corners'.format(
                #     cnt, corners.size / 2, max_corners))
                term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.001)
                corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), term)
                imgpoints.append(corners.reshape(-1, 2))

                # Draw the corners
                # tmp = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                # cv2.drawChessboardCorners(tmp, board.marker_size, corners, True)
                # tmp = board.draw(gray, corners)
                # self.save_cal_imgs.append(tmp)
            else:
                bad_images.append(cnt)
                # print(f'{Fore.RED}*** Image[{cnt}] - Could not find markers ***{Fore.RESET}')

        if len(bad_images) > 0:
            print(f'{Fore.RED}>> Could not find markers in images: {bad_images}{Fore.RESET}')

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

        # rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        #     objpoints, imgpoints, (w, h), K, None, flags=flags)

        rms, mtx, dist, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors = cv2.calibrateCameraExtended(
            objpoints, imgpoints, (w, h), K, None)

        data = {
            'date': time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
            'markerType': board.type,
            'markerSize': board.marker_size,
            'imageSize': images[0].shape,
            'K': mtx,
            'd': dist, #DistortionCoefficients(dist),
            'rms': rms,
            'rvecs': rvecs,
            'tvecs': tvecs,
            "objpoints": objpoints,
            "imgpoints": imgpoints,
            "badImages": bad_images,
            "stdint": stdDeviationsIntrinsics,
            "stdext": stdDeviationsExtrinsics,
            "perViewErr": perViewErrors
        }

        cam = Camera(mtx, dist, images[0].shape[:2])

        print(f"{Fore.GREEN}>> RMS: {rms:0.3f}px{Fore.RESET}")
        print("\n",cam)

        return cam, data



class StereoCalibration(object):
    save_cal_imgs = None

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
        objpoints = data["objpoints"]
        imgpoints_l = data["imgpoints"]

        # print(objpoints)

        # time.sleep(1)

        cam, data = cc.calibrate(imgs_r, board)
        K2 = cam.K
        d2 = cam.d
        rvecs2 = data["rvecs"]
        tvecs2 = data["tvecs"]
        imgpoints_r = data["imgpoints"]

        # print(d1,d2)

        # self.save_cal_imgs = cc.save_cal_imgs

        """
        CALIB_ZERO_DISPARITY: horizontal shift, cx1 == cx2
        """
        if flags is None:
            flags = 0
            # flags |= cv2.CALIB_FIX_INTRINSIC
            flags |= cv2.CALIB_ZERO_DISPARITY
            # flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
            # flags |= cv2.CALIB_USE_INTRINSIC_GUESS
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
            # (w,h),
            (h,w),
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

        sc = StereoCamera()
        sc.R = R
        sc.E = E
        sc.F = F
        sc.T = T
        sc.K1 = K1
        sc.K2 = K2
        sc.d1 = d1
        sc.d2 = d2

        return ret, camera_model, sc

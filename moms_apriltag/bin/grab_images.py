#!/usr/bin/env python3
# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
#
# Author: Kevin J. Walchko
# Date: 11 May 2014
# -------------------------------
#

import cv2
from cv2 import aruco
import numpy as np
import argparse
from pathlib import Path
from moms_apriltag import __version__ as VERSION
from moms_apriltag import bgr2gray, gray2bgr
from moms_apriltag.target import TextWriter
from moms_apriltag import arucoTags
from time import sleep
from colorama import Fore
import sys

def printError(s):
    print(f"{Fore.RED}{s}{Fore.RESET}")

def printInfo(s):
    print(f"{Fore.CYAN}{s}{Fore.RESET}")

def printSuccess(s):
    print(f"{Fore.GREEN}{s}{Fore.RESET}")

def findTags(img, dictionary, params, threshold):
    """
    Finds and draws detected tags on the image.

    img: grayscale image
    dictionary: aruco.Dictionary_get()
    params: aruco.DetectorParameters_create()
    threshold: bool, use cv2.adaptiveThreshold() or not

    Returns: color image
    """
    if len(img.shape) == 3:
        img = bgr2gray(img)

    if threshold:
        # _, img = cv2.threshold(img,200,255,cv2.THRESH_BINARY)
        timg = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,51,0)
    else:
        timg = img

    # dictionary = aruco.Dictionary_get(cv2.aruco.DICT_APRILTAG_36H10)
    # params = aruco.DetectorParameters_create()

    corners, ids, rejectedImgPts = aruco.detectMarkers(
        timg,
        dictionary,
        parameters=params)

    if len(img.shape) == 2:
        img = gray2bgr(img)

    numMarkers = len(corners)
    if numMarkers > 0:
        # aruco.drawDetectedMarkers(img, corners, ids)
        aruco.drawDetectedMarkers(img, corners)

        tag = corners[0][0]
        # print(tag)
        a = tag[0]
        b = tag[1]
        tagSize = dictionary.markerSize + 2
        ppb = np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2) / tagSize

        w = TextWriter(1,(200,0,0), thickness=3)
        row = img.shape[0]
        info = f"Found {numMarkers} markers, {ppb:.1f} pix/bit"
        w.write(img, info, (20, row-20))

    return img


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=f'A simple \
    program to capture images from a camera. moms_apriltag version {VERSION}')

    parser.add_argument('-b', '--board', type=int, nargs=2, help='calibration board size (height,width)')
    parser.add_argument('-c', '--camera', type=int, help='which camera to use, default is 0', default=0)
    parser.add_argument('-p', '--path', help='location to grab images, default is current directory', default='capture')
    parser.add_argument('-f', '--family', help='apriltag family, example: tag36h11')
    parser.add_argument('-s', '--size', type=int, nargs=2, help='size of image capture (height, width ), i.e., 480 640')
    parser.add_argument('-t', '--thresholding', type=bool,
        help='use adaptive thresholding on image before marker detection, default is True', default=True)
    parser.add_argument('-v', '--version', action='version',
        help='returns version number', version=f"{sys.argv[0]} version {VERSION}")

    args = vars(parser.parse_args())

    # camera source ----------------------------------------------
    source = args['camera']

    # setup marker detection -------------------------------------
    family = args['family']
    try:
        fam = arucoTags[family]
    except KeyError:
        printError(f"*** Invalide family: {family} ***")
        sys.exit(1)

    dictionary = aruco.Dictionary_get(fam)
    params = aruco.DetectorParameters_create()

    # board dimensions --------------------------------------------
    boardSize = args['board']
    threshold = args['thresholding']

    # setup save directory ----------------------------------------
    shotdir = args['path']
    p = Path(shotdir)
    path = p.expanduser().absolute()

    if path.exists():
        printInfo(f"Cleaning up old files")
        files = path.glob("*.png")
        for f in files:
            f.unlink()

    printInfo(f"Save location: {str(path)}")
    path.mkdir(parents=True, exist_ok=True)

    # open camera ----------------------------------------------
    cap = cv2.VideoCapture(source)
    if args['size'] is not None:
        printInfo('camera capturing images at size: {}'.format(args['size']))
        cap.set(3, args['size'][1]) # cv2.CAP_PROP_FRAME_WIDTH
        cap.set(4, args['size'][0]) # cv2.CAP_PROP_FRAME_HEIGHT
    # cap = CameraCV()
    # cap.init(win=size, cameraNumber=source)
    # cap = ThreadedCamera()
    # cap.open(path=args["camera"], resolution=size, fmt=fmt)

    print('---------------------------------')
    print(' ESC/q to quit')
    # print(' v to start/stop video capture')
    print(' s to grab a frame')
    print('---------------------------------')

    imgs = []

    # Main loop ---------------------------------------------
    try:
        while True:
            ret, img = cap.read()
            if not ret:
                # sleep(1/30)
                printError("*** No image captured ***")
                sleep(1)
                continue

            img = bgr2gray(img)
            cimg = findTags(img, dictionary, params, threshold)

            cv2.imshow('capture', cimg)
            ch = cv2.waitKey(20)

            # Quit program using ESC or q
            if ch in [27, ord('q')]:
                # if video:
                #     save.release()
                break

            # Start/Stop capturing video
            # elif ch == ord('v'):
            #     if video is False:
            #         # setup video output
            #         vfn = '{0!s}_{1:d}.mp4'.format(filename, video_idx)
            #         h, w = img.shape[:2]
            #         save.start(vfn, (w, h), FPS)
            #         print('[+] start capture', vfn)
            #     else:
            #         save.release()
            #         video_idx += 1
            #         print('[-] stop capture', vfn)
            #     video = not video

            # Capture a single frame
            elif ch == ord('s'):
                imgs.append(img)

            # if video:
            #     save.write(img)
            #     sleep(sleep_time)

            # sleep(1/30)

    except KeyboardInterrupt:
        pass

    finally:
        # save images
        if len(imgs) > 0:
            shot_idx = 0
            # printInfo(f"Saving images to {str(path)}")
            for img in imgs:
                fn = '{0:03d}.png'.format(shot_idx)
                p = str(path.joinpath(fn))
                cv2.imwrite(p, img)
                shot_idx += 1
            printSuccess(f"Wrote {len(imgs)} images to {str(path)}")

        cap.release()
        cv2.destroyAllWindows()

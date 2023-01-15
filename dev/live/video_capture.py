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
# import yaml
import argparse
# from opencvutils import CameraCV
from opencv_camera import ThreadedCamera
from opencv_camera.save.video import SaveVideo
from opencv_camera import __version__ as VERSION
from time import sleep
import sys


def read(matrix_name):
    """
    read camera calibration file in
    """
    fd = open(matrix_name, "r")
    data = yaml.load(fd)
    return data


if __name__ == '__main__':

    # parser = argparse.ArgumentParser(version=VERSION, description='A simple \
    parser = argparse.ArgumentParser(description=f'A simple \
    program to capture images from a camera.You can capture a single frame \
    using the "f" or a video by using "v"')

    parser.add_argument('-c', '--camera', help='which camera to use, default is 0', default=0)
    parser.add_argument('-p', '--path', help='location to grab images, default is current directory', default='.')
    parser.add_argument('-f', '--video_filename', help='video file name, default is "out.mp4"', default='out')
    parser.add_argument('-i', '--colorspace', type=str, help='colorspace: bgr, rgb, hsv, or gray; default is bgr', default="bgr")
    # parser.add_argument('-n', '--numpy', type=str, help='numpy camera calibration matrix')
    parser.add_argument('-s', '--size', type=int, nargs=2, help='size of image capture (height, width ), i.e., 480 640')
    parser.add_argument('-v', '--version', action='version', help='returns version number', version=f"{sys.argv[0]} version {VERSION}")

    args = vars(parser.parse_args())

    # if args["version"]:
    #     print(f"{VERSION}")
    #     exit(0)

    source = args['camera']
    shotdir = args['path']
    filename = args['video_filename']

    # image size
    if args['size'] is not None:
        size = (args['size'][0], args['size'][1])
        print('camera capturing images at size: {}'.format(size))
    else:
        size = (480, 640)

    # calibration matrix
    # if args['numpy'] is not None:
    #     cam_cal = args['numpy']
    #     d = read(cam_cal)
    #     m = d['camera_matrix']
    #     k = d['dist_coeff']
    #     print('Using supplied camera calibration matrix: {}'.format(cam_cal))

    # print size
    # print cam_cal

    save = SaveVideo()

    # open camera
    # cap = CameraCV()
    # cap.init(win=size, cameraNumber=source)
    cap = ThreadedCamera()
    fmt=args["colorspace"]
    if fmt not in ["bgr", "rgb", "hsv", "gray"]:
        print(f"{Fore.RED}*** video_capture: Unknown color format: {fmt} ***{Fore.RESET}")
        fmt = 1
    else:
        if fmt == "bgr":
            fmt = 1
        elif fmt == "rgb":
            fmt = 2
        elif fmt == "hsv":
            fmt = 4
        else:
            fmt = 8

    cap.open(path=args["camera"], resolution=size, fmt=fmt)

    print('---------------------------------')
    print(' ESC/q to quit')
    print(' v to start/stop video capture')
    print(' f to grab a frame')
    print('---------------------------------')

    shot_idx = 0
    video_idx = 0
    video = False
    vfn = None
    FPS = 30
    sleep_time = 1.0/float(FPS)  # 30 FPS

    # Main loop ---------------------------------------------
    try:
        while True:
            ret, img = cap.read()
            if not ret:
                sleep(sleep_time)
                continue

            if args['numpy'] is not None:
                img = cv2.undistort(img, m, k)

            cv2.imshow('capture', img)
            ch = cv2.waitKey(20)

            # Quit program using ESC or q
            if ch in [27, ord('q')]:
                # if video:
                #     save.release()
                break

            # Start/Stop capturing video
            elif ch == ord('v'):
                if video is False:
                    # setup video output
                    vfn = '{0!s}_{1:d}.mp4'.format(filename, video_idx)
                    h, w = img.shape[:2]
                    save.start(vfn, (w, h), FPS)
                    print('[+] start capture', vfn)
                else:
                    save.release()
                    video_idx += 1
                    print('[-] stop capture', vfn)
                video = not video

            # Capture a single frame
            elif ch == ord('f'):
                fn = '{0!s}/shot_{1:03d}.png'.format(shotdir, shot_idx)
                cv2.imwrite(fn, img)
                print('[*] saved image to', fn)
                shot_idx += 1

            if video:
                save.write(img)
                sleep(sleep_time)

    except KeyboardInterrupt:
        if video:
            save.release()
        cap.close()

    cv2.destroyAllWindows()

##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*
from colorama import Fore
import io
from threading import Thread #, Lock
import time
# from slurm.rate import Rate
import numpy as np
import cv2
# from enum import IntFlag
from dataclasses import dataclass
from .color_space import ColorSpace

import time


class Rate:
    """
    Uses sleep to keep a desired message/sample rate for a loop.
    """
    def __init__(self, hertz):
        """
            :hertz: rate loop should run at
        """
        self.last_time = time.time()
        self.dt = 1/hertz

    def sleep(self):
        """
        This uses sleep to delay the function. If your loop is faster than your
        desired Hertz, then this will calculate the time difference so sleep
        keeps you close to you desired hertz. If your loop takes longer than
        your desired hertz, then it doesn't sleep.
        """
        now = time.time()
        diff = now - self.last_time
        if diff < self.dt:
            new_sleep = self.dt - diff
            time.sleep(new_sleep)

        # now that we hav slept a while, set the current time
        # as the last time
        self.last_time = time.time()

#                                     1   2   3   4
# ColorSpace = IntFlag("ColorSpace", "bgr rgb hsv gray")

@dataclass
class ThreadedCamera:
    """
    https://www.raspberrypi.org/documentation/hardware/camera/
    Raspberry Pi v2:
        resolution: 3280 x 2464 pixels
        sensor area: 3.68 mm x 2.76 mm
        pixel size: 1.12 um x 1.12 um
        video modes:1080p30, 720p60 and 640x480p60/90
        optical size: 1/4"
        driver: V4L2 driver

    c = ThreadedCamera()
    c.open(0, (640,480), 2) # starts internal loop, camera 0, RGB format
    frame = c.read()        # numpy array
    c.close()               # stops internal loop and gathers back up the thread
    """

    camera = None  # opencv camera object
    frame: np.ndarray = None   # current frame
    run: bool = False    # thread loop run parameter
    thread_hz: float = 30 # thread loop rate
    fmt: int = 0        # colorspact format
    ps = None      # thread process
    # lock = attr.ib(default=Lock())


    def __del__(self):
        self.close()

    def close(self):
        self.run = False
        time.sleep(0.25)
        self.camera.release()

    def __colorspace(self):
        s = "unknown"
        if self.fmt == 1:
            s = "BGR"
        elif self.fmt == 2:
            s = "RGB"
        elif self.fmt == 4:
            s = "HSV"
        elif self.fmt == 8:
            s = "GRAY"

        return s

    def set_resolution(self, resolution):
        """
        resolution: what supported resolution from the camera do you want (height,width)
        """
        rows, cols = resolution
        self.camera.set(3, cols) #cv2.CAP_PROP_FRAME_WIDTH
        self.camera.set(4, rows) #cv2.CAP_PROP_FRAME_HEIGHT

    def get_resolution(self):
        cols = self.camera.get(3) #cv2.CAP_PROP_FRAME_WIDTH
        rows = self.camera.get(4) #cv2.CAP_PROP_FRAME_HEIGHT
        return (rows, cols,)

    def open(self, path=0, resolution=None, fmt=ColorSpace.bgr):
        """
        Opens the camera object and starts the internal loop in a thread

        path: which camera to open 0,1,2, ..., default: 0
        resolution: what supported resolution from the camera do you want (height,width)
        fmt: image format, 1(BGR), 2(RGB), 4(HSV), 8(grayscale), default is BGR
        """

        if fmt not in list(ColorSpace):
            print(f"{Fore.RED}*** Threaded Camera.Open: Unknown color format: {fmt} ***{Fore.RESET}")
            fmt = 1
        self.fmt = fmt

        self.run = True
        self.camera = cv2.VideoCapture(path)

        if resolution:
            self.set_resolution(resolution)

        width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = int(self.camera.get(5))

        print("========================")
        print(f"Opened camera: {path}")
        print(f"Resolution: {width}x{height} @ {fps}")
        print(f"Colorspace: {self.__colorspace()}")
        print("")

        self.ps = Thread(target=self.thread_func, args=(path, resolution))
        self.ps.daemon = True
        self.ps.start()
        return self

    def read(self):
        """Returns image frame or None if no frame captured"""
        if self.frame is None:
            return False, None

        return True, self.frame

    def thread_func(self, path, resolution):
        """Internal function, do not call"""

        rate = Rate(self.thread_hz)

        while self.run:
            rate.sleep()
            ok, img = self.camera.read()

            if not ok:
                continue

            if self.fmt == ColorSpace.bgr:
                self.frame = img
            elif self.fmt == ColorSpace.hsv:
                self.frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            elif self.fmt == ColorSpace.rgb:
                self.frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif self.fmt == ColorSpace.gray:
                self.frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                print(f"{Fore.RED}*** Threaded Camera: Unknown color format: {self.fmt}, reset to BGR ***{Fore.RESET}")
                self.fmt = ColorSpace.bgr
                self.frame = img

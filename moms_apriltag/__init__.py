# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
from importlib.metadata import version # type: ignore

from .target import ApriltagBoard
from .apriltag_drawer import ApriltagDrawer
from .generator2 import TagGenerator2, apriltags_v2
from .generator3 import TagGenerator3, tag2RGBA, apriltags_v3
from .color_space import *
from .aruco_tags.calibrate import ApriltagCameraCalibration
from .aruco_tags.calibrate import ApriltagStereoCalibration

__license__ = "MIT"
__author__ = "Kevin J. Walchko"
__version__ = version("moms_apriltag")

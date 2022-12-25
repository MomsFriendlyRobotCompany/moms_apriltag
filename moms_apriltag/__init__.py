# -*- coding: utf-8 -*
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
from importlib.metadata import version # type: ignore

from .target import generate
from .target import board
from .generator2 import TagGenerator2
from .generator3 import TagGenerator3
from .target import apriltags_v2, apriltags_v3

__license__ = "MIT"
__author__ = "Kevin J. Walchko"
__version__ = version("moms_apriltag")

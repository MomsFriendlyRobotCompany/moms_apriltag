from importlib.metadata import version # type: ignore

from .target import generate
from .target import board

__license__ = "MIT"
__author__ = "Kevin J. Walchko"
__version__ = version("moms_apriltag")

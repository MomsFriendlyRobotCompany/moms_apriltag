try:
    from importlib.metadata import version # type: ignore
except ImportError:
    from importlib_metadata import version # type: ignore

from .apr import generate, save, flip, Tag
from .calibrate import ApriltagCameraCalibrator
from .display import draw_tag, draw_ids, draw_imgpts, coverage, tip_sheet
from .target import board

__license__ = "MIT"
__author__ = "Kevin J. Walchko"
__version__ = version("apriltag_gen")

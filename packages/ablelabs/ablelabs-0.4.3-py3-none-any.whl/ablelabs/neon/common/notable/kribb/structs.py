from dataclasses import dataclass
import cv2

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.structs import *


@dataclass
class LabelInfo:
    index: int
    width: int
    height: int
    area: int
    centroid: tuple[float, float]
    inscribed_center: tuple[float, float]
    inscribed_radius: int
    perimeter: float
    circularity: float
    brightness: float
    color: tuple[float, float, float]
    contours: list[cv2.Mat]


@dataclass
class ColonyInfo:
    x_ratio: float
    y_ratio: float
    area: float
    circularity: float
    brightness: float
    color: tuple[float, float, float]

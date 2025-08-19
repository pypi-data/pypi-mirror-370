from __future__ import annotations

"""
    Публичный API пакета: функциональные операции и класс-обёртка с дефолтным устройством.
"""

from .types import CvImage, PointHSV
from .enums import ComputeDevice
from .img_ops import ImageProcessor
from .ops import (
    bgr_to_rgb,
    rgb_to_bgr,
    bgr_to_hsv,
    in_range,
    gauss_blur,
    find_contours,
    connected_components,
)

__all__ = [
    "CvImage", "PointHSV",
    "ComputeDevice",
    "ImageProcessor",
    "bgr_to_rgb", "rgb_to_bgr", "bgr_to_hsv", "in_range",
    "gauss_blur",
    "find_contours", "connected_components",
]

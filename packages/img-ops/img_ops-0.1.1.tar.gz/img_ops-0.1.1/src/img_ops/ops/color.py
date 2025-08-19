from __future__ import annotations

__all__ = ["bgr_to_rgb", "rgb_to_bgr", "bgr_to_hsv", "in_range"]

from ..types import CvImage, PointHSV
from ..enums import ComputeDevice
from ..device import resolve_device, gpu_available, mps_available
from ..registry import dispatch

def _normalize(device: str | ComputeDevice | None, default: ComputeDevice) -> ComputeDevice:
    """ Нормализует устройство и применяет фолбэки (GPU/MPS -> CPU, если недоступны). """
    dev = resolve_device(device, default)
    if dev is ComputeDevice.GPU and not gpu_available():
        return ComputeDevice.CPU
    if dev is ComputeDevice.MPS and not mps_available():
        return ComputeDevice.CPU
    return dev

def bgr_to_rgb(image: CvImage, *,
                       device: str | ComputeDevice | None = None,
                       default: ComputeDevice = ComputeDevice.CPU) -> CvImage:
    """ Конвертирует изображение BGR -> RGB. """
    dev = _normalize(device, default)
    return dispatch("bgr_to_rgb", dev, image)

def bgr_to_hsv(image: CvImage, *,
                       device: str | ComputeDevice | None = None,
                       default: ComputeDevice = ComputeDevice.CPU) -> CvImage:
    """ Конвертирует изображение BGR -> HSV. """
    dev = _normalize(device, default)
    return dispatch("bgr_to_hsv", dev, image)

def rgb_to_bgr(image: CvImage, *,
                       device: str | ComputeDevice | None = None,
                       default: ComputeDevice = ComputeDevice.CPU) -> CvImage:
    """ Конвертирует изображение BGR -> HSV. """
    dev = _normalize(device, default)
    return dispatch("rgb_to_bgr", dev, image)

def in_range(image_hsv: CvImage, lower: PointHSV, upper: PointHSV, *,
             device: str | ComputeDevice | None = None,
             default: ComputeDevice = ComputeDevice.CPU) -> CvImage:
    """
        Пороговая фильтрация в HSV-цветовом пространстве.
        Args:
            image_hsv: изображение в HSV.
            lower: нижняя граница (H, S, V).
            upper: верхняя граница (H, S, V).
        Returns:
            Бинарная маска (uint8).
    """
    dev = _normalize(device, default)
    return dispatch("in_range", dev, image_hsv, lower, upper)

from __future__ import annotations

__all__ = ["gauss_blur"]

from typing import Tuple
from ..types import CvImage
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

def gauss_blur(image: CvImage, ksize: Tuple[int, int], sigma: float, *,
               device: str | ComputeDevice | None = None,
               default: ComputeDevice = ComputeDevice.CPU) -> CvImage:
    """
        Гауссово размытие.
        Args:
            image: входное изображение.
            ksize: размер ядра (width, height) — нечётные значения.
            sigma: σ гауссова фильтра.
        Returns:
            Размытое изображение.
    """
    dev = _normalize(device, default)
    return dispatch("gauss_blur", dev, image, ksize, sigma)

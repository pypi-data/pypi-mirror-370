from __future__ import annotations

__all__ = ["REGISTRY", "dispatch"]

from typing import Callable
import cv2

from .types import CvImage, PointHSV  # noqa: F401 (для типов)
from .enums import ComputeDevice
from .device import gpu_available, mps_available

# ---------------- Реализации операций для каждого устройства ----------------

def _cpu() -> dict[str, Callable[..., CvImage]]:
    """
        Реестр CPU-реализаций. Ключ — имя операции.
    """
    return {
        # color
        "bgr_to_rgb": lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        "rgb_to_bgr": lambda img: cv2.cvtColor(img, cv2.COLOR_RGB2BGR),
        "bgr_to_hsv": lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
        "in_range":            lambda hsv, lo, hi: cv2.inRange(hsv, lo, hi),

        # filters
        "gauss_blur":          lambda img, k, s: cv2.GaussianBlur(img, k, s),

        # segmentation
        "find_contours":       lambda mask, mode, method: cv2.findContours(mask, mode, method),
        "connected_components":lambda mask: cv2.connectedComponentsWithStats(mask),

        # utils
        "sum_masks":           lambda a, b: cv2.add(a, b),
    }

def _gpu() -> dict[str, Callable[..., CvImage]]:
    """
        Реестр GPU-реализаций (CUDA), только где поддерживается.
        Если CUDA недоступна — возвращаем пустой словарь (будет фолбэк на CPU).
    """
    if not gpu_available():
        return {}

    def _upload(img):
        g = cv2.cuda_GpuMat()
        g.upload(img)
        return g

    return {
        "bgr_to_rgb":  lambda img: (lambda g=cv2.cuda.cvtColor(_upload(img), cv2.COLOR_BGR2RGB): g.download())(),
        "rgb_to_bgr":  lambda img: (lambda g=cv2.cuda.cvtColor(_upload(img), cv2.COLOR_RGB2BGR): g.download())(),
        "bgr_to_hsv":  lambda img: (lambda g=cv2.cuda.cvtColor(_upload(img), cv2.COLOR_BGR2HSV): g.download())(),
        "in_range":            lambda hsv, lo, hi: (lambda g=cv2.cuda.inRange(_upload(hsv), lo, hi): g.download())(),
        "gauss_blur":          lambda img, k, s: (lambda o=cv2.cuda.createGaussianFilter(cv2.CV_8UC3, -1, k, s).apply(_upload(img)): o.download())(),
        "sum_masks":           lambda a, b: (lambda o=cv2.cuda.add(_upload(a), _upload(b)): o.download())(),
        # find_contours / connected_components — CPU-only
    }

def _mps() -> dict[str, Callable[..., CvImage]]:
    """
        Реестр MPS (Apple Metal). Пока пустой — все операции падают на CPU.
    """
    if not mps_available():
        return {}
    return {}

REGISTRY: dict[ComputeDevice, dict[str, Callable[..., CvImage]]] = {
    ComputeDevice.CPU: _cpu(),
    ComputeDevice.GPU: _gpu(),
    ComputeDevice.MPS: _mps(),
}

def dispatch(op: str, device: ComputeDevice, *args, **kwargs):
    """
        Выполняет операцию `op` на указанном устройстве.
        Если реализации на выбранном устройстве нет — фолбэк на CPU.
        Args:
            op: имя операции (см. ключи в _cpu/_gpu/_mps).
            device: устройство исполнения.
            *args, **kwargs: аргументы операции.
        Returns:
            Результат вызова операции.
        Raises:
            NotImplementedError: если нет реализации ни для выбранного device, ни для CPU.
    """
    impls = REGISTRY.get(device) or {}
    func = impls.get(op)
    if func is None:
        func = REGISTRY[ComputeDevice.CPU].get(op)
        if func is None:
            raise NotImplementedError(f"Operation '{op}' not implemented for {device.value} or CPU.")
    return func(*args, **kwargs)

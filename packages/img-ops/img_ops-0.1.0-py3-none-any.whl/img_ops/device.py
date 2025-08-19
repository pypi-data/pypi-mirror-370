from __future__ import annotations

__all__ = ["resolve_device", "gpu_available", "mps_available"]

from typing import Optional
import cv2

from .enums import ComputeDevice

def resolve_device(device: Optional[str | ComputeDevice],
                   default: ComputeDevice) -> ComputeDevice:
    """
        Преобразует строку/Enum в ComputeDevice.
        Если device=None — возвращает default.
        Args:
            device: "cpu" | "gpu" | "mps" | None | ComputeDevice
            default: устройство по умолчанию, если device не указан.
        Returns:
            ComputeDevice: нормализованное устройство.
        Raises:
            ValueError: если передана неизвестная строка.
            TypeError: если тип аргумента не поддерживается.
    """
    if device is None:
        return default
    if isinstance(device, ComputeDevice):
        return device
    if isinstance(device, str):
        key = device.strip().lower()
        try:
            return ComputeDevice(key)
        except ValueError:
            allowed = ", ".join(d.value for d in ComputeDevice)
            raise ValueError(f"Unknown device '{device}'. Allowed: {allowed}")
    raise TypeError("device must be str | ComputeDevice | None")

def gpu_available() -> bool:
    """
        Доступна ли CUDA (cv2.cuda) в текущей сборке OpenCV.
        Returns:
            bool: True — если есть cv2.cuda и хотя бы одно устройство.
    """
    try:
        return hasattr(cv2, "cuda") and cv2.cuda.getCudaEnabledDeviceCount() > 0
    except Exception:
        return False

def mps_available() -> bool:
    """
        Заглушка для Apple Metal (MPS).
        Сейчас OpenCV не предоставляет прямых MPS-версий для указанных операций,
        поэтому всегда возвращает False и используется фолбэк на CPU.
        Returns:
            bool: False — пока всегда.
    """
    return False
